# Inference image (W7 7.4, ADR-0033). Build from the repository root:
#   docker compose --profile app build inference
#
# Model weights (SED checkpoints, BGE-M3) are NOT baked in -- they are large binaries that
# change independently of code and the host disk is tight; docker-compose.yml mounts
# ml/runs/ and artifacts/hf/ read-only at run time instead (ml.inference.engine already
# resolves both paths relative to its own file, so no code or env change was needed).
#
# CPU only: torch.cuda.is_available() is False with no GPU device passed to the container, and
# ml.inference.engine.Engine already falls back to CPU in that case. GPU passthrough on Windows
# needs WSL2 + nvidia-container-toolkit configured on the host first (ADR-0029 §8, ADR-0033) --
# out of scope for the demo container.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
# libsndfile1: soundfile/librosa need it at runtime. curl: container healthcheck below.
RUN apt-get update && apt-get install -y --no-install-recommends libsndfile1 curl \
    && rm -rf /var/lib/apt/lists/*
COPY requirements-inference.txt .
RUN pip install --no-cache-dir -r requirements-inference.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu
COPY ml/ ml/
COPY services/common/ services/common/
COPY services/inference/ services/inference/
RUN useradd --create-home app && chown -R app /app
USER app
EXPOSE 8001
# start_period is generous: BGE-M3 + 4 CNN14 checkpoints load in the lifespan startup hook
# before /health can return ready (SYSTEM §4.4), and that read comes off a mounted volume.
HEALTHCHECK --interval=10s --timeout=5s --start-period=90s --retries=15 \
    CMD curl -f http://localhost:8001/health || exit 1
CMD ["uvicorn", "services.inference.app.main:app", "--host", "0.0.0.0", "--port", "8001"]
