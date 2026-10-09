import uuid

from flask import request, url_for
from flask_restful import Resource
from sqlalchemy import select

from src.extensions import db
from src.models import Product


def serialize_product(product: Product) -> dict[str, str | int | float | None]:
    """Convierte el producto en JSON e incluye la URL pública de su imagen."""
    image_url = url_for(
        "static",
        filename=f"images/{product.image_filename}",
        _external=True,
    )
    return product.to_dict(image_url)


class ProductListResource(Resource):
    def get(self):
        """Lista productos en orden estable y filtra opcionalmente por categoría."""
        category = request.args.get("category")
        query = Product.query
        if category and category != "all":
            query = query.filter_by(category=category)

        products = query.order_by(Product.sort_order.asc()).all()
        return {"products": [serialize_product(product) for product in products]}, 200


class ProductResource(Resource):
    def get(self, product_id: str):
        """Busca un producto por UUID y responde con un error claro si no existe."""
        try:
            product_uuid = uuid.UUID(product_id)
        except ValueError:
            return {"error": "El identificador del producto no es válido."}, 400

        product = db.session.execute(
            select(Product).where(Product.id == product_uuid)
        ).scalar_one_or_none()
        if product is None:
            return {"error": "Producto no encontrado."}, 404
        return serialize_product(product), 200
