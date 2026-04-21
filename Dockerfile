FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_NO_CACHE=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY README* ./

RUN uv pip install --system --no-cache -e . || true

COPY . .

RUN uv pip install --system --no-cache \
    fastapi \
    "uvicorn[standard]" \
    python-docx \
    openpyxl \
    python-pptx

RUN groupadd --system gendoctools \
    && useradd --system --gid gendoctools --home-dir /app gendoctools \
    && mkdir -p /data \
    && chown -R gendoctools:gendoctools /app /data

USER gendoctools

EXPOSE 8017

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://127.0.0.1:${PORT:-8017}/health || exit 1

CMD ["python", "openai_tool_server.py"]
