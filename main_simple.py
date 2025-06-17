"""
SGD-Colca Backend - Versión simplificada para desarrollo local
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Crear aplicación FastAPI simple
app = FastAPI(
    title="SGD-Colca Backend - Desarrollo Local",
    description="Sistema de Gobernanza Digital - Municipalidad de Colca",
    version="1.0.0-MVP",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "🏛️ SGD-Colca Backend API - Desarrollo Local",
        "status": "🟢 Activo",
        "version": "1.0.0-MVP",
        "environment": "development-local",
        "database": "🔴 Desconectado (modo desarrollo)"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "✅ Funcionando",
            "database": "🔴 No configurado",
            "firebase": "🚧 Pendiente",
        }
    }

@app.get("/api/v1/test")
async def test_endpoint():
    return {
        "message": "🧪 SGD-Colca API Test - Modo Local",
        "database_connection": "disabled",
        "test_data": {
            "usuarios": "mock_data",
            "organigrama": "mock_data"
        }
    }

if __name__ == "__main__":
    print("🚀 Iniciando SGD-Colca Backend - Modo Local...")
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )