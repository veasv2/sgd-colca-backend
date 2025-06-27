# app/routers/organigrama.py
"""
Endpoints de Organigrama Digital para el Sistema de Gobernanza Digital (SGD)
Municipalidad Distrital de Colca

Implementa todos los endpoints para gestión de la estructura organizacional:
áreas, puestos y asignaciones de personal.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
import logging

# Importaciones locales
from app.core.database import get_database
from app.core.deps import (
    get_current_user,
    require_organigrama_admin,
    require_alcalde_or_above,
    log_user_action,
    get_user_context
)
from app.models.auth_models import Area, Puesto, Usuario
from app.schemas.auth_schemas import (
    AreaCreate,
    AreaUpdate,
    AreaResponse,
    PuestoCreate,
    PuestoUpdate,
    PuestoResponse,
    MessageResponse
)

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(
    prefix="/organigrama",
    tags=["Organigrama Digital"],
    responses={
        401: {"description": "No autorizado"},
        403: {"description": "Acceso prohibido"},
        404: {"description": "Recurso no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)

# === ENDPOINTS DE ÁREAS ===

@router.post("/areas",
             response_model=AreaResponse,
             summary="Crear área",
             description="Crea una nueva área en el organigrama")
async def create_area(
    area_data: AreaCreate,
    current_user: Dict[str, Any] = Depends(require_organigrama_admin),
    db: Session = Depends(get_database)
):
    """
    Endpoint para crear una nueva área organizacional
    
    Solo SUPERADMIN y ALCALDE pueden modificar el organigrama.
    
    - **codigo**: Código único del área (ej: ALC, GAF, OAT)
    - **nombre**: Nombre completo del área
    - **descripcion**: Descripción opcional del área
    - **area_padre_id**: ID del área padre (para jerarquía)
    - **nivel**: Nivel jerárquico (1 = más alto)
    """
    try:
        # Verificar que el código no exista
        existing_area = db.query(Area).filter(Area.codigo == area_data.codigo.upper()).first()
        if existing_area:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un área con código {area_data.codigo}"
            )
        
        # Verificar área padre si se especifica
        area_padre = None
        if area_data.area_padre_id:
            area_padre = db.query(Area).filter(Area.id == area_data.area_padre_id).first()
            if not area_padre:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Área padre no encontrada"
                )
            
            # El nivel debe ser mayor que el del padre
            if area_data.nivel <= area_padre.nivel:
                area_data.nivel = area_padre.nivel + 1
        
        # Crear nueva área
        new_area = Area(
            codigo=area_data.codigo.upper(),
            nombre=area_data.nombre,
            descripcion=area_data.descripcion,
            nivel=area_data.nivel,
            activa=area_data.activa,
            area_padre_id=area_data.area_padre_id
        )
        
        db.add(new_area)
        db.commit()
        db.refresh(new_area)
        
        logger.info(f"Área creada: {new_area.codigo} por usuario {current_user.get('username')}")
        
        return AreaResponse(
            id=new_area.id,
            uuid=str(new_area.uuid),
            codigo=new_area.codigo,
            nombre=new_area.nombre,
            descripcion=new_area.descripcion,
            nivel=new_area.nivel,
            activa=new_area.activa,
            fecha_creacion=new_area.fecha_creacion,
            fecha_actualizacion=new_area.fecha_actualizacion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear área: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear área"
        )

@router.get("/areas",
            response_model=List[AreaResponse],
            summary="Listar áreas",
            description="Obtiene todas las áreas del organigrama")
async def list_areas(
    include_inactive: bool = Query(False, description="Incluir áreas inactivas"),
    parent_id: Optional[int] = Query(None, description="Filtrar por área padre"),
    nivel: Optional[int] = Query(None, description="Filtrar por nivel jerárquico"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Endpoint para listar todas las áreas del organigrama
    
    Todos los usuarios autenticados pueden ver la estructura organizacional.
    """
    try:
        # Construir query
        query = db.query(Area)
        
        # Filtros
        if not include_inactive:
            query = query.filter(Area.activa == True)
        
        if parent_id is not None:
            query = query.filter(Area.area_padre_id == parent_id)
        
        if nivel is not None:
            query = query.filter(Area.nivel == nivel)
        
        # Ordenar por nivel y luego por código
        areas = query.order_by(Area.nivel, Area.codigo).all()
        
        # Convertir a respuesta
        areas_response = []
        for area in areas:
            areas_response.append(AreaResponse(
                id=area.id,
                uuid=str(area.uuid),
                codigo=area.codigo,
                nombre=area.nombre,
                descripcion=area.descripcion,
                nivel=area.nivel,
                activa=area.activa,
                fecha_creacion=area.fecha_creacion,
                fecha_actualizacion=area.fecha_actualizacion
            ))
        
        return areas_response
        
    except Exception as e:
        logger.error(f"Error al listar áreas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al listar áreas"
        )

@router.get("/areas/{area_id}",
            response_model=Dict[str, Any],
            summary="Obtener área por ID",
            description="Obtiene información detallada de un área específica")
