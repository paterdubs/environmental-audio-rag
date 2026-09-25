"""PostgreSQL + pgvector event store for W6 (ADR-0005, ADR-0027).

Three retrieval modes (SYSTEM §7.6), always scoped to one corpus — a benchmark split
(``recordings.split``) or the uploaded recordings (``source_dataset = 'upload'``, ADR-0029 §6):

- ``structured_only`` — hard filters, ordered by the earliest onset of a filtered class;
- ``vector_only``     — cosine ranking over every document, no filter;
- ``hybrid``          — hard filters first, cosine ranking inside the filtered set.

Hard filters are SQL over the *indexed (predicted)* events, with the same predicate text as
``ml.retrieval.temporal`` — the semantic score can never override them (SYSTEM §7.2).
"""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from ml.retrieval.temporal import PREDICATES

DEFAULT_DSN = "postgresql://app:app@localhost:5432/environmental_audio"
MODES = ("structured_only", "vector_only", "hybrid")
UPLOAD_CORPUS = "upload"


def corpus_clause(corpus: str) -> str:
    """WHERE fragment over alias ``r`` (recordings); benchmark splits keep the RQ3 text."""
    if corpus == UPLOAD_CORPUS:
        return "r.source_dataset = 'upload'"
    return "r.split = %(split)s"


def connect(dsn: str | None = None):
    import psycopg
    from pgvector.psycopg import register_vector

    conn = psycopg.connect(dsn or os.environ.get("DATABASE_URL", DEFAULT_DSN))
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    return conn


def apply_migrations(conn, directory: Path) -> list[str]:
    """Apply `*.sql` files in name order once each; returns the newly applied names."""
    conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations "
                 "(name TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT now())")
    done = {row[0] for row in conn.execute("SELECT name FROM schema_migrations")}
    applied = []
    for path in sorted(directory.glob("*.sql")):
        if path.name in done:
            continue
        conn.execute(path.read_text(encoding="utf-8"))
        conn.execute("INSERT INTO schema_migrations (name) VALUES (%s)", (path.name,))
        applied.append(path.name)
    conn.commit()
    return applied


