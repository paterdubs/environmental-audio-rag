"""W5 — kiểm chứng bộ trích mention (C2) bằng người: tạo phiếu và chấm phiếu.

    .venv/Scripts/python.exe -m scripts.caption_mention_worksheet build ml/runs/<sed_run>
    # người điền data/manifests/caption_mention_worksheet.csv (xem measurement hướng dẫn)
    .venv/Scripts/python.exe -m scripts.caption_mention_worksheet score ml/runs/<sed_run>

Metric C2 chỉ đúng khi lexicon đọc caption đúng. Audit trước đó chỉ xét phía báo nhầm
(8 mention "bịa" trên test, 7 là lỗi lexicon); phía bỏ sót chưa đo. Người đọc caption
unconstrained **mù** (không timeline, không output lexicon), ghi nguồn âm caption khẳng
định; `score` so với lexicon: precision/recall của bộ trích, và bảng 2×2 cờ "caption có
bịa" của người vs lexicon. Mẫu lấy từ test vì lexicon đã đóng băng trước test — đây là
ước lượng không thiên của chính lexicon đã dùng để báo RQ2; không sửa lexicon theo kết quả.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ml.captioning.lexicon import CaptionLexicon
from ml.evaluation.mention_agreement import (
    agreement,
    extractor_outside,
    extractor_units,
    parse_units,
    unsupported,
)
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
WORKSHEET = ROOT / "data/manifests/caption_mention_worksheet.csv"
COLUMNS = ("item_id", "level", "recording_id", "caption", "classes_mentioned",
           "other_sources", "over_specific", "notes")
FILLED = ("classes_mentioned", "other_sources", "over_specific", "notes")
SEED = "20260922"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "score"))
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--split", default="test")
    parser.add_argument("--n", type=int, default=60)
    parser.add_argument("--worksheet", type=Path, default=WORKSHEET)
    return parser.parse_args()


def load_captions(run_dir: Path, split: str) -> dict[tuple[str, str], dict[str, Any]]:
    path = run_dir / "captions" / f"unconstrained_{split}.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    return {(r["recording_id"], r["level"]): r for r in rows}


def sample(captions: dict[tuple[str, str], dict], n: int) -> list[tuple[str, str]]:
    """n/2 per level, ordered by a seeded hash — deterministic, independent of content."""
    chosen = []
    for level in ("oracle", "e2e"):
        keys = sorted((k for k in captions if k[1] == level),
                      key=lambda k: hashlib.sha256(f"{SEED}:{k[0]}:{k[1]}".encode()).hexdigest())
        chosen += keys[: n // 2]
    return chosen


def build(args: argparse.Namespace) -> None:
    if args.worksheet.exists():
        raise SystemExit(f"{args.worksheet} đã tồn tại — không ghi đè phiếu có thể đã điền")
    captions = load_captions(args.run_dir, args.split)
    rows = [{"item_id": f"m-{i + 1:03d}", "level": level, "recording_id": rid,
             "caption": captions[(rid, level)]["caption"]["text"],
             **dict.fromkeys(FILLED, "")}
            for i, (rid, level) in enumerate(sample(captions, args.n))]
    args.worksheet.parent.mkdir(parents=True, exist_ok=True)
    with args.worksheet.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"worksheet": str(args.worksheet), "n": len(rows)}, ensure_ascii=False))


def read_worksheet(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def score(args: argparse.Namespace) -> None:
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    lexicon = CaptionLexicon.from_taxonomy(taxonomy)
    captions = load_captions(args.run_dir, args.split)
    pairs, specific_pairs, flags, disagreements = [], [], [], []
    for row in read_worksheet(args.worksheet):
        source = captions[(row["recording_id"], row["level"])]
        text = source["caption"]["text"]
        if row["caption"] != text:
            raise SystemExit(f"{row['item_id']}: caption trong phiếu khác caption gốc")
        human = parse_units(row["classes_mentioned"], taxonomy.class_ids)
        extracted = extractor_units(text, lexicon)
        pairs.append((extracted, human))
        human_specific = (parse_units(row["over_specific"], taxonomy.class_ids)
                          if row["over_specific"].strip() else set())
        specific_pairs.append(({frozenset(m.class_ids) for m in lexicon.mentions(text)
                                if m.kind == "specific"}, human_specific))
        present = {e["class_id"] for e in source["timeline"]["events"]}
        flags.append((unsupported(extracted, present, extractor_outside(text, lexicon)),
                      unsupported(human, present, bool(row["other_sources"].strip()))))
        if extracted != human:
            disagreements.append({"item_id": row["item_id"], "caption": text,
                                  "lexicon": sorted("|".join(sorted(u)) for u in extracted),
                                  "human": sorted("|".join(sorted(u)) for u in human)})
    write_agreement(args, lexicon, agreement(pairs), agreement(specific_pairs), flags,
                    disagreements)


def write_agreement(args, lexicon, mentions, specific, flags, disagreements) -> None:
    confusion = {f"lexicon_{a}_human_{b}": sum(f == (a, b) for f in flags)
                 for a in (True, False) for b in (True, False)}
    result = {"run": args.run_dir.name, "split": args.split, "lexicon_sha256": lexicon.sha256(),
              "n_captions": mentions.n_captions,
              "mentions": {"precision": mentions.precision, "recall": mentions.recall,
                           "tp": mentions.true_positive, "fp": mentions.false_positive,
                           "fn": mentions.false_negative, "exact": mentions.exact_captions},
              "over_specific": {"precision": specific.precision, "recall": specific.recall},
              "hallucination_flag": confusion, "disagreements": disagreements}
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    destination = ROOT / "docs/measurements" / f"caption_mention_agreement_{stamp}.md"
    destination.with_suffix(".json").write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                                encoding="utf-8")
    destination.write_text(render(result), encoding="utf-8")
    print(render(result))


def render(result: dict[str, Any]) -> str:
    m, c = result["mentions"], result["hallucination_flag"]
    lines = [
        f"# Bộ trích mention vs người đọc — `{result['run']}` ({result['split']})", "",
        f"> Sinh bởi `scripts.caption_mention_worksheet score`. Lexicon "
        f"`{result['lexicon_sha256'][:8]}…`; {result['n_captions']} caption unconstrained, "
        "người đọc mù (không timeline, không output lexicon).", "",
        "| Mức | Precision | Recall | TP | FP | FN | Caption khớp hoàn toàn |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| Mention (lớp) | {m['precision']:.3f} | {m['recall']:.3f} | {m['tp']} | {m['fp']} "
        f"| {m['fn']} | {m['exact']}/{result['n_captions']} |",
        f"| Gọi tên quá mức | {result['over_specific']['precision']:.3f} "
        f"| {result['over_specific']['recall']:.3f} | | | | |", "",
        "## Cờ \"caption có bịa\" (so với timeline)", "",
        "| | Người: có | Người: không |", "|---|---:|---:|",
        f"| Lexicon: có | {c['lexicon_True_human_True']} | {c['lexicon_True_human_False']} |",
        f"| Lexicon: không | {c['lexicon_False_human_True']} | {c['lexicon_False_human_False']} |",
        "", "## Caption lệch", "",
    ]
    for d in result["disagreements"]:
        lines.append(f"- `{d['item_id']}` lexicon {d['lexicon']} · người {d['human']} "
                     f"— {d['caption']}")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    build(args) if args.action == "build" else score(args)


if __name__ == "__main__":
    main()
