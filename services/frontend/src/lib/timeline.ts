// Pure helpers for the timeline and caption views — no React, unit-tested.

import type { Evidence, Language, SedEvent } from "../api/types";

export interface Lane {
  classId: string;
  events: SedEvent[];
}

/** One lane per class that actually occurs, in taxonomy order (never a hard-coded list). */
export function buildLanes(events: SedEvent[], classOrder: string[]): Lane[] {
  const byClass = new Map<string, SedEvent[]>();
  for (const event of events) {
    const list = byClass.get(event.class_id) ?? [];
    list.push(event);
    byClass.set(event.class_id, list);
  }
  const order = new Map(classOrder.map((id, index) => [id, index]));
  return [...byClass.entries()]
    .sort(([a], [b]) => (order.get(a) ?? Infinity) - (order.get(b) ?? Infinity) || a.localeCompare(b))
    .map(([classId, list]) => ({ classId, events: [...list].sort((x, y) => x.onset_s - y.onset_s) }));
}

/** Evenly spread, perceptually uniform hues keyed by the class's taxonomy index. */
export function classColor(index: number): string {
  const hue = (index * 137.508) % 360;
  return `oklch(64% 0.14 ${hue.toFixed(1)})`;
}

export function percent(seconds: number, duration: number): number {
  if (duration <= 0) return 0;
  return Math.min(100, Math.max(0, (seconds / duration) * 100));
}

/** Seconds with one decimal; Vietnamese uses a decimal comma like the VI captions. */
export function formatSeconds(seconds: number, language: Language): string {
  const text = seconds.toFixed(1);
  return language === "vi" ? text.replace(".", ",") : text;
}

export function formatClock(seconds: number): string {
  const whole = Math.max(0, Math.floor(seconds));
  const minutes = Math.floor(whole / 60);
  return `${minutes}:${String(whole % 60).padStart(2, "0")}`;
}

export interface Segment {
  text: string;
  eventId: number | null;
}

/**
 * Split a caption into plain text and mentions, each mention tied to the event it is
 * grounded in (caption_evidence.mention_span). Overlapping or out-of-range spans are
 * skipped rather than trusted.
 */
export function captionSegments(text: string, evidence: Evidence[]): Segment[] {
  const spans = [...evidence]
    .filter(({ mention_span: [start, end] }) => start >= 0 && end <= text.length && start < end)
    .sort((a, b) => a.mention_span[0] - b.mention_span[0]);
  const segments: Segment[] = [];
  let cursor = 0;
  for (const { event_id, mention_span: [start, end] } of spans) {
    if (start < cursor) continue;
    if (start > cursor) segments.push({ text: text.slice(cursor, start), eventId: null });
    segments.push({ text: text.slice(start, end), eventId: event_id });
    cursor = end;
  }
  if (cursor < text.length) segments.push({ text: text.slice(cursor), eventId: null });
  return segments;
}