def filter_sql(filters: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    """WHERE fragment over alias ``d`` (retrieval_documents) for the query's hard filters."""
    clauses, params = [], {}
    if "classes_all" in filters:
        clauses.append("d.class_ids @> %(classes_all)s::text[]")
        params["classes_all"] = list(filters["classes_all"])
    if "temporal" in filters:
        rule = filters["temporal"]
        condition = PREDICATES[rule["predicate"]].sql().replace(":tolerance_s", "%(tol)s")
        clauses.append(
            "EXISTS (SELECT 1 FROM events a JOIN events b ON " + condition
            + " WHERE a.recording_id = d.recording_id AND a.class_id = %(ta)s"
            " AND b.class_id = %(tb)s AND a.provenance = 'prediction'"
            " AND b.provenance = 'prediction')")
        params |= {"ta": rule["a"], "tb": rule["b"], "tol": float(rule["tolerance_s"])}
    if "duration" in filters:
        clauses.append(
            "EXISTS (SELECT 1 FROM events e WHERE e.recording_id = d.recording_id"
            " AND e.class_id = %(dc)s AND e.offset_s - e.onset_s > %(dmin)s"
            " AND e.provenance = 'prediction')")
        params |= {"dc": filters["duration"]["class_id"],
                   "dmin": float(filters["duration"]["min_s"])}
    if not clauses:
        raise ValueError("a structured query needs at least one hard filter")
    return " AND ".join(clauses), params


def _order_classes(filters: Mapping[str, Any]) -> list[str]:
    if "classes_all" in filters:
        return list(filters["classes_all"])
    if "temporal" in filters:
        return [filters["temporal"]["a"]]
    return [filters["duration"]["class_id"]]


def search(conn, mode: str, split: str, filters: Mapping[str, Any],
           query_vector: np.ndarray | None, embedding_version: str, k: int = 10) -> list[str]:
    """Top-k recording ids for one query in one corpus."""
    params: dict[str, Any] = {"split": split, "version": embedding_version, "k": k}
    base = ("SELECT d.recording_id FROM retrieval_documents d JOIN recordings r "
            f"USING (recording_id) WHERE {corpus_clause(split)}"
            " AND d.embedding_version = %(version)s")
    if mode in ("structured_only", "hybrid"):
        where, extra = filter_sql(filters)
        base += " AND " + where
        params |= extra
    if mode == "structured_only":
        params["order_classes"] = _order_classes(filters)
        order = (" ORDER BY (SELECT min(e.onset_s) FROM events e WHERE e.recording_id ="
                 " d.recording_id AND e.class_id = ANY(%(order_classes)s)"
                 " AND e.provenance = 'prediction'), d.recording_id")
    elif mode in ("vector_only", "hybrid"):
        params["qv"] = query_vector
        order = " ORDER BY d.embedding <=> %(qv)s, d.recording_id"
    else:
        raise ValueError(f"unknown retrieval mode {mode!r}")
    rows = conn.execute(base + order + " LIMIT %(k)s", params).fetchall()
    return [row[0] for row in rows]


def indexed_events(conn, split: str) -> dict[str, list[dict[str, Any]]]:
    """Predicted events per recording of a corpus — what the system actually indexed."""
    rows = conn.execute(
        "SELECT e.recording_id, e.class_id, e.onset_s, e.offset_s FROM events e "
        f"JOIN recordings r USING (recording_id) WHERE {corpus_clause(split)} "
        "AND e.provenance = 'prediction'", {"split": split}).fetchall()
    events: dict[str, list[dict[str, Any]]] = {}
    for rid, class_id, onset, offset in rows:
        events.setdefault(rid, []).append({"class_id": class_id, "onset_s": onset,
                                           "offset_s": offset})
    return events


def insert_recording(conn, row: Mapping[str, Any]) -> None:
    conn.execute(
        "INSERT INTO recordings (recording_id, source_dataset, source_id, duration_s,"
        " sample_rate, channels, sha256, split, audio_path) VALUES (%(recording_id)s,"
        " %(source_dataset)s, %(source_id)s, %(duration_s)s, %(sample_rate)s, %(channels)s,"
        " %(sha256)s, %(split)s, %(audio_path)s)", {"source_dataset": "datased", **row})


def insert_events(conn, recording_id: str, events: Sequence[Mapping[str, Any]],
                  model_version: str, taxonomy_version: str) -> dict[Any, int]:
    """Insert predicted events; returns timeline event_id -> database event_id."""
    mapping = {}
    for event in events:
        row = conn.execute(
            "INSERT INTO events (recording_id, class_id, onset_s, offset_s, score, label_mode,"
            " provenance, model_version, taxonomy_version) VALUES (%s, %s, %s, %s, %s,"
            " 'polyphonic', 'prediction', %s, %s) RETURNING event_id",
            (recording_id, event["class_id"], float(event["onset_s"]),
             float(event["offset_s"]), float(event["score"]), model_version,
             taxonomy_version)).fetchone()
        mapping[event["event_id"]] = row[0]
    return mapping


def insert_caption(conn, recording_id: str, caption: Mapping[str, Any],
                   event_map: Mapping[Any, int]) -> None:
    """Caption row plus G2 evidence rows pointing at the stored events."""
    caption_id = conn.execute(
        "INSERT INTO captions (recording_id, language, text, captioner_version, grounding_mode)"
        " VALUES (%s, %s, %s, %s, %s) RETURNING caption_id",
        (recording_id, caption["language"], caption["text"], caption["captioner_version"],
         caption["grounding_mode"])).fetchone()[0]
    for item in caption["evidence"]:
        start, end = item["mention_span"]
        conn.execute("INSERT INTO caption_evidence (caption_id, event_id, mention_span)"
                     " VALUES (%s, %s, int4range(%s, %s))",
                     (caption_id, event_map[item["event_id"]], start, end))


def insert_document(conn, document: Mapping[str, Any], vector: np.ndarray,
                    embedding_version: str) -> None:
    conn.execute(
        "INSERT INTO retrieval_documents (recording_id, text, embedding, embedding_version,"
        " class_ids, total_events, max_polyphony) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (document["recording_id"], document["text"], vector, embedding_version,
         document["class_ids"], document["total_events"], document["max_polyphony"]))


def events_with_ids(conn, split: str) -> dict[str, list[dict[str, Any]]]:
    """Indexed events of a corpus with their database ids — what answers may cite."""
    rows = conn.execute(
        "SELECT e.event_id, e.recording_id, e.class_id, e.onset_s, e.offset_s FROM events e "
        f"JOIN recordings r USING (recording_id) WHERE {corpus_clause(split)} "
        "AND e.provenance = 'prediction'", {"split": split}).fetchall()
    events: dict[str, list[dict[str, Any]]] = {}
    for event_id, rid, class_id, onset, offset in rows:
        events.setdefault(rid, []).append({"event_id": event_id, "class_id": class_id,
                                           "onset_s": onset, "offset_s": offset})
    return events
