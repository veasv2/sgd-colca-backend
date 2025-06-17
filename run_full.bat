@echo off
echo === SGD-COLCA STARTUP COMPLETO ===

echo 1. Activando entorno virtual...
call venv\Scripts\activate

echo 2. Configurando variables de entorno...
set DATABASE_URL=postgresql://sgd_colca_user:SgdColca2025Seguro@127.0.0.1:5432/sgd_colca_municipal
set GOOGLE_CLOUD_PROJECT=sgd-colca-municipal-2025

echo 3. Verificando Cloud SQL Proxy...
tasklist | find "cloud-sql-proxy" > nul
if errorlevel 1 (
    echo ERROR: Cloud SQL Proxy no está corriendo!
    echo Ejecuta primero: cloud-sql-proxy.exe sgd-colca-municipal-2025:us-central1:sgd-colca-db-principal --port 5432
    pause
    exit
)

echo 4. Iniciando SGD-Colca Backend...
python main.py
pause