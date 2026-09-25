"""Response envelope `{success, data, error, meta}` shared by every service (SYSTEM §4.4)."""

from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse


def ok(data: Any, meta: dict[str, Any] | None = None, status: int = 200) -> JSONResponse:
    return JSONResponse(status_code=status,
                        content={"success": True, "data": data, "error": None, "meta": meta or {}})


def fail(status: int, code: str, message: str, meta: dict[str, Any] | None = None
         ) -> JSONResponse:
    return JSONResponse(status_code=status, content={
        "success": False, "data": None, "error": {"code": code, "message": message},
        "meta": meta or {}})
