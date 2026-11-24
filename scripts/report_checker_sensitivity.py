"""Độ nhạy của bộ chấm ảo giác RQ2: cố tình chèn nguồn âm sai vào mô tả rồi xem có bắt được không.

Bộ chấm (`ml.evaluation.grounding`) dựa trên từ điển; tỷ lệ ảo giác thấp chỉ có nghĩa nếu nó bắt
được ảo giác thật. Script lấy mô tả đầu–cuối dev đã sinh và tạo bốn kiểu nhiễu (ý tưởng thay một
danh từ của BRACE), mỗi kiểu một bản/mô tả, tất định theo seed:

- `swap_canonical`: thay nhắc đầu tiên bằng tên mẫu cố định của một lớp **không** có trong dòng
  thời gian.
- `swap_synonym`: như trên nhưng dùng một cụm đồng nghĩa (không phải tên mẫu cố định) của lớp vắng.
- `insert_class`: nối câu "{tên mẫu cố định lớp vắng} can also be heard."
- `insert_oov`: nối câu với một nguồn âm ngoài taxonomy trong danh sách cố định `OOV_SOURCES`.

Bắt được = số nhắc không có trong dòng thời gian tăng so với mô tả gốc. Chỉ dev; không gọi LLM.

    .venv/Scripts/python.exe -m scripts.report_checker_sensitivity
"""

from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ml.captioning.lexicon import CaptionLexicon
from ml.captioning.template import TemplateCaptioner
from ml.evaluation.coverage import unannotated_recordings
from ml.evaluation.grounding import collapse_enumerations
from ml.provenance import git_state
from ml.taxonomy import load_taxonomy
from scripts.report_caption_vs_gt import BRANCHES, RUNS, SYSTEMS, read_rows

