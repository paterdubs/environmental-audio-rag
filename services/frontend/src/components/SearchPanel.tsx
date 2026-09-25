import { useMutation } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";

import { api, ApiError } from "../api/client";
import type { Corpus, Filters, Language, Mode, Temporal } from "../api/types";
import { formatSeconds } from "../lib/timeline";
import type { TaxonomyView } from "../lib/useTaxonomy";

type Kind = "classes" | "temporal" | "duration";
const PREDICATES: { id: Temporal["predicate"]; vi: string; en: string }[] = [
  { id: "before", vi: "xảy ra trước", en: "before" },
  { id: "after", vi: "xảy ra sau", en: "after" },
  { id: "overlaps", vi: "chồng lấp với", en: "overlaps" },
  { id: "within", vi: "nằm trong", en: "within" },
];

interface Props {
  corpus: Corpus;
  language: Language;
  taxonomy: TaxonomyView;
  onOpen: (recordingId: string, seconds: number) => void;
}

function ClassSelect({ value, onChange, taxonomy, language }: {
  value: string;
  onChange: (v: string) => void;
  taxonomy: TaxonomyView;
  language: Language;
}) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)}>
      {taxonomy.classes.map((c) => (
        <option key={c.class_id} value={c.class_id}>
          {language === "vi" ? c.label_vi : c.label_en}
        </option>
      ))}
    </select>
  );
}

export function SearchPanel({ corpus, language, taxonomy, onOpen }: Props) {
  const first = taxonomy.order[0];
  const [question, setQuestion] = useState("");
  const [kind, setKind] = useState<Kind>("temporal");
  const [a, setA] = useState(first);
  const [b, setB] = useState(taxonomy.order[1] ?? first);
  const [predicate, setPredicate] = useState<Temporal["predicate"]>("before");
  const [minS, setMinS] = useState(10);
  const [mode, setMode] = useState<Mode>("hybrid");
  const search = useMutation({ mutationFn: api.query });
  const vi = language === "vi";

  const filters = (): Filters =>
    kind === "classes"
      ? { classes_all: a === b ? [a] : [a, b] }
      : kind === "temporal"
        ? { temporal: { predicate, a, b, tolerance_s: 0 } }
        : { duration: { class_id: a, min_s: minS } };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const text = question.trim() || `${taxonomy.name(a, language)} · ${taxonomy.name(b, language)}`;
    search.mutate({ question: text, filters: filters(), mode, corpus, language, k: 10 });
  };

  const result = search.data?.data;
  return (
    <section className="panel search" aria-labelledby="search-title">
      <h2 id="search-title">{vi ? "Truy vấn lịch sử" : "Query the history"}</h2>
      <form onSubmit={submit} className="search-form">
        <input
          className="question"
          value={question}
          maxLength={500}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={vi ? "Ví dụ: có tiếng chim trước tiếng còi xe không?" : "e.g. were there birds before a horn?"}
        />
        <div className="segmented" role="radiogroup" aria-label={vi ? "Loại bộ lọc" : "Filter type"}>
          {(["temporal", "classes", "duration"] as const).map((k) => (
            <button key={k} type="button" aria-pressed={kind === k} onClick={() => setKind(k)}>
              {k === "temporal" ? (vi ? "Thứ tự thời gian" : "Temporal") : k === "classes" ? (vi ? "Cùng có mặt" : "Co-occur") : vi ? "Kéo dài" : "Duration"}
            </button>
          ))}
        </div>
        <div className="filter-row">
          <ClassSelect value={a} onChange={setA} taxonomy={taxonomy} language={language} />
          {kind === "temporal" && (
            <select value={predicate} onChange={(e) => setPredicate(e.target.value as Temporal["predicate"])}>
              {PREDICATES.map((p) => (
                <option key={p.id} value={p.id}>
                  {vi ? p.vi : p.en}
                </option>
              ))}
            </select>
          )}
          {kind === "classes" && <span className="joiner">{vi ? "và" : "and"}</span>}
          {kind !== "duration" ? (
            <ClassSelect value={b} onChange={setB} taxonomy={taxonomy} language={language} />
          ) : (
            <label className="inline">
              {vi ? "dài hơn" : "longer than"}
              <input type="number" min={1} max={600} value={minS} onChange={(e) => setMinS(Number(e.target.value))} /> s
            </label>
          )}
        </div>
        <div className="filter-row">
          <select value={mode} onChange={(e) => setMode(e.target.value as Mode)} aria-label="mode">
            <option value="hybrid">hybrid</option>
            <option value="structured_only">structured_only</option>
          </select>
          <button type="submit" className="primary" disabled={search.isPending}>
            {search.isPending ? (vi ? "Đang tìm…" : "Searching…") : vi ? "Tìm" : "Search"}
          </button>
        </div>
      </form>
      {search.isError && (
        <p className="notice notice-error" role="alert">
          {search.error instanceof ApiError ? search.error.message : String(search.error)}
        </p>
      )}
      {result && (
        <div className="answer" aria-live="polite">
          <p>{result.answer}</p>
          <ol className="evidence">
            {result.evidence.map((e) => (
              <li key={`${e.recording_id}-${e.event_id}`}>
                <button type="button" onClick={() => onOpen(e.recording_id, e.onset_s)}>
                  <span className="swatch" style={{ background: taxonomy.color(e.class_id) }} />
                  <code>{e.recording_id}</code>
                  <span>{taxonomy.name(e.class_id, language)}</span>
                  <span className="mono muted">
                    {formatSeconds(e.onset_s, language)}–{formatSeconds(e.offset_s, language)} s
                  </span>
                </button>
              </li>
            ))}
          </ol>
          <p className="muted small">
            {vi ? "Bộ lọc đã áp" : "Filters applied"}: <code>{JSON.stringify(result.filters_applied.hard_filters)}</code> · {result.filters_applied.mode} · corpus {corpus}
          </p>
        </div>
      )}
    </section>
  );
}
