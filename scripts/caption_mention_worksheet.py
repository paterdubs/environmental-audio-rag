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
from ml.evaluation.caption_stats import paired_difference
from ml.evaluation.grounding import evaluate_grounding
from ml.evaluation.mention_agreement import (
    agreement,
    extractor_outside,
    extractor_units,
    human_grounding,
    label_restatement,
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
MIN_ANNOTATED = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "score"))
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--split", default="test")
    parser.add_argument("--n", type=int, default=60)
    parser.add_argument("--worksheet", type=Path, default=WORKSHEET)
    parser.add_argument("--output", type=Path, default=None, help="measurement (mặc định docs/)")
    parser.add_argument("--guide", type=Path, default=None, help="hướng dẫn (mặc định docs/)")
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


GUIDE = """# Phiếu đối chiếu bộ trích mention (C2) — hướng dẫn điền

> Sinh bởi `scripts.caption_mention_worksheet build`. Phiếu:
> `data/manifests/caption_mention_worksheet.csv` ({n} caption unconstrained, tập test;
> {half} mức oracle + {half} mức e2e, chọn bằng thứ tự băm có seed).

**Mục đích.** Metric C2 (hallucination, omission, gọi tên quá mức) dựa vào lexicon tự động
đọc caption. Phiếu này đo lexicon đọc đúng đến đâu. Bạn đọc caption và ghi nguồn âm caption
**khẳng định nghe thấy**. Đọc **mù**: không xem timeline, không xem kết quả lexicon, và
**không nghe audio** — phiếu đo cách đọc câu chữ; audio chứa gì đã có nhãn DataSED trả lời.

Mở được bằng Excel; khi lưu chọn **CSV UTF-8** (lưu kiểu khác sẽ mất dấu).

Các cột cần điền:

- `classes_mentioned` — `class_id` của mọi nguồn âm caption nói là nghe thấy, cách nhau
  bằng `;`. Từ mơ hồ phủ nhiều lớp ghi `lớp_a|lớp_b` (vd `jet_aircrafts|propeller_aircrafts`
  cho "aircraft"). Không có nguồn nào: ghi `none` — không để trống.
  Ví dụ: `birds; jet_aircrafts|propeller_aircrafts`.
- `other_sources` — nguồn âm **ngoài** 22 lớp (gió, mưa, bước chân, đám đông…), cách nhau
  bằng dấu phẩy; trống nếu không có. Ví dụ: `wind, footsteps`.
- `over_specific` — `class_id` của lớp mà caption gọi tên một loại con như sự thật
  ("a gunshot" → `thunder_fireworks_gunshot`, "sirens" → `sirens_and_alarms`,
  "a vacuum cleaner" → `vacuum_cleaner_fan_hairdryer`); cách nhau bằng `;`; trống nếu không có.
  Liệt kê loại con bằng "or" vẫn tính ("a fan or hairdryer" → `vacuum_cleaner_fan_hairdryer`)
  — đúng định nghĩa metric C2, vốn đếm mọi tên loại con.
- `notes` — tuỳ chọn.

**Quy tắc.** (1) Từ bối cảnh ("urban", "park", "street") không phải nguồn âm — không ghi.
(2) Một lớp nhắc nhiều lần chỉ ghi một lần. (3) Cách gọi khác vẫn tính ("chirping" →
`birds`, "people talking" → `voices`, "engine idling" → `vehicle_idling`). (4) Không sửa cột
`caption` — script kiểm nguyên văn. (5) Xong thì chạy
`scripts.caption_mention_worksheet score ml/runs/<run>`.

## 22 lớp

| `class_id` | Nhãn gốc |
|---|---|
{classes}
"""


