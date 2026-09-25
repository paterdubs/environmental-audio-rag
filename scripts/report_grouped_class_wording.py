"""W5 — kiểm diễn đạt hai lớp gộp theo taxonomy.md §7 trên caption đã sinh.

    .venv/Scripts/python.exe -m scripts.report_grouped_class_wording ml/runs/<sed_run> \\
        --split test --frozen-lexicon-sha256 <sha>

Pipeline chỉ có SED coarse (không có subclass prediction), nên áp dòng "Chỉ có coarse
SED" của §7: caption phải nói ở mức lớp gộp ("a siren- or alarm-like sound", "an
impulsive sound resembling thunder, fireworks, or a gunshot"), không được gọi một
subclass như sự thật ("a gunshot is heard"). Với mỗi caption có lớp gộp G trong
timeline, xếp cách caption nhắc G vào một loại, theo thứ tự ưu tiên:

- `disjunction` — ≥2 subclass khác nhau nối bằng "or" ("thunder or fireworks",
  "thunder, fireworks, or a gunshot"): nêu được sự không chắc chắn, tính là hợp lệ
  theo hướng có lợi cho caption (ADR-0022 §3). Luật này định trên ví dụ **dev**;
- `specific` — gọi subclass như sự thật ("a gunshot", "sirens", "thunder, fireworks,
  and gunshots") — vi phạm §7;
- `class` — có mention mức lớp của G;
- `family` — chỉ có từ họ mơ hồ phủ G ("boom", "ringing");
- `absent` — không nhắc G (omission, đã đo ở C2).

Chỉ đọc caption bất biến + chấm template trên cùng timeline; không sửa gì.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from ml.captioning.lexicon import CaptionLexicon, Mention
from ml.captioning.template import TemplateCaptioner
from ml.taxonomy import load_taxonomy
from scripts.generate_llm_captions import check_test_gate
from scripts.score_captions import LLM_BRANCHES

ROOT = Path(__file__).resolve().parents[1]
GROUPED = ("sirens_and_alarms", "thunder_fireworks_gunshot")
CATEGORIES = ("class", "disjunction", "specific", "family", "absent")
# Glue allowed between alternatives: "thunder, fireworks, or a gunshot", "sirens or alarms".
DISJUNCTION_GAP = re.compile(r"\s*,?\s*(?:or\s+)?(?:a |an |the )?\s*")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    parser.add_argument("--frozen-lexicon-sha256", default=None)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def _is_disjunction(text: str, specific: list[Mention]) -> bool:
    """≥2 distinct subclass terms chained only by list glue with at least one "or"."""
    if len({m.phrase.rstrip("s") for m in specific}) < 2:
        return False
    gaps = [text[a.end:b.start] for a, b in zip(specific, specific[1:], strict=False)]
    return (all(DISJUNCTION_GAP.fullmatch(gap) for gap in gaps)
            and any(re.search(r"\bor\b", gap) for gap in gaps))


def classify(text: str, class_id: str, lexicon: CaptionLexicon) -> tuple[str, list[str]]:
    """Category of how `text` refers to `class_id`, plus the specific phrases used."""
    mentions = [m for m in lexicon.mentions(text) if class_id in m.class_ids]
    specific = [m for m in mentions if m.kind == "specific"]
    if specific:
        category = "disjunction" if _is_disjunction(text, specific) else "specific"
        return category, [m.phrase for m in specific]
    for kind in ("class", "family"):
        if any(m.kind == kind for m in mentions):
            return kind, []
    return "absent", []


def tally(rows: list[tuple[str, dict, str]], lexicon: CaptionLexicon) -> dict[str, Any]:
    """rows = (branch/level key, timeline, caption text)."""
    counts: dict[str, dict[str, Counter]] = {}
    phrases: dict[str, Counter] = {}
    for key, timeline, text in rows:
        present = {e["class_id"] for e in timeline["events"]} & set(GROUPED)
        for class_id in sorted(present):
            category, used = classify(text, class_id, lexicon)
            counts.setdefault(key, {}).setdefault(class_id, Counter())[category] += 1
            phrases.setdefault(key, Counter()).update(used if category == "specific" else [])
    return {"counts": {k: {c: dict(v) for c, v in d.items()} for k, d in counts.items()},
            "specific_phrases": {k: dict(v.most_common()) for k, v in phrases.items()}}


def load_rows(run_dir: Path, split: str, lexicon: CaptionLexicon) -> list[tuple[str, dict, str]]:
    rows: list[tuple[str, dict, str]] = []
    timelines: dict[tuple[str, str], dict] = {}
    for branch in LLM_BRANCHES:
        source = run_dir / "captions" / f"{branch}_{split}.jsonl"
        if not source.exists():
            continue
        for line in source.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            timelines[(row["recording_id"], row["level"])] = row["timeline"]
            rows.append((f"{branch}/{row['level']}", row["timeline"], row["caption"]["text"]))
    if not timelines:
        raise SystemExit(f"không có caption nào cho split {split}")
    template = TemplateCaptioner(lexicon)
    for (_, level), timeline in sorted(timelines.items()):
        rows.append((f"template/{level}", timeline, template.caption(timeline)["text"]))
    return rows


def render(result: dict[str, Any]) -> str:
    lines = [
        f"# Diễn đạt lớp gộp (taxonomy.md §7) — `{result['run']}` ({result['split']})", "",
        f"> Sinh bởi `scripts.report_grouped_class_wording`. Lexicon sha256 "
        f"`{result['lexicon_sha256'][:16]}…`. Đơn vị: một caption có lớp gộp trong "
        "timeline. `specific` = gọi subclass như sự thật (vi phạm §7).", "",
        "Giao thức: bản đầu của script (chưa có loại \"liệt kê or\") đã chạy trên cả dev "
        "và test; luật `disjunction` sau đó định bằng ví dụ **dev**, chỉ nới theo hướng có "
        "lợi cho caption — số `specific` ở đây là cận dưới của vi phạm.", "",
        "| Nhánh / mức | Lớp | n | mức lớp | liệt kê \"or\" | **specific** | họ mơ hồ "
        "| không nhắc |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for key in sorted(result["counts"]):
        for class_id, c in sorted(result["counts"][key].items()):
            n = sum(c.values())
            cells = " | ".join(str(c.get(cat, 0)) for cat in CATEGORIES)
            lines.append(f"| {key} | `{class_id}` | {n} | {cells} |")
    lines += ["", "## Cụm `specific` đã dùng", ""]
    for key, used in sorted(result["specific_phrases"].items()):
        if used:
            lines.append(f"- {key}: " + ", ".join(f"{p} ({n})" for p, n in used.items()))
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    lexicon = CaptionLexicon.from_taxonomy(load_taxonomy(ROOT / "ml/configs/taxonomy.yaml"))
    check_test_gate(args.split, lexicon.sha256(), args.frozen_lexicon_sha256)
    result = {"run": args.run_dir.name, "split": args.split,
              "lexicon_sha256": lexicon.sha256(),
              **tally(load_rows(args.run_dir, args.split, lexicon), lexicon)}
    destination = args.output or (
        ROOT / "docs/measurements" / f"grouped_class_wording_{args.run_dir.name}_{args.split}.md"
    )
    destination.with_suffix(".json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    destination.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
