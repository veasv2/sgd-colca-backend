#!/usr/bin/env python3
"""
Script para configurar Alembic y crear la migración inicial
Ejecutar: python scripts/db/setup.py
"""

import os
import sys
import subprocess
from pathlib import Path

# Agregar el directorio raíz del proyecto al path de Python
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def main():
    """
    Configurar Alembic por primera vez en el proyecto
    """
    print("=== CONFIGURANDO ALEMBIC PARA SGD-COLCA ===")
    
    # Verificar que estamos en la raíz del proyecto
    if not os.path.exists("app/main.py"):
        print("[ERROR] Ejecuta este script desde la raíz del proyecto (donde está app/main.py)")
        sys.exit(1)
    
    # Verificar que el entorno virtual esté activo
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("[ERROR] Activa el entorno virtual primero")
        sys.exit(1)
    
    # Paso 1: Verificar que Alembic esté instalado
    try:
        import alembic
        print("[OK] Alembic está instalado")
    except ImportError:
        print("[ERROR] Alembic no está instalado. Ejecuta: pip install alembic")
        sys.exit(1)
    
    # Paso 2: Verificar que los modelos existan
    try:
        from app.core.database import Base
        # Importar todos los modelos para que estén registrados en Base.metadata
        from app.models.auth_models import (
            Area, Puesto, Usuario, Permiso, SesionUsuario, BitacoraAuditoria
        )
        print(f"[OK] Modelos encontrados: {len(Base.metadata.tables)} tablas")
        for table_name in Base.metadata.tables.keys():
            print(f"    - {table_name}")
    except ImportError as e:
        print(f"[ERROR] No se pueden importar los modelos: {e}")
        sys.exit(1)
    
    # Paso 3: Verificar conexión a la base de datos
    try:
        from app.core.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[OK] Conexión a base de datos exitosa")
    except Exception as e:
        print(f"[ERROR] No se puede conectar a la base de datos: {e}")
        print("       Verifica que el Cloud SQL Proxy esté ejecutándose")
        sys.exit(1)
    
    # Paso 4: Inicializar Alembic si no existe
    if not os.path.exists("alembic"):
        print("Inicializando Alembic...")
        try:
            subprocess.run(["alembic", "init", "alembic"], check=True, capture_output=True)
            print("[OK] Alembic inicializado")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Error al inicializar Alembic: {e}")
            sys.exit(1)
    else:
        print("[OK] Alembic ya está inicializado")
    
    # Paso 5: Configurar alembic.ini
    print("Configurando alembic.ini...")
    configure_alembic_ini()
    
    # Paso 6: Configurar env.py
    print("Configurando alembic/env.py...")
    configure_env_py()
    
    # Paso 7: Generar migración inicial
    print("Generando migración inicial...")
    try:
        subprocess.run([
            "alembic", "revision", "--autogenerate", 
            "-m", "Migración inicial - tablas de autenticación"
        ], check=True, capture_output=True)
        print("[OK] Migración inicial generada")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error al generar migración: {e}")
        sys.exit(1)
    
    print("\n=== CONFIGURACIÓN COMPLETADA ===")
    print("Próximos pasos:")
    print("1. Revisar la migración generada en: alembic/versions/")
    print("2. Ejecutar: python scripts/db/migrate.py")
    print("3. Ejecutar: python scripts/db/init_data.py")

def configure_alembic_ini():
    """
    Configurar el archivo alembic.ini
    """
    alembic_ini_content = """# Configuración de Alembic para SGD-Colca

[alembic]
# Ruta al directorio de scripts de Alembic
script_location = alembic

# Template para generar archivos de migración
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

# Timezone para timestamps
timezone = America/Lima

# Conexión a la base de datos (se configura en env.py)
sqlalchemy.url = 

# Revisión de donde partir (leave blank to use current db state)
revision_environment = false
compare_type = true
compare_server_default = true

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
    
    with open("alembic.ini", "w", encoding="utf-8") as f:
        f.write(alembic_ini_content)
    
    print("[OK] alembic.ini configurado")

def configure_env_py():
    """
    Configurar el archivo alembic/env.py
    """
    env_py_content = '''"""
Configuración de entorno para Alembic - SGD Colca
"""
import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Agregar el directorio raíz al path para importar la app
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Importar configuración y modelos
from app.core.config import settings
from app.core.database import Base

# IMPORTANTE: Importar todos los modelos para que estén en Base.metadata
from app.models.auth_models import (
    Area, Puesto, Usuario, Permiso, SesionUsuario, BitacoraAuditoria,
    puesto_permisos  # Tabla de asociación
)

# Configuración de Alembic
config = context.config

# Configurar logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadatos de los modelos para autogenerate
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """
    Ejecutar migraciones en modo 'offline'
    """
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """
    Ejecutar migraciones en modo 'online'
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
    
    with open("alembic/env.py", "w", encoding="utf-8") as f:
        f.write(env_py_content)
    
    print("[OK] alembic/env.py configurado")

if __name__ == "__main__":
    main()