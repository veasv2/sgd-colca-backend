# app/data/initial_data.py
"""
Datos iniciales del sistema SGD Colca
Estos datos son críticos para el funcionamiento del sistema
"""

from datetime import datetime

# === DATOS DE SEGURIDAD ===

# Permisos base del sistema
PERMISOS_INICIALES = [
    # Administración del Sistema
    {
        "codigo": "ADMIN_USUARIOS",
        "nombre": "Administrar Usuarios", 
        "descripcion": "Crear, modificar y eliminar usuarios del sistema",
        "modulo": "SEGURIDAD",
        "tipo_permiso": "ADMINISTRACION"
    },
    {
        "codigo": "ADMIN_PERMISOS",
        "nombre": "Administrar Permisos",
        "descripcion": "Asignar y revocar permisos a usuarios y puestos",
        "modulo": "SEGURIDAD", 
        "tipo_permiso": "ADMINISTRACION"
    },
    {
        "codigo": "ADMIN_ORGANIZACION",
        "nombre": "Administrar Organización",
        "descripcion": "Gestionar unidades orgánicas y puestos",
        "modulo": "ORGANIZACION",
        "tipo_permiso": "ADMINISTRACION"
    },
    
    # Gestión Documental
    {
        "codigo": "DOC_CREAR",
        "nombre": "Crear Documentos",
        "descripcion": "Crear nuevos documentos en el sistema",
        "modulo": "DOCUMENTOS",
        "tipo_permiso": "ESCRITURA"
    },
    {
        "codigo": "DOC_LEER",
        "nombre": "Leer Documentos", 
        "descripcion": "Visualizar documentos del sistema",
        "modulo": "DOCUMENTOS",
        "tipo_permiso": "LECTURA"
    },
    {
        "codigo": "DOC_EDITAR",
        "nombre": "Editar Documentos",
        "descripcion": "Modificar documentos existentes",
        "modulo": "DOCUMENTOS", 
        "tipo_permiso": "ESCRITURA"
    },
    {
        "codigo": "DOC_FIRMAR",
        "nombre": "Firmar Documentos",
        "descripcion": "Firmar documentos digitalmente",
        "modulo": "DOCUMENTOS",
        "tipo_permiso": "ESCRITURA"
    },
    
    # Trámites
    {
        "codigo": "TRAMITE_CREAR",
        "nombre": "Crear Trámites",
        "descripcion": "Iniciar nuevos trámites",
        "modulo": "TRAMITES",
        "tipo_permiso": "ESCRITURA"
    },
    {
        "codigo": "TRAMITE_GESTIONAR",
        "nombre": "Gestionar Trámites",
        "descripcion": "Procesar y gestionar trámites",
        "modulo": "TRAMITES",
        "tipo_permiso": "ESCRITURA"
    },
    
    # Reportes
    {
        "codigo": "REPORTES_VER",
        "nombre": "Ver Reportes",
        "descripcion": "Acceder a reportes del sistema",
        "modulo": "REPORTES",
        "tipo_permiso": "LECTURA"
    },
    {
        "codigo": "REPORTES_ADMIN",
        "nombre": "Administrar Reportes",
        "descripcion": "Crear y configurar reportes",
        "modulo": "REPORTES",
        "tipo_permiso": "ADMINISTRACION"
    }
]

# === DATOS ORGANIZACIONALES ===

# Unidad orgánica principal (Municipalidad)
MUNICIPALIDAD_PRINCIPAL = {
    "nombre": "Municipalidad Distrital de Colca",
    "sigla": "MDC",
    "tipo": "MUNICIPALIDAD",
    "descripcion": "Gobierno Local del Distrito de Colca",
    "nivel": 1,
    "activa": True
}

