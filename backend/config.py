"""
Configuration Settings für JARVIS System
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application Settings"""
    
    # Server
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", 5000))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/jarvis_database.db")
    
    # API
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", 30))
    
    # AI
    AI_UPDATE_INTERVAL: int = 2  # Sekunden
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

print(f"⚙️  Settings loaded:")
print(f"   Host: {settings.SERVER_HOST}")
print(f"   Port: {settings.SERVER_PORT}")
print(f"   Database: {settings.DATABASE_PATH}")
print(f"   Debug: {settings.DEBUG}")
