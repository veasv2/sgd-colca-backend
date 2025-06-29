#!/usr/bin/env python3
# manage.py
"""
CLI de gestión para SGD Colca
Punto de entrada para comandos de administración
"""

import sys
import argparse
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))


def init_db_command(args):
    """Comando para inicializar la base de datos"""
    from scripts.database.init_db import init_database
    
    print("🚀 Inicializando base de datos...")
    success = init_database(skip_migrations=args.skip_migrations)
    
    if success:
        print("\n✅ Base de datos inicializada correctamente")
        return 0
    else:
        print("\n❌ Error inicializando base de datos")
        return 1


def seed_data_command(args):
    """Comando para poblar datos de prueba"""
    from scripts.database.seed_data import seed_test_data
    
    print("🌱 Poblando datos de prueba...")
    success = seed_test_data(
        include_users=args.users,
        include_extended_org=args.extended_org,
        scenario=args.scenario
    )
    
    if success:
        print("\n✅ Datos de prueba cargados correctamente")
        return 0
    else:
        print("\n❌ Error cargando datos de prueba")
        return 1


def reset_db_command(args):
    """Comando para resetear la base de datos"""
    from scripts.database.reset_db import reset_database
    
    # Confirmación de seguridad
    if not args.force:
        confirmation = input("⚠️ ¿Estás seguro de que quieres ELIMINAR todos los datos? (escriba 'SI' para confirmar): ")
        if confirmation != "SI":
            print("❌ Operación cancelada")
            return 1
    
    print("🔄 Reseteando base de datos...")
    success = reset_database(reinit=args.reinit)
    
    if success:
        print("\n✅ Base de datos reseteada correctamente")
        return 0
    else:
        print("\n❌ Error reseteando base de datos")
        return 1


def backup_db_command(args):
    """Comando para crear respaldo de la base de datos"""
    from scripts.database.backup_db import create_backup
    
    print("💾 Creando respaldo de base de datos...")
    success = create_backup(
        output_file=args.output,
        include_data=args.include_data,
        compress=args.compress
    )
    
    if success:
        print("\n✅ Respaldo creado correctamente")
        return 0
    else:
        print("\n❌ Error creando respaldo")
        return 1


def migrate_command(args):
    """Comando para ejecutar migraciones"""
    import subprocess
    
    if args.action == "upgrade":
        cmd = ["alembic", "upgrade", args.revision or "head"]
    elif args.action == "downgrade":
        cmd = ["alembic", "downgrade", args.revision or "-1"]
    elif args.action == "current":
        cmd = ["alembic", "current"]
    elif args.action == "history":
        cmd = ["alembic", "history"]
    elif args.action == "revision":
        if not args.message:
            print("❌ Se requiere un mensaje para crear una revisión")
            return 1
        cmd = ["alembic", "revision", "--autogenerate", "-m", args.message]
    else:
        print(f"❌ Acción no válida: {args.action}")
        return 1
    
    print(f"🔄 Ejecutando: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def status_command(args):
    """Comando para mostrar estado del sistema"""
    from scripts.database.status import show_database_status
    
    print("📊 Estado del sistema SGD Colca")
    print("=" * 40)
    show_database_status(detailed=args.detailed)
    return 0


def main():
    """Función principal del CLI"""
    parser = argparse.ArgumentParser(
        description="Sistema de Gestión Documental - Colca",
        prog="manage.py"
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Comandos disponibles",
        metavar="COMANDO"
    )
    
    # === Comando: init-db ===
    init_parser = subparsers.add_parser(
        "init-db",
        help="Inicializar base de datos completa"
    )
    init_parser.add_argument(
        "--skip-migrations",
        action="store_true",
        help="Omitir aplicación de migraciones"
    )
    init_parser.set_defaults(func=init_db_command)
    
    # === Comando: seed-data ===
    seed_parser = subparsers.add_parser(
        "seed-data",
        help="Poblar base de datos con datos de prueba"
    )
    seed_parser.add_argument(
        "--users",
        action="store_true",
        help="Incluir usuarios de prueba"
    )
    seed_parser.add_argument(
        "--extended-org",
        action="store_true", 
        help="Incluir estructura organizacional extendida"
    )
    seed_parser.add_argument(
        "--scenario",
        choices=["basico", "completo", "desarrollo"],
        default="basico",
        help="Escenario de datos a cargar"
    )
    seed_parser.set_defaults(func=seed_data_command)
    
    # === Comando: reset-db ===
    reset_parser = subparsers.add_parser(
        "reset-db",
        help="Resetear base de datos (ELIMINA TODOS LOS DATOS)"
    )
    reset_parser.add_argument(
        "--force",
        action="store_true",
        help="Forzar reset sin confirmación (PELIGROSO)"
    )
    reset_parser.add_argument(
        "--reinit",
        action="store_true",
        help="Reinicializar automáticamente después del reset"
    )
    reset_parser.set_defaults(func=reset_db_command)
    
    # === Comando: backup ===
    backup_parser = subparsers.add_parser(
        "backup",
        help="Crear respaldo de la base de datos"
    )
    backup_parser.add_argument(
        "--output", "-o",
        help="Archivo de salida (por defecto: backup_YYYYMMDD_HHMMSS.sql)"
    )
    backup_parser.add_argument(
        "--include-data",
        action="store_true",
        default=True,
        help="Incluir datos en el respaldo"
    )
    backup_parser.add_argument(
        "--compress",
        action="store_true",
        help="Comprimir el respaldo"
    )
    backup_parser.set_defaults(func=backup_db_command)
    
    # === Comando: migrate ===
    migrate_parser = subparsers.add_parser(
        "migrate",
        help="Gestionar migraciones de Alembic"
    )
    migrate_parser.add_argument(
        "action",
        choices=["upgrade", "downgrade", "current", "history", "revision"],
        help="Acción a realizar"
    )
    migrate_parser.add_argument(
        "--revision", "-r",
        help="Revisión específica (para upgrade/downgrade)"
    )
    migrate_parser.add_argument(
        "--message", "-m",
        help="Mensaje para nueva revisión"
    )
    migrate_parser.set_defaults(func=migrate_command)
    
    # === Comando: status ===
    status_parser = subparsers.add_parser(
        "status",
        help="Mostrar estado del sistema"
    )
    status_parser.add_argument(
        "--detailed",
        action="store_true",
        help="Mostrar información detallada"
    )
    status_parser.set_defaults(func=status_command)
    
    # === Parsear argumentos y ejecutar ===
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n⏹️ Operación cancelada por el usuario")
        return 1
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        if hasattr(args, 'debug') and args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())