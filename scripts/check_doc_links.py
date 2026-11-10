"""Kiểm link tương đối trong tài liệu Markdown chính (SYSTEM, STATUS, PLAN, REPRODUCE, CLAUDE...).

    .venv/Scripts/python.exe -m scripts.check_doc_links [file.md ...]

Bỏ qua URL tuyệt đối, neo trong trang (`#...`), đoạn mã inline và khối mã. Link có neo
(`file.md#mục`) chỉ kiểm phần file.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCS = ("CLAUDE.md", "docs/SYSTEM.md", "docs/STATUS.md", "docs/PLAN.md",
                "docs/REPRODUCE.md", "docs/DEMO.md", "docs/PAPER_NOTES.md")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
INLINE_CODE = re.compile(r"`[^`]*`")


@dataclass(frozen=True)
class Problem:
    file: str
    line: int
    target: str


def links(text: str) -> list[tuple[int, str]]:
    found, in_block = [], False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_block = not in_block
            continue
        if in_block:
            continue
        for match in LINK.finditer(INLINE_CODE.sub("", line)):
            found.append((number, match.group(1)))
    return found


def check(paths: list[Path], *, root: Path = ROOT) -> list[Problem]:
    problems = []
    for path in paths:
        for number, target in links(path.read_text(encoding="utf-8")):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            relative = target.split("#", 1)[0]
            if relative and not (path.parent / relative).exists():
                problems.append(Problem(path.relative_to(root).as_posix(), number, target))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", type=Path)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    paths = [p.resolve() for p in args.files] or [ROOT / name for name in DEFAULT_DOCS]
    problems = check(paths)
    for p in problems:
        print(f"[FAIL] {p.file}:{p.line} {p.target}")
    total = sum(len(links(p.read_text(encoding="utf-8"))) for p in paths)
    print(f"{len(paths)} tài liệu, {total} link: {len(problems)} lỗi")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
