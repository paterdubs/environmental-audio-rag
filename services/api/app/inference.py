"""HTTP client for the inference service — the api never loads a model itself."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

ANALYZE_TIMEOUT_S = 300.0
DEFAULT_TIMEOUT_S = 30.0


class InferenceUnavailable(RuntimeError):
    pass


class InferenceClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def _request(self, method: str, path: str, timeout: float, **kwargs) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=timeout) as client:
                response = await client.request(method, path, **kwargs)
        except httpx.HTTPError as exc:
            raise InferenceUnavailable(f"không gọi được inference: {exc}") from exc
        body = response.json()
        if not body.get("success"):
            error = body.get("error") or {}
            raise InferenceUnavailable(error.get("message", f"inference {response.status_code}"))
        return body["data"]

    async def health(self) -> dict[str, Any]:
        return await self._request("GET", "/health", DEFAULT_TIMEOUT_S)

    async def models(self) -> dict[str, Any]:
        return await self._request("GET", "/v1/models", DEFAULT_TIMEOUT_S)

    async def analyze(self, recording_id: str, path: Path) -> dict[str, Any]:
        with path.open("rb") as handle:
            files = {"file": (path.name, handle, "application/octet-stream")}
            return await self._request("POST", "/v1/analyze", ANALYZE_TIMEOUT_S,
                                       data={"recording_id": recording_id}, files=files)

    async def embed(self, texts: list[str]) -> dict[str, Any]:
        return await self._request("POST", "/v1/embed", DEFAULT_TIMEOUT_S,
                                   json={"texts": texts})
