import { describe, expect, it } from "vitest";
import { cleanFilters, hasFilters } from "./searchFilters";

describe("edited search filters", () => {
  it("prevents a query when the last class or predicate is removed", () => {
    expect(hasFilters({ classes_all: [] })).toBe(false);
    expect(hasFilters({ temporal: undefined, duration: undefined })).toBe(false);
  });

  it("keeps a duration query valid when its last class chip is removed", () => {
    const duration = { class_id: "birds", min_s: 10 };
    expect(cleanFilters({ classes_all: [], duration })).toEqual({ duration });
    expect(hasFilters({ classes_all: [], duration })).toBe(true);
  });
});
