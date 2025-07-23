# app/api/routers/seguridad/usuario_routers.py

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


# Schemas para CRUD
from app.schemas.seguridad.usuario.usuario_schemas import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioInDB
)
from app.services.seguridad.usuario_service import usuario_service
from app.core.database import get_database

router  = APIRouter(
    prefix="/seguridad/usuario",
    tags=["usuario"]
)

@router .post("/lista", response_model=UsuarioListaResponse)
def lista_usuarios(
    request: UsuarioListaRequest,
    db: Session = Depends(get_database)
):   
    """Obtiene la lista paginada de usuarios con filtros y ordenamiento"""
    return usuario_service.lista_usuario(db=db, request=request)

@router .post("/resumen", response_model=UsuarioSummaryResponse)
def resumen_usuarios(
    request: UsuarioSummaryRequest,
    db: Session = Depends(get_database)
):
    """Genera resumen agrupado de usuarios"""
    return usuario_service.resumen_usuario(db=db, request=request)

# --- CRUD Endpoints ---

@router.post("/", response_model=UsuarioInDB)
def crear_usuario(request: UsuarioCreate, db: Session = Depends(get_database)):
    """Crear un nuevo usuario"""
    return usuario_service.crear_usuario(db=db, obj_in=request)

@router.get("/{uuid}", response_model=UsuarioInDB)
def obtener_usuario(uuid: str, db: Session = Depends(get_database)):
    """Obtener usuario por ID"""
    usuario = usuario_service.obtener_usuario(db=db, uuid=uuid)
    if not usuario:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.put("/{uuid}", response_model=UsuarioInDB)
def actualizar_usuario(uuid: str, request: UsuarioUpdate, db: Session = Depends(get_database)):
    """Actualizar usuario por ID"""
    usuario = usuario_service.actualizar_usuario(db=db, uuid=uuid, obj_in=request)
    if not usuario:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.delete("/{uuid}", response_model=UsuarioInDB)
def eliminar_usuario(uuid: str, db: Session = Depends(get_database)):
    """Eliminar usuario por ID"""
    usuario = usuario_service.eliminar_usuario(db=db, uuid=uuid)
    if not usuario:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario