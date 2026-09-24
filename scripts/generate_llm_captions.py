"""W5 5.6 — sinh caption unconstrained (nhánh đối chứng RQ2) bằng LLM cục bộ.

    # Khởi động server trước (xem ADR-0022, ml/configs/caption_llm.yaml):
    artifacts/llm/llama.cpp-b11158/llama-server.exe -m artifacts/llm/<gguf> \\
        -ngl 99 -c 4096 -np 1 --jinja --port 8081
    .venv/Scripts/python.exe -m scripts.generate_llm_captions ml/runs/<sed_run> --split dev

Mỗi lần chạy sinh CẢ HAI mức trên cùng một tập recording (evaluation_protocol §8.1):
`oracle` (timeline = ground truth DataSED) và `e2e` (timeline = SED prediction đã
đóng băng của run). Chỉ SINH caption, không chấm điểm: chấm điểm cần lexicon đã
đóng băng, và lexicon chỉ được mở rộng trên caption dev (ADR-0022 §3). Vì vậy
`--split test` bị chặn trừ khi truyền đúng SHA-256 của lexicon hiện tại.

Output bất biến, trong `<run>/captions/`: `unconstrained_<split>.jsonl` (một dòng
mỗi recording × mức) + `unconstrained_<split>.meta.json` (provenance).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd

from ml.captioning.lexicon import CaptionLexicon
from ml.captioning.llm import (
    PROMPT_VERSION,
    HttpChatTransport,
    LLMConfig,
    UnconstrainedLLMCaptioner,
    prompt_sha256,
)
from ml.captioning.timeline import canonicalize_timeline
from ml.evaluation.predictions import load_predictions
from ml.postprocessing import process_recordings, stack_predictions_by_recording
from ml.postprocessing.calibration import validate_postproc_artifact
from ml.taxonomy import Taxonomy, load_taxonomy
from ml.training.common import git_state, sha256_file
from scripts.report_threshold_ablation import priors_from_postproc

ROOT = Path(__file__).resolve().parents[1]
LEVELS = ("oracle", "e2e")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    parser.add_argument("--config", type=Path, default=ROOT / "ml/configs/caption_llm.yaml")
    parser.add_argument("--frozen-lexicon-sha256", default=None)
    parser.add_argument("--limit", type=int, default=None, help="chỉ để smoke-test")
    return parser.parse_args()


def check_test_gate(split: str, lexicon_sha: str, frozen_sha: str | None) -> None:
    if split != "test":
        return
    if frozen_sha != lexicon_sha:
        raise SystemExit(
            "Từ chối sinh caption test: lexicon chưa được đóng băng. Truyền "
            f"--frozen-lexicon-sha256 {lexicon_sha} chỉ sau khi đã ghi hash này vào ADR-0022."
        )


def e2e_timelines(run_dir: Path, split: str, taxonomy: Taxonomy) -> dict[str, dict[str, Any]]:
    """Timeline từ prediction đóng băng — cùng đường đi với `scripts.generate_captions`."""
    postproc = json.loads((run_dir / "postproc.json").read_text(encoding="utf-8"))
    validate_postproc_artifact(postproc, taxonomy=taxonomy)
    class_ids = taxonomy.polyphonic_class_ids
    artifact = load_predictions(
        run_dir / "predictions" / f"{split}.npz", expected_class_ids=class_ids
    )
    if artifact.split != split:
        raise SystemExit(f"predictions split={artifact.split!r}, cần {split!r}")
    probabilities = stack_predictions_by_recording(artifact)
    frame_rate = 1.0 / artifact.frame_hop_s
    estimate = process_recordings(
        probabilities, class_ids=class_ids,
        thresholds={c: float(postproc["per_class"][c]["theta"]) for c in class_ids},
        priors=priors_from_postproc(postproc, class_ids), frame_rate=frame_rate,
    )
    return {
        rid: canonicalize_timeline(
            f"datased:{rid}", probabilities[rid].shape[0] / frame_rate,
            estimate.get(rid, []), taxonomy, model_version=run_dir.name,
        )
        for rid in sorted(probabilities)
    }


def oracle_timelines(
    recording_ids: list[str], durations: dict[str, float], taxonomy: Taxonomy
) -> dict[str, dict[str, Any]]:
    """Timeline từ ground truth polyphonic; score=1.0 vì không có score (prompt bỏ score).

    36/717 recording có offset GT vượt `duration_s` của manifest tối đa 5 ms (làm
    tròn của nhãn gốc) — lấy max để không sửa nhãn; prompt in duration 1 chữ số lẻ.
    """
    events = pd.read_csv(ROOT / "data/annotations/datased_polyphonic_events.csv")
    grouped: dict[str, list[dict[str, Any]]] = {rid: [] for rid in recording_ids}
    for row in events[events["recording_id"].isin(recording_ids)].itertuples(index=False):
        grouped[str(row.recording_id)].append(
            {"class_id": row.class_id, "onset_s": row.onset_s, "offset_s": row.offset_s,
             "score": 1.0}
        )
    return {
        rid: canonicalize_timeline(
            f"datased:{rid}", max(durations[rid], max((e["offset_s"] for e in grouped[rid]),
                                                      default=0.0)),
            grouped[rid], taxonomy, model_version="ground_truth",
        )
        for rid in recording_ids
    }


def server_model_path(endpoint: str) -> str:
    with urllib.request.urlopen(endpoint + "/props", timeout=10) as response:
        return str(json.load(response).get("model_path", ""))


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    config = LLMConfig.from_yaml(args.config)
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    lexicon_sha = CaptionLexicon.from_taxonomy(taxonomy).sha256()
    check_test_gate(args.split, lexicon_sha, args.frozen_lexicon_sha256)

    manifest = json.loads((args.run_dir / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("complete"):
        raise SystemExit(f"{args.run_dir} chưa hoàn tất")
    out_dir = args.run_dir / "captions"
    out_path = out_dir / f"unconstrained_{args.split}.jsonl"
    if out_path.exists() and args.limit is None:
        raise SystemExit(f"{out_path} đã tồn tại — output bất biến, không ghi đè")

    served = server_model_path(config.endpoint)
    if Path(served).name != config.model_file:
        raise SystemExit(f"server đang chạy {served!r}, config cần {config.model_file!r}")
    model_sha = sha256_file(ROOT / config.model_local_path)
    if model_sha != config.model_sha256:
        raise SystemExit(f"SHA-256 model lệch: {model_sha} != {config.model_sha256}")

    by_level = {"e2e": e2e_timelines(args.run_dir, args.split, taxonomy)}
    recording_ids = sorted(by_level["e2e"])[: args.limit]
    recordings = pd.read_csv(ROOT / "data/manifests/datased_recordings.csv")
    durations = dict(zip(recordings["recording_id"], recordings["duration_s"], strict=True))
    by_level["oracle"] = oracle_timelines(recording_ids, durations, taxonomy)

    captioner = UnconstrainedLLMCaptioner(
        HttpChatTransport(config.endpoint, config.timeout_s), config
    )
    rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    for rid in recording_ids:
        for level in LEVELS:
            timeline = by_level[level][rid]
            rows.append({"recording_id": rid, "level": level, "timeline": timeline,
                         "caption": captioner.caption(timeline)})
    wall_s = time.perf_counter() - started

    if args.limit is not None:
        out_path = out_dir / f"unconstrained_{args.split}.smoke.jsonl"
    out_dir.mkdir(exist_ok=True)
    out_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    truncated = sum(r["caption"]["generation"]["finish_reason"] == "length" for r in rows)
    meta = {
        "sed_run": args.run_dir.name, "split": args.split, "levels": list(LEVELS),
        "n_recordings": len(recording_ids), "n_captions": len(rows),
        "n_truncated": truncated, "wall_clock_s": round(wall_s, 1),
        "prompt_version": PROMPT_VERSION, "prompt_sha256": prompt_sha256(),
        "lexicon_sha256_at_generation": lexicon_sha,
        "model": {"name": config.model_name, "file": config.model_file, "sha256": model_sha},
        "runtime": {"llama_cpp_build": config.runtime_build},
        "generation": {"temperature": config.temperature, "seed": config.seed,
                       "max_tokens": config.max_tokens,
                       "enable_thinking": config.enable_thinking},
        "output_sha256": sha256_file(out_path), "git": git_state(ROOT),
    }
    out_path.with_suffix(".meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({"output": str(out_path), "n_captions": len(rows),
                      "n_truncated": truncated, "wall_clock_s": meta["wall_clock_s"]}, indent=2))


if __name__ == "__main__":
    main()