async def get_area_by_id(
    area_id: int,
    include_puestos: bool = Query(True, description="Incluir puestos del área"),
    include_usuarios: bool = Query(False, description="Incluir usuarios asignados"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Endpoint para obtener información detallada de un área
    
    Incluye opcionalmente puestos y usuarios asignados.
    """
    try:
        # Buscar área con relaciones
        area_query = db.query(Area)
        if include_puestos:
            area_query = area_query.options(joinedload(Area.puestos))
        
        area = area_query.filter(Area.id == area_id).first()
        
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Área no encontrada"
            )
        
        # Construir respuesta
        area_data = {
            "id": area.id,
            "uuid": str(area.uuid),
            "codigo": area.codigo,
            "nombre": area.nombre,
            "descripcion": area.descripcion,
            "nivel": area.nivel,
            "activa": area.activa,
            "fecha_creacion": area.fecha_creacion,
            "fecha_actualizacion": area.fecha_actualizacion
        }
        
        # Agregar sub-áreas
        sub_areas = db.query(Area).filter(Area.area_padre_id == area_id).all()
        area_data["sub_areas"] = [
            {
                "id": sub.id,
                "codigo": sub.codigo,
                "nombre": sub.nombre,
                "activa": sub.activa
            }
            for sub in sub_areas
        ]
        
        # Agregar puestos si se solicita
        if include_puestos:
            puestos = db.query(Puesto).filter(Puesto.area_id == area_id).order_by(Puesto.nivel_jerarquico).all()
            area_data["puestos"] = []
            
            for puesto in puestos:
                puesto_data = {
                    "id": puesto.id,
                    "codigo": puesto.codigo,
                    "nombre": puesto.nombre,
                    "nivel_jerarquico": puesto.nivel_jerarquico,
                    "activo": puesto.activo
                }
                
                # Agregar usuario asignado si se solicita
                if include_usuarios:
                    usuario = db.query(Usuario).filter(Usuario.puesto_id == puesto.id).first()
                    if usuario:
                        puesto_data["usuario_asignado"] = {
                            "id": usuario.id,
                            "username": usuario.username,
                            "nombres": usuario.nombres,
                            "apellidos": usuario.apellidos,
                            "estado": usuario.estado
                        }
                    else:
                        puesto_data["usuario_asignado"] = None
                
                area_data["puestos"].append(puesto_data)
        
        return area_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener área {area_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener área"
        )

@router.put("/areas/{area_id}",
            response_model=AreaResponse,
            summary="Actualizar área",
            description="Actualiza información de un área")
async def update_area(
    area_id: int,
    area_update: AreaUpdate,
    current_user: Dict[str, Any] = Depends(require_organigrama_admin),
    db: Session = Depends(get_database)
):
    """
    Endpoint para actualizar un área existente
    
    Solo SUPERADMIN y ALCALDE pueden modificar el organigrama.
    """
    try:
        area = db.query(Area).filter(Area.id == area_id).first()
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Área no encontrada"
            )
        
        # Actualizar campos si se proporcionan
        update_data = area_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "codigo" and value:
                # Verificar unicidad del nuevo código
                existing_area = db.query(Area).filter(
                    Area.codigo == value.upper(),
                    Area.id != area_id
                ).first()
                if existing_area:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ya existe un área con código {value}"
                    )
                setattr(area, field, value.upper())
            elif field == "area_padre_id" and value:
                # Verificar que el área padre exista
                area_padre = db.query(Area).filter(Area.id == value).first()
                if not area_padre:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Área padre no encontrada"
                    )
                # Evitar ciclos (el área padre no puede ser descendiente)
                if value == area_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Un área no puede ser padre de sí misma"
                    )
                setattr(area, field, value)
            else:
                setattr(area, field, value)
        
        db.commit()
        db.refresh(area)
        
        logger.info(f"Área {area.codigo} actualizada por usuario {current_user.get('username')}")
        
        return AreaResponse(
            id=area.id,
            uuid=str(area.uuid),
            codigo=area.codigo,
            nombre=area.nombre,
            descripcion=area.descripcion,
            nivel=area.nivel,
            activa=area.activa,
            fecha_creacion=area.fecha_creacion,
            fecha_actualizacion=area.fecha_actualizacion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar área {area_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar área"
        )

@router.delete("/areas/{area_id}",
               response_model=MessageResponse,
               summary="Desactivar área",
               description="Desactiva un área del organigrama")
async def deactivate_area(
    area_id: int,
    current_user: Dict[str, Any] = Depends(require_organigrama_admin),
    db: Session = Depends(get_database)
):
    """
    Endpoint para desactivar un área (soft delete)
    
    No elimina físicamente el área para preservar integridad referencial.
    """
    try:
        area = db.query(Area).filter(Area.id == area_id).first()
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Área no encontrada"
            )
        
        # Verificar que no tenga sub-áreas activas
        sub_areas_activas = db.query(Area).filter(
            Area.area_padre_id == area_id,
            Area.activa == True
        ).count()
        
        if sub_areas_activas > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede desactivar un área que tiene sub-áreas activas"
            )
        
        # Verificar que no tenga puestos activos con usuarios asignados
        puestos_con_usuarios = db.query(Puesto).join(Usuario).filter(
            Puesto.area_id == area_id,
            Puesto.activo == True,
            Usuario.estado == "ACTIVO"
        ).count()
        
        if puestos_con_usuarios > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede desactivar un área que tiene usuarios activos asignados"
            )
        
        # Desactivar área
        area.activa = False
        db.commit()
        
        logger.info(f"Área {area.codigo} desactivada por usuario {current_user.get('username')}")
        
        return MessageResponse(
            message=f"Área {area.codigo} desactivada exitosamente",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al desactivar área {area_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al desactivar área"
        )

# === ENDPOINTS DE PUESTOS ===

@router.post("/puestos",
             response_model=PuestoResponse,
             summary="Crear puesto",
             description="Crea un nuevo puesto en el organigrama")
async def create_puesto(
    puesto_data: PuestoCreate,
    current_user: Dict[str, Any] = Depends(require_organigrama_admin),
    db: Session = Depends(get_database)
):
    """
    Endpoint para crear un nuevo puesto organizacional
    
    - **codigo**: Código único del puesto
    - **nombre**: Nombre del puesto
    - **area_id**: ID del área a la que pertenece
    - **puesto_superior_id**: ID del puesto superior (jerarquía)
    - **nivel_jerarquico**: Nivel jerárquico del puesto
    """
    try:
        # Verificar que el código no exista
        existing_puesto = db.query(Puesto).filter(Puesto.codigo == puesto_data.codigo.upper()).first()
        if existing_puesto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un puesto con código {puesto_data.codigo}"
            )
        
        # Verificar que el área exista y esté activa
        area = db.query(Area).filter(Area.id == puesto_data.area_id).first()
        if not area or not area.activa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Área no encontrada o inactiva"
            )
        
        # Verificar puesto superior si se especifica
        if puesto_data.puesto_superior_id:
            puesto_superior = db.query(Puesto).filter(Puesto.id == puesto_data.puesto_superior_id).first()
            if not puesto_superior:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Puesto superior no encontrado"
                )
            
            # El nivel jerárquico debe ser mayor que el del superior
            if puesto_data.nivel_jerarquico <= puesto_superior.nivel_jerarquico:
                puesto_data.nivel_jerarquico = puesto_superior.nivel_jerarquico + 1
        
        # Crear nuevo puesto
        new_puesto = Puesto(
            codigo=puesto_data.codigo.upper(),
            nombre=puesto_data.nombre,
            descripcion=puesto_data.descripcion,
            area_id=puesto_data.area_id,
            puesto_superior_id=puesto_data.puesto_superior_id,
            nivel_jerarquico=puesto_data.nivel_jerarquico,
            activo=puesto_data.activo
        )
        
        db.add(new_puesto)
        db.commit()
        db.refresh(new_puesto)
        
        logger.info(f"Puesto creado: {new_puesto.codigo} por usuario {current_user.get('username')}")
        
        return PuestoResponse(
            id=new_puesto.id,
            uuid=str(new_puesto.uuid),
            codigo=new_puesto.codigo,
            nombre=new_puesto.nombre,
            descripcion=new_puesto.descripcion,
            nivel_jerarquico=new_puesto.nivel_jerarquico,
            activo=new_puesto.activo,
            area_id=new_puesto.area_id,
            puesto_superior_id=new_puesto.puesto_superior_id,
            fecha_creacion=new_puesto.fecha_creacion,
            fecha_actualizacion=new_puesto.fecha_actualizacion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear puesto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear puesto"
        )

@router.get("/puestos",
            response_model=List[Dict[str, Any]],
            summary="Listar puestos",
            description="Obtiene todos los puestos del organigrama")
async def list_puestos(
    area_id: Optional[int] = Query(None, description="Filtrar por área"),
    include_inactive: bool = Query(False, description="Incluir puestos inactivos"),
    include_usuarios: bool = Query(False, description="Incluir usuarios asignados"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Endpoint para listar todos los puestos del organigrama
    """
    try:
        # Construir query con relaciones
        query = db.query(Puesto).options(joinedload(Puesto.area))
        
        # Filtros
        if area_id:
            query = query.filter(Puesto.area_id == area_id)
        
        if not include_inactive:
            query = query.filter(Puesto.activo == True)
        
        # Ordenar por área y nivel jerárquico
        puestos = query.order_by(Puesto.area_id, Puesto.nivel_jerarquico).all()
        
        # Construir respuesta
        puestos_response = []
        for puesto in puestos:
            puesto_data = {
                "id": puesto.id,
                "uuid": str(puesto.uuid),
                "codigo": puesto.codigo,
                "nombre": puesto.nombre,
                "descripcion": puesto.descripcion,
                "nivel_jerarquico": puesto.nivel_jerarquico,
                "activo": puesto.activo,
                "area_id": puesto.area_id,
                "puesto_superior_id": puesto.puesto_superior_id,
                "fecha_creacion": puesto.fecha_creacion,
                "fecha_actualizacion": puesto.fecha_actualizacion,
                "area": {
                    "id": puesto.area.id,
                    "codigo": puesto.area.codigo,
                    "nombre": puesto.area.nombre
                }
            }
            
            # Agregar usuario asignado si se solicita
            if include_usuarios:
                usuario = db.query(Usuario).filter(Usuario.puesto_id == puesto.id).first()
                if usuario:
                    puesto_data["usuario_asignado"] = {
                        "id": usuario.id,
                        "username": usuario.username,
                        "nombres": usuario.nombres,
                        "apellidos": usuario.apellidos,
                        "estado": usuario.estado
                    }
                else:
                    puesto_data["usuario_asignado"] = None
            
            puestos_response.append(puesto_data)
        
        return puestos_response
        
    except Exception as e:
        logger.error(f"Error al listar puestos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al listar puestos"
        )

@router.get("/puestos/{puesto_id}",
            response_model=Dict[str, Any],
            summary="Obtener puesto por ID",
            description="Obtiene información detallada de un puesto específico")
async def get_puesto_by_id(
    puesto_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Endpoint para obtener información detallada de un puesto
    """
    try:
        puesto = db.query(Puesto).options(
            joinedload(Puesto.area)
        ).filter(Puesto.id == puesto_id).first()
        
        if not puesto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Puesto no encontrado"
            )
        
        # Construir respuesta completa
        puesto_data = {
            "id": puesto.id,
            "uuid": str(puesto.uuid),
            "codigo": puesto.codigo,
            "nombre": puesto.nombre,
            "descripcion": puesto.descripcion,
            "nivel_jerarquico": puesto.nivel_jerarquico,
            "activo": puesto.activo,
            "area_id": puesto.area_id,
            "puesto_superior_id": puesto.puesto_superior_id,
            "fecha_creacion": puesto.fecha_creacion,
            "fecha_actualizacion": puesto.fecha_actualizacion,
            "area": {
                "id": puesto.area.id,
                "codigo": puesto.area.codigo,
                "nombre": puesto.area.nombre,
                "nivel": puesto.area.nivel
            }
        }
        
        # Agregar puesto superior si existe
        if puesto.puesto_superior_id:
            puesto_superior = db.query(Puesto).filter(Puesto.id == puesto.puesto_superior_id).first()
            if puesto_superior:
                puesto_data["puesto_superior"] = {
                    "id": puesto_superior.id,
                    "codigo": puesto_superior.codigo,
                    "nombre": puesto_superior.nombre
                }
        
        # Agregar puestos subordinados
        puestos_subordinados = db.query(Puesto).filter(
            Puesto.puesto_superior_id == puesto_id
        ).all()
        puesto_data["puestos_subordinados"] = [
            {
                "id": sub.id,
                "codigo": sub.codigo,
                "nombre": sub.nombre,
                "activo": sub.activo
            }
            for sub in puestos_subordinados
        ]
        
        # Agregar usuario asignado
        usuario = db.query(Usuario).filter(Usuario.puesto_id == puesto_id).first()
        if usuario:
            puesto_data["usuario_asignado"] = {
                "id": usuario.id,
                "username": usuario.username,
                "nombres": usuario.nombres,
                "apellidos": usuario.apellidos,
                "estado": usuario.estado,
                "tipo_usuario": usuario.tipo_usuario
            }
        else:
            puesto_data["usuario_asignado"] = None
        
        return puesto_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener puesto {puesto_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener puesto"
        )

@router.put("/puestos/{puesto_id}",
            response_model=PuestoResponse,
            summary="Actualizar puesto",
            description="Actualiza información de un puesto")
async def update_puesto(
    puesto_id: int,
    puesto_update: PuestoUpdate,
    current_user: Dict[str, Any] = Depends(require_organigrama_admin),
    db: Session = Depends(get_database)
):
    """
    Endpoint para actualizar un puesto existente
    """
    try:
        puesto = db.query(Puesto).filter(Puesto.id == puesto_id).first()
        if not puesto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Puesto no encontrado"
            )
        
        # Actualizar campos si se proporcionan
        update_data = puesto_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "codigo" and value:
                # Verificar unicidad del nuevo código
                existing_puesto = db.query(Puesto).filter(
                    Puesto.codigo == value.upper(),
                    Puesto.id != puesto_id
                ).first()
                if existing_puesto:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ya existe un puesto con código {value}"
                    )
                setattr(puesto, field, value.upper())
            elif field == "area_id" and value:
                # Verificar que el área exista y esté activa
                area = db.query(Area).filter(Area.id == value).first()
                if not area or not area.activa:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Área no encontrada o inactiva"
                    )
                setattr(puesto, field, value)
            elif field == "puesto_superior_id" and value:
                # Verificar que el puesto superior exista
                puesto_superior = db.query(Puesto).filter(Puesto.id == value).first()
                if not puesto_superior:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Puesto superior no encontrado"
                    )
                # Evitar ciclos
                if value == puesto_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Un puesto no puede ser superior de sí mismo"
                    )
                setattr(puesto, field, value)
            else:
                setattr(puesto, field, value)
        
        db.commit()
        db.refresh(puesto)
        
        logger.info(f"Puesto {puesto.codigo} actualizado por usuario {current_user.get('username')}")
        
        return PuestoResponse(
            id=puesto.id,
            uuid=str(puesto.uuid),
            codigo=puesto.codigo,
            nombre=puesto.nombre,
            descripcion=puesto.descripcion,
            nivel_jerarquico=puesto.nivel_jerarquico,
            activo=puesto.activo,
            area_id=puesto.area_id,
            puesto_superior_id=puesto.puesto_superior_id,
            fecha_creacion=puesto.fecha_creacion,
            fecha_actualizacion=puesto.fecha_actualizacion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar puesto {puesto_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar puesto"
        )

# === ENDPOINTS DE ESTRUCTURA ORGANIZACIONAL ===

@router.get("/estructura",
            response_model=Dict[str, Any],
            summary="Obtener estructura completa",
            description="Obtiene la estructura organizacional completa en formato jerárquico")
async def get_organizational_structure(
    include_usuarios: bool = Query(False, description="Incluir usuarios asignados"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Endpoint para obtener la estructura organizacional completa
    
    Retorna un árbol jerárquico con áreas, puestos y usuarios asignados.
    """
    try:
        # Obtener todas las áreas activas ordenadas por nivel
        areas = db.query(Area).filter(Area.activa == True).order_by(Area.nivel, Area.codigo).all()
        
        # Construir estructura jerárquica
        def build_area_tree(area_padre_id=None):
            area_children = []
            for area in areas:
                if area.area_padre_id == area_padre_id:
                    area_data = {
                        "id": area.id,
                        "codigo": area.codigo,
                        "nombre": area.nombre,
                        "descripcion": area.descripcion,
                        "nivel": area.nivel,
                        "puestos": [],
                        "sub_areas": build_area_tree(area.id)
                    }
                    
                    # Agregar puestos del área
                    puestos = db.query(Puesto).filter(
                        Puesto.area_id == area.id,
                        Puesto.activo == True
                    ).order_by(Puesto.nivel_jerarquico).all()
                    
                    for puesto in puestos:
                        puesto_data = {
                            "id": puesto.id,
                            "codigo": puesto.codigo,
                            "nombre": puesto.nombre,
                            "nivel_jerarquico": puesto.nivel_jerarquico
                        }
                        
                        # Agregar usuario asignado si se solicita
                        if include_usuarios:
                            usuario = db.query(Usuario).filter(Usuario.puesto_id == puesto.id).first()
                            if usuario:
                                puesto_data["usuario"] = {
                                    "id": usuario.id,
                                    "username": usuario.username,
                                    "nombres": usuario.nombres,
                                    "apellidos": usuario.apellidos,
                                    "estado": usuario.estado
                                }
                            else:
                                puesto_data["usuario"] = None
                        
                        area_data["puestos"].append(puesto_data)
                    
                    area_children.append(area_data)
            
            return area_children
        
        estructura = {
            "municipalidad": "Municipalidad Distrital de Colca",
            "fecha_consulta": db.query(func.now()).scalar(),
            "total_areas": len(areas),
            "total_puestos": db.query(Puesto).filter(Puesto.activo == True).count(),
            "estructura": build_area_tree()
        }
        
        return estructura
        
    except Exception as e:
        logger.error(f"Error al obtener estructura organizacional: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener estructura organizacional"
        )

@router.get("/jerarquia/{puesto_id}",
            response_model=Dict[str, Any],
            summary="Obtener jerarquía de puesto",
            description="Obtiene la cadena jerárquica completa de un puesto")
async def get_puesto_hierarchy(
    puesto_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Endpoint para obtener la cadena jerárquica completa de un puesto
    
    Retorna desde el puesto más alto hasta el especificado, y todos sus subordinados.
    """
    try:
        puesto = db.query(Puesto).filter(Puesto.id == puesto_id).first()
        if not puesto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Puesto no encontrado"
            )
        
        # Construir cadena hacia arriba (superiores)
        def get_superior_chain(puesto_actual):
            chain = []
            while puesto_actual:
                chain.insert(0, {
                    "id": puesto_actual.id,
                    "codigo": puesto_actual.codigo,
                    "nombre": puesto_actual.nombre,
                    "nivel_jerarquico": puesto_actual.nivel_jerarquico
                })
                
                if puesto_actual.puesto_superior_id:
                    puesto_actual = db.query(Puesto).filter(
                        Puesto.id == puesto_actual.puesto_superior_id
                    ).first()
                else:
                    break
            
            return chain
        
        # Construir árbol hacia abajo (subordinados)
        def get_subordinate_tree(puesto_id):
            subordinados = db.query(Puesto).filter(
                Puesto.puesto_superior_id == puesto_id,
                Puesto.activo == True
            ).all()
            
            result = []
            for sub in subordinados:
                sub_data = {
                    "id": sub.id,
                    "codigo": sub.codigo,
                    "nombre": sub.nombre,
                    "nivel_jerarquico": sub.nivel_jerarquico,
                    "subordinados": get_subordinate_tree(sub.id)
                }
                result.append(sub_data)
            
            return result
        
        jerarquia = {
            "puesto_consultado": {
                "id": puesto.id,
                "codigo": puesto.codigo,
                "nombre": puesto.nombre,
                "nivel_jerarquico": puesto.nivel_jerarquico
            },
            "cadena_superior": get_superior_chain(puesto),
            "subordinados": get_subordinate_tree(puesto_id)
        }
        
        return jerarquia
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener jerarquía del puesto {puesto_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener jerarquía"
        )

# === ENDPOINTS DE ASIGNACIÓN DE USUARIOS ===

@router.post("/asignar-usuario/{puesto_id}/{usuario_id}",
             response_model=MessageResponse,
             summary="Asignar usuario a puesto",
             description="Asigna un usuario a un puesto específico")
async def assign_user_to_puesto(
    puesto_id: int,
    usuario_id: int,
    current_user: Dict[str, Any] = Depends(require_organigrama_admin),
    db: Session = Depends(get_database)
):
    """
    Endpoint para asignar un usuario a un puesto
    
    Solo SUPERADMIN y ALCALDE pueden realizar asignaciones.
    """
    try:
        # Verificar que el puesto exista y esté activo
        puesto = db.query(Puesto).filter(Puesto.id == puesto_id).first()
        if not puesto or not puesto.activo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Puesto no encontrado o inactivo"
            )
        
        # Verificar que el usuario exista y esté activo
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario or usuario.estado != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado o inactivo"
            )
        
        # Verificar que el puesto no tenga ya un usuario asignado
        existing_assignment = db.query(Usuario).filter(Usuario.puesto_id == puesto_id).first()
        if existing_assignment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El puesto ya tiene asignado al usuario {existing_assignment.username}"
            )
        
        # Verificar que el usuario no tenga ya un puesto asignado
        if usuario.puesto_id:
            puesto_actual = db.query(Puesto).filter(Puesto.id == usuario.puesto_id).first()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El usuario ya tiene asignado el puesto {puesto_actual.codigo if puesto_actual else 'N/A'}"
            )
        
        # Realizar asignación
        usuario.puesto_id = puesto_id
        db.commit()
        
        logger.info(f"Usuario {usuario.username} asignado al puesto {puesto.codigo} por {current_user.get('username')}")
        
        return MessageResponse(
            message=f"Usuario {usuario.username} asignado exitosamente al puesto {puesto.codigo}",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al asignar usuario {usuario_id} al puesto {puesto_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al asignar usuario"
        )

@router.delete("/desasignar-usuario/{usuario_id}",
               response_model=MessageResponse,
               summary="Desasignar usuario de puesto",
               description="Remueve la asignación de un usuario a su puesto")
async def unassign_user_from_puesto(
    usuario_id: int,
    current_user: Dict[str, Any] = Depends(require_organigrama_admin),
    db: Session = Depends(get_database)
):
    """
    Endpoint para desasignar un usuario de su puesto actual
    """
    try:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        if not usuario.puesto_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario no tiene un puesto asignado"
            )
        
        # Obtener información del puesto actual para el log
        puesto_actual = db.query(Puesto).filter(Puesto.id == usuario.puesto_id).first()
        puesto_codigo = puesto_actual.codigo if puesto_actual else "N/A"
        
        # Desasignar usuario
        usuario.puesto_id = None
        db.commit()
        
        logger.info(f"Usuario {usuario.username} desasignado del puesto {puesto_codigo} por {current_user.get('username')}")
        
        return MessageResponse(
            message=f"Usuario {usuario.username} desasignado exitosamente del puesto {puesto_codigo}",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al desasignar usuario {usuario_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al desasignar usuario"
        )

# === ENDPOINTS DE ESTADÍSTICAS Y REPORTES ===

@router.get("/estadisticas",
            response_model=Dict[str, Any],
            summary="Estadísticas del organigrama",
            description="Obtiene estadísticas generales del organigrama")
async def get_organigrama_stats(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Endpoint para obtener estadísticas del organigrama
    """
    try:
        from sqlalchemy import func
        
        # Estadísticas básicas
        total_areas = db.query(Area).filter(Area.activa == True).count()
        total_areas_inactivas = db.query(Area).filter(Area.activa == False).count()
        total_puestos = db.query(Puesto).filter(Puesto.activo == True).count()
        total_puestos_inactivos = db.query(Puesto).filter(Puesto.activo == False).count()
        
        # Estadísticas de usuarios
        usuarios_con_puesto = db.query(Usuario).filter(
            Usuario.puesto_id.isnot(None),
            Usuario.estado == "ACTIVO"
        ).count()
        
        puestos_sin_usuario = db.query(Puesto).filter(
            Puesto.activo == True,
            ~Puesto.id.in_(
                db.query(Usuario.puesto_id).filter(
                    Usuario.puesto_id.isnot(None),
                    Usuario.estado == "ACTIVO"
                )
            )
        ).count()
        
        # Distribución por área
        areas_con_puestos = db.query(
            Area.codigo,
            Area.nombre,
            func.count(Puesto.id).label('total_puestos'),
            func.count(Usuario.id).label('usuarios_asignados')
        ).outerjoin(Puesto, Area.id == Puesto.area_id).outerjoin(
            Usuario, and_(Puesto.id == Usuario.puesto_id, Usuario.estado == "ACTIVO")
        ).filter(Area.activa == True).group_by(Area.id, Area.codigo, Area.nombre).all()
        
        distribucion_areas = []
        for area in areas_con_puestos:
            distribucion_areas.append({
                "area_codigo": area.codigo,
                "area_nombre": area.nombre,
                "total_puestos": area.total_puestos,
                "usuarios_asignados": area.usuarios_asignados,
                "puestos_vacantes": area.total_puestos - area.usuarios_asignados,
                "porcentaje_ocupacion": round((area.usuarios_asignados / area.total_puestos * 100) if area.total_puestos > 0 else 0, 2)
            })
        
        # Distribución por nivel jerárquico
        niveles_jerarquicos = db.query(
            Puesto.nivel_jerarquico,
            func.count(Puesto.id).label('total_puestos'),
            func.count(Usuario.id).label('usuarios_asignados')
        ).outerjoin(
            Usuario, and_(Puesto.id == Usuario.puesto_id, Usuario.estado == "ACTIVO")
        ).filter(Puesto.activo == True).group_by(Puesto.nivel_jerarquico).order_by(Puesto.nivel_jerarquico).all()
        
        distribucion_niveles = []
        for nivel in niveles_jerarquicos:
            distribucion_niveles.append({
                "nivel": nivel.nivel_jerarquico,
                "total_puestos": nivel.total_puestos,
                "usuarios_asignados": nivel.usuarios_asignados,
                "puestos_vacantes": nivel.total_puestos - nivel.usuarios_asignados
            })
        
        estadisticas = {
            "resumen_general": {
                "total_areas_activas": total_areas,
                "total_areas_inactivas": total_areas_inactivas,
                "total_puestos_activos": total_puestos,
                "total_puestos_inactivos": total_puestos_inactivos,
                "usuarios_con_puesto": usuarios_con_puesto,
                "puestos_sin_usuario": puestos_sin_usuario,
                "porcentaje_ocupacion_global": round((usuarios_con_puesto / total_puestos * 100) if total_puestos > 0 else 0, 2)
            },
            "distribucion_por_area": distribucion_areas,
            "distribucion_por_nivel": distribucion_niveles,
            "fecha_consulta": func.now()
        }
        
        return estadisticas
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas del organigrama: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener estadísticas"
        )

@router.get("/vacantes",
            response_model=List[Dict[str, Any]],
            summary="Puestos vacantes",
            description="Obtiene lista de puestos sin usuario asignado")
async def get_vacant_positions(
    area_id: Optional[int] = Query(None, description="Filtrar por área"),
    nivel_jerarquico: Optional[int] = Query(None, description="Filtrar por nivel jerárquico"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Endpoint para obtener puestos vacantes (sin usuario asignado)
    """
    try:
        # Query base para puestos sin usuario asignado
        query = db.query(Puesto).options(joinedload(Puesto.area)).filter(
            Puesto.activo == True,
            ~Puesto.id.in_(
                db.query(Usuario.puesto_id).filter(
                    Usuario.puesto_id.isnot(None),
                    Usuario.estado == "ACTIVO"
                )
            )
        )
        
        # Aplicar filtros
        if area_id:
            query = query.filter(Puesto.area_id == area_id)
        
        if nivel_jerarquico:
            query = query.filter(Puesto.nivel_jerarquico == nivel_jerarquico)
        
        # Ordenar por área y nivel jerárquico
        puestos_vacantes = query.order_by(Puesto.area_id, Puesto.nivel_jerarquico).all()
        
        # Construir respuesta
        vacantes = []
        for puesto in puestos_vacantes:
            vacantes.append({
                "id": puesto.id,
                "codigo": puesto.codigo,
                "nombre": puesto.nombre,
                "descripcion": puesto.descripcion,
                "nivel_jerarquico": puesto.nivel_jerarquico,
                "area": {
                    "id": puesto.area.id,
                    "codigo": puesto.area.codigo,
                    "nombre": puesto.area.nombre
                },
                "fecha_creacion": puesto.fecha_creacion
            })
        
        return vacantes
        
    except Exception as e:
        logger.error(f"Error al obtener puestos vacantes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener puestos vacantes"
        )

# === ENDPOINTS DE VALIDACIÓN ===

@router.post("/validar-estructura",
             response_model=Dict[str, Any],
             summary="Validar estructura organizacional",
             description="Valida la integridad de la estructura organizacional")
async def validate_organizational_structure(
    current_user: Dict[str, Any] = Depends(require_organigrama_admin),
    db: Session = Depends(get_database)
):
    """
    Endpoint para validar la integridad de la estructura organizacional
    
    Identifica inconsistencias, referencias rotas y problemas de jerarquía.
    """
    try:
        validacion = {
            "valida": True,
            "errores": [],
            "advertencias": [],
            "estadisticas": {}
        }
        
        # Verificar áreas huérfanas (con padre inexistente)
        areas_huerfanas = db.query(Area).filter(
            Area.area_padre_id.isnot(None),
            ~Area.area_padre_id.in_(db.query(Area.id))
        ).all()
        
        if areas_huerfanas:
            validacion["valida"] = False
            validacion["errores"].append({
                "tipo": "areas_huerfanas",
                "mensaje": "Áreas con padre inexistente",
                "areas": [{"id": a.id, "codigo": a.codigo, "padre_id": a.area_padre_id} for a in areas_huerfanas]
            })
        
        # Verificar ciclos en jerarquía de áreas
        def detectar_ciclo_areas(area_id, visitados=None):
            if visitados is None:
                visitados = set()
            
            if area_id in visitados:
                return True
            
            visitados.add(area_id)
            area = db.query(Area).filter(Area.id == area_id).first()
            
            if area and area.area_padre_id:
                return detectar_ciclo_areas(area.area_padre_id, visitados.copy())
            
            return False
        
        areas_con_ciclos = []
        for area in db.query(Area).filter(Area.area_padre_id.isnot(None)).all():
            if detectar_ciclo_areas(area.id):
                areas_con_ciclos.append(area)
        
        if areas_con_ciclos:
            validacion["valida"] = False
            validacion["errores"].append({
                "tipo": "ciclos_areas",
                "mensaje": "Ciclos detectados en jerarquía de áreas",
                "areas": [{"id": a.id, "codigo": a.codigo} for a in areas_con_ciclos]
            })
        
        # Verificar puestos con área inexistente
        puestos_sin_area = db.query(Puesto).filter(
            ~Puesto.area_id.in_(db.query(Area.id))
        ).all()
        
        if puestos_sin_area:
            validacion["valida"] = False
            validacion["errores"].append({
                "tipo": "puestos_sin_area",
                "mensaje": "Puestos con área inexistente",
                "puestos": [{"id": p.id, "codigo": p.codigo, "area_id": p.area_id} for p in puestos_sin_area]
            })
        
        # Verificar puestos con superior inexistente
        puestos_sin_superior = db.query(Puesto).filter(
            Puesto.puesto_superior_id.isnot(None),
            ~Puesto.puesto_superior_id.in_(db.query(Puesto.id))
        ).all()
        
        if puestos_sin_superior:
            validacion["valida"] = False
            validacion["errores"].append({
                "tipo": "puestos_sin_superior",
                "mensaje": "Puestos con superior inexistente",
                "puestos": [{"id": p.id, "codigo": p.codigo, "superior_id": p.puesto_superior_id} for p in puestos_sin_superior]
            })
        
        # Verificar usuarios con puesto inexistente
        usuarios_sin_puesto = db.query(Usuario).filter(
            Usuario.puesto_id.isnot(None),
            ~Usuario.puesto_id.in_(db.query(Puesto.id))
        ).all()
        
        if usuarios_sin_puesto:
            validacion["valida"] = False
            validacion["errores"].append({
                "tipo": "usuarios_sin_puesto",
                "mensaje": "Usuarios con puesto inexistente",
                "usuarios": [{"id": u.id, "username": u.username, "puesto_id": u.puesto_id} for u in usuarios_sin_puesto]
            })
        
        # Advertencias (no son errores críticos)
        
        # Áreas sin puestos
        areas_sin_puestos = db.query(Area).filter(
            Area.activa == True,
            ~Area.id.in_(db.query(Puesto.area_id))
        ).all()
        
        if areas_sin_puestos:
            validacion["advertencias"].append({
                "tipo": "areas_sin_puestos",
                "mensaje": "Áreas activas sin puestos definidos",
                "areas": [{"id": a.id, "codigo": a.codigo, "nombre": a.nombre} for a in areas_sin_puestos]
            })
        
        # Puestos duplicados por código
        from sqlalchemy import func
        codigos_duplicados = db.query(
            Puesto.codigo,
            func.count(Puesto.id).label('total')
        ).group_by(Puesto.codigo).having(func.count(Puesto.id) > 1).all()
        
        if codigos_duplicados:
            validacion["advertencias"].append({
                "tipo": "codigos_duplicados",
                "mensaje": "Códigos de puesto duplicados",
                "codigos": [{"codigo": c.codigo, "total": c.total} for c in codigos_duplicados]
            })
        
        # Estadísticas de validación
        validacion["estadisticas"] = {
            "total_areas": db.query(Area).count(),
            "total_puestos": db.query(Puesto).count(),
            "total_usuarios_asignados": db.query(Usuario).filter(Usuario.puesto_id.isnot(None)).count(),
            "errores_encontrados": len(validacion["errores"]),
            "advertencias_encontradas": len(validacion["advertencias"])
        }
        
        return validacion
        
    except Exception as e:
        logger.error(f"Error al validar estructura organizacional: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al validar estructura"
        )

# === IMPORTACIONES NECESARIAS PARA FUNCIONES ===
from datetime import datetime
from sqlalchemy import func