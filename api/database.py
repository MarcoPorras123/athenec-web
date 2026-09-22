"""
Athenec - Configuracion de base de datos
=========================================
Funciona igual en local (SQLite), Docker (Postgres) y Vercel
(Postgres gestionado: Neon / Vercel Postgres / Supabase).

Normaliza automaticamente las URLs que entregan los proveedores
gestionados, que suelen venir en formato `postgres://` (no aceptado
por SQLAlchemy 2.x) y sin driver explicito.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()


def _normalizar_url(url: str) -> str:
    """Convierte las variantes que usan los proveedores gestionados
    a la forma que espera SQLAlchemy 2.x con psycopg2."""
    if not url:
        return "sqlite:///./athenec.db"
    # Heroku/Neon/Vercel entregan `postgres://`
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    # `postgresql://` sin driver -> fijamos psycopg2
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


# Vercel Postgres expone varias env vars; tomamos la primera disponible.
RAW_URL = (
    os.getenv("DATABASE_URL")
    or os.getenv("POSTGRES_URL")
    or os.getenv("POSTGRES_PRISMA_URL")
    or "sqlite:///./athenec.db"
)
DATABASE_URL = _normalizar_url(RAW_URL)

ES_SQLITE = DATABASE_URL.startswith("sqlite")
# En serverless cada invocacion es efimera: un pool persistente no aporta
# y agota las conexiones del proveedor. NullPool abre y cierra por request.
ES_SERVERLESS = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

connect_args = {}
engine_kwargs = {"echo": False, "future": True}

if ES_SQLITE:
    connect_args["check_same_thread"] = False
else:
    # Los Postgres gestionados exigen TLS.
    connect_args["sslmode"] = os.getenv("PGSSLMODE", "require")
    connect_args["connect_timeout"] = 10

if ES_SERVERLESS:
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300

engine = create_engine(DATABASE_URL, connect_args=connect_args, **engine_kwargs)

SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, future=True
)

Base = declarative_base()


def get_db():
    """Dependency de FastAPI: yield una sesion y la cierra siempre."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
