import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    ORIGIN = os.getenv("FRONTEND_ORIGINS")
    PORT = int(os.getenv("PORT"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG")
    JWT_SECRET_KEY= os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)