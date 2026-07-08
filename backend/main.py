"""
Athenec - Punto de entrada de la API
====================================
FastAPI + CORS + inclusion de routers + creacion de tablas al iniciar.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database import Base, engine
import models  # noqa: F401  -> registra los modelos en Base.metadata
from routers import soluciones

# ----------------------------------------------------------------------
# Configuracion
# ----------------------------------------------------------------------
load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
API_PREFIX = os.getenv("API_PREFIX", "/api")
FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:5173,http://localhost:3000",
)
ALLOWED_ORIGINS = [o.strip() for o in FRONTEND_ORIGIN.split(",") if o.strip()]


# ----------------------------------------------------------------------
# Ciclo de vida: crear tablas al arrancar
# ----------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea las tablas si no existen (idempotente)."""
    Base.metadata.create_all(bind=engine)
    yield
    # Nada que limpiar por ahora.


# ----------------------------------------------------------------------
# App
# ----------------------------------------------------------------------
app = FastAPI(
    title="Athenec API",
    description=(
        "API RESTful de Athenec: soluciones tecnologicas, asesoria academica y venta de equipos."
    ),
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
# Endpoints de salud
# ----------------------------------------------------------------------
@app.get("/", tags=["health"])
def root():
    return {
        "service": "Athenec API",
        "version": app.version,
        "environment": ENVIRONMENT,
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


# ----------------------------------------------------------------------
# Registro de routers
# ----------------------------------------------------------------------
app.include_router(soluciones.router, prefix=API_PREFIX)


# ----------------------------------------------------------------------
# Ejecucion directa
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=ENVIRONMENT == "development",
    )
