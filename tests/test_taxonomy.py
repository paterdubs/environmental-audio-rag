from pathlib import Path

from ml.taxonomy import load_taxonomy, normalize_text

ROOT = Path(__file__).resolve().parents[1]


def test_taxonomy_cardinality_and_polyphonic_subset() -> None:
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    assert len(taxonomy.class_ids) == 22
    assert len(taxonomy.polyphonic_class_ids) == 21
    assert "wind_turbine" not in taxonomy.polyphonic_class_ids
    assert sum(len(item.subclasses) for item in taxonomy.classes) == 28


def test_source_labels_have_unique_normalized_aliases() -> None:
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    assert len(taxonomy.alias_to_id) >= 22
    assert taxonomy.alias_to_id[normalize_text("Sirens and alarms")] == "sirens_and_alarms"

