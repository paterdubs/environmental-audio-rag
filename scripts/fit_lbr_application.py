"""Cấu hình ứng dụng LBR V3 (ADR-0045 §11): rescorer học nhãn giao nhau. Chỉ đọc dev.npz.

V3 không qua luật chọn tầng C (§6) — số chính của luận văn vẫn là V2. Script này đo V3 trên
cùng OOF và cùng fold như tầng C (cross-fit lồng nhau, kiểm chuyển sang OOF P1×3), báo Δ micro
thước chính so với B0 và các thước ứng dụng ADR-0046, rồi fit model cuối trên đủ 5 fold để
mở test cùng lượt với V2. Không đọc test.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from ml.evaluation.application_metrics import RECALL_FIRST_PRECISION_FLOOR
from ml.postprocessing.boundary_refine import LbrConfig
from ml.postprocessing.lbr_crossfit import build_data, crossfit_lbr_multi
from scripts.fit_lbr_oof import (
    POINTS,
    _fmt,
    _strip,
    baseline_events,
    bootstrap,
    build_manifest,
    load,
    objectives,
    save_final,
    score_all,
    sebb_params,
)
from scripts.report_oof import output_name

ROOT = Path(__file__).resolve().parents[1]
VARIANT = "v3"


def run_v3(src: dict, tgt: dict, params, config: LbrConfig) -> dict:
    data = {name: build_data(ctx["probabilities"], ctx["reference"], ctx["folds"],
                             class_ids=ctx["class_ids"], frame_rate=ctx["frame_rate"],
                             params=params, config=config) for name, ctx in (("src", src),
                                                                           ("tgt", tgt))}
    objs = objectives(src)
    events = {"B0": baseline_events(src, params, objs),
              "P1x3": baseline_events(tgt, params, objectives(tgt))}
    out = crossfit_lbr_multi(data["src"], variant=VARIANT, objectives=objs, config=config,
                             targets={"src": data["src"], "tgt": data["tgt"]})
    events["LBR_v3"] = out["src"].events
    events["LBR_v3_on_P1x3"] = out["tgt"].events
    thresholds = {str(k): v for k, v in out["src"].thresholds.items()}
    return {"data": data, "objectives": objs, "events": events, "thresholds": thresholds}


def render(result: dict) -> str:
    res, deltas = result["results"], result["deltas"]
    lines = ["# LBR V3 — cấu hình ứng dụng (ADR-0045 §11, ADR-0046)", "",
             "> OOF 564 recording annotated, 5 fold, cross-fit lồng nhau như tầng C. V3 được tìm "
             "ra **sau** khi xem kết quả tầng C trên chính OOF này (thăm dò 10/11) — không phải "
             "ứng viên ghi trước, không thay V2 làm số chính. Không đọc test.", "",
             "## Thước chính — 21 lớp, điểm F1", "",
             "| Hệ thống | Macro | Micro | Nsys/Nref | Δ micro [95% CI] |",
             "|---|---:|---:|---:|---|"]
    for name, points in res.items():
        m = points["f1"]["all"]
        d = deltas.get(name)
        delta = (f"{d['estimate']:+.4f} [{d['lower']:+.4f}, {d['upper']:+.4f}] vs {d['baseline']}"
                 if d else "—")
        lines.append(f"| {name} | {_fmt(m['macro_f1'])} | {_fmt(m['micro_f1'])} | "
                     f"{m['nsys']}/{m['nref']} | {delta} |")
    for set_name, title in (("all", "21 lớp"), ("vn", "19 lớp Việt Nam")):
        lines += ["", f"## Thước ứng dụng — {title}", "",
                  "| Hệ thống | Điểm | Micro chính | Collar 1 s | Segment 1 s | Giao nhau P | "
                  "Giao nhau R | Giao nhau F1 |", "|---|---|---:|---:|---:|---:|---:|---:|"]
        for name, points in res.items():
            for point in POINTS:
                m = points[point][set_name]
                i = m["intersection"]["micro"]
                lines.append(f"| {name} | {point} | {_fmt(m['micro_f1'])} | "
                             f"{_fmt(m['event_f1_collar_1s']['micro'])} | "
                             f"{_fmt(m['segment_f1_1s']['micro'])} | {_fmt(i['precision'])} | "
                             f"{_fmt(i['recall'])} | {_fmt(i['f1'])} |")
    return "\n".join([*lines, "",
                      f"Sàn precision điểm ưu tiên phát hiện: {RECALL_FIRST_PRECISION_FLOOR}.",
                      f"Ngưỡng theo fold: {result['fold_thresholds']}.", ""])


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="OOF B0 (nguồn train)")
    parser.add_argument("--transfer", type=Path, required=True, help="OOF P1×3 (kiểm chuyển)")
    parser.add_argument("--label", default="B0v3")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "docs/measurements")
    parser.add_argument("--tag", default="LBR_v3")
    parser.add_argument("--runs-dir", type=Path, default=ROOT / "ml/runs",
                        help="chỉ để chạy xem trước khi tree bẩn; run chính thức ở ml/runs")
    args = parser.parse_args()
    now = datetime.now(UTC)
    measurement = args.out_dir / output_name(now, args.tag)
    if measurement.exists() or measurement.with_suffix(".md").exists():
        raise FileExistsError(measurement)
    src, tgt = load(args.source), load(args.transfer)
    if src["recordings"] != tgt["recordings"] or src["folds"] != tgt["folds"]:
        raise ValueError("nguồn và đích kiểm chuyển phải cùng recording và fold")
    params, config = sebb_params(args.source), LbrConfig()
    run = run_v3(src, tgt, params, config)
    results = score_all(src, tgt, run["events"])
    deltas = bootstrap(results, [("B0", "LBR_v3"), ("P1x3", "LBR_v3_on_P1x3")])
    out = args.runs_dir / f"sed_lbr_{args.label}_{now:%Y%m%dT%H%M%SZ}"
    out.mkdir(parents=True)
    model_sha = save_final(out, run, VARIANT, src, params, config)
    manifest = build_manifest(out, src, tgt, params, config, VARIANT, model_sha)
    manifest["command"] = ["python", "-m", "scripts.fit_lbr_application", *sys.argv[1:]]
    manifest["config"]["role"] = "application"
    manifest["config"]["decision"] = "ADR-0045 §11"
    result = {"run": out.name, "variant": VARIANT, "role": "application", "deltas": deltas,
              "results": _strip(results), "git": manifest["git"],
              "fold_thresholds": run["thresholds"]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    payload = json.dumps(result, ensure_ascii=False, indent=2, default=float)
    (out / "lbr_application_annotated.json").write_text(payload, encoding="utf-8")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    measurement.write_text(payload, encoding="utf-8")
    measurement.with_suffix(".md").write_text(render(result), encoding="utf-8")
    print(measurement)


if __name__ == "__main__":
    main()