# Unidades orgánicas base
UNIDADES_ORGANICAS_INICIALES = [
    # Órganos de Gobierno
    {
        "nombre": "Alcaldía",
        "sigla": "ALC",
        "tipo": "ORGANO_GOBIERNO", 
        "descripcion": "Órgano ejecutivo de la municipalidad",
        "nivel": 2
    },
    {
        "nombre": "Concejo Municipal",
        "sigla": "CM",
        "tipo": "ORGANO_GOBIERNO",
        "descripcion": "Órgano normativo y fiscalizador",
        "nivel": 2
    },
    
    # Órganos de Alta Dirección
    {
        "nombre": "Gerencia Municipal", 
        "sigla": "GM",
        "tipo": "ORGANO_ALTA_DIRECCION",
        "descripcion": "Órgano de dirección y gestión municipal",
        "nivel": 2
    },
    
    # Órganos de Apoyo
    {
        "nombre": "Secretaría General",
        "sigla": "SG", 
        "tipo": "ORGANO_APOYO",
        "descripcion": "Órgano de apoyo y coordinación",
        "nivel": 3,
        "unidad_padre_sigla": "GM"
    },
    {
        "nombre": "Oficina de Administración",
        "sigla": "OA",
        "tipo": "ORGANO_APOYO", 
        "descripcion": "Gestión administrativa y recursos",
        "nivel": 3,
        "unidad_padre_sigla": "GM"
    },
    
    # Órganos de Línea
    {
        "nombre": "Gerencia de Desarrollo Urbano",
        "sigla": "GDU",
        "tipo": "ORGANO_LINEA",
        "descripcion": "Desarrollo urbano y territorial",
        "nivel": 3,
        "unidad_padre_sigla": "GM"
    },
    {
        "nombre": "Gerencia de Servicios Públicos",
        "sigla": "GSP", 
        "tipo": "ORGANO_LINEA",
        "descripcion": "Gestión de servicios públicos municipales",
        "nivel": 3,
        "unidad_padre_sigla": "GM"
    }
]

# Puestos base del sistema
PUESTOS_INICIALES = [
    {
        "nombre": "Alcalde",
        "codigo": "ALC-001",
        "descripcion": "Máxima autoridad ejecutiva municipal",
        "unidad_organica_sigla": "ALC",
        "nivel_jerarquico": 1
    },
    {
        "nombre": "Gerente Municipal",
        "codigo": "GM-001", 
        "descripcion": "Responsable de la gestión municipal",
        "unidad_organica_sigla": "GM",
        "puesto_superior_codigo": "ALC-001",
        "nivel_jerarquico": 2
    },
    {
        "nombre": "Secretario General",
        "codigo": "SG-001",
        "descripcion": "Responsable de secretaría general",
        "unidad_organica_sigla": "SG", 
        "puesto_superior_codigo": "GM-001",
        "nivel_jerarquico": 3
    },
    {
        "nombre": "Jefe de Administración",
        "codigo": "OA-001",
        "descripcion": "Responsable de administración",
        "unidad_organica_sigla": "OA",
        "puesto_superior_codigo": "GM-001", 
        "nivel_jerarquico": 3
    }
]

# Usuario administrador inicial
USUARIO_ADMIN_INICIAL = {
    "username": "admin",
    "email": "admin@colca.gob.pe",
    "password": "admin123",  # Cambiar en producción
    "nombres": "Administrador",
    "apellidos": "del Sistema",
    "dni": "00000000",
    "telefono": "999999999",
    "tipo_usuario": "SUPERADMIN",
    "estado": "ACTIVO",
    "puesto_codigo": "SG-001"  # Secretario General por defecto
}

# Configuración del sistema
CONFIGURACION_INICIAL = {
    "nombre_sistema": "Sistema de Gestión Documental - Colca",
    "version": "1.0.0",
    "fecha_instalacion": datetime.now(),
    "municipalidad": "Municipalidad Distrital de Colca",
    "departamento": "Junín",
    "provincia": "Huancayo",
    "distrito": "Colca"
}