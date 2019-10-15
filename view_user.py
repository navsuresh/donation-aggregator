from flask import Blueprint
from pymongo import MongoClient
from flask import Flask
client = MongoClient()
app = Flask(__name__)
with client:
	db = client.login
	db.users.drop()
	db.charity.drop()
	
db = client.login
collection1 = db.users
collection2 = db.charity
user_data=[{'_id':1,'user_handle':'virat','email':'virat@gmail.com','firstname':'virat','lastname':'kohli','phonenumber':9908678695,'password':'ghjldg'},{'_id':2,'user_handle':'rohit','email':'rohit@gmail.com','firstname':'rohit','lastname':'sharma','phonenumber':9900973743,'password':'gghjikm'}]
db.users.insert_many(user_data)

charity_data=[{'_id':1,'charity_name':'give india','charity_handle':'GI','email':'giveindia@gmail.com','phonenumber':9379494567,'password':'sksdfo'},{'_id':2,'charity_name':'smile foundation','charity_handle':'SF','email':'smilefoundation@gmail.com','phonenumber':9394567246,'password':'ewhfjef'}]
db.charity.insert_many(charity_data)

#user=Blueprint('view_user',__name__,template_folder='templates')

@app.route('/')
def test():
	return "<h1>hello</h1>"

@app.route('/view_user/<user_id>',methods=['GET','POST'])
def view_user(user_id):
	document1 = db.users.find_one({'_id':int(user_id)})
	if document1!=None:
		return '<h1>'+str(document1)+'</h1>'
	else:
		return "<h1>fail</h1>"


@app.route('/view_charity/<charity_id>',methods=['GET','POST'])
def view_charity(charity_id):
	document2 = db.charity.find_one({'_id':int(charity_id)})
	if document2!=None:
		return '<h1>'+str(document2)+'</h1>'
	else:
		return "<h1>fail</h1>"





if __name__ == '__main__':
    #app.secret_key = 'mysecret'
    app.run(debug=True)
