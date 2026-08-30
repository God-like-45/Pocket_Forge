from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "pocketforge"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:15432/pocketforge"
    
    CELERY_BROKER_URL: str = "redis://localhost:16379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:16379/0"
    
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()
