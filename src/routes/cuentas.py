from flask import Blueprint
from flask_restful import Api

from ..resources.cuentas import CrearCuentas, IniciarSesion, EliminarCuenta

cuentas_bp = Blueprint("cuentas", __name__)
api = Api(cuentas_bp)

api.add_resource(CrearCuentas, "/registro")
api.add_resource(IniciarSesion, "/login")
api.add_resource(EliminarCuenta, "/cuentas/<uuid:cuenta_id>")