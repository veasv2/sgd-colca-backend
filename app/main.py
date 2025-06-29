# app/main.py
"""
Aplicación Principal del Sistema de Gestión de Usuarios
Municipalidad Distrital de Colca - Módulo de Seguridad
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from sqlalchemy import text

from app.core.config import settings
from app.api.routers.seguridad import usuarios

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
    logger.info(f"Iniciando {settings.PROJECT_NAME} - Módulo Usuarios")
    logger.info(f"Entorno: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    
    # Verificar conexión a base de datos
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Conexión a base de datos establecida")
    except Exception as e:
        logger.error(f"❌ Error de conexión a base de datos: {e}")
    
    # La aplicación está funcionando
    yield
    
    # === SHUTDOWN ===
    logger.info("Cerrando aplicación")

# Crear aplicación FastAPI con lifespan
app = FastAPI(
    title=f"{settings.PROJECT_NAME} - Gestión de Usuarios",
    description="API para gestión de usuarios del sistema de gobernanza digital",
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

# Incluir router de usuarios
app.include_router(usuarios.router, prefix="/api/v1")

# === ENDPOINTS PRINCIPALES ===

@app.get("/", tags=["Sistema"])
async def root():
    """
    Endpoint raíz del sistema
    """
    return {
        "message": "Sistema de Gestión de Usuarios",
        "municipalidad": settings.MUNICIPALITY_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "Activo",
        "modulo": "Gestión de Usuarios",
        "features": [
            "CRUD de Usuarios",
            "Validación de Contraseñas",
            "Gestión de Perfiles"
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
            "service": "Gestión de Usuarios",
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
                "service": "Gestión de Usuarios",
                "error": str(e) if settings.DEBUG else "Database connection failed"
            }
        )

# === CONFIGURACIÓN ADICIONAL PARA DESARROLLO ===

if settings.DEBUG:
    # Endpoint adicional para desarrollo
    @app.get("/debug/usuarios-info", tags=["Debug"])
    async def debug_usuarios_info():
        """
        Información del módulo de usuarios (solo en modo debug)
        """
        return {
            "warning": "Este endpoint solo está disponible en modo debug",
            "modulo": "Gestión de Usuarios",
            "endpoints_disponibles": [
                "POST /api/v1/usuarios/ - Crear usuario",
                "GET /api/v1/usuarios/ - Listar usuarios",
                "GET /api/v1/usuarios/{id} - Obtener usuario",
                "PUT /api/v1/usuarios/{id} - Actualizar usuario",
                "DELETE /api/v1/usuarios/{id} - Eliminar usuario",
                "GET /api/v1/usuarios/username/{username} - Buscar por username",
                "PATCH /api/v1/usuarios/{id}/change-password - Cambiar contraseña"
            ],
            "validaciones": [
                "Username único",
                "Email único", 
                "DNI único",
                "Contraseña segura"
            ]
        }
    
    logger.info("🔧 Modo debug activado - endpoints adicionales disponibles")