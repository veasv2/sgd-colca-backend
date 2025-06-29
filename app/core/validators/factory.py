# app/core/validators/factory.py

"""
Factory de validadores genéricos reutilizables

Este módulo contiene las funciones factory que crean validadores parametrizables
para diferentes tipos de datos. Son la infraestructura base del sistema de 
validación y están diseñados para ser reutilizados en cualquier dominio.

Principios:
- Máxima reutilización
- Configuración parametrizable
- Sin dependencias del dominio específico
- Compatibilidad con Pydantic v2
"""

from typing import Annotated, Optional, Union, Callable, Any
from pydantic import BeforeValidator, AfterValidator
from pydantic.types import StringConstraints
import re
from datetime import datetime, date
from decimal import Decimal

# =============================================================================
# FACTORY PARA VALIDADORES DE TEXTO
# =============================================================================

def crear_tipo_texto(
    min_length: int = 1,
    max_length: int = 255,
    requerido: bool = True,
    solo_mayusculas: bool = False,
    solo_minusculas: bool = False,
    sin_espacios: bool = False,
    formato_titulo: bool = False,
    patron_regex: Optional[str] = None,
    caracteres_permitidos: Optional[str] = None,
    caracteres_prohibidos: Optional[str] = None,
    normalizar_espacios: bool = True,
    remover_acentos: bool = False
):
    """
    Factory que crea tipos de texto parametrizables con validaciones avanzadas
    
    Args:
        min_length: Longitud mínima del texto
        max_length: Longitud máxima del texto
        requerido: Si el campo es obligatorio
        solo_mayusculas: Convertir automáticamente a mayúsculas
        solo_minusculas: Convertir automáticamente a minúsculas  
        sin_espacios: No permitir espacios en el texto
        formato_titulo: Convertir a formato título
        patron_regex: Patrón regex que debe cumplir
        caracteres_permitidos: String con caracteres permitidos
        caracteres_prohibidos: String con caracteres prohibidos
        normalizar_espacios: Convertir múltiples espacios en uno solo
        remover_acentos: Remover acentos del texto
        
    Returns:
        Annotated[str, ...]: Tipo anotado con validaciones
    """
    
    def validador_personalizado(valor: str) -> str:
        """Validador interno que aplica todas las reglas"""
        
        # Validar si es requerido
        if requerido and (not valor or not valor.strip()):
            raise ValueError("Este campo es requerido")
        
        # Si no es requerido y está vacío, retornar vacío
        if not requerido and not valor:
            return ""
        
        # Limpiar espacios al inicio y final
        valor_limpio = valor.strip()
        
        # Normalizar espacios múltiples
        if normalizar_espacios:
            valor_limpio = ' '.join(valor_limpio.split())
        
        # Remover acentos si se solicita
        if remover_acentos:
            import unicodedata
            valor_limpio = unicodedata.normalize('NFD', valor_limpio)
            valor_limpio = ''.join(char for char in valor_limpio 
                                 if unicodedata.category(char) != 'Mn')
        
        # Validar espacios
        if sin_espacios and ' ' in valor_limpio:
            raise ValueError("No se permiten espacios en este campo")
        
        # Validar caracteres prohibidos
        if caracteres_prohibidos:
            chars_encontrados = set(valor_limpio) & set(caracteres_prohibidos)
            if chars_encontrados:
                raise ValueError(
                    f"Caracteres no permitidos encontrados: {', '.join(sorted(chars_encontrados))}"
                )
        
        # Validar caracteres permitidos
        if caracteres_permitidos:
            chars_validos = set(caracteres_permitidos)
            chars_invalidos = set(valor_limpio) - chars_validos
            if chars_invalidos:
                raise ValueError(
                    f"Caracteres no permitidos: {', '.join(sorted(chars_invalidos))}. "
                    f"Solo se permiten: {caracteres_permitidos}"
                )
        
        # Validar patrón regex
        if patron_regex and not re.match(patron_regex, valor_limpio, re.IGNORECASE):
            raise ValueError(f"El formato no es válido. Debe cumplir el patrón: {patron_regex}")
        
        # Aplicar transformaciones
        if solo_mayusculas and solo_minusculas:
            raise ValueError("No se pueden aplicar mayúsculas y minúsculas simultáneamente")
        
        if solo_mayusculas:
            valor_limpio = valor_limpio.upper()
        elif solo_minusculas:
            valor_limpio = valor_limpio.lower()
        
        if formato_titulo:
            valor_limpio = valor_limpio.title()
        
        return valor_limpio
    
    # Combinar StringConstraints de Pydantic con validador personalizado
    return Annotated[
        str,
        StringConstraints(min_length=min_length, max_length=max_length),
        BeforeValidator(validador_personalizado)
    ]

