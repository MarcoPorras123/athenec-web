"""
Athenec - Modelos de dominio (SQLAlchemy)
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from database import Base


class Cotizacion(Base):
    """
    Registro de una solicitud de cotizacion recibida
    desde el formulario de Soluciones Tecnologicas.
    """
    __tablename__ = "cotizaciones"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(32), unique=True, index=True, nullable=False)

    nombre_cliente = Column(String(120), nullable=False)
    correo = Column(String(255), nullable=False, index=True)
    tipo_proyecto = Column(String(32), nullable=False)
    descripcion = Column(Text, nullable=False)

    # Estado del ciclo comercial
    # nueva | contactada | cotizada | ganada | perdida
    status = Column(String(16), nullable=False, default="nueva")

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<Cotizacion id={self.id} ticket={self.ticket_id} status={self.status}>"


# Indice compuesto: consultas frecuentes por (status, fecha) para el panel comercial
Index("ix_cotizaciones_status_created", Cotizacion.status, Cotizacion.created_at)
