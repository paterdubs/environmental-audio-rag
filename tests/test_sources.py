from pathlib import Path

from ml.dataops.sources import load_sources

ROOT = Path(__file__).resolve().parents[1]


def test_source_contract_is_frozen() -> None:
    sources = load_sources(ROOT / "ml" / "configs" / "sources.yaml")
    assert set(sources) == {"datasec", "datased"}
    assert sources["datasec"].expected_size == 6_414_663_316
    assert sources["datased"].expected_md5 == "44e093f675fc44cfb8a11b68456b72d7"

