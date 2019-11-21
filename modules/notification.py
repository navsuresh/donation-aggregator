from modules import globals
from flask import request, jsonify, Response, session, Blueprint
from flask_restful import Resource, Api

api_bp = Blueprint('api_notifications', __name__)
api = Api(api_bp)


def push_notification(message, cid):
    followers = globals.db.follow_index.find_one({"cid": cid})['followers']
    for follower in followers:
        message["uid"] = follower
        globals.db.inbox.insert(message)


class PushNotifications(Resource):
    def post(self, cid):
        data = request.get_json()  # {"foundation-name": "", "content":"", "date":"" }
        data['foundation-name'] = globals.db.charity_details.find_one({"cid": cid})['username']
        data['type'] = 'update'
        push_notification(data, cid)
        return Response(status=200)


class GetNotifications(Resource):
    def get(self):
        inbox = list(globals.db.inbox.find_one({"uid": session['uid']}))
        for message in inbox:
            del message['_id']
        response = jsonify(inbox)
        response.status = 200
        return response


class Inbox(Resource):
    def get(self):
        return globals.app.send_static_file('inbox.html')


api.add_resource(PushNotifications, '/<cid>/push_notification')
api.add_resource(GetNotifications, '/get_notifications')
api.add_resource(Inbox, '/inbox')
