"""
Configuración de entorno para Alembic - SGD Colca (PostgreSQL con múltiples esquemas)
"""
import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, text
from alembic import context

# === Agregar la carpeta base del proyecto al sys.path ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)

# === Importar configuración y base de datos ===
from app.core.config import settings
from app.core.database import Base

# === Importar modelos (asegurar que estén registrados en Base.metadata) ===
from app.models.organizacion_models import UnidadOrganica, Puesto
from app.models.seguridad_models import (
    Usuario, Permiso, SesionUsuario, RegistroEventos, puesto_permisos
)

# === Configuración de Alembic ===
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# === Metadatos para detección de cambios ===
target_metadata = Base.metadata

# === Configuración para PostgreSQL con múltiples esquemas ===
include_schemas = True


def run_migrations_offline() -> None:
    """
    Ejecutar migraciones en modo 'offline'
    """
    url = settings.DATABASE_URL
    print(f"DEBUG OFFLINE - DATABASE_URL: '{url}'")
    
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
    # Debug: mostrar la URL que estamos usando
    database_url = settings.DATABASE_URL
    print(f"DEBUG ONLINE - DATABASE_URL from settings: '{database_url}'")
    
    if not database_url or database_url.strip() == "":
        raise ValueError("DATABASE_URL está vacía. Verifica tu archivo .env")
    
    # Debug adicional
    print(f"DEBUG - settings module: {settings}")
    print(f"DEBUG - DATABASE_URL type: {type(database_url)}")
    print(f"DEBUG - DATABASE_URL starts with postgresql: {database_url.startswith('postgresql')}")
    
    # IMPORTANTE: No usar config.get_section porque contiene el placeholder
    # Crear configuración limpia solo con nuestra URL
    configuration = {
        "sqlalchemy.url": database_url,
        "sqlalchemy.echo": "false"
    }
    
    print(f"DEBUG - Configuration URL: '{configuration.get('sqlalchemy.url')}'")
    print(f"DEBUG - Configuration: {configuration}")

    # Probar crear engine directamente primero
    try:
        from sqlalchemy import create_engine
        test_engine = create_engine(database_url)
        print("✅ Engine directo creado exitosamente")
        test_engine.dispose()
    except Exception as e:
        print(f"❌ Error creando engine directo: {e}")
        raise

    # Usar create_engine directamente en lugar de engine_from_config
    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Crear esquemas si no existen
        try:
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS seguridad"))
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS organizacion"))
            connection.commit()
            print("✅ Esquemas creados/verificados correctamente")
        except Exception as e:
            print(f"⚠️ Error creando esquemas: {e}")

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=include_schemas
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()