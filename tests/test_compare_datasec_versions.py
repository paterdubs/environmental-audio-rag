import hashlib
import io
import json
import wave
import zipfile

import pandas as pd
import pytest

from ml.taxonomy import Taxonomy, TaxonomyClass
from scripts.compare_datasec_versions import (
    EXPECTED_MD5,
    compare,
    normalize_member,
    scan_archive,
    source_manifest,
    verify_inventory_bytes,
)


def wav_bytes(frames=800):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(8000)
        audio.writeframes(b"\0\0" * frames)
    return buffer.getvalue()


@pytest.fixture
def archive_fixture(tmp_path):
    taxonomy = Taxonomy("1", (TaxonomyClass("bells", "Bells", (), (), True),), "a" * 64)
    content = wav_bytes()
    rows = []
    archive = tmp_path / "v4.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zipped:
        for i in range(6):
            path = f"DATASEC/Bells/{i}.wav"
            raw = content if i < 5 else wav_bytes(1600)
            out = tmp_path / "extracted" / path
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(raw)
            rows.append({"file_id": f"datasec:{path}", "relative_path": path,
                         "sha256": hashlib.sha256(raw).hexdigest()})
            if i < 5:
                zipped.writestr("prefix/" + path, raw)
        zipped.writestr("readme.txt", "not an audio member")
    return archive, pd.DataFrame(rows), tmp_path / "extracted", taxonomy


def test_hash_byte_verification_scan_and_no_extraction(archive_fixture, tmp_path):
    archive, inventory, extracted, taxonomy = archive_fixture
    before = set(tmp_path.rglob("*"))
    verified = verify_inventory_bytes(inventory, extracted)
    assert len(verified) == 5
    members = scan_archive(archive, inventory, taxonomy)
    assert len(members) == 5
    assert members["in_v3"].all()
    assert members["duration_s"].tolist() == pytest.approx([0.1] * 5)
    assert set(members["sha256"]) == {hashlib.sha256(wav_bytes()).hexdigest()}
    assert set(tmp_path.rglob("*")) == before
    (extracted / inventory.iloc[0]["relative_path"]).write_bytes(b"tampered")
    with pytest.raises(ValueError, match="không khớp byte"):
        verify_inventory_bytes(inventory, extracted)


def test_normalization_and_unsafe_paths():
    assert normalize_member("prefix\\DATASEC\\Bells\\1.wav") == "DATASEC/Bells/1.wav"
    assert normalize_member("DATASEC/DATASEC/Bells/1.wav") == "DATASEC/Bells/1.wav"
    with pytest.raises(ValueError, match="Path chứa"):
        normalize_member("DATASEC/../Bells/1.wav")
    with pytest.raises(ValueError, match="Không có DATASEC"):
        normalize_member("unknown/Bells/1.wav")


def versions():
    old = pd.DataFrame({"file_id": ["a", "b", "c"], "relative_path": ["a", "b", "c"],
                        "sha256": ["hash_a", "hash_b", "hash_c"],
                        "class_id": ["music", "music", "bells"], "duration_s": [1., 2., 3.]})
    exclusions = pd.DataFrame({"file_id": ["b"]})
    splits = pd.DataFrame({"file_id": ["a", "c"], "split": ["train", "validation"]})
    return old, exclusions, splits


def test_subset_removed_intersections_and_hours():
    old, exclusions, splits = versions()
    result = compare(old, old.iloc[[0]], exclusions, splits)
    assert result["v4_subset_v3_by_hash"]
    assert result["safe_to_filter_without_new_features"]
    assert result["v3"]["hours"] == pytest.approx(6 / 3600)
    assert result["removed_paths"] == ["b", "c"]
    intersections = result["removed_by_hash_intersections"]
    assert intersections["exclusions"]["file_ids"] == ["b"]
    assert intersections["splits"]["validation"]["file_ids"] == ["c"]
    assert intersections["splits"]["train"]["count"] == 0


def test_hash_subset_does_not_hide_renaming_or_changed_path():
    old, exclusions, splits = versions()
    new = old.iloc[[0, 1]].copy()
    new.loc[new.index[0], "relative_path"] = "renamed"
    new.loc[new.index[1], "sha256"] = "hash_c"  # known hash, but changed content at path b
    result = compare(old, new, exclusions, splits)
    assert result["v4_subset_v3_by_hash"]
    assert not result["safe_to_filter_without_new_features"]
    assert result["changed_paths"] == [{"relative_path": "b", "v3_sha256": "hash_b",
                                         "v4_sha256": "hash_c"}]
    assert result["added_paths"] == ["renamed"]
    assert "DỪNG" in result["proposal"]


def test_new_hash_blocks_reuse():
    old, exclusions, splits = versions()
    new = old.iloc[[0]].copy()
    new["sha256"] = "new_hash"
    result = compare(old, new, exclusions, splits)
    assert not result["v4_subset_v3_by_hash"]
    assert len(result["added_v4_by_hash"]) == 1


def test_source_license_must_come_from_record(tmp_path):
    source = {"id": 23097290, "doi": "10.5281/zenodo.23097290", "metadata": {
        "publication_date": "2026-10-02", "license": {"id": "cc-by-nc-sa-4.0"}},
        "files": [{"key": "DATASEC.zip", "checksum": f"md5:{EXPECTED_MD5}", "size": 123}]}
    path = tmp_path / "record.json"
    path.write_text(json.dumps(source))
    assert source_manifest(path)["license"] == "cc-by-nc-sa-4.0"
    del source["metadata"]["license"]
    path.write_text(json.dumps(source))
    with pytest.raises(ValueError, match="thiếu license"):
        source_manifest(path)


def test_duplicate_normalized_member_is_rejected(archive_fixture):
    archive, inventory, _, taxonomy = archive_fixture
    with zipfile.ZipFile(archive, "a") as zipped:
        zipped.writestr("different-prefix/DATASEC/Bells/0.wav", wav_bytes())
    with pytest.raises(ValueError, match="trùng đường dẫn"):
        scan_archive(archive, inventory, taxonomy)


def test_bad_archive_md5_stops_before_reading_inventory(tmp_path, monkeypatch):
    import scripts.compare_datasec_versions as report

    archive = tmp_path / "bad.zip"
    archive.write_bytes(b"bad")
    monkeypatch.setattr(report, "source_manifest", lambda _: {"archive_bytes": 3})
    monkeypatch.setattr("sys.argv", ["compare", "--archive", str(archive),
                                    "--v3-extracted", str(tmp_path),
                                    "--source-record", str(tmp_path / "source.json")])
    with pytest.raises(SystemExit, match="MD5/size không khớp"):
        report.main()
