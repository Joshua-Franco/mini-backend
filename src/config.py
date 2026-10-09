import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Lee la configuración del entorno y aplica valores locales predeterminados."""

    # No usa una base local alternativa: DATABASE_URL debe apuntar a PostgreSQL.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    # CORS acepta los orígenes locales indicados y descarta entradas vacías.
    FRONTEND_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:5475,http://127.0.0.1:5475",
        ).split(",")
        if origin.strip()
    ]
