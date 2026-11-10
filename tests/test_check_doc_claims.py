"""Đối chiếu số trong tài liệu với artifact (ADR-0048 §4): bắt đúng lỗi kiểu ghi nhầm PSDS B0."""

import json
from pathlib import Path

import pytest

from scripts import check_doc_claims as checker


@pytest.fixture()
def repo(tmp_path: Path) -> tuple[Path, Path]:
    root, runs = tmp_path / "repo", tmp_path / "runs"
    (root / "docs").mkdir(parents=True)
    (runs / "run_a").mkdir(parents=True)
    evaluation = {"psds": {"psds_1": 0.31311781, "psds_2": 0.73095254},
                  "results": [{"lbr_run": "x", "curves": {"log (mới)": {"value": 0.35118}}},
                              {"lbr_run": "y", "curves": {"log (mới)": {"value": 0.33688}}}]}
    (runs / "run_a" / "evaluation.json").write_text(json.dumps(evaluation), encoding="utf-8")
    return root, runs


def claim(mentions: list[dict], key: list, decimals: int = 4) -> dict:
    return {"id": "c", "source": "ml/runs/run_a/evaluation.json", "key": key,
            "decimals": decimals, "mentions": mentions}


def test_select_walks_keys_indices_and_unique_filters():
    data = {"a": [{"run": "x", "v": 1}, {"run": "y", "v": 2}], "b": [10, 20]}
    assert checker.select(data, ["a", {"run": "y"}, "v"]) == 2
    assert checker.select(data, ["b", 1]) == 20
    with pytest.raises(KeyError, match="0 khớp"):
        checker.select(data, ["a", {"run": "z"}, "v"])


def test_correct_mention_passes_even_across_a_line_break(repo):
    root, runs = repo
    (root / "docs/STATUS.md").write_text("PSDS của B0\n0.3131 / 0.7310 (lưới tuyến tính)",
                                         encoding="utf-8")
    spec = claim([{"file": "docs/STATUS.md", "text": "B0 {value} / 0.7310"}], ["psds", "psds_1"])
    assert checker.check([spec], root=root, runs_root=runs) == []


def test_misquoted_value_is_reported_with_both_numbers(repo):
    root, runs = repo
    (root / "docs/STATUS.md").write_text("B0 0.3489 / 0.6987", encoding="utf-8")
    spec = claim([{"file": "docs/STATUS.md", "text": "B0 {value} / "}], ["psds", "psds_1"])
    [failure] = checker.check([spec], root=root, runs_root=runs)
    assert "0.3489" in failure.message and "0.3131" in failure.message


def test_every_occurrence_must_match_not_only_the_first(repo):
    root, runs = repo
    (root / "docs/STATUS.md").write_text("B0 0.3131 / x. Sau đó B0 0.3489 / y", encoding="utf-8")
    spec = claim([{"file": "docs/STATUS.md", "text": "B0 {value} / "}], ["psds", "psds_1"])
    assert len(checker.check([spec], root=root, runs_root=runs)) == 1


def test_missing_mention_fails_instead_of_passing_silently(repo):
    root, runs = repo
    (root / "docs/STATUS.md").write_text("không có số", encoding="utf-8")
    spec = claim([{"file": "docs/STATUS.md", "text": "B0 {value} / "}], ["psds", "psds_1"])
    [failure] = checker.check([spec], root=root, runs_root=runs)
    assert "không thấy" in failure.message


def test_filtered_list_key_with_spaces_and_mention_level_decimals(repo):
    root, runs = repo
    (root / "docs/A.md").write_text("V3 0.337 trên lưới log", encoding="utf-8")
    spec = claim([{"file": "docs/A.md", "text": "V3 {value} trên", "decimals": 3}],
                 ["results", {"lbr_run": "y"}, "curves", "log (mới)", "value"])
    assert checker.check([spec], root=root, runs_root=runs) == []


def test_template_must_have_exactly_one_placeholder():
    with pytest.raises(ValueError, match="value"):
        checker.mention_regex("B0 không có chỗ số")


def test_sources_outside_ml_runs_resolve_against_the_repo(repo):
    root, runs = repo
    (root / "docs/m.json").write_text(json.dumps({"v": 0.5}), encoding="utf-8")
    (root / "docs/A.md").write_text("đạt 0.50 ở", encoding="utf-8")
    spec = {"id": "m", "source": "docs/m.json", "key": ["v"], "decimals": 2,
            "mentions": [{"file": "docs/A.md", "text": "đạt {value} ở"}]}
    assert checker.check([spec], root=root, runs_root=runs) == []


def test_repo_claims_file_is_valid_and_consistent():
    root = Path(checker.__file__).resolve().parents[1]
    claims = checker.load_claims(root / "docs/claims.yaml")
    assert claims and len({c["id"] for c in claims}) == len(claims)
    for spec in claims:
        assert spec["mentions"], spec["id"]
        for mention in spec["mentions"]:
            checker.mention_regex(mention["text"])
