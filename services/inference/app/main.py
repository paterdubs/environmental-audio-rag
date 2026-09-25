"""Inference service (ADR-0029 §4): the only process that loads checkpoints or BGE-M3.

    .venv/Scripts/python.exe -m uvicorn services.inference.app.main:app --port 8001

No SQL here — `api` persists. `/health` is 200 only once every model is loaded (SYSTEM §4.4).
"""

from __future__ import annotations

import asyncio
import tempfile
import uuid
from collections.abc import Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, UploadFile
from pydantic import BaseModel, Field

from services.common.audio import AudioRejected, save_upload
from services.common.envelope import fail, ok

MAX_TEXTS = 64
MAX_TEXT_CHARS = 4000


class EmbedRequest(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=MAX_TEXTS)


def load_engine() -> Any:
    from ml.inference.engine import Engine  # torch import deferred to startup

    return Engine()


def create_app(engine_factory: Callable[[], Any] = load_engine) -> FastAPI:
    state: dict[str, Any] = {}

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        state["engine"] = await asyncio.to_thread(engine_factory)
        yield
        state.clear()

    app = FastAPI(title="environmental-audio inference", lifespan=lifespan)

    @app.get("/health")
    def health():
        engine = state.get("engine")
        if engine is None:
            return fail(503, "not_ready", "model chưa nạp xong")
        return ok({"status": "ready", "model_version": engine.info()["model_version"]})

    @app.get("/v1/models")
    def models():
        engine = state.get("engine")
        return ok(engine.info()) if engine else fail(503, "not_ready", "model chưa nạp xong")

    @app.post("/v1/analyze")
    async def analyze(file: UploadFile = File(...), recording_id: str = Form(...)):  # noqa: B008
        engine = state.get("engine")
        if engine is None:
            return fail(503, "not_ready", "model chưa nạp xong")
        with tempfile.TemporaryDirectory() as tmp:
            try:
                stored = await save_upload(file, Path(tmp) / f"{uuid.uuid4().hex}"
                                           f"{Path(file.filename or '').suffix.lower()}")
            except AudioRejected as exc:
                return fail(exc.status, exc.code, str(exc))
            result = await asyncio.to_thread(engine.analyze, recording_id, stored.path)
        audio = {"sha256": stored.sha256, "bytes": stored.size, "duration_s": stored.duration_s,
                 "sample_rate": stored.sample_rate, "channels": stored.channels}
        return ok({**result, "audio": audio})

    @app.post("/v1/embed")
    async def embed(request: EmbedRequest):
        engine = state.get("engine")
        if engine is None:
            return fail(503, "not_ready", "model chưa nạp xong")
        if any(not t.strip() or len(t) > MAX_TEXT_CHARS for t in request.texts):
            return fail(422, "bad_text", f"mỗi câu phải khác rỗng và ≤ {MAX_TEXT_CHARS} ký tự")
        vectors = await asyncio.to_thread(engine.embed, request.texts)
        return ok({"vectors": vectors.tolist(),
                   "embedding_version": engine.info()["embedding_version"]})

    return app


app = create_app()
