"""Train DataSED polyphonic — ba nhánh A/B/C (ADR-0002, ADR-0020).

    # Nhánh A (scratch)
    .venv/Scripts/python.exe -m scripts.train_sed --encoder audio --evaluate-test

    # Nhánh B (AudioSet -> DataSED trực tiếp)
    .venv/Scripts/python.exe -m scripts.train_sed --encoder panns \
        --audioset-checkpoint artifacts/checkpoints/Cnn14_mAP=0.431.pth --evaluate-test

    # Nhánh C (AudioSet -> DataSEC -> DataSED, checkpoint D1)
    .venv/Scripts/python.exe -m scripts.train_sed --encoder panns \
        --datasec-checkpoint ml/runs/classifier_datasec_20260923T121808Z/checkpoints/best.pt \
        --evaluate-test

`--encoder panns` đòi đúng một trong hai cờ checkpoint (ADR-0020 §1). Nhánh C
không cần `--normalization` — `input_mean`/`input_std` đi kèm state_dict của
checkpoint D1 (ADR-0020 §4).

`--recipe v2` (ADR-0030): CNN14 giữ độ phân giải thời gian (pool thời gian chỉ ở 3 khối
đầu, /8 = 80 ms), BiGRU 2 lớp chạy ở nhịp encoder, 30 epoch warmup + cosine, lr encoder
3e-4 (pilot ADR-0030 §2), random crop, mixup + FilterAugment, trần `pos_weight` 10, chọn
checkpoint theo macro-AP dev. Mỗi núm ghi đè được riêng (`--time-pooling`, `--mixup-p`, …).
Không có `--recipe` = v1, trùng từng tham số với mọi run RQ1.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import torch
from torch.utils.data import DataLoader

from ml.datasets.features import SedFeatureDataset
from ml.evaluation.predictions import save_predictions
from ml.models import SoundEventDetector
from ml.models.sed_factory import panns_encoder, sed_model
from ml.taxonomy import load_taxonomy
from ml.training.common import (
    create_run_directory,
    git_state,
    runtime_environment,
    seed_everything,
    sha256_file,
    write_json,
)
from ml.training.sed import (
    SedTrainingConfig,
    collect_predictions,
    estimate_pos_weight,
    run_epoch,
    train_sed,
)

ROOT = Path(__file__).resolve().parents[1]
# ADR-0030: every knob of a recipe; CLI flags override one knob at a time (ablations).
RECIPES: dict[str, dict[str, object]] = {
    "v1": {"epochs": 8, "learning_rate": 0.001, "encoder_learning_rate": None,
           "warmup_epochs": 0, "cosine_decay": False, "select_metric": "macro_f1",
           "mixup_p": 0.0, "filter_augment_p": 0.0, "random_crop": False,
           "pos_weight_cap": 50.0, "time_pooling": [2, 2, 2, 2, 2, 2], "rnn_hidden": 128,
           "rnn_layers": 1, "upsample": "before_rnn", "model_version": "sed-v1.0"},
    "v2": {"epochs": 30, "learning_rate": 0.001, "encoder_learning_rate": 0.0003,
           "warmup_epochs": 1, "cosine_decay": True,
           "select_metric": "macro_average_precision", "mixup_p": 0.5,
           "filter_augment_p": 0.5, "random_crop": True, "pos_weight_cap": 10.0,
           "time_pooling": [2, 2, 2, 1, 1, 1], "rnn_hidden": 256, "rnn_layers": 2,
           "upsample": "after_rnn", "model_version": "sed-v2.0"},
}

# ADR-0020 §2: feature set đi theo encoder, không tách cờ riêng.
ENCODER_FEATURE_SET = {"audio": "logmel_v1", "panns": "logmel_panns_v1"}
ENCODER_FRAME_RATE = {"audio": 50.0, "panns": 100.0}
# ADR-0020 §3: cùng cửa sổ/hop THEO GIÂY (10 s / 10 s, không overlap) giữa các nhánh.
WINDOW_SECONDS = 10.0
HOP_SECONDS = 10.0
PANNS_BATCH_SIZE = 24  # C2: batch đo an toàn thật ở cửa sổ 10 s trên 8 GB VRAM.
DEFAULT_NORMALIZATION = (
    ROOT / "data" / "manifests" / "datased_logmel_panns_v1_train_normalization.npz"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--recipe", choices=tuple(RECIPES), default="v1")
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument(
        "--batch-size", type=int, default=None, help="Mặc định: 8 (audio)/24 (panns)"
    )
    parser.add_argument("--learning-rate", type=float, default=None)
    parser.add_argument("--encoder-learning-rate", type=float, default=None)
    parser.add_argument("--warmup-epochs", type=int, default=None)
    parser.add_argument("--cosine-decay", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--select-metric", choices=("macro_f1", "macro_average_precision"),
                        default=None)
    parser.add_argument("--mixup-p", type=float, default=None)
    parser.add_argument("--filter-augment-p", type=float, default=None)
    parser.add_argument("--random-crop", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--time-pooling", default=None,
                        help="hệ số pool thời gian mỗi khối CNN14, ví dụ 2,2,2,1,1,1")
    parser.add_argument("--rnn-hidden", type=int, default=None)
    parser.add_argument("--rnn-layers", type=int, default=None)
    parser.add_argument("--upsample", choices=("before_rnn", "after_rnn"), default=None)
    parser.add_argument("--seed", type=int, default=20260922)
    parser.add_argument("--encoder", choices=("audio", "panns"), default="audio")
    parser.add_argument(
        "--audioset-checkpoint", type=Path, default=None, help="Nhánh B (--encoder panns)"
    )
    parser.add_argument(
        "--datasec-checkpoint", type=Path, default=None,
        help="Nhánh C, checkpoint D1 best.pt (--encoder panns)",
    )
    parser.add_argument(
        "--normalization", type=Path, default=None,
        help="Chuẩn hoá train-only cho nhánh B; bỏ qua với --datasec-checkpoint (ADR-0020 §4). "
        f"Mặc định: {DEFAULT_NORMALIZATION}",
    )
    parser.add_argument(
        "--pos-weight-cap", type=float, default=None,
        help="Trần pos_weight (ablation A4: 10, 30, 50, inf = không clip); mặc định theo recipe",
    )
    parser.add_argument("--evaluate-test", action="store_true")
    parser.add_argument("--device", default="cuda")
    return parser.parse_args()


def validate_checkpoint_flags(args: argparse.Namespace) -> None:
    if args.encoder == "audio":
        if args.audioset_checkpoint or args.datasec_checkpoint:
            raise SystemExit(
                "--audioset-checkpoint/--datasec-checkpoint chỉ dùng với --encoder panns"
            )
        return
    has_audioset = args.audioset_checkpoint is not None
    has_datasec = args.datasec_checkpoint is not None
    if has_audioset == has_datasec:
        raise SystemExit(
            "--encoder panns cần ĐÚNG MỘT trong --audioset-checkpoint (nhánh B) hoặc "
            "--datasec-checkpoint (nhánh C) -- ADR-0020 §1"
        )


SPLITS_PATH = ROOT / "data" / "splits" / "datased_polyphonic.csv"


def load_datased_tables(feature_set: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(recordings ⋈ features ⋈ frozen split, polyphonic events) — shared with dump_predictions."""
    recordings = pd.read_csv(ROOT / "data" / "manifests" / "datased_recordings.csv")
    features = pd.read_csv(ROOT / "data" / "manifests" / f"datased_{feature_set}.csv")
    splits = pd.read_csv(SPLITS_PATH)
    events = pd.read_csv(ROOT / "data" / "annotations" / "datased_polyphonic_events.csv")
    joined = (
        recordings.drop(columns=["frames"]).merge(
            features[["file_id", "feature_relative_path", "frames"]],
            on="file_id",
            validate="one_to_one",
        )
        .merge(splits[["recording_id", "split"]], on="recording_id", validate="one_to_one")
    )
    return joined, events


