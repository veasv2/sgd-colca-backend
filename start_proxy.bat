@echo off
echo Iniciando Cloud SQL Proxy para SGD-Colca...
cloud-sql-proxy.exe sgd-colca-municipal-2025:us-central1:sgd-colca-db-principal --port 5432
pause