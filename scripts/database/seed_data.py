# scripts/database/seed_data.py
"""
Script para poblar la base de datos con datos de prueba
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from sqlalchemy.orm import Session
from app.core.security import generate_password_hash

from app.core.database import SessionLocal
from app.models import Usuario, UnidadOrganica, Puesto
from app.data import (
    USUARIOS_TEST,
    UNIDADES_TEST,
    PUESTOS_TEST,
    ESCENARIOS_TEST
)


def create_test_users(db: Session, scenario="basico"):
    """Crear usuarios de prueba"""
    print("👥 Creando usuarios de prueba...")
    
    try:
        # Determinar qué usuarios crear según el escenario
        if scenario == "basico":
            usuarios_a_crear = [u for u in USUARIOS_TEST if u["username"] in ESCENARIOS_TEST["usuarios_basicos"]["usuarios"]]
        else:
            usuarios_a_crear = USUARIOS_TEST
        
        created_count = 0
        
        for user_data in usuarios_a_crear:
            # Verificar si el usuario ya existe
            existing = db.query(Usuario).filter(
                Usuario.username == user_data["username"]
            ).first()
            
            if not existing:
                user_info = user_data.copy()
                
                # Hash de la contraseña
                password = user_info.pop("password")
                user_info["password_hash"] = generate_password_hash(password)
                
                # Resolver puesto si existe
                puesto_codigo = user_info.pop("puesto_codigo", None)
                if puesto_codigo:
                    puesto = db.query(Puesto).filter(
                        Puesto.codigo == puesto_codigo
                    ).first()
                    if puesto:
                        user_info["puesto_id"] = puesto.id
                
                usuario = Usuario(**user_info)
                db.add(usuario)
                created_count += 1
                print(f"  ➕ Usuario creado: {user_data['username']} ({user_data['tipo_usuario']})")
            else:
                print(f"  ⏭️ Usuario ya existe: {user_data['username']}")
        
        db.commit()
        print(f"✅ {created_count} usuarios de prueba creados")
        return True
        
    except Exception as e:
        print(f"❌ Error creando usuarios de prueba: {e}")
        db.rollback()
        return False


def create_extended_organization(db: Session):
    """Crear estructura organizacional extendida"""
    print("🏢 Creando estructura organizacional extendida...")
    
    try:
        # Crear unidades adicionales
        for unidad_data in UNIDADES_TEST:
            existing = db.query(UnidadOrganica).filter(
                UnidadOrganica.sigla == unidad_data["sigla"]
            ).first()
            
            if not existing:
                unidad_info = unidad_data.copy()
                
                # Resolver unidad padre
                if "unidad_padre_sigla" in unidad_info:
                    padre_sigla = unidad_info.pop("unidad_padre_sigla")
                    padre = db.query(UnidadOrganica).filter(
                        UnidadOrganica.sigla == padre_sigla
                    ).first()
                    if padre:
                        unidad_info["unidad_padre_id"] = padre.id
                
                unidad = UnidadOrganica(**unidad_info)
                db.add(unidad)
                print(f"  ➕ Unidad creada: {unidad_data['sigla']} - {unidad_data['nombre']}")
            else:
                print(f"  ⏭️ Unidad ya existe: {unidad_data['sigla']}")
        
        # Crear puestos adicionales
        for puesto_data in PUESTOS_TEST:
            existing = db.query(Puesto).filter(
                Puesto.codigo == puesto_data["codigo"]
            ).first()
            
            if not existing:
                puesto_info = puesto_data.copy()
                
                # Resolver unidad orgánica
                unidad_sigla = puesto_info.pop("unidad_organica_sigla")
                unidad = db.query(UnidadOrganica).filter(
                    UnidadOrganica.sigla == unidad_sigla
                ).first()
                if unidad:
                    puesto_info["unidad_organica_id"] = unidad.id
                
                # Resolver puesto superior
                if "puesto_superior_codigo" in puesto_info:
                    superior_codigo = puesto_info.pop("puesto_superior_codigo")
                    superior = db.query(Puesto).filter(
                        Puesto.codigo == superior_codigo
                    ).first()
                    if superior:
                        puesto_info["puesto_superior_id"] = superior.id
                
                puesto = Puesto(**puesto_info)
                db.add(puesto)
                print(f"  ➕ Puesto creado: {puesto_data['codigo']} - {puesto_data['nombre']}")
            else:
                print(f"  ⏭️ Puesto ya existe: {puesto_data['codigo']}")
        
        db.commit()
        print("✅ Estructura organizacional extendida creada")
        return True
        
    except Exception as e:
        print(f"❌ Error creando estructura extendida: {e}")
        db.rollback()
        return False


def seed_test_data(include_users=True, include_extended_org=False, scenario="basico"):
    """
    Poblar base de datos con datos de prueba
    
    Args:
        include_users (bool): Incluir usuarios de prueba
        include_extended_org (bool): Incluir estructura organizacional extendida
        scenario (str): Escenario de datos (basico, completo, desarrollo)
    """
    print("🌱 Iniciando población de datos de prueba...")
    print("=" * 50)
    print(f"📋 Configuración:")
    print(f"  • Escenario: {scenario}")
    print(f"  • Incluir usuarios: {'Sí' if include_users else 'No'}")
    print(f"  • Estructura extendida: {'Sí' if include_extended_org else 'No'}")
    print()
    
    try:
        db = SessionLocal()
        
        # 1. Crear estructura organizacional extendida si se solicita
        if include_extended_org:
            if not create_extended_organization(db):
                return False
            print()
        
        # 2. Crear usuarios de prueba si se solicita
        if include_users:
            if not create_test_users(db, scenario):
                return False
            print()
        
        db.close()
        
        print("=" * 50)
        print("🎉 Datos de prueba cargados exitosamente!")
        print()
        
        if include_users:
            print("🔐 Usuarios de prueba creados:")
            usuarios_scenario = USUARIOS_TEST
            if scenario == "basico":
                usuarios_scenario = [u for u in USUARIOS_TEST if u["username"] in ESCENARIOS_TEST["usuarios_basicos"]["usuarios"]]
            
            for user in usuarios_scenario:
                print(f"  • {user['username']} ({user['tipo_usuario']}) - Email: {user['email']}")
            print("  🔑 Contraseña para todos: test123")
        
        print("\n⚠️ Estos datos son SOLO para desarrollo/testing")
        print("❌ NO usar en producción")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fatal poblando datos: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Poblar datos de prueba SGD Colca")
    parser.add_argument(
        "--scenario",
        choices=["basico", "completo", "desarrollo"],
        default="basico",
        help="Escenario de datos a cargar"
    )
    parser.add_argument(
        "--no-users",
        action="store_true",
        help="No crear usuarios de prueba"
    )
    parser.add_argument(
        "--extended-org",
        action="store_true",
        help="Incluir estructura organizacional extendida"
    )
    
    args = parser.parse_args()
    
    success = seed_test_data(
        include_users=not args.no_users,
        include_extended_org=args.extended_org,
        scenario=args.scenario
    )
    
    sys.exit(0 if success else 1)