def split_dataset(joined: pd.DataFrame, events: pd.DataFrame, split: str, *,
                  feature_set: str, class_ids: tuple[str, ...], frame_rate: float,
                  window_frames: int, hop_frames: int, random_crop: bool = False
                  ) -> SedFeatureDataset:
    return SedFeatureDataset(
        joined[joined["split"] == split],
        events,
        feature_root=ROOT / "data" / "features" / "datased" / feature_set,
        class_ids=class_ids,
        frame_rate=frame_rate,
        window_frames=window_frames,
        hop_frames=hop_frames,
        random_crop=random_crop,
    )


def best_validation_metrics(
    history: list[dict[str, object]], select_metric: str
) -> dict[str, object]:
    """`best_validation` reported in `metrics.json`, using the metric that actually picked the
    checkpoint (PLAN nợ #24). Trước đây trường này luôn là max `macro_f1` bất kể `select_metric`:
    đúng cho v1 (macro_f1), nhưng cho v2 (macro_average_precision) nó là một con số không liên
    quan tới checkpoint đã chọn -- không ai dùng số này để kết luận (mọi báo cáo v2 đọc thẳng
    `logs/history.json`), nhưng vẫn phải sửa cho những run về sau."""
    validations = [item["validation"] for item in history]
    return {
        "select_metric": select_metric,
        "best_validation": max(validation[select_metric] for validation in validations),
    }


