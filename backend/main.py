"""
Athenec - Punto de entrada de la API
====================================
Aplicacion FastAPI con:
- Configuracion via .env
- Middleware CORS
- Inclusion ordenada de routers modulares
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Routers
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
# Instancia FastAPI
# ----------------------------------------------------------------------
app = FastAPI(
    title="Athenec API",
    description=(
        "API RESTful de Athenec para las tres lineas de negocio: "
        "soluciones tecnologicas, asesoria academica y venta de equipos."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ----------------------------------------------------------------------
# Middleware CORS
# ----------------------------------------------------------------------
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
    """Mensaje raiz de bienvenida."""
    return {
        "service": "Athenec API",
        "version": app.version,
        "environment": ENVIRONMENT,
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
def health():
    """Chequeo de salud para monitores / load balancers."""
    return {"status": "ok"}


# ----------------------------------------------------------------------
# Registro ordenado de routers
# ----------------------------------------------------------------------
app.include_router(soluciones.router, prefix=API_PREFIX)

# Futuros:
# from routers import asesoria, equipos, auth
# app.include_router(asesoria.router, prefix=API_PREFIX)
# app.include_router(equipos.router, prefix=API_PREFIX)
# app.include_router(auth.router, prefix=API_PREFIX)


# ----------------------------------------------------------------------
# Ejecucion directa (para debug local)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=ENVIRONMENT == "development",
    )
