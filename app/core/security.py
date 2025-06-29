# app/core/security.py

from passlib.context import CryptContext
from typing import Optional
import secrets
import string

# Configuración del contexto de passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Crear hash de una contraseña
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar si la contraseña coincide con el hash
    """
    return pwd_context.verify(plain_password, hashed_password)

def generate_random_password(length: int = 12) -> str:
    """
    Generar una contraseña aleatoria segura
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def is_password_strong(password: str) -> tuple[bool, list[str]]:
    """
    Validar si una contraseña cumple con los criterios de seguridad
    
    Returns:
        tuple: (es_valida, lista_de_errores)
    """
    errors = []
    
    # Longitud mínima
    if len(password) < 8:
        errors.append("La contraseña debe tener al menos 8 caracteres")
    
    # Al menos una mayúscula
    if not any(c.isupper() for c in password):
        errors.append("La contraseña debe contener al menos una letra mayúscula")
    
    # Al menos una minúscula
    if not any(c.islower() for c in password):
        errors.append("La contraseña debe contener al menos una letra minúscula")
    
    # Al menos un número
    if not any(c.isdigit() for c in password):
        errors.append("La contraseña debe contener al menos un número")
    
    # Al menos un carácter especial
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("La contraseña debe contener al menos un carácter especial")
    
    return len(errors) == 0, errors