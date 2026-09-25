import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { api } from "../api/client";
import type { Corpus, Language } from "../api/types";
import { formatClock } from "../lib/timeline";
import type { TaxonomyView } from "../lib/useTaxonomy";

const CORPORA: { id: Corpus; vi: string; en: string }[] = [
  { id: "upload", vi: "Đã tải lên", en: "Uploads" },
  { id: "validation", vi: "Dev (benchmark)", en: "Dev (benchmark)" },
  { id: "test", vi: "Test (benchmark)", en: "Test (benchmark)" },
];
const PAGE = 12;

interface Props {
  corpus: Corpus;
  selected: string | null;
  language: Language;
  taxonomy: TaxonomyView | undefined;
  onCorpus: (corpus: Corpus) => void;
  onSelect: (id: string) => void;
}

export function RecordingList({ corpus, selected, language, taxonomy, onCorpus, onSelect }: Props) {
  const [classId, setClassId] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const list = useQuery({
    queryKey: ["recordings", corpus, classId, page],
    queryFn: () => api.recordings(corpus, classId, page, PAGE),
    placeholderData: keepPreviousData,
  });
  const total = Number(list.data?.meta.total ?? 0);
  const pages = Math.max(1, Math.ceil(total / PAGE));
  const vi = language === "vi";
  return (
    <section className="panel list" aria-labelledby="list-title">
      <div className="panel-head">
        <h2 id="list-title">{vi ? "Bản ghi" : "Recordings"}</h2>
        <span className="count">{total}</span>
      </div>
      <div className="tabs" role="tablist">
        {CORPORA.map((c) => (
          <button
            key={c.id}
            role="tab"
            type="button"
            aria-selected={corpus === c.id}
            onClick={() => {
              setPage(1);
              onCorpus(c.id);
            }}
          >
            {vi ? c.vi : c.en}
          </button>
        ))}
      </div>
      <label className="field">
        <span>{vi ? "Có lớp" : "Contains class"}</span>
        <select
          value={classId ?? ""}
          onChange={(e) => {
            setPage(1);
            setClassId(e.target.value || null);
          }}
        >
          <option value="">{vi ? "— mọi lớp —" : "— any class —"}</option>
          {taxonomy?.classes.map((c) => (
            <option key={c.class_id} value={c.class_id}>
              {vi ? c.label_vi : c.label_en}
            </option>
          ))}
        </select>
      </label>
      {list.isError && <p className="notice notice-error">{String(list.error)}</p>}
      <ol className="recordings">
        {list.data?.data.map((r) => (
          <li key={r.recording_id}>
            <button type="button" aria-current={selected === r.recording_id} onClick={() => onSelect(r.recording_id)}>
              <code>{r.recording_id.replace(/^upload:/, "↑ ").slice(0, 22)}</code>
              <span className="muted">{formatClock(r.duration_s)}</span>
            </button>
          </li>
        ))}
        {list.data && list.data.data.length === 0 && (
          <li className="empty">{vi ? "Chưa có bản ghi nào." : "No recordings yet."}</li>
        )}
      </ol>
      {pages > 1 && (
        <div className="pager">
          <button type="button" disabled={page <= 1} onClick={() => setPage(page - 1)}>
            ←
          </button>
          <span>
            {page} / {pages}
          </span>
          <button type="button" disabled={page >= pages} onClick={() => setPage(page + 1)}>
            →
          </button>
        </div>
      )}
    </section>
  );
}
