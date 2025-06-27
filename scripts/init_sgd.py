# scripts/init_sgd.py
"""
Script de Inicialización del Sistema de Gobernanza Digital (SGD)
Municipalidad Distrital de Colca

Este script configura el sistema desde cero:
1. Crea las tablas de base de datos
2. Establece el usuario SUPERADMIN inicial
3. Configura la estructura organizacional básica de Colca
4. Carga datos de prueba para desarrollo

Uso:
    python scripts/init_sgd.py [--environment {dev|prod}] [--force]
"""

import sys
import os
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any

# Agregar el directorio padre al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Importaciones locales
from app.core.database import engine, SessionLocal, create_database, Base
from app.models.auth_models import Usuario, Area, Puesto
from app.core.security import create_password_hash, validate_password_strength
from app.schemas.auth_schemas import TipoUsuarioEnum, EstadoUsuarioEnum
from app.core.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sgd_initialization.log')
    ]
)
logger = logging.getLogger(__name__)

class SGDInitializer:
    """
    Clase principal para inicializar el Sistema de Gobernanza Digital
    """
    
    def __init__(self, environment: str = "dev", force: bool = False):
        self.environment = environment
        self.force = force
        self.db: Session = SessionLocal()
        
        logger.info(f"Inicializando SGD para entorno: {environment}")
        if force:
            logger.warning("Modo FORCE activado - se recrearán las tablas")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
        if exc_type:
            logger.error(f"Error durante inicialización: {exc_val}")
    
    def initialize_system(self) -> bool:
        """
        Ejecuta la inicialización completa del sistema
        
        Returns:
            bool: True si la inicialización fue exitosa
        """
        try:
            logger.info("=== INICIANDO CONFIGURACIÓN DEL SGD ===")
            
            # Paso 1: Configurar base de datos
            self._setup_database()
            
            # Paso 2: Crear usuario SUPERADMIN
            superadmin_created = self._create_superadmin()
            
            # Paso 3: Configurar estructura organizacional
            self._setup_organizational_structure()
            
            # Paso 4: Crear datos de prueba (solo en desarrollo)
            if self.environment == "dev":
                self._create_test_data()
            
            # Paso 5: Validación final
            self._validate_initialization()
            
            logger.info("=== INICIALIZACIÓN COMPLETADA EXITOSAMENTE ===")
            return True
            
        except Exception as e:
            logger.error(f"Error durante la inicialización: {e}")
            self.db.rollback()
            return False
    
    def _setup_database(self):
        """Configura la base de datos y crea las tablas"""
        logger.info("Configurando base de datos...")
        
        if self.force:
            logger.warning("Eliminando tablas existentes...")
            Base.metadata.drop_all(bind=engine)
        
        # Crear todas las tablas
        create_database()
        logger.info("Tablas de base de datos creadas/verificadas")
    
    def _create_superadmin(self) -> bool:
        """
        Crea el usuario SUPERADMIN inicial
        
        Returns:
            bool: True si se creó el usuario, False si ya existía
        """
        logger.info("Configurando usuario SUPERADMIN...")
        
        # Verificar si ya existe un SUPERADMIN
        existing_superadmin = self.db.query(Usuario).filter(
            Usuario.tipo_usuario == TipoUsuarioEnum.SUPERADMIN
        ).first()
        
        if existing_superadmin and not self.force:
            logger.info(f"SUPERADMIN ya existe: {existing_superadmin.username}")
            return False
        
        # Configuración del SUPERADMIN
        superadmin_config = {
            "username": "superadmin",
            "email": "admin@colca.gob.pe",
            "password": "SGD2025!Colca#Admin",  # Contraseña temporal segura
            "nombres": "Administrador",
            "apellidos": "del Sistema",
            "dni": "00000000",  # DNI temporal
            "telefono": "+51900000000"
        }
        
        # Validar contraseña
        password_validation = validate_password_strength(superadmin_config["password"])
        if not password_validation["valid"]:
            raise ValueError(f"Contraseña SUPERADMIN insegura: {password_validation['errors']}")
        
        # Eliminar SUPERADMIN existente si force=True
        if existing_superadmin and self.force:
            logger.warning(f"Eliminando SUPERADMIN existente: {existing_superadmin.username}")
            self.db.delete(existing_superadmin)
            self.db.commit()
        
        # Crear nuevo SUPERADMIN
        superadmin = Usuario(
            username=superadmin_config["username"],
            email=superadmin_config["email"],
            password_hash=create_password_hash(superadmin_config["password"]),
            nombres=superadmin_config["nombres"],
            apellidos=superadmin_config["apellidos"],
            dni=superadmin_config["dni"],
            telefono=superadmin_config["telefono"],
            tipo_usuario=TipoUsuarioEnum.SUPERADMIN,
            estado=EstadoUsuarioEnum.ACTIVO,
            puesto_id=None  # SUPERADMIN no tiene puesto específico
        )
        
        self.db.add(superadmin)
        self.db.commit()
        self.db.refresh(superadmin)
        
        logger.info(f"✅ SUPERADMIN creado exitosamente")
        logger.info(f"   Username: {superadmin_config['username']}")
        logger.info(f"   Email: {superadmin_config['email']}")
        logger.warning(f"   ⚠️  CAMBIAR CONTRASEÑA EN PRIMER LOGIN")
        
        return True
    
    def _setup_organizational_structure(self):
        """Configura la estructura organizacional básica de la Municipalidad de Colca"""
        logger.info("Configurando estructura organizacional...")
        
        # Definir la estructura organizacional de Colca
        estructura_colca = {
            "areas": [
                # Nivel 1 - Órganos de Alta Dirección
                {"codigo": "ALC", "nombre": "Alcaldía", "descripcion": "Despacho de Alcaldía", "nivel": 1, "padre": None},
                
                # Nivel 2 - Órganos de Control y Asesoramiento
                {"codigo": "OCI", "nombre": "Órgano de Control Institucional", "descripcion": "Control interno municipal", "nivel": 2, "padre": "ALC"},
                {"codigo": "GAL", "nombre": "Gerencia de Asesoría Legal", "descripcion": "Asesoría jurídica municipal", "nivel": 2, "padre": "ALC"},
                {"codigo": "GPP", "nombre": "Gerencia de Planeamiento y Presupuesto", "descripcion": "Planificación y presupuesto institucional", "nivel": 2, "padre": "ALC"},
                
                # Nivel 3 - Gerencia Municipal
                {"codigo": "GM", "nombre": "Gerencia Municipal", "descripcion": "Gerencia general de la municipalidad", "nivel": 3, "padre": "ALC"},
                
                # Nivel 4 - Gerencias de Línea
                {"codigo": "GAF", "nombre": "Gerencia de Administración y Finanzas", "descripcion": "Administración de recursos y finanzas", "nivel": 4, "padre": "GM"},
                {"codigo": "GDU", "nombre": "Gerencia de Desarrollo Urbano", "descripcion": "Desarrollo urbano y territorial", "nivel": 4, "padre": "GM"},
                {"codigo": "GDS", "nombre": "Gerencia de Desarrollo Social", "descripcion": "Programas y servicios sociales", "nivel": 4, "padre": "GM"},
                {"codigo": "GSP", "nombre": "Gerencia de Servicios Públicos", "descripcion": "Servicios públicos locales", "nivel": 4, "padre": "GM"},
                
                # Nivel 5 - Subgerencias y Oficinas
                {"codigo": "SGTH", "nombre": "Subgerencia de Talento Humano", "descripcion": "Gestión del talento humano", "nivel": 5, "padre": "GAF"},
                {"codigo": "SGC", "nombre": "Subgerencia de Contabilidad", "descripcion": "Contabilidad municipal", "nivel": 5, "padre": "GAF"},
                {"codigo": "SGT", "nombre": "Subgerencia de Tesorería", "descripcion": "Tesorería municipal", "nivel": 5, "padre": "GAF"},
                {"codigo": "SGL", "nombre": "Subgerencia de Logística", "descripcion": "Abastecimiento y logística", "nivel": 5, "padre": "GAF"},
                
                {"codigo": "SGOU", "nombre": "Subgerencia de Obras y Urbanismo", "descripcion": "Ejecución de obras públicas", "nivel": 5, "padre": "GDU"},
                {"codigo": "SGCAT", "nombre": "Subgerencia de Catastro", "descripcion": "Catastro municipal", "nivel": 5, "padre": "GDU"},
                
                {"codigo": "OAT", "nombre": "Oficina de Administración Tributaria", "descripcion": "Administración de tributos municipales", "nivel": 5, "padre": "GAF"},
                {"codigo": "UIT", "nombre": "Unidad de Informática y Telecomunicaciones", "descripcion": "Sistemas informáticos", "nivel": 5, "padre": "GAF"},
                {"codigo": "SEC", "nombre": "Secretaría General", "descripcion": "Secretaría general y archivo", "nivel": 5, "padre": "GM"},
                {"codigo": "IMP", "nombre": "Oficina de Imagen Institucional", "descripcion": "Comunicaciones e imagen", "nivel": 5, "padre": "ALC"}
            ],
            "puestos": [
                # Alcaldía
                {"codigo": "ALC-001", "nombre": "Alcalde", "area": "ALC", "nivel": 1, "superior": None},
                
                # Gerencia Municipal
                {"codigo": "GM-001", "nombre": "Gerente Municipal", "area": "GM", "nivel": 2, "superior": "ALC-001"},
                
                # Gerencias de línea
                {"codigo": "GAF-001", "nombre": "Gerente de Administración y Finanzas", "area": "GAF", "nivel": 3, "superior": "GM-001"},
                {"codigo": "GDU-001", "nombre": "Gerente de Desarrollo Urbano", "area": "GDU", "nivel": 3, "superior": "GM-001"},
                {"codigo": "GDS-001", "nombre": "Gerente de Desarrollo Social", "area": "GDS", "nivel": 3, "superior": "GM-001"},
                {"codigo": "GSP-001", "nombre": "Gerente de Servicios Públicos", "area": "GSP", "nivel": 3, "superior": "GM-001"},
                
                # Órganos de control y asesoramiento
                {"codigo": "OCI-001", "nombre": "Jefe del Órgano de Control Institucional", "area": "OCI", "nivel": 2, "superior": "ALC-001"},
                {"codigo": "GAL-001", "nombre": "Gerente de Asesoría Legal", "area": "GAL", "nivel": 2, "superior": "ALC-001"},
                {"codigo": "GPP-001", "nombre": "Gerente de Planeamiento y Presupuesto", "area": "GPP", "nivel": 2, "superior": "ALC-001"},
                
                # Subgerencias
                {"codigo": "SGTH-001", "nombre": "Subgerente de Talento Humano", "area": "SGTH", "nivel": 4, "superior": "GAF-001"},
                {"codigo": "SGC-001", "nombre": "Subgerente de Contabilidad", "area": "SGC", "nivel": 4, "superior": "GAF-001"},
                {"codigo": "SGT-001", "nombre": "Subgerente de Tesorería", "area": "SGT", "nivel": 4, "superior": "GAF-001"},
                {"codigo": "SGL-001", "nombre": "Subgerente de Logística", "area": "SGL", "nivel": 4, "superior": "GAF-001"},
                
                {"codigo": "SGOU-001", "nombre": "Subgerente de Obras y Urbanismo", "area": "SGOU", "nivel": 4, "superior": "GDU-001"},
                {"codigo": "SGCAT-001", "nombre": "Subgerente de Catastro", "area": "SGCAT", "nivel": 4, "superior": "GDU-001"},
                
                # Oficinas y unidades
                {"codigo": "OAT-001", "nombre": "Jefe de Administración Tributaria", "area": "OAT", "nivel": 4, "superior": "GAF-001"},
                {"codigo": "UIT-001", "nombre": "Jefe de Informática y Telecomunicaciones", "area": "UIT", "nivel": 4, "superior": "GAF-001"},
                {"codigo": "SEC-001", "nombre": "Secretario General", "area": "SEC", "nivel": 4, "superior": "GM-001"},
                {"codigo": "IMP-001", "nombre": "Jefe de Imagen Institucional", "area": "IMP", "nivel": 3, "superior": "ALC-001"},
                
                # Especialistas y analistas (ejemplos)
                {"codigo": "SGTH-002", "nombre": "Especialista en Recursos Humanos", "area": "SGTH", "nivel": 5, "superior": "SGTH-001"},
                {"codigo": "SGC-002", "nombre": "Contador Público", "area": "SGC", "nivel": 5, "superior": "SGC-001"},
                {"codigo": "UIT-002", "nombre": "Analista de Sistemas", "area": "UIT", "nivel": 5, "superior": "UIT-001"},
                {"codigo": "SEC-002", "nombre": "Asistente de Secretaría", "area": "SEC", "nivel": 5, "superior": "SEC-001"}
            ]
        }
        
        # Crear áreas
        areas_creadas = {}
        logger.info("Creando áreas organizacionales...")
        
        for area_data in estructura_colca["areas"]:
            try:
                # Buscar área padre si existe
                area_padre_id = None
                if area_data["padre"]:
                    area_padre = areas_creadas.get(area_data["padre"])
                    if area_padre:
                        area_padre_id = area_padre.id
                
                # Verificar si el área ya existe
                existing_area = self.db.query(Area).filter(Area.codigo == area_data["codigo"]).first()
                
                if existing_area and not self.force:
                    logger.info(f"  Área ya existe: {area_data['codigo']}")
                    areas_creadas[area_data["codigo"]] = existing_area
                    continue
                
                if existing_area and self.force:
                    self.db.delete(existing_area)
                    self.db.commit()
                
                # Crear nueva área
                nueva_area = Area(
                    codigo=area_data["codigo"],
                    nombre=area_data["nombre"],
                    descripcion=area_data["descripcion"],
                    nivel=area_data["nivel"],
                    activa=True,
                    area_padre_id=area_padre_id
                )
                
                self.db.add(nueva_area)
                self.db.commit()
                self.db.refresh(nueva_area)
                
                areas_creadas[area_data["codigo"]] = nueva_area
                logger.info(f"  ✅ Área creada: {area_data['codigo']} - {area_data['nombre']}")
                
            except IntegrityError as e:
                self.db.rollback()
                logger.error(f"  ❌ Error al crear área {area_data['codigo']}: {e}")
                raise
        
        # Crear puestos
        puestos_creados = {}
        logger.info("Creando puestos organizacionales...")
        
        for puesto_data in estructura_colca["puestos"]:
            try:
                # Buscar área del puesto
                area = areas_creadas.get(puesto_data["area"])
                if not area:
                    logger.error(f"  ❌ Área no encontrada para puesto {puesto_data['codigo']}: {puesto_data['area']}")
                    continue
                
                # Buscar puesto superior si existe
                puesto_superior_id = None
                if puesto_data["superior"]:
                    puesto_superior = puestos_creados.get(puesto_data["superior"])
                    if puesto_superior:
                        puesto_superior_id = puesto_superior.id
                
                # Verificar si el puesto ya existe
                existing_puesto = self.db.query(Puesto).filter(Puesto.codigo == puesto_data["codigo"]).first()
                
                if existing_puesto and not self.force:
                    logger.info(f"  Puesto ya existe: {puesto_data['codigo']}")
                    puestos_creados[puesto_data["codigo"]] = existing_puesto
                    continue
                
                if existing_puesto and self.force:
                    self.db.delete(existing_puesto)
                    self.db.commit()
                
                # Crear nuevo puesto
                nuevo_puesto = Puesto(
                    codigo=puesto_data["codigo"],
                    nombre=puesto_data["nombre"],
                    descripcion=f"Puesto de {puesto_data['nombre']} en {area.nombre}",
                    area_id=area.id,
                    puesto_superior_id=puesto_superior_id,
                    nivel_jerarquico=puesto_data["nivel"],
                    activo=True
                )
                
                self.db.add(nuevo_puesto)
                self.db.commit()
                self.db.refresh(nuevo_puesto)
                
                puestos_creados[puesto_data["codigo"]] = nuevo_puesto
                logger.info(f"  ✅ Puesto creado: {puesto_data['codigo']} - {puesto_data['nombre']}")
                
            except IntegrityError as e:
                self.db.rollback()
                logger.error(f"  ❌ Error al crear puesto {puesto_data['codigo']}: {e}")
                raise
        
        logger.info(f"✅ Estructura organizacional configurada: {len(areas_creadas)} áreas, {len(puestos_creados)} puestos")
    
    def _create_test_data(self):
        """Crea datos de prueba para desarrollo"""
        logger.info("Creando datos de prueba para desarrollo...")
        
        # Obtener puesto de Alcalde para crear usuario ALCALDE
        puesto_alcalde = self.db.query(Puesto).filter(Puesto.codigo == "ALC-001").first()
        
        if puesto_alcalde:
            # Crear usuario ALCALDE de prueba
            test_alcalde_config = {
                "username": "alcalde",
                "email": "alcalde@colca.gob.pe",
                "password": "Alcalde2025!",
                "nombres": "Juan Carlos",
                "apellidos": "Pérez Mendoza",
                "dni": "12345678",
                "telefono": "+51987654321"
            }
            
            # Verificar si ya existe
            existing_alcalde = self.db.query(Usuario).filter(
                Usuario.tipo_usuario == TipoUsuarioEnum.ALCALDE
            ).first()
            
            if not existing_alcalde:
                alcalde_usuario = Usuario(
                    username=test_alcalde_config["username"],
                    email=test_alcalde_config["email"],
                    password_hash=create_password_hash(test_alcalde_config["password"]),
                    nombres=test_alcalde_config["nombres"],
                    apellidos=test_alcalde_config["apellidos"],
                    dni=test_alcalde_config["dni"],
                    telefono=test_alcalde_config["telefono"],
                    tipo_usuario=TipoUsuarioEnum.ALCALDE,
                    estado=EstadoUsuarioEnum.ACTIVO,
                    puesto_id=puesto_alcalde.id
                )
                
                self.db.add(alcalde_usuario)
                self.db.commit()
                logger.info(f"✅ Usuario ALCALDE de prueba creado: {test_alcalde_config['username']}")
        
        # Crear algunos funcionarios de prueba
        funcionarios_prueba = [
            {
                "username": "gerente.municipal",
                "email": "gm@colca.gob.pe",
                "password": "GM2025!Test",
                "nombres": "María Elena",
                "apellidos": "García López",
                "dni": "87654321",
                "puesto_codigo": "GM-001"
            },
            {
                "username": "gerente.gaf",
                "email": "gaf@colca.gob.pe",
                "password": "GAF2025!Test",
                "nombres": "Carlos Alberto",
                "apellidos": "Rodríguez Silva",
                "dni": "11223344",
                "puesto_codigo": "GAF-001"
            },
            {
                "username": "analista.sistemas",
                "email": "sistemas@colca.gob.pe",
                "password": "UIT2025!Test",
                "nombres": "Ana Sofía",
                "apellidos": "Vargas Huamán",
                "dni": "55667788",
                "puesto_codigo": "UIT-002"
            }
        ]
        
        for func_data in funcionarios_prueba:
            try:
                # Buscar puesto
                puesto = self.db.query(Puesto).filter(Puesto.codigo == func_data["puesto_codigo"]).first()
                
                if puesto:
                    # Verificar si ya existe el usuario
                    existing_user = self.db.query(Usuario).filter(Usuario.username == func_data["username"]).first()
                    
                    if not existing_user:
                        funcionario = Usuario(
                            username=func_data["username"],
                            email=func_data["email"],
                            password_hash=create_password_hash(func_data["password"]),
                            nombres=func_data["nombres"],
                            apellidos=func_data["apellidos"],
                            dni=func_data["dni"],
                            tipo_usuario=TipoUsuarioEnum.FUNCIONARIO,
                            estado=EstadoUsuarioEnum.ACTIVO,
                            puesto_id=puesto.id
                        )
                        
                        self.db.add(funcionario)
                        self.db.commit()
                        logger.info(f"✅ Funcionario de prueba creado: {func_data['username']}")
                    else:
                        logger.info(f"  Funcionario ya existe: {func_data['username']}")
                
            except Exception as e:
                self.db.rollback()
                logger.error(f"❌ Error al crear funcionario {func_data['username']}: {e}")
        
        logger.info("✅ Datos de prueba creados para desarrollo")
    
    def _validate_initialization(self):
        """Valida que la inicialización se haya completado correctamente"""
        logger.info("Validando inicialización...")
        
        # Verificar SUPERADMIN
        superadmin_count = self.db.query(Usuario).filter(
            Usuario.tipo_usuario == TipoUsuarioEnum.SUPERADMIN
        ).count()
        
        if superadmin_count == 0:
            raise ValueError("No se encontró usuario SUPERADMIN")
        
        # Verificar estructura organizacional
        areas_count = self.db.query(Area).filter(Area.activa == True).count()
        puestos_count = self.db.query(Puesto).filter(Puesto.activo == True).count()
        
        if areas_count == 0:
            raise ValueError("No se encontraron áreas organizacionales")
        
        if puestos_count == 0:
            raise ValueError("No se encontraron puestos organizacionales")
        
        # Estadísticas finales
        total_usuarios = self.db.query(Usuario).count()
        usuarios_asignados = self.db.query(Usuario).filter(Usuario.puesto_id.isnot(None)).count()
        
        logger.info("=== ESTADÍSTICAS DE INICIALIZACIÓN ===")
        logger.info(f"Áreas creadas: {areas_count}")
        logger.info(f"Puestos creados: {puestos_count}")
        logger.info(f"Usuarios totales: {total_usuarios}")
        logger.info(f"Usuarios con puesto asignado: {usuarios_asignados}")
        logger.info(f"Puestos vacantes: {puestos_count - usuarios_asignados}")
        
        logger.info("✅ Validación completada exitosamente")

