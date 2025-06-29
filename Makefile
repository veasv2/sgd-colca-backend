# Makefile para SGD Colca
# Uso: make <comando>

.PHONY: help init seed status migrate backup reset install dev

# Comando por defecto
help:
	@echo "SGD Colca - Comandos Disponibles"
	@echo "=================================="
	@echo ""
	@echo "Gestion Basica:"
	@echo "  make init           - Inicializar BD completa"
	@echo "  make seed           - Datos de prueba basicos"
	@echo "  make seed-full      - Datos de prueba completos"
	@echo "  make status         - Estado del sistema"
	@echo "  make status-detail  - Estado detallado"
	@echo ""
	@echo "Migraciones:"
	@echo "  make migrate        - Aplicar migraciones"
	@echo "  make migration MSG='descripcion' - Nueva migracion"
	@echo "  make migrate-current - Revision actual"
	@echo "  make migrate-history - Historial de migraciones"
	@echo ""
	@echo "Respaldos:"
	@echo "  make backup         - Crear respaldo comprimido"
	@echo "  make backup-schema  - Solo estructura (sin datos)"
	@echo "  make restore FILE='archivo.sql' - Restaurar respaldo"
	@echo ""
	@echo "Reset (PELIGROSO):"
	@echo "  make reset          - Reset BD con confirmacion"
	@echo "  make reset-force    - Reset sin confirmacion"
	@echo "  make reset-reinit   - Reset y reinicializar"
	@echo ""
	@echo "Desarrollo:"
	@echo "  make install        - Instalar dependencias"
	@echo "  make dev            - Configurar entorno desarrollo"
	@echo "  make clean          - Limpiar archivos temporales"

# === GESTIÓN BÁSICA ===
init:
	@echo "Inicializando base de datos..."
	python manage.py init-db

seed:
	@echo "Cargando datos de prueba basicos..."
	python manage.py seed-data --scenario basico

seed-full:
	@echo "Cargando datos de prueba completos..."
	python manage.py seed-data --extended-org --scenario completo

status:
	@echo "Estado del sistema:"
	python manage.py status

status-detail:
	@echo "Estado detallado del sistema:"
	python manage.py status --detailed

# === MIGRACIONES ===
migrate:
	@echo "Aplicando migraciones..."
	python manage.py migrate upgrade

migration:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: Se requiere mensaje. Uso: make migration MSG='descripcion'"; \
		exit 1; \
	fi
	@echo "Creando nueva migracion: $(MSG)"
	python manage.py migrate revision -m "$(MSG)"

migrate-current:
	@echo "Revision actual:"
	python manage.py migrate current

migrate-history:
	@echo "Historial de migraciones:"
	python manage.py migrate history

# === RESPALDOS ===
backup:
	@echo "Creando respaldo comprimido..."
	python manage.py backup --compress

backup-schema:
	@echo "Creando respaldo solo esquema..."
	python manage.py backup --no-data --compress

restore:
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Se requiere archivo. Uso: make restore FILE='archivo.sql'"; \
		exit 1; \
	fi
	@echo "Restaurando desde: $(FILE)"
	python -c "from scripts.database.backup_db import restore_backup; restore_backup('$(FILE)')"

# === RESET (PELIGROSO) ===
reset:
	@echo "PELIGRO: Esto eliminara todos los datos"
	python manage.py reset-db

reset-force:
	@echo "RESET FORZADO - Sin confirmacion"
	python manage.py reset-db --force

reset-reinit:
	@echo "Reset y reinicializacion automatica"
	python manage.py reset-db --force --reinit

# === DESARROLLO ===
install:
	@echo "Instalando dependencias..."
	pip install -r requirements.txt

dev: install init seed
	@echo "Entorno de desarrollo configurado"
	@echo "Usuario admin: admin / admin123"

clean:
	@echo "Limpiando archivos temporales..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete

# === COMANDOS AVANZADOS ===
quick-reset: reset-force init seed
	@echo "Reset rapido completado"

setup-prod: install migrate
	@echo "Configuracion de produccion lista"
	@echo "CAMBIAR CONTRASEÑAS POR DEFECTO"