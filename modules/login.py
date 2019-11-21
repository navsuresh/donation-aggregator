from modules import globals
from flask import request, session, Blueprint
from flask_restful import Resource, Api
from flask_mail import Mail, Message
import json
import random
import re
import bcrypt

api_bp = Blueprint('api_login', __name__)
api = Api(api_bp)

userStore = {}
loggedIn = []
linkReset = {}

mail = Mail(globals.app)


class LoginPage(Resource):
    def get(self):
        return globals.app.send_static_file('index.html')


class SignupPage(Resource):
    def get(self):
        return globals.app.send_static_file('signup.html')


class SendMail(Resource):
    def post(self):
        requestData = json.loads(request.get_data().decode("UTF-8"))
        print(requestData)
        email = requestData["email"]
        code = random.randint(100000, 999999)
        msg = Message('Confirm your Sign-up!', sender='charity.email.se@gmail.com', recipients=[email])
        msg.body = "Your activation code is " + str(code)
        session[email] = code
        mail.send(msg)
        userStore[email] = requestData
        userStore[email]["password"] = bcrypt.hashpw(userStore[email]["password"].encode("utf-8"), bcrypt.gensalt())
        return "Sent"


class VerifyOTP(Resource):
    def createUser(self, key):

        if userStore[key]["role"] == "charity":
            userStore[key]["cid"] = "CHARITY" + str(random.randint(10000000, 99999999))
            userStore[key]["followers"] = 0
            insertDB = globals.db.charity_details.insert_one(userStore[key])
        else:
            userStore[key]["uid"] = "USER" + str(random.randint(10000000, 99999999))
            insertDB = globals.db.user_details.insert_one(userStore[key])
        del userStore[key]

    def post(self):
        jsonReq = json.loads(request.get_data().decode("UTF-8"))
        email = jsonReq["email"]
        otp = jsonReq["otp"]
        if (int(otp) == int(session[email])):
            session.pop(email)
            self.createUser(email)
            return "1"
        else:
            return "0"


class UpdateCharityFollowCount(Resource):

    def post(self):
        jsonReq = request.get_json(force=True)
        print(jsonReq)
        myquery = {"cid": jsonReq["CharityID"]}
        row = globals.db.charity_details.find({"cid": jsonReq["CharityID"]}).limit(1)
        currFollow = row[0]["followers"] + 1
        newvalues = {"$set": {"followers": currFollow}}
        updateDB = globals.db.charity_details.update_one(myquery, newvalues)

    def get(self):
        row = globals.db.charity_details.find({"cid": request.args["CharityID"]}).limit(1)
        return str(row[0]["followers"])


class Login(Resource):
    def post(self):
        jsonReq = json.loads(request.get_data().decode("UTF-8"))
        email = jsonReq["email"]
        password = jsonReq["password"]
        userrow = globals.db.user_details.find({"email": email}).limit(1)
        charityrow = globals.db.charity_details.find({"email": email}).limit(1)
        if userrow.count():
            if bcrypt.checkpw(password.encode("utf-8"), userrow[0]["password"]):
                return "Logged In-" + str(userrow[0]["uid"])
        elif charityrow.count():
            if bcrypt.checkpw(password.encode("utf-8"), charityrow[0]["password"]):
                return "Logged In-" + str(charityrow[0]["cid"])
        return "Wrong password"


class ForgotPassword(Resource):

    def post(self):
        requestData = json.loads(request.get_data().decode("UTF-8"))
        url = re.sub('[^a-zA-Z]', '', str(bcrypt.hashpw(requestData["email"].encode("utf-8"), bcrypt.gensalt())))[:30:]
        email = requestData["email"]
        linkReset[url] = email
        msg = Message('Reset password', sender='charity.email.se@gmail.com', recipients=[email])
        msg.body = "Click this URL to reset your password " + "http://localhost:5000/validatepassword/" + url
        mail.send(msg)
        return "Sent"


class ValidateResetPassword(Resource):

    def get(self, url):
        if url in linkReset:
            return globals.app.send_static_file('reset.html')


class SetNewPassword(Resource):

    def post(self):
        password = json.loads(request.get_data().decode("UTF-8"))["password"]
        url = json.loads(request.get_data().decode("UTF-8"))["url"]
        myquery = {"email": linkReset[url]}
        newvalues = {"$set": {"password": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())}}
        updateDB = globals.db.user_details.update_one(myquery, newvalues)
        del linkReset[url]


class CustomProfilePage(Resource):

    def get(self):
        return globals.app.send_static_file('customize.html')


class EventsPage(Resource):

    def get(self, eventid):
        return globals.app.send_static_file('events.html')




api.add_resource(LoginPage, '/login')
api.add_resource(SignupPage, '/signup')
api.add_resource(SendMail, '/sendMail')
api.add_resource(VerifyOTP, '/verifyotp')
api.add_resource(Login, '/login/senddata')
api.add_resource(ForgotPassword, '/passwordreset')
api.add_resource(ValidateResetPassword, '/validatepassword/<url>')
api.add_resource(SetNewPassword, '/resetpassword')
