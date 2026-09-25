"""Recording-level reads and writes for the API (ADR-0029 §5–§6). Torch-free.

Every event returned carries ``model_version`` and ``taxonomy_version`` (SYSTEM §4.4 rule 2);
captions come with their ``caption_evidence`` rows — a caption without them is not grounded.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from ml.retrieval import store

RECORDING_COLUMNS = ("recording_id", "source_dataset", "source_id", "duration_s", "sample_rate",
                     "channels", "sha256", "split", "ingested_at", "audio_path")


def find_by_sha(conn, sha256: str, source_dataset: str = "upload") -> str | None:
    row = conn.execute("SELECT recording_id FROM recordings WHERE sha256 = %s"
                       " AND source_dataset = %s", (sha256, source_dataset)).fetchone()
    return row[0] if row else None


def get_recording(conn, recording_id: str) -> dict[str, Any] | None:
    row = conn.execute(f"SELECT {', '.join(RECORDING_COLUMNS)} FROM recordings"
                       " WHERE recording_id = %s", (recording_id,)).fetchone()
    return dict(zip(RECORDING_COLUMNS, row, strict=True)) if row else None


def recording_events(conn, recording_id: str) -> list[dict[str, Any]]:
    columns = ("event_id", "class_id", "onset_s", "offset_s", "score", "provenance",
               "model_version", "taxonomy_version")
    rows = conn.execute(f"SELECT {', '.join(columns)} FROM events WHERE recording_id = %s"
                        " ORDER BY onset_s, offset_s, class_id, event_id",
                        (recording_id,)).fetchall()
    return [dict(zip(columns, row, strict=True)) for row in rows]


def recording_captions(conn, recording_id: str) -> list[dict[str, Any]]:
    captions = conn.execute(
        "SELECT caption_id, language, text, captioner_version, grounding_mode FROM captions"
        " WHERE recording_id = %s ORDER BY language, caption_id", (recording_id,)).fetchall()
    out = []
    for caption_id, language, text, version, mode in captions:
        evidence = conn.execute(
            "SELECT event_id, lower(mention_span), upper(mention_span) FROM caption_evidence"
            " WHERE caption_id = %s ORDER BY lower(mention_span)", (caption_id,)).fetchall()
        out.append({"caption_id": caption_id, "language": language, "text": text,
                    "captioner_version": version, "grounding_mode": mode,
                    "evidence": [{"event_id": e, "mention_span": [s, t]}
                                 for e, s, t in evidence]})
    return out


def list_recordings(conn, corpus: str, class_id: str | None, limit: int, offset: int
                    ) -> tuple[list[dict[str, Any]], int]:
    """Recordings of one corpus, optionally only those with a predicted event of `class_id`."""
    where = store.corpus_clause(corpus)
    params: dict[str, Any] = {"split": corpus, "limit": limit, "offset": offset}
    if class_id is not None:
        where += (" AND EXISTS (SELECT 1 FROM events e WHERE e.recording_id = r.recording_id"
                  " AND e.class_id = %(class_id)s AND e.provenance = 'prediction')")
        params["class_id"] = class_id
    total = conn.execute(f"SELECT count(*) FROM recordings r WHERE {where}", params).fetchone()[0]
    rows = conn.execute(
        f"SELECT {', '.join('r.' + c for c in RECORDING_COLUMNS)} FROM recordings r WHERE {where}"
        " ORDER BY r.ingested_at DESC, r.recording_id LIMIT %(limit)s OFFSET %(offset)s",
        params).fetchall()
    return [dict(zip(RECORDING_COLUMNS, row, strict=True)) for row in rows], int(total)


def insert_analysis(conn, recording: Mapping[str, Any], analysis: Mapping[str, Any],
                    vector: np.ndarray, embedding_version: str) -> None:
    """Recording + events + captions (with evidence) + document. The caller commits or rolls
    back — a nested `conn.transaction()` would only be a savepoint inside an implicit
    transaction already opened by an earlier SELECT, and nothing would be committed."""
    timeline = analysis["timeline"]
    store.insert_recording(conn, recording)
    event_map = store.insert_events(conn, recording["recording_id"], timeline["events"],
                                    timeline["model_version"], timeline["taxonomy_version"])
    for caption in analysis["captions"].values():
        store.insert_caption(conn, recording["recording_id"], caption, event_map)
    store.insert_document(conn, analysis["document"], vector, embedding_version)


def corpus_embedding_versions(conn, corpus: str) -> list[str]:
    rows = conn.execute(
        "SELECT DISTINCT d.embedding_version FROM retrieval_documents d JOIN recordings r"
        f" USING (recording_id) WHERE {store.corpus_clause(corpus)}", {"split": corpus}).fetchall()
    return sorted(row[0] for row in rows)
