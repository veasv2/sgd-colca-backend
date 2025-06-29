# app/data/test_data.py
"""
Datos de prueba para desarrollo y testing
Estos datos NO deben usarse en producción
"""

# === USUARIOS DE PRUEBA ===

USUARIOS_TEST = [
    {
        "username": "alcalde.test",
        "email": "alcalde@test.colca.gob.pe",
        "password": "test123",
        "nombres": "Juan Carlos",
        "apellidos": "Pérez Mendoza", 
        "dni": "12345678",
        "telefono": "987654321",
        "tipo_usuario": "ALCALDE",
        "estado": "ACTIVO",
        "puesto_codigo": "ALC-001"
    },
    {
        "username": "gerente.test",
        "email": "gerente@test.colca.gob.pe", 
        "password": "test123",
        "nombres": "María Elena",
        "apellidos": "García Flores",
        "dni": "23456789",
        "telefono": "987654322",
        "tipo_usuario": "FUNCIONARIO",
        "estado": "ACTIVO", 
        "puesto_codigo": "GM-001"
    },
    {
        "username": "secretario.test",
        "email": "secretario@test.colca.gob.pe",
        "password": "test123", 
        "nombres": "Carlos Alberto",
        "apellidos": "Rodríguez Vega",
        "dni": "34567890",
        "telefono": "987654323",
        "tipo_usuario": "FUNCIONARIO",
        "estado": "ACTIVO",
        "puesto_codigo": "SG-001"
    },
    {
        "username": "admin.desarrollo",
        "email": "admin.dev@test.colca.gob.pe",
        "password": "dev123",
        "nombres": "Desarrollador",
        "apellidos": "Sistema Test",
        "dni": "99999999", 
        "telefono": "999999998",
        "tipo_usuario": "FUNCIONARIO",
        "estado": "ACTIVO",
        "puesto_codigo": "OA-001"
    }
]

# === UNIDADES ORGÁNICAS ADICIONALES PARA TESTING ===

UNIDADES_TEST = [
    {
        "nombre": "Sub Gerencia de Tecnologías",
        "sigla": "SGT",
        "tipo": "SUB_GERENCIA",
        "descripcion": "Área de sistemas y tecnología",
        "nivel": 4,
        "unidad_padre_sigla": "OA"
    },
    {
        "nombre": "Área de Mesa de Partes",
        "sigla": "AMP", 
        "tipo": "AREA",
        "descripcion": "Recepción y distribución de documentos",
        "nivel": 4,
        "unidad_padre_sigla": "SG"
    },
    {
        "nombre": "Área de Archivo Central",
        "sigla": "AAC",
        "tipo": "AREA", 
        "descripcion": "Gestión del archivo documental",
        "nivel": 4,
        "unidad_padre_sigla": "SG"
    }
]

# === PUESTOS ADICIONALES PARA TESTING ===

PUESTOS_TEST = [
    {
        "nombre": "Responsable de Sistemas",
        "codigo": "SGT-001",
        "descripcion": "Encargado de tecnologías de información",
        "unidad_organica_sigla": "SGT",
        "puesto_superior_codigo": "OA-001",
        "nivel_jerarquico": 4
    },
    {
        "nombre": "Encargado de Mesa de Partes", 
        "codigo": "AMP-001",
        "descripcion": "Responsable de mesa de partes",
        "unidad_organica_sigla": "AMP",
        "puesto_superior_codigo": "SG-001",
        "nivel_jerarquico": 4
    },
    {
        "nombre": "Archivero",
        "codigo": "AAC-001",
        "descripcion": "Encargado del archivo central",
        "unidad_organica_sigla": "AAC", 
        "puesto_superior_codigo": "SG-001",
        "nivel_jerarquico": 4
    },
    {
        "nombre": "Asistente Administrativo",
        "codigo": "OA-002",
        "descripcion": "Apoyo en gestión administrativa", 
        "unidad_organica_sigla": "OA",
        "puesto_superior_codigo": "OA-001",
        "nivel_jerarquico": 4
    }
]

# === CONFIGURACIÓN DE DESARROLLO ===

CONFIG_DESARROLLO = {
    "debug_mode": True,
    "test_emails": True,
    "fake_authentication": False,
    "mock_external_services": True,
    "log_level": "DEBUG",
    "seed_sample_documents": True,
    "auto_approve_test_users": True
}

# === ESCENARIOS DE TESTING ===

ESCENARIOS_TEST = {
    "usuarios_basicos": {
        "descripcion": "Usuarios mínimos para testing básico",
        "usuarios": ["admin", "alcalde.test", "secretario.test"]
    },
    "organizacion_completa": {
        "descripcion": "Estructura organizacional completa",
        "incluir_unidades_test": True,
        "incluir_puestos_test": True
    },
    "permisos_completos": {
        "descripcion": "Todos los permisos asignados para testing",
        "asignar_todos_permisos": True
    }
}