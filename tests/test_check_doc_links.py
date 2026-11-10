"""Link tương đối trong tài liệu Markdown phải trỏ tới file/thư mục có thật."""

from pathlib import Path

from scripts import check_doc_links as checker


def test_reports_missing_relative_targets_and_ignores_urls_anchors_and_code(tmp_path: Path):
    docs = tmp_path / "docs"
    (docs / "decisions").mkdir(parents=True)
    (docs / "decisions" / "ADR-0001-a.md").write_text("x", encoding="utf-8")
    page = docs / "P.md"
    page.write_text(
        "[ok](decisions/ADR-0001-a.md) [mục](#1-tong-quan) [web](https://example.org)\n"
        "[thư mục](decisions/) [sai](decisions/ADR-0002-b.md) [neo](decisions/ADR-0001-a.md#x)\n"
        "`[không phải link](nowhere.md)`\n```\n[trong khối mã](nowhere.md)\n```\n",
        encoding="utf-8")
    problems = checker.check([page], root=tmp_path)
    assert [(p.line, p.target) for p in problems] == [(2, "decisions/ADR-0002-b.md")]


def test_repo_documents_have_no_broken_relative_links():
    root = Path(checker.__file__).resolve().parents[1]
    problems = checker.check([root / name for name in checker.DEFAULT_DOCS], root=root)
    assert problems == [], "\n".join(f"{p.file}:{p.line} {p.target}" for p in problems)
