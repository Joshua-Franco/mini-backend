from flask import Flask
from flask_cors import CORS

from .configuration.config import Config
from .extensions.extension import db, jwt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    @jwt.unauthorized_loader
    def sin_token(reason):
        return {"error": "Token requerido"}, 401

    @jwt.invalid_token_loader
    def token_invalido(reason):
        return {"error": "Token inválido"}, 401

    @jwt.expired_token_loader
    def token_expirado(header, payload):
        return {"error": "Token expirado"}, 401

    with app.app_context():
        from .models import productos, cuentas   # registra los modelos
        db.create_all()

    from .routes import register_routes
    register_routes(app)

    return app