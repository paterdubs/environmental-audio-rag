import { useQuery } from "@tanstack/react-query";

import { api, ApiError } from "../api/client";
import type { Health, Language, ModelsStatus } from "../api/types";

const TEXT = {
  vi: { ready: "Sẵn sàng", down: "Chưa sẵn sàng", db: "CSDL", model: "Mô hình" },
  en: { ready: "Ready", down: "Not ready", db: "DB", model: "Model" },
};

export function StatusBar({ language, onLanguage }: { language: Language; onLanguage: (l: Language) => void }) {
  const health = useQuery({
    queryKey: ["health"],
    queryFn: async (): Promise<Health> => {
      try {
        return (await api.health()).data;
      } catch (error) {
        // 503 still carries the component breakdown in meta
        if (error instanceof ApiError) return { status: "not_ready", ...(error.meta as Omit<Health, "status">) };
        throw error;
      }
    },
    refetchInterval: 15_000,
  });
  const models = useQuery({ queryKey: ["models"], queryFn: async (): Promise<ModelsStatus> => (await api.models()).data, refetchInterval: 15_000 });
  const t = TEXT[language];
  const data = health.data;
  const ready = data?.status === "ready";
  return (
    <header className="statusbar">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true" />
        <div>
          <h1>{language === "vi" ? "Sổ âm thanh môi trường" : "Environmental sound log"}</h1>
          <p className="brand-sub">
            {language === "vi"
              ? "Phát hiện sự kiện · mô tả có bằng chứng · truy vấn có trích dẫn"
              : "Event detection · grounded captions · cited retrieval"}
          </p>
        </div>
      </div>
      <div className="status-cluster">
        <span className={`pill ${ready ? "pill-ok" : "pill-warn"}`} role="status">
          <span className="dot" />
          {ready ? t.ready : t.down}
          {data && (
            <span className="pill-detail">
              {t.db} {data.database ? "✓" : "✗"} · {t.model} {data.inference ? "✓" : "✗"}
            </span>
          )}
        </span>
        {data?.model_version && <code className="provenance" title="model_version">{data.model_version}</code>}
        {models.data && <span className={`model-badge ${models.data.official ? "" : "demo"}`} role="status">{models.data.official ? models.data.model_version : (language === "vi" ? "Demo — SED v2, chưa phải hệ thống chính thức" : "Demo — SED v2, not the official system")}</span>}
        <div className="segmented" role="group" aria-label="Ngôn ngữ / Language">
          {(["vi", "en"] as const).map((lang) => (
            <button key={lang} type="button" aria-pressed={language === lang} onClick={() => onLanguage(lang)}>
              {lang.toUpperCase()}
            </button>
          ))}
        </div>
      </div>
    </header>
  );
}
