from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://mongo:27017/ai_matching"
    APP_NAME: str = "AI Matching Job API"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()