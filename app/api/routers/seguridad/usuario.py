# app/api/routers/seguridad/usuario.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Schemas para filtros
from app.schemas.seguridad.usuario_filter_schemas import (
    UsuarioListaRequest,
    UsuarioListaResponse
)

from app.services.seguridad.usuario_service import usuario_service
from app.core.database import get_database

router = APIRouter(
    prefix="/seguridad/usuario",  # ← Corregido: "seguridad" (no "segruidad")
    tags=["usuario"]
)

@router.post("/lista", response_model=UsuarioListaResponse)
def lista_usuarios(  # ← Corregido: plural "usuarios" (no "usuario")
    request: UsuarioListaRequest,
    db: Session = Depends(get_database)
):   
    return usuario_service.lista_usuarios(db=db, request=request)