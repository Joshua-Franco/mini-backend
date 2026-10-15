from flask import Blueprint
from flask_restful import Api

from ..resources.encendido import Server

server_bp = Blueprint("server", __name__)
api = Api(server_bp)

api.add_resource(Server, "/")