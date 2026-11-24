"""Sinh hai bảng hệ thống cho Chương 5 từ chính mã nguồn và tệp cấu hình.

- `f15_tech_stack.md`: công nghệ theo tầng, phiên bản đọc từ `requirements-*.txt`,
  `services/frontend/package.json`, `docker-compose.yml`, Dockerfile và `caption_llm.yaml`;
- `f16_api.md`: mọi endpoint HTTP, đọc bằng AST từ decorator FastAPI trong `services/`.

Cột "vai trò" là mô tả do nhóm viết, khai báo trong `ROLES` / `ENDPOINTS`. Nếu một công nghệ
không còn trong tệp phụ thuộc, hoặc mã có endpoint chưa được mô tả (hay mô tả endpoint đã xóa),
script báo lỗi thay vì sinh bảng lệch với mã.

    .venv/Scripts/python.exe -m scripts.report_system_tables
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from ml.provenance import git_state

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "report" / "final_tables"
FRONTEND_PACKAGE = ROOT / "services" / "frontend" / "package.json"
COMPOSE = ROOT / "docker-compose.yml"
LLM_CONFIG = ROOT / "ml" / "configs" / "caption_llm.yaml"
DOCKERFILES = (
    ROOT / "services" / "api" / "Dockerfile",
    ROOT / "services" / "inference" / "Dockerfile",
)
SERVICE_SOURCES = (
    ROOT / "services" / "api" / "app" / "main.py",
    ROOT / "services" / "api" / "app" / "recordings.py",
    ROOT / "services" / "api" / "app" / "retrieval.py",
    ROOT / "services" / "inference" / "app" / "main.py",
)


@dataclass(frozen=True)
class Tech:
    layer: str
    name: str
    source: str  # "pip:<gói>", "npm:<gói>", "image:<tên>", "docker:<ảnh nền>", "llm", "runtime"
    role: str
    adr: str = ""


ROLES: tuple[Tech, ...] = (
    Tech(
        "Hạ tầng",
        "Docker Compose",
        "compose",
        "Dựng ba dịch vụ db, api, inference bằng một lệnh; cô lập phụ thuộc của từng dịch vụ",
        "0029",
    ),
    Tech(
        "Hạ tầng",
        "Python; Node.js (build giao diện)",
        "docker:python+node",
        "Python cho học máy, đánh giá và hai dịch vụ; Node.js chỉ dùng khi build giao diện",
    ),
    Tech(
        "Học máy",
        "PyTorch",
        "pip:torch",
        "Huấn luyện và suy luận mô hình SED, mô hình phân loại DataSEC",
        "0002",
    ),
    Tech(
        "Học máy",
        "librosa, soundfile",
        "pip:librosa+soundfile",
        "Đọc âm thanh, đổi tần số lấy mẫu, trích log-mel",
    ),
    Tech(
        "Học máy",
        "scikit-learn",
        "pip:scikit-learn",
        "Hai bộ học tăng cường gradient của LBR",
        "0045",
    ),
    Tech(
        "Đánh giá",
        "sed_eval, psds_eval",
        "pip:sed_eval+psds_eval",
        "Event-F1 theo collar và PSDS bằng thư viện chuẩn, không tự viết lại",
        "0020",
    ),
    Tech("Đánh giá", "pytest, ruff", "pip:pytest+ruff", "Kiểm thử tự động và kiểm tra mã trong CI"),
    Tech(
        "Mô hình ngôn ngữ",
        "llama.cpp + Qwen3.5-9B",
        "llm",
        "Chạy cục bộ: phân tích câu hỏi thành bộ lọc JSON; sinh mô tả cho thí nghiệm RQ2",
        "0022, 0036",
    ),
    Tech(
        "Truy hồi",
        "sentence-transformers (BGE-M3)",
        "pip:sentence-transformers",
        "Nhúng tài liệu và câu hỏi tiếng Việt, tiếng Anh vào cùng không gian 1024 chiều",
        "0004",
    ),
    Tech(
        "Lưu trữ",
        "PostgreSQL 16 + pgvector",
        "image:pgvector/pgvector",
        "Kho sự kiện: bộ lọc, điều kiện thời gian và xếp hạng vector trong một câu SQL",
        "0005",
    ),
    Tech(
        "Lưu trữ",
        "psycopg",
        "pip:psycopg[binary]",
        "Trình điều khiển PostgreSQL cho API và script dựng kho",
    ),
    Tech(
        "Dịch vụ",
        "FastAPI, Uvicorn",
        "pip:fastapi+uvicorn",
        "Hai dịch vụ HTTP: API (không nạp torch) và suy luận",
        "0029",
    ),
    Tech("Dịch vụ", "httpx", "pip:httpx", "API gọi dịch vụ suy luận và llama.cpp"),
    Tech(
        "Giao diện",
        "React",
        "npm:react",
        "Giao diện một trang: tải lên, dòng thời gian, thẻ bộ lọc, câu trả lời",
        "0037",
    ),
    Tech(
        "Giao diện",
        "TypeScript, Vite",
        "npm:typescript+vite",
        "Kiểu tĩnh cho giao diện; đóng gói bản build phục vụ qua API",
    ),
    Tech(
        "Giao diện",
        "TanStack Query",
        "npm:@tanstack/react-query",
        "Gọi API và lưu đệm kết quả phía trình duyệt",
    ),
    Tech(
        "Giao diện",
        "Vitest, Playwright",
        "npm:vitest+playwright",
        "Kiểm thử thành phần giao diện và chụp ảnh màn hình demo",
    ),
)

ENDPOINTS: dict[tuple[str, str, str], str] = {
    ("API", "GET", "/health"): "Kiểm tra API và kết nối cơ sở dữ liệu",
    ("API", "GET", "/api/v1/taxonomy"): "21 lớp SED và tên hiển thị EN/VI cho giao diện",
    (
        "API",
        "GET",
        "/api/v1/models/status",
    ): "Phiên bản mô hình đang phục vụ (B0, LBR, điểm vận hành)",
    (
        "API",
        "POST",
        "/api/v1/audio/upload",
    ): "Nhận tệp âm thanh, gọi suy luận, lưu sự kiện và mô tả",
    ("API", "GET", "/api/v1/recordings"): "Danh sách bản ghi theo kho, lọc theo lớp, phân trang",
    ("API", "GET", "/api/v1/recordings/{recording_id}"): "Thông tin một bản ghi",
    (
        "API",
        "GET",
        "/api/v1/recordings/{recording_id}/timeline",
    ): "Dòng thời gian sự kiện của bản ghi",
    (
        "API",
        "GET",
        "/api/v1/recordings/{recording_id}/caption",
    ): "Mô tả EN/VI kèm sự kiện bằng chứng",
    ("API", "GET", "/api/v1/recordings/{recording_id}/audio"): "Phát lại tệp âm thanh gốc",
    ("API", "POST", "/api/v1/retrieval/parse"): "Câu hỏi tự nhiên → bộ lọc JSON (llama.cpp)",
    ("API", "POST", "/api/v1/retrieval/query"): "Truy hồi theo chế độ và trả lời có bằng chứng",
    ("Suy luận", "GET", "/health"): "Trạng thái nạp mô hình",
    ("Suy luận", "GET", "/v1/models"): "Thông tin mô hình SED, LBR, embedding đã nạp",
    ("Suy luận", "POST", "/v1/analyze"): "Tệp âm thanh → dòng thời gian, mô tả, tài liệu, vector",
    ("Suy luận", "POST", "/v1/embed"): "Nhúng câu hỏi bằng BGE-M3",
}


# ---------------------------------------------------------------- phiên bản
_REQ = re.compile(r"^([A-Za-z0-9_.\-\[\]]+)\s*(.*)$")


def pip_versions(root: Path = ROOT) -> dict[str, str]:
    versions: dict[str, str] = {}
    for path in sorted(root.glob("requirements*.txt")):
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.split("#", 1)[0].strip()
            match = _REQ.match(line)
            if match:
                versions.setdefault(match.group(1).lower(), match.group(2).replace(",", ", "))
    return versions


def npm_versions(path: Path = FRONTEND_PACKAGE) -> dict[str, str]:
    package = json.loads(path.read_text(encoding="utf-8"))
    return {**package.get("devDependencies", {}), **package.get("dependencies", {})}


def compose_images(path: Path = COMPOSE) -> dict[str, str]:
    services = yaml.safe_load(path.read_text(encoding="utf-8"))["services"]
    images = {}
    for service in services.values():
        if "image" in service:
            name, _, tag = service["image"].partition(":")
            images[name] = tag
    return images


def docker_bases(paths: tuple[Path, ...] = DOCKERFILES) -> dict[str, str]:
    bases = {}
    for path in paths:
        for match in re.finditer(
            r"^FROM\s+([\w./-]+):([\w.-]+)", path.read_text(encoding="utf-8"), re.M
        ):
            bases[match.group(1)] = match.group(2)
    return bases


def resolve_version(tech: Tech, sources: dict[str, dict[str, str]]) -> str:
    kind, _, keys = tech.source.partition(":")
    if kind == "llm":
        config = yaml.safe_load(LLM_CONFIG.read_text(encoding="utf-8"))
        return f"build {config['runtime']['build']}; {config['model']['file']}"
    if kind == "compose":
        services = yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))["services"]
        return f"{len(services)} dịch vụ: " + ", ".join(services)
    table, parts = sources[kind], []
    names = keys.split("+")
    for key in names:
        value = table.get(key.lower(), table.get(key))
        if value is None:
            raise KeyError(f"{tech.name}: không thấy {kind}:{key} trong tệp phụ thuộc")
        parts.append(value if len(names) == 1 else f"{key} {value}")
    return "; ".join(parts)


def build_tech_stack(revision: str) -> str:
    sources = {
        "pip": pip_versions(),
        "npm": npm_versions(),
        "image": compose_images(),
        "docker": docker_bases(),
    }
    rows = [[t.layer, t.name, resolve_version(t, sources), t.role, t.adr or "—"] for t in ROLES]
    return render(
        "Công nghệ sử dụng theo tầng",
        ["Tầng", "Công nghệ", "Phiên bản (từ tệp cấu hình)", "Vai trò trong hệ thống", "ADR"],
        rows,
        [
            "requirements*.txt",
            "services/frontend/package.json",
            "docker-compose.yml",
            "services/*/Dockerfile",
            "ml/configs/caption_llm.yaml",
        ],
        revision,
    )


# ---------------------------------------------------------------- endpoint
def _prefix(tree: ast.Module) -> str:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "APIRouter":
            for keyword in node.keywords:
                if keyword.arg == "prefix":
                    return ast.literal_eval(keyword.value)
    return ""


def routes(path: Path) -> list[tuple[str, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    prefix, found = _prefix(tree), []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr in {"get", "post", "put", "delete", "patch"}
                and decorator.args
            ):
                route = ast.literal_eval(decorator.args[0])
                found.append((decorator.func.attr.upper(), prefix + route))
    return found


def build_api(revision: str) -> str:
    found = []
    for path in SERVICE_SOURCES:
        service = "Suy luận" if "inference" in path.parts else "API"
        found.extend((service, method, route) for method, route in routes(path))
    missing = sorted(set(found) - set(ENDPOINTS))
    stale = sorted(set(ENDPOINTS) - set(found))
    if missing or stale:
        raise KeyError(f"endpoint chưa mô tả: {missing}; mô tả không còn trong mã: {stale}")
    rows = [
        [service, method, f"`{route}`", ENDPOINTS[(service, method, route)]]
        for service, method, route in found
    ]
    return render(
        "Các endpoint HTTP của hai dịch vụ",
        ["Dịch vụ", "Phương thức", "Đường dẫn", "Chức năng"],
        rows,
        [path.relative_to(ROOT).as_posix() for path in SERVICE_SOURCES],
        revision,
    )


# ---------------------------------------------------------------- ghi
def render(
    title: str, headers: list[str], rows: list[list[str]], sources: list[str], revision: str
) -> str:
    lines = [
        f"# {title}",
        "",
        f"> Sinh tự động bởi `scripts.report_system_tables` tại git `{revision[:7]}`.",
        "",
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    lines += ["| " + " | ".join(str(c).replace("|", "\\|") for c in row) + " |" for row in rows]
    lines += ["", "**Nguồn:** " + "; ".join(f"`{s}`" for s in sources) + ".", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    revision = git_state(ROOT)["revision"]
    outputs = {"f15_tech_stack.md": build_tech_stack(revision), "f16_api.md": build_api(revision)}
    for name, text in outputs.items():
        (args.output / name).write_text(text, encoding="utf-8")
        print(f"đã ghi {args.output / name}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
