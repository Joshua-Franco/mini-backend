from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Las extensiones se enlazan a la aplicación en create_app().
db = SQLAlchemy()
jwt = JWTManager()
