"""D1 — Train E1: `HierarchicalAudioClassifier(PannsCNN14Encoder)` trên DataSEC.

    .venv/Scripts/python.exe -m scripts.train_classifier --epochs 12 --device cuda

Đây là bước giữa của nhánh C (ADR-0002): PANNs CNN14 pretrained AudioSet (F1)
→ DataSEC (bước này) → DataSED. Viết lại hoàn toàn theo ADR-0019 — bản trước
đọc hai file chưa từng tồn tại trong git và dùng model không ứng nhánh nào.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import torch
from torch.utils.data import DataLoader

from ml.dataops.registry import keys_for
from ml.datasets.datasec import (
    DataSECFeatureDataset,
    DataSECLabelSpace,
    build_datasec_manifest,
    make_class_balanced_sampler,
)
from ml.models import HierarchicalAudioClassifier, PannsCNN14Encoder, build_family_mask
from ml.models.hierarchical import HierarchicalLossWeights
from ml.taxonomy import load_taxonomy
from ml.training.classification import (
    ClassificationTrainingConfig,
    inverse_frequency_weights,
    run_hierarchical_epoch,
    train_hierarchical_classifier,
)
from ml.training.common import (
    create_run_directory,
    git_state,
    runtime_environment,
    seed_everything,
    sha256_file,
    write_json,
)

ROOT = Path(__file__).resolve().parents[1]
FEATURE_SET = "logmel_panns_v1"
FRAMES = 500  # 5 s @ 100 fps — khớp window đã đo VRAM ở C2 (batch 32 an toàn)
SUPPORT_THRESHOLD = 10  # ADR-0006 §3/§4


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--seed", type=int, default=20260922)
    parser.add_argument("--evaluate-test", action="store_true")
    parser.add_argument("--device", default="cuda")
    parser.add_argument(
        "--checkpoint",
        default=None,
        help="Checkpoint PANNs AudioSet đã xác minh (F1). Bỏ trống = encoder scratch, "
        "PHẢI ghi rõ trong báo cáo đây không phải nhánh C như ADR-0002 định nghĩa.",
    )
    parser.add_argument(
        "--normalization",
        default=str(ROOT / "data" / "manifests" / f"datasec_{FEATURE_SET}_train_normalization.npz"),
        help="Thống kê z-score train-only thay bn0 (F1, ADR-0018 §3).",
    )
    parser.add_argument("--consistency-weight", type=float, default=0.5)
    parser.add_argument("--subclass-weight", type=float, default=1.0)
    return parser.parse_args()


def load_rows(label_mode: str = "classification") -> pd.DataFrame:
    """Nạp bảng nối `(coarse, subclass, feature, split)` theo `file_id` qua registry.

    Không dùng `clip_id` hay `data/splits/datasec.csv` — hai thứ đó chưa từng
    tồn tại (ADR-0019). Join theo `file_id` tự động loại các clip đã bị D3 loại
    khỏi split, vì split đóng băng vốn đã không chứa chúng.
    """
    keys = keys_for("datasec")
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    inventory = pd.read_csv(ROOT / "data" / "manifests" / keys.manifest)
    manifest = build_datasec_manifest(inventory, taxonomy)

    features = pd.read_csv(ROOT / "data" / "manifests" / f"datasec_{FEATURE_SET}.csv")
    splits = pd.read_csv(ROOT / "data" / "splits" / f"datasec_{label_mode}.csv")

    rows = manifest.merge(
        features[["file_id", "feature_relative_path"]], on="file_id", validate="one_to_one"
    ).merge(splits[["file_id", "split"]], on="file_id", validate="one_to_one")
    if rows.empty:
        raise SystemExit("Join file_id giữa manifest/feature/split ra rỗng — kiểm namespace.")
    return rows


def supported_subclass_ids(rows: pd.DataFrame, label_space: DataSECLabelSpace) -> set[int]:
    """Subclass có `n_test >= 10` — cố định một lần, dùng xuyên suốt mọi epoch.

    Tính lại theo từng tập con (train/validation/test riêng biệt) sẽ làm hai số
    macro-F1 không so sánh được qua các epoch, vì "n>=10" mỗi lần trỏ tới một
    tập node khác nhau (ADR-0019 §4).
    """
    index = {value: i for i, value in enumerate(label_space.subclass_ids)}
    counts = rows.loc[rows["split"] == "test", "subclass_id"].value_counts()
    return {index[name] for name, count in counts.items() if count >= SUPPORT_THRESHOLD}


def build_loaders(
    rows: pd.DataFrame, label_space: DataSECLabelSpace, *, batch_size: int
) -> dict[str, DataLoader]:
    feature_root = ROOT / "data" / "features" / "datasec" / FEATURE_SET
    loaders: dict[str, DataLoader] = {}
    for split in ("train", "validation", "test"):
        subset = rows[rows["split"] == split]
        if subset.empty:
            raise SystemExit(f"Split {split!r} rỗng sau khi join — kiểm dữ liệu trước khi train.")
        dataset = DataSECFeatureDataset(
            subset, feature_root=feature_root, label_space=label_space,
            frames=FRAMES, random_crop=split == "train",
        )
        sampler = make_class_balanced_sampler(dataset, level="coarse", seed=20260922) \
            if split == "train" else None
        loaders[split] = DataLoader(
            dataset,
            batch_size=batch_size,
            sampler=sampler,
            shuffle=sampler is None and split == "train",
            num_workers=0,
        )
    return loaders


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    seed_everything(args.seed)
    device = torch.device(args.device)

    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    label_space = DataSECLabelSpace.from_taxonomy(taxonomy)
    rows = load_rows()
    config = ClassificationTrainingConfig(
        epochs=args.epochs, batch_size=args.batch_size,
        learning_rate=args.learning_rate, seed=args.seed, frames=FRAMES,
    )
    loaders = build_loaders(rows, label_space, batch_size=config.batch_size)
    supported = supported_subclass_ids(rows, label_space)
    family_mask = build_family_mask(taxonomy, label_space.coarse_ids, label_space.subclass_ids)

    train_coarse_labels = [
        label_space.coarse_ids.index(str(class_id))
        for class_id in rows.loc[rows["split"] == "train", "class_id"]
    ]
    coarse_weight = inverse_frequency_weights(train_coarse_labels, len(label_space.coarse_ids))

    normalization_path = Path(args.normalization)
    encoder = PannsCNN14Encoder(
        normalization_path=normalization_path if normalization_path.exists() else None
    )
    checkpoint_report = None
    if args.checkpoint:
        checkpoint_report = encoder.load_audioset_pretrained(args.checkpoint)
    model = HierarchicalAudioClassifier(
        encoder, num_coarse=len(label_space.coarse_ids), num_subclass=len(label_space.subclass_ids)
    )
    loss_weights = HierarchicalLossWeights(
        subclass=args.subclass_weight, consistency=args.consistency_weight
    )

    run = create_run_directory(ROOT, "classifier_datasec")
    manifest = {
        "command": sys.argv,
        "config": {
            **asdict(config),
            "loss_weights": asdict(loss_weights),
            "checkpoint_path": args.checkpoint,
            "checkpoint_sha256": sha256_file(Path(args.checkpoint)) if args.checkpoint else None,
            "checkpoint_parameter_fraction": (
                checkpoint_report.parameter_fraction if checkpoint_report else None
            ),
            "normalization_path": str(normalization_path) if normalization_path.exists() else None,
        },
        "class_ids": list(label_space.coarse_ids),
        "primary_metric": "coarse_macro_f1",
        "taxonomy_sha256": taxonomy.checksum,
        "split_sha256": sha256_file(ROOT / "data" / "splits" / "datasec_classification.csv"),
        "data_manifest_sha256": sha256_file(
            ROOT / "data" / "manifests" / f"datasec_{FEATURE_SET}.csv"
        ),
        "git": git_state(ROOT),
        "environment": runtime_environment(),
        "dataset_items": {name: len(loader.dataset) for name, loader in loaders.items()},
        "supported_subclass_ids": sorted(supported),
        "complete": False,
    }
    write_json(run / "manifest.json", manifest)

    history, best_path = train_hierarchical_classifier(
        model, loaders, device=device, coarse_weight=coarse_weight, family_mask=family_mask,
        supported_subclass_ids=supported, config=config,
        checkpoint_directory=run / "checkpoints", loss_weights=loss_weights,
    )
    write_json(run / "logs" / "history.json", {"epochs": history})
    metrics = {
        "best_validation_coarse_macro_f1": max(
            item["validation"]["coarse_macro_f1"] for item in history
        ),
    }
    if args.evaluate_test:
        checkpoint = torch.load(best_path, map_location=device, weights_only=True)
        model.load_state_dict(checkpoint["model_state"])
        with torch.inference_mode():
            metrics["test"] = run_hierarchical_epoch(
                model, loaders["test"], device=device, coarse_weight=coarse_weight.to(device),
                family_mask=family_mask, supported_subclass_ids=supported,
                optimizer=None, scaler=None, loss_weights=loss_weights,
            )
    write_json(run / "metrics.json", metrics)
    manifest["complete"] = True
    manifest["best_checkpoint"] = str(best_path.relative_to(run))
    write_json(run / "manifest.json", manifest)
    print(json.dumps({"run": str(run), "metrics": metrics}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