def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(
        description="Inicializa el Sistema de Gobernanza Digital (SGD) de la Municipalidad Distrital de Colca"
    )
    parser.add_argument(
        "--environment",
        choices=["dev", "prod"],
        default="dev",
        help="Entorno de inicialización"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forzar recreación de datos existentes"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("SISTEMA DE GOBERNANZA DIGITAL (SGD)")
    print("MUNICIPALIDAD DISTRITAL DE COLCA")
    print("SCRIPT DE INICIALIZACIÓN")
    print("=" * 60)
    print()
    
    if args.force:
        confirm = input("⚠️  ADVERTENCIA: Se eliminarán todos los datos existentes. ¿Continuar? (s/N): ")
        if confirm.lower() != 's':
            print("Inicialización cancelada.")
            return
    
    try:
        with SGDInitializer(args.environment, args.force) as initializer:
            success = initializer.initialize_system()
            
            if success:
                print("\n🎉 ¡INICIALIZACIÓN COMPLETADA EXITOSAMENTE!")
                print("\n📋 CREDENCIALES INICIALES:")
                print("   SUPERADMIN:")
                print("   - Username: superadmin")
                print("   - Email: admin@colca.gob.pe")
                print("   - Password: SGD2025!Colca#Admin")
                print("\n⚠️  IMPORTANTE:")
                print("   1. Cambiar contraseña del SUPERADMIN en el primer login")
                print("   2. Configurar usuarios específicos para cada puesto")
                print("   3. Revisar la estructura organizacional según necesidades")
                
                if args.environment == "dev":
                    print("\n🧪 DATOS DE PRUEBA DISPONIBLES:")
                    print("   - alcalde / Alcalde2025!")
                    print("   - gerente.municipal / GM2025!Test")
                    print("   - analista.sistemas / UIT2025!Test")
                
                print(f"\n📄 Log completo disponible en: sgd_initialization.log")
                
            else:
                print("\n❌ ERROR: La inicialización no se completó correctamente.")
                print("Revise el archivo de log para más detalles.")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n\n⏹️  Inicialización interrumpida por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        print("Revise el archivo de log para más detalles.")
        sys.exit(1)

if __name__ == "__main__":
    main()