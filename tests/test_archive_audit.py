import hashlib
import zipfile
from pathlib import Path

import pytest

from ml.dataops.archive_audit import audit_archive, audit_payload
from ml.dataops.sources import Source
from ml.taxonomy import load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = ROOT / "ml" / "configs" / "taxonomy.yaml"


def build_archive(path: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, payload in entries.items():
            archive.writestr(name, payload)


def md5_of(path: Path) -> str:
    return hashlib.md5(path.read_bytes(), usedforsecurity=False).hexdigest()


def make_source(path: Path, md5: str, size: int) -> Source:
    return Source(
        name="datasec",
        record_id=1,
        record_url="https://example.invalid/record",
        api_url="https://example.invalid/api",
        expected_file=path.name,
        expected_size=size,
        expected_md5=md5,
    )


@pytest.fixture
def taxonomy():
    return load_taxonomy(TAXONOMY)


def test_audit_reads_labels_and_subclasses_from_layout(tmp_path: Path, taxonomy) -> None:
    # Arrange
    archive = tmp_path / "DATASEC.zip"
    build_archive(
        archive,
        {
            "DATASEC/Bells/a.wav": b"\0" * 10,
            "DATASEC/Workshop/drill/b.wav": b"\0" * 20,
            "DATASEC/Workshop/saw/c.wav": b"\0" * 30,
        },
    )
    source = make_source(archive, "unused", archive.stat().st_size)

    # Act
    audit = audit_archive(source, archive, taxonomy, verify_md5=False)

    # Assert
    assert audit.audio_files == 3
    assert audit.uncompressed_bytes == 60
    labels = {node.source_label: node for node in audit.labels}
    assert labels["Bells"].canonical_class_id == "bells"
    assert labels["Bells"].subclasses == {}
    assert labels["Workshop"].subclasses == {"drill": 1, "saw": 1}


def test_audit_flags_label_outside_taxonomy(tmp_path: Path, taxonomy) -> None:
    archive = tmp_path / "DATASEC.zip"
    build_archive(archive, {"DATASEC/Helicopter landing pad/a.wav": b"\0"})
    source = make_source(archive, md5_of(archive), archive.stat().st_size)

    audit = audit_archive(source, archive, taxonomy, verify_md5=True)

    assert audit.unmapped_labels == ("Helicopter landing pad",)
    assert audit.verdict == "fail_unmapped_label"


def test_skipping_md5_never_reports_a_full_pass(tmp_path: Path, taxonomy) -> None:
    """A skipped checksum must stay distinguishable from a verified one."""
    archive = tmp_path / "DATASEC.zip"
    build_archive(archive, {"DATASEC/Bells/a.wav": b"\0"})
    source = make_source(archive, md5_of(archive), archive.stat().st_size)

    skipped = audit_archive(source, archive, taxonomy, verify_md5=False)
    verified = audit_archive(source, archive, taxonomy, verify_md5=True)

    assert skipped.md5_actual is None
    assert skipped.md5_match is None
    assert skipped.verdict == "pass_unverified_md5"
    assert verified.md5_match is True
    assert verified.verdict == "pass"


def test_audit_verdict_fails_on_checksum_mismatch(tmp_path: Path, taxonomy) -> None:
    archive = tmp_path / "DATASEC.zip"
    build_archive(archive, {"DATASEC/Bells/a.wav": b"\0"})
    source = make_source(archive, "0" * 32, archive.stat().st_size + 1)

    audit = audit_archive(source, archive, taxonomy, verify_md5=True)

    assert audit.size_match is False
    assert audit.md5_match is False
    assert audit.verdict == "fail_checksum"


def test_audit_separates_annotation_and_documentation_entries(tmp_path: Path, taxonomy) -> None:
    archive = tmp_path / "DataSED.zip"
    build_archive(
        archive,
        {
            "DataSED/SED_wav/S-0001.wav": b"\0",
            "DataSED/SED_ground_truth/Polyphonic_sound_detection.csv": b"a,b\n",
            "DataSED/LICENSE": b"CC BY-NC-SA 4.0\n",
            "DataSED/README.txt": b"notes\n",
        },
    )
    source = make_source(archive, "unused", archive.stat().st_size)

    audit = audit_archive(source, archive, taxonomy, verify_md5=False)

    assert audit.annotation_files == (
        "DataSED/SED_ground_truth/Polyphonic_sound_detection.csv",
    )
    assert audit.documentation_files == ("DataSED/LICENSE", "DataSED/README.txt")


def test_audit_payload_is_json_serialisable_and_carries_taxonomy_hash(
    tmp_path: Path, taxonomy
) -> None:
    archive = tmp_path / "DATASEC.zip"
    build_archive(archive, {"DATASEC/Bells/a.wav": b"\0"})
    source = make_source(archive, "unused", archive.stat().st_size)

    payload = audit_payload(audit_archive(source, archive, taxonomy, verify_md5=False))

    assert payload["taxonomy_sha256"] == taxonomy.checksum
    assert payload["taxonomy_version"] == taxonomy.version
    assert payload["coarse_labels"] == 1
    assert payload["subclass_labels"] == 0


def test_annotation_labelled_archive_skips_folder_derived_labels(
    tmp_path: Path, taxonomy
) -> None:
    """DataSED keeps labels in CSV, so folder names must not become labels."""
    archive = tmp_path / "DataSED.zip"
    build_archive(
        archive,
        {
            "DataSED/SED_wav/S-0001.wav": b"\0" * 4,
            "DataSED/SED_ground_truth/Polyphonic_sound_detection.csv": b"a,b\n",
        },
    )
    source = make_source(archive, md5_of(archive), archive.stat().st_size)

    audit = audit_archive(source, archive, taxonomy, label_depth=None, verify_md5=True)

    assert audit.labels == ()
    assert audit.unmapped_labels == ()
    assert audit.audio_files == 1
    assert audit.uncompressed_bytes == 4
    assert audit.verdict == "pass"
