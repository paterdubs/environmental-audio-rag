import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"


def validate(name: str, instance: object) -> None:
    schema = json.loads((CONTRACTS / name).read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(instance)


@pytest.mark.parametrize(
    "name",
    [
        "recording.schema.json",
        "event.schema.json",
        "timeline.schema.json",
        "inference_response.schema.json",
        "retrieval_result.schema.json",
        "run_manifest.schema.json",
    ],
)
def test_contract_schema_is_valid_draft_2020_12(name: str) -> None:
    schema = json.loads((CONTRACTS / name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)


def test_recording_contract_rejects_invalid_sha256() -> None:
    recording = {
        "recording_id": "datased:S-0001",
        "source_dataset": "datased",
        "source_id": "S-0001",
        "duration_s": 93.8,
        "sample_rate": 44100,
        "channels": 1,
        "sha256": "not-a-sha256",
        "split": "train",
        "captured_at": None,
        "ingested_at": "2026-09-23T00:00:00Z",
        "audio_path": "data/raw/datased/S-0001.wav",
    }

    with pytest.raises(ValidationError):
        validate("recording.schema.json", recording)


def test_prediction_event_requires_model_version() -> None:
    event = {
        "event_id": 1,
        "recording_id": "datased:S-0001",
        "class_id": "birds",
        "onset_s": 0.0,
        "offset_s": 17.6,
        "score": 0.88,
        "label_mode": "polyphonic",
        "provenance": "prediction",
        "model_version": None,
        "taxonomy_version": "0.1",
    }

    with pytest.raises(ValidationError):
        validate("event.schema.json", event)


def test_timeline_contract_requires_prediction_versions() -> None:
    timeline = {
        "recording_id": "datased:S-0001",
        "duration_s": 93.8,
        "taxonomy_version": "0.1",
        "model_version": "sed-v1.0",
        "events": [
            {"event_id": 1, "class_id": "birds", "onset_s": 0.0, "offset_s": 17.6, "score": 0.88}
        ],
    }

    validate("timeline.schema.json", timeline)
    timeline.pop("model_version")
    with pytest.raises(ValidationError):
        validate("timeline.schema.json", timeline)


def test_inference_envelope_keeps_success_and_error_consistent() -> None:
    response = {
        "success": True,
        "data": {
            "recording_id": "datased:S-0001",
            "duration_s": 93.8,
            "taxonomy_version": "0.1",
            "model_version": "sed-v1.0",
            "events": [],
        },
        "error": None,
        "meta": {},
    }
    validate("inference_response.schema.json", response)

    response["error"] = {"code": "unexpected", "message": "must be null on success"}
    with pytest.raises(ValidationError):
        validate("inference_response.schema.json", response)


def test_retrieval_result_allows_empty_evidence_with_applied_filters() -> None:
    result = {
        "question": "Was glass breaking detected?",
        "filters_applied": {"mode": "hybrid"},
        "answer": "No matching event was found.",
        "evidence": [],
        "documents": [],
    }

    validate("retrieval_result.schema.json", result)


@pytest.mark.parametrize("manifest", sorted((ROOT / "ml" / "runs").glob("*/manifest.json")))
def test_committed_run_manifests_match_contract(manifest: Path) -> None:
    validate("run_manifest.schema.json", json.loads(manifest.read_text(encoding="utf-8")))
