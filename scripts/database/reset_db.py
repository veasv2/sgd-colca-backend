# scripts/database/reset_db.py
"""
Script para resetear completamente la base de datos
⚠️ PELIGROSO: Elimina todos los datos
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from sqlalchemy import text, MetaData
from alembic import command
from alembic.config import Config

from app.core.database import engine, SessionLocal


def drop_all_tables():
    """Eliminar todas las tablas de la base de datos"""
    print("🗑️ Eliminando todas las tablas...")
    
    try:
        with engine.connect() as connection:
            # Obtener metadatos de todas las tablas
            metadata = MetaData()
            metadata.reflect(bind=engine, schema='seguridad')
            metadata.reflect(bind=engine, schema='organizacion')
            metadata.reflect(bind=engine)  # Schema público
            
            # Eliminar todas las tablas en orden reverso (por las FK)
            metadata.drop_all(bind=engine)
            
            # También eliminar la tabla de versiones de Alembic
            try:
                connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
                connection.commit()
            except:
                pass
            
            print("✅ Todas las tablas eliminadas")
            return True
            
    except Exception as e:
        print(f"❌ Error eliminando tablas: {e}")
        return False


def drop_schemas():
    """Eliminar esquemas personalizados"""
    print("📁 Eliminando esquemas...")
    
    try:
        with engine.connect() as connection:
            # Eliminar esquemas en orden (primero las tablas, luego los esquemas)
            schemas_to_drop = ['seguridad', 'organizacion']
            
            for schema in schemas_to_drop:
                try:
                    connection.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
                    print(f"  ➖ Esquema eliminado: {schema}")
                except Exception as e:
                    print(f"  ⚠️ Error eliminando esquema {schema}: {e}")
            
            connection.commit()
            print("✅ Esquemas eliminados")
            return True
            
    except Exception as e:
        print(f"❌ Error eliminando esquemas: {e}")
        return False


def recreate_schemas():
    """Recrear esquemas básicos"""
    print("📁 Recreando esquemas...")
    
    try:
        with engine.connect() as connection:
            schemas_to_create = ['seguridad', 'organizacion']
            
            for schema in schemas_to_create:
                connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
                print(f"  ➕ Esquema creado: {schema}")
            
            connection.commit()
            print("✅ Esquemas recreados")
            return True
            
    except Exception as e:
        print(f"❌ Error recreando esquemas: {e}")
        return False


def reset_alembic():
    """Resetear el historial de Alembic"""
    print("📊 Reseteando historial de Alembic...")
    
    try:
        with engine.connect() as connection:
            # Eliminar tabla de versiones de Alembic
            connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
            connection.commit()
            
        print("✅ Historial de Alembic reseteado")
        return True
        
    except Exception as e:
        print(f"❌ Error reseteando Alembic: {e}")
        return False


def reinitialize_database():
    """Reinicializar la base de datos después del reset"""
    print("🔄 Reinicializando base de datos...")
    
    try:
        from scripts.database.init_db import init_database
        
        # Inicializar con migraciones
        success = init_database(skip_migrations=False)
        
        if success:
            print("✅ Base de datos reinicializada")
            return True
        else:
            print("❌ Error reinicializando base de datos")
            return False
            
    except Exception as e:
        print(f"❌ Error en reinicialización: {e}")
        return False


def reset_database(reinit=False, force=False):
    """
    Resetear completamente la base de datos
    
    Args:
        reinit (bool): Si True, reinicializa automáticamente después del reset
        force (bool): Si True, no pide confirmación
    """
    print("🚨 RESETEO COMPLETO DE BASE DE DATOS")
    print("=" * 50)
    print("⚠️ ADVERTENCIA: Esta operación eliminará TODOS los datos")
    print("⚠️ Esta acción NO se puede deshacer")
    print()
    
    if not force:
        print("Para continuar, escribe exactamente: ELIMINAR TODO")
        confirmation = input("Confirmación: ").strip()
        
        if confirmation != "ELIMINAR TODO":
            print("❌ Confirmación incorrecta. Operación cancelada.")
            return False
        print()
    
    try:
        # 1. Eliminar todas las tablas
        if not drop_all_tables():
            return False
        print()
        
        # 2. Eliminar esquemas
        if not drop_schemas():
            return False
        print()
        
        # 3. Recrear esquemas básicos
        if not recreate_schemas():
            return False
        print()
        
        # 4. Resetear Alembic
        if not reset_alembic():
            return False
        print()
        
        print("=" * 50)
        print("🗑️ Base de datos reseteada completamente")
        
        # 5. Reinicializar si se solicita
        if reinit:
            print()
            if not reinitialize_database():
                return False
            print()
            print("🎉 Base de datos reseteada y reinicializada!")
        else:
            print()
            print("📋 Para reinicializar la base de datos, ejecuta:")
            print("   python manage.py init-db")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fatal en reseteo: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Resetear base de datos SGD Colca",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
⚠️ ADVERTENCIA ⚠️
Este script eliminará TODOS los datos de la base de datos.
Use solo en desarrollo o con respaldo completo.

Ejemplos:
  python reset_db.py                    # Reset con confirmación
  python reset_db.py --force --reinit   # Reset y reinit automático
        """
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forzar reset sin confirmación (PELIGROSO)"
    )
    parser.add_argument(
        "--reinit",
        action="store_true",
        help="Reinicializar automáticamente después del reset"
    )
    
    args = parser.parse_args()
    
    success = reset_database(
        reinit=args.reinit,
        force=args.force
    )
    
    sys.exit(0 if success else 1)