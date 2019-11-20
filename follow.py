from globals import *
from flask import  request, Response, Blueprint, session
from flask_restful import Resource, Api


api_bp = Blueprint('api_folow', __name__)
api = Api(api_bp)


class Follow(Resource):
    def post(self, cid):
        """
        if (session["logged_in"] == False):  # not logged in
            return "Not logged in.", 400
        """
        user_id = session["uid"]
        charity = db.follow_index.find_one({"cid": cid})
        if charity is None:
            db.follow_index.insert({"cid": cid, "followers": [user_id]})
        else:
            if user_id not in charity['followers']:
                db.follow_index.update({"cid": cid}, {"$push": {"followers": user_id}})
        return Response(status=200)


class Unfollow(Resource):
    def post(self):
        """
        if (session["logged_in"] == False):  # not logged in
            return "Not logged in.", 400
        """
        user_id = request.json["user_id"]
        charity_id = request.json["charity_id"]
        charity = db.follow_index.find_one({"charity_id": charity_id})
        if user_id in charity['followers']:
            db.follow_index.update({"charity_id": charity_id}, {"$pull": {"followers": user_id}})
        return Response(status=200)


api.add_resource(Follow, '/<cid>/follow')
api.add_resource(Unfollow, '/follow-feed')

# if __name__ == '__main__':
#     app.run(debug=True)