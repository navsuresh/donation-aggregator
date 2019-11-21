from modules import globals
from uuid import uuid1
from flask import request, jsonify, Response, session, Blueprint
from flask_restful import Resource, Api

api_bp = Blueprint('api_charity', __name__)
api = Api(api_bp)


class CustomProfilePage(Resource):
    def get(self,cid):
        return globals.app.send_static_file('customize.html')

class GetCustomCharityData(Resource):
    def post(self,cid):
        data = request.get_json()
        pageData = globals.db.charities.find_one({"cid": cid})
        if pageData==None:
            globals.db.charities.insert(data)
        else:
            globals.db.charities.update({"cid": cid}, {"$set": data})
        response = "Added"
        return response

class LoadCharityPageData(Resource):
    def post(self,cid):
        pageData = globals.db.charities.find_one({"cid": cid})
        del pageData['_id']
        response = jsonify(pageData)
        return response

api.add_resource(CustomProfilePage, '/profile/<cid>')
api.add_resource(GetCustomCharityData, '/customdata/<cid>')
api.add_resource(LoadCharityPageData, '/charitydata/<cid>')