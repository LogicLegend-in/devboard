FROM python:3.12-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

# Install runtime libpq for PostgreSQL support and curl for diagnostics
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

COPY --from=builder /root/.local /home/appuser/.local

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app:/app/backend
ENV PYTHONUNBUFFERED=1
ENV PORT=8004
ENV HOST=0.0.0.0
ENV ENVIRONMENT=production

# Copy application sources, frontend assets, and shared library
COPY shared/ /app/shared/
COPY backend/app/ /app/backend/app/
COPY backend/app/ /app/app/
COPY frontend/ /app/frontend/

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8004

HEALTHCHECK --interval=20s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request, os; port = os.getenv('PORT', '8004'); urllib.request.urlopen(f'http://localhost:{port}/health')"

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8004} --workers ${WORKERS:-2}"]
