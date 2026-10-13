from pathlib import Path

from flask import Flask, request, url_for
from flask_cors import CORS
from flask_restful import Api
from sqlalchemy import inspect, text

from src.config import Config
from src.extensions import db, jwt
from src.resources.auth import CurrentUserResource, LoginResource, RegisterResource
from src.resources.products import ProductListResource, ProductResource
from src.seed import seed_products


def init_db(app: Flask) -> None:
    """Crea las tablas y carga productos de ejemplo si el catálogo está vacío."""
    with app.app_context():
        db.create_all()
        migrate_product_schema()
        seed_products()


def migrate_product_schema() -> None:
    """Adapta tablas existentes al modelo actual del catálogo."""
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns("productos")}
    dialect = db.engine.dialect.name

    if dialect == "postgresql":
        actions = []
        if "activado" not in columns:
            actions.append("ADD COLUMN IF NOT EXISTS activado BOOLEAN NOT NULL DEFAULT TRUE")
        actions.extend(
            [
                "DROP COLUMN IF EXISTS sort_order",
                "DROP COLUMN IF EXISTS old_price",
                "DROP COLUMN IF EXISTS category",
                "DROP COLUMN IF EXISTS badge",
                "DROP COLUMN IF EXISTS icon",
                "DROP COLUMN IF EXISTS specs",
            ]
        )
        statement = "ALTER TABLE productos " + ", ".join(actions)
    else:
        actions = []
        if "activado" not in columns:
            actions.append("ADD COLUMN activado BOOLEAN NOT NULL DEFAULT TRUE")
        removed_columns = {"sort_order", "old_price", "category", "badge", "icon", "specs"}
        for index in inspector.get_indexes("productos"):
            if removed_columns.intersection(index["column_names"]):
                index_name = db.engine.dialect.identifier_preparer.quote(index["name"])
                with db.engine.begin() as connection:
                    connection.execute(text(f"DROP INDEX {index_name}"))
        for column in removed_columns:
            if column in columns:
                actions.append(f"DROP COLUMN {column}")
        if not actions:
            return

    with db.engine.begin() as connection:
        if dialect == "postgresql":
            connection.execute(text(statement))
        else:
            for action in actions:
                connection.execute(text(f"ALTER TABLE productos {action}"))


def create_app() -> Flask:
    """Configura Flask, la base de datos, CORS y las rutas de la API."""
    app = Flask(__name__, static_folder="static")
    app.config.from_object(Config)

    # Conecta extensiones sin acoplarlas a una instancia global de Flask.
    db.init_app(app)
    jwt.init_app(app)

    # Rechaza operaciones de cuenta si falta la clave usada para firmar tokens.
    @app.before_request
    def check_auth_configuration():
        if request.path.startswith("/api/auth/") and not app.config.get("JWT_SECRET_KEY"):
            return {"error": "La autenticación no está configurada en el servidor."}, 503
        return None

    # Endpoint sencillo para comprobar que el servidor responde.
    @app.get("/")
    def health_check():
        return {"server": "okay"}, 200

    @app.get("/api/images")
    def list_images():
        """Devuelve imágenes permitidas con sus URLs públicas."""
        images_directory = Path(app.static_folder or "") / "images"
        # Solo publica formatos comunes de imagen y ordena la lista por nombre.
        allowed_extensions = {".gif", ".jpeg", ".jpg", ".png", ".webp"}
        images = (
            [
                {
                    "filename": image.name,
                    "url": url_for("static", filename=f"images/{image.name}", _external=True),
                }
                for image in sorted(images_directory.iterdir(), key=lambda file: file.name.casefold())
                if image.is_file() and image.suffix.casefold() in allowed_extensions
            ]
            if images_directory.is_dir()
            else []
        )
        return {"images": images}, 200

    # Autoriza el origen del frontend y los encabezados usados por la API.
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGINS"]}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    init_db(app)

    # Registra las rutas del catálogo y las operaciones de cuenta.
    api = Api(app)
    api.add_resource(ProductListResource, "/api/products")
    api.add_resource(ProductResource, "/api/products/<string:product_id>")
    api.add_resource(RegisterResource, "/api/auth/register")
    api.add_resource(LoginResource, "/api/auth/login")
    api.add_resource(CurrentUserResource, "/api/auth/me")

    return app
