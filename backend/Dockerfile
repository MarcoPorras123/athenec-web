# ============================================================
# Athenec - Backend (FastAPI)
# Imagen final < 200MB con python:3.11-slim
# ============================================================

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dependencias del sistema minimas (curl para healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cachea capa de dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt

# Codigo
COPY . .

# Usuario no-root para seguridad
RUN groupadd -r athenec && useradd -r -g athenec athenec \
    && mkdir -p /app/data && chown -R athenec:athenec /app
USER athenec

# Persistir SQLite en /app/data (volumen)
ENV DATABASE_URL=sqlite:////app/data/athenec.db

EXPOSE 8000

# Healthcheck contra /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# En produccion se recomienda 2-4 workers segun CPU. Sin --reload.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
