"""API service: validation without a database, and a full upload → query round trip against
the real event store (skipped without PostgreSQL; everything created is deleted)."""

import hashlib
import io
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import soundfile

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from ml.captioning.lexicon import VI_LEXICON_CONFIG, CaptionLexicon  # noqa: E402
from ml.captioning.template import TemplateCaptioner  # noqa: E402
from ml.captioning.timeline import canonicalize_timeline  # noqa: E402
from ml.retrieval import store  # noqa: E402
from ml.retrieval.document_builder import build_document  # noqa: E402
from ml.taxonomy import load_taxonomy  # noqa: E402
from services.api.app.inference import InferenceUnavailable  # noqa: E402
from services.api.app.main import Settings, create_app  # noqa: E402

ROOT = Path(__file__).parents[1]
TAXONOMY = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
VERSION = "test-embedding-api"


class FakeInference:
    """Stands in for the inference service; builds a real template analysis."""

    def __init__(self, available: bool = True) -> None:
        self.available = available

    async def health(self):
        if not self.available:
            raise InferenceUnavailable("down")
        return {"model_version": "sed-fake"}

    async def models(self):
        return {"model_version": "sed-fake", "taxonomy_sha256": TAXONOMY.checksum}

    async def embed(self, texts):
        vector = np.zeros(1024, np.float32)
        vector[0] = 1.0
        return {"vectors": [vector.tolist()] * len(texts), "embedding_version": VERSION}

    async def analyze(self, recording_id, path):
        if not self.available:
            raise InferenceUnavailable("down")
        events = [{"class_id": "birds", "onset_s": 0.2, "offset_s": 0.6, "score": 0.9},
                  {"class_id": "horn", "onset_s": 0.7, "offset_s": 0.9, "score": 0.8}]
        timeline = canonicalize_timeline(recording_id, 1.0, events, TAXONOMY,
                                         model_version="sed-fake")
        en = TemplateCaptioner(CaptionLexicon.from_taxonomy(TAXONOMY)).caption(timeline)
        vi = TemplateCaptioner(CaptionLexicon.from_taxonomy(
            TAXONOMY, config=VI_LEXICON_CONFIG)).caption(timeline, language="vi")
        vector = (await self.embed(["x"]))["vectors"][0]
        return {"timeline": timeline, "captions": {"en": en, "vi": vi},
                "document": build_document(en["text"] + "\n" + vi["text"], timeline),
                "embedding": vector, "embedding_version": VERSION,
                "audio": {"sha256": hashlib.sha256(path.read_bytes()).hexdigest()}}


def wav(seed: int) -> bytes:
    buffer = io.BytesIO()
    noise = np.random.default_rng(seed).normal(0, 0.01, 16000).astype(np.float32)
    soundfile.write(buffer, noise, 16000, format="WAV")
    return buffer.getvalue()


def client(tmp_path, inference=None, connect=None) -> TestClient:
    settings = Settings(None, "http://unused", tmp_path)
    return TestClient(create_app(settings, inference or FakeInference(), connect))


def test_api_process_never_imports_torch() -> None:
    code = ("import sys, services.api.app.main; "
            "sys.exit(1 if 'torch' in sys.modules else 0)")
    assert subprocess.run([sys.executable, "-c", code], cwd=ROOT).returncode == 0


def test_request_validation_uses_the_envelope(tmp_path) -> None:
    api = client(tmp_path, connect=lambda: pytest.fail("no database needed"))
    unknown = api.post("/api/v1/retrieval/query",
                       json={"question": "q", "filters": {"classes_all": ["car"]}})
    no_filter = api.post("/api/v1/retrieval/query", json={"question": "q", "filters": {}})
    bad_file = api.post("/api/v1/audio/upload", files={"file": ("a.txt", b"x", "text/plain")})
    assert unknown.status_code == 422 and unknown.json()["error"]["code"] == "unknown_class"
    assert no_filter.status_code == 422 and not no_filter.json()["success"]
    assert bad_file.status_code == 415


