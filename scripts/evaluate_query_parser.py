"""Đánh giá parser câu hỏi EN/VI thành Filters trên hai tập đã khóa (ADR-0036)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ml.captioning.lexicon import VI_LEXICON_CONFIG, CaptionLexicon
from ml.provenance import git_state
from ml.retrieval.filters import Filters
from ml.retrieval.query_parser import PROMPT_VERSION, QueryParser, QueryParserInvalid
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
QUERYSET = ROOT / "data/manifests/retrieval_queryset_v2.json"
PARAPHRASE = ROOT / "data/manifests/query_parse_paraphrase_v1.csv"
CONFIG = ROOT / "ml/configs/caption_llm.yaml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=("all", "template", "paraphrase"), default="all")
    return parser.parse_args()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def samples(dataset: str) -> list[dict[str, Any]]:
    rows = []
    if dataset in ("all", "template"):
        for query in json.loads(QUERYSET.read_text(encoding="utf-8")):
            for language, field in (("en", "question"), ("vi", "question_vi")):
                rows.append({"dataset": "template", "query_id": query["query_id"],
                             "group": query["group"], "language": language,
                             "question": query[field], "gold": query["filters"]})
    if dataset in ("all", "paraphrase"):
        with PARAPHRASE.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                rows.append({"dataset": "paraphrase", "query_id": row["query_id"],
                             "group": row["group"], "language": row["language"],
                             "question": row["question"], "gold": json.loads(row["filters_json"])})
    return rows


def normalise(filters: Mapping[str, Any]) -> dict[str, Any]:
    result = Filters.model_validate(filters).as_dict()
    if "classes_all" in result:
        result["classes_all"] = sorted(result["classes_all"])
    return result


def _classes(filters: Mapping[str, Any]) -> set[str]:
    return Filters.model_validate(filters).class_ids()


def summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    exact = sum(row["exact"] for row in rows)
    succeeded = sum(row["error"] is None for row in rows)
    tp = fp = fn = 0
    temporal = [row for row in rows if "temporal" in row["gold"]]
    predicate_correct = 0
    for row in rows:
        gold = _classes(row["gold"])
        predicted = _classes(row["predicted"]) if row["predicted"] is not None else set()
        tp += len(gold & predicted)
        fp += len(predicted - gold)
        fn += len(gold - predicted)
        if "temporal" in row["gold"] and row["predicted"] is not None:
            predicate_correct += row["predicted"].get("temporal", {}).get("predicate") == (
                row["gold"]["temporal"]["predicate"])
    return {
        "n": len(rows), "parse_success": succeeded / len(rows), "n_parse_success": succeeded,
        "exact_match": exact / len(rows), "n_exact": exact,
        "class_precision": tp / (tp + fp) if tp + fp else 0.0,
        "class_recall": tp / (tp + fn) if tp + fn else 0.0,
        "predicate_accuracy": predicate_correct / len(temporal) if temporal else None,
        "n_temporal": len(temporal),
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Đánh giá parser câu hỏi thành bộ lọc", "",
        "> Chỉ đo chuyển câu hỏi thành filter; không đọc audio, dev/test annotation hay output "
        "SED. "
        "Tập `template` là cận trên vì câu hỏi sinh từ mẫu; tập `paraphrase` gồm 40 câu viết "
        "tay đã commit trước lần chạy parser đầu tiên.", "",
        f"Model `{result['model']}`, prompt `{result['prompt_version']}`, greedy temperature 0, "
        f"seed {result['seed']}; git `{result['git']['revision'][:8]}`, "
        f"dirty=`{str(result['git']['dirty']).lower()}`.", "",
        "| Tập | n | Parse thành công | Exact toàn filter | P lớp | R lớp | Đúng predicate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, summary in result["summary"].items():
        predicate = ("—" if summary["predicate_accuracy"] is None
                     else f"{summary['predicate_accuracy']:.3f} ({summary['n_temporal']})")
        lines.append(
            f"| {name} | {summary['n']} | {summary['parse_success']:.3f} "
            f"({summary['n_parse_success']}/{summary['n']}) | {summary['exact_match']:.3f} "
            f"({summary['n_exact']}/{summary['n']}) | {summary['class_precision']:.3f} | "
            f"{summary['class_recall']:.3f} | {predicate} |")
    lines += ["", "## Diễn giải bắt buộc", "",
              "Exact match yêu cầu đúng toàn bộ filter sau chuẩn hóa; `classes_all` không xét thứ "
              "tự, còn vai trò temporal `a`/`b` có xét thứ tự. Lỗi parse được tính là sai, không "
              "thay bằng filter gold. Số template không đại diện câu hỏi tự do.", ""]
    return "\n".join(lines)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    vi = CaptionLexicon.from_taxonomy(taxonomy, config=VI_LEXICON_CONFIG)
    labels = {item.class_id: {"en": item.source_label.lower(),
                              "vi": vi.canonical_phrase(item.class_id)}
              for item in taxonomy.classes if item.class_id in taxonomy.polyphonic_class_ids}
    parser = QueryParser.from_config(CONFIG, labels)
    evaluated = []
    selected = samples(args.dataset)
    for index, sample in enumerate(selected, 1):
        identity = f"{sample['dataset']} {sample['query_id']}/{sample['language']}"
        print(f"[{index}/{len(selected)}] {identity}")
        try:
            parsed = parser.parse(sample["question"], sample["language"])
            predicted, raw, error = parsed.filters.as_dict(), parsed.raw, None
        except QueryParserInvalid as exc:
            predicted, raw, error = None, None, str(exc)
        evaluated.append({**sample, "predicted": predicted, "raw": raw, "error": error,
                          "exact": predicted is not None
                          and normalise(predicted) == normalise(sample["gold"])})
    groups = {name: [row for row in evaluated if row["dataset"] == name]
              for name in sorted({row["dataset"] for row in evaluated})}
    result = {
        "model": parser.config.model_name, "endpoint": parser.config.endpoint,
        "prompt_version": PROMPT_VERSION, "temperature": parser.config.temperature,
        "seed": parser.config.seed, "git": git_state(ROOT),
        "inputs": {"queryset": {"path": str(QUERYSET.relative_to(ROOT)),
                                  "sha256": _sha256(QUERYSET)},
                   "paraphrase": {"path": str(PARAPHRASE.relative_to(ROOT)),
                                   "sha256": _sha256(PARAPHRASE)}},
        "summary": {name: summarise(rows) for name, rows in groups.items()},
        "predictions": evaluated,
    }
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    destination = ROOT / "docs/measurements" / f"query_parser_{stamp}.md"
    destination.with_suffix(".json").write_text(
        json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    destination.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