ROOT = Path(__file__).resolve().parents[1]
_TEMPLATE = TemplateCaptioner(CaptionLexicon.from_taxonomy(
    load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")))
M = ROOT / "docs" / "measurements"
SEED = 20260922
KINDS = ("swap_canonical", "swap_synonym", "insert_class", "insert_oov")
OOV_SOURCES = ("a baby crying", "a door slamming", "a hammer striking", "rain falling",
               "a crowd cheering", "a cat meowing", "a clock ticking", "a phone vibrating")


def unsupported(text: str, timeline_classes: set[str], lexicon: CaptionLexicon) -> int:
    mentions = collapse_enumerations(text, lexicon.mentions(text))
    return sum(not (m.class_ids & timeline_classes) for m in mentions)


def name(class_id: str) -> str:
    """How the English template names a class (`TemplateCaptioner`)."""
    return TemplateCaptioner._phrase(_TEMPLATE, class_id)


def synonyms(lexicon: CaptionLexicon, classes: tuple[str, ...]) -> dict[str, list[str]]:
    """class_id → single-class phrases of kind `class` other than the template name."""
    out: dict[str, list[str]] = defaultdict(list)
    for entry in lexicon.entries:
        if entry.kind == "class" and len(entry.class_ids) == 1:
            (class_id,) = entry.class_ids
            if class_id in classes and entry.phrase != name(class_id).lower():
                out[class_id].append(entry.phrase)
    return {k: sorted(v) for k, v in out.items()}


def perturb(text: str, kind: str, absent: list[str], lexicon: CaptionLexicon,
            syn: dict[str, list[str]], rng: random.Random, oov: str) -> str | None:
    """One perturbed caption, or None when the kind does not apply."""
    if kind == "insert_oov":
        return f"{text} {oov[0].upper()}{oov[1:]} can also be heard."
    if not absent:
        return None
    target = rng.choice(absent)
    phrase = name(target)
    if kind == "insert_class":
        return f"{text} {phrase[0].upper()}{phrase[1:]} can also be heard."
    mentions = collapse_enumerations(text, lexicon.mentions(text))
    if not mentions:
        return None
    if kind == "swap_synonym":
        options = [c for c in absent if syn.get(c)]
        if not options:
            return None
        phrase = rng.choice(syn[rng.choice(options)])
    first = mentions[0]
    return text[:first.start] + phrase + text[first.end:]


def score(captions: list[tuple[str, set[str]]], lexicon: CaptionLexicon,
          classes: tuple[str, ...]) -> dict[str, Any]:
    """Detection rate per perturbation kind, and per OOV source."""
    rng = random.Random(SEED)
    syn = synonyms(lexicon, classes)
    hits = {k: [0, 0] for k in KINDS}
    oov_hits = {s: [0, 0] for s in OOV_SOURCES}
    for index, (text, present) in enumerate(captions):
        base = unsupported(text, present, lexicon)
        absent = [c for c in classes if c not in present]
        oov = OOV_SOURCES[index % len(OOV_SOURCES)]
        for kind in KINDS:
            new = perturb(text, kind, absent, lexicon, syn, rng, oov)
            if new is None:
                continue
            caught = unsupported(new, present, lexicon) > base
            hits[kind][0] += caught
            hits[kind][1] += 1
            if kind == "insert_oov":
                oov_hits[oov][0] += caught
                oov_hits[oov][1] += 1
    rate = lambda h: {"caught": h[0], "n": h[1], "rate": h[0] / h[1] if h[1] else None}  # noqa: E731
    return {"by_kind": {k: rate(v) for k, v in hits.items()},
            "by_oov_source": {k: rate(v) for k, v in oov_hits.items()}}


def collect(lexicon: CaptionLexicon) -> dict[str, list[tuple[str, set[str]]]]:
    template = TemplateCaptioner(lexicon)
    excluded = unannotated_recordings()
    out: dict[str, list[tuple[str, set[str]]]] = defaultdict(list)
    for run in SYSTEMS.values():
        for branch in BRANCHES[1:]:
            rows = read_rows(RUNS / run / "captions" / f"{branch}_dev.jsonl", excluded)["e2e"]
            for _, row in sorted(rows.items()):
                present = {e["class_id"] for e in row["timeline"]["events"]}
                out[branch].append((row["caption"]["text"], present))
                if branch == "constrained":
                    text = template.caption(row["timeline"])["text"]
                    out["template"].append((text, present))
    return out


def build() -> dict[str, Any]:
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    lexicon = CaptionLexicon.from_taxonomy(taxonomy)
    classes = tuple(taxonomy.polyphonic_class_ids)
    captions = collect(lexicon)
    results = {branch: score(items, lexicon, classes) for branch, items in captions.items()}
    pooled = score([c for items in captions.values() for c in items], lexicon, classes)
    return {"split": "dev", "eval_set": "annotated", "systems": list(SYSTEMS), "seed": SEED,
            "oov_sources": list(OOV_SOURCES), "results": results, "pooled": pooled,
            "git": git_state(ROOT), "created_at": datetime.now(UTC).isoformat()}


def render(data: dict[str, Any]) -> str:
    def cell(r: dict[str, Any]) -> str:
        return "—" if r["rate"] is None else f"{r['rate']:.3f} ({r['caught']}/{r['n']})"

    lines = ["# Độ nhạy bộ chấm ảo giác (dev, mô tả đầu–cuối của bốn hệ SED)", "",
             "> Sinh bởi `scripts.report_checker_sensitivity`; tỷ lệ nhiễu bị bắt (bắt/tổng).", "",
             "| Nhánh | " + " | ".join(KINDS) + " |", "|---|" + "---:|" * len(KINDS)]
    for branch, r in [*data["results"].items(), ("gộp", data["pooled"])]:
        lines.append(f"| {branch} | " + " | ".join(cell(r["by_kind"][k]) for k in KINDS) + " |")
    lines += ["", "| Nguồn ngoài taxonomy | Bị bắt |", "|---|---:|"]
    for source, r in data["pooled"]["by_oov_source"].items():
        lines.append(f"| {source} | {cell(r)} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    data = build()
    stem = M / f"checker_sensitivity_dev_{datetime.now(UTC):%Y%m%d}"
    stem.with_suffix(".json").write_text(json.dumps(data, indent=1, ensure_ascii=False),
                                         encoding="utf-8")
    stem.with_suffix(".md").write_text(render(data), encoding="utf-8")
    print(render(data))


if __name__ == "__main__":
    main()
