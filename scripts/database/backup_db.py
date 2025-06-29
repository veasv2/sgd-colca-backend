# scripts/database/backup_db.py
"""
Script para crear respaldos de la base de datos
"""

import sys
import os
import subprocess
import gzip
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from app.core.config import settings


def parse_database_url(database_url):
    """Parsear la URL de la base de datos para obtener parámetros de conexión"""
    try:
        parsed = urlparse(database_url)
        
        return {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 5432,
            'database': parsed.path.lstrip('/'),
            'username': parsed.username,
            'password': parsed.password
        }
    except Exception as e:
        print(f"❌ Error parseando URL de base de datos: {e}")
        return None


def create_backup_filename(output_file=None, compress=False):
    """Crear nombre del archivo de respaldo"""
    if output_file:
        return output_file
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = ".sql.gz" if compress else ".sql"
    
    # Crear directorio de respaldos si no existe
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    return backup_dir / f"sgd_colca_backup_{timestamp}{extension}"


def create_backup(output_file=None, include_data=True, compress=False):
    """
    Crear respaldo de la base de datos usando pg_dump
    
    Args:
        output_file (str): Archivo de salida (opcional)
        include_data (bool): Incluir datos en el respaldo
        compress (bool): Comprimir el respaldo
    """
    print("💾 Iniciando respaldo de base de datos...")
    print("=" * 50)
    
    try:
        # Parsear configuración de BD
        db_config = parse_database_url(settings.DATABASE_URL)
        if not db_config:
            return False
        
        # Crear nombre del archivo
        backup_file = create_backup_filename(output_file, compress)
        
        print(f"📋 Configuración del respaldo:")
        print(f"  • Base de datos: {db_config['database']}")
        print(f"  • Host: {db_config['host']}:{db_config['port']}")
        print(f"  • Incluir datos: {'Sí' if include_data else 'No'}")
        print(f"  • Comprimir: {'Sí' if compress else 'No'}")
        print(f"  • Archivo: {backup_file}")
        print()
        
        # Preparar comando pg_dump
        cmd = [
            "pg_dump",
            f"--host={db_config['host']}",
            f"--port={db_config['port']}",
            f"--username={db_config['username']}",
            "--verbose",
            "--clean",
            "--if-exists",
            "--create"
        ]
        
        if not include_data:
            cmd.append("--schema-only")
        
        cmd.append(db_config['database'])
        
        # Configurar variable de entorno para la contraseña
        env = os.environ.copy()
        if db_config['password']:
            env['PGPASSWORD'] = db_config['password']
        
        print("🔄 Ejecutando pg_dump...")
        
        # Ejecutar pg_dump
        if compress:
            # Comprimir directamente
            with gzip.open(backup_file, 'wt', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    env=env,
                    text=True
                )
        else:
            # Sin compresión
            with open(backup_file, 'w', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    env=env,
                    text=True
                )
        
        # Verificar resultado
        if result.returncode == 0:
            file_size = Path(backup_file).stat().st_size
            size_mb = file_size / (1024 * 1024)
            
            print("=" * 50)
            print("✅ Respaldo creado exitosamente!")
            print(f"📁 Archivo: {backup_file}")
            print(f"📏 Tamaño: {size_mb:.2f} MB")
            
            # Mostrar información adicional del respaldo
            print(f"\n📋 Detalles del respaldo:")
            print(f"  • Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  • Tipo: {'Solo estructura' if not include_data else 'Estructura + datos'}")
            print(f"  • Formato: {'Comprimido (gzip)' if compress else 'SQL plano'}")
            
            # Instrucciones para restaurar
            print(f"\n🔄 Para restaurar este respaldo:")
            if compress:
                print(f"   gunzip -c {backup_file} | psql -h {db_config['host']} -U {db_config['username']} -d {db_config['database']}")
            else:
                print(f"   psql -h {db_config['host']} -U {db_config['username']} -d {db_config['database']} -f {backup_file}")
            
            return True
        else:
            print("❌ Error durante el respaldo:")
            print(result.stderr)
            return False
        
    except FileNotFoundError:
        print("❌ Error: pg_dump no encontrado")
        print("💡 Instala PostgreSQL client tools:")
        print("   - Ubuntu/Debian: sudo apt-get install postgresql-client")
        print("   - CentOS/RHEL: sudo yum install postgresql")
        print("   - macOS: brew install postgresql")
        print("   - Windows: Instalar desde https://www.postgresql.org/download/")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado creando respaldo: {e}")
        return False


def restore_backup(backup_file, drop_existing=False):
    """
    Restaurar base de datos desde un respaldo
    
    Args:
        backup_file (str): Archivo de respaldo
        drop_existing (bool): Eliminar BD existente antes de restaurar
    """
    print(f"🔄 Restaurando respaldo desde: {backup_file}")
    print("=" * 50)
    
    try:
        # Verificar que el archivo existe
        if not Path(backup_file).exists():
            print(f"❌ Archivo de respaldo no encontrado: {backup_file}")
            return False
        
        # Parsear configuración de BD
        db_config = parse_database_url(settings.DATABASE_URL)
        if not db_config:
            return False
        
        print(f"📋 Configuración de restauración:")
        print(f"  • Base de datos: {db_config['database']}")
        print(f"  • Host: {db_config['host']}:{db_config['port']}")
        print(f"  • Archivo: {backup_file}")
        print(f"  • Eliminar existente: {'Sí' if drop_existing else 'No'}")
        print()
        
        # Configurar variable de entorno para la contraseña
        env = os.environ.copy()
        if db_config['password']:
            env['PGPASSWORD'] = db_config['password']
        
        # Comando de restauración
        if backup_file.endswith('.gz'):
            # Archivo comprimido
            cmd = f"gunzip -c {backup_file} | psql -h {db_config['host']} -p {db_config['port']} -U {db_config['username']} -d {db_config['database']}"
            result = subprocess.run(cmd, shell=True, env=env)
        else:
            # Archivo sin comprimir
            cmd = [
                "psql",
                f"--host={db_config['host']}",
                f"--port={db_config['port']}",
                f"--username={db_config['username']}",
                f"--dbname={db_config['database']}",
                f"--file={backup_file}"
            ]
            result = subprocess.run(cmd, env=env)
        
        if result.returncode == 0:
            print("✅ Respaldo restaurado exitosamente!")
            return True
        else:
            print("❌ Error durante la restauración")
            return False
        
    except Exception as e:
        print(f"❌ Error inesperado restaurando respaldo: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gestionar respaldos de base de datos SGD Colca")
    subparsers = parser.add_subparsers(dest="action", help="Acción a realizar")
    
    # Comando para crear respaldo
    backup_parser = subparsers.add_parser("create", help="Crear respaldo")
    backup_parser.add_argument("--output", "-o", help="Archivo de salida")
    backup_parser.add_argument("--no-data", action="store_true", help="Solo estructura (sin datos)")
    backup_parser.add_argument("--compress", action="store_true", help="Comprimir respaldo")
    
    # Comando para restaurar respaldo
    restore_parser = subparsers.add_parser("restore", help="Restaurar respaldo")
    restore_parser.add_argument("file", help="Archivo de respaldo")
    restore_parser.add_argument("--drop", action="store_true", help="Eliminar BD existente")
    
    args = parser.parse_args()
    
    if args.action == "create":
        success = create_backup(
            output_file=args.output,
            include_data=not args.no_data,
            compress=args.compress
        )
    elif args.action == "restore":
        success = restore_backup(
            backup_file=args.file,
            drop_existing=args.drop
        )
    else:
        parser.print_help()
        success = False
    
    sys.exit(0 if success else 1)