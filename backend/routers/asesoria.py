"""Router: Asesoria de tesis."""
from datetime import datetime
from enum import Enum
from typing import Literal, List, Optional

from fastapi import APIRouter, status, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy.orm import Session

from database import get_db
from models import AsesoriaSolicitud
from email_service import notificar_nueva_cotizacion

router = APIRouter(prefix="/asesoria", tags=["asesoria"])


class NivelAcademico(str, Enum):
    PREGRADO = "pregrado"
    MAESTRIA = "maestria"
    DOCTORADO = "doctorado"


class FaseTesis(str, Enum):
    INICIO = "inicio"
    METODOLOGIA = "metodologia"
    RESULTADOS = "resultados"
    SUSTENTACION = "sustentacion"


class StatusSolicitud(str, Enum):
    NUEVA = "nueva"
    CONTACTADA = "contactada"
    EN_ASESORIA = "en_asesoria"
    FINALIZADA = "finalizada"
    PERDIDA = "perdida"


class AsesoriaRequest(BaseModel):
    nombre_cliente: str = Field(..., min_length=2, max_length=120)
    correo: EmailStr
    nivel: NivelAcademico
    tema: str = Field(..., min_length=3, max_length=255)
    fase: FaseTesis
    descripcion: str = Field(..., min_length=10, max_length=2000)


class AsesoriaOut(BaseModel):
    id: int
    ticket_id: str
    nombre_cliente: str
    correo: EmailStr
    nivel: NivelAcademico
    tema: str
    fase: FaseTesis
    descripcion: str
    status: StatusSolicitud
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AsesoriaResponse(BaseModel):
    success: Literal[True] = True
    message: str
    ticket_id: str
    data: AsesoriaOut


def _ticket() -> str:
    now = datetime.utcnow()
    return "ASE-" + now.strftime("%Y%m%d-%H%M%S") + "-" + f"{now.microsecond // 1000:03d}"


@router.post("/solicitar", response_model=AsesoriaResponse, status_code=status.HTTP_201_CREATED,
             summary="Solicitar asesoria de tesis")
def solicitar_asesoria(payload: AsesoriaRequest,
                       background_tasks: BackgroundTasks,
                       db: Session = Depends(get_db)) -> AsesoriaResponse:
    ticket_id = _ticket()
    row = AsesoriaSolicitud(
        ticket_id=ticket_id,
        nombre_cliente=payload.nombre_cliente,
        correo=payload.correo,
        nivel=payload.nivel.value,
        tema=payload.tema,
        fase=payload.fase.value,
        descripcion=payload.descripcion,
        status=StatusSolicitud.NUEVA.value,
    )
    db.add(row); db.commit(); db.refresh(row)

    background_tasks.add_task(
        notificar_nueva_cotizacion,
        tipo="asesoria",
        ticket_id=ticket_id,
        nombre_cliente=payload.nombre_cliente,
        correo=payload.correo,
        detalle=(f"Nivel: {payload.nivel.value}\nFase: {payload.fase.value}\n"
                 f"Tema: {payload.tema}\n\n{payload.descripcion}"),
    )

    return AsesoriaResponse(
        message="Solicitud recibida. Te contactaremos para agendar tu sesion.",
        ticket_id=ticket_id,
        data=AsesoriaOut.model_validate(row),
    )


@router.get("/solicitudes", response_model=List[AsesoriaOut],
            summary="Listar solicitudes de asesoria")
def listar(db: Session = Depends(get_db),
           status_filter: Optional[StatusSolicitud] = Query(None, alias="status"),
           limit: int = Query(50, ge=1, le=500),
           offset: int = Query(0, ge=0)) -> List[AsesoriaOut]:
    q = db.query(AsesoriaSolicitud)
    if status_filter is not None:
        q = q.filter(AsesoriaSolicitud.status == status_filter.value)
    rows = q.order_by(AsesoriaSolicitud.created_at.desc()).offset(offset).limit(limit).all()
    return [AsesoriaOut.model_validate(r) for r in rows]


@router.get("/solicitudes/{ticket_id}", response_model=AsesoriaOut,
            summary="Detalle de solicitud de asesoria")
def detalle(ticket_id: str, db: Session = Depends(get_db)) -> AsesoriaOut:
    row = db.query(AsesoriaSolicitud).filter(AsesoriaSolicitud.ticket_id == ticket_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="No encontrada.")
    return AsesoriaOut.model_validate(row)
