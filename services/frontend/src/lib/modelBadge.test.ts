import { describe, expect, it } from "vitest";

import type { ModelsStatus } from "../api/types";
import { describeModel } from "./modelBadge";

const base: ModelsStatus = {
  model_version: "x",
  members: [],
  served_run: "ml/runs/sed_served_B0_20261107T175659Z",
  official: true,
  postproc: "sebb",
  threshold_mode: "csebb",
  taxonomy_version: "1",
  taxonomy_sha256: "abc",
  device: "cpu",
};

describe("describeModel", () => {
  it("names the LBR variant and operating point read from the status payload", () => {
    const status = {
      ...base,
      official: false,
      lbr_run: "ml/runs/sed_lbr_B0v3_20261110T042337Z",
      operating_point: "recall_first",
    };
    const vi = describeModel(status, "vi");
    expect(vi.demo).toBe(true);
    expect(vi.text).toContain("LBR V3");
    expect(vi.text).toContain("ưu tiên phát hiện");
    expect(vi.text).not.toContain("SED v2");
    expect(describeModel(status, "en").text).toContain("detection-first");
  });

  it("falls back to V2 for an LBR run without a version tag and to the f1 point", () => {
    const status = {
      ...base,
      official: false,
      lbr_run: "ml/runs/sed_lbr_B0_20261109T172809Z",
      operating_point: "f1",
    };
    const { text } = describeModel(status, "vi");
    expect(text).toContain("LBR V2");
    expect(text).toContain("điểm F1");
  });

  it("marks the frozen B0 system as official only when the backend says so", () => {
    const official = describeModel(base, "en");
    expect(official.demo).toBe(false);
    expect(official.text).toContain("B0");
    expect(official.text).toContain("official");
    expect(describeModel({ ...base, official: false }, "vi").demo).toBe(true);
  });

  it("names the f2 ensemble from the served run instead of hardcoding it", () => {
    const status = { ...base, served_run: "ml/runs/sed_ensemble_t2b_20260927T200914Z" };
    expect(describeModel(status, "vi").text).toContain("f2");
  });

  it("never claims a system when the run name is unknown", () => {
    const status = { ...base, official: false, served_run: "ml/runs/mystery_run" };
    expect(describeModel(status, "en").text).toContain("mystery_run");
  });
});
