"""Lệnh `-m scripts.X` trong tài liệu phải trỏ tới module có thật và cờ có khai báo (kiểm tĩnh)."""

from pathlib import Path

import pytest

from scripts import check_doc_commands as checker


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "alpha.py").write_text(
        'from scripts.common import shared\nparser.add_argument("--split")\n'
        "parser.add_argument('--tag')\n", encoding="utf-8")
    (tmp_path / "scripts" / "common.py").write_text('p.add_argument("--device")\n',
                                                    encoding="utf-8")
    (tmp_path / "docs").mkdir()
    return tmp_path


def test_extracts_commands_with_powershell_and_bash_continuations():
    text = ("```powershell\n& $py -W ignore -m scripts.alpha ml\\runs\\x `\n  --split test `\n"
            "  --tag t\n```\n.venv/Scripts/python.exe -m scripts.beta --a \\\n    --b 1\n")
    commands = checker.extract_commands(text)
    assert [(c.module, c.flags) for c in commands] == [("alpha", ("--split", "--tag")),
                                                       ("beta", ("--a", "--b"))]
    assert commands[0].line == 2


def test_inline_code_in_a_table_row_is_one_command_per_span():
    text = "| a | `python -m scripts.alpha --split dev` và `python -m scripts.alpha --tag x` |\n"
    assert [c.flags for c in checker.extract_commands(text)] == [("--split",), ("--tag",)]


def test_known_flags_include_flags_of_imported_scripts_modules(repo):
    assert checker.known_flags("alpha", root=repo) == {"--split", "--tag", "--device", "--help"}
    assert checker.known_flags("missing", root=repo) is None


def test_check_reports_missing_modules_and_unknown_flags(repo):
    doc = repo / "docs" / "R.md"
    doc.write_text("`python -m scripts.alpha --split dev --device cuda`\n"
                   "`python -m scripts.alpha --splitt dev`\n`python -m scripts.gone`\n",
                   encoding="utf-8")
    problems = checker.check([doc], root=repo)
    assert [p.message for p in problems] == ["cờ không có trong scripts.alpha: --splitt",
                                             "không có module scripts.gone"]
    assert problems[0].line == 2


def test_repo_documents_reference_only_real_commands():
    root = Path(checker.__file__).resolve().parents[1]
    problems = checker.check([root / name for name in checker.DEFAULT_DOCS], root=root)
    assert problems == [], "\n".join(f"{p.file}:{p.line} {p.message}" for p in problems)
