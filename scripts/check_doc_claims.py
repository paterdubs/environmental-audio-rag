"""Đối chiếu số chính trong tài liệu với artifact (ADR-0048 §4).

    .venv/Scripts/python.exe -m scripts.check_doc_claims [--claims <yaml>] [--runs-root <dir>]

Mỗi claim trong `docs/claims.yaml` trỏ tới một giá trị trong một JSON đã sinh (measurement hoặc
artifact trong `ml/runs/`) và liệt kê các câu trong tài liệu ghi giá trị đó. Mẫu câu chứa đúng một
`{value}`; mọi lần mẫu khớp trong file phải ghi đúng giá trị đã làm tròn, và phải khớp ít nhất một
lần — không thấy câu nào là lỗi, không phải "đạt". Khoảng trắng và xuống dòng được gộp trước khi so,
vì tài liệu ngắt dòng ở 100 ký tự. Nguồn `ml/runs/...` đọc từ `--runs-root` (worktree không có run).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
NUMBER = r"([-+]?\d+\.\d+)"
WHITESPACE = re.compile(r"\s+")
UNICODE_MINUS = "−"  # tài liệu viết "−0.0128"; so như "-0.0128"


def normalise(text: str) -> str:
    return WHITESPACE.sub(" ", text).replace(UNICODE_MINUS, "-")


@dataclass(frozen=True)
class Failure:
    claim: str
    file: str
    message: str


def load_claims(path: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return list(data["claims"])


def select(data: Any, key: list[Any]) -> Any:
    """Đi theo khóa dict (str), chỉ số list (int), hoặc bộ lọc {trường: giá trị, ...} khớp một."""
    for part in key:
        if isinstance(part, dict):
            matches = [item for item in data if isinstance(item, dict)
                       and all(item.get(f) == w for f, w in part.items())]
            if len(matches) != 1:
                raise KeyError(f"{part}: {len(matches)} khớp")
            data = matches[0]
        else:
            data = data[part]
    return data


def mention_regex(template: str) -> re.Pattern[str]:
    parts = normalise(template).split("{value}")
    if len(parts) != 2:
        raise ValueError(f"mẫu phải có đúng một {{value}}: {template!r}")
    return re.compile(re.escape(parts[0]) + NUMBER + re.escape(parts[1]))


def resolve_source(source: str, *, root: Path, runs_root: Path) -> Path:
    parts = Path(source).parts
    if parts[:2] == ("ml", "runs"):
        return runs_root.joinpath(*parts[2:])
    return root / source


def check(claims: list[dict[str, Any]], *, root: Path, runs_root: Path) -> list[Failure]:
    failures: list[Failure] = []
    texts: dict[str, str] = {}
    for spec in claims:
        source = resolve_source(spec["source"], root=root, runs_root=runs_root)
        try:
            value = float(select(json.loads(source.read_text(encoding="utf-8")), spec["key"]))
        except (KeyError, IndexError, TypeError, ValueError) as error:
            failures.append(Failure(spec["id"], spec["source"],
                                    f"khóa {spec['key']} không đọc được: {error}"))
            continue
        for mention in spec["mentions"]:
            name = mention["file"]
            if name not in texts:
                texts[name] = normalise((root / name).read_text(encoding="utf-8"))
            decimals = int(mention.get("decimals", spec.get("decimals", 4)))
            expected = f"{value:.{decimals}f}"
            found = mention_regex(mention["text"]).findall(texts[name])
            if not found:
                failures.append(Failure(spec["id"], name, f"không thấy mẫu {mention['text']!r}"))
            for written in found:
                if written.lstrip("+") != expected:
                    message = f"ghi {written}, artifact {expected} ({spec['source']})"
                    failures.append(Failure(spec["id"], name, message))
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims", type=Path, default=ROOT / "docs/claims.yaml")
    parser.add_argument("--runs-root", type=Path, default=ROOT / "ml/runs")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    claims = load_claims(args.claims)
    failures = check(claims, root=ROOT, runs_root=args.runs_root)
    n_mentions = sum(len(c["mentions"]) for c in claims)
    for failure in failures:
        print(f"[FAIL] {failure.claim} · {failure.file}: {failure.message}")
    print(f"{len(claims)} claim, {n_mentions} câu: {len(failures)} lỗi")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
