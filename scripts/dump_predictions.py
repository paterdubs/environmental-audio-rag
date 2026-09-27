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
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import torch

from ml.evaluation.predictions import save_predictions
from ml.models import SoundEventDetector
from ml.models.embedding_sed import EmbeddingSequenceSED
from ml.models.sed_factory import embedding_head, sed_architecture, sed_model
from ml.taxonomy import load_taxonomy
from ml.training.common import seed_everything, write_json
from ml.training.sed import collect_predictions
from scripts.train_sed import frozen_beats, load_datased_tables, make_loader, split_dataset

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_SPLIT = {"test": "test", "dev": "validation"}  # predictions literal → split CSV


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--split", choices=("test",), default="test")
    parser.add_argument("--verify-dev", action="store_true",
                        help="chỉ kiểm: sinh lại logit dev và so SHA-256 với lúc train")
    parser.add_argument("--device", default="cuda")
    return parser.parse_args()


def load_model(run_dir: Path, config: dict, classes: int, device: torch.device
               ) -> SoundEventDetector | EmbeddingSequenceSED:
    if config["encoder_type"] == "beats":
        model = embedding_head(config, classes)  # Track 2a: head only, BEATs stays frozen
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


def dump(run_dir: Path, split: str, out_path: Path, device: torch.device) -> str:
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("complete"):
        raise SystemExit(f"{run_dir} chưa hoàn tất")
    config = manifest["config"]
    seed_everything(int(config["seed"]))  # same cuDNN flags as the training process
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    class_ids = taxonomy.polyphonic_class_ids
    if taxonomy.checksum != manifest["taxonomy_sha256"]:
        raise SystemExit("taxonomy đã đổi so với lúc train")
    is_beats = config["encoder_type"] == "beats"
    joined, events = load_datased_tables(config["feature_set"])
    dataset = split_dataset(joined, events, CONTRACT_SPLIT[split],
                            feature_set=config["feature_set"], class_ids=class_ids,
                            frame_rate=float(config["frame_rate"]),
                            window_frames=int(config["window_frames"]),
                            hop_frames=int(config["hop_frames"]), waveform=is_beats)
    encoder = None
    if is_beats:
        encoder, info = frozen_beats(Path(config["checkpoint_path"]),
                                     expected_sha256=config["checkpoint_sha256"])
        if info["waveform_manifest_sha256"] != config["waveform_manifest_sha256"]:
            raise SystemExit("cache waveform 16 kHz đã đổi so với lúc train "
                             "(data/manifests/datased_wav16k.csv)")
    loader = make_loader(dataset, batch_size=int(config["batch_size"]), shuffle=False,
                         device=device, encoder=encoder)
    artifact = collect_predictions(
        load_model(run_dir, config, len(class_ids), device), loader, device=device,
        class_ids=class_ids, split=split,
        model_version=str(config.get("model_version", "sed-v1.0")),
        taxonomy_sha256=taxonomy.checksum, frame_rate=float(config["frame_rate"]))
    return save_predictions(out_path, artifact, expected_class_ids=class_ids)


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    device = torch.device(args.device)
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
