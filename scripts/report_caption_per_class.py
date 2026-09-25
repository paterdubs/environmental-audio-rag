"""W5 — lỗi grounding theo từng lớp (evaluation_protocol Q2) cho mỗi nhánh × mức.

    .venv/Scripts/python.exe -m scripts.report_caption_per_class ml/runs/<sed_run> \\
        --split test --frozen-lexicon-sha256 <sha>

Số trung bình của `score_captions` có thể che lớp yếu. Script này đếm theo lớp:

- **bỏ sót**: caption có lớp c trong timeline nhưng không mention nào (được hỗ trợ) phủ c;
- **nhắc không có bằng chứng**: mention đơn lớp c trong khi c không có trong timeline;
- **gọi tên quá mức**: mention kind `specific` của c.

Cùng lexicon, cùng cách gộp liệt kê (`collapse_enumerations`) với `score_captions`; template
chấm trên đúng các timeline đó. Chỉ đếm, không chọn hay sửa gì.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from ml.captioning.lexicon import CaptionLexicon
from ml.captioning.template import TemplateCaptioner
from ml.evaluation.grounding import collapse_enumerations
from ml.taxonomy import load_taxonomy
from scripts.generate_llm_captions import check_test_gate
from scripts.score_captions import LLM_BRANCHES

ROOT = Path(__file__).resolve().parents[1]
OUTCOMES = ("present", "omitted", "unsupported", "specific", "out_of_taxonomy")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    parser.add_argument("--frozen-lexicon-sha256", default=None)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def class_errors(timeline: dict[str, Any], text: str, lexicon: CaptionLexicon) -> dict:
    """Per-class outcome of one caption: present/omitted, unsupported, over-specific."""
    present = {e["class_id"] for e in timeline["events"]}
    mentions = collapse_enumerations(text, lexicon.mentions(text))
    covered = set().union(*(m.class_ids & present for m in mentions if m.class_ids & present))
    unsupported = [m.class_id for m in mentions
                   if m.class_id is not None and not m.class_ids & present]
    return {"present": present, "omitted": present - covered,
            "unsupported": Counter(unsupported),
            "specific": Counter(m.class_id for m in mentions
                                if m.kind == "specific" and m.class_id is not None),
            "out_of_taxonomy": Counter(m.phrase for m in mentions if not m.class_ids)}


def tally(rows: list[tuple[str, dict, str]], lexicon: CaptionLexicon) -> dict[str, dict]:
    """rows = (branch/level, timeline, caption text) → per key, per class counts."""
    table: dict[str, dict] = {}
    for key, timeline, text in rows:
        outcome = class_errors(timeline, text, lexicon)
        entry = table.setdefault(key, {name: Counter() for name in OUTCOMES})
        for name in OUTCOMES:
            entry[name].update(outcome[name])
    return {key: {name: dict(counter) for name, counter in entry.items()}
            for key, entry in table.items()}


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
    keys = sorted(result["classes"])
    lines = [
        f"# Lỗi grounding theo lớp — `{result['run']}` ({result['split']})", "",
        f"> Sinh bởi `scripts.report_caption_per_class`. Lexicon "
        f"`{result['lexicon_sha256'][:8]}…`. Ô omission: số caption bỏ sót lớp / số caption "
        "có lớp đó trong timeline.", "",
    ]
    for level in ("e2e", "oracle"):
        level_keys = [k for k in keys if k.endswith(f"/{level}")]
        if not level_keys:
            continue
        lines += [f"## Omission theo lớp — {level}", "",
                  "| Lớp | " + " | ".join(k.split("/")[0] for k in level_keys) + " |",
                  "|---|" + "---:|" * len(level_keys)]
        classes = sorted({c for k in level_keys for c in result["classes"][k]["present"]})
        for class_id in classes:
            cells = []
            for key in level_keys:
                entry = result["classes"][key]
                n = entry["present"].get(class_id, 0)
                cells.append(f"{entry['omitted'].get(class_id, 0)}/{n}" if n else "—")
            lines.append(f"| `{class_id}` | " + " | ".join(cells) + " |")
        lines += ["", f"## Nhắc không có bằng chứng, gọi tên quá mức, ngoài taxonomy — {level}",
                  ""]
        for key in level_keys:
            entry = result["classes"][key]
            unsupported = ", ".join(f"{c} ({n})" for c, n in sorted(entry["unsupported"].items()))
            specific = ", ".join(f"{c} ({n})" for c, n in sorted(entry["specific"].items()))
            outside = ", ".join(f"{p} ({n})" for p, n in sorted(entry["out_of_taxonomy"].items()))
            lines.append(f"- **{key}** — không bằng chứng: {unsupported or '0'}; "
                         f"quá mức: {specific or '0'}; ngoài taxonomy: {outside or '0'}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    lexicon = CaptionLexicon.from_taxonomy(load_taxonomy(ROOT / "ml/configs/taxonomy.yaml"))
    check_test_gate(args.split, lexicon.sha256(), args.frozen_lexicon_sha256)
    result = {"run": args.run_dir.name, "split": args.split, "lexicon_sha256": lexicon.sha256(),
              "classes": tally(load_rows(args.run_dir, args.split, lexicon), lexicon)}
    destination = args.output or (
        ROOT / "docs/measurements" / f"caption_per_class_{args.run_dir.name}_{args.split}.md")
    destination.with_suffix(".json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    destination.write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
