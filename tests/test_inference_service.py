import io

import numpy as np
import pytest
import soundfile

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from services.inference.app.main import create_app  # noqa: E402


class FakeEngine:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def info(self) -> dict:
        return {"model_version": "sed-fake", "embedding_version": "emb-fake",
                "served_run": "ml/runs/sed-fake", "official": False}

    def analyze(self, recording_id, path):
        self.calls.append(recording_id)
        assert path.exists()
        return {"timeline": {"recording_id": recording_id, "events": []},
                "captions": {}, "document": {"text": "x"}, "embedding": [0.0],
                "embedding_version": "emb-fake"}

    def embed(self, texts):
        return np.ones((len(texts), 2), np.float32)


def wav_bytes(seconds: float = 1.0) -> bytes:
    buffer = io.BytesIO()
    soundfile.write(buffer, np.zeros(int(16000 * seconds), np.float32), 16000, format="WAV")
    return buffer.getvalue()


def test_health_reflects_real_readiness_and_analyze_returns_an_envelope() -> None:
    engine = FakeEngine()
    with TestClient(create_app(lambda: engine)) as client:
        assert client.get("/health").json()["data"]["model_version"] == "sed-fake"
        response = client.post("/v1/analyze", data={"recording_id": "upload:a"},
                               files={"file": ("a.wav", wav_bytes(), "audio/wav")})
    body = response.json()
    assert response.status_code == 200 and body["success"] and body["error"] is None
    assert body["data"]["audio"]["duration_s"] == pytest.approx(1.0)
    assert len(body["data"]["audio"]["sha256"]) == 64 and engine.calls == ["upload:a"]


def test_models_reports_served_run_and_official_flag() -> None:
    with TestClient(create_app(FakeEngine)) as client:
        data = client.get("/v1/models").json()["data"]
    assert data["served_run"] == "ml/runs/sed-fake" and data["official"] is False


def test_not_ready_is_503_not_200() -> None:
    client = TestClient(create_app(lambda: None))  # no lifespan run → engine absent
    response = client.get("/health")
    assert response.status_code == 503 and response.json()["error"]["code"] == "not_ready"


def test_bad_uploads_are_rejected_before_the_model() -> None:
    engine = FakeEngine()
    with TestClient(create_app(lambda: engine)) as client:
        text = client.post("/v1/analyze", data={"recording_id": "upload:b"},
                           files={"file": ("a.txt", b"hello", "text/plain")})
        broken = client.post("/v1/analyze", data={"recording_id": "upload:c"},
                             files={"file": ("a.wav", b"not audio", "audio/wav")})
    assert text.status_code == 415 and broken.status_code == 422 and engine.calls == []


def test_embed_validates_texts() -> None:
    with TestClient(create_app(FakeEngine)) as client:
        good = client.post("/v1/embed", json={"texts": ["birds then horn"]})
        empty = client.post("/v1/embed", json={"texts": ["  "]})
        none = client.post("/v1/embed", json={"texts": []})
    assert good.json()["data"]["vectors"] == [[1.0, 1.0]]
    assert empty.status_code == 422 and none.status_code == 422
