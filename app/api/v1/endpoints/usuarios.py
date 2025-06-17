"""
Endpoints para gestión de usuarios - Implementación correcta con ORM
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.usuario import UsuarioResponse, UsuarioCreate, UsuarioUpdate, UsuarioList
from app.crud.usuario import usuario_crud

router = APIRouter()

@router.get("/", response_model=UsuarioList)
async def listar_usuarios(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(50, ge=1, le=100, description="Número máximo de registros"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    search: Optional[str] = Query(None, description="Buscar por nombre, apellido o email"),
    db: Session = Depends(get_db)
):
    """Listar usuarios con paginación y filtros"""
    try:
        if search:
            usuarios = usuario_crud.search(db, search, skip, limit)
            total = len(usuarios)  # Para búsquedas, contar los resultados
        else:
            usuarios = usuario_crud.get_all(db, skip, limit, activo)
            total = usuario_crud.count(db, activo)
        
        # Convertir a schema response con información de puesto
        usuarios_response = []
        for usuario in usuarios:
            usuario_dict = {
                "id": usuario.id,
                "firebase_uid": usuario.firebase_uid,
                "email": usuario.email,
                "nombres": usuario.nombres,
                "apellidos": usuario.apellidos,
                "dni": usuario.dni,
                "telefono": usuario.telefono,
                "puesto_id": usuario.puesto_id,
                "es_superadmin": usuario.es_superadmin,
                "activo": usuario.activo,
                "ultimo_acceso": usuario.ultimo_acceso,
                "created_at": usuario.created_at,
                "updated_at": usuario.updated_at,
                "puesto_nombre": usuario.puesto.nombre if usuario.puesto else None,
                "unidad_nombre": usuario.puesto.unidad_organica.nombre if usuario.puesto and usuario.puesto.unidad_organica else None
            }
            usuarios_response.append(UsuarioResponse(**usuario_dict))
        
        return UsuarioList(
            success=True,
            data=usuarios_response,
            total=total,
            page=(skip // limit) + 1,
            per_page=limit
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {str(e)}")

@router.get("/count")
async def contar_usuarios(db: Session = Depends(get_db)):
    """Contar usuarios por estado"""
    try:
        total = usuario_crud.count(db)
        activos = usuario_crud.count(db, activo=True)
        inactivos = total - activos
        
        return {
            "success": True,
            "data": {
                "total": total,
                "activos": activos,
                "inactivos": inactivos
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al contar usuarios: {str(e)}")

@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """Obtener usuario por ID"""
    usuario = usuario_crud.get_by_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Construir respuesta con información de puesto
    usuario_dict = {
        "id": usuario.id,
        "firebase_uid": usuario.firebase_uid,# Ver la URL actual (incorrecta)
git remote -v

# Cambiar a la URL correcta de tu repositorio
git remote set-url origin https://github.com/veasv2/sgd-colca-backend.git

# Verificar que se cambió correctamente
git remote -v
        "email": usuario.email,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "dni": usuario.dni,
        "telefono": usuario.telefono,
        "puesto_id": usuario.puesto_id,
        "es_superadmin": usuario.es_superadmin,
        "activo": usuario.activo,
        "ultimo_acceso": usuario.ultimo_acceso,
        "created_at": usuario.created_at,
        "updated_at": usuario.updated_at,
        "puesto_nombre": usuario.puesto.nombre if usuario.puesto else None,
        "unidad_nombre": usuario.puesto.unidad_organica.nombre if usuario.puesto and usuario.puesto.unidad_organica else None
    }
    
    return UsuarioResponse(**usuario_dict)

@router.post("/", response_model=UsuarioResponse)
async def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Crear nuevo usuario"""
    # Verificar que no exista usuario con mismo email o firebase_uid
    if usuario_crud.get_by_email(db, usuario.email):
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email")
    
    if usuario_crud.get_by_firebase_uid(db, usuario.firebase_uid):
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese Firebase UID")
    
    try:
        nuevo_usuario = usuario_crud.create(db, usuario)
        return await obtener_usuario(nuevo_usuario.id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")

@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: UUID, 
    usuario_update: UsuarioUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar usuario"""
    usuario_actualizado = usuario_crud.update(db, usuario_id, usuario_update)
    if not usuario_actualizado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return await obtener_usuario(usuario_id, db)

@router.delete("/{usuario_id}")
async def eliminar_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """Eliminar usuario (soft delete)"""
    if not usuario_crud.delete(db, usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {"success": True, "message": "Usuario eliminado correctamente"}
