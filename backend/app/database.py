import os
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

# Database URL from environment - Tortoise ORM requires 'postgres://' scheme
DATABASE_URL = os.getenv("DATABASE_URL", "postgres://cointelligence_user:secure_password@localhost:5432/cointelligence_db")

# Convert postgresql:// to postgres:// if needed (Tortoise ORM requirement)
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgres://", 1)

# Tortoise ORM configuration
TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.models.user", "aerich.models"],
            "default_connection": "default",
        },
    },
}

async def init_db():
    """Initialize Tortoise ORM"""
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    print("✅ Connected to PostgreSQL database with Tortoise ORM")

async def close_db():
    """Close Tortoise ORM connections"""
    await Tortoise.close_connections()
    print("❌ Disconnected from PostgreSQL database")

def register_db(app):
    """Register Tortoise ORM with FastAPI app"""
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True,
    )
