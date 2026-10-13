import uuid
from decimal import Decimal

from flask import current_app, request, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from sqlalchemy import select
from pydantic import ValidationError

from src.extensions import db
from src.models import Product, User
from src.resources.auth_schemas import ProductPayload


def serialize_product(product: Product) -> dict[str, str | int | float | bool | None]:
    """Convierte el producto en JSON e incluye la URL pública de su imagen."""
    # Genera una URL absoluta para que el frontend pueda mostrar la imagen.
    image_url = url_for(
        "static",
        filename=f"images/{product.image_filename}",
        _external=True,
    )
    return product.to_dict(image_url)


def validate_product_payload():
    """Valida los campos de producto antes de escribir en la base de datos."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, {"error": "Envía los datos del producto en formato JSON."}, 400

    try:
        return ProductPayload.model_validate(data), None, None
    except ValidationError as error:
        messages = [
            f"{'.'.join(str(part) for part in item['loc'])}: {item['msg']}"
            for item in error.errors(include_url=False)
        ]
        return None, {"error": " ".join(messages)}, 400


def admin_error():
    """Restringe las escrituras a cuentas autenticadas incluidas en ADMIN_EMAILS."""
    identity = get_jwt_identity()
    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        return {"error": "La identidad del token no es válida."}, 401

    user = db.session.get(User, user_id)
    if user is None:
        return {"error": "La cuenta asociada al token ya no existe."}, 401
    if user.email not in current_app.config["ADMIN_EMAILS"]:
        return {"error": "Se requieren permisos de administrador."}, 403
    return None


def apply_product_payload(product: Product, payload: ProductPayload) -> None:
    """Copia los datos validados al modelo y conserva precisión en los precios."""
    product.name = payload.name
    product.price = Decimal(str(payload.price))
    product.image_filename = payload.image_filename


class ProductListResource(Resource):
    def get(self):
        """Lista productos activos en orden alfabético."""
        products = (
            Product.query.filter_by(activado=True)
            .order_by(Product.name.asc())
            .all()
        )
        return {"products": [serialize_product(product) for product in products]}, 200

    @jwt_required()
    def post(self):
        """Crea un producto después de comprobar identidad y permisos."""
        permission_error = admin_error()
        if permission_error:
            return permission_error

        payload, validation_error, status = validate_product_payload()
        if validation_error:
            return validation_error, status
        assert isinstance(payload, ProductPayload)

        product = Product()
        apply_product_payload(product, payload)
        db.session.add(product)
        db.session.commit()

        return serialize_product(product), 201


class ProductResource(Resource):
    def get(self, product_id: str):
        """Busca un producto por UUID y responde con un error claro si no existe."""
        # Valida el formato antes de consultar la base de datos.
        try:
            product_uuid = uuid.UUID(product_id)
        except ValueError:
            return {"error": "El identificador del producto no es válido."}, 400

        product = db.session.execute(
            select(Product).where(Product.id == product_uuid, Product.activado.is_(True))
        ).scalar_one_or_none()
        if product is None:
            return {"error": "Producto no encontrado."}, 404
        return serialize_product(product), 200

    @jwt_required()
    def put(self, product_id: str):
        """Reemplaza los campos del producto validado por su UUID."""
        permission_error = admin_error()
        if permission_error:
            return permission_error

        product_uuid = self.parse_product_id(product_id)
        if isinstance(product_uuid, tuple):
            return product_uuid
        product = db.session.execute(
            select(Product).where(Product.id == product_uuid, Product.activado.is_(True))
        ).scalar_one_or_none()
        if product is None:
            return {"error": "Producto no encontrado."}, 404

        payload, validation_error, status = validate_product_payload()
        if validation_error:
            return validation_error, status
        assert isinstance(payload, ProductPayload)

        apply_product_payload(product, payload)
        db.session.commit()

        return serialize_product(product), 200

    @jwt_required()
    def delete(self, product_id: str):
        """Desactiva el producto solicitado sin borrarlo de la base de datos."""
        permission_error = admin_error()
        if permission_error:
            return permission_error

        product_uuid = self.parse_product_id(product_id)
        if isinstance(product_uuid, tuple):
            return product_uuid
        product = db.session.execute(
            select(Product).where(Product.id == product_uuid, Product.activado.is_(True))
        ).scalar_one_or_none()
        if product is None:
            return {"error": "Producto no encontrado."}, 404

        product.activado = False
        db.session.commit()
        return {"message": "Producto desactivado."}, 200

    @staticmethod
    def parse_product_id(product_id: str) -> uuid.UUID | tuple[dict[str, str], int]:
        """Valida el UUID antes de ejecutar una consulta por producto."""
        try:
            return uuid.UUID(product_id)
        except ValueError:
            return {"error": "El identificador del producto no es válido."}, 400
