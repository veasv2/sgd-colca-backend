# app/core/security.py
"""
Utilidades de seguridad para SGD Colca
"""

import hashlib
import secrets
import hmac


def generate_password_hash(password: str) -> str:
    """
    Generar hash seguro de contraseña usando PBKDF2
    
    Args:
        password (str): Contraseña en texto plano
        
    Returns:
        str: Hash de la contraseña en formato pbkdf2_sha256$salt$hash
    """
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 100,000 iteraciones
    )
    return f"pbkdf2_sha256${salt}${password_hash.hex()}"


def check_password_hash(password_hash: str, password: str) -> bool:
    """
    Verificar si una contraseña coincide con su hash
    
    Args:
        password_hash (str): Hash almacenado
        password (str): Contraseña a verificar
        
    Returns:
        bool: True si la contraseña es correcta
    """
    try:
        algorithm, salt, stored_hash = password_hash.split('$')
        
        if algorithm != 'pbkdf2_sha256':
            return False
        
        password_hash_check = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        
        return hmac.compare_digest(stored_hash, password_hash_check.hex())
        
    except (ValueError, AttributeError):
        return False


def generate_secure_token(length: int = 32) -> str:
    """
    Generar token seguro para sesiones
    
    Args:
        length (int): Longitud del token en bytes
        
    Returns:
        str: Token hexadecimal
    """
    return secrets.token_hex(length)