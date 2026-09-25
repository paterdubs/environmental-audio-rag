"""Ingest and recording routes (SYSTEM §4.4). Torch-free: inference is reached over HTTP."""

from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import Any

import numpy as np
from fastapi import APIRouter, File, Query, Request, UploadFile
from fastapi.responses import FileResponse

from ml.retrieval import recordings as repo
from services.api.app.inference import InferenceUnavailable
from services.common.audio import AudioRejected, save_upload, suffix_of
from services.common.envelope import fail, ok

router = APIRouter(prefix="/api/v1")
ROOT = Path(__file__).resolve().parents[3]
DATASED_AUDIO = ROOT / "data/raw/datased/extracted"


def _versions(events: list[dict[str, Any]]) -> dict[str, Any]:
    return {"model_versions": sorted({str(e["model_version"]) for e in events
                                      if e["model_version"]}),
            "taxonomy_versions": sorted({str(e["taxonomy_version"]) for e in events})}


async def _db(request: Request, function, *args):
    """Run one repository call on a fresh connection in a worker thread."""
    def run():
        conn = request.app.state.connect()
        try:
            return function(conn, *args)
        finally:
            conn.close()
    return await asyncio.to_thread(run)


def _store_analysis(conn, row: dict[str, Any], analysis: dict[str, Any]) -> None:
    try:
        repo.insert_analysis(conn, row, analysis, np.asarray(analysis["embedding"], np.float32),
                             analysis["embedding_version"])
        conn.commit()
    except Exception:
        conn.rollback()
        raise


@router.post("/audio/upload")
async def upload(request: Request, file: UploadFile = File(...)):  # noqa: B008
    settings = request.app.state.settings
    try:
        uid = uuid.uuid4()
        destination = settings.upload_dir / f"{uid}{suffix_of(file.filename)}"
        stored = await save_upload(file, destination)
    except AudioRejected as exc:
        return fail(exc.status, exc.code, str(exc))
    existing = await _db(request, repo.find_by_sha, stored.sha256)
    if existing:
        destination.unlink(missing_ok=True)
        return ok({"recording_id": existing}, meta={"duplicate": True})
    recording_id = f"upload:{uid}"
    try:
        analysis = await request.app.state.inference.analyze(recording_id, destination)
    except InferenceUnavailable as exc:
        destination.unlink(missing_ok=True)
        return fail(503, "inference_unavailable", str(exc))
    if analysis["audio"]["sha256"] != stored.sha256:
        destination.unlink(missing_ok=True)
        return fail(500, "integrity", "inference nhận nội dung khác file đã lưu")
    row = {"recording_id": recording_id, "source_dataset": "upload", "source_id": str(uid),
           "duration_s": stored.duration_s, "sample_rate": stored.sample_rate,
           "channels": stored.channels, "sha256": stored.sha256, "split": None,
           "audio_path": destination.relative_to(ROOT).as_posix()
           if destination.is_relative_to(ROOT) else str(destination)}
    try:
        await _db(request, _store_analysis, row, analysis)
    except Exception:
        destination.unlink(missing_ok=True)  # never keep audio that has no recording row
        raise
    return ok({"recording_id": recording_id, "timeline": analysis["timeline"],
               "captions": analysis["captions"]}, meta={"duplicate": False}, status=201)


@router.get("/recordings")
async def list_recordings(request: Request, corpus: str = "upload", class_id: str | None = None,
                          page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    if corpus not in ("upload", "validation", "test"):
        return fail(422, "bad_corpus", "corpus phải là upload, validation hoặc test")
    if class_id is not None and class_id not in request.app.state.taxonomy.polyphonic_class_ids:
        return fail(422, "unknown_class", f"class_id {class_id!r} không thuộc 21 lớp SED")
    rows, total = await _db(request, repo.list_recordings, corpus, class_id, limit,
                            (page - 1) * limit)
    return ok(jsonable(rows), meta={"total": total, "page": page, "limit": limit})


async def _recording_or_404(request: Request, recording_id: str):
    recording = await _db(request, repo.get_recording, recording_id)
    return recording, (None if recording else
                       fail(404, "not_found", f"không có recording {recording_id}"))


@router.get("/recordings/{recording_id}")
async def get_recording(request: Request, recording_id: str):
    recording, missing = await _recording_or_404(request, recording_id)
    if missing:
        return missing
    events = await _db(request, repo.recording_events, recording_id)
    captions = await _db(request, repo.recording_captions, recording_id)
    return ok(jsonable({"recording": recording, "events": events, "captions": captions,
                        **_versions(events)}))


@router.get("/recordings/{recording_id}/timeline")
async def timeline(request: Request, recording_id: str):
    recording, missing = await _recording_or_404(request, recording_id)
    if missing:
        return missing
    events = await _db(request, repo.recording_events, recording_id)
    return ok(jsonable({"recording_id": recording_id, "duration_s": recording["duration_s"],
                        "events": events, **_versions(events)}))


@router.get("/recordings/{recording_id}/caption")
async def caption(request: Request, recording_id: str):
    _, missing = await _recording_or_404(request, recording_id)
    if missing:
        return missing
    return ok(jsonable(await _db(request, repo.recording_captions, recording_id)))


@router.get("/recordings/{recording_id}/audio")
async def audio(request: Request, recording_id: str):
    recording, missing = await _recording_or_404(request, recording_id)
    if missing:
        return missing
    path = audio_file(recording, request.app.state.settings.upload_dir)
    if path is None:
        return fail(404, "no_audio", "không tìm thấy file audio")
    return FileResponse(path)


def audio_file(recording: dict[str, Any], upload_dir: Path) -> Path | None:
    """Stored audio of a recording, only if it resolves inside that source's own root."""
    if not recording["audio_path"]:
        return None
    if recording["source_dataset"] == "upload":
        root, stored = upload_dir, Path(recording["audio_path"])
        path = stored if stored.is_absolute() else ROOT / stored
    elif recording["source_dataset"] == "datased":
        root, path = DATASED_AUDIO, DATASED_AUDIO / recording["audio_path"]
    else:
        return None
    path = path.resolve()
    return path if path.is_relative_to(root.resolve()) and path.is_file() else None


def jsonable(value: Any) -> Any:
    """Datetimes and other DB scalars → JSON-safe values."""
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [jsonable(v) for v in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value
