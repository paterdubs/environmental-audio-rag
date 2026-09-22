from __future__ import annotations

import argparse
import json
from pathlib import Path

from ml.dataops.sources import (
    copy_reference_files,
    download_parallel,
    download_with_resume,
    extract_zip,
    fetch_metadata,
    load_sources,
    requests_session,
    resolve_file,
    stream_md5,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "ml" / "configs" / "sources.yaml"


def selected_sources(names: list[str]):
    sources = load_sources(CONFIG)
    unknown = set(names) - set(sources)
    if unknown:
        raise SystemExit(f"Unknown source(s): {sorted(unknown)}")
    return [sources[name] for name in names]


def command_metadata(names: list[str]) -> None:
    session = requests_session()
    for source in selected_sources(names):
        metadata = fetch_metadata(source, ROOT / "data" / "reference", session)
        item = resolve_file(source, metadata)
        print(
            json.dumps(
                {
                    "source": source.name,
                    "file": item["key"],
                    "size": item["size"],
                    "checksum": item["checksum"],
                }
            )
        )


def command_download(names: list[str], workers: int) -> None:
    session = requests_session()
    for source in selected_sources(names):
        metadata = fetch_metadata(source, ROOT / "data" / "reference", session)
        item = resolve_file(source, metadata)
        archive = ROOT / "data" / "raw" / source.name / "archives" / source.expected_file
        if workers > 1:
            download_parallel(item["links"]["self"], archive, source.expected_size, workers)
        else:
            download_with_resume(item["links"]["self"], archive, source.expected_size, session)
        actual = stream_md5(archive)
        if actual != source.expected_md5:
            raise RuntimeError(f"{source.name}: md5 mismatch {actual} != {source.expected_md5}")
        print(f"verified {source.name}: {archive} md5={actual}")


def command_extract(names: list[str]) -> None:
    for source in selected_sources(names):
        archive = ROOT / "data" / "raw" / source.name / "archives" / source.expected_file
        if not archive.exists():
            raise FileNotFoundError(archive)
        if stream_md5(archive) != source.expected_md5:
            raise RuntimeError(f"{source.name}: archive checksum failed")
        destination = ROOT / "data" / "raw" / source.name / "extracted"
        extract_zip(archive, destination)
        copied = copy_reference_files(destination, ROOT / "data" / "reference", source.name)
        print(f"extracted {source.name}: {destination}; references={copied}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["metadata", "download", "extract"])
    parser.add_argument("sources", nargs="*", default=["datasec", "datased"])
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    if args.action == "download":
        command_download(args.sources, args.workers)
    else:
        {"metadata": command_metadata, "extract": command_extract}[args.action](args.sources)


if __name__ == "__main__":
    main()
