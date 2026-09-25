"""W6 6.1–6.4 — dựng event store + index BGE-M3 cho một corpus (ADR-0027).

    docker compose up -d
    .venv/Scripts/python.exe -m scripts.build_retrieval_index --split validation test

Mỗi corpus: timeline e2e từ dự đoán đóng băng của run (mặc định run B `054531Z` +
`postproc.json`, E5) → caption template EN + VI (ADR-0025) → document (caption + tóm tắt event,
SYSTEM §7.1) → embedding BGE-M3 → nạp `recordings`, `events`, `captions`, `caption_evidence`,
`retrieval_documents`. Corpus đã có trong DB thì dừng, trừ khi `--replace`.
Ghi provenance vào `ml/runs/retrieval_index_<ts>/manifest.json`.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from ml.captioning.lexicon import VI_LEXICON_CONFIG, CaptionLexicon
from ml.captioning.template import TemplateCaptioner
from ml.provenance import git_state
from ml.retrieval import store
from ml.retrieval.document_builder import build_document
from ml.retrieval.embedding import Embedder
from ml.taxonomy import load_taxonomy
from scripts.generate_llm_captions import e2e_timelines

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = ROOT / "ml/runs/sed_polyphonic_20260924T054531Z"
SPLIT_FILE = {"validation": "dev", "test": "test"}  # corpus name -> predictions file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--postproc", type=Path, default=None)
    parser.add_argument("--split", nargs="+", choices=tuple(SPLIT_FILE), default=["validation"])
    parser.add_argument("--device", default=None)
    parser.add_argument("--replace", action="store_true")
    return parser.parse_args()


def recording_rows() -> dict[str, dict]:
    splits = {}
    with (ROOT / "data/splits/datased_polyphonic.csv").open(encoding="utf-8", newline="") as f:
        splits = {row["recording_id"]: row["split"] for row in csv.DictReader(f)}
    rows = {}
    with (ROOT / "data/manifests/datased_recordings.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rid = row["recording_id"]
            rows[f"datased:{rid}"] = {
                "recording_id": f"datased:{rid}", "source_id": rid,
                "duration_s": float(row["duration_s"]), "sample_rate": int(row["sample_rate"]),
                "channels": int(row["channels"]), "sha256": row["content_sha256"],
                "split": splits[rid], "audio_path": row["audio_relative_path"]}
    return rows


def build_corpus(args, split: str, taxonomy, embedder: Embedder) -> dict:
    timelines = e2e_timelines(args.run, SPLIT_FILE[split], taxonomy, args.postproc)
    en = TemplateCaptioner(CaptionLexicon.from_taxonomy(taxonomy))
    vi = TemplateCaptioner(CaptionLexicon.from_taxonomy(taxonomy, config=VI_LEXICON_CONFIG))
    items = []
    for rid in sorted(timelines):
        timeline = timelines[rid]
        captions = (en.caption(timeline), vi.caption(timeline, language="vi"))
        document = build_document(captions[0]["text"] + "\n" + captions[1]["text"], timeline)
        items.append((timeline, captions, document))
    vectors = embedder.encode([doc["text"] for _, _, doc in items])
    return {"items": items, "vectors": vectors}


def load_corpus(conn, split: str, corpus: dict, meta: dict, version: str, replace: bool) -> int:
    existing = conn.execute("SELECT count(*) FROM recordings WHERE split = %s",
                            (split,)).fetchone()[0]
    if existing and not replace:
        raise SystemExit(f"corpus {split} đã có {existing} recording — dùng --replace")
    conn.execute("DELETE FROM recordings WHERE split = %s", (split,))
    for (timeline, captions, document), vector in zip(corpus["items"], corpus["vectors"],
                                                      strict=True):
        rid = timeline["recording_id"]
        store.insert_recording(conn, meta[rid])
        event_map = store.insert_events(conn, rid, timeline["events"],
                                        timeline["model_version"], timeline["taxonomy_version"])
        for caption in captions:
            store.insert_caption(conn, rid, caption, event_map)
        store.insert_document(conn, document, vector, version)
    conn.commit()
    return len(corpus["items"])


def run_manifest(run_id, args, taxonomy, embedder, loaded, migrations, git) -> dict:
    """Valid against contracts/run_manifest.schema.json, like every run under ml/runs."""
    import platform

    import sentence_transformers

    sed = json.loads((args.run / "manifest.json").read_text(encoding="utf-8"))
    return {
        "run_id": run_id, "task": "retrieval_index", "complete": True,
        "command": ["python", "-m", "scripts.build_retrieval_index", *sys.argv[1:]],
        "class_ids": list(taxonomy.polyphonic_class_ids),
        "taxonomy_sha256": taxonomy.checksum, "split_sha256": sed["split_sha256"],
        "data_manifest_sha256": sed["data_manifest_sha256"],
        "config": {"sed_run": args.run.name,
                   "postproc": (args.postproc or args.run / "postproc.json").name,
                   "embedding_version": embedder.version, "model_revision": embedder.revision,
                   "corpora": loaded, "migrations_applied": migrations},
        "environment": {"python": platform.python_version(),
                        "sentence_transformers": sentence_transformers.__version__},
        "git": git,
    }


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    git = git_state(ROOT)
    taxonomy = load_taxonomy(ROOT / "ml/configs/taxonomy.yaml")
    embedder = Embedder(device=args.device)
    meta = recording_rows()
    conn = store.connect()
    migrations = store.apply_migrations(conn, ROOT / "db/migrations")
    loaded = {split: load_corpus(conn, split, build_corpus(args, split, taxonomy, embedder),
                                 meta, embedder.version, args.replace)
              for split in args.split}
    out = ROOT / "ml/runs" / f"retrieval_index_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    manifest = run_manifest(out.name, args, taxonomy, embedder, loaded, migrations, git)
    out.mkdir(parents=True)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
