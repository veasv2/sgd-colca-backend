"""
Endpoints para gestión de documentos TDI
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/tdi")
async def listar_documentos_tdi():
    """Listar documentos TDI"""
    return {"message": "Endpoint en desarrollo", "module": "documentos_tdi"}

@router.get("/tipos")
async def listar_tipos_documento():
    """Listar tipos de documento"""
    return {"message": "Endpoint en desarrollo", "module": "tipos_documento"}
