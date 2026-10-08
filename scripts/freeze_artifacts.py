"""Đóng băng danh mục artifact dùng trong báo cáo.

    .venv/Scripts/python.exe -m scripts.freeze_artifacts

Script chỉ đọc artifact đã có.  Với thư mục cache BGE-M3, SHA-256 được tính trên
cây file theo thứ tự tên (đường dẫn tương đối, kích thước và nội dung từng file),
để có một định danh ổn định mà không giả vờ cache là một tệp đơn lẻ.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from ml.provenance import git_state
from scripts.report_test_ledger import run_details

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "ml" / "runs"
MEASUREMENTS = ROOT / "docs" / "measurements"

# Các tên này là các hệ thống/ensemble được trích trong các bảng kết quả.
REPORT_RUNS = {
    "v1 A (scratch)": "sed_polyphonic_20260923T173234Z",
    "v1 B (AudioSet)": "sed_polyphonic_20260924T054531Z",
    "v1 C (AudioSet→DataSEC)": "sed_polyphonic_20260924T061000Z",
    "v1 ensemble C": "sed_ensemble_C_clean_20260925T045631Z",
    "v2 B": "sed_polyphonic_20260926T033312Z",
    "v2 ensemble B": "sed_ensemble_v2_20260926T155630Z",
    "C-v2 ensemble": "sed_ensemble_cv2_20260926T205405Z",
    "T2a ensemble": "sed_ensemble_t2a_20260927T141952Z",
    "T2b ensemble (served f2 source)": "sed_ensemble_t2b_20260927T200914Z",
    "S11 focal ensemble": "sed_ensemble_s11_focal_t2b_20260928T185207Z",
    "S13 f2 test output": "sed_ensemble_s13_f2_20260929T045053Z",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_tree(path: Path) -> tuple[str, int, int]:
    """Hash deterministic một thư mục; trả hash, số file và tổng byte."""
    digest = hashlib.sha256()
    files = sorted(p for p in path.rglob("*") if p.is_file())
    total = 0
    for file in files:
        relative = file.relative_to(path).as_posix().encode("utf-8")
        size = file.stat().st_size
        total += size
        digest.update(relative + b"\0" + str(size).encode("ascii") + b"\0")
        with file.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest(), len(files), total


def artifact(path: Path, *, kind: str = "file") -> dict:
    relative = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
    if not path.exists():
        return {"path": relative, "kind": kind, "exists": False, "sha256": None}
    if path.is_dir():
        digest, files, total = sha256_tree(path)
        return {"path": relative, "kind": "tree", "exists": True, "sha256": digest,
                "files": files, "bytes": total}
    return {"path": relative, "kind": kind, "exists": True, "sha256": sha256_file(path),
            "bytes": path.stat().st_size}


def member_runs(run: Path, manifest: dict, *, seen: frozenset[Path] = frozenset()
                ) -> Iterable[Path]:
    """Resolve OOF/ensemble/rewindow dependencies to checkpoint-owning training runs."""
    if run.resolve() in seen:
        raise ValueError(f'dependency cycle: {run}')
    config = manifest.get('config', {})
    members = config.get("members", []) or (
        [config['source_run']] if 'source_run' in config else [])
    for member in members:
        dependency = RUNS / member
        path = dependency / 'manifest.json'
        nested = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        yield from member_runs(dependency, nested, seen=seen | {run.resolve()})
    if not members:
        yield run


def dependency_manifests(run: Path, manifest: dict, seen: frozenset[Path] = frozenset()
                         ) -> Iterable[Path]:
    if run.resolve() in seen:
        raise ValueError(f'dependency cycle: {run}')
    config = manifest.get('config', {})
    refs = config.get('members', []) or ([config['source_run']] if 'source_run' in config else [])
    for ref in refs:
        dependency = RUNS / ref
        path = dependency / 'manifest.json'
        yield path
        if path.exists():
            nested = json.loads(path.read_text(encoding='utf-8'))
            yield from dependency_manifests(dependency, nested, seen | {run.resolve()})


def phase_o_runs() -> dict[str, str]:
    found = {}
    for path in sorted(RUNS.glob('*/manifest.json')):
        manifest = json.loads(path.read_text(encoding='utf-8'))
        if manifest.get('complete') and run_details(path.parent, runs_dir=RUNS):
            found[f"phase O: {path.parent.name}"] = path.parent.name
    return found


def run_entry(label: str, run_id: str, *, skip_test_predictions: bool = False) -> dict:
    run = RUNS / run_id
    manifest_path = run / "manifest.json"
    entry = {"label": label, "run_id": run_id, "exists": run.is_dir(), "artifacts": []}
    if not manifest_path.exists():
        entry["missing_reason"] = "Không có manifest.json; không thể suy dependency."
        return entry
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entry.update(run_details(run, runs_dir=RUNS))
    entry["git"] = manifest.get("git")
    entry["split_sha256"] = manifest.get("split_sha256")
    entry["taxonomy_sha256"] = manifest.get("taxonomy_sha256")
    entry["data_manifest_sha256"] = manifest.get("data_manifest_sha256")
    entry["artifacts"].append(artifact(manifest_path, kind="run_manifest"))
    # Không coi một split chưa từng chạy là "thiếu": các ứng viên S13 chỉ có dev,
    # còn output f2 chỉ có test theo protocol mở test đúng một lần.
    for filename in (('dev.npz',) if skip_test_predictions else ('dev.npz', 'test.npz')):
        prediction = run / "predictions" / filename
        if prediction.exists():
            entry["artifacts"].append(artifact(prediction, kind="prediction"))
    for path in sorted([*run.glob("postproc*.json"), *run.glob("sebb*.json")]):
        entry["artifacts"].append(artifact(path, kind="postproc_or_sebb"))
    for path in sorted(set(dependency_manifests(run, manifest))):
        entry['artifacts'].append(artifact(path, kind='dependency_manifest'))
    for member in sorted(set(member_runs(run, manifest))):
        checkpoint = member / "checkpoints" / "best.pt"
        entry["artifacts"].append(artifact(checkpoint, kind="best_checkpoint"))
    return entry


def render(result: dict) -> str:
    lines = ["# Đóng băng artifact báo cáo", "",
             "> Sinh bởi `scripts.freeze_artifacts`; chỉ đọc file hiện có, không chạy lại "
             "huấn luyện hay đánh giá. `MISSING` là thiếu trên máy hiện tại, không phải hash bịa.",
             "",
             f"Git lúc bắt đầu: `{result['git']['revision']}` · dirty={result['git']['dirty']}", "",
             "## Run và ensemble", "",
             "| Hệ thống | Run | Artifact có/thiếu | Hop (s) | Gộp | Fold |",
             "|---|---|---:|---|---|---|"]
    for run in result["runs"]:
        present = sum(item["exists"] for item in run["artifacts"])
        missing = sum(not item["exists"] for item in run["artifacts"])
        lines.append(f"| {run['label']} | `{run['run_id']}` | {present}/{missing} | "
                     f"{run.get('hop_seconds', '—')} | {run.get('window_weighting', '—')} | "
                     f"{run.get('cv_fold', '—')} |")
    if result.get('skip_test_predictions'):
        lines += ['', 'Lượt này bỏ qua toàn bộ predictions/test.npz: không mở hoặc hash file đó. '
                  'Các hash này không được xác minh lại trong lượt freeze này.']
    lines += ["", "## SHA-256 và sự tồn tại", "",
              "| Nhóm | Đường dẫn | Kiểu | Tồn tại | SHA-256 |",
              "|---|---|---|:---:|---|"]
    for run in result["runs"]:
        for item in run["artifacts"]:
            digest = item["sha256"] or "MISSING"
            lines.append(f"| {run['label']} | `{item['path']}` | {item['kind']} | "
                         f"{'có' if item['exists'] else 'không'} | `{digest}` |")
    for item in result["external"]:
        digest = item["sha256"] or "MISSING"
        lines.append(f"| checkpoint/cache ngoài | `{item['path']}` | {item['kind']} | "
                     f"{'có' if item['exists'] else 'không'} | `{digest}` |")
    lines += ["", "## File nguồn đóng băng", "",
              "| Đường dẫn | Tồn tại | SHA-256 |", "|---|:---:|---|"]
    for item in result["frozen_inputs"]:
        lines.append(f"| `{item['path']}` | {'có' if item['exists'] else 'không'} | "
                     f"`{item['sha256'] or 'MISSING'}` |")
    return "\n".join(lines) + "\n"


def main() -> None:
    global RUNS
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs-dir', type=Path, default=RUNS)
    parser.add_argument('--asset-root', type=Path, default=ROOT)
    parser.add_argument('--out-dir', type=Path, default=MEASUREMENTS)
    parser.add_argument('--skip-test-predictions', action='store_true')
    args = parser.parse_args()
    RUNS = args.runs_dir.resolve()
    git = git_state(ROOT)
    external = [
        artifact(args.asset_root / "artifacts/checkpoints/Cnn14_mAP=0.431.pth",
                 kind="AudioSet_CNN14"),
        artifact(args.asset_root / "artifacts/checkpoints/BEATs_strong_1.pt", kind="BEATs"),
        artifact(args.asset_root / "artifacts/checkpoints/frame_mn10_strong_1.pt",
                 kind="frame_mn10"),
        artifact(args.asset_root / "artifacts/llm/Qwen_Qwen3.5-9B-Q4_K_M.gguf", kind="Qwen_GGUF"),
        artifact(args.asset_root / "artifacts/hf/models--BAAI--bge-m3", kind="BGE-M3_cache_tree"),
    ]
    frozen_paths = [
        ROOT / "data/splits/datased_polyphonic.frozen.json",
        ROOT / "data/splits/datased_trainval_folds.csv",
        ROOT / "ml/configs/taxonomy.yaml",
        ROOT / "ml/configs/caption_lexicon.yaml",
        ROOT / "ml/configs/caption_lexicon_vi.yaml",
        ROOT / "ml/configs/caption_llm.yaml",
        ROOT / "ml/retrieval/query_set.py",
        ROOT / "ml/captioning/constrained.py",
    ]
    result = {
        "git": git,
        "runs": [run_entry(label, run_id, skip_test_predictions=args.skip_test_predictions)
                 for label, run_id in {**REPORT_RUNS, **phase_o_runs()}.items()],
        "external": external,
        "frozen_inputs": [artifact(path, kind="frozen_input") for path in frozen_paths],
        "skip_test_predictions": args.skip_test_predictions,
    }
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    output = args.out_dir / f"artifact_freeze_{stamp}.md"
    if output.exists() or output.with_suffix('.json').exists():
        raise FileExistsError(output)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    output.with_suffix(".json").write_text(json.dumps(result, ensure_ascii=False, indent=2),
                                              encoding="utf-8")
    output.write_text(render(result), encoding="utf-8")
    missing = [item for run in result["runs"] for item in run["artifacts"] if not item["exists"]]
    missing += [item for item in external + result["frozen_inputs"] if not item["exists"]]
    print(render(result))
    print(f"Đã ghi {output}; thiếu {len(missing)} artifact.")


if __name__ == "__main__":
    main()