# =============================================================================
# FACTORY PARA VALIDADORES NUMÉRICOS
# =============================================================================

def crear_tipo_numero(
    tipo_base: type = int,
    min_valor: Optional[Union[int, float, Decimal]] = None,
    max_valor: Optional[Union[int, float, Decimal]] = None,
    permitir_cero: bool = True,
    permitir_negativos: bool = True,
    decimales_max: Optional[int] = None
):
    """
    Factory que crea tipos numéricos con validaciones
    
    Args:
        tipo_base: Tipo base (int, float, Decimal)
        min_valor: Valor mínimo permitido
        max_valor: Valor máximo permitido
        permitir_cero: Si permite el valor cero
        permitir_negativos: Si permite valores negativos
        decimales_max: Máximo número de decimales (para float/Decimal)
        
    Returns:
        Annotated[tipo_base, ...]: Tipo anotado con validaciones
    """
    
    def validador_numerico(valor: Union[int, float, str, Decimal]) -> Union[int, float, Decimal]:
        """Validador numérico"""
        
        # Convertir al tipo base
        try:
            if tipo_base == Decimal:
                valor_convertido = Decimal(str(valor))
            else:
                valor_convertido = tipo_base(valor)
        except (ValueError, TypeError) as e:
            raise ValueError(f"No se pudo convertir '{valor}' a {tipo_base.__name__}: {e}")
        
        # Validar cero
        if not permitir_cero and valor_convertido == 0:
            raise ValueError("El valor cero no está permitido")
        
        # Validar negativos
        if not permitir_negativos and valor_convertido < 0:
            raise ValueError("Los valores negativos no están permitidos")
        
        # Validar rango
        if min_valor is not None and valor_convertido < min_valor:
            raise ValueError(f"El valor debe ser mayor o igual a {min_valor}")
        
        if max_valor is not None and valor_convertido > max_valor:
            raise ValueError(f"El valor debe ser menor o igual a {max_valor}")
        
        # Validar decimales para float y Decimal
        if decimales_max is not None and tipo_base in (float, Decimal):
            if isinstance(valor_convertido, Decimal):
                _, digits, exp = valor_convertido.as_tuple()
                num_decimales = max(0, -exp) if exp < 0 else 0
            else:  # float
                num_decimales = len(str(valor_convertido).split('.')[-1]) if '.' in str(valor_convertido) else 0
            
            if num_decimales > decimales_max:
                raise ValueError(f"Máximo {decimales_max} decimales permitidos")
        
        return valor_convertido
    
    return Annotated[tipo_base, BeforeValidator(validador_numerico)]

# =============================================================================
# FACTORY PARA VALIDADORES DE FECHA
# =============================================================================

def crear_tipo_fecha(
    tipo_base: type = date,
    fecha_minima: Optional[Union[date, datetime, str]] = None,
    fecha_maxima: Optional[Union[date, datetime, str]] = None,
    permitir_futuro: bool = True,
    permitir_pasado: bool = True,
    formatos_permitidos: Optional[list] = None
):
    """
    Factory que crea tipos de fecha con validaciones
    
    Args:
        tipo_base: Tipo base (date, datetime)
        fecha_minima: Fecha mínima permitida
        fecha_maxima: Fecha máxima permitida
        permitir_futuro: Si permite fechas futuras
        permitir_pasado: Si permite fechas pasadas
        formatos_permitidos: Lista de formatos de fecha permitidos
        
    Returns:
        Annotated[tipo_base, ...]: Tipo anotado con validaciones
    """
    
    def validador_fecha(valor: Union[date, datetime, str]) -> Union[date, datetime]:
        """Validador de fechas"""
        
        # Convertir string a fecha si es necesario
        if isinstance(valor, str):
            if formatos_permitidos:
                fecha_convertida = None
                for formato in formatos_permitidos:
                    try:
                        fecha_convertida = datetime.strptime(valor, formato)
                        if tipo_base == date:
                            fecha_convertida = fecha_convertida.date()
                        break
                    except ValueError:
                        continue
                
                if fecha_convertida is None:
                    raise ValueError(f"Formato de fecha inválido. Formatos permitidos: {formatos_permitidos}")
                
                valor = fecha_convertida
            else:
                try:
                    fecha_convertida = datetime.fromisoformat(valor.replace('Z', '+00:00'))
                    if tipo_base == date:
                        fecha_convertida = fecha_convertida.date()
                    valor = fecha_convertida
                except ValueError:
                    raise ValueError("Formato de fecha inválido")
        
        # Convertir datetime a date si es necesario
        if tipo_base == date and isinstance(valor, datetime):
            valor = valor.date()
        
        # Obtener fecha actual para comparaciones
        hoy = datetime.now().date() if tipo_base == date else datetime.now()
        
        # Validar futuro/pasado
        if not permitir_futuro and valor > hoy:
            raise ValueError("No se permiten fechas futuras")
        
        if not permitir_pasado and valor < hoy:
            raise ValueError("No se permiten fechas pasadas")
        
        # Validar rango de fechas
        if fecha_minima:
            if isinstance(fecha_minima, str):
                fecha_minima = datetime.fromisoformat(fecha_minima.replace('Z', '+00:00'))
                if tipo_base == date:
                    fecha_minima = fecha_minima.date()
            
            if valor < fecha_minima:
                raise ValueError(f"La fecha debe ser posterior a {fecha_minima}")
        
        if fecha_maxima:
            if isinstance(fecha_maxima, str):
                fecha_maxima = datetime.fromisoformat(fecha_maxima.replace('Z', '+00:00'))
                if tipo_base == date:
                    fecha_maxima = fecha_maxima.date()
            
            if valor > fecha_maxima:
                raise ValueError(f"La fecha debe ser anterior a {fecha_maxima}")
        
        return valor
    
    return Annotated[tipo_base, BeforeValidator(validador_fecha)]

