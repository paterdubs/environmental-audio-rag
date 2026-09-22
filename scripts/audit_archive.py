"""Audit a dataset archive before extraction (data gate D0/D1).

Usage:
    python -m scripts.audit_archive datasec
    python -m scripts.audit_archive datased --label-depth 2 --skip-md5
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ml.dataops.archive_audit import audit_archive, audit_payload, write_audit
from ml.dataops.sources import load_sources
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "ml" / "configs" / "sources.yaml"
TAXONOMY = ROOT / "ml" / "configs" / "taxonomy.yaml"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", choices=["datasec", "datased"])
    parser.add_argument(
        "--label-depth",
        type=int,
        default=1,
        help="Path index holding the coarse label (DATASEC/<class>/... = 1)",
    )
    parser.add_argument(
        "--labels-in-annotations",
        action="store_true",
        help="Labels live in annotation tables, not folder names (DataSED)",
    )
    parser.add_argument(
        "--skip-md5",
        action="store_true",
        help="Skip the MD5 pass; size is still checked",
    )
    args = parser.parse_args()

    source = load_sources(SOURCES)[args.dataset]
    taxonomy = load_taxonomy(TAXONOMY)
    archive = ROOT / "data" / "raw" / args.dataset / "archives" / source.expected_file
    audit = audit_archive(
        source,
        archive,
        taxonomy,
        label_depth=None if args.labels_in_annotations else args.label_depth,
        verify_md5=not args.skip_md5,
    )

    destination = ROOT / "data" / "manifests" / f"{args.dataset}_archive_audit.json"
    write_audit(audit, destination)
    payload = audit_payload(audit)
    print(
        json.dumps(
            {key: payload[key] for key in ("dataset", "verdict", "size_match", "md5_match")}
            | {
                "audio_files": payload["audio_files"],
                "coarse_labels": payload["coarse_labels"],
                "subclass_labels": payload["subclass_labels"],
                "unmapped_labels": payload["unmapped_labels"],
                "manifest": str(destination.relative_to(ROOT)),
            },
            ensure_ascii=False,
        )
    )
    if audit.verdict != "pass":
        raise SystemExit(f"{args.dataset}: archive audit verdict={audit.verdict}")


if __name__ == "__main__":
    main()
