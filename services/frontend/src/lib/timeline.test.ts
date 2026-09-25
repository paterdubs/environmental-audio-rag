import { describe, expect, it } from "vitest";

import type { SedEvent } from "../api/types";
import { buildLanes, captionSegments, formatClock, formatSeconds, percent } from "./timeline";

const event = (event_id: number, class_id: string, onset_s: number, offset_s: number): SedEvent => ({
  event_id,
  class_id,
  onset_s,
  offset_s,
  score: 0.9,
  provenance: "prediction",
  model_version: "m",
  taxonomy_version: "0.1",
});

describe("buildLanes", () => {
  it("keeps only occurring classes, in taxonomy order, events sorted by onset", () => {
    const lanes = buildLanes([event(1, "horn", 5, 6), event(2, "birds", 3, 4), event(3, "horn", 1, 2)], [
      "bells",
      "birds",
      "horn",
    ]);
    expect(lanes.map((l) => l.classId)).toEqual(["birds", "horn"]);
    expect(lanes[1].events.map((e) => e.event_id)).toEqual([3, 1]);
  });
});

describe("captionSegments", () => {
  it("ties each mention to its evidence event and keeps the rest as plain text", () => {
    const text = "Birds from 1.0 to 2.0 seconds.";
    const segments = captionSegments(text, [{ event_id: 7, mention_span: [0, 5] }]);
    expect(segments).toEqual([
      { text: "Birds", eventId: 7 },
      { text: " from 1.0 to 2.0 seconds.", eventId: null },
    ]);
    expect(segments.map((s) => s.text).join("")).toBe(text);
  });

  it("skips spans that overlap or fall outside the text", () => {
    const segments = captionSegments("abcdef", [
      { event_id: 1, mention_span: [0, 3] },
      { event_id: 2, mention_span: [2, 4] },
      { event_id: 3, mention_span: [5, 99] },
    ]);
    expect(segments.filter((s) => s.eventId !== null).map((s) => s.eventId)).toEqual([1]);
    expect(segments.map((s) => s.text).join("")).toBe("abcdef");
  });
});

describe("formatting", () => {
  it("uses a decimal comma in Vietnamese and clamps percentages", () => {
    expect(formatSeconds(12.34, "vi")).toBe("12,3");
    expect(formatSeconds(12.34, "en")).toBe("12.3");
    expect(formatClock(125.9)).toBe("2:05");
    expect(percent(-1, 10)).toBe(0);
    expect(percent(20, 10)).toBe(100);
  });
});
