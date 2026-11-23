"""Khối lượng thực hiện của dự án, đếm từ chính repo (commit, ADR, đo đạc, mã, kiểm thử, run).

Mọi số đếm bằng lệnh có thể chạy lại; không ước lượng. Số run đếm thư mục trong `ml/runs/` của bản
sao hiện tại (thư mục này không nằm trong git), nên đây là số của máy làm việc.

    .venv/Scripts/python.exe -m scripts.report_workload
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ml.provenance import git_state

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "docs" / "measurements"
PYTHON_DIRS = ("ml", "scripts", "tests", "services")
SKIP_PARTS = {"node_modules", "__pycache__", ".venv", "dist"}


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True,
                          text=True, encoding="utf-8").stdout.strip()


def _lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def _files(root: Path, suffixes: tuple[str, ...]) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file() and p.suffix in suffixes
            and not SKIP_PARTS & set(p.parts)]


def count_python_lines() -> dict[str, int]:
    return {name: sum(_lines(p) for p in _files(ROOT / name, (".py",)))
            for name in PYTHON_DIRS if (ROOT / name).is_dir()}


def count_frontend_lines() -> int:
    return sum(_lines(p) for p in _files(ROOT / "services" / "frontend" / "src", (".ts", ".tsx")))


def count_test_functions() -> int:
    pattern = re.compile(r"^\s*(?:async\s+)?def test_", re.MULTILINE)
    return sum(len(pattern.findall(p.read_text(encoding="utf-8", errors="replace")))
               for p in _files(ROOT / "tests", (".py",)))


def count_runs() -> dict[str, int]:
    runs = ROOT / "ml" / "runs"
    names = [p.name for p in runs.iterdir() if p.is_dir()] if runs.is_dir() else []
    return {"sed": sum(n.startswith("sed_polyphonic_") for n in names),
            "classifier": sum(n.startswith("classifier_datasec_") for n in names),
            "total_dirs": len(names)}


def build() -> dict[str, Any]:
    dates = _git("log", "--format=%as").splitlines()
    return {
        "commits": int(_git("rev-list", "--count", "HEAD")),
        "first_commit": dates[-1], "last_commit": dates[0],
        "adr": len([p for p in (ROOT / "docs" / "decisions").glob("ADR-*.md")]),
        "measurement_reports": len(list(M.glob("*.md"))),
        "python_lines": count_python_lines(),
        "frontend_lines": count_frontend_lines(),
        "test_functions": count_test_functions(),
        "json_schemas": len(list((ROOT / "contracts").glob("*.schema.json"))),
        "runs": count_runs(),
        "git": git_state(ROOT), "created_at": datetime.now(UTC).isoformat(),
    }


def render(data: dict[str, Any]) -> str:
    py = data["python_lines"]
    return "\n".join([
        "# Khối lượng thực hiện (đếm từ repo)", "",
        f"- Commit: {data['commits']} ({data['first_commit']} đến {data['last_commit']})",
        f"- ADR: {data['adr']}; báo cáo đo: {data['measurement_reports']}",
        "- Dòng Python: " + ", ".join(f"{k} {v}" for k, v in py.items())
        + f" (tổng {sum(py.values())}); giao diện TS/TSX: {data['frontend_lines']}",
        f"- Hàm kiểm thử: {data['test_functions']}; JSON Schema: {data['json_schemas']}",
        f"- Run huấn luyện: SED {data['runs']['sed']}, phân loại {data['runs']['classifier']}",
        ""])


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    data = build()
    stem = f"workload_{datetime.now(UTC):%Y%m%d}"
    (M / f"{stem}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False),
                                    encoding="utf-8")
    (M / f"{stem}.md").write_text(render(data), encoding="utf-8")
    print(render(data))


if __name__ == "__main__":
    main()