def resolve_recipe(args: argparse.Namespace) -> dict[str, object]:
    """Recipe defaults, then every knob the caller set explicitly on the command line."""
    knobs = dict(RECIPES[args.recipe])
    for key in knobs:
        value = getattr(args, key, None)
        if value is not None:
            knobs[key] = value
    if isinstance(knobs["time_pooling"], str):
        knobs["time_pooling"] = [int(p) for p in str(knobs["time_pooling"]).split(",")]
    return knobs


def build_encoder(args: argparse.Namespace, knobs: dict[str, object]
                  ) -> tuple[torch.nn.Module, dict[str, object]]:
    """Trả về (encoder, thông tin nguồn trọng số để ghi manifest)."""
    if args.encoder == "audio":
        return None, {
            "weight_source": "scratch",
            "checkpoint_path": None,
            "checkpoint_sha256": None,
        }

    if args.datasec_checkpoint:
        # ADR-0020 §4: KHÔNG truyền normalization_path -- state_dict của checkpoint D1
        # đã mang theo input_mean/input_std, ghi đè bất kỳ giá trị nào đặt trước đó.
        encoder = panns_encoder(knobs)
        checkpoint = torch.load(args.datasec_checkpoint, map_location="cpu", weights_only=True)
        dummy_head = SoundEventDetector(classes=1, encoder=encoder)
        dummy_head.load_classifier_encoder(checkpoint)
        return encoder, {
            "weight_source": f"datasec:{args.datasec_checkpoint}",
            "checkpoint_path": str(args.datasec_checkpoint),
            "checkpoint_sha256": sha256_file(args.datasec_checkpoint),
        }

    normalization_path = args.normalization or DEFAULT_NORMALIZATION
    if not normalization_path.exists():
        raise SystemExit(
            f"Nhánh B cần chuẩn hoá train-only DataSED (F2) tại {normalization_path}, "
            "không tồn tại -- ADR-0020 §4"
        )
    encoder = panns_encoder(knobs, normalization_path=normalization_path)
    report = encoder.load_audioset_pretrained(args.audioset_checkpoint)
    return encoder, {
        "weight_source": "audioset",
        "checkpoint_path": str(args.audioset_checkpoint),
        "checkpoint_sha256": sha256_file(args.audioset_checkpoint),
        "checkpoint_parameter_fraction": report.transplanted_parameters
        / report.checkpoint_parameters,
        "normalization_path": str(normalization_path),
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    validate_checkpoint_flags(args)
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    seed_everything(args.seed)
    device = torch.device(args.device)
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    class_ids = taxonomy.polyphonic_class_ids

    knobs = resolve_recipe(args)
    feature_set = ENCODER_FEATURE_SET[args.encoder]
    frame_rate = ENCODER_FRAME_RATE[args.encoder]
    window_frames = round(WINDOW_SECONDS * frame_rate)
    hop_frames = round(HOP_SECONDS * frame_rate)
    batch_size = args.batch_size or (PANNS_BATCH_SIZE if args.encoder == "panns" else 8)
    config = SedTrainingConfig(
        epochs=int(knobs["epochs"]),
        batch_size=batch_size,
        learning_rate=float(knobs["learning_rate"]),
        seed=args.seed,
        window_frames=window_frames,
        hop_frames=hop_frames,
        encoder_learning_rate=knobs["encoder_learning_rate"],
        warmup_epochs=int(knobs["warmup_epochs"]),
        cosine_decay=bool(knobs["cosine_decay"]),
        select_metric=str(knobs["select_metric"]),
        mixup_p=float(knobs["mixup_p"]),
        filter_augment_p=float(knobs["filter_augment_p"]),
    )

    joined, events = load_datased_tables(feature_set)
    loaders: dict[str, DataLoader] = {}
    for split in ("train", "validation", "test"):
        dataset = split_dataset(
            joined, events, split, feature_set=feature_set, class_ids=class_ids,
            frame_rate=frame_rate, window_frames=config.window_frames,
            hop_frames=config.hop_frames,
            random_crop=bool(knobs["random_crop"]) and split == "train",
        )
        loaders[split] = DataLoader(
            dataset,
            batch_size=config.batch_size,
            shuffle=split == "train",
            num_workers=0,
            pin_memory=device.type == "cuda",
        )

    train_ids = set(joined.loc[joined["split"] == "train", "recording_id"])
    train_events = events[events["recording_id"].isin(train_ids)]
    pos_weight = estimate_pos_weight(
        class_ids,
        train_events[["class_id", "onset_s", "offset_s"]].itertuples(index=False, name=None),
        float(joined.loc[joined["split"] == "train", "duration_s"].sum()),
        maximum=float(knobs["pos_weight_cap"]),
    )
    encoder, weight_info = build_encoder(args, knobs)
    if args.encoder == "panns":
        model = sed_model(knobs, len(class_ids), encoder)
    else:
        model = SoundEventDetector(classes=len(class_ids), hidden_size=int(knobs["rnn_hidden"]),
                                   rnn_layers=int(knobs["rnn_layers"]),
                                   upsample=str(knobs["upsample"]))
    cap = float(knobs["pos_weight_cap"])

    run = create_run_directory(ROOT, "sed_polyphonic")
    manifest = {
        "command": sys.argv,
        "config": {
            **asdict(config),
            "encoder_type": args.encoder,
            "feature_set": feature_set,
            "frame_rate": frame_rate,
            "pos_weight_cap": cap if math.isfinite(cap) else None,
            "recipe": args.recipe,
            **{key: knobs[key] for key in ("time_pooling", "rnn_hidden", "rnn_layers",
                                           "upsample", "random_crop", "model_version")},
            **weight_info,
        },
        "class_ids": class_ids,
        "taxonomy_sha256": taxonomy.checksum,
        "split_sha256": sha256_file(SPLITS_PATH),
        "data_manifest_sha256": sha256_file(
            ROOT / "data" / "annotations" / "datased_polyphonic_events.csv"
        ),
        "git": git_state(ROOT),
        "environment": runtime_environment(),
        "dataset_windows": {name: len(loader.dataset) for name, loader in loaders.items()},
        "pos_weight": pos_weight.tolist(),
        "complete": False,
    }
    write_json(run / "manifest.json", manifest)
    history, best_path = train_sed(
        model,
        loaders,
        device=device,
        pos_weight=pos_weight,
        config=config,
        checkpoint_directory=run / "checkpoints",
    )
    write_json(run / "logs" / "history.json", {"epochs": history})
    metrics = best_validation_metrics(history, config.select_metric)

    checkpoint = torch.load(best_path, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["model_state"])

    # `predictions/dev.npz` luôn được ghi (kể cả không --evaluate-test): W3.6 quét
    # threshold trên dev không phụ thuộc việc test đã mở hay chưa. Split CSV/loaders
    # dùng "validation"; contract prediction dùng literal "dev" — ánh xạ tường minh
    # ở đây, không đổi tên cột split (ADR-0020 §6).
    dev_predictions = collect_predictions(
        model,
        loaders["validation"],
        device=device,
        class_ids=class_ids,
        split="dev",
        model_version=str(knobs["model_version"]),
        taxonomy_sha256=taxonomy.checksum,
        frame_rate=frame_rate,
    )
    dev_sha256 = save_predictions(
        run / "predictions" / "dev.npz", dev_predictions, expected_class_ids=class_ids
    )

    if args.evaluate_test:
        with torch.inference_mode():
            metrics["test"] = run_epoch(
                model,
                loaders["test"],
                device=device,
                pos_weight=pos_weight.to(device),
                optimizer=None,
                scaler=None,
                threshold=config.threshold,
            )
        test_predictions = collect_predictions(
            model,
            loaders["test"],
            device=device,
            class_ids=class_ids,
            split="test",
            model_version=str(knobs["model_version"]),
            taxonomy_sha256=taxonomy.checksum,
            frame_rate=frame_rate,
        )
        test_sha256 = save_predictions(
            run / "predictions" / "test.npz", test_predictions, expected_class_ids=class_ids
        )
        metrics["test_predictions_sha256"] = test_sha256
    metrics["dev_predictions_sha256"] = dev_sha256
    write_json(run / "metrics.json", metrics)
    manifest["complete"] = True
    manifest["best_checkpoint"] = str(best_path.relative_to(run))
    write_json(run / "manifest.json", manifest)
    print(json.dumps({"run": str(run), "metrics": metrics}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
