"""API service (ADR-0029 §5): upload, persistence, query. Must never import torch.

    .venv/Scripts/python.exe -m uvicorn services.api.app.main:app --port 8000

Settings from the environment: `DATABASE_URL`, `INFERENCE_URL` (default
http://localhost:8001), `UPLOAD_DIR` (default data/uploads).
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from ml.captioning.lexicon import VI_LEXICON_CONFIG, CaptionLexicon
from ml.retrieval import store
from ml.retrieval.query_parser import QueryParser
from ml.taxonomy import load_taxonomy
from services.api.app import recordings, retrieval
from services.api.app.inference import InferenceClient, InferenceUnavailable
from services.common.envelope import fail, ok

ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    database_url: str | None
    inference_url: str
    upload_dir: Path
    frontend_dist: Path | None = None

    @classmethod
    def from_env(cls) -> Settings:
        return cls(os.environ.get("DATABASE_URL"),
                   os.environ.get("INFERENCE_URL", "http://localhost:8001"),
                   Path(os.environ.get("UPLOAD_DIR", ROOT / "data/uploads")),
                   Path(os.environ.get("FRONTEND_DIST", ROOT / "services/frontend/dist")))


def _database_ok(connect: Callable[[], Any]) -> bool:
    try:
        conn = connect()
        try:
            conn.execute("SELECT 1")
        finally:
            conn.close()
        return True
    except Exception:  # noqa: BLE001 — any failure means "not ready"
        return False


def create_app(settings: Settings | None = None, inference: Any = None,
               connect: Callable[[], Any] | None = None, query_parser: Any = None) -> FastAPI:
    settings = settings or Settings.from_env()
    app = FastAPI(title="environmental-audio api")
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    vi = CaptionLexicon.from_taxonomy(taxonomy, config=VI_LEXICON_CONFIG)
    labels = {c.class_id: c.source_label.lower() for c in taxonomy.classes}
    app.state.settings = settings
    app.state.taxonomy = taxonomy
    app.state.class_names = {"en": labels.__getitem__, "vi": vi.canonical_phrase}
    parser_labels = {class_id: {"en": labels[class_id], "vi": vi.canonical_phrase(class_id)}
                     for class_id in taxonomy.polyphonic_class_ids}
    app.state.query_parser = query_parser or QueryParser.from_config(
        ROOT / "ml/configs/caption_llm.yaml", parser_labels)
    app.state.inference = inference or InferenceClient(settings.inference_url)
    app.state.connect = connect or (lambda: store.connect(settings.database_url))
    app.include_router(recordings.router)
    app.include_router(retrieval.router)

    @app.exception_handler(RequestValidationError)
    async def invalid(_: Request, exc: RequestValidationError):
        return fail(422, "invalid_request", "; ".join(
            f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()))

    @app.get("/health")
    async def health():
        database = await asyncio.to_thread(_database_ok, app.state.connect)
        try:
            model = (await app.state.inference.health())["model_version"]
        except InferenceUnavailable:
            model = None
        components = {"database": database, "inference": model is not None,
                      "model_version": model}
        if database and model:
            return ok({"status": "ready", **components})
        return fail(503, "not_ready", "database hoặc inference chưa sẵn sàng", meta=components)

    classes = [{"class_id": c, "label_en": labels[c], "label_vi": vi.canonical_phrase(c)}
               for c in taxonomy.polyphonic_class_ids]

    @app.get("/api/v1/taxonomy")
    async def taxonomy_view():
        """The 21 SED classes with display names — the frontend keeps no class constants."""
        return ok({"version": taxonomy.version, "sha256": taxonomy.checksum, "classes": classes})

    @app.get("/api/v1/models/status")
    async def models_status():
        try:
            info = await app.state.inference.models()
        except InferenceUnavailable as exc:
            return fail(503, "inference_unavailable", str(exc))
        return ok({**info, "api_taxonomy_sha256": taxonomy.checksum,
                   "taxonomy_consistent": info.get("taxonomy_sha256") == taxonomy.checksum})

    # Built frontend (7.4): one origin for UI and API. Mounted last so API routes win.
    if settings.frontend_dist is not None and (settings.frontend_dist / "index.html").is_file():
        app.mount("/", StaticFiles(directory=settings.frontend_dist, html=True), name="frontend")
    return app


app = create_app()
