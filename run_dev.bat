@echo off
echo Activando entorno virtual...
call venv\Scripts\activate

echo Cargando variables de entorno...
set DATABASE_URL=postgresql://sgd_colca_user:SgdColca2025Seguro@127.0.0.1:5432/sgd_colca_municipal

echo Iniciando SGD-Colca Backend...
python main.py
pause