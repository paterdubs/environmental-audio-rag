"""Chạy demo đầu-cuối trên máy dev (W7 7.4, ADR-0029): db → inference → api + giao diện.

    .venv/Scripts/python.exe -m scripts.serve_demo [--api-port 8010] [--inference-port 8001]

1. `docker compose up -d db` và chờ PostgreSQL healthy.
2. Build frontend nếu chưa có `services/frontend/dist` (cần Node/npm).
3. Chạy inference (GPU nếu có) rồi api; chỉ báo sẵn sàng khi `/health` của api trả 200
   — tức DB và model đều đã nạp thật (SYSTEM §4.4).
Ctrl+C dừng inference và api (db để chạy tiếp, như trước).
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "services/frontend"
READY_TIMEOUT_S = 300


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-port", type=int, default=8010)
    parser.add_argument("--inference-port", type=int, default=8001)
    parser.add_argument("--skip-db", action="store_true", help="db đã chạy sẵn ở nơi khác")
    return parser.parse_args()


def wait_ready(url: str, label: str, process: subprocess.Popen | None = None) -> None:
    deadline = time.monotonic() + READY_TIMEOUT_S
    while time.monotonic() < deadline:
        if process is not None and process.poll() is not None:
            raise SystemExit(f"{label} đã dừng với mã {process.returncode}")
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.status == 200:
                    print(f"  ✓ {label} sẵn sàng")
                    return
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(2)
    raise SystemExit(f"{label} không sẵn sàng sau {READY_TIMEOUT_S} s ({url})")


def start_db() -> None:
    print("• db (docker compose)")
    subprocess.run(["docker", "compose", "up", "-d", "--wait", "db"], cwd=ROOT, check=True)


def build_frontend() -> None:
    if (FRONTEND / "dist/index.html").is_file():
        return
    npm = shutil.which("npm")
    if npm is None:
        print("  ! không có npm — api chạy không kèm giao diện")
        return
    print("• build frontend")
    subprocess.run([npm, "ci"], cwd=FRONTEND, check=True)
    subprocess.run([npm, "run", "build"], cwd=FRONTEND, check=True)


def uvicorn(app: str, port: int, env: dict[str, str]) -> subprocess.Popen:
    return subprocess.Popen([sys.executable, "-m", "uvicorn", app, "--host", "127.0.0.1",
                             "--port", str(port), "--log-level", "warning"], cwd=ROOT, env=env)


def main() -> None:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not args.skip_db:
        start_db()
    build_frontend()
    env = {**os.environ, "INFERENCE_URL": f"http://127.0.0.1:{args.inference_port}"}
    children: list[subprocess.Popen] = []
    try:
        print("• inference (nạp 4 checkpoint + BGE-M3)")
        children.append(uvicorn("services.inference.app.main:app", args.inference_port, env))
        wait_ready(f"http://127.0.0.1:{args.inference_port}/health", "inference", children[-1])
        print("• api")
        children.append(uvicorn("services.api.app.main:app", args.api_port, env))
        wait_ready(f"http://127.0.0.1:{args.api_port}/health", "api", children[-1])
        print(f"\nGiao diện: http://127.0.0.1:{args.api_port}/   (Ctrl+C để dừng)")
        while all(child.poll() is None for child in children):
            time.sleep(1)
        raise SystemExit("một service đã dừng bất thường")
    except KeyboardInterrupt:
        print("\nĐang dừng…")
    finally:
        for child in children:
            child.terminate()
        for child in children:
            child.wait(timeout=30)


if __name__ == "__main__":
    main()
