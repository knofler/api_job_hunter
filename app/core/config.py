from typing import List

from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://mongo:27017/jobhunter-app"
    MONGO_DB_NAME: str = "jobhunter-app"
    APP_NAME: str = "AI Matching Job API"
    DEBUG: bool = True
    RUN_STARTUP_SEED: bool = True
    CORS_ALLOW_ORIGINS: str = "*"
    CORS_ALLOW_CREDENTIALS: bool = False

    class Config:
        env_file = ".env"

    @property
    def cors_origins(self) -> List[str]:
        if self.CORS_ALLOW_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ALLOW_ORIGINS.split(",") if origin.strip()]

settings = Settings()