def test_taxonomy_endpoint_lists_the_21_sed_classes_with_both_names(tmp_path) -> None:
    data = client(tmp_path).get("/api/v1/taxonomy").json()["data"]
    assert [c["class_id"] for c in data["classes"]] == list(TAXONOMY.polyphonic_class_ids)
    assert all(c["label_en"] and c["label_vi"] for c in data["classes"])
    assert data["sha256"] == TAXONOMY.checksum


def test_built_frontend_is_served_without_shadowing_the_api(tmp_path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<!doctype html><title>ui</title>", encoding="utf-8")
    settings = Settings(None, "http://unused", tmp_path, dist)
    api = TestClient(create_app(settings, FakeInference(), lambda: None))
    assert "<title>ui</title>" in api.get("/").text
    assert api.get("/api/v1/taxonomy").json()["success"]


def test_health_is_503_when_inference_is_down(tmp_path) -> None:
    def broken():
        raise OSError("no db")
    response = client(tmp_path, FakeInference(available=False), broken).get("/health")
    assert response.status_code == 503
    assert response.json()["meta"] == {"database": False, "inference": False,
                                       "model_version": None}


class BrokenConnection:
    """Answers the duplicate lookup, then fails the insert like a lost database would."""

    def execute(self, sql, *args):
        if sql.lstrip().upper().startswith("SELECT"):
            return type("Cursor", (), {"fetchone": lambda self: None})()
        raise OSError("database went away")

    def rollback(self):
        pass

    def close(self):
        pass


def test_failed_insert_leaves_no_orphan_audio(tmp_path) -> None:
    api = TestClient(create_app(Settings(None, "http://unused", tmp_path), FakeInference(),
                                BrokenConnection), raise_server_exceptions=False)
    response = api.post("/api/v1/audio/upload", files={"file": ("a.wav", wav(3), "audio/wav")})
    assert response.status_code == 500
    assert list(tmp_path.iterdir()) == []


def _db_or_skip():
    try:
        store.connect().close()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"PostgreSQL not available: {exc}")


def test_upload_then_read_then_query_round_trip(tmp_path) -> None:
    _db_or_skip()
    api = client(tmp_path)
    created = []
    try:
        first = api.post("/api/v1/audio/upload", files={"file": ("a.wav", wav(1), "audio/wav")})
        assert first.status_code == 201, first.json()
        rid = first.json()["data"]["recording_id"]
        created.append(rid)
        again = api.post("/api/v1/audio/upload", files={"file": ("b.wav", wav(1), "audio/wav")})
        assert again.json()["data"]["recording_id"] == rid and again.json()["meta"]["duplicate"]

        detail = api.get(f"/api/v1/recordings/{rid}").json()["data"]
        assert detail["model_versions"] == ["sed-fake"] and len(detail["captions"]) == 2
        assert all(len(c["evidence"]) == 2 for c in detail["captions"])
        assert api.get(f"/api/v1/recordings/{rid}/audio").status_code == 200
        listed = api.get("/api/v1/recordings", params={"class_id": "horn"}).json()
        assert rid in [r["recording_id"] for r in listed["data"]]

        body = {"question": "chim rồi còi xe", "corpus": "upload", "language": "vi",
                "filters": {"temporal": {"predicate": "before", "a": "birds", "b": "horn"}}}
        answer = api.post("/api/v1/retrieval/query", json=body).json()
        assert answer["success"]
        assert {e["recording_id"] for e in answer["data"]["evidence"]} == {rid}
        missing = api.post("/api/v1/retrieval/query", json={
            **body, "filters": {"temporal": {"predicate": "before", "a": "horn", "b": "birds"}}})
        assert missing.json()["data"]["evidence"] == []
        assert api.get("/api/v1/recordings/upload:none").status_code == 404
    finally:
        conn = store.connect()
        conn.execute("DELETE FROM recordings WHERE recording_id = ANY(%s)", (created,))
        conn.commit()
        conn.close()
