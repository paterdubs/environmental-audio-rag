"""Upload validation shared by `api` (the boundary) and `inference` (defence in depth)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import soundfile
from fastapi import UploadFile

MAX_BYTES = 50 * 1024 * 1024  # ADR-0029 §6
MAX_DURATION_S = 600.0
ALLOWED_SUFFIXES = (".wav", ".flac", ".ogg", ".mp3")
CHUNK = 1024 * 1024


class AudioRejected(ValueError):
    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status, self.code = status, code


@dataclass(frozen=True)
class StoredAudio:
    path: Path
    sha256: str
    size: int
    duration_s: float
    sample_rate: int
    channels: int


def suffix_of(filename: str | None) -> str:
    suffix = Path(filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise AudioRejected(415, "unsupported_format",
                            f"định dạng {suffix or '(không có)'} không hỗ trợ; "
                            f"chấp nhận {', '.join(ALLOWED_SUFFIXES)}")
    return suffix


async def save_upload(upload: UploadFile, destination: Path) -> StoredAudio:
    """Stream to disk under the size cap, hash on the way, then check it decodes."""
    suffix_of(upload.filename)
    digest, size = hashlib.sha256(), 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as handle:
        while chunk := await upload.read(CHUNK):
            size += len(chunk)
            if size > MAX_BYTES:
                handle.close()
                destination.unlink(missing_ok=True)
                raise AudioRejected(413, "too_large", f"file vượt {MAX_BYTES // 2**20} MB")
            digest.update(chunk)
            handle.write(chunk)
    return inspect(destination, digest.hexdigest(), size)


def inspect(path: Path, sha256: str, size: int) -> StoredAudio:
    try:
        info = soundfile.info(str(path))
    except Exception as exc:  # noqa: BLE001 — libsndfile raises several types for bad input
        path.unlink(missing_ok=True)
        raise AudioRejected(422, "undecodable", "không đọc được audio") from exc
    if info.duration <= 0 or info.duration > MAX_DURATION_S:
        path.unlink(missing_ok=True)
        raise AudioRejected(422, "bad_duration",
                            f"thời lượng {info.duration:.1f} s ngoài (0, {MAX_DURATION_S:.0f}] s")
    return StoredAudio(path, sha256, size, float(info.duration), int(info.samplerate),
                       int(info.channels))
