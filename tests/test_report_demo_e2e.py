import pytest

from scripts import report_demo_e2e as report


def test_cli_requires_a_recording_id() -> None:
    args = report.parse_args(["--recording-id", "S-0016"])
    assert args.recording_id == "S-0016"


def test_train_audio_rejects_non_train_recording(monkeypatch, tmp_path) -> None:
    (tmp_path / "data/splits").mkdir(parents=True)
    (tmp_path / "data/splits/datased_polyphonic.csv").write_text(
        "recording_id,split\nS-X,test\n", encoding="utf-8")
    monkeypatch.setattr(report, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="không thuộc split train"):
        report.train_audio("S-X")


def test_render_records_operational_evidence() -> None:
    text = report.render({
        "source_recording_id": "S-0016", "source_split": "train",
        "served_run": "ml/runs/v2", "official": False, "device": "cpu",
        "upload_elapsed_s": 1.2345, "events": 2, "caption_languages": ["en", "vi"],
        "captions_with_evidence": 2, "rag_mode": "hybrid", "rag_elapsed_s": 0.25,
        "rag_evidence": 1, "rag_contains_uploaded_recording": True,
    })
    assert "1.234 s" in text and "official=`false`" in text
    assert "en, vi" in text and "chứa recording vừa upload: true" in text
