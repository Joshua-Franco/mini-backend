from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from src.config import Config
from src.extensions import db
from src.resources.products import ProductListResource, ProductResource
from src.seed import seed_products


def init_db(app: Flask) -> None:
    """Crea el esquema y carga el catálogo inicial al arrancar la aplicación."""
    with app.app_context():
        db.create_all()
        seed_products()


def create_app() -> Flask:
    """Configura Flask, la base de datos, CORS y las rutas de la API."""
    app = Flask(__name__, static_folder="static")
    app.config.from_object(Config)

    # Conecta extensiones sin acoplarlas a una instancia global de Flask.
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGINS"]}})

    init_db(app)

    # Registra las rutas para listar y consultar productos.
    api = Api(app)
    api.add_resource(ProductListResource, "/api/products")
    api.add_resource(ProductResource, "/api/products/<string:product_id>")

    return app
