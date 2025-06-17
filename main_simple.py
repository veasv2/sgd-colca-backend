"""
SGD-Colca Backend - Versión simple para probar
"""
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="SGD-Colca Test")

@app.get("/")
async def root():
    return {
        "message": "SGD-Colca Backend funcionando",
        "status": "OK"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("🚀 Iniciando SGD-Colca en puerto 8080...")
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8080,
        reload=False
    )
