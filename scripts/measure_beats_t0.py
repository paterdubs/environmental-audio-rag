"""Track 2a T0 gate, step 3 (ADR-0032 §4): does frozen BEATs fit and run on this GPU?

    .venv/Scripts/python.exe -m scripts.measure_beats_t0 \
        [--audioset-classes <PretrainedSED data_util/audioset_classes.py>]

Measured on real dev windows (the same `SedWaveformDataset` the training uses), never test:
- load report of `BEATs_strong_1.pt` (SHA-256 checked);
- GPU vs CPU fbank, and fp16 autocast vs fp32 embeddings (the training path uses autocast);
- peak VRAM of the encoder forward per batch size, and of one head training step at batch 24;
- encoder throughput at batch 24 -> seconds per epoch of the T2a recipe;
- optional semantic check: the checkpoint's own AudioSet-strong head on one dev event per class,
  top-3 AudioSet labels next to the DataSED labels of that window (class names from PretrainedSED
  commit 1aa47e48, file passed in, SHA-256 recorded).

Writes `docs/measurements/track2_t0_beats_<date>.{json,md}`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import runpy
import sys
import time
from collections.abc import Callable
from datetime import date
from pathlib import Path

import pandas as pd
import torch

from ml.datasets.waveforms import SedWaveformDataset
from ml.models.beats_frozen import FrozenBeatsEncoder
from ml.models.embedding_sed import EmbeddingSequenceSED
from ml.taxonomy import load_taxonomy
from scripts.train_sed import load_datased_tables, split_dataset

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "artifacts" / "checkpoints" / "BEATs_strong_1.pt"
BATCH = 24


def dev_dataset() -> tuple[SedWaveformDataset, int, pd.DataFrame]:
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    joined, events = load_datased_tables("logmel_panns_v1")
    dataset = split_dataset(joined, events, "validation", feature_set="logmel_panns_v1",
                            class_ids=taxonomy.polyphonic_class_ids, frame_rate=100.0,
                            window_frames=1000, hop_frames=1000, waveform=True)
    train = split_dataset(joined, events, "train", feature_set="logmel_panns_v1",
                          class_ids=taxonomy.polyphonic_class_ids, frame_rate=100.0,
                          window_frames=1000, hop_frames=1000, waveform=True)
    return dataset, len(train), events


def batch_of(dataset: SedWaveformDataset, size: int, start: int = 0) -> torch.Tensor:
    return torch.stack([dataset[(start + i) % len(dataset)][0] for i in range(size)])


def peak_mb(run: Callable[[], None]) -> float:
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    run()
    torch.cuda.synchronize()
    return torch.cuda.max_memory_allocated() / 2**20


def precision_checks(encoder: FrozenBeatsEncoder, windows: torch.Tensor) -> dict[str, float]:
    gpu = windows.cuda()  # fbank has no parameters: same method on either device
    fbank_gap = (encoder.fbank(gpu).cpu() - encoder.fbank(windows)).abs().max().item()
    with torch.no_grad():
        full = encoder(gpu)
        with torch.autocast("cuda"):
            half = encoder(gpu).float()
    cosine = torch.nn.functional.cosine_similarity(full, half, dim=-1)
    return {"fbank_gpu_vs_cpu_max_abs": fbank_gap,
            "embedding_fp16_vs_fp32_max_abs": (full - half).abs().max().item(),
            "embedding_fp16_vs_fp32_min_cosine": cosine.min().item()}


def memory_and_speed(encoder: FrozenBeatsEncoder, dataset: SedWaveformDataset
                     ) -> dict[str, object]:
    def forward(size: int) -> None:
        with torch.no_grad(), torch.autocast("cuda"):
            encoder(batch_of(dataset, size).cuda())

    encoder_peak = {size: round(peak_mb(lambda s=size: forward(s)), 1) for size in (8, 16, 24, 32)}
    head = EmbeddingSequenceSED(21, input_size=768, output_frames=1000).cuda()
    optimizer = torch.optim.AdamW(head.parameters(), lr=1e-3)
    scaler = torch.amp.GradScaler("cuda")

    def train_step() -> None:
        with torch.no_grad(), torch.autocast("cuda"):
            embeddings = encoder(batch_of(dataset, BATCH).cuda()).float()
        with torch.autocast("cuda"):
            loss = head(embeddings).float().sigmoid().mean()
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad(set_to_none=True)

    step_peak = round(peak_mb(train_step), 1)
    batches = [batch_of(dataset, BATCH, start=i * BATCH) for i in range(6)]
    forward(BATCH)  # warm-up
    torch.cuda.synchronize()
    began = time.perf_counter()
    with torch.no_grad(), torch.autocast("cuda"):
        for batch in batches:
            encoder(batch.cuda())
    torch.cuda.synchronize()
    per_window = (time.perf_counter() - began) / (len(batches) * BATCH)
    return {"encoder_forward_peak_mb": encoder_peak, "head_train_step_peak_mb_batch24": step_peak,
            "encoder_seconds_per_window_batch24": per_window,
            "gpu": torch.cuda.get_device_name(0),
            "gpu_total_mb": round(torch.cuda.get_device_properties(0).total_memory / 2**20)}


def semantic_check(encoder: FrozenBeatsEncoder, dataset: SedWaveformDataset,
                   events: pd.DataFrame, classes_path: Path) -> dict[str, object]:
    names = runpy.run_path(str(classes_path))["as_strong_train_classes"]
    state = torch.load(CHECKPOINT, map_location="cpu", weights_only=True, mmap=True)
    head = torch.nn.Linear(768, len(names))
    head.load_state_dict({"weight": state["strong_head.weight"], "bias": state["strong_head.bias"]})
    head = head.cuda()
    class_of = {index: class_id for class_id, index in dataset.class_index.items()}
    dev_events = events[events["recording_id"].isin({w.recording_id for w in dataset.windows})]
    rows = []
    for class_id, group in dev_events.groupby("class_id"):
        event = group.sort_values(["recording_id", "onset_s"]).iloc[0]
        index = next(i for i, w in enumerate(dataset.windows) if w.recording_id ==
                     event.recording_id and w.start_frame <= event.onset_s * 100 <
                     w.start_frame + 1000)
        with torch.no_grad(), torch.autocast("cuda"):
            probabilities = head(encoder(dataset[index][0][None].cuda())).float().sigmoid()[0]
        target = dataset[index][1]
        present = sorted(class_of[c] for c in torch.nonzero(target.sum(0)).flatten().tolist())
        top = torch.topk(probabilities.amax(0), 3)
        rows.append({"class_id": class_id, "recording_id": event.recording_id,
                     "window_start_s": dataset.windows[index].start_frame / 100,
                     "labels_in_window": present,
                     "beats_top3": [[names[i], round(v, 3)] for v, i in
                                    zip(top.values.tolist(), top.indices.tolist(), strict=True)]})
    return {"audioset_classes_sha256": hashlib.sha256(classes_path.read_bytes()).hexdigest(),
            "rows": rows}


def to_markdown(result: dict[str, object]) -> str:
    speed = result["memory_and_speed"]
    lines = [f"# Track 2a — cổng T0 bước 3 (BEATs đóng băng), {result['date']}", "",
             "Sinh bởi `scripts/measure_beats_t0.py`; chỉ cửa sổ dev, không chạm test.", "",
             "| Đo | Giá trị |", "|---|---|",
             f"| Checkpoint SHA-256 | `{result['load']['checkpoint_sha256']}` |",
             f"| Tensor / tham số encoder | {result['load']['loaded_tensors']} / "
             f"{result['load']['loaded_parameters']:,} |",
             f"| GPU | {speed['gpu']} ({speed['gpu_total_mb']} MB) |"]
    lines += [f"| Đỉnh VRAM forward encoder, batch {size} | {mb} MB |"
              for size, mb in speed["encoder_forward_peak_mb"].items()]
    lines += [f"| Đỉnh VRAM một bước train head, batch {BATCH} | "
              f"{speed['head_train_step_peak_mb_batch24']} MB |",
              f"| Encoder, giây/cửa sổ (batch {BATCH}, fp16) | "
              f"{speed['encoder_seconds_per_window_batch24']:.4f} |",
              f"| Ước tính giây/epoch (train {result['train_windows']} + dev "
              f"{result['dev_windows']} cửa sổ) | {result['estimated_seconds_per_epoch']:.0f} |"]
    lines += [f"| {key} | {value:.3g} |" for key, value in result["precision"].items()]
    if "semantic" in result:
        lines += ["", "## Head AudioSet-strong của chính checkpoint trên một event dev mỗi lớp",
                  "", "Kiểm đường ống encoder có \"nghe\" đúng không; không phải metric.", "",
                  "| Lớp DataSED | Recording @ s | Nhãn trong cửa sổ | Top-3 AudioSet |",
                  "|---|---|---|---|"]
        lines += [f"| {r['class_id']} | {r['recording_id']} @ {r['window_start_s']:.0f} | "
                  f"{', '.join(r['labels_in_window'])} | "
                  f"{'; '.join(f'{n} {p:.2f}' for n, p in r['beats_top3'])} |"
                  for r in result["semantic"]["rows"]]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--audioset-classes", type=Path, default=None)
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    torch.manual_seed(0)
    encoder = FrozenBeatsEncoder()
    report = encoder.load_pretrained(CHECKPOINT)
    encoder.cuda()
    dataset, train_windows, events = dev_dataset()
    result: dict[str, object] = {
        "date": date.today().isoformat(),
        "load": {"checkpoint_sha256": report.checkpoint_sha256,
                 "loaded_tensors": report.loaded_tensors,
                 "loaded_parameters": report.loaded_parameters,
                 "ignored_keys": list(report.ignored_keys)},
        "precision": precision_checks(encoder, batch_of(dataset, 8)),
    }
    speed = memory_and_speed(encoder, dataset)
    result.update(memory_and_speed=speed, train_windows=train_windows,
                  dev_windows=len(dataset),
                  estimated_seconds_per_epoch=speed["encoder_seconds_per_window_batch24"]
                  * (train_windows + len(dataset)))
    if args.audioset_classes:
        result["semantic"] = semantic_check(encoder, dataset, events, args.audioset_classes)
    stem = ROOT / "docs" / "measurements" / f"track2_t0_beats_{date.today():%Y%m%d}"
    stem.with_suffix(".json").write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                         encoding="utf-8")
    stem.with_suffix(".md").write_text(to_markdown(result), encoding="utf-8")
    print(to_markdown(result))


if __name__ == "__main__":
    main()
