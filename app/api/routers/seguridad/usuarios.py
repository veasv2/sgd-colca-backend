# app/api/routers/usuarios.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas import (
    UsuarioCreate, 
    UsuarioUpdate, 
    UsuarioRead,
    UsuarioInDB
)

from app.services.seguridad.usuario_service import usuario_service
from app.core.database import get_database

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)

@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def create_usuario(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_database)
):
    """
    Crear un nuevo usuario
    """
    return usuario_service.create_usuario(db=db, usuario_data=usuario_data)

@router.get("/{usuario_id}", response_model=UsuarioRead)
def get_usuario(
    usuario_id: int,
    db: Session = Depends(get_database)
):
    """
    Obtener usuario por ID
    """
    return usuario_service.get_usuario(db=db, usuario_id=usuario_id)

@router.get("/", response_model=List[UsuarioRead])
def get_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_database)
):
    """
    Obtener lista de usuarios con paginación
    """
    usuarios = usuario_service.get_usuarios(db=db, skip=skip, limit=limit)
    return usuarios

@router.put("/{usuario_id}", response_model=UsuarioRead)
def update_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    db: Session = Depends(get_database)
):
    """
    Actualizar usuario existente
    """
    return usuario_service.update_usuario(
        db=db, 
        usuario_id=usuario_id, 
        usuario_data=usuario_data
    )

@router.delete("/{usuario_id}", response_model=UsuarioRead)
def delete_usuario(
    usuario_id: int,
    db: Session = Depends(get_database)
):
    """
    Eliminar usuario
    """
    return usuario_service.delete_usuario(db=db, usuario_id=usuario_id)

@router.get("/username/{username}", response_model=UsuarioRead)
def get_usuario_by_username(
    username: str,
    db: Session = Depends(get_database)
):
    """
    Obtener usuario por username
    """
    usuario = usuario_service.get_usuario_by_username(db=db, username=username)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return usuario

# Endpoints para cambio de contraseña
from pydantic import BaseModel

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.patch("/{usuario_id}/change-password", response_model=UsuarioRead)
def change_password(
    usuario_id: int,
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_database)
):
    """
    Cambiar contraseña de usuario
    """
    return usuario_service.change_password(
        db=db,
        usuario_id=usuario_id,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )