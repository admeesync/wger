from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = 'sqlite:///./wger.db'
    secret_key: str = 'change-this-secret-in-production'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 1440
    upload_dir: str = 'uploads'
    allowed_origins: str = '*'  # comma-separated list of FE origins allowed to call this API

    # Supabase Storage settings
    supabase_url: str | None = None
    supabase_key: str | None = None
    supabase_bucket_name: str | None = None

    class Config:

        env_file = '.env'


settings = Settings()
