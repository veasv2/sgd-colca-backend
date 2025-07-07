"""
Script para inicializar la base de datos desde cero
Aplica migraciones (sin insertar datos iniciales)
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from alembic import command
from alembic.config import Config

def apply_migrations():
    """Aplicar todas las migraciones de Alembic"""
    try:
        print("📊 Aplicando migraciones de base de datos...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✅ Migraciones aplicadas exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error aplicando migraciones: {e}")
        return False

def init_database():
    """
    Inicializar base de datos (solo migraciones)
    """
    print("🚀 Iniciando inicialización de base de datos...")
    print("=" * 50)
    
    try:
        if not apply_migrations():
            return False
        
        print("=" * 50)
        print("🎉 Base de datos creada y migraciones aplicadas exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error fatal en inicialización: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
