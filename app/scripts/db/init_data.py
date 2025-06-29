#!/usr/bin/env python3
"""
Ruta: app/scripts/db/init_data.py

Script para insertar datos iniciales en la base de datos del sistema SGD-Colca.
Ejecutar: python scripts/db/init_data.py
"""

import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import engine
from app.models.seguridad_models import Usuario, Permiso, TipoPermiso, TipoUsuario
from app.models.organizacion_models import UnidadOrganica, Puesto
from passlib.hash import bcrypt
import uuid

def crear_datos_iniciales(db: Session):
    print("=== INSERTANDO DATOS INICIALES ===")

    # 1. Crear Unidad Orgánica inicial
    unidad = UnidadOrganica(
        nombre="Alcaldía",
        sigla="ALC",
        tipo="Despacho",
        nivel=1,
        activo=True,
        creado_por=None  # Puede actualizarse luego
    )
    db.add(unidad)
    db.flush()

    # 2. Crear Puesto inicial
    puesto = Puesto(
        nombre="Alcalde",
        codigo="ALC-001",
        descripcion="Máxima autoridad municipal",
        unidad_organica_id=unidad.id,
        nivel_jerarquico=1,
        activo=True,
        creado_por=None
    )
    db.add(puesto)
    db.flush()

    # 3. Crear Usuario SUPERADMIN
    usuario = Usuario(
        username="admin",
        email="admin@colca.gob.pe",
        password_hash=bcrypt.hash("admin123"),
        nombres="Administrador",
        apellidos="SGD-Colca",
        dni="00000000",
        telefono="999999999",
        tipo_usuario=TipoUsuario.SUPERADMIN,
        estado="ACTIVO",
        puesto_id=puesto.id
    )
    db.add(usuario)

    # 4. Crear permisos base (ejemplo mínimo)
    permisos = [
        Permiso(codigo="USUARIOS_READ", nombre="Ver Usuarios", descripcion="Puede ver usuarios", modulo="Usuarios", tipo_permiso=TipoPermiso.LECTURA),
        Permiso(codigo="USUARIOS_CREATE", nombre="Crear Usuarios", descripcion="Puede crear usuarios", modulo="Usuarios", tipo_permiso=TipoPermiso.ESCRITURA),
        Permiso(codigo="USUARIOS_ADMIN", nombre="Administrar Usuarios", descripcion="Acceso completo", modulo="Usuarios", tipo_permiso=TipoPermiso.ADMINISTRACION),
    ]
    db.add_all(permisos)

    try:
        db.commit()
        print("[OK] Datos iniciales insertados correctamente.")
    except IntegrityError:
        db.rollback()
        print("[INFO] Los datos iniciales ya existen, se omite inserción.")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error insertando datos iniciales: {e}")
        sys.exit(1)

def main():
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        crear_datos_iniciales(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
