from __future__ import annotations

import hashlib
import json
import os
import shutil
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
import yaml
from tqdm import tqdm


@dataclass(frozen=True)
class Source:
    name: str
    record_id: int
    record_url: str
    api_url: str
    expected_file: str
    expected_size: int
    expected_md5: str


def load_sources(path: Path) -> dict[str, Source]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))["sources"]
    return {name: Source(name=name, **values) for name, values in raw.items()}


def stream_md5(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_metadata(
    source: Source, reference_dir: Path, session: requests.Session
) -> dict[str, Any]:
    response = session.get(source.api_url, timeout=60)
    response.raise_for_status()
    metadata = response.json()
    reference_dir.mkdir(parents=True, exist_ok=True)
    target = reference_dir / f"zenodo_{source.name}_{source.record_id}.json"
    target.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata


def resolve_file(source: Source, metadata: dict[str, Any]) -> dict[str, Any]:
    matches = [item for item in metadata["files"] if item["key"] == source.expected_file]
    if len(matches) != 1:
        raise RuntimeError(f"{source.name}: expected exactly one file {source.expected_file!r}")
    item = matches[0]
    actual_md5 = str(item["checksum"]).removeprefix("md5:")
    if int(item["size"]) != source.expected_size or actual_md5 != source.expected_md5:
        raise RuntimeError(
            f"{source.name}: Zenodo metadata changed; expected size/md5 "
            f"{source.expected_size}/{source.expected_md5}, got {item['size']}/{actual_md5}"
        )
    return item


def download_with_resume(
    url: str,
    destination: Path,
    expected_size: int,
    session: requests.Session,
    chunk_size: int = 8 * 1024 * 1024,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    current = destination.stat().st_size if destination.exists() else 0
    if current > expected_size:
        raise RuntimeError(f"Partial file is larger than expected: {destination}")
    if current == expected_size:
        return

    headers = {"Range": f"bytes={current}-"} if current else {}
    response = session.get(url, headers=headers, stream=True, timeout=(30, 300))
    response.raise_for_status()
    if current and response.status_code != 206:
        current = 0
        mode = "wb"
    else:
        mode = "ab" if current else "wb"

    with destination.open(mode) as handle, tqdm(
        total=expected_size,
        initial=current,
        unit="B",
        unit_scale=True,
        desc=destination.name,
    ) as progress:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                handle.write(chunk)
                progress.update(len(chunk))

    if destination.stat().st_size != expected_size:
        raise RuntimeError(
            f"Incomplete download {destination}: {destination.stat().st_size} != {expected_size}"
        )


def _range_worker(
    url: str,
    part_path: Path,
    start: int,
    end: int,
    user_agent: str,
    progress: tqdm,
    lock: threading.Lock,
) -> None:
    expected = end - start + 1
    current = part_path.stat().st_size if part_path.exists() else 0
    if current > expected:
        raise RuntimeError(f"Oversized range part: {part_path}")
    for attempt in range(1, 6):
        if current == expected:
            return
        headers = {
            "Range": f"bytes={start + current}-{end}",
            "User-Agent": user_agent,
        }
        try:
            with requests.get(url, headers=headers, stream=True, timeout=(30, 90)) as response:
                response.raise_for_status()
                if response.status_code != 206:
                    raise RuntimeError(
                        f"Server ignored range for {part_path}: {response.status_code}"
                    )
                with part_path.open("ab") as handle:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if not chunk:
                            continue
                        handle.write(chunk)
                        current += len(chunk)
                        with lock:
                            progress.update(len(chunk))
        except (requests.RequestException, OSError) as error:
            if attempt == 5:
                raise RuntimeError(f"Range download failed after retries: {part_path}") from error
        current = part_path.stat().st_size if part_path.exists() else 0
    if current != expected:
        raise RuntimeError(f"Incomplete range {part_path}: {current} != {expected}")


def download_parallel(
    url: str,
    destination: Path,
    expected_size: int,
    workers: int = 8,
    user_agent: str = "environmental-audio-rag/0.1 academic-research",
) -> None:
    """Resume a partial prefix, then fetch remaining byte ranges concurrently."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size == expected_size:
        return
    prefix_size = destination.stat().st_size if destination.exists() else 0
    if prefix_size > expected_size:
        raise RuntimeError(f"Partial file is larger than expected: {destination}")

    parts_dir = destination.with_name(destination.name + ".parts")
    plan_path = parts_dir / "plan.json"
    parts_dir.mkdir(parents=True, exist_ok=True)
    if plan_path.exists():
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        if plan["expected_size"] != expected_size or plan["prefix_size"] != prefix_size:
            raise RuntimeError(f"Existing range plan conflicts with destination: {plan_path}")
        ranges = [tuple(values) for values in plan["ranges"]]
    else:
        remaining = expected_size - prefix_size
        step = max(1, (remaining + workers - 1) // workers)
        ranges = [
            (start, min(start + step - 1, expected_size - 1))
            for start in range(prefix_size, expected_size, step)
        ]
        plan_path.write_text(
            json.dumps(
                {
                    "expected_size": expected_size,
                    "prefix_size": prefix_size,
                    "ranges": ranges,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    existing = sum(
        min((parts_dir / f"part_{index:03d}.bin").stat().st_size, end - start + 1)
        if (parts_dir / f"part_{index:03d}.bin").exists()
        else 0
        for index, (start, end) in enumerate(ranges)
    )
    lock = threading.Lock()
    with tqdm(
        total=expected_size,
        initial=prefix_size + existing,
        unit="B",
        unit_scale=True,
        desc=destination.name,
    ) as progress:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(
                    _range_worker,
                    url,
                    parts_dir / f"part_{index:03d}.bin",
                    start,
                    end,
                    user_agent,
                    progress,
                    lock,
                ): index
                for index, (start, end) in enumerate(ranges)
            }
            for future in as_completed(futures):
                future.result()

    assembled = destination.with_name(destination.name + ".assembling")
    with assembled.open("wb") as output:
        if prefix_size:
            with destination.open("rb") as prefix:
                shutil.copyfileobj(prefix, output, length=8 * 1024 * 1024)
        for index, (start, end) in enumerate(ranges):
            part_path = parts_dir / f"part_{index:03d}.bin"
            if part_path.stat().st_size != end - start + 1:
                raise RuntimeError(f"Range size mismatch: {part_path}")
            with part_path.open("rb") as part:
                shutil.copyfileobj(part, output, length=8 * 1024 * 1024)
    if assembled.stat().st_size != expected_size:
        raise RuntimeError(f"Assembled size mismatch: {assembled}")
    os.replace(assembled, destination)
    shutil.rmtree(parts_dir)


def extract_zip(archive: Path, destination: Path) -> None:
    marker = destination / ".extracted.json"
    if marker.exists():
        state = json.loads(marker.read_text(encoding="utf-8"))
        if state.get("archive_md5") == stream_md5(archive):
            return
        raise RuntimeError(f"Extraction marker does not match archive: {destination}")
    if destination.exists() and any(destination.iterdir()):
        raise RuntimeError(f"Refusing to extract into non-empty directory: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zipped:
        bad = zipped.testzip()
        if bad is not None:
            raise RuntimeError(f"Corrupt member in {archive}: {bad}")
        zipped.extractall(destination)
    marker.write_text(
        json.dumps({"archive": archive.name, "archive_md5": stream_md5(archive)}, indent=2),
        encoding="utf-8",
    )


def copy_reference_files(extracted_root: Path, reference_dir: Path, source_name: str) -> list[str]:
    reference_dir.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for path in extracted_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".txt", ".md", ".pdf"}:
            continue
        if path.stat().st_size > 10 * 1024 * 1024:
            continue
        name = f"{source_name}__{path.name}"
        shutil.copy2(path, reference_dir / name)
        copied.append(name)
    return copied


def requests_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "environmental-audio-rag/0.1 academic-research"})
    return session
