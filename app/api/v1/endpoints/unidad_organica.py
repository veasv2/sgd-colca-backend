# En app/api/v1/endpoints/unidades_organicas.py

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.unidad_organica import UnidadOrganicaResponse, UnidadOrganicaCreate, UnidadOrganicaUpdate, UnidadOrganicaList # Asegúrate de que UnidadOrganicaList esté importado
from app.crud.unidad_organica import unidad_organica_crud

router = APIRouter(
    prefix="/unidades-organicas",
    tags=["Unidades Orgánicas"]
)

@router.post("/", response_model=UnidadOrganicaResponse, status_code=status.HTTP_201_CREATED)
def create_unidad_organica_endpoint(
    unidad_organica: UnidadOrganicaCreate,
    db: Session = Depends(get_db)
):
    db_unidad_existente_codigo = unidad_organica_crud.get_by_codigo(db, codigo=unidad_organica.codigo)
    if db_unidad_existente_codigo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una unidad orgánica con este código."
        )
    
    if unidad_organica.unidad_padre_id:
        db_unidad_padre = unidad_organica_crud.get(db, id=unidad_organica.unidad_padre_id)
        if not db_unidad_padre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La unidad padre especificada no existe."
            )

    return unidad_organica_crud.create(db=db, obj_in=unidad_organica)

@router.get("/", response_model=UnidadOrganicaList)
async def listar_unidades_organicas(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        if search:
            unidades = unidad_organica_crud.search(db, search_term=search, skip=skip, limit=limit)
            total = len(unidades) 
        else:
            unidades = unidad_organica_crud.get_all(db, skip=skip, limit=limit)
            total = unidad_organica_crud.count(db)

        unidades_response = []
        for unidad in unidades:
            # Aquí Pydantic se encarga de la validación al convertir el ORM object a UnidadOrganicaResponse
            unidades_response.append(UnidadOrganicaResponse.model_validate(unidad)) # Mejor usar model_validate directamente
        
        return UnidadOrganicaList(
            total=total,
            items=unidades_response # <--- ¡Aquí está el cambio clave!
            # page=(skip // limit) + 1,  # Estos campos no están en UnidadOrganicaList de tu esquema actual
            # per_page=limit             # Si los necesitas, agrégalos al esquema UnidadOrganicaList
        )
    
    except Exception as e:
        # Aquí puedes loggear el error completo para depuración
        print(f"Error en listar_unidades_organicas: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener unidades orgánicas: {str(e)}")

@router.get("/count")
async def contar_unidades_organicas(db: Session = Depends(get_db)):
    try:
        total = unidad_organica_crud.count(db)
        
        return {
            "success": True, # Si tu response_model para /count es solo un dict, mantén success
            "data": {
                "total": total
            }
        }
    except Exception as e:
        print(f"Error en contar_unidades_organicas: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al contar unidades orgánicas: {str(e)}")

@router.get("/{unidad_organica_id}", response_model=UnidadOrganicaResponse)
def read_unidad_organica_endpoint(
    unidad_organica_id: UUID,
    db: Session = Depends(get_db)
):
    db_unidad_organica = unidad_organica_crud.get(db, id=unidad_organica_id)
    if db_unidad_organica is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidad orgánica no encontrada."
        )
    return db_unidad_organica

@router.patch("/{unidad_organica_id}", response_model=UnidadOrganicaResponse)
def update_unidad_organica_endpoint(
    unidad_organica_id: UUID,
    unidad_organica_update: UnidadOrganicaUpdate,
    db: Session = Depends(get_db)
):
    db_unidad_organica = unidad_organica_crud.get(db, id=unidad_organica_id)
    if db_unidad_organica is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidad orgánica no encontrada."
        )
    
    if unidad_organica_update.codigo is not None and unidad_organica_update.codigo != db_unidad_organica.codigo:
        db_existing_by_codigo = unidad_organica_crud.get_by_codigo(db, codigo=unidad_organica_update.codigo)
        if db_existing_by_codigo and db_existing_by_codigo.id != unidad_organica_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El código proporcionado ya está en uso por otra unidad orgánica."
            )

    if unidad_organica_update.unidad_padre_id:
        db_unidad_padre = unidad_organica_crud.get(db, id=unidad_organica_update.unidad_padre_id)
        if not db_unidad_padre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La unidad padre especificada no existe."
            )

    return unidad_organica_crud.update(db=db, db_obj=db_unidad_organica, obj_in=unidad_organica_update)

@router.delete("/{unidad_organica_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unidad_organica_endpoint(
    unidad_organica_id: UUID,
    db: Session = Depends(get_db)
):
    db_unidad_organica = unidad_organica_crud.get(db, id=unidad_organica_id)
    if db_unidad_organica is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidad orgánica no encontrada."
        )
    
    unidad_organica_crud.remove(db=db, id=unidad_organica_id)
    return {}