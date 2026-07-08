"""Router: Consulta de equipos tecnologicos."""
from datetime import datetime
from enum import Enum
from typing import Literal, List, Optional

from fastapi import APIRouter, status, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy.orm import Session

from database import get_db
from models import ConsultaEquipo
from email_service import notificar_nueva_cotizacion

router = APIRouter(prefix="/equipos", tags=["equipos"])


class CategoriaEquipo(str, Enum):
    LAPTOP = "laptop"
    PC = "pc"
    PERIFERICO = "periferico"
    COMPONENTE = "componente"


class Presupuesto(str, Enum):
    BAJO = "0-1500"
    MEDIO = "1500-3000"
    ALTO = "3000-6000"
    PREMIUM = "6000+"


class StatusConsulta(str, Enum):
    NUEVA = "nueva"
    COTIZADA = "cotizada"
    FACTURADA = "facturada"
    ENTREGADA = "entregada"
    PERDIDA = "perdida"


class ConsultaRequest(BaseModel):
    nombre_cliente: str = Field(..., min_length=2, max_length=120)
    correo: EmailStr
    categoria: CategoriaEquipo
    presupuesto: Optional[Presupuesto] = None
    detalle: str = Field(..., min_length=10, max_length=2000)


class ConsultaOut(BaseModel):
    id: int
    ticket_id: str
    nombre_cliente: str
    correo: EmailStr
    categoria: CategoriaEquipo
    presupuesto: Optional[Presupuesto] = None
    detalle: str
    status: StatusConsulta
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ConsultaResponse(BaseModel):
    success: Literal[True] = True
    message: str
    ticket_id: str
    data: ConsultaOut


def _ticket() -> str:
    now = datetime.utcnow()
    return "EQP-" + now.strftime("%Y%m%d-%H%M%S") + "-" + f"{now.microsecond // 1000:03d}"


@router.post("/consultar", response_model=ConsultaResponse, status_code=status.HTTP_201_CREATED,
             summary="Solicitar cotizacion de equipos")
def consultar_equipos(payload: ConsultaRequest,
                      background_tasks: BackgroundTasks,
                      db: Session = Depends(get_db)) -> ConsultaResponse:
    ticket_id = _ticket()
    row = ConsultaEquipo(
        ticket_id=ticket_id,
        nombre_cliente=payload.nombre_cliente,
        correo=payload.correo,
        categoria=payload.categoria.value,
        presupuesto=payload.presupuesto.value if payload.presupuesto else None,
        detalle=payload.detalle,
        status=StatusConsulta.NUEVA.value,
    )
    db.add(row); db.commit(); db.refresh(row)

    background_tasks.add_task(
        notificar_nueva_cotizacion,
        tipo="equipos",
        ticket_id=ticket_id,
        nombre_cliente=payload.nombre_cliente,
        correo=payload.correo,
        detalle=(f"Categoria: {payload.categoria.value}\n"
                 f"Presupuesto: {payload.presupuesto.value if payload.presupuesto else 'no indicado'}\n\n"
                 f"{payload.detalle}"),
    )

    return ConsultaResponse(
        message="Consulta recibida. Te enviaremos opciones a tu correo.",
        ticket_id=ticket_id,
        data=ConsultaOut.model_validate(row),
    )


@router.get("/consultas", response_model=List[ConsultaOut],
            summary="Listar consultas de equipos")
def listar(db: Session = Depends(get_db),
           status_filter: Optional[StatusConsulta] = Query(None, alias="status"),
           limit: int = Query(50, ge=1, le=500),
           offset: int = Query(0, ge=0)) -> List[ConsultaOut]:
    q = db.query(ConsultaEquipo)
    if status_filter is not None:
        q = q.filter(ConsultaEquipo.status == status_filter.value)
    rows = q.order_by(ConsultaEquipo.created_at.desc()).offset(offset).limit(limit).all()
    return [ConsultaOut.model_validate(r) for r in rows]


@router.get("/consultas/{ticket_id}", response_model=ConsultaOut,
            summary="Detalle de consulta")
def detalle(ticket_id: str, db: Session = Depends(get_db)) -> ConsultaOut:
    row = db.query(ConsultaEquipo).filter(ConsultaEquipo.ticket_id == ticket_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="No encontrada.")
    return ConsultaOut.model_validate(row)
