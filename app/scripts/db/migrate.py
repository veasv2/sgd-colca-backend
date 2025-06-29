#!/usr/bin/env python3
"""
Ruta: app/scripts/db/migrate.py

Script para aplicar las migraciones de Alembic al esquema actual.
Ejecutar: python scripts/db/migrate.py
"""

import subprocess
import sys

def main():
    print("=== APLICANDO MIGRACIONES CON ALEMBIC ===")

    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("[OK] Migraciones aplicadas exitosamente")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] No se pudieron aplicar las migraciones: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
