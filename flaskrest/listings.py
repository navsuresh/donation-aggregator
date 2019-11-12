#from main import app
from flask import Flask,redirect,render_template,request,Blueprint
from flask_pymongo import PyMongo
from datetime import datetime
#from main import mongo

#listings = Flask(__name__)

listings = Blueprint('listings', __name__,
                        template_folder='templates')

mongo = PyMongo()

@listings.route('/')
def home():
    return render_template('update.html')

@listings.route('/listings',methods=['GET','POST'])
def index():
    date1 = datetime.now()
    todate = date1.strftime("%Y-%m-%d")
    req = mongo.db.Event.find({'dateRegister':{'$gte':todate}}).sort('dateRegister')
        
		#resp = jsonify('User added successfully!')
    return render_template('index.html',req = req)








##list events,order by date
#event name ,event category,short description,organizer,date posted,date held,link to view event
#should there be search implemented - not right now
#can have filters based on category , organizer,date,last day to register if there


#