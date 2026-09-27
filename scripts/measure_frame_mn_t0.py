"""Track 2b T0 gate, step 3 (ADR-0032 §4): does full fine-tuning of frame_mn10 fit this GPU?

    .venv/Scripts/python.exe -m scripts.measure_frame_mn_t0 \
        [--audioset-classes <PretrainedSED data_util/audioset_classes.py>]

Unlike Track 2a the whole network trains, so memory is measured on a complete training step
(forward, backward, AdamW step under autocast) at several batch sizes, not on a forward pass.
Time per epoch is measured end to end -- DataLoader reads and random crops from the waveform cache
(`num_workers=0`, as `train_sed`), mixup, step -- because Track 2a's encoder-only estimate turned
out 4-5x too optimistic. Only train/dev windows are read, never test.

Writes `docs/measurements/track2_t0_frame_mn_<date>.{json,md}`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import runpy
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd
import torch
from torch.utils.data import DataLoader

from ml.datasets.waveforms import SedWaveformDataset
from ml.models.frame_mn_finetune import FrameMnSED
from ml.taxonomy import load_taxonomy
from ml.training.augment import mixup
from ml.training.sed import masked_bce
from scripts.measure_beats_t0 import batch_of, peak_mb
from scripts.train_sed import load_datased_tables, split_dataset

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "artifacts" / "checkpoints" / "frame_mn10_strong_1.pt"
BATCH_SIZES = (8, 16, 24, 32, 48)
TIMED_STEPS = 15


def datasets() -> tuple[SedWaveformDataset, SedWaveformDataset, pd.DataFrame]:
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    joined, events = load_datased_tables("logmel_panns_v1")
    common = {"feature_set": "logmel_panns_v1", "class_ids": taxonomy.polyphonic_class_ids,
              "frame_rate": 100.0, "window_frames": 1000, "hop_frames": 1000, "waveform": True}
    train = split_dataset(joined, events, "train", random_crop=True, **common)
    dev = split_dataset(joined, events, "validation", **common)
    return train, dev, events


def fresh_model() -> FrameMnSED:
    model = FrameMnSED(21)
    model.load_pretrained(CHECKPOINT)
    return model.cuda().train()


def train_step(model: FrameMnSED, optimizer: torch.optim.Optimizer,
               scaler: torch.amp.GradScaler, batch: tuple[torch.Tensor, ...]) -> None:
    waveforms, targets, valid = (item.cuda(non_blocking=True) for item in batch)
    waveforms, targets, valid = mixup(waveforms, targets, valid)
    with torch.autocast("cuda"):
        loss = masked_bce(model(waveforms), targets, valid, torch.ones(21, device="cuda"))
    optimizer.zero_grad(set_to_none=True)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()


def step_peak_mb(train: SedWaveformDataset, size: int) -> float | str:
    model = fresh_model()
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
    scaler = torch.amp.GradScaler("cuda")
    batch = next(iter(DataLoader(train, batch_size=size, shuffle=False)))
    try:
        train_step(model, optimizer, scaler, batch)  # optimizer state allocated here
        return round(peak_mb(lambda: train_step(model, optimizer, scaler, batch)), 1)
    except torch.OutOfMemoryError:
        return "OOM"


def memory_by_batch(train: SedWaveformDataset) -> dict[int, float | str]:
    peaks: dict[int, float | str] = {}
    for size in BATCH_SIZES:
        peaks[size] = step_peak_mb(train, size)
        torch.cuda.empty_cache()
    return peaks


def epoch_time(train: SedWaveformDataset, dev: SedWaveformDataset, batch: int
               ) -> dict[str, float]:
    model = fresh_model()
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
    scaler = torch.amp.GradScaler("cuda")
    loader = iter(DataLoader(train, batch_size=batch, shuffle=True, num_workers=0,
                             pin_memory=True))
    train_step(model, optimizer, scaler, next(loader))  # warm-up (cuDNN autotune, allocator)
    torch.cuda.synchronize()
    began = time.perf_counter()
    for _ in range(TIMED_STEPS):
        train_step(model, optimizer, scaler, next(loader))
    torch.cuda.synchronize()
    train_step_s = (time.perf_counter() - began) / TIMED_STEPS
    model.eval()
    dev_loader = iter(DataLoader(dev, batch_size=batch, shuffle=False, num_workers=0))
    began = time.perf_counter()
    with torch.inference_mode(), torch.autocast("cuda"):
        for _ in range(5):
            model(next(dev_loader)[0].cuda()).float().sigmoid().cpu()
    torch.cuda.synchronize()
    eval_batch_s = (time.perf_counter() - began) / 5
    train_batches = len(train) // batch + (len(train) % batch > 0)
    dev_batches = len(dev) // batch + (len(dev) % batch > 0)
    return {"batch_size": batch, "train_step_seconds": train_step_s,
            "eval_batch_seconds": eval_batch_s,
            # run_epoch evaluates train on the fly; dev is one extra inference pass per epoch
            "estimated_seconds_per_epoch": train_batches * train_step_s
            + dev_batches * eval_batch_s}


def precision_check(dev: SedWaveformDataset) -> dict[str, float]:
    model = fresh_model().eval()
    windows = batch_of(dev, 8).cuda()
    with torch.no_grad():
        full = model.embed(windows)
        with torch.autocast("cuda"):
            half = model.embed(windows).float()
    cosine = torch.nn.functional.cosine_similarity(full, half, dim=-1)
    return {"embedding_fp16_vs_fp32_max_abs": (full - half).abs().max().item(),
            "embedding_fp16_vs_fp32_min_cosine": cosine.min().item()}


def semantic_check(dev: SedWaveformDataset, events: pd.DataFrame, classes_path: Path
                   ) -> dict[str, object]:
    names = runpy.run_path(str(classes_path))["as_strong_train_classes"]
    model = FrameMnSED(len(names))
    model.load_pretrained(CHECKPOINT)
    state = torch.load(CHECKPOINT, map_location="cpu", weights_only=True)
    model.head.load_state_dict({"weight": state["strong_head.weight"],
                                "bias": state["strong_head.bias"]})
    model = model.cuda().eval()
    class_of = {index: class_id for class_id, index in dev.class_index.items()}
    dev_events = events[events["recording_id"].isin({w.recording_id for w in dev.windows})]
    rows = []
    for class_id, group in dev_events.groupby("class_id"):
        event = group.sort_values(["recording_id", "onset_s"]).iloc[0]
        index = next(i for i, w in enumerate(dev.windows) if w.recording_id ==
                     event.recording_id and w.start_frame <= event.onset_s * 100 <
                     w.start_frame + 1000)
        waveform, target, _ = dev[index]
        with torch.no_grad(), torch.autocast("cuda"):
            probabilities = model(waveform[None].cuda()).float().sigmoid()[0]
        present = sorted(class_of[c] for c in torch.nonzero(target.sum(0)).flatten().tolist())
        top = torch.topk(probabilities.amax(0), 3)
        rows.append({"class_id": class_id, "recording_id": event.recording_id,
                     "window_start_s": dev.windows[index].start_frame / 100,
                     "labels_in_window": present,
                     "top3": [[names[i], round(v, 3)] for v, i in
                              zip(top.values.tolist(), top.indices.tolist(), strict=True)]})
    return {"audioset_classes_sha256": hashlib.sha256(classes_path.read_bytes()).hexdigest(),
            "rows": rows}


def to_markdown(result: dict[str, object]) -> str:
    speed = result["epoch_time"]
    lines = [f"# Track 2b — cổng T0 bước 3 (frame_mn10 fine-tune toàn bộ), {result['date']}", "",
             "Sinh bởi `scripts/measure_frame_mn_t0.py`; chỉ cửa sổ train/dev, không chạm test.",
             "", "| Đo | Giá trị |", "|---|---|",
             f"| Checkpoint SHA-256 | `{result['load']['checkpoint_sha256']}` |",
             f"| Tensor / tham số encoder | {result['load']['loaded_tensors']} / "
             f"{result['load']['loaded_parameters']:,} |",
             f"| GPU | {result['gpu']} ({result['gpu_total_mb']} MB) |"]
    lines += [f"| Đỉnh VRAM một bước train đầy đủ (mixup, fwd, bwd, AdamW), batch {size} | "
              f"{mb if mb == 'OOM' else f'{mb} MB'} |"
              for size, mb in result["train_step_peak_mb"].items()]
    lines += [f"| Batch chọn | {speed['batch_size']} |",
              f"| Giây/bước train, gồm đọc đĩa + crop (batch {speed['batch_size']}) | "
              f"{speed['train_step_seconds']:.3f} |",
              f"| Giây/batch suy luận dev | {speed['eval_batch_seconds']:.3f} |",
              f"| Ước tính giây/epoch (train {result['train_windows']} + dev "
              f"{result['dev_windows']} cửa sổ) | {speed['estimated_seconds_per_epoch']:.0f} |"]
    lines += [f"| {key} | {value:.3g} |" for key, value in result["precision"].items()]
    if "semantic" in result:
        lines += ["", "## Head AudioSet-strong của chính checkpoint trên một event dev mỗi lớp",
                  "", "Kiểm đường ống frontend + mạng có \"nghe\" đúng không; không phải metric.",
                  "", "| Lớp DataSED | Recording @ s | Nhãn trong cửa sổ | Top-3 AudioSet |",
                  "|---|---|---|---|"]
        lines += [f"| {r['class_id']} | {r['recording_id']} @ {r['window_start_s']:.0f} | "
                  f"{', '.join(r['labels_in_window'])} | "
                  f"{'; '.join(f'{n} {p:.2f}' for n, p in r['top3'])} |"
                  for r in result["semantic"]["rows"]]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--audioset-classes", type=Path, default=None)
    parser.add_argument("--batch-size", type=int, default=24,
                        help="batch dùng để đo thời gian (chọn sau khi xem bảng VRAM)")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    torch.manual_seed(0)
    report = FrameMnSED(21).load_pretrained(CHECKPOINT)
    train, dev, events = datasets()
    peaks = memory_by_batch(train)
    if peaks.get(args.batch_size) == "OOM":
        raise SystemExit(f"batch {args.batch_size} không vừa GPU: {peaks}")
    result: dict[str, object] = {
        "date": date.today().isoformat(),
        "load": {"checkpoint_sha256": report.checkpoint_sha256,
                 "loaded_tensors": report.loaded_tensors,
                 "loaded_parameters": report.loaded_parameters,
                 "ignored_keys": list(report.ignored_keys)},
        "gpu": torch.cuda.get_device_name(0),
        "gpu_total_mb": round(torch.cuda.get_device_properties(0).total_memory / 2**20),
        "train_step_peak_mb": peaks, "train_windows": len(train), "dev_windows": len(dev),
        "precision": precision_check(dev),
        "epoch_time": epoch_time(train, dev, args.batch_size),
    }
    if args.audioset_classes:
        result["semantic"] = semantic_check(dev, events, args.audioset_classes)
    stem = ROOT / "docs" / "measurements" / f"track2_t0_frame_mn_{date.today():%Y%m%d}"
    stem.with_suffix(".json").write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                         encoding="utf-8")
    stem.with_suffix(".md").write_text(to_markdown(result), encoding="utf-8")
    print(to_markdown(result))


if __name__ == "__main__":
    main()
