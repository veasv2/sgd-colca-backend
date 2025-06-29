# sql/verify_tables.py
import os
import sys

# Agregar la raíz del proyecto al path (subir un nivel desde sql/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)

print(f"📁 Directorio base: {BASE_DIR}")

from app.core.config import settings
from sqlalchemy import create_engine, text

def verify_tables():
    print(f"🔗 Conectando a: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Verificar esquemas
        result = conn.execute(text("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name IN ('seguridad', 'organizacion')
            ORDER BY schema_name;
        """))
        
        print("\n📁 Esquemas creados:")
        schemas = result.fetchall()
        if schemas:
            for row in schemas:
                print(f"  ✅ {row[0]}")
        else:
            print("  ❌ No se encontraron esquemas")
        
        # Verificar tablas en esquema seguridad
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'seguridad'
            ORDER BY table_name;
        """))
        
        print("\n📋 Tablas en esquema 'seguridad':")
        tables = result.fetchall()
        if tables:
            for row in tables:
                print(f"  ✅ {row[0]}")
        else:
            print("  ❌ No se encontraron tablas en esquema seguridad")
            
        # Verificar tablas en esquema organizacion
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'organizacion'
            ORDER BY table_name;
        """))
        
        print("\n📋 Tablas en esquema 'organizacion':")
        tables = result.fetchall()
        if tables:
            for row in tables:
                print(f"  ✅ {row[0]}")
        else:
            print("  ❌ No se encontraron tablas en esquema organizacion")

        # Verificar tabla alembic_version
        result = conn.execute(text("""
            SELECT version_num 
            FROM alembic_version;
        """))
        
        version = result.fetchone()
        if version:
            print(f"\n🔄 Versión actual de migración: {version[0]}")
        else:
            print("\n❌ No se encontró versión de migración")

if __name__ == "__main__":
    try:
        verify_tables()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()