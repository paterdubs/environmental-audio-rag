-- Event store schema for PostgreSQL 16 + pgvector (ADR-0005).
-- This migration is intentionally SQL-only so it can be reviewed/run by Alembic later.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE recordings (
    recording_id TEXT PRIMARY KEY,
    source_dataset TEXT NOT NULL CHECK (source_dataset IN ('datased', 'datasec', 'upload')),
    source_id TEXT NOT NULL,
    duration_s DOUBLE PRECISION NOT NULL CHECK (duration_s > 0),
    sample_rate INTEGER NOT NULL CHECK (sample_rate > 0),
    channels SMALLINT NOT NULL CHECK (channels > 0),
    sha256 CHAR(64) NOT NULL,
    split TEXT CHECK (split IN ('train', 'validation', 'test') OR split IS NULL),
    captured_at TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    audio_path TEXT,
    UNIQUE (source_dataset, source_id)
);

CREATE TABLE events (
    event_id BIGSERIAL PRIMARY KEY,
    recording_id TEXT NOT NULL REFERENCES recordings(recording_id) ON DELETE CASCADE,
    class_id TEXT NOT NULL,
    onset_s DOUBLE PRECISION NOT NULL CHECK (onset_s >= 0),
    offset_s DOUBLE PRECISION NOT NULL CHECK (offset_s > onset_s),
    score REAL NOT NULL CHECK (score BETWEEN 0 AND 1),
    label_mode TEXT NOT NULL CHECK (label_mode IN ('polyphonic', 'monophonic')),
    provenance TEXT NOT NULL CHECK (provenance IN ('ground_truth', 'prediction')),
    model_version TEXT,
    taxonomy_version TEXT NOT NULL,
    CHECK ((provenance = 'ground_truth' AND model_version IS NULL)
        OR (provenance = 'prediction' AND model_version IS NOT NULL))
);

CREATE TABLE event_subclass_predictions (
    event_id BIGINT NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
    subclass_id TEXT NOT NULL,
    score REAL NOT NULL CHECK (score BETWEEN 0 AND 1),
    model_version TEXT NOT NULL,
    verifiable BOOLEAN NOT NULL,
    PRIMARY KEY (event_id, subclass_id, model_version)
);

CREATE TABLE captions (
    caption_id BIGSERIAL PRIMARY KEY,
    recording_id TEXT NOT NULL REFERENCES recordings(recording_id) ON DELETE CASCADE,
    language CHAR(2) NOT NULL CHECK (language IN ('en', 'vi')),
    text TEXT NOT NULL CHECK (length(trim(text)) > 0),
    captioner_version TEXT NOT NULL,
    grounding_mode TEXT NOT NULL CHECK (grounding_mode IN ('constrained', 'unconstrained')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE caption_evidence (
    caption_id BIGINT NOT NULL REFERENCES captions(caption_id) ON DELETE CASCADE,
    event_id BIGINT NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
    mention_span INT4RANGE,
    PRIMARY KEY (caption_id, event_id)
);

CREATE TABLE retrieval_documents (
    document_id BIGSERIAL PRIMARY KEY,
    recording_id TEXT NOT NULL REFERENCES recordings(recording_id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    embedding VECTOR(1024),
    embedding_version TEXT NOT NULL,
    class_ids TEXT[] NOT NULL,
    total_events INTEGER NOT NULL CHECK (total_events >= 0),
    max_polyphony SMALLINT NOT NULL CHECK (max_polyphony >= 0),
    UNIQUE (recording_id, embedding_version)
);

CREATE TABLE runs (
    run_id TEXT PRIMARY KEY,
    task TEXT NOT NULL,
    config_sha256 CHAR(64) NOT NULL,
    data_manifest_sha256 CHAR(64) NOT NULL,
    split_sha256 CHAR(64) NOT NULL,
    taxonomy_sha256 CHAR(64) NOT NULL,
    code_revision TEXT NOT NULL,
    seed INTEGER NOT NULL,
    primary_metric TEXT NOT NULL,
    primary_value REAL,
    complete BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX events_recording_onset_idx ON events (recording_id, onset_s);
CREATE INDEX events_class_onset_idx ON events (class_id, onset_s);
CREATE INDEX events_duration_idx ON events ((offset_s - onset_s));
CREATE INDEX docs_class_gin_idx ON retrieval_documents USING gin (class_ids);
CREATE INDEX docs_embedding_hnsw_idx ON retrieval_documents USING hnsw (embedding vector_cosine_ops);
