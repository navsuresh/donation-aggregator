from pymongo import MongoClient
from flask import Flask
from flask import Blueprint
client = MongoClient()
app = Flask(__name__)
with client:
	db = client.login
	db.users.drop()
	db.charity.drop()
	
db = client.login
collection1 = db.users
collection2 = db.charities

user_data=[{'user_id':'u1','user_handle':'virat','email':'virat@gmail.com','firstname':'virat','lastname':'kohli','phonenumber':9908678695,'password':'ghjldg','followed_list':["c1","c3"]},{'user_id':'u2','user_handle':'rohit','email':'rohit@gmail.com','firstname':'rohit','lastname':'sharma','phonenumber':9900973743,'password':'gghjikm','followed_list':["c1","c4"]}]
db.users.insert_many(user_data)

charity_data=[{'charity_id':'c1','charity_name':'give india','charity_handle':'GI','email':'giveindia@gmail.com','phonenumber':9379494567,'password':'sksdfo'},{'charity_id':'c2','charity_name':'smile foundation','charity_handle':'SF','email':'smilefoundation@gmail.com','phonenumber':9394567246,'password':'ewhfjef'}]
db.users.insert_many(charity_data)

@app.route('/')
def test():
	return "<h1>Hello</h1>"

@app.route('/follow_charity/<charity_id>',methods=['GET','POST'])
def follow_charity(charity_id,user_id):
	d1=db.users.user_id.find({followed_list:{$in:[charity_id]}})
	if d1!=None:
		return "Already following"
	else:
		db.users.update({user_id:int(user_id)},$push:{followed_list:charity_id})

if __name__ == '__main__':
    #app.secret_key = 'mysecret'
    app.run(debug=True)
