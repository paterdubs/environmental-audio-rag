"""Upload corpus round trip against the real event store; every write is rolled back."""

from pathlib import Path

import numpy as np
import pytest

from ml.captioning.lexicon import VI_LEXICON_CONFIG, CaptionLexicon
from ml.captioning.template import TemplateCaptioner
from ml.captioning.timeline import canonicalize_timeline
from ml.retrieval import recordings, store
from ml.retrieval.document_builder import build_document
from ml.taxonomy import load_taxonomy

TAXONOMY = load_taxonomy(Path(__file__).parents[1] / "ml/configs/taxonomy.yaml")
RID = "upload:00000000-0000-0000-0000-000000000000"
SHA = "f" * 64
VERSION = "test-embedding"


def _connect_or_skip():
    try:
        conn = store.connect()
        store.apply_migrations(conn, Path(__file__).parents[1] / "db/migrations")
    except Exception as exc:  # noqa: BLE001 — any connection failure means "no database here"
        pytest.skip(f"PostgreSQL not available: {exc}")
    return conn


def analysis() -> dict:
    events = [{"class_id": "birds", "onset_s": 1.0, "offset_s": 4.0, "score": 0.9},
              {"class_id": "horn", "onset_s": 2.0, "offset_s": 3.0, "score": 0.8}]
    timeline = canonicalize_timeline(RID, 30.0, events, TAXONOMY, model_version="sed-test")
    en = TemplateCaptioner(CaptionLexicon.from_taxonomy(TAXONOMY)).caption(timeline)
    vi = TemplateCaptioner(CaptionLexicon.from_taxonomy(TAXONOMY, config=VI_LEXICON_CONFIG)
                           ).caption(timeline, language="vi")
    document = build_document(en["text"] + "\n" + vi["text"], timeline)
    return {"timeline": timeline, "captions": {"en": en, "vi": vi}, "document": document}


def test_upload_round_trip_keeps_versions_evidence_and_corpus_scope() -> None:
    conn = _connect_or_skip()
    try:
        row = {"recording_id": RID, "source_dataset": "upload", "source_id": RID.split(":")[1],
               "duration_s": 30.0, "sample_rate": 44100, "channels": 1, "sha256": SHA,
               "split": None, "audio_path": "data/uploads/x.wav"}
        vector = np.zeros(1024, np.float32)
        vector[0] = 1.0
        recordings.insert_analysis(conn, row, analysis(), vector, VERSION)

        assert recordings.find_by_sha(conn, SHA) == RID
        assert recordings.get_recording(conn, RID)["source_dataset"] == "upload"
        events = recordings.recording_events(conn, RID)
        assert [e["class_id"] for e in events] == ["birds", "horn"]
        assert all(e["model_version"] == "sed-test" and e["taxonomy_version"] for e in events)
        captions = recordings.recording_captions(conn, RID)
        assert {c["language"] for c in captions} == {"en", "vi"}
        assert all(len(c["evidence"]) == 2 for c in captions)
        listed, total = recordings.list_recordings(conn, "upload", "horn", 10, 0)
        assert RID in [r["recording_id"] for r in listed] and total >= 1
        hits = store.search(conn, "structured_only", "upload", {"classes_all": ["horn"]},
                            None, VERSION)
        assert hits == [RID]
        # benchmark corpora never see uploads
        assert RID not in store.search(conn, "vector_only", "test", {}, vector, VERSION)
        # the dev database may also hold real demo uploads with the served embedding version
        assert VERSION in recordings.corpus_embedding_versions(conn, "upload")
    finally:
        conn.rollback()
    try:
        assert recordings.find_by_sha(conn, SHA) is None  # nothing leaked into the store
    finally:
        conn.rollback()
        conn.close()
