from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from src.config import Config
from src.extensions import db
from src.resources.products import ProductListResource, ProductResource


def create_app() -> Flask:
    """Configura Flask, la base de datos, CORS y las rutas de la API."""
    app = Flask(__name__, static_folder="static")
    app.config.from_object(Config)

    # Conecta extensiones sin acoplarlas a una instancia global de Flask.
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGINS"]}})

    # Registra las rutas para listar y consultar productos.
    api = Api(app)
    api.add_resource(ProductListResource, "/api/products")
    api.add_resource(ProductResource, "/api/products/<string:product_id>")

    return app
