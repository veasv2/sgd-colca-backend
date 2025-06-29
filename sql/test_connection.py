# test_connection.py
from app.core.config import settings
from sqlalchemy import create_engine, text

print(f"DATABASE_URL: {settings.DATABASE_URL}")

try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))  # Usar text() para SQLAlchemy 2.0
        print("✅ Conexión exitosa")
        print(f"Resultado: {result.fetchone()}")
except Exception as e:
    print(f"❌ Error de conexión: {e}")