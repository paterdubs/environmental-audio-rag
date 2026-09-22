from __future__ import annotations

import argparse
from pathlib import Path

from ml.dataops.inventory import build_inventory, inventory_summary, write_inventory, write_summary

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", choices=["datasec", "datased"])
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    raw_root = ROOT / "data" / "raw" / args.dataset / "extracted"
    records = build_inventory(args.dataset, raw_root, args.workers)
    write_inventory(records, ROOT / "data" / "manifests" / f"{args.dataset}_inventory.csv")
    summary = inventory_summary(records)
    write_summary(
        summary, ROOT / "data" / "manifests" / f"{args.dataset}_inventory_summary.json"
    )
    print(summary)


if __name__ == "__main__":
    main()
