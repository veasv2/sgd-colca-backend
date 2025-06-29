# test_alembic_config.py
from app.core.config import settings
print(f"DATABASE_URL: '{settings.DATABASE_URL}'")
print(f"Length: {len(settings.DATABASE_URL)}")
print(f"Is empty: {settings.DATABASE_URL == ''}")