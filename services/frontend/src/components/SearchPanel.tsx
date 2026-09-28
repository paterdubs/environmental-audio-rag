import { useMutation } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import { api, ApiError } from "../api/client";
import type { Corpus, Filters, Language, Mode, Temporal } from "../api/types";
import { formatSeconds } from "../lib/timeline";
import type { TaxonomyView } from "../lib/useTaxonomy";

type Kind = "classes" | "temporal" | "duration";
const PREDICATES: { id: Temporal["predicate"]; vi: string; en: string }[] = [
  { id: "before", vi: "xảy ra trước", en: "before" }, { id: "after", vi: "xảy ra sau", en: "after" },
  { id: "overlaps", vi: "chồng lấp với", en: "overlaps" }, { id: "within", vi: "nằm trong", en: "within" },
];
interface Props { corpus: Corpus; language: Language; taxonomy: TaxonomyView; onOpen: (recordingId: string, seconds: number) => void; }
function ClassSelect({ value, onChange, taxonomy, language }: { value: string; onChange: (v: string) => void; taxonomy: TaxonomyView; language: Language }) {
  return <select value={value} onChange={(e) => onChange(e.target.value)}>{taxonomy.classes.map((c) => <option key={c.class_id} value={c.class_id}>{language === "vi" ? c.label_vi : c.label_en}</option>)}</select>;
}

