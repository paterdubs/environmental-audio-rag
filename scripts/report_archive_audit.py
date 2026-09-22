"""Generate a Markdown measurement from archive audit manifests.

Usage:
    python -m scripts.report_archive_audit datasec datased
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data" / "manifests"
REFERENCE = ROOT / "data" / "reference"

VERDICT_NOTE = {
    "pass": "size and MD5 verified, every observed label maps to the taxonomy",
    "pass_unverified_md5": "size verified, MD5 pass was skipped",
    "fail_checksum": "size or MD5 does not match the frozen source contract",
    "fail_unmapped_label": "archive holds a label absent from the taxonomy",
}


def gib(value: int) -> str:
    return f"{value / 2**30:.2f}"


def zenodo_license(dataset: str) -> tuple[str, str]:
    """Return (license id, record DOI) from the stored Zenodo record."""
    matches = sorted(REFERENCE.glob(f"zenodo_{dataset}_*.json"))
    if not matches:
        return "(not recorded)", "(not recorded)"
    metadata = json.loads(matches[-1].read_text(encoding="utf-8"))["metadata"]
    licence = metadata.get("license") or {}
    return str(licence.get("id", "(not recorded)")), str(metadata.get("doi", "(not recorded)"))


def summary_table(audits: list[dict]) -> list[str]:
    lines = [
        "| Field | " + " | ".join(f"`{a['dataset']}`" for a in audits) + " |",
        "|---|" + "---:|" * len(audits),
    ]
    rows: list[tuple[str, list[str]]] = [
        ("Archive bytes", [f"{a['bytes_actual']:,}" for a in audits]),
        ("Size matches contract", [str(a["size_match"]) for a in audits]),
        ("MD5", [f"`{a['md5_actual']}`" for a in audits]),
        ("MD5 matches contract", [str(a["md5_match"]) for a in audits]),
        ("ZIP entries", [f"{a['entries']:,}" for a in audits]),
        ("Audio files", [f"{a['audio_files']:,}" for a in audits]),
        ("Uncompressed GiB", [gib(a["uncompressed_bytes"]) for a in audits]),
        ("Annotation tables", [str(len(a["annotation_files"])) for a in audits]),
        ("LICENSE/README inside archive", [str(len(a["documentation_files"])) for a in audits]),
        ("Coarse labels in layout", [str(a["coarse_labels"]) for a in audits]),
        ("Subclass labels in layout", [str(a["subclass_labels"]) for a in audits]),
        ("Labels outside taxonomy", [str(len(a["unmapped_labels"])) for a in audits]),
        ("Verdict", [f"**{a['verdict']}**" for a in audits]),
    ]
    lines.extend(f"| {name} | " + " | ".join(values) + " |" for name, values in rows)
    return lines


def label_table(audit: dict) -> list[str]:
    lines = [
        "",
        f"### `{audit['dataset']}` label layout",
        "",
        "| Source label | Canonical class ID | Files | Subclasses (files) |",
        "|---|---|---:|---|",
    ]
    for node in audit["labels"]:
        subs = node["subclasses"]
        rendered = ", ".join(f"`{k}` ({v})" for k, v in subs.items()) if subs else "—"
        lines.append(
            f"| {node['source_label']} | `{node['canonical_class_id']}` "
            f"| {node['files']:,} | {rendered} |"
        )
    total = sum(node["files"] for node in audit["labels"])
    lines.append(f"| **Total** | | **{total:,}** | |")
    return lines


def build_report(audits: list[dict]) -> str:
    lines = [
        "# Archive audit — DataSEC and DataSED",
        "",
        "> Generated from `data/manifests/<dataset>_archive_audit.json` by",
        "> `python -m scripts.report_archive_audit`. Do not edit the numbers by hand.",
        "",
        f"- Generated at: `{datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        f"- Taxonomy version: `{audits[0]['taxonomy_version']}`",
        f"- Taxonomy SHA-256: `{audits[0]['taxonomy_sha256']}`",
        "",
        "## Provenance and licence",
        "",
        "| Dataset | Record DOI | Licence |",
        "|---|---|---|",
    ]
    for audit in audits:
        licence, doi = zenodo_license(audit["dataset"])
        lines.append(f"| `{audit['dataset']}` | `{doi}` | `{licence}` |")
    lines.extend(
        [
            "",
            "Licence comes from the stored Zenodo record, **not** from the archive: the audit",
            "found no LICENSE or README entry inside either ZIP (see table below).",
            "",
            "## Audit summary",
            "",
        ]
    )
    lines.extend(summary_table(audits))
    lines.extend(
        [
            "",
            "Verdict meanings:",
            "",
        ]
    )
    lines.extend(
        f"- `{verdict}` — {note}"
        for verdict, note in VERDICT_NOTE.items()
        if verdict in {a["verdict"] for a in audits}
    )
    lines.append("")
    lines.append("## Label layout")
    for audit in audits:
        if audit["labels"]:
            lines.extend(label_table(audit))
        else:
            lines.extend(
                [
                    "",
                    f"### `{audit['dataset']}` label layout",
                    "",
                    "Labels are not encoded in the directory tree. The archive ships "
                    f"{len(audit['annotation_files'])} annotation table(s):",
                    "",
                ]
            )
            lines.extend(f"- `{name}`" for name in audit["annotation_files"])
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This audit reads the ZIP central directory only. It verifies archive integrity,",
            "audio counts and label-name coverage. It does **not** open any audio file, so it",
            "says nothing about sample rate, duration, decodability, annotation validity or",
            "duplicates. Those belong to gates D1–D3 and require extraction plus inventory.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("datasets", nargs="+", choices=["datasec", "datased"])
    args = parser.parse_args()
    audits = [
        json.loads((MANIFESTS / f"{name}_archive_audit.json").read_text(encoding="utf-8"))
        for name in args.datasets
    ]
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    output = ROOT / "docs" / "measurements" / f"archive_audit_{stamp}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_report(audits), encoding="utf-8")
    print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
