from flask import Blueprint
from pymongo import MongoClient
from flask import Flask,render_template
from flask import request
client = MongoClient()
app = Flask(__name__)
	
client = MongoClient('localhost', 27017)
db = client['SE']
user_collection = db['users']
charity_collection = db['charity']
event_collection = db['event']

event_data=[{'_id':1,'event_name':'Fundraising for kerala floods','charity_name':'give india','email':'giveindia@gmail.com','phonenumber':9379494567,'target_amount':2000000},
{'_id':2,'event_name':'Fundraising for cancer treatment','charity_name':'smile foundation','email':'smilefoundation@gmail.com','phonenumber':9394567246,'target_amount':1500000}]
event_collection.insert(event_data)

user_data=[{'_id':1,'user_handle':'virat','email':'virat@gmail.com','firstname':'virat','lastname':'kohli','phonenumber':9908678695,'password':'ghjldg'},
{'_id':2,'user_handle':'rohit','email':'rohit@gmail.com','firstname':'rohit','lastname':'sharma','phonenumber':9900973743,'password':'gghjikm'},
{'_id':3,'user_handle':'hardik','email':'hardik@gmail.com','firstname':'hardik','lastname':'pandya','phonenumber':9743040947,'password':'hkjdbkjf'},
{'_id':4,'user_handle':'jasprit','email':'jasprit@gmail.com','firstname':'jasprit','lastname':'bumrah','phonenumber':9900973743,'password':'kjkdnj'},
{'_id':5,'user_handle':'ishant','email':'ishant@gmail.com','firstname':'ishant','lastname':'sharma','phonenumber':9590394064,'password':'xjkksll'},
{'_id':6,'user_handle':'madan','email':'madanr99@gmail.com','firstname':'madan','lastname':'r','phonenumber':9900974085,'password':'abc'}]
user_collection.insert(user_data)

charity_data=[{'_id':1,'charity_name':'give india','charity_handle':'GI','email':'giveindia@gmail.com','phonenumber':9379494567,'password':'sksdfo'},
{'_id':2,'charity_name':'smile foundation','charity_handle':'SF','email':'smilefoundation@gmail.com','phonenumber':9394567246,'password':'ewhfjef'}]
charity_collection.insert(charity_data)


