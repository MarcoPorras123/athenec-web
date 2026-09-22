"""
Athenec - Entrypoint unico de la API
=====================================
Sirve para dos destinos:
  * Vercel  -> el runtime @vercel/python detecta el objeto ASGI `app`
  * Docker  -> uvicorn index:app

Las rutas se registran bajo API_PREFIX (/api) para que en Vercel
la URL publica /api/... caiga directamente en el router correcto.
"""

import os
import sys

# Garantiza que los modulos hermanos (database, models, routers...) sean
# importables tanto en Vercel como en local, sin depender del cwd.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database import Base, engine
import models  # noqa: F401  -> registra los modelos en Base.metadata
from routers import soluciones, asesoria, equipos

# ----------------------------------------------------------------------
# Configuracion
# ----------------------------------------------------------------------
load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
API_PREFIX = os.getenv("API_PREFIX", "/api")

# En Vercel el frontend se sirve desde el mismo dominio, por lo que las
# peticiones son same-origin y CORS no aplica. Igual dejamos la lista
# configurable para entornos con dominios separados.
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "").strip()
if FRONTEND_ORIGIN:
    ALLOWED_ORIGINS = [o.strip() for o in FRONTEND_ORIGIN.split(",") if o.strip()]
else:
    ALLOWED_ORIGINS = ["*"]


# ----------------------------------------------------------------------
# Ciclo de vida
# ----------------------------------------------------------------------
_TABLES_READY = False


def _ensure_tables() -> None:
    """Crea las tablas si no existen. Idempotente y tolerante a fallos
    para no tumbar un cold start de serverless si la DB tarda."""
    global _TABLES_READY
    if _TABLES_READY:
        return
    try:
        Base.metadata.create_all(bind=engine)
        _TABLES_READY = True
    except Exception as exc:  # pragma: no cover
        print(f"[athenec] aviso: no se pudieron crear las tablas todavia: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_tables()
    yield


# ----------------------------------------------------------------------
# App
# ----------------------------------------------------------------------
app = FastAPI(
    title="Athenec API",
    description=(
        "API RESTful de Athenec: soluciones tecnologicas, "
        "asesoria academica y venta de equipos."
    ),
    version="0.3.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------------
# Health
# ----------------------------------------------------------------------
@app.get("/api", tags=["health"])
def root():
    return {
        "service": "Athenec API",
        "version": app.version,
        "environment": ENVIRONMENT,
        "docs": "/api/docs",
    }


@app.get("/api/health", tags=["health"])
def health():
    _ensure_tables()
    return {"status": "ok", "environment": ENVIRONMENT}


# ----------------------------------------------------------------------
# Routers
# ----------------------------------------------------------------------
app.include_router(soluciones.router, prefix=API_PREFIX)
app.include_router(asesoria.router, prefix=API_PREFIX)
app.include_router(equipos.router, prefix=API_PREFIX)


# ----------------------------------------------------------------------
# Ejecucion directa (Docker / local)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "index:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=ENVIRONMENT == "development",
    )
