from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import URL
from .config import Settings

settings = Settings()

# def _make_url() -> str:
#     # postgresql+psycopg://user:password@host:port/dbname
#     return(
#         f"postgresql+psycopg://{settings.DB_USER}:{settings.DB_PASSWORD}"
#         f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
#     )


def _get_db_password() -> str:
    if settings.VAULT_ADDR and settings.VAULT_TOKEN:
        try:
            client = hvac.Client(url=settings.VAULT_ADDR, token=settings.VAULT_TOKEN)
            secret = client.secrets.kv.v2.read_secret_version(path=settings.VAULT_DB_SECRET_PATH)
            pwd = secret["data"]["data"]["POSTGRES_PASSWORD"]
            logger.info("DB password fetched from Vault.")
            return pwd
        except Exception as e:
            logger.warning(f"Vault fetch failed; falling back to env DB_PASSWORD. Reason: {e}")
    return settings.DB_PASSWORD

def _make_url() -> URL:
    return URL.create(
        drivername="postgresql+psycopg",
        username=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,    # int is fine; Pydantic will coerce
        database=settings.DB_NAME,
    )

class Base(DeclarativeBase):
    pass

engine = create_engine(_make_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)