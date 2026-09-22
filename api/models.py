"""
Athenec - Modelos de dominio (SQLAlchemy)
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from database import Base


class Cotizacion(Base):
    """Solicitud desde el form de Soluciones Tecnologicas."""
    __tablename__ = "cotizaciones"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(32), unique=True, index=True, nullable=False)
    nombre_cliente = Column(String(120), nullable=False)
    correo = Column(String(255), nullable=False, index=True)
    tipo_proyecto = Column(String(32), nullable=False)
    descripcion = Column(Text, nullable=False)
    status = Column(String(16), nullable=False, default="nueva")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<Cotizacion id={self.id} ticket={self.ticket_id} status={self.status}>"


Index("ix_cotizaciones_status_created", Cotizacion.status, Cotizacion.created_at)


class AsesoriaSolicitud(Base):
    """Solicitud desde el form de Asesoria de Tesis."""
    __tablename__ = "asesorias"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(32), unique=True, index=True, nullable=False)
    nombre_cliente = Column(String(120), nullable=False)
    correo = Column(String(255), nullable=False, index=True)
    nivel = Column(String(32), nullable=False)  # pregrado, maestria, doctorado
    tema = Column(String(255), nullable=False)
    fase = Column(String(32), nullable=False)   # inicio, metodologia, resultados, sustentacion
    descripcion = Column(Text, nullable=False)
    status = Column(String(16), nullable=False, default="nueva")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


Index("ix_asesorias_status_created", AsesoriaSolicitud.status, AsesoriaSolicitud.created_at)


class ConsultaEquipo(Base):
    """Consulta desde el form de Equipos Tecnologicos."""
    __tablename__ = "consultas_equipos"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(32), unique=True, index=True, nullable=False)
    nombre_cliente = Column(String(120), nullable=False)
    correo = Column(String(255), nullable=False, index=True)
    categoria = Column(String(32), nullable=False)  # laptop, pc, periferico, componente
    presupuesto = Column(String(32), nullable=True)  # rango textual
    detalle = Column(Text, nullable=False)
    status = Column(String(16), nullable=False, default="nueva")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


Index("ix_equipos_status_created", ConsultaEquipo.status, ConsultaEquipo.created_at)
