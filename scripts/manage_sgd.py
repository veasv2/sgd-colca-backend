# scripts/manage_sgd.py
"""
Script de Mantenimiento del Sistema de Gobernanza Digital (SGD)
Municipalidad Distrital de Colca

Utilidades para administración y mantenimiento del sistema:
- Crear usuarios específicos
- Backup y restauración
- Validación de integridad
- Estadísticas del sistema
- Reseteo de contraseñas

Uso:
    python scripts/manage_sgd.py <comando> [opciones]
"""

import sys
import os
import argparse
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from getpass import getpass

# Agregar el directorio padre al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

# Importaciones locales
from app.core.database import SessionLocal
from app.models.auth_models import Usuario, Area, Puesto
from app.core.security import create_password_hash, validate_password_strength
from app.schemas.auth_schemas import TipoUsuarioEnum, EstadoUsuarioEnum
from app.services.auth_service import AuthService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SGDManager:
    """
    Clase principal para mantenimiento del Sistema de Gobernanza Digital
    """
    
    def __init__(self):
        self.db: Session = SessionLocal()
        self.auth_service = AuthService(self.db)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    # === GESTIÓN DE USUARIOS ===
    
    def create_user_interactive(self) -> bool:
        """Crea un usuario de forma interactiva"""
        print("\n=== CREAR NUEVO USUARIO ===")
        
        try:
            # Recopilar datos básicos
            username = input("Username: ").strip().lower()
            if not username:
                print("❌ Username requerido")
                return False
            
            # Verificar que no exista
            if self.db.query(Usuario).filter(Usuario.username == username).first():
                print(f"❌ El username '{username}' ya existe")
                return False
            
            email = input("Email: ").strip().lower()
            if not email or "@" not in email:
                print("❌ Email válido requerido")
                return False
            
            # Verificar que no exista
            if self.db.query(Usuario).filter(Usuario.email == email).first():
                print(f"❌ El email '{email}' ya está registrado")
                return False
            
            nombres = input("Nombres: ").strip()
            apellidos = input("Apellidos: ").strip()
            dni = input("DNI (opcional): ").strip()
            telefono = input("Teléfono (opcional): ").strip()
            
            # Seleccionar tipo de usuario
            print("\nTipos de usuario disponibles:")
            print("1. FUNCIONARIO")
            print("2. ALCALDE")
            print("3. SUPERADMIN")
            
            tipo_choice = input("Seleccione tipo (1-3): ").strip()
            tipo_map = {
                "1": TipoUsuarioEnum.FUNCIONARIO,
                "2": TipoUsuarioEnum.ALCALDE,
                "3": TipoUsuarioEnum.SUPERADMIN
            }
            
            if tipo_choice not in tipo_map:
                print("❌ Tipo de usuario inválido")
                return False
            
            tipo_usuario = tipo_map[tipo_choice]
            
            # Seleccionar puesto si es funcionario o alcalde
            puesto_id = None
            if tipo_usuario in [TipoUsuarioEnum.FUNCIONARIO, TipoUsuarioEnum.ALCALDE]:
                puestos_disponibles = self.get_available_positions()
                if puestos_disponibles:
                    print("\nPuestos disponibles:")
                    for i, puesto in enumerate(puestos_disponibles, 1):
                        print(f"{i}. {puesto['codigo']} - {puesto['nombre']} ({puesto['area_nombre']})")
                    
                    puesto_choice = input(f"Seleccione puesto (1-{len(puestos_disponibles)}) o ENTER para omitir: ").strip()
                    
                    if puesto_choice and puesto_choice.isdigit():
                        puesto_idx = int(puesto_choice) - 1
                        if 0 <= puesto_idx < len(puestos_disponibles):
                            puesto_id = puestos_disponibles[puesto_idx]['id']
            
            # Solicitar contraseña
            while True:
                password = getpass("Contraseña: ")
                password_confirm = getpass("Confirmar contraseña: ")
                
                if password != password_confirm:
                    print("❌ Las contraseñas no coinciden")
                    continue
                
                validation = validate_password_strength(password)
                if not validation["valid"]:
                    print(f"❌ Contraseña insegura: {', '.join(validation['errors'])}")
                    continue
                
                break
            
            # Crear usuario
            nuevo_usuario = Usuario(
                username=username,
                email=email,
                password_hash=create_password_hash(password),
                nombres=nombres,
                apellidos=apellidos,
                dni=dni if dni else None,
                telefono=telefono if telefono else None,
                tipo_usuario=tipo_usuario,
                estado=EstadoUsuarioEnum.ACTIVO,
                puesto_id=puesto_id
            )
            
            self.db.add(nuevo_usuario)
            self.db.commit()
            
            print(f"\n✅ Usuario creado exitosamente:")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Tipo: {tipo_usuario}")
            if puesto_id:
                puesto = self.db.query(Puesto).filter(Puesto.id == puesto_id).first()
                print(f"   Puesto: {puesto.codigo} - {puesto.nombre}")
            
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error al crear usuario: {e}")
            return False
    
    def reset_user_password(self, username: str) -> bool:
        """Resetea la contraseña de un usuario"""
        try:
            user = self.db.query(Usuario).filter(Usuario.username == username).first()
            if not user:
                print(f"❌ Usuario '{username}' no encontrado")
                return False
            
            print(f"\nResetear contraseña para: {user.nombres} {user.apellidos} ({user.username})")
            
            while True:
                new_password = getpass("Nueva contraseña: ")
                confirm_password = getpass("Confirmar contraseña: ")
                
                if new_password != confirm_password:
                    print("❌ Las contraseñas no coinciden")
                    continue
                
                validation = validate_password_strength(new_password)
                if not validation["valid"]:
                    print(f"❌ Contraseña insegura: {', '.join(validation['errors'])}")
                    continue
                
                break
            
            user.password_hash = create_password_hash(new_password)
            self.db.commit()
            
            print(f"✅ Contraseña reseteada exitosamente para {username}")
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error al resetear contraseña: {e}")
            return False
    
    def list_users(self, detailed: bool = False) -> None:
        """Lista todos los usuarios del sistema"""
        try:
            users = self.db.query(Usuario).all()
            
            print(f"\n=== USUARIOS DEL SISTEMA ({len(users)} total) ===")
            
            for user in users:
                puesto_info = ""
                if user.puesto_id:
                    puesto = self.db.query(Puesto).filter(Puesto.id == user.puesto_id).first()
                    if puesto:
                        area = self.db.query(Area).filter(Area.id == puesto.area_id).first()
                        puesto_info = f" | {puesto.codigo} ({area.codigo})" if area else f" | {puesto.codigo}"
                
                status_icon = "✅" if user.estado == EstadoUsuarioEnum.ACTIVO else "❌"
                
                print(f"{status_icon} {user.username} | {user.nombres} {user.apellidos} | {user.tipo_usuario}{puesto_info}")
                
                if detailed:
                    print(f"    Email: {user.email}")
                    print(f"    DNI: {user.dni or 'N/A'}")
                    print(f"    Último acceso: {user.ultimo_acceso or 'Nunca'}")
                    print(f"    Creado: {user.fecha_creacion}")
                    print()
            
        except Exception as e:
            print(f"❌ Error al listar usuarios: {e}")
    
    def get_available_positions(self) -> List[Dict[str, Any]]:
        """Obtiene puestos disponibles (sin usuario asignado)"""
        try:
            # Subconsulta para obtener puestos ocupados
            occupied_positions = self.db.query(Usuario.puesto_id).filter(
                Usuario.puesto_id.isnot(None),
                Usuario.estado == EstadoUsuarioEnum.ACTIVO
            ).subquery()
            
            # Puestos disponibles
            available_puestos = self.db.query(Puesto, Area).join(Area).filter(
                Puesto.activo == True,
                Area.activa == True,
                ~Puesto.id.in_(occupied_positions)
            ).order_by(Area.codigo, Puesto.codigo).all()
            
            result = []
            for puesto, area in available_puestos:
                result.append({
                    'id': puesto.id,
                    'codigo': puesto.codigo,
                    'nombre': puesto.nombre,
                    'area_codigo': area.codigo,
                    'area_nombre': area.nombre
                })
            
            return result
            
        except Exception as e:
            print(f"❌ Error al obtener puestos disponibles: {e}")
            return []
    
    # === ESTADÍSTICAS Y REPORTES ===
    
    def show_system_stats(self) -> None:
        """Muestra estadísticas del sistema"""
        try:
            print("\n=== ESTADÍSTICAS DEL SISTEMA ===")
            
            # Usuarios
            total_users = self.db.query(Usuario).count()
            active_users = self.db.query(Usuario).filter(Usuario.estado == EstadoUsuarioEnum.ACTIVO).count()
            superadmins = self.db.query(Usuario).filter(Usuario.tipo_usuario == TipoUsuarioEnum.SUPERADMIN).count()
            alcaldes = self.db.query(Usuario).filter(Usuario.tipo_usuario == TipoUsuarioEnum.ALCALDE).count()
            funcionarios = self.db.query(Usuario).filter(Usuario.tipo_usuario == TipoUsuarioEnum.FUNCIONARIO).count()
            
            print(f"\n👥 USUARIOS:")
            print(f"   Total: {total_users}")
            print(f"   Activos: {active_users}")
            print(f"   SUPERADMIN: {superadmins}")
            print(f"   ALCALDE: {alcaldes}")
            print(f"   FUNCIONARIO: {funcionarios}")
            
            # Estructura organizacional
            total_areas = self.db.query(Area).count()
            active_areas = self.db.query(Area).filter(Area.activa == True).count()
            total_puestos = self.db.query(Puesto).count()
            active_puestos = self.db.query(Puesto).filter(Puesto.activo == True).count()
            
            print(f"\n🏢 ESTRUCTURA ORGANIZACIONAL:")
            print(f"   Áreas totales: {total_areas}")
            print(f"   Áreas activas: {active_areas}")
            print(f"   Puestos totales: {total_puestos}")
            print(f"   Puestos activos: {active_puestos}")
            
            # Asignaciones
            users_with_position = self.db.query(Usuario).filter(
                Usuario.puesto_id.isnot(None),
                Usuario.estado == EstadoUsuarioEnum.ACTIVO
            ).count()
            vacant_positions = active_puestos - users_with_position
            
            print(f"\n📊 ASIGNACIONES:")
            print(f"   Usuarios con puesto: {users_with_position}")
            print(f"   Puestos vacantes: {vacant_positions}")
            if active_puestos > 0:
                ocupacion = (users_with_position / active_puestos) * 100
                print(f"   Ocupación: {ocupacion:.1f}%")
            
            # Últimos accesos
            recent_logins = self.db.query(Usuario).filter(
                Usuario.ultimo_acceso.isnot(None),
                Usuario.ultimo_acceso >= func.date_sub(func.now(), func.interval(7, 'day'))
            ).count()
            
            print(f"\n🔐 ACTIVIDAD:")
            print(f"   Usuarios activos última semana: {recent_logins}")
            
            # Distribución por área
            area_distribution = self.db.query(
                Area.codigo,
                Area.nombre,
                func.count(Usuario.id).label('usuarios')
            ).outerjoin(Puesto, Area.id == Puesto.area_id).outerjoin(
                Usuario, and_(Puesto.id == Usuario.puesto_id, Usuario.estado == EstadoUsuarioEnum.ACTIVO)
            ).filter(Area.activa == True).group_by(Area.id).order_by(Area.codigo).all()
            
            print(f"\n📈 DISTRIBUCIÓN POR ÁREA:")
            for area in area_distribution:
                print(f"   {area.codigo}: {area.usuarios} usuarios")
            
        except Exception as e:
            print(f"❌ Error al obtener estadísticas: {e}")
    
    def validate_system_integrity(self) -> None:
        """Valida la integridad del sistema"""
        print("\n=== VALIDACIÓN DE INTEGRIDAD ===")
        
        errors = []
        warnings = []
        
        try:
            # Verificar usuarios sin SUPERADMIN
            superadmin_count = self.db.query(Usuario).filter(
                Usuario.tipo_usuario == TipoUsuarioEnum.SUPERADMIN,
                Usuario.estado == EstadoUsuarioEnum.ACTIVO
            ).count()
            
            if superadmin_count == 0:
                errors.append("No hay usuarios SUPERADMIN activos")
            elif superadmin_count > 1:
                warnings.append(f"Múltiples SUPERADMIN detectados ({superadmin_count})")
            
            # Verificar usuarios con puestos inexistentes
            users_invalid_position = self.db.query(Usuario).filter(
                Usuario.puesto_id.isnot(None),
                ~Usuario.puesto_id.in_(self.db.query(Puesto.id))
            ).count()
            
            if users_invalid_position > 0:
                errors.append(f"Usuarios con puestos inexistentes: {users_invalid_position}")
            
            # Verificar puestos con áreas inexistentes
            puestos_invalid_area = self.db.query(Puesto).filter(
                ~Puesto.area_id.in_(self.db.query(Area.id))
            ).count()
            
            if puestos_invalid_area > 0:
                errors.append(f"Puestos con áreas inexistentes: {puestos_invalid_area}")
            
            # Verificar áreas huérfanas
            orphan_areas = self.db.query(Area).filter(
                Area.area_padre_id.isnot(None),
                ~Area.area_padre_id.in_(self.db.query(Area.id))
            ).count()
            
            if orphan_areas > 0:
                errors.append(f"Áreas huérfanas (padre inexistente): {orphan_areas}")
            
            # Verificar puestos duplicados
            duplicate_positions = self.db.query(
                Puesto.codigo,
                func.count(Puesto.id).label('total')
            ).group_by(Puesto.codigo).having(func.count(Puesto.id) > 1).count()
            
            if duplicate_positions > 0:
                warnings.append(f"Códigos de puesto duplicados: {duplicate_positions}")
            
            # Verificar usuarios duplicados
            duplicate_usernames = self.db.query(
                Usuario.username,
                func.count(Usuario.id).label('total')
            ).group_by(Usuario.username).having(func.count(Usuario.id) > 1).count()
            
            if duplicate_usernames > 0:
                errors.append(f"Usernames duplicados: {duplicate_usernames}")
            
            duplicate_emails = self.db.query(
                Usuario.email,
                func.count(Usuario.id).label('total')
            ).group_by(Usuario.email).having(func.count(Usuario.id) > 1).count()
            
            if duplicate_emails > 0:
                errors.append(f"Emails duplicados: {duplicate_emails}")
            
            # Mostrar resultados
            if not errors and not warnings:
                print("✅ Sistema íntegro - no se encontraron problemas")
            else:
                if errors:
                    print("❌ ERRORES CRÍTICOS:")
                    for error in errors:
                        print(f"   • {error}")
                
                if warnings:
                    print("⚠️  ADVERTENCIAS:")
                    for warning in warnings:
                        print(f"   • {warning}")
            
        except Exception as e:
            print(f"❌ Error durante validación: {e}")
    
    # === BACKUP Y EXPORTACIÓN ===
    
    def export_organizational_structure(self, filename: str = None) -> bool:
        """Exporta la estructura organizacional a JSON"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"sgd_estructura_{timestamp}.json"
            
            # Exportar áreas
            areas = self.db.query(Area).order_by(Area.nivel, Area.codigo).all()
            areas_data = []
            for area in areas:
                areas_data.append({
                    'codigo': area.codigo,
                    'nombre': area.nombre,
                    'descripcion': area.descripcion,
                    'nivel': area.nivel,
                    'activa': area.activa,
                    'area_padre_codigo': None  # Se resolverá después
                })
                
                # Resolver código del área padre
                if area.area_padre_id:
                    area_padre = self.db.query(Area).filter(Area.id == area.area_padre_id).first()
                    if area_padre:
                        areas_data[-1]['area_padre_codigo'] = area_padre.codigo
            
            # Exportar puestos
            puestos = self.db.query(Puesto, Area).join(Area).order_by(Area.codigo, Puesto.codigo).all()
            puestos_data = []
            for puesto, area in puestos:
                puesto_data = {
                    'codigo': puesto.codigo,
                    'nombre': puesto.nombre,
                    'descripcion': puesto.descripcion,
                    'area_codigo': area.codigo,
                    'nivel_jerarquico': puesto.nivel_jerarquico,
                    'activo': puesto.activo,
                    'puesto_superior_codigo': None
                }
                
                # Resolver código del puesto superior
                if puesto.puesto_superior_id:
                    puesto_superior = self.db.query(Puesto).filter(Puesto.id == puesto.puesto_superior_id).first()
                    if puesto_superior:
                        puesto_data['puesto_superior_codigo'] = puesto_superior.codigo
                
                puestos_data.append(puesto_data)
            
            # Crear estructura de exportación
            export_data = {
                'metadata': {
                    'sistema': 'SGD - Sistema de Gobernanza Digital',
                    'municipalidad': 'Municipalidad Distrital de Colca',
                    'fecha_exportacion': datetime.now().isoformat(),
                    'version': '1.0.0'
                },
                'areas': areas_data,
                'puestos': puestos_data
            }
            
            # Guardar archivo
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Estructura organizacional exportada a: {filename}")
            print(f"   Áreas: {len(areas_data)}")
            print(f"   Puestos: {len(puestos_data)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al exportar estructura: {e}")
            return False
    
    def export_users_list(self, filename: str = None, include_sensitive: bool = False) -> bool:
        """Exporta lista de usuarios"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"sgd_usuarios_{timestamp}.json"
            
            users = self.db.query(Usuario).order_by(Usuario.username).all()
            users_data = []
            
            for user in users:
                user_data = {
                    'username': user.username,
                    'email': user.email,
                    'nombres': user.nombres,
                    'apellidos': user.apellidos,
                    'dni': user.dni,
                    'telefono': user.telefono,
                    'tipo_usuario': user.tipo_usuario,
                    'estado': user.estado,
                    'ultimo_acceso': user.ultimo_acceso.isoformat() if user.ultimo_acceso else None,
                    'fecha_creacion': user.fecha_creacion.isoformat(),
                    'puesto_codigo': None,
                    'area_codigo': None
                }
                
                # Agregar información del puesto
                if user.puesto_id:
                    puesto = self.db.query(Puesto).filter(Puesto.id == user.puesto_id).first()
                    if puesto:
                        user_data['puesto_codigo'] = puesto.codigo
                        area = self.db.query(Area).filter(Area.id == puesto.area_id).first()
                        if area:
                            user_data['area_codigo'] = area.codigo
                
                users_data.append(user_data)
            
            export_data = {
                'metadata': {
                    'sistema': 'SGD - Sistema de Gobernanza Digital',
                    'municipalidad': 'Municipalidad Distrital de Colca',
                    'fecha_exportacion': datetime.now().isoformat(),
                    'incluye_datos_sensibles': include_sensitive,
                    'total_usuarios': len(users_data)
                },
                'usuarios': users_data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Lista de usuarios exportada a: {filename}")
            print(f"   Total usuarios: {len(users_data)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al exportar usuarios: {e}")
            return False

def main():
    """Función principal del script de mantenimiento"""
    parser = argparse.ArgumentParser(
        description="Herramientas de mantenimiento para el SGD",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Comandos disponibles:
  create-user          Crear usuario interactivamente
  list-users           Listar todos los usuarios
  reset-password       Resetear contraseña de usuario
  stats               Mostrar estadísticas del sistema
  validate            Validar integridad del sistema
  export-structure    Exportar estructura organizacional
  export-users        Exportar lista de usuarios
  
Ejemplos:
  python manage_sgd.py create-user
  python manage_sgd.py list-users --detailed
  python manage_sgd.py reset-password --username admin
  python manage_sgd.py export-structure --output estructura.json
        """
    )
    
    parser.add_argument('command', help='Comando a ejecutar')
    parser.add_argument('--username', help='Username del usuario (para reset-password)')
    parser.add_argument('--detailed', action='store_true', help='Mostrar información detallada')
    parser.add_argument('--output', help='Archivo de salida para exportaciones')
    parser.add_argument('--include-sensitive', action='store_true', help='Incluir datos sensibles en exportaciones')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("SGD - HERRAMIENTAS DE MANTENIMIENTO")
    print("Municipalidad Distrital de Colca")
    print("=" * 60)
    print()
    
    try:
        with SGDManager() as manager:
            if args.command == 'create-user':
                manager.create_user_interactive()
                
            elif args.command == 'list-users':
                manager.list_users(detailed=args.detailed)
                
            elif args.command == 'reset-password':
                if not args.username:
                    username = input("Username: ").strip()
                else:
                    username = args.username
                manager.reset_user_password(username)
                
            elif args.command == 'stats':
                manager.show_system_stats()
                
            elif args.command == 'validate':
                manager.validate_system_integrity()
                
            elif args.command == 'export-structure':
                manager.export_organizational_structure(args.output)
                
            elif args.command == 'export-users':
                manager.export_users_list(args.output, args.include_sensitive)
                
            else:
                print(f"❌ Comando desconocido: {args.command}")
                parser.print_help()
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n⏹️  Operación interrumpida por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()