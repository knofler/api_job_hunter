from typing import List, Optional

from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://mongo:27017/jobhunter-app"
    MONGO_DB_NAME: str = "jobhunter-app"
    APP_NAME: str = "AI Matching Job API"
    DEBUG: bool = True
    RUN_STARTUP_SEED: bool = True
    CORS_ALLOW_ORIGINS: str = "*"
    CORS_ALLOW_CREDENTIALS: bool = False
    # Auth0 / OIDC
    AUTH0_DOMAIN: Optional[str] = None
    AUTH0_AUDIENCE: Optional[str] = None
    AUTH0_ISSUER: Optional[str] = None
    AUTH0_ALGORITHMS: str = "RS256"

    LLM_DEFAULT_PROVIDER: str = "openai"
    LLM_SETTINGS_SECRET_KEY: Optional[str] = None
    ADMIN_API_KEY: Optional[str] = None
    # When true, ignore env var provider keys and require admin- or user-provided keys
    DISABLE_ENV_LLM_KEYS: bool = False

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"

    GOOGLE_GEMINI_API_KEY: Optional[str] = None
    GOOGLE_GEMINI_MODEL: str = "gemini-1.5-flash"

    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_SESSION_TOKEN: Optional[str] = None
    AWS_REGION: Optional[str] = None
    BEDROCK_MODEL: str = "anthropic.claude-3-haiku-20240307-v1:0"

    class Config:
        env_file = ".env"

    @property
    def cors_origins(self) -> List[str]:
        if self.CORS_ALLOW_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ALLOW_ORIGINS.split(",") if origin.strip()]

settings = Settings()