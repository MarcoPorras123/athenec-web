"""
Athenec - Configuracion de base de datos
=========================================
Motor SQLAlchemy 2.x listo para SQLite en local
y PostgreSQL / AWS RDS en produccion (solo cambia DATABASE_URL).
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./athenec.db")

# SQLite necesita connect_args especial para permitir uso desde threads.
# Postgres / MySQL no lo requiere.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,   # ponlo True para ver el SQL en consola
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()


def get_db():
    """Dependency de FastAPI: yield una sesion y la cierra siempre."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
