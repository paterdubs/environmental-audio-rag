"""Kiểm tĩnh lệnh `python -m scripts.X ...` trong tài liệu (REPRODUCE, CLAUDE §7, DEMO).

    .venv/Scripts/python.exe -m scripts.check_doc_commands [file.md ...]

Mỗi lệnh phải trỏ tới `scripts/X.py` có thật, và mọi cờ `--...` của nó phải xuất hiện dưới dạng
chuỗi `"--cờ"`/`'--cờ'` trong mã nguồn của module hoặc của module `scripts.*` mà nó import (ví dụ
`train_sed` dùng cờ chung). Không import, không chạy gì — đọc mã nguồn. Lệnh nối dòng bằng
dấu `` ` `` (PowerShell) hoặc `\\` (bash) được gộp; mỗi đoạn mã inline là một lệnh riêng.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCS = ("docs/REPRODUCE.md", "CLAUDE.md", "docs/DEMO.md")
COMMAND = re.compile(r"-m\s+scripts\.([a-z0-9_]+)")
FLAG = re.compile(r"(?<![\w-])--[a-z0-9][a-z0-9-]*")
IMPORT = re.compile(r"from scripts(?:\.([a-z0-9_]+))? import ([a-z0-9_, ()\n]+)")


@dataclass(frozen=True)
class Command:
    module: str
    flags: tuple[str, ...]
    line: int


@dataclass(frozen=True)
class Problem:
    file: str
    line: int
    message: str


def _segments(line: str) -> list[str]:
    """Đoạn chứa lệnh: từng đoạn mã inline nếu có, không thì cả dòng."""
    spans = re.findall(r"`([^`]*-m\s+scripts\.[^`]*)`", line)
    return spans or [line]


def extract_commands(text: str) -> list[Command]:
    lines = text.splitlines()
    commands: list[Command] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        start = index
        if COMMAND.search(line) and not re.search(r"`[^`]*-m\s+scripts\.", line):
            joined = line
            while joined.rstrip().endswith(("`", "\\")) and index + 1 < len(lines):
                index += 1
                joined = joined.rstrip()[:-1] + " " + lines[index]
            segments = [joined]
        else:
            segments = _segments(line) if COMMAND.search(line) else []
        for segment in segments:
            for match, nxt in _with_next(list(COMMAND.finditer(segment))):
                tail = segment[match.end(): nxt.start() if nxt else None]
                commands.append(Command(match.group(1), tuple(FLAG.findall(tail)), start + 1))
        index += 1
    return commands


def _with_next(matches: list[re.Match[str]]) -> list[tuple[re.Match[str], re.Match[str] | None]]:
    return [(m, matches[i + 1] if i + 1 < len(matches) else None) for i, m in enumerate(matches)]


def known_flags(module: str, *, root: Path = ROOT, _seen: frozenset[str] = frozenset()
                ) -> set[str] | None:
    path = root / "scripts" / f"{module}.py"
    if not path.exists():
        return None
    source = path.read_text(encoding="utf-8")
    flags = set(re.findall(r"""["'](--[a-z0-9][a-z0-9-]*)["']""", source)) | {"--help"}
    for package_module, names in IMPORT.findall(source):
        imported = [package_module] if package_module else [
            n.strip() for n in re.split(r"[,\s()]+", names) if n.strip()]
        for name in imported:
            if name and name not in _seen and name != module:
                flags |= known_flags(name, root=root, _seen=_seen | {module}) or set()
    return flags


def check(paths: list[Path], *, root: Path = ROOT) -> list[Problem]:
    problems: list[Problem] = []
    cache: dict[str, set[str] | None] = {}
    for path in paths:
        name = path.relative_to(root).as_posix()
        for command in extract_commands(path.read_text(encoding="utf-8")):
            if command.module not in cache:
                cache[command.module] = known_flags(command.module, root=root)
            flags = cache[command.module]
            if flags is None:
                missing = f"không có module scripts.{command.module}"
                problems.append(Problem(name, command.line, missing))
                continue
            unknown = [f for f in command.flags if f not in flags]
            if unknown:
                problems.append(Problem(name, command.line,
                                        f"cờ không có trong scripts.{command.module}: "
                                        + ", ".join(unknown)))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", type=Path)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    paths = [p.resolve() for p in args.files] or [ROOT / name for name in DEFAULT_DOCS]
    problems = check(paths)
    for problem in problems:
        print(f"[FAIL] {problem.file}:{problem.line} {problem.message}")
    n = sum(len(extract_commands(p.read_text(encoding="utf-8"))) for p in paths)
    print(f"{len(paths)} tài liệu, {n} lệnh: {len(problems)} lỗi")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
