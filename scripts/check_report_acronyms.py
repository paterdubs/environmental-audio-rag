"""Kiểm chữ viết tắt trong nguồn báo cáo theo quy tắc của mẫu khoa.

    .venv/Scripts/python.exe -m scripts.check_report_acronyms [--source report/gon_src] [--strict]

Mẫu khoa: "Viết tắt sau lần viết đầy đủ thứ nhất và chữ viết tắt để trong ngoặc đơn", và
danh mục viết tắt xếp A, B, C. Script đọc thân bài theo thứ tự chương (từ Chương 1), cộng
các bảng được nhúng bằng `@@INCLUDE`, rồi báo bốn loại vấn đề:

- chữ có trong danh mục nhưng không dùng ở đâu;
- chữ dùng từ hai lần trở lên nhưng thiếu trong danh mục;
- lần xuất hiện thứ nhất không có dạng đầy đủ đi kèm (trong ngoặc ngay trước hoặc sau);
- danh mục không xếp theo thứ tự chữ cái.

Tóm tắt và Abstract được kiểm riêng, mỗi trang tự định nghĩa chữ của mình. Việc nhận ra
dạng đầy đủ dựa trên dấu ngoặc nên vẫn cần đọc lại bằng mắt; script chỉ khoanh vùng.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from scripts.report_docx import display as display_mod

ROOT = Path(__file__).resolve().parents[1]
LIST_TITLE = "@@HEADING1N:DANH MỤC CÁC THUẬT NGỮ VIẾT TẮT@@"
INCLUDE = re.compile(r"@@INCLUDE:([^|@]+)(?:\|[^@]*)?@@")
TOKEN = re.compile(
    r"(?<![\w@./-])([a-z]?[A-Z][A-Za-z0-9]*[A-Z][A-Za-z0-9]*(?:-[A-Z0-9][A-Za-z0-9]*)*)")
STRIP = (
    re.compile(r"`[^`]*`"),            # mã, class_id
    re.compile(r"\[@[^\]]*\]"),         # trích dẫn
    re.compile(r"@@[A-Z0-9]+(?::[^@]*)?@@"),
    re.compile(r"⟪[^⟫]*⟫"),
    re.compile(r"\$\$?[^$]*\$\$?"),     # công thức
    re.compile(r"!\[[^\]]*\]\([^)]*\)"),
    re.compile(r"https?://\S+"),
    re.compile(r"\S+\.(?:json|md|py|csv|yaml|pt|npz|docx|pdf|png|wav)\b"),
)
# Tên riêng, đơn vị và từ thường không phải chữ viết tắt cần định nghĩa.
IGNORE = frozenset({
    "AudioSet", "PyTorch", "PostgreSQL", "FastAPI", "GitHub", "TypeScript", "FlagEmbedding",
    "TS", "ThS", "PGS", "GS", "IUH", "KHDL18A", "HCM", "FFFFFF", "NaN", "OpenAI", "CUDA",
    "SpecAugment", "FilterAugment", "AudioSet-Strong", "PretrainedSED", "MobileNet", "LaTeX",
    "Frame-MobileNet", "DejaVu", "ColorBrewer", "PDF", "DOCX", "OOXML", "UTF-8", "ID", "ASCII",
    "GiB", "MB", "GB", "KB", "kHz", "Hz", "dB", "ms",
    "GET", "POST", "PUT", "DELETE", "EN", "VI", "PASS", "OOF",  # phương thức, mã trong bảng
    "CNN14", "WAV", "FLAC", "OGG", "MP3",  # tên mô hình và định dạng tệp
})
SKIP_LINE = ("#", "**Title:**", "**Tên đề tài:**")


@dataclass(frozen=True)
class Entry:
    acronym: str
    full: str


def normalise(token: str) -> str:
    """PSDS-2 → PSDS, nDCG@10 → nDCG, BLEU-4 → BLEU, RQ1 → RQ; giữ SHA-256, BGE-M3, CNN14."""
    if token in {"SHA-256", "BGE-M3", "CNN14", "LA-RAG", "MD5"}:
        return token
    token = re.sub(r"-\d+$", "", token)
    return re.sub(r"(?<=[A-Z])\d+$", "", token)


def clean(line: str) -> str:
    if line.lstrip().startswith(SKIP_LINE):
        return ""
    for pattern in STRIP:
        line = pattern.sub(" ", line)
    return line


def read_list(front: str) -> list[Entry]:
    start = front.index(LIST_TITLE)
    entries = []
    for line in front[start:].splitlines()[1:]:
        if line.startswith("@@") and entries:
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        header = cells[0] in {"Từ viết tắt", "---"} or set(cells[0]) <= {"-"}
        if len(cells) >= 2 and not header:
            entries.append(Entry(cells[0], cells[1]))
    return entries


def body_lines(source: Path) -> list[tuple[str, int, str]]:
    """(tệp, số dòng, nội dung) của Chương 1 trở đi, kèm dòng của bảng được nhúng.

    Bảng nhúng được đổi tên theo `display.yaml` của bản báo cáo, đúng như lúc dựng.
    """
    shown = display_mod.load(source / "display.yaml")
    rows = []
    for path in sorted(source.glob("[0-9][0-9]_*.md")):
        if path.name.startswith("00_"):
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = INCLUDE.search(line)
            if match:
                table = ROOT / match.group(1).strip()
                lines = display_mod.apply_table(
                    table.read_text(encoding="utf-8").splitlines(), table.name, shown)
                for t_number, t_line in enumerate(lines, 1):
                    if t_line.startswith("|"):
                        rows.append((table.name, t_number, t_line))
                continue
            rows.append((path.name, number, line))
    return rows


def front_parts(front: str) -> dict[str, str]:
    abstract = front.split("@@TITLE:ABSTRACT@@", 1)[1].split("@@PAGEBREAK@@", 1)[0]
    summary = front.split("@@TITLE:TÓM TẮT@@", 1)[1].split("@@PAGEBREAK@@", 1)[0]
    return {"Abstract": abstract, "Tóm tắt": summary}


def is_defined(line: str, start: int, end: int, full: str) -> bool:
    before, after = line[max(0, start - 3):start], line[end:end + 2]
    if before.endswith("– ") and line[end:end + 1] in {")", ",", ";"}:
        return True
    if before.endswith("("):
        return True
    if after.startswith(" ("):
        return True
    return bool(full) and full.split(",")[0].strip().lower() in line.lower()


def tokens(line: str) -> list[tuple[str, int, int]]:
    return [(normalise(m.group(1)), m.start(1), m.end(1)) for m in TOKEN.finditer(line)]


def first_uses(lines: list[tuple[str, int, str]], known: dict[str, str]) -> tuple[Counter, dict]:
    counts, first = Counter(), {}
    for name, number, raw in lines:
        line = clean(raw)
        for token, start, end in tokens(line):
            if token in IGNORE:
                continue
            counts[token] += 1
            if token not in first:
                first[token] = (name, number, is_defined(line, start, end, known.get(token, "")))
    return counts, first


def check(source: Path) -> list[str]:
    front = (source / "00_phan_dau.md").read_text(encoding="utf-8")
    entries = read_list(front)
    known = {e.acronym: e.full for e in entries}
    counts, first = first_uses(body_lines(source), known)
    problems = []
    order = [e.acronym.lower() for e in entries]
    if order != sorted(order):
        problems.append("danh mục: chưa xếp theo thứ tự chữ cái")
    for entry in entries:
        if counts[entry.acronym] == 0:
            problems.append(f"danh mục có nhưng thân bài không dùng: {entry.acronym}")
    for token, count in sorted(counts.items()):
        if count >= 2 and token not in known:
            name, number, _ = first[token]
            problems.append(f"dùng {count} lần, thiếu trong danh mục: {token} ({name}:{number})")
    for token, (name, number, defined) in sorted(first.items()):
        if token in known and not defined:
            problems.append(f"lần đầu chưa viết đầy đủ: {token} ({name}:{number})")
    for part, text in front_parts(front).items():
        seen = set()
        for line in text.splitlines():
            cleaned = clean(line)
            for token, start, end in tokens(cleaned):
                if token in known and token not in seen and token not in IGNORE:
                    seen.add(token)
                    if not is_defined(cleaned, start, end, known[token]):
                        problems.append(f"{part}: chưa viết đầy đủ {token}")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", default="report/gon_src")
    parser.add_argument("--strict", action="store_true", help="trả mã lỗi 1 nếu có vấn đề")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    problems = check(ROOT / args.source)
    for problem in problems:
        print(problem)
    print(f"{len(problems)} vấn đề")
    if args.strict and problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
