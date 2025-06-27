"""
API v1 para SGD-Colca
"""
from fastapi import APIRouter
from .endpoints import health,unidad_organica

api_router = APIRouter()

# Incluir endpoints
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(unidad_organica.router, prefix="/unidad_organica", tags=["unidad_organica"])
# api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
# api_router.include_router(organigrama.router, prefix="/organigrama", tags=["organigrama"])
# api_router.include_router(documentos.router, prefix="/documentos", tags=["documentos"])