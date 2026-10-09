import os

from dotenv import load_dotenv

load_dotenv()


def normalize_database_url(database_url: str) -> str:
    """Adapta las URLs PostgreSQL de Neon al controlador Psycopg 3."""
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


class Config:
    """Lee la configuración del entorno y aplica valores locales predeterminados."""

    # No usa una base local alternativa: DATABASE_URL debe apuntar a PostgreSQL.
    SQLALCHEMY_DATABASE_URI = normalize_database_url(os.getenv("DATABASE_URL", ""))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() in {"true", "1"}
    # CORS acepta orígenes separados por coma y descarta entradas vacías.
    FRONTEND_ORIGINS = [
        origin.strip().rstrip("/")
        for origin in os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:5475,http://127.0.0.1:5475",
        ).split(",")
        if origin.strip().rstrip("/")
    ]
