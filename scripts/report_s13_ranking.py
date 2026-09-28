"""Báo cáo thứ hạng tạm thời của các ứng viên S13 chỉ bằng CV trên dev.

Ví dụ::

    .venv/Scripts/python.exe -m scripts.report_s13_ranking \
        --candidate "f4=ml/runs/sed_ensemble_t2b_bv2_20260927T200921Z" \
        --candidate "d=ml/runs/sed_ensemble_cv2_20260926T205405Z" \
        --eval-set annotated

Mỗi ứng viên được chấm bằng họ hậu xử lý tốt hơn giữa theta và cSEBB. File ``all``
không hậu tố chỉ được đọc để định lượng ảnh hưởng của ADR-0034; mọi lựa chọn dùng file
``annotated`` và không đọc artifact test.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from ml.evaluation.coverage import EVAL_SETS, eval_suffix
from ml.provenance import git_state

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class FamilyScore:
    family: str
    config: str
    mean: float
    sd: float
    folds: tuple[float, ...]


@dataclass(frozen=True)
class Candidate:
    label: str
    run: str
    models: int
    score: FamilyScore
    families: tuple[FamilyScore, ...]
    all_score: FamilyScore
    all_families: tuple[FamilyScore, ...]

    @property
    def delta_vs_all(self) -> float:
        return self.score.mean - self.all_score.mean


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--candidate",
        action="append",
        required=True,
        help="'nhãn=đường/dẫn/run' — lặp lại cho mỗi ứng viên",
    )
    parser.add_argument("--eval-set", choices=EVAL_SETS, default="annotated")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "docs" / "measurements")
    return parser.parse_args()


def _read(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"thiếu artifact bắt buộc: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"artifact phải là JSON object: {path}")
    return value


def _selected_key(payload: dict, family: str, path: Path) -> str:
    selected = payload.get("selected")
    if not isinstance(selected, dict):
        raise ValueError(f"thiếu selected trong {path}")
    if family == "theta":
        try:
            return f"{selected['threshold_mode']}|{float(selected['g_max_percentile']):g}"
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"selected của họ theta không hợp lệ trong {path}") from exc
    config = selected.get("config")
    if not isinstance(config, str) or not config:
        raise ValueError(f"selected của họ cSEBB không hợp lệ trong {path}")
    return config


def _family_score(path: Path, family: str, *, eval_set: str | None) -> FamilyScore:
    payload = _read(path)
    if eval_set is not None:
        if payload.get("eval_set") != eval_set:
            raise ValueError(
                f"eval_set không khớp trong {path}: "
                f"{payload.get('eval_set')!r} != {eval_set!r}"
            )
        if payload.get("git", {}).get("dirty") is not False:
            raise ValueError(f"artifact không sinh trên tree sạch (git.dirty != false): {path}")

    config = _selected_key(payload, family, path)
    cv = payload.get("cv", {}).get(config)
    if not isinstance(cv, dict):
        raise ValueError(f"không tìm thấy cv[{config!r}] trong {path}")
    try:
        folds = tuple(float(value) for value in cv["folds"])
        score = FamilyScore(
            family=family,
            config=config,
            mean=float(cv["mean"]),
            sd=float(cv["sd"]),
            folds=folds,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"mean/sd/folds không hợp lệ trong {path}") from exc
    if not folds:
        raise ValueError(f"folds rỗng trong {path}")
    return score


def _family_files(run_dir: Path, eval_set: str) -> tuple[tuple[str, Path], ...]:
    suffix = eval_suffix(eval_set)
    return (
        ("theta", run_dir / f"postproc_cv_selection{suffix}.json"),
        ("csebb", run_dir / f"sebb_cv_selection{suffix}.json"),
    )


def load_families(
    run_dir: Path, eval_set: str, *, validate_provenance: bool
) -> tuple[FamilyScore, ...]:
    required_eval_set = eval_set if validate_provenance else None
    return tuple(
        _family_score(path, family, eval_set=required_eval_set)
        for family, path in _family_files(run_dir, eval_set)
    )


def best_family(families: tuple[FamilyScore, ...]) -> FamilyScore:
    """Họ có CV mean cao nhất; hòa giữa họ giữ thứ tự theta rồi cSEBB."""
    return max(families, key=lambda result: result.mean)


def model_count(manifest: dict) -> int:
    members = manifest.get("config", {}).get("members", [])
    return len(members) if isinstance(members, list) and members else 1


def load_candidate(spec: str, eval_set: str = "annotated") -> Candidate:
    label, separator, raw_path = spec.partition("=")
    run_dir = Path(raw_path)
    if not separator or not label or not run_dir.is_dir():
        raise ValueError(f"ứng viên không hợp lệ: {spec!r} (cần 'nhãn=đường/dẫn/run')")

    manifest = _read(run_dir / "manifest.json")
    families = load_families(run_dir, eval_set, validate_provenance=True)
    # Artifact lịch sử ``all`` có trước trường eval_set và trước gate provenance ADR-0034.
    # Nó chỉ là cột đối chiếu, tuyệt đối không tham gia xếp hạng.
    all_families = load_families(run_dir, "all", validate_provenance=False)
    return Candidate(
        label=label,
        run=run_dir.name,
        models=model_count(manifest),
        score=best_family(families),
        families=families,
        all_score=best_family(all_families),
        all_families=all_families,
    )


def rank_candidates(candidates: list[Candidate]) -> tuple[list[Candidate], str]:
    if not candidates:
        raise ValueError("cần ít nhất một ứng viên")
    ranking = sorted(candidates, key=lambda candidate: (-candidate.score.mean, candidate.models,
                                                         candidate.label))
    note = ""
    if len(ranking) > 1:
        leader, runner_up = ranking[:2]
        gap = leader.score.mean - runner_up.score.mean
        if gap <= leader.score.sd:
            note = (
                f"Chênh lệch hạng 1 (`{leader.label}`) − hạng 2 (`{runner_up.label}`) "
                f"là {gap:+.4f}, không lớn hơn sd giữa fold của hạng 1 "
                f"({leader.score.sd:.4f}): **không được gọi là tốt hơn hạng 2**."
            )
    return ranking, note


def _cell(value: str) -> str:
    return "`" + value.replace("|", "\\|") + "`"


def _family_name(family: str) -> str:
    return "θ" if family == "theta" else "cSEBB"


def _folds_cell(values: tuple[float, ...]) -> str:
    return ", ".join(f"{value:.4f}" for value in values)


def render(ranking: list[Candidate], note: str, eval_set: str, git: dict) -> str:
    lines = [
        f"# Thứ hạng ứng viên S13 — CV dev `{eval_set}`",
        "",
        "> **Chỉ dev, CHƯA phải lựa chọn S13, không mở test.** Sinh bởi "
        "`scripts.report_s13_ranking`; event-F1 micro, 5 fold theo `leakage_group`. "
        "Điểm là CV mean của họ tốt hơn giữa θ và cSEBB.",
        f"> git `{git['revision'][:7]}`, dirty={str(git['dirty']).lower()}.",
        "",
        "| Hạng | Nhãn | Run | Model | Họ chấm | Cấu hình | "
        "CV annotated mean ± sd | Fold annotated | Họ all | CV all | Δ annotated − all |",
        "|---:|---|---|---:|---|---|---:|---|---|---:|---:|",
    ]
    for rank, candidate in enumerate(ranking, 1):
        lines.append(
            f"| {rank} | {candidate.label} | `{candidate.run}` | {candidate.models} | "
            f"{_family_name(candidate.score.family)} | {_cell(candidate.score.config)} | "
            f"{candidate.score.mean:.4f} ± {candidate.score.sd:.4f} | "
            f"{_folds_cell(candidate.score.folds)} | "
            f"{_family_name(candidate.all_score.family)} | {candidate.all_score.mean:.4f} | "
            f"{candidate.delta_vs_all:+.4f} |"
        )
    if note:
        lines += ["", note]
    lines += [
        "",
        "Cột `all` chỉ để đối chiếu ảnh hưởng của ADR-0034; không tham gia xếp hạng. "
        "Kết quả này không chọn hệ thống và không cho phép mở test trước mốc S13.",
    ]
    return "\n".join(lines) + "\n"


def candidate_dict(rank: int, candidate: Candidate) -> dict:
    return {
        "rank": rank,
        "label": candidate.label,
        "run": candidate.run,
        "models": candidate.models,
        "annotated": {
            "score_family": candidate.score.family,
            "score": asdict(candidate.score),
            "families": [asdict(family) for family in candidate.families],
        },
        "all": {
            "score_family": candidate.all_score.family,
            "score": asdict(candidate.all_score),
            "families": [asdict(family) for family in candidate.all_families],
        },
        "delta_annotated_minus_all": candidate.delta_vs_all,
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    candidates = [load_candidate(spec, args.eval_set) for spec in args.candidate]
    ranking, note = rank_candidates(candidates)
    git = git_state(ROOT)
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    output = args.out_dir / f"s13_ranking_{args.eval_set}_{stamp}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "eval_set": args.eval_set,
        "metric": "event-F1 micro, CV 5 fold dev theo leakage_group",
        "provisional": True,
        "test_accessed": False,
        "leader": ranking[0].label,
        "ranking": [candidate_dict(rank, candidate) for rank, candidate in enumerate(ranking, 1)],
        "note": note,
        "git": git,
    }
    output.with_suffix(".json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    report = render(ranking, note, args.eval_set, git)
    output.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