# =============================================================================
# FACTORIES PARA VALIDADORES ESPECIALIZADOS
# =============================================================================

def crear_validador_email_institucional(dominio_permitido: str = "munihuancayo.gob.pe"):
    """
    Crea un validador para emails institucionales
    
    Args:
        dominio_permitido: Dominio que debe tener el email
        
    Returns:
        Función validadora para usar con BeforeValidator
    """
    def validar_email_institucional(email: str) -> str:
        email_limpio = email.strip().lower()
        
        # Validación básica de formato email
        patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron_email, email_limpio):
            raise ValueError("Formato de email inválido")
        
        # Validar dominio específico
        if not email_limpio.endswith(f"@{dominio_permitido}"):
            raise ValueError(f"El email debe pertenecer al dominio @{dominio_permitido}")
            
        return email_limpio
    
    return validar_email_institucional

def crear_validador_dni():
    """
    Crea un validador para números de DNI peruanos
    
    Returns:
        Función validadora para DNI
    """
    def validar_dni(dni: Union[str, int]) -> str:
        # Convertir a string y limpiar
        dni_str = str(dni).strip()
        dni_limpio = ''.join(filter(str.isdigit, dni_str))
        
        # Validar longitud
        if len(dni_limpio) != 8:
            raise ValueError("El DNI debe tener exactamente 8 dígitos")
        
        # Validar que no sean todos iguales
        if len(set(dni_limpio)) == 1:
            raise ValueError("El DNI no puede tener todos los dígitos iguales")
        
        # Validar que no empiece con 0
        if dni_limpio.startswith('0'):
            raise ValueError("El DNI no puede empezar con 0")
        
        # Validar rangos válidos para DNI peruano
        dni_numero = int(dni_limpio)
        if dni_numero < 1000000 or dni_numero > 99999999:
            raise ValueError("DNI fuera del rango válido")
            
        return dni_limpio
    
    return validar_dni

def crear_validador_codigo_correlativo(
    prefijo: str,
    longitud_numero: int = 4,
    separador: str = "-",
    incluir_anio: bool = False
):
    """
    Crea un validador para códigos correlativos con formato específico
    
    Args:
        prefijo: Prefijo del código (ej: "DOC", "EXP")
        longitud_numero: Longitud del número correlativo
        separador: Separador entre partes
        incluir_anio: Si incluye el año en el código
        
    Returns:
        Función validadora para códigos correlativos
    """
    def validar_codigo_correlativo(codigo: str) -> str:
        codigo_limpio = codigo.strip().upper()
        
        # Construir patrón esperado
        if incluir_anio:
            patron = f"^{prefijo.upper()}{separador}\\d{{{longitud_numero}}}{separador}\\d{{4}}$"
            formato_esperado = f"{prefijo.upper()}{separador}{'0' * longitud_numero}{separador}AAAA"
        else:
            patron = f"^{prefijo.upper()}{separador}\\d{{{longitud_numero}}}$"
            formato_esperado = f"{prefijo.upper()}{separador}{'0' * longitud_numero}"
        
        if not re.match(patron, codigo_limpio):
            raise ValueError(f"Formato inválido. Esperado: {formato_esperado}")
        
        return codigo_limpio
    
    return validar_codigo_correlativo