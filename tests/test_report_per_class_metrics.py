from __future__ import annotations

from pathlib import Path

import numpy as np

from scripts.report_per_class_metrics import class_rows, render_report, validate_locked_metrics


def test_class_rows_preserve_requested_order_and_count_exact_hits() -> None:
    rows = class_rows(
        ("first", "second"),
        np.asarray([0, 0, 1, 1]),
        np.asarray([0, 1, 1, 1]),
    )

    assert [row["class_id"] for row in rows] == ["first", "second"]
    assert rows[0]["support"] == 2
    assert rows[0]["correct"] == 1
    assert rows[1]["correct"] == 2


def test_render_report_hides_low_support_f1() -> None:
    report = render_report(
        run_dir=Path("ml/runs/example"),
        checkpoint_sha256="a" * 64,
        coarse=[{"class_id": "coarse", "support": 12, "correct": 10, "f1": 0.8}],
        subclass_all=[
            {"class_id": "supported", "support": 10, "correct": 8, "f1": 0.8},
            {"class_id": "small", "support": 3, "correct": 2, "f1": 0.6},
        ],
        subclass_supported=[
            {"class_id": "supported", "support": 10, "correct": 8, "f1": 0.8}
        ],
    )

    low_section = report.split("## Low-support subclass nodes", maxsplit=1)[1]
    assert "`small` | 2 / 3" in low_section
    assert "0.600000" not in low_section


def test_locked_metrics_use_only_supported_rows_for_supported_macro() -> None:
    coarse = [{"class_id": "coarse", "support": 12, "correct": 10, "f1": 0.8}]
    all_nodes = [
        {"class_id": "supported", "support": 10, "correct": 8, "f1": 0.8},
        {"class_id": "small", "support": 3, "correct": 2, "f1": 0.6},
    ]
    supported = [all_nodes[0]]

    validate_locked_metrics(
        {
            "coarse_macro_f1": 0.8,
            "subclass_macro_f1_all": 0.7,
            "subclass_macro_f1_supported": 0.8,
        },
        coarse,
        all_nodes,
        supported,
    )
