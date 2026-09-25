"""`POST /api/v1/retrieval/query` — evidence-bound answer over one corpus (SYSTEM §4.4, §7.4).

Always returns `evidence[]` (possibly empty) plus the filters actually applied; the answer text
is generated only from indexed events that satisfy those filters (`ml.retrieval.answer`).
"""

from __future__ import annotations

import asyncio
from typing import Any

import numpy as np
from fastapi import APIRouter, Request

from ml.retrieval import recordings as repo
from ml.retrieval import store
from ml.retrieval.answer import answer
from services.api.app.inference import InferenceUnavailable
from services.api.app.schemas import QueryRequest
from services.common.envelope import fail, ok

router = APIRouter(prefix="/api/v1")


def _search(connect, query: QueryRequest, vector: np.ndarray | None, version: str | None
            ) -> dict[str, Any] | str:
    conn = connect()
    try:
        if version is None:  # structured_only: scope documents by the corpus' single version
            versions = repo.corpus_embedding_versions(conn, query.corpus)
            if len(versions) != 1:
                return f"corpus {query.corpus} có {len(versions)} phiên bản embedding"
            version = versions[0]
        filters = query.filters.as_dict()
        ranked = store.search(conn, query.mode, query.corpus, filters, vector, version, query.k)
        events = store.events_with_ids(conn, query.corpus)
        return {"ranked": ranked, "events": events, "version": version}
    finally:
        conn.close()


@router.post("/retrieval/query")
async def query(request: Request, body: QueryRequest):
    state = request.app.state
    unknown = sorted(body.filters.class_ids() - set(state.taxonomy.polyphonic_class_ids))
    if unknown:
        return fail(422, "unknown_class", f"lớp ngoài 21 lớp SED: {unknown}")
    vector, version = None, None
    if body.mode == "hybrid":
        try:
            embedded = await state.inference.embed([body.question])
        except InferenceUnavailable as exc:
            return fail(503, "inference_unavailable", str(exc))
        vector = np.asarray(embedded["vectors"][0], np.float32)
        version = embedded["embedding_version"]
    found = await asyncio.to_thread(_search, state.connect, body, vector, version)
    if isinstance(found, str):
        return fail(409, "embedding_version", found)
    result = answer(body.question, body.filters.as_dict(), body.mode, found["ranked"],
                    found["events"], body.language, state.class_names[body.language], body.k)
    return ok(result, meta={"corpus": body.corpus, "embedding_version": found["version"]})
