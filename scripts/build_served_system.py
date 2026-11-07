"""O6 (ADR-0041 §12): package the final SED system for serving.

    .venv/Scripts/python.exe -m scripts.build_served_system --label B0 \\
        --members ml/runs/<fold0> ... ml/runs/<fold4> --hop-seconds 5 --weighting triangular:0.3 \\
        --postproc ml/runs/sed_oof_B0_h5_<ts>/sebb_cv_selection_annotated.json \\
        --evaluated ml/runs/sed_ensemble_B0_final_test_<ts>

Writes `ml/runs/sed_served_<label>_<ts>/` with a manifest `ServedSed` reads (`config.members`,
`config.serving`) and a byte-identical copy of the frozen post-processing file, whose SHA-256 is
recorded next to the source path. `--evaluated` names the test ensemble that was measured with this
exact configuration; parity (`scripts.check_inference_parity --reference-run`) compares to it.
No model is trained or re-selected.
"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

from ml.evaluation.predictions import triangular_floor
from ml.provenance import git_state
from ml.training.common import sha256_file

ROOT = Path(__file__).resolve().parents[1]
SHARED = ("split_sha256", "data_manifest_sha256", "taxonomy_sha256")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--label", required=True)
    parser.add_argument("--members", nargs="+", type=Path, required=True)
    parser.add_argument("--hop-seconds", type=float, required=True)
    parser.add_argument("--weighting", required=True)
    parser.add_argument("--postproc", type=Path, required=True)
    parser.add_argument("--evaluated", type=Path, required=True)
    return parser.parse_args()


def check_members(members: list[Path]) -> list[dict]:
    manifests = [json.loads((m / "manifest.json").read_text(encoding="utf-8")) for m in members]
    for member, manifest in zip(members, manifests, strict=True):
        if not manifest.get("complete") or manifest["git"]["dirty"]:
            raise SystemExit(f"{member}: chưa hoàn tất hoặc train trên tree bẩn")
        if not (member / "checkpoints" / "best.pt").exists():
            raise SystemExit(f"{member}: thiếu checkpoints/best.pt")
        if any(manifest.get(k) != manifests[0].get(k) for k in SHARED):
            raise SystemExit(f"{member}: khác dữ liệu với member đầu")
    return manifests


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    triangular_floor(args.weighting)
    manifests = check_members(args.members)
    if len({m.parent.resolve() for m in args.members}) != 1:
        raise SystemExit("mọi member phải nằm cùng thư mục runs")
    out = args.members[0].parent / f"sed_served_{args.label}_{datetime.now(UTC):%Y%m%dT%H%M%SZ}"
    out.mkdir()
    shutil.copyfile(args.postproc, out / args.postproc.name)
    manifest = {
        "run_id": out.name, "task": "sed_served", "complete": True,
        "command": ["python", "-m", "scripts.build_served_system", *sys.argv[1:]],
        "class_ids": manifests[0]["class_ids"], **{k: manifests[0][k] for k in SHARED},
        "config": {
            "members": [m.name for m in args.members],
            "serving": {"hop_seconds": args.hop_seconds, "window_weighting": args.weighting},
            "postproc_source": str(args.postproc), "postproc_name": args.postproc.name,
            "postproc_sha256": sha256_file(args.postproc),
            "evaluated_run": args.evaluated.name,
            "members_cv_fold": [m["config"].get("cv_fold") for m in manifests],
        },
        "environment": {"python": platform.python_version()},
        "git": git_state(ROOT),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"run_dir": str(out)}, indent=1))


if __name__ == "__main__":
    main()
