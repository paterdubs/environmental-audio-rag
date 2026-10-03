"""Danh mục tài liệu tham khảo theo mẫu khoa.

Quy tắc của mẫu (report/quy_cach_bao_cao.md §1): nhóm theo ngôn ngữ (Việt trước, Anh sau), trong
nhóm xếp alphabet theo **họ** tác giả nước ngoài và theo **tên** tác giả Việt; không có tác giả thì
xếp theo tên cơ quan. Số thứ tự `[n]` đánh liên tục theo danh mục đã sắp xếp, và trích dẫn trong bài
dùng đúng số đó.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

LANGUAGE_ORDER = ("vi", "en")
LANGUAGE_TITLES = {"vi": "Tiếng Việt", "en": "Tiếng Anh"}

_ENTRY = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", re.S)
_FIELD = re.compile(r"(\w+)\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}\s*,?", re.S)


@dataclass(frozen=True)
class Author:
    family: str
    given: str

    @property
    def display(self) -> str:
        return f"{self.given} {self.family}".strip()


@dataclass(frozen=True)
class Entry:
    key: str
    kind: str
    fields: dict[str, str] = field(default_factory=dict)

    @property
    def language(self) -> str:
        return self.fields.get("language", "en")

    @property
    def authors(self) -> list[Author]:
        return parse_authors(self.fields.get("author", ""))


def parse_authors(raw: str) -> list[Author]:
    authors = []
    for part in re.split(r"\s+and\s+", raw.strip()):
        part = part.strip()
        if not part:
            continue
        if part.startswith("{") and part.endswith("}"):
            authors.append(Author(family=part[1:-1], given=""))
        elif "," in part:
            family, given = (piece.strip() for piece in part.split(",", 1))
            authors.append(Author(family=family, given=given))
        else:
            authors.append(Author(family=part, given=""))
    return authors


def parse_bib(text: str) -> list[Entry]:
    entries = []
    for kind, key, body in _ENTRY.findall(text):
        fields = {name.lower(): " ".join(value.split()) for name, value in _FIELD.findall(body)}
        entries.append(Entry(key=key, kind=kind.lower(), fields=fields))
    keys = [entry.key for entry in entries]
    duplicates = {key for key in keys if keys.count(key) > 1}
    if duplicates:
        raise ValueError(f"Khóa BibTeX trùng: {sorted(duplicates)}")
    return entries


def _fold(text: str) -> str:
    """Khóa so sánh không phân biệt dấu (Việt: 'Đ' xếp như 'D')."""
    text = text.replace("Đ", "D").replace("đ", "d")
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch)).casefold()


def sort_key(entry: Entry) -> tuple:
    authors = entry.authors
    if not authors:
        name = entry.fields.get("title", "")
    elif entry.language == "vi" and authors[0].given:
        # Tác giả Việt: xếp theo tên (từ cuối của phần tên riêng), không đảo họ.
        name = authors[0].given.split()[-1] + " " + authors[0].family
    else:
        name = authors[0].family + " " + authors[0].given
    return (_fold(name), entry.fields.get("year", ""), _fold(entry.fields.get("title", "")))


def ordered(entries: list[Entry]) -> list[tuple[str, list[Entry]]]:
    unknown = {entry.language for entry in entries} - set(LANGUAGE_ORDER)
    if unknown:
        raise ValueError(f"Ngôn ngữ chưa có thứ tự nhóm: {sorted(unknown)}")
    groups = []
    for language in LANGUAGE_ORDER:
        members = sorted((e for e in entries if e.language == language), key=sort_key)
        if members:
            groups.append((language, members))
    return groups


def numbering(entries: list[Entry]) -> dict[str, int]:
    number = 0
    result = {}
    for _, members in ordered(entries):
        for entry in members:
            number += 1
            result[entry.key] = number
    return result


def _pages(value: str) -> str:
    return value.replace("--", "–")


def format_entry(entry: Entry) -> list[tuple[str, bool]]:
    """Trả về các đoạn (văn bản, in nghiêng) của một mục, chưa gồm số `[n]`."""
    f = entry.fields
    authors = entry.authors
    names = ", ".join(author.display for author in authors) if authors else ""
    parts: list[tuple[str, bool]] = [(f"{names} ({f.get('year', 'n.d.')}), ", False)]
    title = f.get("title", "")
    if entry.kind == "misc" and f.get("url"):
        parts.append((f"{title}", True))
        parts.append(
            (
                f", {f.get('howpublished', '')}, {f['url']}"
                if f.get("howpublished")
                else f", {f['url']}",
                False,
            )
        )
        if f.get("urldate"):
            year, month, day = f["urldate"].split("-")
            parts.append((f", truy cập {day}/{month}/{year}", False))
        parts.append((".", False))
        return parts
    parts.append((f"“{title}”, ", False))
    if entry.kind == "article":
        parts.append((f.get("journal", ""), True))
        detail = []
        if f.get("volume"):
            detail.append(f"Vol. {f['volume']}" + (f" ({f['number']})" if f.get("number") else ""))
        if f.get("pages"):
            detail.append(f"pp. {_pages(f['pages'])}")
        elif f.get("eid"):
            detail.append(f"Article {f['eid']}")
        parts.append(((", " + ", ".join(detail)) if detail else "", False))
    elif entry.kind == "inproceedings":
        parts.append((f.get("booktitle", ""), True))
        if f.get("pages"):
            parts.append((f", pp. {_pages(f['pages'])}", False))
    else:  # bản arXiv đã đọc trực tiếp
        version = f"v{f['version']}" if f.get("version") else ""
        parts.append(("arXiv preprint", True))
        parts.append((f" arXiv:{f.get('eprint', '')}{version}", False))
    if f.get("doi"):
        parts.append((f", DOI: {f['doi']}", False))
    parts.append((".", False))
    return parts


def load(path: Path) -> list[Entry]:
    return parse_bib(path.read_text(encoding="utf-8"))
