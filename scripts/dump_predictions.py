"""Ghi `predictions/<split>.npz` từ `best.pt` của một run SED đã hoàn tất.

    .venv/Scripts/python.exe -m scripts.dump_predictions ml/runs/<run> --split test
    .venv/Scripts/python.exe -m scripts.dump_predictions ml/runs/<run> --verify-dev

ADR-0030 §5: run v2 train **không** kèm `--evaluate-test`. Logit test chỉ được sinh sau khi
lựa chọn hệ thống (chỉ bằng dev) đã commit. Script dựng lại đúng dataset (cửa sổ/hop, batch)
và model (kiến trúc từ manifest, `ml.models.sed_factory`) như lúc train, rồi dùng lại
`collect_predictions` — cùng autocast, cùng thứ tự cửa sổ.

`--verify-dev` sinh lại logit dev vào file tạm và so SHA-256 với `dev_predictions_sha256`
đã ghi lúc train: khớp nghĩa là đường dump này tái tạo đúng từng bit đường train, nên
logit test sinh sau cũng là logit của đúng checkpoint đó.

Track 2a (ADR-0032 §2): cùng đường; BEATs đóng băng được dựng lại từ checkpoint ghi trong
manifest (kiểm SHA-256), đầu vào là cache 16 kHz (kiểm SHA-256 manifest cache).
Track 2b (ADR-0032 §3): cả mạng frame_mn nằm trong `best.pt`, cùng đầu vào cache 16 kHz.

Giai đoạn O, O-A (ADR-0041): suy luận cửa sổ trượt chồng lấn. `--hop-seconds` cắt lại
recording với hop nhỏ hơn lúc train và ghi vào một **run dẫn xuất**
`ml/runs/sed_rewindow_<label>_<ts>/` (run gốc và các file chọn hậu xử lý đã khóa không bị
đụng). Kiểu gộp cửa sổ (`--weighting`, mặc định `triangular:0.3`) nằm trong chính artifact nên
mọi bước sau (CV hậu xử lý, ensemble, đánh giá) tự áp đúng:

    .venv/Scripts/python.exe -m scripts.dump_predictions ml/runs/<run> --split dev \
        --hop-seconds 2.5 --label f2m1_h2.5
    # test của run dẫn xuất: CHỈ sau khi lựa chọn trên dev đã commit
    .venv/Scripts/python.exe -m scripts.dump_predictions ml/runs/<run> --split test \
        --hop-seconds 2.5 --into ml/runs/sed_rewindow_f2m1_h2.5_<ts>
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import platform
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import torch

from ml.evaluation.predictions import UNIFORM_WEIGHTING, save_predictions, triangular_floor
from ml.models import SoundEventDetector
from ml.models.embedding_sed import EmbeddingSequenceSED
from ml.models.sed_factory import (
    beats_finetune_model,
    embedding_head,
    frame_mn_model,
    sed_architecture,
    sed_model,
)
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from ml.training.common import seed_everything, sha256_file, write_json
from ml.training.sed import collect_predictions
from scripts.train_sed import (
    WAVEFORM_ENCODERS,
    WAVEFORM_MANIFEST,
    apply_cv_fold,
    frozen_beats,
    load_datased_tables,
    make_loader,
    split_dataset,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_SPLIT = {"test": "test", "dev": "validation"}  # predictions literal → split CSV
SHARED = ("split_sha256", "data_manifest_sha256", "taxonomy_sha256")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--split", choices=("test", "dev"), default="test",
                        help="'dev' chỉ hợp lệ cùng --hop-seconds (run dẫn xuất)")
    parser.add_argument("--verify-dev", action="store_true",
                        help="chỉ kiểm: sinh lại logit dev và so SHA-256 với lúc train")
    parser.add_argument("--hop-seconds", type=float, default=None,
                        help="O-A: hop suy luận khác lúc train → ghi run dẫn xuất")
    parser.add_argument("--weighting", default="triangular:0.3",
                        help="'uniform' hoặc 'triangular:<sàn>' (chỉ dùng với --hop-seconds)")
    parser.add_argument("--label", default=None, help="nhãn run dẫn xuất mới")
    parser.add_argument("--into", type=Path, default=None,
                        help="ghi vào run dẫn xuất đã có (vd thêm test sau khi chọn trên dev)")
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()
    if args.hop_seconds is None and (args.split == "dev" and not args.verify_dev):
        parser.error("--split dev chỉ dùng với --hop-seconds; dev gốc đã sinh lúc train")
    if args.hop_seconds is not None and not (args.label or args.into):
        parser.error("--hop-seconds cần --label (run mới) hoặc --into (run dẫn xuất đã có)")
    triangular_floor(args.weighting)
    return args


def load_model(run_dir: Path, config: dict, classes: int, device: torch.device
               ) -> SoundEventDetector | EmbeddingSequenceSED:
    if config["encoder_type"] == "beats":
        model = embedding_head(config, classes)  # Track 2a: head only, BEATs stays frozen
    elif config["encoder_type"] == "frame_mn":
        model = frame_mn_model(config, classes)  # Track 2b: whole network is in best.pt
    elif config["encoder_type"] == "beats_ft":
        model = beats_finetune_model(config, classes)  # O-D: whole BEATs is in best.pt
    elif config["encoder_type"] == "panns":
        model = sed_model(config, classes)
    else:
        architecture = sed_architecture(config)
        model = SoundEventDetector(classes=classes, hidden_size=int(architecture["rnn_hidden"]),
                                   rnn_layers=int(architecture["rnn_layers"]),
                                   upsample=str(architecture["upsample"]))
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    checkpoint = torch.load(run_dir / manifest["best_checkpoint"], map_location="cpu",
                            weights_only=True)
    model.load_state_dict(checkpoint["model_state"])
    return model.to(device).eval()


def dump(run_dir: Path, split: str, out_path: Path, device: torch.device, *,
         hop_frames: int | None = None, weighting: str = UNIFORM_WEIGHTING) -> str:
    """`hop_frames=None` reproduces the training cut exactly (bit-identical, `--verify-dev`)."""
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("complete"):
        raise SystemExit(f"{run_dir} chưa hoàn tất")
    config = dict(manifest["config"])
    if hop_frames is not None:
        config["hop_frames"] = hop_frames
    seed_everything(int(config["seed"]))  # same cuDNN flags as the training process
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    class_ids = taxonomy.polyphonic_class_ids
    if taxonomy.checksum != manifest["taxonomy_sha256"]:
        raise SystemExit("taxonomy đã đổi so với lúc train")
    is_beats = config["encoder_type"] == "beats"
    is_waveform = config["encoder_type"] in WAVEFORM_ENCODERS
    joined, events = load_datased_tables(config["feature_set"])
    # OOF fold run (ADR-0041 tầng C): its "dev" is the held-out fold, never the frozen dev.
    joined = apply_cv_fold(joined, config.get("cv_fold"))
    dataset = split_dataset(joined, events, CONTRACT_SPLIT[split],
                            feature_set=config["feature_set"], class_ids=class_ids,
                            frame_rate=float(config["frame_rate"]),
                            window_frames=int(config["window_frames"]),
                            hop_frames=int(config["hop_frames"]), waveform=is_waveform)
    encoder = None
    if is_beats:
        encoder, _ = frozen_beats(Path(config["checkpoint_path"]),
                                  expected_sha256=config["checkpoint_sha256"])
    if is_waveform and sha256_file(WAVEFORM_MANIFEST) != config["waveform_manifest_sha256"]:
        raise SystemExit("cache waveform 16 kHz đã đổi so với lúc train "
                         "(data/manifests/datased_wav16k.csv)")
    loader = make_loader(dataset, batch_size=int(config["batch_size"]), shuffle=False,
                         device=device, encoder=encoder)
    artifact = collect_predictions(
        load_model(run_dir, config, len(class_ids), device), loader, device=device,
        class_ids=class_ids, split=split,
        model_version=str(config.get("model_version", "sed-v1.0")),
        taxonomy_sha256=taxonomy.checksum, frame_rate=float(config["frame_rate"]))
    artifact = dataclasses.replace(artifact, window_weighting=weighting)
    return save_predictions(out_path, artifact, expected_class_ids=class_ids)


def derived_run_dir(args: argparse.Namespace, source: dict, hop_frames: int) -> Path:
    """New `sed_rewindow_*` run (with manifest), or an existing one whose recipe must match."""
    recipe = {"source_run": args.run_dir.name, "hop_seconds": args.hop_seconds,
              "hop_frames": hop_frames, "window_frames": int(source["config"]["window_frames"]),
              "window_weighting": args.weighting}
    if args.into is not None:
        manifest = json.loads((args.into / "manifest.json").read_text(encoding="utf-8"))
        if any(manifest["config"].get(key) != value for key, value in recipe.items()):
            raise SystemExit(f"{args.into}: công thức dẫn xuất khác {recipe}")
        return args.into
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "ml" / "runs" / f"sed_rewindow_{args.label}_{stamp}"
    manifest = {
        "run_id": out.name, "task": "sed_rewindow", "complete": True,
        "command": ["python", "-m", "scripts.dump_predictions", *sys.argv[1:]],
        "class_ids": source["class_ids"], **{key: source[key] for key in SHARED},
        "config": {**recipe, "frame_rate": source["config"]["frame_rate"],
                   "model_version": source["config"].get("model_version"),
                   "source_git": source.get("git")},
        "git": git_state(ROOT),
        "environment": {"python": platform.python_version(), "torch": torch.__version__},
    }
    out.mkdir(parents=True)
    write_json(out / "manifest.json", manifest)
    write_json(out / "metrics.json", {})
    return out


def dump_derived(args: argparse.Namespace, device: torch.device) -> None:
    source = json.loads((args.run_dir / "manifest.json").read_text(encoding="utf-8"))
    hop_frames = round(args.hop_seconds * float(source["config"]["frame_rate"]))
    if not 0 < hop_frames <= int(source["config"]["window_frames"]):
        raise SystemExit(f"hop {hop_frames} frame phải trong (0, cửa sổ]")
    out = derived_run_dir(args, source, hop_frames)
    out_path = out / "predictions" / f"{args.split}.npz"
    if out_path.exists():
        raise SystemExit(f"{out_path} đã tồn tại — không ghi đè logit đã sinh")
    metrics = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
    metrics[f"{args.split}_predictions_sha256"] = dump(
        args.run_dir, args.split, out_path, device, hop_frames=hop_frames,
        weighting=args.weighting)
    write_json(out / "metrics.json", metrics)
    print(json.dumps({"run_dir": str(out), **metrics}, indent=1))


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    device = torch.device(args.device)
    if args.hop_seconds is not None:
        dump_derived(args, device)
        return
    metrics_path = args.run_dir / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    if args.verify_dev:
        with tempfile.TemporaryDirectory() as tmp:
            digest = dump(args.run_dir, "dev", Path(tmp) / "dev.npz", device)
        expected = metrics["dev_predictions_sha256"]
        print(json.dumps({"dev_sha256": digest, "recorded": expected,
                          "identical": digest == expected}, indent=1))
        raise SystemExit(0 if digest == expected else 1)
    out_path = args.run_dir / "predictions" / f"{args.split}.npz"
    if out_path.exists():
        raise SystemExit(f"{out_path} đã tồn tại — không ghi đè logit đã sinh")
    metrics[f"{args.split}_predictions_sha256"] = dump(args.run_dir, args.split, out_path,
                                                       device)
    write_json(metrics_path, metrics)
    print(json.dumps({"predictions": str(out_path),
                      "sha256": metrics[f"{args.split}_predictions_sha256"]}, indent=1))


if __name__ == "__main__":
    main()
