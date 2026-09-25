// Shapes returned by services/api (ADR-0029 §5). Every response is an envelope.

export interface Envelope<T> {
  success: boolean;
  data: T | null;
  error: { code: string; message: string } | null;
  meta: Record<string, unknown>;
}

export type Corpus = "upload" | "validation" | "test";
export type Language = "vi" | "en";
export type Mode = "hybrid" | "structured_only";

export interface TaxonomyClass {
  class_id: string;
  label_en: string;
  label_vi: string;
}

export interface Taxonomy {
  version: string;
  sha256: string;
  classes: TaxonomyClass[];
}

export interface Recording {
  recording_id: string;
  source_dataset: string;
  source_id: string;
  duration_s: number;
  sample_rate: number;
  channels: number;
  sha256: string;
  split: string | null;
  ingested_at: string;
  audio_path: string | null;
}

export interface SedEvent {
  event_id: number;
  class_id: string;
  onset_s: number;
  offset_s: number;
  score: number;
  provenance: string;
  model_version: string | null;
  taxonomy_version: string;
}

export interface Evidence {
  event_id: number;
  mention_span: [number, number];
}

export interface Caption {
  caption_id: number;
  language: Language;
  text: string;
  captioner_version: string;
  grounding_mode: string;
  evidence: Evidence[];
}

export interface RecordingDetail {
  recording: Recording;
  events: SedEvent[];
  captions: Caption[];
  model_versions: string[];
  taxonomy_versions: string[];
}

export interface Temporal {
  predicate: "before" | "after" | "overlaps" | "within";
  a: string;
  b: string;
  tolerance_s: number;
}

export interface Filters {
  classes_all?: string[];
  temporal?: Temporal;
  duration?: { class_id: string; min_s: number };
}

export interface QueryRequest {
  question: string;
  filters: Filters;
  mode: Mode;
  corpus: Corpus;
  language: Language;
  k: number;
}

export interface AnswerEvidence {
  recording_id: string;
  event_id: number;
  class_id: string;
  onset_s: number;
  offset_s: number;
}

export interface RetrievalResult {
  question: string;
  answer: string;
  evidence: AnswerEvidence[];
  filters_applied: { mode: Mode; hard_filters: Filters; k: number; language: Language };
  documents: { recording_id: string; score: number }[];
}

export interface Health {
  status: string;
  database: boolean;
  inference: boolean;
  model_version: string | null;
}
