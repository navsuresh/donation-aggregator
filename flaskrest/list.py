from flask import Flask,redirect,render_template,request,Blueprint,make_response,url_for
from bson.json_util import dumps
from datetime import datetime
from flask_restful import Resource, Api
#from flask_pymongo import PyMongo
from pymongo import MongoClient




client = MongoClient('localhost', 27017)
db = client["charity_agg"]
events = db["events"]



class Home(Resource):
    def get(self):
        headers = {'Content-Type':'text/html'}
        return make_response(render_template('update.html'),200,headers)

class Listings(Resource):
    def get(self):
        #now = datetime.now()
        #timestamp = datetime.timestamp(now)
        #todate1 = datetime.fromtimestamp(timestamp)
        date1 = datetime.now()
        todate = date1.strftime('%Y-%m-%d')
        print("date1 is ",todate)
        req = events.find({'Date':{'$gte':todate}}).sort('Date')
        req2 = req
        #sresp = dumps(req2)
        #print(sresp)
            #resp = jsonify('User added successfully!')
        headers = {'Content-Type':'text/html'}
        return make_response(render_template('index.html',req=req),200,headers)