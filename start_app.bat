@echo off
echo === INICIANDO SGD-COLCA ===
echo 1. Cerrando procesos previos...
taskkill /F /IM cloud-sql-proxy.exe 2>nul
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak > nul
echo 2. Iniciando Cloud SQL Proxy con credenciales...
start "Cloud SQL Proxy" .\cloud-sql-proxy.exe sgd-colca-municipal-2025:us-central1:sgd-colca-db-principal --port 5432 --credentials-file "D:\2) Desarrollo\sgd-colca-backend\sgd-colca-service-account.json"
echo 3. Esperando que el proxy se conecte...
set counter=0
:check_proxy
set /a counter+=1
netstat -an | find "127.0.0.1:5432" | find "LISTENING" >nul
if errorlevel 1 (
    if %counter% LSS 20 (
        echo    Intento %counter%/20: Esperando proxy...
        timeout /t 1 /nobreak > nul
        goto check_proxy
    ) else (
        echo [ERROR] El proxy no se conecto en 20 segundos
        echo    Revisa la ventana del Cloud SQL Proxy para ver errores
        pause
        goto activate_env
    )
) else (
    echo [OK] Proxy conectado en puerto 5432 (en %counter% segundos)
)
echo 4. Probando conexion a la base de datos...
python -c "import psycopg2; psycopg2.connect('postgresql://sgd_colca_user:SgdColca2025Seguro@127.0.0.1:5432/sgd_colca_municipal').close(); print('[OK] Base de datos conectada')" 2>nul
if errorlevel 1 (
    echo [ERROR] Error conectando a la base de datos
    echo    Continuando de todas formas - FastAPI mostrara el error especifico
) else (
    echo [OK] Conexion a base de datos exitosa
)
:activate_env
echo 5. Activando entorno virtual...
call venv\Scripts\activate
echo 6. Configurando variables...
set DATABASE_URL=postgresql://sgd_colca_user:SgdColca2025Seguro@127.0.0.1:5432/sgd_colca_municipal
echo 7. Iniciando FastAPI...
echo =========================================
echo SISTEMA INICIADO - URLs disponibles:
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo Health: http://localhost:8000/health
echo =========================================
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000