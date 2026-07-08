"""
Router: Soluciones Tecnologicas
================================
Endpoints:
- POST /soluciones/cotizar         -> crea y persiste una cotizacion
- GET  /soluciones/cotizaciones    -> lista cotizaciones (uso interno / admin)
- GET  /soluciones/cotizaciones/{ticket_id}  -> detalle
"""

from datetime import datetime
from enum import Enum
from typing import Literal, List, Optional

from fastapi import APIRouter, status, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy.orm import Session

from database import get_db
from models import Cotizacion

router = APIRouter(
    prefix="/soluciones",
    tags=["soluciones"],
)


# ----------------------------------------------------------------------
# Schemas
# ----------------------------------------------------------------------
class TipoProyecto(str, Enum):
    WEB = "web"
    MOVIL = "movil"
    AUTOMATIZACION = "automatizacion"
    INTEGRACION = "integracion"
    DATOS = "datos"
    OTRO = "otro"


class StatusCotizacion(str, Enum):
    NUEVA = "nueva"
    CONTACTADA = "contactada"
    COTIZADA = "cotizada"
    GANADA = "ganada"
    PERDIDA = "perdida"


class CotizacionRequest(BaseModel):
    nombre_cliente: str = Field(..., min_length=2, max_length=120, examples=["Maria Perez"])
    correo: EmailStr = Field(..., examples=["maria@example.com"])
    tipo_proyecto: TipoProyecto = Field(..., examples=["web"])
    descripcion: str = Field(..., min_length=10, max_length=2000)


class CotizacionOut(BaseModel):
    """Representacion de una cotizacion persistida."""
    id: int
    ticket_id: str
    nombre_cliente: str
    correo: EmailStr
    tipo_proyecto: TipoProyecto
    descripcion: str
    status: StatusCotizacion
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CotizacionResponse(BaseModel):
    """Respuesta de la creacion."""
    success: Literal[True] = True
    message: str
    ticket_id: str
    data: CotizacionOut


# ----------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------
def _generar_ticket_id() -> str:
    """COT-YYYYMMDD-HHMMSS-<3digitos microseg> (UTC) - a prueba de colisiones intra-segundo."""
    now = datetime.utcnow()
    return "COT-" + now.strftime("%Y%m%d-%H%M%S") + "-" + f"{now.microsecond // 1000:03d}"


# ----------------------------------------------------------------------
# Endpoints
# ----------------------------------------------------------------------
@router.post(
    "/cotizar",
    response_model=CotizacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar cotizacion de un proyecto de software",
)
def cotizar_solucion(
    payload: CotizacionRequest,
    db: Session = Depends(get_db),
) -> CotizacionResponse:
    """
    Recibe una solicitud de cotizacion, la persiste en base de datos
    y devuelve una confirmacion con ticket_id.
    """
    ticket_id = _generar_ticket_id()

    cotizacion = Cotizacion(
        ticket_id=ticket_id,
        nombre_cliente=payload.nombre_cliente,
        correo=payload.correo,
        tipo_proyecto=payload.tipo_proyecto.value,
        descripcion=payload.descripcion,
        status=StatusCotizacion.NUEVA.value,
    )
    db.add(cotizacion)
    db.commit()
    db.refresh(cotizacion)

    return CotizacionResponse(
        message="Cotizacion recibida correctamente. Te contactaremos pronto.",
        ticket_id=ticket_id,
        data=CotizacionOut.model_validate(cotizacion),
    )


@router.get(
    "/cotizaciones",
    response_model=List[CotizacionOut],
    summary="Listar cotizaciones (uso interno)",
)
def listar_cotizaciones(
    db: Session = Depends(get_db),
    status_filter: Optional[StatusCotizacion] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> List[CotizacionOut]:
    """Listado paginado, opcionalmente filtrado por status. Mas recientes primero."""
    query = db.query(Cotizacion)
    if status_filter is not None:
        query = query.filter(Cotizacion.status == status_filter.value)
    rows = (
        query.order_by(Cotizacion.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [CotizacionOut.model_validate(r) for r in rows]


@router.get(
    "/cotizaciones/{ticket_id}",
    response_model=CotizacionOut,
    summary="Detalle de una cotizacion por ticket_id",
)
def obtener_cotizacion(
    ticket_id: str,
    db: Session = Depends(get_db),
) -> CotizacionOut:
    row = db.query(Cotizacion).filter(Cotizacion.ticket_id == ticket_id).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Cotizacion {ticket_id} no encontrada.")
    return CotizacionOut.model_validate(row)
