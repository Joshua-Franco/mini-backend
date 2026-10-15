from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from sqlalchemy import select

from ..models.productos import Producto
from ..extensions.extension import db


class Productos(Resource):
    # GET /productos (pública)
    def get(self):
        productos = db.session.execute(select(Producto)).scalars().all()
        return [p.to_dict() for p in productos], 200

    # POST /productos (protegida)
    @jwt_required()
    def post(self):
        data = request.get_json(silent=True) or {}

        nombre = data.get("nombre")
        precio = data.get("precio")

        if not nombre or precio is None:
            return {"error": "nombre y precio son obligatorios"}, 400

        try:
            precio = float(precio)
        except (TypeError, ValueError):
            return {"error": "precio debe ser un número"}, 400

        producto = Producto(
            nombre=nombre,
            precio=precio,
        )
        db.session.add(producto)
        db.session.commit()
        return producto.to_dict(), 201


class ProductoPorId(Resource):
    # GET /productos/<id> (pública)
    def get(self, id):
        producto = db.session.get(Producto, id)
        if not producto:
            return {"error": "Producto no encontrado"}, 404
        return producto.to_dict(), 200

    # PUT /productos/<id> (protegida)
    @jwt_required()
    def put(self, id):
        producto = db.session.get(Producto, id)
        if not producto:
            return {"error": "Producto no encontrado"}, 404

        data = request.get_json(silent=True) or {}

        if "nombre" in data:
            producto.nombre = data["nombre"]
        if "precio" in data:
            try:
                producto.precio = float(data["precio"])
            except (TypeError, ValueError):
                return {"error": "precio debe ser un número"}, 400
        db.session.commit()
        return producto.to_dict(), 200

    # DELETE /productos/<id> (protegida)
    @jwt_required()
    def delete(self, id):
        producto = db.session.get(Producto, id)
        if not producto:
            return {"error": "Producto no encontrado"}, 404

        db.session.delete(producto)
        db.session.commit()
        return "", 204
