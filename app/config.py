from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Stack Task API"
    ENV: str = "dev"
    LOG_LEVEL: str = "INFO"


    # (Used later for DB/Vault/LLM; harmless for now)
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "appdb"
    DB_USER: str = "appuser"
    DB_PASSWORD: str = "changeme"

    VAULT_ADDR: str | None = None
    VAULT_TOKEN: str | None = None
    VAULT_DB_SECRET_PATH: str = "db-creds"

    # app/config.py (add into class Settings)
    # LLM settings
    OPENAI_API_KEY: str | None = None
    OAI_MODEL: str = "gpt-4o-mini"    # safe, fast, cheap default
    OAI_TIMEOUT_SECONDS: int = 30

    VAULT_OPENAI_SECRET_PATH: str = "openai"

    class Config:
        env_file = ".env"
        extra = "ignore"