from flask_restful import Resource

class Server(Resource):
    def get(self):
        return {"server": "Okay, the server is running!"}, 200