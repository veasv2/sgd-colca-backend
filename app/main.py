# app/main.py
"""
Aplicación Principal del Sistema de Gobernanza Digital (SGD)
Municipalidad Distrital de Colca
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from sqlalchemy import text
from app.core.database import create_database

from app.core.config import settings
from app.routers import auth, organigrama

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === LIFESPAN EVENTS ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manejador de eventos de ciclo de vida de la aplicación
    """
    # === STARTUP ===
    logger.info(f"Iniciando {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Entorno: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    
    # Verificar conexión a base de datos
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        # create_database()
        # logger.info("✅ Tablas de base de datos creadas/verificadas")
        logger.info("✅ Conexión a base de datos establecida")
    except Exception as e:
        logger.error(f"❌ Error de conexión a base de datos: {e}")
    
    # La aplicación está funcionando
    yield
    
    # === SHUTDOWN ===
    logger.info(f"Cerrando {settings.PROJECT_NAME}")

# Crear aplicación FastAPI con lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# === MIDDLEWARE ===

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Middleware de logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Procesar request
    response = await call_next(request)
    
    # Calcular tiempo de procesamiento
    process_time = time.time() - start_time
    
    # Log response
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
    
    # Agregar header de tiempo de procesamiento
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# === EXCEPTION HANDLERS ===

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Manejador global de excepciones
    """
    logger.error(f"Error global: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "message": "Error interno del servidor",
            "detail": str(exc) if settings.DEBUG else "Error interno",
            "success": False
        }
    )

# === ROUTERS ===

# Incluir routers de la aplicación
app.include_router(auth.router, prefix="/api/v1")
app.include_router(organigrama.router, prefix="/api/v1")

# === ENDPOINTS PRINCIPALES ===

@app.get("/", tags=["Sistema"])
async def root():
    """
    Endpoint raíz del sistema
    """
    return {
        "message": "Sistema de Gobernanza Digital",
        "municipalidad": settings.MUNICIPALITY_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "Activo",
        "features": [
            "Autenticación y Autorización",
            "Organigrama Digital",
            "Gestión de Usuarios",
            "Control de Acceso Basado en Roles"
        ]
    }

@app.get("/health", tags=["Sistema"])
async def health_check():
    """
    Endpoint de verificación de estado del sistema
    """
    try:
        # Verificar conexión a base de datos
        from app.core.database import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "service": "SGD Colca",
            "version": settings.VERSION,
            "database": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy", 
                "service": "SGD Colca",
                "error": str(e) if settings.DEBUG else "Database connection failed"
            }
        )

@app.get("/info", tags=["Sistema"])
async def system_info():
    """
    Información detallada del sistema
    """
    return {
        "sistema": {
            "nombre": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "entorno": settings.ENVIRONMENT,
            "debug": settings.DEBUG
        },
        "municipalidad": {
            "nombre": settings.MUNICIPALITY_NAME,
            "ruc": settings.MUNICIPALITY_RUC,
            "direccion": settings.MUNICIPALITY_ADDRESS
        },
        "configuracion": {
            "base_datos": "PostgreSQL" if "postgresql" in settings.DATABASE_URL else "Otra",
            "autenticacion": "JWT",
            "cors_habilitado": True
        }
    }

# === CONFIGURACIÓN ADICIONAL PARA DESARROLLO ===

if settings.DEBUG:
    # Endpoint adicional para desarrollo
    @app.get("/debug/config", tags=["Debug"])
    async def debug_config():
        """
        Muestra configuración actual (solo en modo debug)
        """
        return {
            "warning": "Este endpoint solo está disponible en modo debug",
            "config": {
                "PROJECT_NAME": settings.PROJECT_NAME,
                "VERSION": settings.VERSION,
                "ENVIRONMENT": settings.ENVIRONMENT,
                "DEBUG": settings.DEBUG,
                "LOG_LEVEL": settings.LOG_LEVEL,
                "DATABASE_URL": settings.DATABASE_URL[:20] + "..." if len(settings.DATABASE_URL) > 20 else settings.DATABASE_URL,
                "ACCESS_TOKEN_EXPIRE_MINUTES": settings.ACCESS_TOKEN_EXPIRE_MINUTES
            }
        }
    
    logger.info("🔧 Modo debug activado - endpoints adicionales disponibles")