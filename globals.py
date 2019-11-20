from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.charity_agg
index_title_col = db["index_title"]