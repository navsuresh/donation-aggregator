from flask import Flask,render_template,jsonify
import bcrypt
from flask_mail import Mail, Message
from flask import request,session
from flask_restful import Resource, Api
import json
import random
import pymongo
import re
mongoConn = pymongo.MongoClient("mongodb://localhost:27017/")

db = mongoConn["charity_aggregator"]
col = db["user_details"]
app = Flask(__name__)
api = Api(app)
app.secret_key = "chartiyaggregator" 

userStore = {}

linkReset = {}

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'charity.email.se@gmail.com'
app.config['MAIL_PASSWORD'] = 'charitySE123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail=Mail(app)

class LoginPage(Resource):
    def get(self):
        return app.send_static_file('index.html')


class SignupPage(Resource):
    def get(self):
        return app.send_static_file('signup.html')

class SendMail(Resource):
    def post(self):
        requestData = json.loads(request.get_data().decode("UTF-8"))
        email = requestData["email"]
        code = random.randint(100000,999999)
        msg = Message('Confirm your Sign-up!', sender = 'charity.email.se@gmail.com', recipients = [email])
        msg.body = "Your activation code is "+ str(code)
        session[email] = code
        mail.send(msg)
        userStore[email] = requestData
        userStore[email]["password"] = bcrypt.hashpw(userStore[email]["password"].encode("utf-8"), bcrypt.gensalt())
        return "Sent"


class VerifyOTP(Resource):
    def createUser(self,key):
        userStore[key]["_id"] = "USER"+str(random.randint(10000000,99999999))
        insertDB = col.insert_one(userStore[key])
        del userStore[key]

    def post(self):
        jsonReq = json.loads(request.get_data().decode("UTF-8"))
        email = jsonReq["email"]
        otp = jsonReq["otp"]
        if(int(otp)==int(session[email])):
            session.pop(email)
            self.createUser(email)
            return "1"
        else:
            return "0"

class Login(Resource):
    def post(self):
        jsonReq = json.loads(request.get_data().decode("UTF-8"))
        email = jsonReq["email"]
        password = jsonReq["password"]
        row = col.find({"email":email}).limit(1)
        if row.count():
            if bcrypt.checkpw(password.encode("utf-8"), row[0]["password"]):
                return "Logged In"
        return "Wrong password"

class ForgotPassword(Resource):

    def post(self):
        requestData = json.loads(request.get_data().decode("UTF-8"))
        url = re.sub('[^a-zA-Z]', '', str(bcrypt.hashpw(requestData["email"].encode("utf-8"),bcrypt.gensalt())))[:30:]
        email = requestData["email"]
        linkReset[url] = email
        msg = Message('Reset password', sender = 'charity.email.se@gmail.com', recipients = [email])
        msg.body = "Click this URL to reset your password "+"http://localhost:4000/validatepassword/"+ url
        mail.send(msg)
        return "Sent"
        
class ValidateResetPassword(Resource):

    def get(self,url):
        if url in linkReset:
            return app.send_static_file('reset.html')

class SetNewPassword(Resource):

    def post(self):
        password = json.loads(request.get_data().decode("UTF-8"))["password"]
        url = json.loads(request.get_data().decode("UTF-8"))["url"]
        myquery = { "email": linkReset[url] }
        newvalues = { "$set": { "password": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()) } }
        updateDB = col.update_one(myquery,newvalues)
        del linkReset[url]
            
        

api.add_resource(LoginPage, '/login')
api.add_resource(SignupPage, '/signup')
api.add_resource(SendMail, '/sendMail')
api.add_resource(VerifyOTP, '/verifyotp')
api.add_resource(Login, '/login/senddata')
api.add_resource(ForgotPassword, '/passwordreset')
api.add_resource(ValidateResetPassword, '/validatepassword/<url>')
api.add_resource(SetNewPassword, '/resetpassword')

if __name__ == '__main__':
    app.run(port=4000,debug=True)
