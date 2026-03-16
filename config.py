import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "UltraXpert Backend API"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "1e4d3a2b7f9c8d5e6a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./ultraxpert.db"
    
    # SMTP
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: str = "UltraXpert Support"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
