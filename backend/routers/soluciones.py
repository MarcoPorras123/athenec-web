"""
Router: Soluciones Tecnologicas
================================
Endpoints relacionados con solicitudes de cotizacion
para desarrollo de software a medida.
"""

from datetime import datetime
from enum import Enum
from typing import Literal

from fastapi import APIRouter, status
from pydantic import BaseModel, EmailStr, Field

router = APIRouter(
    prefix="/soluciones",
    tags=["soluciones"],
)


# ----------------------------------------------------------------------
# Schemas (Pydantic v2)
# ----------------------------------------------------------------------
class TipoProyecto(str, Enum):
    WEB = "web"
    MOVIL = "movil"
    AUTOMATIZACION = "automatizacion"
    INTEGRACION = "integracion"
    DATOS = "datos"
    OTRO = "otro"


class CotizacionRequest(BaseModel):
    """Payload de entrada validado por Pydantic."""
    nombre_cliente: str = Field(
        ...,
        min_length=2,
        max_length=120,
        description="Nombre completo del solicitante.",
        examples=["Maria Perez"],
    )
    correo: EmailStr = Field(
        ...,
        description="Correo electronico de contacto.",
        examples=["maria@example.com"],
    )
    tipo_proyecto: TipoProyecto = Field(
        ...,
        description="Categoria del proyecto solicitado.",
        examples=["web"],
    )
    descripcion: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Detalle del proyecto a cotizar.",
        examples=["Necesito una tienda online con pasarela de pagos."],
    )


class CotizacionResponse(BaseModel):
    """Respuesta de confirmacion."""
    success: Literal[True] = True
    message: str
    ticket_id: str
    data: CotizacionRequest


# ----------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------
def _generar_ticket_id() -> str:
    """Genera un ID de ticket legible: COT-YYYYMMDD-HHMMSS."""
    return "COT-" + datetime.utcnow().strftime("%Y%m%d-%H%M%S")


# ----------------------------------------------------------------------
# Endpoints
# ----------------------------------------------------------------------
@router.post(
    "/cotizar",
    response_model=CotizacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar cotizacion de un proyecto de software",
)
def cotizar_solucion(payload: CotizacionRequest) -> CotizacionResponse:
    """
    Recibe una solicitud de cotizacion y devuelve una confirmacion.

    En una version futura este endpoint:
    - Persistira la solicitud en base de datos (SQLAlchemy).
    - Enviara notificacion por correo al equipo comercial.
    - Encolara la tarea en SQS / background task.
    """
    ticket_id = _generar_ticket_id()

    # TODO: persistir en base de datos
    # TODO: enviar correo de notificacion

    return CotizacionResponse(
        message="Cotizacion recibida correctamente. Te contactaremos pronto.",
        ticket_id=ticket_id,
        data=payload,
    )
