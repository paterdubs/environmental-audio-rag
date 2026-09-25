# API + frontend build in one image (W7 7.4, ADR-0029). Build from the repository root:
#   docker compose --profile app build api
# Inference (torch, GPU, checkpoints) is NOT in this image — it runs on the host.

FROM node:24-slim AS frontend
WORKDIR /frontend
COPY services/frontend/package.json services/frontend/package-lock.json ./
RUN npm ci
COPY services/frontend/ ./
RUN npm run build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt
COPY ml/__init__.py ml/taxonomy.py ml/
COPY ml/configs/ ml/configs/
COPY ml/captioning/ ml/captioning/
COPY ml/retrieval/ ml/retrieval/
COPY services/common/ services/common/
COPY services/api/ services/api/
COPY db/migrations/ db/migrations/
COPY --from=frontend /frontend/dist services/frontend/dist
RUN useradd --create-home app && mkdir -p data/uploads && chown app data/uploads
USER app
EXPOSE 8000
CMD ["uvicorn", "services.api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