def guide(taxonomy, n: int) -> str:
    rows = "\n".join(f"| `{c.class_id}` | {c.source_label} |" for c in taxonomy.classes)
    return GUIDE.format(n=n, half=n // 2, classes=rows)


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
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    instructions = getattr(args, "guide", None) or (
        ROOT / "docs/measurements" / f"caption_mention_worksheet_{stamp}.md")
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    instructions.write_text(guide(taxonomy, len(rows)), encoding="utf-8")
    print(json.dumps({"worksheet": str(args.worksheet), "guide": str(instructions),
                      "n": len(rows)}, ensure_ascii=False))


def read_worksheet(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def annotated_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    """Rows with every fill-in cell empty are not annotated yet (skipped and counted);
    a row with other cells filled but no `classes_mentioned` is an error."""
    done, pending = [], 0
    for row in rows:
        if not any(row[column].strip() for column in FILLED):
            pending += 1
        elif not row["classes_mentioned"].strip():
            raise SystemExit(f"{row['item_id']}: thiếu classes_mentioned (ghi 'none' nếu "
                             "caption không nhắc nguồn âm nào)")
        else:
            done.append(row)
    if len(done) < MIN_ANNOTATED:
        raise SystemExit(f"mới có {len(done)} dòng đã điền — cần ít nhất {MIN_ANNOTATED}")
    return done, pending


def compare_row(row: dict[str, str], source: dict, lexicon: CaptionLexicon, class_ids) -> dict:
    text = source["caption"]["text"]
    if row["caption"] != text:
        raise SystemExit(f"{row['item_id']}: caption trong phiếu khác caption gốc")
    human = parse_units(row["classes_mentioned"], class_ids)
    extracted = extractor_units(text, lexicon)
    human_specific = (parse_units(row["over_specific"], class_ids)
                      if row["over_specific"].strip() else set())
    lexicon_specific = {frozenset(m.class_ids) for m in lexicon.mentions(text)
                        if m.kind == "specific"}
    present = {e["class_id"] for e in source["timeline"]["events"]}
    outside = [s for s in row["other_sources"].split(",") if s.strip()]
    flag = (unsupported(extracted, present, extractor_outside(text, lexicon)),
            unsupported(human, present, bool(outside)))
    missed_specific = {c for unit in human_specific - lexicon_specific for c in unit}
    disagreement = None if extracted == human else {
        "item_id": row["item_id"], "caption": text,
        "lexicon": sorted("|".join(sorted(u)) for u in extracted),
        "human": sorted("|".join(sorted(u)) for u in human)}
    return {"pair": (extracted, human), "specific": (lexicon_specific, human_specific),
            "flag": flag, "disagreement": disagreement,
            "metrics": (evaluate_grounding(source["timeline"], source["caption"], lexicon),
                        human_grounding(human, len(outside), present)),
            "label_restated": sum(label_restatement(c, text, lexicon) for c in missed_specific),
            "missed_specific": len(missed_specific)}


def score(args: argparse.Namespace) -> None:
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    lexicon = CaptionLexicon.from_taxonomy(taxonomy)
    captions = load_captions(args.run_dir, args.split)
    rows, pending = annotated_rows(read_worksheet(args.worksheet))
    results = [compare_row(row, captions[(row["recording_id"], row["level"])], lexicon,
                           taxonomy.class_ids) for row in rows]
    extra = {"metric_bias": metric_bias(rows, results),
             "over_specific_missed": {
                 "total": sum(r["missed_specific"] for r in results),
                 "label_restatement": sum(r["label_restated"] for r in results)}}
    write_agreement(args, lexicon, agreement([r["pair"] for r in results]),
                    agreement([r["specific"] for r in results]),
                    [r["flag"] for r in results],
                    [r["disagreement"] for r in results if r["disagreement"]], pending, extra)


def metric_bias(rows: list[dict[str, str]], results: list[dict]) -> dict:
    """C2 read by the lexicon vs by the human on the same captions (paired CI)."""
    lexicon = {row["item_id"]: r["metrics"][0] for row, r in zip(rows, results, strict=True)}
    human = {row["item_id"]: r["metrics"][1] for row, r in zip(rows, results, strict=True)}
    out = {}
    for metric in ("hallucination_rate", "omission_rate"):
        diff = paired_difference(lexicon, human, metric)
        out[metric] = {"lexicon": sum(getattr(m, metric) for m in lexicon.values()) / len(lexicon),
                       "human": sum(getattr(m, metric) for m in human.values()) / len(human),
                       "lexicon_minus_human": [diff.estimate, diff.lower, diff.upper]}
    return out


def write_agreement(args, lexicon, mentions, specific, flags, disagreements, pending,
                    extra) -> None:
    confusion = {f"lexicon_{a}_human_{b}": sum(f == (a, b) for f in flags)
                 for a in (True, False) for b in (True, False)}
    result = {"run": args.run_dir.name, "split": args.split, "lexicon_sha256": lexicon.sha256(),
              "n_captions": mentions.n_captions, "n_not_annotated": pending,
              "mentions": {"precision": mentions.precision, "recall": mentions.recall,
                           "tp": mentions.true_positive, "fp": mentions.false_positive,
                           "fn": mentions.false_negative, "exact": mentions.exact_captions},
              "over_specific": {"precision": specific.precision, "recall": specific.recall},
              "hallucination_flag": confusion, **extra, "disagreements": disagreements}
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    destination = getattr(args, "output", None) or (
        ROOT / "docs/measurements" / f"caption_mention_agreement_{stamp}.md")
    destination.with_suffix(".json").write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                                encoding="utf-8")
    destination.write_text(render(result), encoding="utf-8")
    print(render(result))


def render_bias(result: dict[str, Any]) -> list[str]:
    missed = result["over_specific_missed"]
    lines = [f"Gọi tên quá mức người đánh dấu mà lexicon không: {missed['total']}, trong đó "
             f"{missed['label_restatement']} là nhắc lại đúng tên lớp (vd \"cicadas and "
             "crickets\") — lexicon coi là mức lớp theo thiết kế.", "",
             "## C2 trên cùng mẫu: lexicon đọc vs người đọc", "",
             "| Metric | Lexicon | Người | Lexicon − người [CI 95%] |", "|---|---:|---:|---:|"]
    for metric, v in result["metric_bias"].items():
        d = v["lexicon_minus_human"]
        lines.append(f"| {metric} | {v['lexicon']:.4f} | {v['human']:.4f} "
                     f"| {d[0]:+.4f} [{d[1]:+.4f}, {d[2]:+.4f}] |")
    return lines + [""]


def render(result: dict[str, Any]) -> str:
    m, c = result["mentions"], result["hallucination_flag"]
    lines = [
        f"# Bộ trích mention vs người đọc — `{result['run']}` ({result['split']})", "",
        f"> Sinh bởi `scripts.caption_mention_worksheet score`. Lexicon "
        f"`{result['lexicon_sha256'][:8]}…`; {result['n_captions']} caption unconstrained đã "
        f"điền ({result['n_not_annotated']} dòng chưa điền, bỏ qua); người đọc mù (không "
        "timeline, không output lexicon, không nghe audio).", "",
        "| Mức | Precision | Recall | TP | FP | FN | Caption khớp hoàn toàn |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| Mention (lớp) | {m['precision']:.3f} | {m['recall']:.3f} | {m['tp']} | {m['fp']} "
        f"| {m['fn']} | {m['exact']}/{result['n_captions']} |",
        f"| Gọi tên quá mức | {result['over_specific']['precision']:.3f} "
        f"| {result['over_specific']['recall']:.3f} | | | | |", "",
        *render_bias(result),
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
