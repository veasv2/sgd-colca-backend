# sql/reset_database.py
import os
import sys

# Agregar la raíz del proyecto al path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)

from app.core.config import settings
from sqlalchemy import create_engine, text

def reset_database():
    print("🧹 Iniciando limpieza completa de la base de datos...")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # 1. Eliminar tabla alembic_version
            print("\n1️⃣ Eliminando tabla alembic_version...")
            conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
            
            # 2. Eliminar todas las tablas de los esquemas
            print("2️⃣ Eliminando tablas del esquema seguridad...")
            conn.execute(text("DROP SCHEMA IF EXISTS seguridad CASCADE"))
            
            print("3️⃣ Eliminando tablas del esquema organizacion...")
            conn.execute(text("DROP SCHEMA IF EXISTS organizacion CASCADE"))
            
            # 3. Recrear esquemas vacíos
            print("4️⃣ Recreando esquemas...")
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS seguridad"))
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS organizacion"))
            
            conn.commit()
            print("✅ Base de datos limpiada exitosamente")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error durante la limpieza: {e}")
            raise

def clean_migration_files():
    print("\n🗂️ Limpiando archivos de migración...")
    versions_dir = os.path.join(BASE_DIR, "alembic", "versions")
    
    if os.path.exists(versions_dir):
        for file in os.listdir(versions_dir):
            if file.endswith('.py') and file != '__init__.py':
                file_path = os.path.join(versions_dir, file)
                os.remove(file_path)
                print(f"  🗑️ Eliminado: {file}")
        print("✅ Archivos de migración eliminados")
    else:
        print("⚠️ Carpeta versions no encontrada")

if __name__ == "__main__":
    try:
        # Limpiar base de datos
        reset_database()
        
        # Limpiar archivos de migración
        clean_migration_files()
        
        print("\n🎉 ¡Limpieza completa terminada!")
        print("\n📋 Próximos pasos:")
        print("1. alembic revision --autogenerate -m 'Initial migration'")
        print("2. alembic upgrade head")
        print("3. python sql\\verify_tables.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()