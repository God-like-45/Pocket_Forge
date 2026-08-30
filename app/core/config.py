from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "pocketforge"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:15432/pocketforge"
    
    CELERY_BROKER_URL: str = "redis://localhost:16379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:16379/0"
    
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

    @property
    def async_database_url(self) -> str:
        # Render provides 'postgres://' which is deprecated in SQLAlchemy, and we need asyncpg
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

settings = Settings()
