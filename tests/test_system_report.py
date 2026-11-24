"""Hai bảng và sơ đồ hệ thống của Chương 5 phải khớp mã nguồn (scripts/report_system_tables,
scripts/build_system_figures)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import report_system_tables as tables
from scripts.build_system_figures import (
    ERD_LAYOUT,
    MIGRATION,
    SERVED_RUN,
    parse_schema,
    served_facts,
)

SQL = """
CREATE TABLE parent (
    parent_id TEXT PRIMARY KEY,
    embedding VECTOR(8)
);

CREATE TABLE child (
    parent_id TEXT NOT NULL REFERENCES parent(parent_id) ON DELETE CASCADE,
    other_id BIGINT NOT NULL,
    PRIMARY KEY (parent_id, other_id)
);
"""


def test_parse_schema_reads_keys_vectors_and_foreign_keys():
    parent, child = parse_schema(SQL)
    assert parent.columns == (("parent_id", "TEXT", True), ("embedding", "vector(8)", False))
    assert child.references == (("parent_id", "parent"),)
    assert [primary for _, _, primary in child.columns] == [True, True]


def test_every_migrated_table_has_a_place_on_the_erd():
    names = {table.name for table in parse_schema(MIGRATION.read_text(encoding="utf-8"))}
    assert names == set(ERD_LAYOUT)


def test_api_table_covers_exactly_the_routes_in_code():
    found = set()
    for path in tables.SERVICE_SOURCES:
        service = "Suy luận" if "inference" in path.parts else "API"
        found |= {(service, method, route) for method, route in tables.routes(path)}
    assert found == set(tables.ENDPOINTS)


def test_router_prefix_is_applied(tmp_path: Path):
    source = tmp_path / "r.py"
    source.write_text(
        'router = APIRouter(prefix="/api/v1")\n\n@router.get("/x")\nasync def x():\n    pass\n',
        encoding="utf-8",
    )
    assert tables.routes(source) == [("GET", "/api/v1/x")]


def test_tech_versions_come_from_dependency_files():
    sources = {
        "pip": tables.pip_versions(),
        "npm": tables.npm_versions(),
        "image": tables.compose_images(),
        "docker": tables.docker_bases(),
    }
    versions = {tech.name: tables.resolve_version(tech, sources) for tech in tables.ROLES}
    assert versions["PostgreSQL 16 + pgvector"] == "pg16"
    assert versions["React"].startswith("^19")
    with pytest.raises(KeyError):
        tables.resolve_version(tables.Tech("x", "x", "pip:no-such-package", "x"), sources)


@pytest.mark.skipif(not SERVED_RUN.is_file(), reason="ml/runs không nằm trong git (CI)")
def test_served_facts_match_b0_manifest():
    facts = served_facts()
    assert (facts.folds, facts.window_s, facts.hop_s, facts.recipe) == (5, 10.0, 5.0, "t2b")
