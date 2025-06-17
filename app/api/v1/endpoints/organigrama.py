"""
Endpoints para gestión del organigrama (unidades orgánicas y puestos)
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/unidades")
async def listar_unidades():
    """Listar unidades orgánicas"""
    return {"message": "Endpoint en desarrollo", "module": "organigrama"}

@router.get("/puestos")
async def listar_puestos():
    """Listar puestos de trabajo"""
    return {"message": "Endpoint en desarrollo", "module": "organigrama"}
