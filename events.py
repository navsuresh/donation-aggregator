from globals import *
from uuid import uuid1
from flask import Flask, request, jsonify, Response, session, Blueprint
from flask_restful import Resource, Api
from search import Search


api_bp = Blueprint('api_events', __name__)
api = Api(api_bp)

search_engine = Search()



class CreateEvent(Resource):
    def post(self, cid):
        """Generates an event identifier and makes an entry into events collection"""
        '''
            if(session["logged_in"]==False): # not logged in
                return "Not logged in.",400
            if(session["logged_in_as"]!="charity"): # not logged in as a charity
                return "The cid does not match logged_in id.",400
        '''
        slot_count = db.events.find_one({"doc_type": "common"})["slots_count"]   # doc_type common used for getting common data for the collection
        data = request.get_json()
        data["eid"] = str(uuid1())
        data["cid"] = cid
        data["participants"] = []
        data["slots"] = ["_empty" for _ in range(slot_count)]  # Initialise placeholders for allowable widgets
        db.events.insert(data)
        search_engine.update_index(data)
        response = jsonify({"eid": data["eid"]})
        response.status_code = 201
        return response


class ViewEvent(Resource):
    def get(self, eid):
        """Return a single event"""
        event = db.events.find_one({"eid": eid})
        del event['_id']
        response = jsonify(event)
        response.status_code = 200
        return response


class Register(Resource):
    def get(self, eid):
        """Registers a user for an event"""
        db.events.update({"eid": eid}, {'$push': {'participants': session["uid"]}})
        response = Response(status=200)
        return response


class GetParticipantList(Resource):
    def get(self, eid):
        """
        if(session["logged_in"]==False): # not logged in
            return "Not logged in.",400
        if(session["logged_in_as"]!="charity": # not logged in as a charity
            return "The cid does not match logged_in id.",400
        """

        events = db.events.find_one({"eid": eid})
        if events is None:
            return "Invalid Event", 200
        """
        if session["cid"] != events["cid"]:
            return "The CID does not match logged_in ID", 400
        """

        participant_list = []
        for userID in events["participants"]:
            user_details = db.users.find_one({"userID": userID})
            participant_list.append({"FirstName": user_details["FirstName"], "LastName": user_details["LastName"],
                                     "ContactNo": user_details["ContactNo"], "EmailID": user_details["EmailID"]})
        response = jsonify(participant_list)
        response.status_code = 200
        return response


class UpdateEvent(Resource):
    def put(self, eid):
        """
            if(session["logged_in"]==False): # not logged in
                return "Not logged in.",400
            if(session["logged_in_as"]!="charity"): # not logged in as a charity
                return "You do not have permission to update this page.",400
        """
        event = db.events.find_one({"eid": eid})
        if event is None:
            return "Invalid Event", 200
        """
        if event["cid"] != session["cid"]:
            return "The cid does not match logged_in id.", 400
        """
        data = request.get_json()
        db.events.update({"eid": eid}, {"$set": data})
        return Response(status=200)


class ViewAllEvents(Resource):
    def get(self):
        data = list(db.events.find({"event-title": {"$exists": True}}))
        for event in data:
            del event['_id']
        response = jsonify(list(data))
        response.status_code = 200
        return response


class Search(Resource):
    def get(self, query):
        results = search_engine.compute_score(query)
        print(results)
        response = jsonify(results)
        print(response)
        response.status_code = 200
        return response


api.add_resource(CreateEvent, '/<cid>/create-event')
api.add_resource(ViewEvent, '/<eid>/view-event')
api.add_resource(ViewAllEvents, '/list-events')
api.add_resource(Register, '/<eid>/register')
api.add_resource(GetParticipantList, '/get-participant-list')
api.add_resource(UpdateEvent, '/<eid>/update-event')
api.add_resource(Search, '/search/<query>')

#
# if __name__ == '__main__':
#     app.run(debug=True)


