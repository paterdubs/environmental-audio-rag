"""Kiểm DataSEC v4 bằng byte hash trong zip, tránh giải nén hoặc đổi dữ liệu v3.

Chỉ đề xuất tái dùng feature khi danh sách v4 giữ nguyên path và hash của v3.
Manifest nguồn lấy license từ Zenodo record, không suy license từ archive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import soundfile as sf

from ml.dataops.datasec_labels import path_labels
from ml.provenance import git_state
from ml.taxonomy import Taxonomy, load_taxonomy

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MD5 = "11e0ae0098ecf3d982ab5f7375c56844"
RECORD_ID = 23097290


def digest_file(path: Path, algorithm: str = "sha256") -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def normalize_member(name: str) -> str:
    """Đổi slash, bỏ tiền tố trước DATASEC cuối cùng; cấm '..', giữ nguyên case còn lại."""
    parts = PurePosixPath(name.replace("\\", "/")).parts
    if ".." in parts:
        raise ValueError(f"Path chứa '..': {name}")
    roots = [i for i, part in enumerate(parts) if part.casefold() == "datasec"]
    if not roots or len(parts) <= roots[-1] + 2:
        raise ValueError(f"Không có DATASEC/<lớp>/<file>: {name}")
    return str(PurePosixPath("DATASEC", *parts[roots[-1] + 1:]))


def source_manifest(path: Path) -> dict:
    record = json.loads(path.read_text(encoding="utf-8-sig"))
    metadata = record["metadata"]
    file = next(item for item in record["files"] if item["key"] == "DATASEC.zip")
    if int(record["id"]) != RECORD_ID or file["checksum"] != f"md5:{EXPECTED_MD5}":
        raise ValueError("Zenodo record hoặc checksum không khớp đặc tả XO-3")
    license_id = metadata.get("license", {}).get("id")
    if not license_id:
        raise ValueError("Zenodo record thiếu license; không xử lý archive")
    return {"record_id": RECORD_ID, "version": "v4", "doi": record["doi"],
            "publication_date": metadata["publication_date"], "license": license_id,
            "license_source": f"https://zenodo.org/api/records/{RECORD_ID}",
            "archive_md5": EXPECTED_MD5, "archive_bytes": int(file["size"]),
            "record_metadata_sha256": digest_file(path)}


def verify_inventory_bytes(inventory: pd.DataFrame, extracted: Path) -> list[dict]:
    indices = np.linspace(0, len(inventory) - 1, min(5, len(inventory)), dtype=int)
    checked = []
    for index in indices:
        row = inventory.iloc[index]
        path = extracted / row["relative_path"]
        actual = digest_file(path)
        if actual != row["sha256"]:
            raise ValueError(f"Inventory v3 không khớp byte SHA-256: {path}")
        checked.append({"file_id": row["file_id"], "path": str(path), "sha256": actual})
    if not checked:
        raise ValueError("Inventory v3 rỗng")
    return checked


def scan_archive(archive: Path, inventory: pd.DataFrame, taxonomy: Taxonomy) -> pd.DataFrame:
    rows = []
    known = set(inventory["sha256"])
    seen = set()
    with zipfile.ZipFile(archive) as zipped:
        for member in zipped.infolist():
            if member.is_dir() or not member.filename.lower().endswith(".wav"):
                continue
            path = normalize_member(member.filename)
            if path in seen:
                raise ValueError(f"Member trùng đường dẫn sau chuẩn hóa: {path}")
            seen.add(path)
            with zipped.open(member) as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            with zipped.open(member) as stream:
                info = sf.info(stream)
            class_id, _ = path_labels(path, taxonomy)
            rows.append({"file_id": f"datasec:{path}", "relative_path": path,
                         "sha256": digest, "in_v3": digest in known,
                         "class_id": class_id, "duration_s": info.frames / info.samplerate})
    if not rows:
        raise ValueError("Archive không có WAV")
    return pd.DataFrame(rows)


def class_totals(frame: pd.DataFrame) -> dict:
    return {c: {"files": len(group), "hours": float(group["duration_s"].sum() / 3600)}
            for c, group in frame.groupby("class_id")}


def intersections(removed: pd.DataFrame, exclusions: pd.DataFrame, splits: pd.DataFrame) -> dict:
    ids = set(removed["file_id"])
    excluded = sorted(ids & set(exclusions["file_id"]))
    by_split = {s: sorted(ids & set(group["file_id"])) for s, group in splits.groupby("split")}
    return {"exclusions": {"count": len(excluded), "file_ids": excluded},
            "splits": {s: {"count": len(values), "file_ids": values}
                       for s, values in by_split.items()},
            "not_in_split": sorted(ids - set(splits["file_id"]))}


def compare(v3: pd.DataFrame, v4: pd.DataFrame, exclusions: pd.DataFrame,
            splits: pd.DataFrame) -> dict:
    old = v3.set_index("relative_path")["sha256"].to_dict()
    new = v4.set_index("relative_path")["sha256"].to_dict()
    removed_paths = sorted(old.keys() - new.keys())
    added_paths = sorted(new.keys() - old.keys())
    changed = [{"relative_path": p, "v3_sha256": old[p], "v4_sha256": new[p]}
               for p in sorted(old.keys() & new.keys()) if old[p] != new[p]]
    old_hashes, new_hashes = set(old.values()), set(new.values())
    removed_hash_rows = v3[~v3["sha256"].isin(new_hashes)]
    added_hash_rows = v4[~v4["sha256"].isin(old_hashes)]
    subset = new_hashes <= old_hashes
    safe_filter = subset and not added_paths and not changed
    return {
        "v3": {"files": len(v3), "hours": float(v3["duration_s"].sum() / 3600),
               "by_class": class_totals(v3)},
        "v4": {"files": len(v4), "hours": float(v4["duration_s"].sum() / 3600),
               "by_class": class_totals(v4)},
        "removed_paths": removed_paths, "added_paths": added_paths, "changed_paths": changed,
        "removed_v3_by_hash": removed_hash_rows[["file_id", "relative_path", "sha256"]]
        .to_dict(orient="records"),
        "added_v4_by_hash": added_hash_rows[["file_id", "relative_path", "sha256"]]
        .to_dict(orient="records"),
        "v4_subset_v3_by_hash": subset, "safe_to_filter_without_new_features": safe_filter,
        "removed_by_hash_intersections": intersections(removed_hash_rows, exclusions, splits),
        "removed_by_path_intersections": intersections(
            v3[v3["relative_path"].isin(removed_paths)], exclusions, splits),
        "proposal": ("Có thể lọc danh sách v3 theo member v4, giữ exclusion D3; "
                     "Claude quyết cách tích hợp, script không đổi split/inventory."
                     if safe_filter else "DỪNG đề xuất lọc: có path mới/hash khác hoặc hash mới; "
                     "Claude quyết kiểm D3/D4 phần mới trước khi dùng."),
    }


def render(result: dict) -> str:
    lines = ["# DataSEC v4 so với v3", "", "Sinh bởi `scripts.compare_datasec_versions`.", "",
             "Đã kiểm MD5 toàn archive trước khi đọc WAV; SHA-256 từng member đọc stream "
             "trong zip, không giải nén. 5 mẫu byte v3 được đối chiếu inventory trước scan.", "",
             "Chuẩn hóa: đổi backslash thành slash, bỏ tiền tố trước DATASEC cuối cùng, "
             "chuẩn root thành DATASEC, giữ case phần còn lại, cấm '..' và path trùng. "
             "`in_v3` là thuộc tập hash v3, không phải cùng path. WAV duration từ header "
             "qua soundfile; hash gồm toàn bộ byte file. Không sửa inventory/split/exclusion.", "",
             f"Nguồn: [Zenodo record v4](https://zenodo.org/records/{RECORD_ID}), "
             f"DOI {result['source']['doi']}, license `{result['source']['license']}` "
             "lấy từ metadata record, không lấy từ zip.", "",
             f"MD5 archive: `{result['archive_md5']}`.", "",
             "| Lớp | v3 file | v3 giờ | v4 file | v4 giờ |", "|---|---:|---:|---:|---:|"]
    for c in sorted(result["v3"]["by_class"].keys() | result["v4"]["by_class"].keys()):
        a = result["v3"]["by_class"].get(c, {"files": 0, "hours": 0})
        b = result["v4"]["by_class"].get(c, {"files": 0, "hours": 0})
        lines.append(f"| {c} | {a['files']} | {a['hours']:.8f} | {b['files']} | {b['hours']:.8f} |")
    lines += ["", f"Tổng v3: {result['v3']['files']} file, {result['v3']['hours']:.8f} giờ; "
              f"v4: {result['v4']['files']} file, {result['v4']['hours']:.8f} giờ.", "",
              f"Path bị bỏ/thêm/cùng path khác hash: {len(result['removed_paths'])}/"
              f"{len(result['added_paths'])}/{len(result['changed_paths'])}.", "",
              f"File v3 mất hash ở v4: {len(result['removed_v3_by_hash'])}; "
              f"file v4 có hash mới: {len(result['added_v4_by_hash'])}.", "",
              f"v4 ⊆ v3 theo hash: **{result['v4_subset_v3_by_hash']}**.", "",
              "## Giao file v3 bị bỏ theo hash với exclusion/split", ""]
    intersect = result["removed_by_hash_intersections"]
    lines += [f"Exclusions: {intersect['exclusions']['count']} file.", ""]
    lines += [f"- {s}: {row['count']} file." for s, row in intersect["splits"].items()]
    lines += ["", "## Đề xuất", "", result["proposal"], "",
              "Danh sách path/hash bị bỏ/thêm/thay đổi, giao theo path, SHA-256 bảng nguồn, "
              "5 mẫu v3 và provenance đầy đủ ở JSON; member ở `datasec_v4_members.csv`."]
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--v3-extracted", type=Path, required=True)
    parser.add_argument("--source-record", type=Path, required=True)
    parser.add_argument("--date", default=datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
                        .strftime("%Y%m%d"))
    args = parser.parse_args()
    source = source_manifest(args.source_record)  # manifest nguồn đã lưu trước xử lý
    actual_md5 = digest_file(args.archive, "md5")
    if actual_md5 != EXPECTED_MD5 or args.archive.stat().st_size != source["archive_bytes"]:
        raise SystemExit(f"DỪNG: archive MD5/size không khớp: {actual_md5}")
    inventory_path = ROOT / "data/manifests/datasec_inventory.csv"
    exclusions_path = ROOT / "data/manifests/exclusions.csv"
    splits_path = ROOT / "data/splits/datasec_classification.csv"
    taxonomy_path = ROOT / "ml/configs/taxonomy.yaml"
    taxonomy = load_taxonomy(taxonomy_path)
    inventory = pd.read_csv(inventory_path)
    verified = verify_inventory_bytes(inventory, args.v3_extracted)
    inventory["class_id"] = [path_labels(p, taxonomy)[0] for p in inventory["relative_path"]]
    members = scan_archive(args.archive, inventory, taxonomy)
    result = {"git": git_state(ROOT), "source": source, "archive_md5": actual_md5,
              "v3_byte_hash_samples": verified,
              "inputs": {str(p.relative_to(ROOT)): digest_file(p) for p in
                         (inventory_path, exclusions_path, splits_path, taxonomy_path)},
              **compare(inventory, members, pd.read_csv(exclusions_path), pd.read_csv(splits_path))}
    member_path = ROOT / "data/manifests/datasec_v4_members.csv"
    members[["file_id", "relative_path", "sha256", "in_v3"]].to_csv(
        member_path, index=False, lineterminator="\n")
    result["members_sha256"] = digest_file(member_path)
    out = ROOT / f"docs/measurements/datasec_v4_diff_{args.date}"
    out.with_suffix(".json").write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                        encoding="utf-8")
    out.with_suffix(".md").write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
