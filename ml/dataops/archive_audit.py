"""Audit a downloaded dataset archive before extraction.

The audit reads the ZIP central directory only, so it is cheap enough to run as
gate D0/D1 on a multi-gigabyte archive. It answers four questions the data plan
requires before any extraction:

1. Does the archive match the size and MD5 recorded in the source config?
2. How many audio entries does it hold, and how large are they uncompressed?
3. Does the label layout (directory tree or annotation CSV) match expectations?
4. Does every label present in the archive map to the versioned taxonomy?
"""

from __future__ import annotations

import json
import zipfile
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

from ml.dataops.sources import Source, stream_md5
from ml.taxonomy import Taxonomy, normalize_text

AUDIO_SUFFIXES = frozenset({".wav", ".flac", ".mp3", ".ogg"})


@dataclass(frozen=True)
class LabelNode:
    """One coarse label observed in the archive, with its observed subclasses."""

    source_label: str
    canonical_class_id: str | None
    files: int
    subclasses: dict[str, int] = field(default_factory=dict)

    @property
    def is_mapped(self) -> bool:
        return self.canonical_class_id is not None


@dataclass(frozen=True)
class ArchiveAudit:
    dataset: str
    archive_name: str
    bytes_actual: int
    bytes_expected: int
    md5_actual: str | None
    md5_expected: str
    entries: int
    audio_files: int
    uncompressed_bytes: int
    annotation_files: tuple[str, ...]
    documentation_files: tuple[str, ...]
    taxonomy_version: str
    taxonomy_sha256: str
    labels: tuple[LabelNode, ...]

    @property
    def size_match(self) -> bool:
        return self.bytes_actual == self.bytes_expected

    @property
    def md5_match(self) -> bool | None:
        """``None`` when the MD5 pass was skipped, so callers cannot read it as success."""
        if self.md5_actual is None:
            return None
        return self.md5_actual == self.md5_expected

    @property
    def unmapped_labels(self) -> tuple[str, ...]:
        return tuple(node.source_label for node in self.labels if not node.is_mapped)

    @property
    def verdict(self) -> str:
        """Gate verdict. A skipped MD5 never reports a full ``pass``."""
        if not self.size_match or self.md5_match is False:
            return "fail_checksum"
        if self.unmapped_labels:
            return "fail_unmapped_label"
        return "pass" if self.md5_match else "pass_unverified_md5"


def _classify_entries(names: list[str]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Split non-audio entries into annotation tables and documentation."""
    annotations, documentation = [], []
    for name in names:
        suffix = Path(name).suffix.lower()
        if suffix in {".csv", ".tsv", ".json", ".jams"}:
            annotations.append(name)
        elif suffix in {".txt", ".md", ".pdf", ".doc", ".docx"} or Path(name).stem.upper() in {
            "LICENSE",
            "README",
            "COPYING",
        }:
            documentation.append(name)
    return tuple(sorted(annotations)), tuple(sorted(documentation))


def _is_audio(name: str) -> bool:
    return Path(name).suffix.lower() in AUDIO_SUFFIXES


def _count_audio(archive: zipfile.ZipFile) -> tuple[int, int]:
    """Count audio entries and their uncompressed size, ignoring labels."""
    files = 0
    uncompressed = 0
    for info in archive.infolist():
        if info.is_dir() or not _is_audio(info.filename):
            continue
        files += 1
        uncompressed += info.file_size
    return files, uncompressed


def _collect_labels(
    archive: zipfile.ZipFile, taxonomy: Taxonomy, *, label_depth: int
) -> tuple[tuple[LabelNode, ...], int, int]:
    """Read coarse/subclass labels from the directory layout of audio entries."""
    alias = taxonomy.alias_to_id
    coarse: dict[str, int] = defaultdict(int)
    subclasses: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    audio_files = 0
    uncompressed = 0
    for info in archive.infolist():
        if info.is_dir() or not _is_audio(info.filename):
            continue
        audio_files += 1
        uncompressed += info.file_size
        parts = Path(info.filename).parts
        if len(parts) <= label_depth:
            continue
        coarse[parts[label_depth]] += 1
        if len(parts) > label_depth + 2:
            subclasses[parts[label_depth]][parts[label_depth + 1]] += 1

    nodes = tuple(
        LabelNode(
            source_label=label,
            canonical_class_id=alias.get(normalize_text(label)),
            files=count,
            subclasses=dict(sorted(subclasses[label].items())),
        )
        for label, count in sorted(coarse.items())
    )
    return nodes, audio_files, uncompressed


def audit_archive(
    source: Source,
    archive_path: Path,
    taxonomy: Taxonomy,
    *,
    label_depth: int | None = 1,
    verify_md5: bool = True,
) -> ArchiveAudit:
    """Audit ``archive_path`` against ``source`` and ``taxonomy``.

    ``label_depth`` is the index of the coarse-label component in each entry
    path, so a ``DATASEC/<class>/<subclass>/file.wav`` layout uses depth 1.
    Pass ``None`` for archives whose labels live in annotation tables rather
    than the directory tree (DataSED): the audit then counts audio and lists
    annotation files without inventing labels from folder names.
    """
    if not archive_path.exists():
        raise FileNotFoundError(archive_path)
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        annotations, documentation = _classify_entries(names)
        if label_depth is None:
            labels: tuple[LabelNode, ...] = ()
            audio_files, uncompressed = _count_audio(archive)
        else:
            labels, audio_files, uncompressed = _collect_labels(
                archive, taxonomy, label_depth=label_depth
            )
    return ArchiveAudit(
        dataset=source.name,
        archive_name=archive_path.name,
        bytes_actual=archive_path.stat().st_size,
        bytes_expected=source.expected_size,
        md5_actual=stream_md5(archive_path) if verify_md5 else None,
        md5_expected=source.expected_md5,
        entries=len(names),
        audio_files=audio_files,
        uncompressed_bytes=uncompressed,
        annotation_files=annotations,
        documentation_files=documentation,
        taxonomy_version=taxonomy.version,
        taxonomy_sha256=taxonomy.checksum,
        labels=labels,
    )


def audit_payload(audit: ArchiveAudit) -> dict:
    """Serialise the audit, including derived verdict fields."""
    return {
        **asdict(audit),
        "size_match": audit.size_match,
        "md5_match": audit.md5_match,
        "coarse_labels": len(audit.labels),
        "subclass_labels": sum(len(node.subclasses) for node in audit.labels),
        "unmapped_labels": list(audit.unmapped_labels),
        "verdict": audit.verdict,
    }


def write_audit(audit: ArchiveAudit, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(audit_payload(audit), ensure_ascii=False, indent=2)
    path.write_text(payload + "\n", encoding="utf-8")
