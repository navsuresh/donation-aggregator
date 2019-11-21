from modules import globals
from uuid import uuid1
from flask import request, jsonify, Response, session, Blueprint, render_template
from flask_restful import Resource, Api
from modules.search import Search
from modules.notification import push_notification


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
        slot_count = globals.db.events.find_one({"doc_type": "common"})["slot_count"]   # doc_type common used for getting common data for the collection
        data = request.get_json()
        data["eid"] = str(uuid1())
        data["cid"] = cid
        data["participants"] = []
        data["slots"] = ["_empty" for _ in range(slot_count)]  # Initialise placeholders for allowable widgets
        globals.db.events.insert(data)
        search_engine.update_index(data)
        data["type"]="eventlistings"
        push_notification(data, cid)
        response = jsonify({"eid": data["eid"]})
        response.status_code = 201
        return response


class ViewEvent(Resource):
    def get(self, eid):
        """Return a single event"""
        print(type(eid), eid)
        event = globals.db.events.find_one({"eid": eid})
        del event['_id']
        response = jsonify(event)
        response.status_code = 200
        return response


class Register(Resource):
    def get(self, eid):
        """Registers a user for an event"""
        globals.db.events.update({"eid": eid}, {'$push': {'participants': session["uid"]}})
        globals.db.user_details.update({"uid": session["uid"]}, {'$push': {'registered_events': eid}})
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

        events = globals.db.events.find_one({"eid": eid})
        if events is None:
            return "Invalid Event", 200
        """
        if session["cid"] != events["cid"]:
            return "The CID does not match logged_in ID", 400
        """

        participant_list = []
        for userID in events["participants"]:
            user_details = globals.db.users.find_one({"userID": userID})
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
        event = globals.db.events.find_one({"eid": eid})
        if event is None:
            return "Invalid Event", 200
        """
        if event["cid"] != session["cid"]:
            return "The cid does not match logged_in id.", 400
        """
        data = request.get_json()
        globals.db.events.update({"eid": eid}, {"$set": data})
        return Response(status=200)


class ViewAllEvents(Resource):
    def get(self):
        data = list(globals.db.events.find({"event-title": {"$exists": True}}))
        for event in data:
            del event['_id']
        response = jsonify(list(data))
        response.status_code = 200
        return response


class Search(Resource):
    def get(self, query):
        results = search_engine.compute_score(query)
        response = jsonify(results)
        response.status_code = 200
        return response


class Event(Resource):
    def get(self):
        return globals.app.send_static_file('event_listings.html')


class EventsPage(Resource):
    def get(self, eventid):
        return globals.app.send_static_file('events.html')


# update a slot
class UpdateWidget(Resource):
    def post(self, eid):
        # un-comment when session is implemented
        """
            if(session["logged_in"]==False): # not logged in
                return "Not logged in.",400
            if(session["logged_in_as"]!="charity"): # not logged in as a charity
                return "You do not have permission to update this page.",400
        """
        event = globals.db.events.find_one({"eid": eid})
        if event is None:
            return "Invalid Event", 200
        """
        if event["cid"] != session["cid"]:
            return "The cid does not match logged_in id.", 400
        """

        slots = eval(request.data) # expecting json format (Ex - '[src1, src2, src3]')
        myquery = {"eid": eid}
        newvalues = {"$set": {"slots": slots}} # updating slots to the new value
        globals.db.events.update_one(myquery, newvalues)

        return "updated", 200

# recieve a slot
class GetWidget(Resource):
    def post(self, eid):
        event = globals.db.events.find_one({"eid": eid})
        if event is None:
            return "Invalid Event", 200

        slots = globals.db.events.find_one({"eid": eid})["widgets"]
        return jsonify(slots)


class Calendar(Resource):
    def get(self):
        return globals.app.send_static_file('calendar.html')


api.add_resource(UpdateWidget, '/<eid>/update-widget')
api.add_resource(GetWidget, '/<eid>/get-widget')
api.add_resource(CreateEvent, '/<cid>/create-event')
api.add_resource(ViewEvent, '/<eid>/view-event')
api.add_resource(ViewAllEvents, '/list-events')
api.add_resource(Register, '/<eid>/register')
api.add_resource(GetParticipantList, '/get-participant-list')
api.add_resource(UpdateEvent, '/<eid>/update-event')
api.add_resource(Search, '/search/<query>')
api.add_resource(Event, '/event-listings')
api.add_resource(EventsPage, '/events/<eventid>')
api.add_resource(Calendar, '/calendar')

#
# if __name__ == '__main__':
#     globals.app.run(debug=True)


