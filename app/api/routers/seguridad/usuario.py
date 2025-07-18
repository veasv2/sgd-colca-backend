# app/api/routers/seguridad/usuario.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Schemas para filtros y listas
from app.schemas.seguridad.usuario.usuario_filter_schemas import (
    UsuarioListaRequest,
    UsuarioListaResponse
)

# Schemas para resúmenes
from app.schemas.seguridad.usuario.usuario_summary_schemas import (
    UsuarioSummaryRequest,
    UsuarioSummaryResponse
)

from app.services.seguridad.usuario_service import usuario_service
from app.core.database import get_database

router = APIRouter(
    prefix="/seguridad/usuario",
    tags=["usuario"]
)

@router.post("/lista", response_model=UsuarioListaResponse)
def lista_usuarios(
    request: UsuarioListaRequest,
    db: Session = Depends(get_database)
):   
    """Obtiene la lista paginada de usuarios con filtros y ordenamiento"""
    return usuario_service.lista_usuario(db=db, request=request)

@router.post("/resumen", response_model=UsuarioSummaryResponse)
def resumen_usuarios(
    request: UsuarioSummaryRequest,
    db: Session = Depends(get_database)
):
    """Genera resumen agrupado de usuarios"""
    return usuario_service.resumen_usuario(db=db, request=request)