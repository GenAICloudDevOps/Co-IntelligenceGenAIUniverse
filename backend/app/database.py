import os
from databases import Database
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cointelligence_user:secure_password@localhost:5432/cointelligence_db")

# Database instance for async operations
database = Database(DATABASE_URL)

# SQLAlchemy setup for models (SQLAlchemy 1.4 compatible)
engine = create_engine(DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
metadata = MetaData()

# Dependency to get database session
def get_database():
    return database

async def connect_database():
    """Connect to the database"""
    await database.connect()
    print("✅ Connected to PostgreSQL database")

async def disconnect_database():
    """Disconnect from the database"""
    await database.disconnect()
    print("❌ Disconnected from PostgreSQL database")
