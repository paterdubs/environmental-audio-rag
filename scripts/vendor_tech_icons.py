"""Chép biểu tượng công nghệ từ Simple Icons 16.38.1 (CC0 1.0) vào repo, kèm manifest nguồn.

Tải gói npm, kiểm SHA-256 với giá trị đã ghi, rồi chỉ đọc đúng các tệp `icons/<slug>.svg` cần
dùng (không giải nén toàn bộ gói). Mỗi tệp SVG được kiểm là một đường `path` duy nhất trên khung
24 × 24 trước khi ghi. CC0 chỉ áp cho tệp SVG; quyền nhãn hiệu vẫn thuộc chủ sở hữu, xem chú thích
dưới hình trong báo cáo.

    .venv/Scripts/python.exe -m scripts.vendor_tech_icons
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "report" / "assets" / "tech_icons"
VERSION = "16.38.1"
URL = f"https://registry.npmjs.org/simple-icons/-/simple-icons-{VERSION}.tgz"
SHA256 = "8ad81af0009aa0935df4411080feb4547b72e13458bbcf4d803b259b1f078804"
SLUGS = ("docker", "pytorch", "scikitlearn", "qwen", "huggingface", "pytest", "ruff", "fastapi",
         "react", "typescript", "vite", "reactquery", "vitest")
SVG = re.compile(r'^<svg [^>]*viewBox="0 0 24 24"[^>]*><title>[^<]+</title>'
                 r'<path d="([^"]+)"/></svg>\s*$')


def path_data(svg: str) -> str:
    """Đường `d` của một biểu tượng Simple Icons; từ chối mọi dạng khác (script, nhiều phần tử)."""
    match = SVG.match(svg)
    if not match:
        raise ValueError("SVG không đúng dạng một path trên khung 24 × 24")
    return match.group(1)


def download(url: str = URL, expected: str = SHA256) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:  # noqa: S310 (URL cố định)
        data = response.read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != expected:
        raise ValueError(f"SHA-256 của gói là {digest}, không khớp {expected}")
    return data


def vendor(archive: bytes, output: Path, slugs: tuple[str, ...] = SLUGS) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        meta = {d["slug"]: d for d in json.load(tar.extractfile("package/data/simple-icons.json"))}
        icons = {}
        for slug in slugs:
            svg = tar.extractfile(f"package/icons/{slug}.svg").read().decode("utf-8")
            path_data(svg)
            (output / f"{slug}.svg").write_text(svg, encoding="utf-8")
            info = meta[slug]
            icons[slug] = {"title": info["title"], "hex": info["hex"],
                           "source": info.get("source"),
                           "license": info.get("license", {"type": "CC0-1.0"}),
                           "guidelines": info.get("guidelines")}
        (output / "LICENSE.md").write_bytes(tar.extractfile("package/LICENSE.md").read())
        (output / "DISCLAIMER.md").write_bytes(tar.extractfile("package/DISCLAIMER.md").read())
    manifest = {"package": f"simple-icons@{VERSION}", "url": URL, "sha256": SHA256,
                "icons": icons}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                                          encoding="utf-8")
    return manifest


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--archive", type=Path, help="gói .tgz đã tải sẵn (vẫn kiểm SHA-256)")
    args = parser.parse_args()
    if args.archive:
        data = args.archive.read_bytes()
        if hashlib.sha256(data).hexdigest() != SHA256:
            raise SystemExit("SHA-256 của gói không khớp")
    else:
        data = download()
    manifest = vendor(data, args.output)
    print(f"Đã chép {len(manifest['icons'])} biểu tượng vào {args.output}")


if __name__ == "__main__":
    main()
