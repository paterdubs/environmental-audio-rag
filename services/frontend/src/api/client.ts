import type {
  Corpus,
  Envelope,
  Health,
  QueryRequest,
  Recording,
  RecordingDetail,
  RetrievalResult,
  Taxonomy,
} from "./types";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly meta: Record<string, unknown> = {},
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<{ data: T; meta: Record<string, unknown> }> {
  const response = await fetch(path, init);
  let body: Envelope<T>;
  try {
    body = (await response.json()) as Envelope<T>;
  } catch {
    throw new ApiError(response.status, "bad_response", `Máy chủ trả về phản hồi không hợp lệ (${response.status})`);
  }
  if (!body.success || body.data === null) {
    throw new ApiError(response.status, body.error?.code ?? "unknown", body.error?.message ?? "Lỗi không rõ", body.meta);
  }
  return { data: body.data, meta: body.meta };
}

export const api = {
  health: () => request<Health>("/health"),
  taxonomy: () => request<Taxonomy>("/api/v1/taxonomy").then((r) => r.data),
  recordings: (corpus: Corpus, classId: string | null, page: number, limit = 20) => {
    const params = new URLSearchParams({ corpus, page: String(page), limit: String(limit) });
    if (classId) params.set("class_id", classId);
    return request<Recording[]>(`/api/v1/recordings?${params}`);
  },
  recording: (id: string) => request<RecordingDetail>(`/api/v1/recordings/${encodeURIComponent(id)}`).then((r) => r.data),
  upload: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<{ recording_id: string }>("/api/v1/audio/upload", { method: "POST", body: form });
  },
  query: (body: QueryRequest) =>
    request<RetrievalResult>("/api/v1/retrieval/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  audioUrl: (id: string) => `/api/v1/recordings/${encodeURIComponent(id)}/audio`,
};
