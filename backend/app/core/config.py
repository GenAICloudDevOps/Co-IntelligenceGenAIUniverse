import os
from typing import Optional

class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://cointelligence_user:secure_password@localhost:5432/cointelligence_db")
    
    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # App Settings
    APP_NAME: str = "Co-Intelligence GenAI Universe"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # CORS Settings
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8501",
        "http://localhost:8502",
        "http://localhost:8503",
    ]
    
    # Add PUBLIC_IP based origins
    PUBLIC_IP = os.getenv("PUBLIC_IP", "localhost")
    if PUBLIC_IP != "localhost":
        ALLOWED_ORIGINS.extend([
            f"http://{PUBLIC_IP}:3000",
            f"http://{PUBLIC_IP}:8000",
            f"http://{PUBLIC_IP}:8501",
            f"http://{PUBLIC_IP}:8502",
            f"http://{PUBLIC_IP}:8503",
        ])

settings = Settings()
