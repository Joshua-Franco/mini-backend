from .server import server_bp
from .productos import productos_bp
from .cuentas import cuentas_bp


def register_routes(app):
    app.register_blueprint(server_bp)                      # responde en /
    app.register_blueprint(productos_bp,)
    app.register_blueprint(cuentas_bp,)