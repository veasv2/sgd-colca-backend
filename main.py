"""
SGD-COLCA BACKEND API
Sistema de Gobernanza Digital - Municipalidad de Colca
FastAPI + SQLAlchemy + Firebase Auth + Google Cloud
"""

import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager

# Importaciones locales
from app.core.config import settings
from app.core.database import database, engine, Base
from app.api.v1 import api_router

# Importar todos los modelos para que se creen las tablas
from app.models import *

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print("🚀 Iniciando SGD-Colca Backend...")
    
    # Conectar a la base de datos
    try:
        await database.connect()
        print("✅ Conexión a base de datos establecida")
    except Exception as e:
        print(f"❌ Error conectando a base de datos: {e}")
    
    # Crear tablas si no existen (backup por si no se ejecutaron migraciones)
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas verificadas/creadas")
    except Exception as e:
        print(f"⚠️  Advertencia en creación de tablas: {e}")
    
    print(f"🌍 Ambiente: {settings.ENVIRONMENT}")
    print(f"🔥 Firebase Project: {settings.FIREBASE_PROJECT_ID}")
    
    yield
    
    # Shutdown
    print("🛑 Cerrando SGD-Colca Backend...")
    await database.disconnect()
    print("✅ Conexión a base de datos cerrada")

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configurar CORS
allowed_origins = [
    "http://localhost:4200",  # Angular desarrollo
    "https://sgd-colca-municipal-2025.web.app",  # Firebase Hosting
    "https://sgd-colca-municipal-2025.firebaseapp.com",  # Firebase Hosting
]

if settings.ENVIRONMENT == "development":
    allowed_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# MIDDLEWARE DE AUTENTICACIÓN FIREBASE (OPCIONAL)
# =====================================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Middleware para verificar tokens de Firebase
    Por ahora devuelve None, implementaremos Firebase después
    """
    # TODO: Implementar verificación de Firebase token
    # token = credentials.credentials
    # decoded_token = auth.verify_id_token(token)
    # return decoded_token
    return None

# =====================================================
# RUTAS PRINCIPALES
# =====================================================

@app.get("/")
async def root():
    """Endpoint principal de la API"""
    return {
        "message": "🏛️ SGD-Colca Backend API",
        "description": "Sistema de Gobernanza Digital - Municipalidad de Colca",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "🟢 Activo",
        "modules": {
            "usuarios": "✅ Disponible",
            "organigrama": "✅ Disponible", 
            "documentos_tdi": "🚧 En desarrollo",
            "mesa_partes": "🚧 En desarrollo",
            "concejo": "🚧 En desarrollo",
            "auditoria": "✅ Disponible"
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check para Cloud Run y monitoreo"""
    try:
        # Verificar conexión a base de datos
        await database.fetch_one("SELECT 1 as test")
        db_status = "✅ Conectado"
    except Exception as e:
        db_status = f"❌ Error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": "2025-01-17T00:00:00Z",
        "version": settings.VERSION,
        "services": {
            "database": db_status,
            "firebase": "🚧 Pendiente configuración",
            "drive_api": "🚧 Pendiente configuración",
            "cloud_storage": "🚧 Pendiente configuración"
        },
        "environment": settings.ENVIRONMENT
    }

@app.get("/api/v1/test")
async def test_endpoint():
    """Endpoint de prueba para verificar la API"""
    return {
        "message": "🧪 SGD-Colca API Test Endpoint",
        "database_connection": "active",
        "timestamp": "2025-01-17T00:00:00Z",
        "test_data": {
            "unidades_organicas": "ready",
            "puestos": "ready",
            "usuarios": "ready",
            "tipos_documento": "ready"
        }
    }

# =====================================================
# INCLUIR ROUTERS DE LA API
# =====================================================

# Incluir rutas de la API v1
app.include_router(api_router, prefix="/api/v1")

# =====================================================
# MANEJO DE ERRORES GLOBAL
# =====================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejo global de errores"""
    import traceback
    
    error_detail = str(exc)
    if settings.DEBUG:
        error_detail = traceback.format_exc()
    
    return {
        "error": "Error interno del servidor",
        "message": error_detail if settings.DEBUG else "Ha ocurrido un error interno",
        "status_code": 500,
        "path": str(request.url)
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejo de errores HTTP"""
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "path": str(request.url)
    }

# =====================================================
# EJECUCIÓN LOCAL (DESARROLLO)
# =====================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )