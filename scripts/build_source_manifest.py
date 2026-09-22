from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from ml.dataops.sources import load_sources

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    sources = load_sources(ROOT / "ml" / "configs" / "sources.yaml")
    result = {"generated_at": datetime.now(UTC).isoformat(), "sources": {}}
    for name, source in sources.items():
        metadata_path = ROOT / "data" / "reference" / f"zenodo_{name}_{source.record_id}.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        archive = ROOT / "data" / "raw" / name / "archives" / source.expected_file
        extracted = ROOT / "data" / "raw" / name / "extracted"
        archive_complete = archive.exists() and archive.stat().st_size == source.expected_size
        documentation = (
            sorted(
                path.relative_to(extracted).as_posix()
                for path in extracted.rglob("*")
                if path.is_file()
                and any(token in path.name.lower() for token in ("license", "readme"))
            )
            if extracted.exists()
            else []
        )
        result["sources"][name] = {
            "record_id": source.record_id,
            "doi": metadata["metadata"].get("doi", metadata.get("doi")),
            "publication_date": metadata["metadata"].get("publication_date"),
            "license_from_zenodo_metadata": metadata["metadata"].get("license", {}).get("id"),
            "record_url": source.record_url,
            "archive_file": source.expected_file,
            "archive_bytes": source.expected_size,
            "archive_md5": source.expected_md5,
            "archive_complete": archive_complete,
            "archive_sha256": sha256_file(archive) if archive_complete else None,
            "license_or_readme_inside_archive": documentation,
        }
    output = ROOT / "data" / "manifests" / "source_archives.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
