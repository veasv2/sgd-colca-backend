@echo off
echo === INICIANDO SGD-COLCA COMPLETO ===

echo 1. Iniciando Cloud SQL Proxy en segundo plano...
start "Cloud SQL Proxy" cloud-sql-proxy.exe sgd-colca-municipal-2025:us-central1:sgd-colca-db-principal --port 5432

echo 2. Esperando 3 segundos para que el proxy inicie...
timeout /t 3 /nobreak > nul

echo 3. Activando entorno virtual...
call venv\Scripts\activate

echo 4. Configurando variables de entorno...
set DATABASE_URL=postgresql://sgd_colca_user:SgdColca2025Seguro@127.0.0.1:5432/sgd_colca_municipal

echo 5. Iniciando SGD-Colca Backend...
python main.py