export function SearchPanel({ corpus, language, taxonomy, onOpen }: Props) {
  const first = taxonomy.order[0] ?? ""; const [question, setQuestion] = useState("");
  const [kind, setKind] = useState<Kind>("temporal"); const [a, setA] = useState(first); const [b, setB] = useState(taxonomy.order[1] ?? first);
  const [predicate, setPredicate] = useState<Temporal["predicate"]>("before"); const [minS, setMinS] = useState(10); const [mode, setMode] = useState<Mode>("hybrid");
  const [natural, setNatural] = useState(true); const [parsed, setParsed] = useState<Filters | null>(null);
  const parse = useMutation({ mutationFn: api.parse }); const search = useMutation({ mutationFn: api.query }); const vi = language === "vi";
  const manualFilters = (): Filters => kind === "classes" ? { classes_all: a === b ? [a] : [a, b] } : kind === "temporal" ? { temporal: { predicate, a, b, tolerance_s: 0 } } : { duration: { class_id: a, min_s: minS } };
  const runQuery = (filters: Filters) => search.mutate({ question: question.trim() || `${taxonomy.name(a, language)} · ${taxonomy.name(b, language)}`, filters, mode, corpus, language, k: 10 });
  const parseQuestion = async (event: FormEvent) => { event.preventDefault(); if (!question.trim()) return; try { setParsed((await parse.mutateAsync({ question: question.trim(), language })).data.filters); } catch { setNatural(false); setParsed(null); } };
  const submitManual = (event: FormEvent) => { event.preventDefault(); runQuery(manualFilters()); };
  const label = (id: string) => taxonomy.name(id, language); const displayFilters = parsed ?? manualFilters();
  const removeClass = (id: string) => setParsed((current) => current ? { ...current, classes_all: current.classes_all?.filter((c) => c !== id) } : current);
  const updateTemporal = (next: Partial<Temporal>) => setParsed((current) => current?.temporal ? { ...current, temporal: { ...current.temporal, ...next } } : current);
  return <section className="panel search" aria-labelledby="search-title"><h2 id="search-title">{vi ? "Truy vấn tự nhiên" : "Natural-language search"}</h2>
    <form onSubmit={natural ? parseQuestion : submitManual} className="search-form">
      <input className="question" value={question} maxLength={500} onChange={(e) => setQuestion(e.target.value)} placeholder={vi ? "Ví dụ: có tiếng chim trước tiếng còi xe không?" : "e.g. were there birds before a horn?"} />
      <div className="filter-row"><button type="button" className={natural ? "primary" : ""} aria-pressed={natural} onClick={() => setNatural(true)}>{vi ? "Câu hỏi" : "Question"}</button><button type="button" className={!natural ? "primary" : ""} aria-pressed={!natural} onClick={() => setNatural(false)}>{vi ? "Bộ lọc thủ công" : "Manual filters"}</button></div>
      {!natural && <><div className="segmented" role="radiogroup" aria-label={vi ? "Loại bộ lọc" : "Filter type"}>{(["temporal", "classes", "duration"] as const).map((k) => <button key={k} type="button" aria-pressed={kind === k} onClick={() => setKind(k)}>{k === "temporal" ? (vi ? "Thứ tự thời gian" : "Temporal") : k === "classes" ? (vi ? "Cùng có mặt" : "Co-occur") : vi ? "Kéo dài" : "Duration"}</button>)}</div>
        <div className="filter-row"><ClassSelect value={a} onChange={setA} taxonomy={taxonomy} language={language} />{kind === "temporal" && <select value={predicate} onChange={(e) => setPredicate(e.target.value as Temporal["predicate"])}>{PREDICATES.map((p) => <option key={p.id} value={p.id}>{vi ? p.vi : p.en}</option>)}</select>}{kind === "classes" && <span className="joiner">{vi ? "và" : "and"}</span>}{kind !== "duration" ? <ClassSelect value={b} onChange={setB} taxonomy={taxonomy} language={language} /> : <label className="inline">{vi ? "dài hơn" : "longer than"}<input type="number" min={1} max={600} value={minS} onChange={(e) => setMinS(Number(e.target.value))} /> s</label>}</div></>}
      {natural && parsed && <div className="parsed-filters" aria-live="polite"><p className="muted small">{vi ? "Bộ lọc đã hiểu — có thể sửa trước khi tìm:" : "Understood filters — edit before searching:"}</p>{parsed.classes_all?.map((id) => <span className="filter-chip" key={id}><span className="swatch" style={{ background: taxonomy.color(id) }} />{label(id)}<button type="button" aria-label={`${vi ? "Xoá" : "Remove"} ${label(id)}`} onClick={() => removeClass(id)}>×</button></span>)}{parsed.temporal && <span className="filter-chip"><span>{label(parsed.temporal.a)}</span><select aria-label="predicate" value={parsed.temporal.predicate} onChange={(e) => updateTemporal({ predicate: e.target.value as Temporal["predicate"] })}>{PREDICATES.map((p) => <option key={p.id} value={p.id}>{vi ? p.vi : p.en}</option>)}</select><span>{label(parsed.temporal.b)}</span><button type="button" aria-label={vi ? "Xoá bộ lọc thời gian" : "Remove temporal filter"} onClick={() => setParsed((current) => current ? { ...current, temporal: undefined } : current)}>×</button></span>}{parsed.duration && <span className="filter-chip">{label(parsed.duration.class_id)} ≥ {parsed.duration.min_s}s<button type="button" aria-label={vi ? "Xoá bộ lọc thời lượng" : "Remove duration filter"} onClick={() => setParsed((current) => current ? { ...current, duration: undefined } : current)}>×</button></span>}<button type="button" className="primary" disabled={search.isPending || Object.keys(displayFilters).length === 0} onClick={() => runQuery(displayFilters)}>{search.isPending ? (vi ? "Đang tìm…" : "Searching…") : vi ? "Chạy truy vấn" : "Run query"}</button></div>}
      <div className="filter-row"><select value={mode} onChange={(e) => setMode(e.target.value as Mode)} aria-label="mode"><option value="hybrid">hybrid</option><option value="structured_only">structured_only</option></select>{!natural && <button type="submit" className="primary" disabled={search.isPending}>{search.isPending ? (vi ? "Đang tìm…" : "Searching…") : vi ? "Tìm" : "Search"}</button>}{natural && parse.isPending && <span className="muted" role="status">{vi ? "Đang hiểu câu hỏi…" : "Understanding question…"}</span>}</div>
    </form>
    {parse.isError && <p className="notice notice-error" role="alert">{vi ? "Không hiểu được câu hỏi; hãy chọn bộ lọc thủ công." : "Could not parse the question; choose manual filters."} {parse.error instanceof ApiError ? parse.error.message : ""}</p>}
    {search.isError && <p className="notice notice-error" role="alert">{search.error instanceof ApiError ? search.error.message : String(search.error)}</p>}
    {search.data?.data && <div className="answer" aria-live="polite"><p>{search.data.data.answer}</p><ol className="evidence">{search.data.data.evidence.map((e) => <li key={`${e.recording_id}-${e.event_id}`}><button type="button" onClick={() => onOpen(e.recording_id, e.onset_s)}><span className="swatch" style={{ background: taxonomy.color(e.class_id) }} /><code>{e.recording_id}</code><span>{taxonomy.name(e.class_id, language)}</span><span className="mono muted">{formatSeconds(e.onset_s, language)}–{formatSeconds(e.offset_s, language)} s</span></button></li>)}</ol><p className="muted small">{vi ? "Bộ lọc đã áp" : "Filters applied"}: <code>{JSON.stringify(search.data.data.filters_applied.hard_filters)}</code> · {search.data.data.filters_source === "parsed" ? (vi ? "từ parser" : "parsed") : (vi ? "do người dùng" : "user")} · corpus {corpus}</p></div>}
  </section>;
}
