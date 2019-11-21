from modules import globals
from uuid import uuid1
from flask import request, jsonify, Response, session, Blueprint
from flask_restful import Resource, Api

api_bp = Blueprint('api_charity', __name__)
api = Api(api_bp)


class CustomProfilePage(Resource):
    def get(self):
        return globals.app.send_static_file('customize.html')




api.add_resource(CustomProfilePage, '/profile')