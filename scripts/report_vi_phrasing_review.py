"""Sinh danh sách cụm tiếng Việt cần người dùng duyệt, không sửa lexicon."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
UI_PHRASES = [
    "Truy vấn tự nhiên", "Bộ lọc thủ công", "Bộ lọc đã hiểu — có thể sửa trước khi tìm",
    "Không hiểu được câu hỏi; hãy chọn bộ lọc thủ công",
    "Đang phân tích… (CPU có thể mất khoảng một phút)",
    "Demo — SED v2, chưa phải hệ thống chính thức", "Bộ lọc đã áp", "Đang hiểu câu hỏi…",
]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=date.today().isoformat().replace("-", ""))
    args = parser.parse_args()
    source = ROOT / "ml/configs/caption_lexicon_vi.yaml"
    lexicon = yaml.safe_load(source.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for section in ("class", "specific"):
        for class_id, phrases in lexicon.get(section, {}).items():
            for phrase in phrases:
                rows.append({
                    "source": f"caption_lexicon_vi.yaml:{section}.{class_id}",
                    "phrase": phrase,
                })
    for phrase in UI_PHRASES:
        rows.append({"source": "services/frontend/src", "phrase": phrase})
    forbidden = [str(p) for p in lexicon.get("forbidden_terms", [])]
    output = ROOT / "docs/measurements" / f"vi_phrasing_review_{args.date}.md"
    payload = {
        "date": args.date,
        "source": str(source.relative_to(ROOT)),
        "count": len(rows),
        "phrases": rows,
        "forbidden_terms_checked": forbidden,
        "decision": "CẦN NGƯỜI DÙNG DUYỆT — không tự sửa lexicon VI",
    }
    table = "\n".join(f"| `{r['source']}` | {r['phrase']} |" for r in rows)
    markdown = (
        "# Rà cụm từ tiếng Việt\n\n"
        f"Ngày sinh: {args.date}. Tổng cụm: {len(rows)}.\n\n"
        "**CẦN NGƯỜI DÙNG DUYỆT — không tự sửa lexicon VI.**\n\n"
        "| Nguồn | Cụm từ |\n|---|---|\n"
        f"{table}\n\nDanh sách forbidden_terms đã được đọc để kiểm tra hồi quy; "
        "không thay đổi file nguồn.\n"
    )
    output.write_text(markdown, encoding="utf-8")
    output.with_suffix(".json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Đã sinh {output.relative_to(ROOT)} ({len(rows)} cụm; chờ người dùng duyệt).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
