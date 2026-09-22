from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ml.dataops.datased import build_recordings, locate_datased, normalize_events
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    raw_root = ROOT / "data" / "raw" / "datased" / "extracted"
    manifest_root = ROOT / "data" / "manifests"
    annotation_root = ROOT / "data" / "annotations"
    inventory = pd.read_csv(manifest_root / "datased_inventory.csv")
    taxonomy = load_taxonomy(ROOT / "ml" / "configs" / "taxonomy.yaml")
    wav_directory, source_labels = locate_datased(raw_root)
    recordings = build_recordings(inventory, wav_directory, raw_root)
    manifest_root.mkdir(parents=True, exist_ok=True)
    annotation_root.mkdir(parents=True, exist_ok=True)
    recordings.to_csv(manifest_root / "datased_recordings.csv", index=False, lineterminator="\n")

    audit = {
        "recordings": len(recordings),
        "hours": float(recordings["duration_s"].sum() / 3600),
        "exact_duplicate_groups": int(
            (recordings.groupby("content_sha256").size() > 1).sum()
        ),
        "taxonomy_version": taxonomy.version,
        "taxonomy_sha256": taxonomy.checksum,
        "annotations": {},
    }
    for mode, source_path in source_labels.items():
        events, mode_audit = normalize_events(
            source_path,
            mode=mode,
            recordings=recordings,
            taxonomy=taxonomy,
        )
        events.to_csv(
            annotation_root / f"datased_{mode}_events.csv", index=False, lineterminator="\n"
        )
        audit["annotations"][mode] = mode_audit
    audit_path = manifest_root / "datased_preparation_audit.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
