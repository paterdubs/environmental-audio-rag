import { describe, expect, it, vi } from "vitest";

import { api, ApiError } from "./client";

const envelope = (data: unknown, success = true) => ({ success, data: success ? data : null, error: success ? null : { code: "query_parser_unavailable", message: "LLM unavailable" }, meta: {} });

describe("natural query API contract", () => {
  it("parses filters then sends the edited filters to query", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(new Response(JSON.stringify(envelope({ filters: { classes_all: ["birds"] }, raw: "{}" }))))
      .mockResolvedValueOnce(new Response(JSON.stringify(envelope({ filters_source: "user", filters_applied: { hard_filters: { classes_all: ["birds"] } }, evidence: [], answer: "ok", question: "birds", documents: [] }))));
    const parsed = await api.parse({ question: "Có tiếng chim không?", language: "vi" });
    await api.query({ question: "Có tiếng chim không?", filters: parsed.data.filters, mode: "hybrid", corpus: "validation", language: "vi", k: 10 });
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(JSON.parse(String(fetchMock.mock.calls[1][1]?.body))).toMatchObject({ filters: { classes_all: ["birds"] } });
    fetchMock.mockRestore();
  });

  it("preserves a clear parser error for manual fallback", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(new Response(JSON.stringify(envelope(null, false)), { status: 503 }));
    await expect(api.parse({ question: "???", language: "en" })).rejects.toMatchObject<ApiError>({ code: "query_parser_unavailable", status: 503 });
    fetchMock.mockRestore();
  });
});
