from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Markdown measurement from a run")
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    run = args.run.resolve()
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
    lines = [
        f"# Run `{run.name}`",
        "",
        "> Generated from run artifacts by `python -m scripts.report_run`.",
        "",
        "## Provenance",
        "",
        f"- Complete: `{manifest['complete']}`",
        f"- Torch: `{manifest['environment']['torch']}`",
        f"- GPU: `{manifest['environment']['gpu']}`",
        f"- Taxonomy SHA-256: `{manifest['taxonomy_sha256']}`",
        f"- Split SHA-256: `{manifest['split_sha256']}`",
        f"- Best validation frame macro-F1: `{metrics['best_validation']:.6f}`",
    ]
    test = metrics.get("test")
    if test:
        lines.extend(
            [
                "",
                "## Frozen test result",
                "",
                f"- Frame macro-F1 at threshold 0.5: `{test['macro_f1']:.6f}`",
                f"- Frame macro average precision: `{test['macro_average_precision']:.6f}`",
                f"- Evaluated frames: `{test['frames']}`",
                "",
                "| Class | Frame F1 |",
                "|---|---:|",
            ]
        )
        lines.extend(
            f"| `{class_id}` | {score:.6f} |"
            for class_id, score in zip(
                manifest["class_ids"], test["per_class_f1"], strict=True
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "These are frame-level baseline metrics. Event-based F1 and PSDS require calibrated "
            "post-processing and are not implied by this report.",
            "",
        ]
    )
    output = ROOT / "docs" / "measurements" / f"{run.name}.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
