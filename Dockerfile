# ── Stage 1: build React frontend ──────────────────────────────────────────
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --frozen-lockfile 2>/dev/null || npm install
COPY frontend/ .
RUN npm run build

# ── Stage 2: Python runtime ─────────────────────────────────────────────────
FROM python:3.11-slim
WORKDIR /app

# System deps for lxml / python-pptx
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency installation
RUN pip install uv

# Copy dependency manifest and install
COPY pyproject.toml ./
RUN uv pip install --system "fastapi>=0.111" "uvicorn[standard]>=0.29" \
    "python-multipart>=0.0.9" "requests>=2.31" "python-pptx>=1.0.2" "lxml"

# Copy application source
COPY src/ ./src/

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

EXPOSE ${PORT:-11451}

CMD ["sh", "-c", "uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT:-11451}"]
