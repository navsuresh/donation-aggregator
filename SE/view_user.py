import hashlib
from pymongo import MongoClient
from flask import Flask,render_template,request,Blueprint 
client = MongoClient()
app = Flask(__name__)

#user=Blueprint('view_user',__name__,template_folder='templates')

client = MongoClient('localhost', 27017)
db = client['SE']
user_collection = db['users']
charity_collection = db['charity']

@app.route('/')
def test():
	return "<h1>hello</h1>"

@app.route('/view_user/<user_id>',methods=['GET','POST'])
def view_user(user_id):
	user_data=user_collection.find_one({'_id':int(user_id)},{'_id':0,'password':0})
	if user_data!=None:
		name=user_data['firstname']+' '+user_data['lastname']
		return render_template('view_user.html',result=user_data,name=name)
		#return '<h1>'+str(document1)+'</h1>'

	else:
		return "<h1>fail</h1>"


@app.route('/view_charity/<charity_id>',methods=['GET','POST'])
def view_charity(charity_id):
	charity_data=charity_collection.find_one({'_id':int(charity_id)},{'_id':0,'password':0})
	if charity_data!=None:
		name=charity_data['charity_name']
		return render_template('view_user.html',result=charity_data,name=name)
		#return '<h1>'+str(document2)+'</h1>'
	else:
		return "<h1>fail</h1>"



def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['GET','POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'



if __name__ == '__main__':
    #app.secret_key = 'mysecret'
    app.run(debug=True)
