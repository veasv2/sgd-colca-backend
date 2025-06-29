# scripts/database/status.py
"""
Script para mostrar el estado del sistema y base de datos
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from sqlalchemy import text, inspect
from sqlalchemy.exc import OperationalError
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

from app.core.database import engine, SessionLocal
from app.models import Usuario, Permiso, UnidadOrganica, Puesto
from app.core.config import settings


def check_database_connection():
    """Verificar conexión a la base de datos"""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, "✅ Conexión exitosa"
    except OperationalError as e:
        return False, f"❌ Error de conexión: {e}"
    except Exception as e:
        return False, f"❌ Error inesperado: {e}"


def get_alembic_status():
    """Obtener estado de las migraciones de Alembic"""
    try:
        # Configurar Alembic
        alembic_cfg = Config("alembic.ini")
        script_dir = ScriptDirectory.from_config(alembic_cfg)
        
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            
            # Revisión actual en BD
            current_rev = context.get_current_revision()
            
            # Última revisión disponible
            head_rev = script_dir.get_current_head()
            
            # Revisiones pendientes
            pending_revs = []
            if current_rev != head_rev:
                pending_revs = list(script_dir.walk_revisions(head_rev, current_rev))
            
            return {
                'status': 'ok',
                'current_revision': current_rev,
                'head_revision': head_rev,
                'pending_count': len(pending_revs),
                'pending_revisions': [rev.revision for rev in pending_revs],
                'up_to_date': current_rev == head_rev
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def get_database_info():
    """Obtener información general de la base de datos"""
    try:
        db = SessionLocal()
        
        # Información básica
        info = {
            'database_url': settings.DATABASE_URL[:50] + "..." if len(settings.DATABASE_URL) > 50 else settings.DATABASE_URL,
            'tables': {},
            'schemas': []
        }
        
        # Obtener esquemas
        inspector = inspect(engine)
        info['schemas'] = inspector.get_schema_names()
        
        # Contar registros en tablas principales
        try:
            info['tables']['usuarios'] = db.query(Usuario).count()
        except:
            info['tables']['usuarios'] = 'N/A'
            
        try:
            info['tables']['permisos'] = db.query(Permiso).count()
        except:
            info['tables']['permisos'] = 'N/A'
            
        try:
            info['tables']['unidades_organicas'] = db.query(UnidadOrganica).count()
        except:
            info['tables']['unidades_organicas'] = 'N/A'
            
        try:
            info['tables']['puestos'] = db.query(Puesto).count()
        except:
            info['tables']['puestos'] = 'N/A'
        
        db.close()
        return info
        
    except Exception as e:
        return {'error': str(e)}


def get_system_info():
    """Obtener información del sistema"""
    try:
        return {
            'python_version': sys.version.split()[0],
            'platform': sys.platform,
            'current_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'project_root': str(root_dir),
            'debug_mode': getattr(settings, 'DEBUG', 'N/A'),
            'log_level': getattr(settings, 'LOG_LEVEL', 'N/A')
        }
    except Exception as e:
        return {'error': str(e)}


def show_database_status(detailed=False):
    """Mostrar estado completo del sistema"""
    
    print("📊 Estado del Sistema SGD Colca")
    print("=" * 60)
    print(f"🕒 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Conexión a la base de datos
    print("🔌 CONEXIÓN A BASE DE DATOS")
    print("-" * 30)
    connected, msg = check_database_connection()
    print(f"Estado: {msg}")
    print()
    
    if not connected:
        print("❌ No se puede continuar sin conexión a la base de datos")
        return
    
    # 2. Estado de migraciones
    print("📊 ESTADO DE MIGRACIONES")
    print("-" * 30)
    alembic_status = get_alembic_status()
    
    if alembic_status['status'] == 'ok':
        print(f"Revisión actual: {alembic_status['current_revision'] or 'Ninguna'}")
        print(f"Última revisión: {alembic_status['head_revision'] or 'Ninguna'}")
        
        if alembic_status['up_to_date']:
            print("Estado: ✅ Al día")
        else:
            print(f"Estado: ⚠️ {alembic_status['pending_count']} migración(es) pendiente(s)")
            if detailed and alembic_status['pending_revisions']:
                print("Migraciones pendientes:")
                for rev in alembic_status['pending_revisions']:
                    print(f"  • {rev}")
    else:
        print(f"❌ Error obteniendo estado: {alembic_status['error']}")
    print()
    
    # 3. Información de la base de datos
    print("🗄️ INFORMACIÓN DE BASE DE DATOS")
    print("-" * 30)
    db_info = get_database_info()
    
    if 'error' not in db_info:
        print(f"URL: {db_info['database_url']}")
        print(f"Esquemas: {', '.join(db_info['schemas'])}")
        print()
        print("Registros por tabla:")
        for table, count in db_info['tables'].items():
            print(f"  • {table}: {count}")
    else:
        print(f"❌ Error: {db_info['error']}")
    print()
    
    # 4. Información del sistema (solo si se solicita detalle)
    if detailed:
        print("💻 INFORMACIÓN DEL SISTEMA")
        print("-" * 30)
        sys_info = get_system_info()
        
        if 'error' not in sys_info:
            print(f"Python: {sys_info['python_version']}")
            print(f"Plataforma: {sys_info['platform']}")
            print(f"Directorio: {sys_info['project_root']}")
            print(f"Debug: {sys_info['debug_mode']}")
            print(f"Log Level: {sys_info['log_level']}")
        else:
            print(f"❌ Error: {sys_info['error']}")
        print()
    
    # 5. Recomendaciones
    print("💡 RECOMENDACIONES")
    print("-" * 30)
    
    if not connected:
        print("🔧 Verificar configuración de base de datos")
    elif alembic_status.get('status') == 'ok' and not alembic_status.get('up_to_date', True):
        print("🔧 Ejecutar migraciones pendientes: python manage.py migrate upgrade")
    elif db_info.get('tables', {}).get('usuarios', 0) == 0:
        print("🔧 Inicializar datos: python manage.py init-db")
    else:
        print("✅ Sistema funcionando correctamente")
    
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Mostrar estado del sistema SGD Colca")
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Mostrar información detallada"
    )
    
    args = parser.parse_args()
    
    show_database_status(detailed=args.detailed)