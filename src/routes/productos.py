from flask import Blueprint
from flask_restful import Api

from ..resources.productos import (
    Productos,
    ProductoPorId,
)

productos_bp = Blueprint("productos", __name__)
api = Api(productos_bp)

api.add_resource(Productos, "/productos")
api.add_resource(ProductoPorId, "/productos/<uuid:id>")
