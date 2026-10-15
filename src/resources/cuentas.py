from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from pydantic import ValidationError
from sqlalchemy import select

from ..models.cuentas import Cuenta
from ..schemas.cuentas import CuentaCrear
from ..extensions.extension import db


class CrearCuentas(Resource):
    # POST /registro
    def post(self):
        try:
            data = CuentaCrear(**(request.get_json(silent=True) or {}))
        except ValidationError as e:
            return {"errors": e.errors(include_url=False, include_context=False, include_input=False)}, 400

        existe = db.session.execute(
            select(Cuenta).where(Cuenta.email == data.email)
        ).scalars().first()
        if existe:
            return {"error": "El email ya está registrado"}, 409

        cuenta = Cuenta(nombre=data.nombre, email=data.email)
        cuenta.set_password(data.password)
        db.session.add(cuenta)
        db.session.commit()

        token = create_access_token(identity=str(cuenta.id))

        return {"cuenta": cuenta.to_dict(access_token=token)}, 201

class IniciarSesion(Resource):
    # POST /login
    @jwt_required()
    def post(self):
        data = request.get_json(silent=True) or {}

        cuenta = db.session.execute(
            select(Cuenta).where(
                Cuenta.email == data.get("email")
            )
        ).scalars().first()

        if not cuenta:
            return {
                "error": "El correo electrónico ingresado no está registrado."
            }, 401

        if not cuenta.check_password(data.get("contrasena", "")):
            return {
                "error": "La contraseña ingresada es incorrecta."
            }, 401

        if str(get_jwt_identity()) != str(cuenta.id):
            return {
                "error": "El token no corresponde a esta cuenta."
            }, 401

        authorization = request.headers.get("Authorization", "")
        scheme, separator, token = authorization.partition(" ")

        if not separator or scheme.lower() != "bearer" or not token:
            return {"error": "Se requiere un token Bearer válido."}, 401

        return {
            "cuenta": cuenta.to_dict(access_token=token)
        }, 200


class EliminarCuenta(Resource):
    # DELETE /cuentas/<uuid:cuenta_id>
    @jwt_required()
    def delete(self, cuenta_id):
        usuario_id = get_jwt_identity()

        if str(cuenta_id) != usuario_id:
            return {
                "error": "Se requiere un JWT válido para realizar esta operación."
            }, 401

        cuenta = db.session.get(Cuenta, cuenta_id)

        if not cuenta:
            return {
                "error": "Cuenta no encontrada."
            }, 404

        db.session.delete(cuenta)
        db.session.commit()

        return {
            "message": "Cuenta eliminada exitosamente."
        }, 200