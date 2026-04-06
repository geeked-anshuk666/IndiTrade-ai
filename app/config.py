from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    jwt_secret: str
    allowed_origins: str = "http://localhost:3000"
    jwt_expiry_minutes: int = 60
    rate_limit_analyze: str = "5/minute"
    rate_limit_auth: str = "10/minute"

    class Config:
        env_file = ".env"

settings = Settings()
