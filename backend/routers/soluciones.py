"""Router: Soluciones Tecnologicas (con auth en endpoints internos)."""
import csv
import io
from datetime import datetime
from enum import Enum
from typing import Literal, List, Optional

from fastapi import APIRouter, status, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy.orm import Session

from database import get_db
from models import Cotizacion
from email_service import notificar_nueva_cotizacion
from auth import verify_admin_token

router = APIRouter(prefix="/soluciones", tags=["soluciones"])


class TipoProyecto(str, Enum):
    WEB = "web"; MOVIL = "movil"; AUTOMATIZACION = "automatizacion"
    INTEGRACION = "integracion"; DATOS = "datos"; OTRO = "otro"


class StatusCotizacion(str, Enum):
    NUEVA = "nueva"; CONTACTADA = "contactada"; COTIZADA = "cotizada"
    GANADA = "ganada"; PERDIDA = "perdida"


class CotizacionRequest(BaseModel):
    nombre_cliente: str = Field(..., min_length=2, max_length=120)
    correo: EmailStr
    tipo_proyecto: TipoProyecto
    descripcion: str = Field(..., min_length=10, max_length=2000)


class CotizacionOut(BaseModel):
    id: int; ticket_id: str; nombre_cliente: str; correo: EmailStr
    tipo_proyecto: TipoProyecto; descripcion: str
    status: StatusCotizacion; created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CotizacionResponse(BaseModel):
    success: Literal[True] = True
    message: str; ticket_id: str; data: CotizacionOut


class StatusUpdateRequest(BaseModel):
    status: StatusCotizacion


def _ticket() -> str:
    now = datetime.utcnow()
    return "COT-" + now.strftime("%Y%m%d-%H%M%S") + "-" + f"{now.microsecond // 1000:03d}"


# ---- PUBLICO ----
@router.post("/cotizar", response_model=CotizacionResponse, status_code=status.HTTP_201_CREATED,
             summary="Solicitar cotizacion (publico)")
def cotizar_solucion(payload: CotizacionRequest,
                     background_tasks: BackgroundTasks,
                     db: Session = Depends(get_db)) -> CotizacionResponse:
    tid = _ticket()
    row = Cotizacion(
        ticket_id=tid, nombre_cliente=payload.nombre_cliente, correo=payload.correo,
        tipo_proyecto=payload.tipo_proyecto.value, descripcion=payload.descripcion,
        status=StatusCotizacion.NUEVA.value,
    )
    db.add(row); db.commit(); db.refresh(row)
    background_tasks.add_task(
        notificar_nueva_cotizacion, tipo="soluciones", ticket_id=tid,
        nombre_cliente=payload.nombre_cliente, correo=payload.correo,
        detalle=f"Tipo proyecto: {payload.tipo_proyecto.value}\n\n{payload.descripcion}",
    )
    return CotizacionResponse(
        message="Cotizacion recibida correctamente. Te contactaremos pronto.",
        ticket_id=tid, data=CotizacionOut.model_validate(row),
    )


# ---- PROTEGIDO ----
@router.get("/cotizaciones", response_model=List[CotizacionOut],
            summary="Listar cotizaciones (auth)", dependencies=[Depends(verify_admin_token)])
def listar(db: Session = Depends(get_db),
           status_filter: Optional[StatusCotizacion] = Query(None, alias="status"),
           limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)) -> List[CotizacionOut]:
    q = db.query(Cotizacion)
    if status_filter is not None:
        q = q.filter(Cotizacion.status == status_filter.value)
    rows = q.order_by(Cotizacion.created_at.desc()).offset(offset).limit(limit).all()
    return [CotizacionOut.model_validate(r) for r in rows]


@router.get("/cotizaciones/export", summary="Exportar CSV (auth)",
            dependencies=[Depends(verify_admin_token)])
def exportar_csv(db: Session = Depends(get_db)) -> StreamingResponse:
    rows = db.query(Cotizacion).order_by(Cotizacion.created_at.desc()).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id","ticket_id","nombre_cliente","correo","tipo_proyecto","descripcion","status","created_at"])
    for r in rows:
        w.writerow([r.id, r.ticket_id, r.nombre_cliente, r.correo, r.tipo_proyecto,
                    r.descripcion, r.status, r.created_at.isoformat()])
    buf.seek(0)
    filename = f"cotizaciones_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/cotizaciones/{ticket_id}", response_model=CotizacionOut,
            summary="Detalle (auth)", dependencies=[Depends(verify_admin_token)])
def detalle(ticket_id: str, db: Session = Depends(get_db)) -> CotizacionOut:
    row = db.query(Cotizacion).filter(Cotizacion.ticket_id == ticket_id).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Cotizacion {ticket_id} no encontrada.")
    return CotizacionOut.model_validate(row)


@router.patch("/cotizaciones/{ticket_id}", response_model=CotizacionOut,
              summary="Actualizar status (auth)", dependencies=[Depends(verify_admin_token)])
def patch_status(ticket_id: str, payload: StatusUpdateRequest,
                 db: Session = Depends(get_db)) -> CotizacionOut:
    row = db.query(Cotizacion).filter(Cotizacion.ticket_id == ticket_id).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Cotizacion {ticket_id} no encontrada.")
    row.status = payload.status.value
    db.commit(); db.refresh(row)
    return CotizacionOut.model_validate(row)
