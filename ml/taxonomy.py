from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import yaml


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


@dataclass(frozen=True)
class TaxonomyClass:
    class_id: str
    source_label: str
    aliases: tuple[str, ...]
    subclasses: tuple[str, ...]
    polyphonic: bool


@dataclass(frozen=True)
class Taxonomy:
    version: str
    classes: tuple[TaxonomyClass, ...]
    checksum: str

    @property
    def class_ids(self) -> tuple[str, ...]:
        return tuple(item.class_id for item in self.classes)

    @property
    def polyphonic_class_ids(self) -> tuple[str, ...]:
        return tuple(item.class_id for item in self.classes if item.polyphonic)

    @property
    def alias_to_id(self) -> dict[str, str]:
        aliases: dict[str, str] = {}
        for item in self.classes:
            for alias in (item.class_id, item.source_label, *item.aliases):
                normalized = normalize_text(alias)
                if normalized in aliases and aliases[normalized] != item.class_id:
                    raise ValueError(f"Ambiguous taxonomy alias: {alias}")
                aliases[normalized] = item.class_id
        return aliases


def load_taxonomy(path: Path) -> Taxonomy:
    content = path.read_bytes()
    raw = yaml.safe_load(content)
    classes = tuple(
        TaxonomyClass(
            class_id=item["id"],
            source_label=item["source_label"],
            aliases=tuple(item.get("aliases", [])),
            subclasses=tuple(item.get("subclasses", [])),
            polyphonic=bool(item.get("polyphonic", True)),
        )
        for item in raw["classes"]
    )
    if len({item.class_id for item in classes}) != len(classes):
        raise ValueError("Duplicate taxonomy class IDs")
    return Taxonomy(
        version=str(raw["version"]),
        classes=classes,
        checksum=hashlib.sha256(content).hexdigest(),
    )


def taxonomy_snapshot(taxonomy: Taxonomy) -> str:
    return json.dumps(
        {
            "version": taxonomy.version,
            "checksum": taxonomy.checksum,
            "class_ids": taxonomy.class_ids,
            "polyphonic_class_ids": taxonomy.polyphonic_class_ids,
        },
        indent=2,
    )
