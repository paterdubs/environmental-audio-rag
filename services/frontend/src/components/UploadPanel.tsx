import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";

import { api, ApiError } from "../api/client";
import type { Language } from "../api/types";

const ACCEPT = ".wav,.flac,.ogg,.mp3";

export function UploadPanel({ language, onUploaded }: { language: Language; onUploaded: (id: string) => void }) {
  const input = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [elapsed, setElapsed] = useState<number | null>(null);
  const client = useQueryClient();
  const upload = useMutation({
    mutationFn: (file: File) => api.upload(file),
    onSuccess: ({ data }) => {
      client.invalidateQueries({ queryKey: ["recordings"] });
      onUploaded(data.recording_id);
    },
  });
  const send = (file: File | undefined) => {
    if (!file) return;
    const started = performance.now();
    setElapsed(null);
    upload.mutate(file, { onSettled: () => setElapsed((performance.now() - started) / 1000) });
  };
  const vi = language === "vi";
  return (
    <section className="panel upload" aria-labelledby="upload-title">
      <h2 id="upload-title">{vi ? "Tải bản ghi lên" : "Upload a recording"}</h2>
      <button
        type="button"
        className={`dropzone ${dragging ? "is-dragging" : ""} ${upload.isPending ? "is-busy" : ""}`}
        onClick={() => input.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          send(e.dataTransfer.files[0]);
        }}
        disabled={upload.isPending}
      >
        {upload.isPending ? (
          <span className="busy">{vi ? "Đang phân tích… (CPU có thể mất khoảng một phút)" : "Analysing… (CPU may take about a minute)"}</span>
        ) : (
          <>
            <strong>{vi ? "Kéo thả file vào đây" : "Drop a file here"}</strong>
            <span>{vi ? "hoặc bấm để chọn" : "or click to choose"} · WAV, FLAC, OGG, MP3 · ≤ 50 MB · ≤ 10 {vi ? "phút" : "min"}</span>
          </>
        )}
      </button>
      <input ref={input} type="file" accept={ACCEPT} hidden onChange={(e) => send(e.target.files?.[0])} />
      {upload.isError && (
        <p className="notice notice-error" role="alert">
          {upload.error instanceof ApiError ? upload.error.message : String(upload.error)}
        </p>
      )}
      {upload.isSuccess && upload.data.meta.duplicate === true && (
        <p className="notice">{vi ? "File này đã có — mở bản ghi cũ." : "Already uploaded — opened the existing recording."}</p>
      )}
      {elapsed !== null && upload.isSuccess && <p className="muted small">{vi ? `Đã xử lý trong ${elapsed.toFixed(1)} giây.` : `Processed in ${elapsed.toFixed(1)} seconds.`}</p>}
    </section>
  );
}
