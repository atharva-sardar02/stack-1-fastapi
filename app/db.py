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