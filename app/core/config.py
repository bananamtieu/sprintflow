from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    ENV: str = "dev"
    DATABASE_URL: str = "sqlite:///./sprintflow.db"
    JWT_SECRET_KEY: str = "dev-only-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SESSION_SECRET: str = "dev-secret-change-me"

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def jwt_secret_must_be_set(cls, v: str, info):
        env = info.data.get("ENV", "dev")
        if env != "dev" and (not v or v == "dev-only-change-me" or v == "your_secret_key"):
            raise ValueError("JWT_SECRET_KEY must be set in environment for non-dev")
        return v

settings = Settings()