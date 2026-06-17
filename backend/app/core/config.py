from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Explainable Violence Detection Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "production-grade-super-secret-key-violence-incitation-platform"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week
    
    # Database Settings
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "violence_detection"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        
    # AI Service URL
    AI_SERVICE_URL: str = "http://localhost:8001"
    
    # Redis configuration for cache & Celery queue
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Sentry DSN for error tracking
    SENTRY_DSN: Optional[str] = None
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
