from flask import Flask,redirect,render_template,request,Blueprint,make_response,url_for
from flask_restful import Api
from list import Home,Listings



api_bp = Blueprint('api', __name__)
api = Api(api_bp)


#mongo = PyMongo()




api.add_resource(Home,'/')
api.add_resource(Listings, '/listings')
