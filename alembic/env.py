# alembic/env.py

"""
Configuración de entorno para Alembic - SGD Colca (PostgreSQL con múltiples esquemas)
"""
import os
import sys
from logging.config import fileConfig
from sqlalchemy import create_engine, engine_from_config, pool, text
from alembic import context

# === Agregar la carpeta base del proyecto al sys.path ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)

# === Importar configuración y base de datos ===
from app.core.config import settings
from app.core.database import Base

# === Importar todos los modelos usando __init__.py ===
# Esto carga automáticamente todos los modelos definidos en __init__.py
import app.models  # Importa todo el paquete, registrando todos los modelos

# === Configuración de Alembic ===
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# === Metadatos para detección de cambios ===
target_metadata = Base.metadata

# === Configuración para PostgreSQL con múltiples esquemas ===
include_schemas = True

# === Esquemas que maneja la aplicación ===
SCHEMAS = ['seguridad', 'organizacion']


def create_schemas_if_not_exist(connection):
    """
    Crear esquemas si no existen
    """
    try:
        for schema in SCHEMAS:
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        connection.commit()
        print(f"✅ Esquemas verificados/creados: {', '.join(SCHEMAS)}")
    except Exception as e:
        print(f"⚠️ Error creando esquemas: {e}")
        raise


def run_migrations_offline() -> None:
    """
    Ejecutar migraciones en modo 'offline'
    """
    url = settings.DATABASE_URL
    
    if not url or url.strip() == "":
        raise ValueError("DATABASE_URL está vacía. Verifica tu configuración.")
    
    print(f"🔄 Ejecutando migraciones offline con URL: {url[:50]}...")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=include_schemas
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Ejecutar migraciones en modo 'online'
    """
    database_url = settings.DATABASE_URL
    
    if not database_url or database_url.strip() == "":
        raise ValueError("DATABASE_URL está vacía. Verifica tu archivo .env")
    
    print(f"🔄 Ejecutando migraciones online con URL: {database_url[:50]}...")
    
    # Crear engine directamente con la URL de configuración
    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
        echo=False  # Cambiar a True si necesitas debug de SQL
    )

    with connectable.connect() as connection:
        # Crear esquemas si no existen
        create_schemas_if_not_exist(connection)

        # Configurar contexto de Alembic
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=include_schemas
        )

        with context.begin_transaction():
            print(f"📊 Modelos detectados: {len(target_metadata.tables)} tablas")
            context.run_migrations()
            print("✅ Migraciones completadas exitosamente")


# === Ejecutar migraciones ===
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()