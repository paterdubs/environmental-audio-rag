"""Architecture guards for service boundaries."""

from __future__ import annotations

import ast
from pathlib import Path

API_DIRECTORY = Path(__file__).resolve().parents[1] / "services" / "api"


def _torch_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(
                alias.name
                for alias in node.names
                if alias.name == "torch" or alias.name.startswith("torch.")
            )
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "torch" or node.module.startswith("torch."):
                imports.append(node.module)
    return imports


def test_api_does_not_import_torch() -> None:
    violations: dict[str, list[str]] = {}
    for path in API_DIRECTORY.rglob("*.py"):
        imports = _torch_imports(path)
        if imports:
            violations[path.relative_to(API_DIRECTORY).as_posix()] = imports

    assert not violations, (
        "services/api must not import torch; inference belongs in services/inference. "
        f"Found: {violations}"
    )
