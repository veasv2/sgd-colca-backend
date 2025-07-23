# app/api/routers/seguridad/usuario_routers.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

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

from app.core.deps import get_async_db, get_usuario_service
from app.services.seguridad.usuario_service import UsuarioService

router = APIRouter(
    prefix="/seguridad/usuario",
    tags=["usuario"]
)

@router.post("/lista", response_model=UsuarioListaResponse)
async def lista_usuarios(
    request: UsuarioListaRequest,
    db: AsyncSession = Depends(get_async_db),
    usuario_service: UsuarioService = Depends(get_usuario_service)
):   
    """Obtiene la lista paginada de usuarios con filtros y ordenamiento"""
    return await usuario_service.lista_usuario(db=db, request=request)

@router.post("/resumen", response_model=UsuarioSummaryResponse)
async def resumen_usuarios(
    request: UsuarioSummaryRequest,
    db: AsyncSession = Depends(get_async_db),
    usuario_service: UsuarioService = Depends(get_usuario_service)
):
    """Genera resumen agrupado de usuarios"""
    return await usuario_service.resumen_usuario(db=db, request=request)

# --- CRUD Endpoints ---

@router.post("/", response_model=UsuarioInDB, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    request: UsuarioCreate, 
    db: AsyncSession = Depends(get_async_db),
    usuario_service: UsuarioService = Depends(get_usuario_service)
):
    """Crear un nuevo usuario"""
    return await usuario_service.crear_usuario(db=db, obj_in=request)

@router.get("/{uuid}", response_model=UsuarioInDB)
async def obtener_usuario(
    uuid: str, 
    db: AsyncSession = Depends(get_async_db),
    usuario_service: UsuarioService = Depends(get_usuario_service)
):
    """Obtener usuario por UUID"""
    try:
        return await usuario_service.obtener_usuario(db=db, uuid=uuid)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.put("/{uuid}", response_model=UsuarioInDB)
async def actualizar_usuario(
    uuid: str, 
    request: UsuarioUpdate, 
    db: AsyncSession = Depends(get_async_db),
    usuario_service: UsuarioService = Depends(get_usuario_service)
):
    """Actualizar usuario por UUID"""
    try:
        return await usuario_service.actualizar_usuario(db=db, uuid=uuid, obj_in=request)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.delete("/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_usuario(
    uuid: str, 
    db: AsyncSession = Depends(get_async_db),
    usuario_service: UsuarioService = Depends(get_usuario_service)
):
    """Eliminar usuario por UUID"""
    success = await usuario_service.eliminar_usuario(db=db, uuid=uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")