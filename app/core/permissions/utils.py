# app/core/permissions/utils.py

from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models import Usuario
from app.core.database import get_db
from .base import PermisosGenerales

def get_user_permissions(db: Session, usuario: Usuario) -> List[str]:
    """
    Obtener todos los permisos de un usuario basado en su puesto
    """
    if not usuario.puesto_id:
        return []
    
    query = """
        SELECT p.codigo 
        FROM seguridad.permisos p
        INNER JOIN seguridad.puesto_permisos pp ON p.id = pp.permiso_id
        WHERE pp.puesto_id = :puesto_id AND p.activo = true
    """
    
    result = db.execute(query, {"puesto_id": usuario.puesto_id})
    return [row[0] for row in result.fetchall()]

def user_has_permission(db: Session, usuario: Usuario, permission: str) -> bool:
    """
    Verificar si un usuario tiene un permiso específico
    """
    # SUPERADMIN tiene todos los permisos
    if usuario.tipo_usuario == "SUPERADMIN":
        return True
    
    # Obtener permisos del usuario
    user_permissions = get_user_permissions(db, usuario)
    
    # Verificar permiso específico
    if permission in user_permissions:
        return True
    
    # Verificar permiso de ADMIN_TOTAL
    if PermisosGenerales.ADMIN_TOTAL.value in user_permissions:
        return True
    
    return False

def require_permission(permission: str):
    """
    Dependency para requerir un permiso específico
    """
    def permission_checker(
        current_user: Usuario = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> Usuario:
        if not user_has_permission(db, current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Sin permisos suficientes. Requiere: {permission}"
            )
        return current_user
    
    return Depends(permission_checker)

def require_any_permission(*permissions: str):
    """
    Dependency que requiere AL MENOS UNO de los permisos especificados
    """
    def permission_checker(
        current_user: Usuario = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> Usuario:
        for permission in permissions:
            if user_has_permission(db, current_user, permission):
                return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sin permisos suficientes. Requiere uno de: {', '.join(permissions)}"
        )
    
    return Depends(permission_checker)

def require_role_or_permission(role: str, permission: str):
    """
    Dependency que requiere un ROL específico O un permiso específico
    """
    def role_permission_checker(
        current_user: Usuario = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> Usuario:
        # Verificar por rol
        if current_user.tipo_usuario == role:
            return current_user
        
        # Verificar por permiso
        if user_has_permission(db, current_user, permission):
            return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requiere rol {role} o permiso {permission}"
        )
    
    return Depends(role_permission_checker)

# TODO: Implementar cuando tengas autenticación JWT
def get_current_user():
    """
    Esta función debe ser implementada para obtener el usuario actual
    desde el JWT token
    """