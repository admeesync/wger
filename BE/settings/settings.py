from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = 'sqlite:///./wger.db'
    secret_key: str = 'change-this-secret-in-production'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 1440
    upload_dir: str = 'uploads'
    allowed_origins: str = '*'  # comma-separated list of FE origins allowed to call this API
    supabase_url: str = ''
    supabase_service_key: str = ''
    supabase_storage_bucket: str = 'member-photos'

    @field_validator('database_url', mode='before')
    @classmethod
    def strip_database_url(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    class Config:
        env_file = '.env'


settings = Settings()

