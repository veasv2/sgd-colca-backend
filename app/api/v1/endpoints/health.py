"""
Endpoints de health check y status
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()

@router.get("/database")
async def check_database():
    """Verificar estado de la base de datos"""
    try:
        from app.core.database import database
        result = await database.fetch_one("SELECT COUNT(*) as count FROM usuarios")
        return {
            "status": "connected",
            "users_count": result["count"] if result else 0,
            "message": "Base de datos funcionando correctamente"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/tables")
async def check_tables():
    """Verificar que existan las tablas principales"""
    try:
        from app.core.database import database
        
        tables_to_check = [
            "usuarios", "unidades_organicas", "puestos", 
            "tipos_documento", "documentos_tdi", 
            "expedientes_mesa_partes", "audit_log"
        ]
        
        table_status = {}
        for table in tables_to_check:
            try:
                result = await database.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                table_status[table] = {
                    "exists": True,
                    "count": result["count"] if result else 0
                }
            except Exception as e:
                table_status[table] = {
                    "exists": False,
                    "error": str(e)
                }
        
        return {
            "status": "success",
            "tables": table_status
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
