from pymongo import MongoClient
from flask import Flask
from flask_cors import CORS

# app = Flask(__name__)

global app
global mail

app = None

client = MongoClient('localhost', 27017)
db = client.charity_aggregator
index_title_col = db["index_title"]

