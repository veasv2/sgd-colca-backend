# scripts/database/init_db.py
"""
Script para inicializar la base de datos desde cero
Aplica migraciones y carga datos iniciales
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from sqlalchemy.orm import Session
from alembic import command
from alembic.config import Config
from app.core.security import generate_password_hash

from app.core.database import engine, SessionLocal
from app.models import (
    Usuario, Permiso, UnidadOrganica, Puesto
)
from app.data import (
    PERMISOS_INICIALES,
    MUNICIPALIDAD_PRINCIPAL,
    UNIDADES_ORGANICAS_INICIALES, 
    PUESTOS_INICIALES,
    USUARIO_ADMIN_INICIAL
)


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


def create_initial_permissions(db: Session):
    """Crear permisos iniciales del sistema"""
    print("🔐 Creando permisos iniciales...")
    
    try:
        for permiso_data in PERMISOS_INICIALES:
            # Verificar si el permiso ya existe
            existing = db.query(Permiso).filter(
                Permiso.codigo == permiso_data["codigo"]
            ).first()
            
            if not existing:
                permiso = Permiso(**permiso_data)
                db.add(permiso)
                print(f"  ➕ Permiso creado: {permiso_data['codigo']}")
            else:
                print(f"  ⏭️ Permiso ya existe: {permiso_data['codigo']}")
        
        db.commit()
        print("✅ Permisos iniciales creados")
        return True
        
    except Exception as e:
        print(f"❌ Error creando permisos: {e}")
        db.rollback()
        return False


def create_organizational_structure(db: Session):
    """Crear estructura organizacional inicial"""
    print("🏢 Creando estructura organizacional...")
    
    try:
        # 1. Crear municipalidad principal
        municipalidad = db.query(UnidadOrganica).filter(
            UnidadOrganica.sigla == MUNICIPALIDAD_PRINCIPAL["sigla"]
        ).first()
        
        if not municipalidad:
            municipalidad = UnidadOrganica(**MUNICIPALIDAD_PRINCIPAL)
            db.add(municipalidad)
            db.flush()  # Para obtener el ID
            print(f"  ➕ Municipalidad creada: {MUNICIPALIDAD_PRINCIPAL['nombre']}")
        
        # 2. Crear unidades orgánicas
        unidades_map = {MUNICIPALIDAD_PRINCIPAL["sigla"]: municipalidad}
        
        for unidad_data in UNIDADES_ORGANICAS_INICIALES:
            existing = db.query(UnidadOrganica).filter(
                UnidadOrganica.sigla == unidad_data["sigla"]
            ).first()
            
            if not existing:
                # Resolver unidad padre si existe
                unidad_padre_id = None
                if "unidad_padre_sigla" in unidad_data:
                    padre_sigla = unidad_data.pop("unidad_padre_sigla")
                    if padre_sigla in unidades_map:
                        unidad_padre_id = unidades_map[padre_sigla].id
                    else:
                        # Buscar en la base de datos
                        padre = db.query(UnidadOrganica).filter(
                            UnidadOrganica.sigla == padre_sigla
                        ).first()
                        if padre:
                            unidad_padre_id = padre.id
                
                unidad_data["unidad_padre_id"] = unidad_padre_id
                unidad = UnidadOrganica(**unidad_data)
                db.add(unidad)
                db.flush()
                
                unidades_map[unidad.sigla] = unidad
                print(f"  ➕ Unidad creada: {unidad.sigla} - {unidad.nombre}")
            else:
                unidades_map[existing.sigla] = existing
                print(f"  ⏭️ Unidad ya existe: {existing.sigla}")
        
        db.commit()
        print("✅ Estructura organizacional creada")
        return unidades_map
        
    except Exception as e:
        print(f"❌ Error creando estructura organizacional: {e}")
        db.rollback()
        return None


def create_initial_positions(db: Session, unidades_map: dict):
    """Crear puestos iniciales"""
    print("👥 Creando puestos iniciales...")
    
    try:
        puestos_map = {}
        
        for puesto_data in PUESTOS_INICIALES:
            existing = db.query(Puesto).filter(
                Puesto.codigo == puesto_data["codigo"]
            ).first()
            
            if not existing:
                # Resolver unidad orgánica
                unidad_sigla = puesto_data.pop("unidad_organica_sigla")
                if unidad_sigla in unidades_map:
                    puesto_data["unidad_organica_id"] = unidades_map[unidad_sigla].id
                
                # Resolver puesto superior si existe
                if "puesto_superior_codigo" in puesto_data:
                    superior_codigo = puesto_data.pop("puesto_superior_codigo")
                    if superior_codigo in puestos_map:
                        puesto_data["puesto_superior_id"] = puestos_map[superior_codigo].id
                    else:
                        # Buscar en la base de datos
                        superior = db.query(Puesto).filter(
                            Puesto.codigo == superior_codigo
                        ).first()
                        if superior:
                            puesto_data["puesto_superior_id"] = superior.id
                
                puesto = Puesto(**puesto_data)
                db.add(puesto)
                db.flush()
                
                puestos_map[puesto.codigo] = puesto
                print(f"  ➕ Puesto creado: {puesto.codigo} - {puesto.nombre}")
            else:
                puestos_map[existing.codigo] = existing
                print(f"  ⏭️ Puesto ya existe: {existing.codigo}")
        
        db.commit()
        print("✅ Puestos iniciales creados")
        return puestos_map
        
    except Exception as e:
        print(f"❌ Error creando puestos: {e}")
        db.rollback()
        return None


def create_admin_user(db: Session, puestos_map: dict):
    """Crear usuario administrador inicial"""
    print("👤 Creando usuario administrador...")
    
    try:
        existing = db.query(Usuario).filter(
            Usuario.username == USUARIO_ADMIN_INICIAL["username"]
        ).first()
        
        if not existing:
            user_data = USUARIO_ADMIN_INICIAL.copy()
            
            # Hash de la contraseña
            password = user_data.pop("password")
            user_data["password_hash"] = generate_password_hash(password)
            
            # Resolver puesto
            puesto_codigo = user_data.pop("puesto_codigo")
            if puesto_codigo in puestos_map:
                user_data["puesto_id"] = puestos_map[puesto_codigo].id
            
            usuario = Usuario(**user_data)
            db.add(usuario)
            db.commit()
            
            print(f"  ➕ Usuario administrador creado: {USUARIO_ADMIN_INICIAL['username']}")
            print(f"  🔑 Contraseña inicial: {password}")
            print(f"  ⚠️ CAMBIAR CONTRASEÑA EN PRODUCCIÓN")
        else:
            print(f"  ⏭️ Usuario administrador ya existe: {existing.username}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando usuario administrador: {e}")
        db.rollback()
        return False


def init_database(skip_migrations=False):
    """
    Inicializar base de datos completa
    
    Args:
        skip_migrations (bool): Si True, omite las migraciones
    """
    print("🚀 Iniciando inicialización de base de datos...")
    print("=" * 50)
    
    try:
        # 1. Aplicar migraciones
        if not skip_migrations:
            if not apply_migrations():
                return False
            print()
        
        # 2. Crear sesión de base de datos
        db = SessionLocal()
        
        # 3. Crear permisos iniciales
        if not create_initial_permissions(db):
            return False
        print()
        
        # 4. Crear estructura organizacional
        unidades_map = create_organizational_structure(db)
        if not unidades_map:
            return False
        print()
        
        # 5. Crear puestos
        puestos_map = create_initial_positions(db, unidades_map)
        if not puestos_map:
            return False
        print()
        
        # 6. Crear usuario administrador
        if not create_admin_user(db, puestos_map):
            return False
        print()
        
        db.close()
        
        print("=" * 50)
        print("🎉 Base de datos inicializada exitosamente!")
        print()
        print("📋 Resumen:")
        print(f"  • {len(PERMISOS_INICIALES)} permisos creados")
        print(f"  • {len(UNIDADES_ORGANICAS_INICIALES) + 1} unidades orgánicas creadas")
        print(f"  • {len(PUESTOS_INICIALES)} puestos creados")
        print(f"  • 1 usuario administrador creado")
        print()
        print("🔐 Acceso inicial:")
        print(f"  Usuario: {USUARIO_ADMIN_INICIAL['username']}")
        print(f"  Email: {USUARIO_ADMIN_INICIAL['email']}")
        print("  ⚠️ CAMBIAR CONTRASEÑA EN PRODUCCIÓN")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fatal en inicialización: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Inicializar base de datos SGD Colca")
    parser.add_argument(
        "--skip-migrations", 
        action="store_true",
        help="Omitir aplicación de migraciones"
    )
    
    args = parser.parse_args()
    
    success = init_database(skip_migrations=args.skip_migrations)
    sys.exit(0 if success else 1)