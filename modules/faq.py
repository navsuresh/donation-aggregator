from modules import globals
from flask import request, jsonify, Blueprint, session
from flask_restful import Resource, Api

import datetime


# ------------------------------------------------------

api_bp = Blueprint('api_faq', __name__)
api = Api(api_bp)


class createFAQ(Resource):
    def post(self):
        '''
        Expected json format:
        {
            "CharityID": 1,
            "EventID":  "12",
            "QueryString": "Will refreshments be provided at the event?"
        }
        '''
        req = eval(request.data)
        cid = req["CharityID"]
        eid = req["EventID"]

        events = globals.db.events
        # Check if corresponding charity and event IDs exist
        if (events.find_one({"cid": cid, "eid": eid}) == None):
            return "There is no event ID %s for charity ID %s in DB" % (eid, cid), 404
        faqs = globals.db.faq
        # Check if any faqs exist for this event. If yes, get max value of ++FaqID as new FaqID
        new_faq_id = faqs.find_one({"CharityID": cid, "EventID": eid}, sort=[("FaqID", -1)])
        if (new_faq_id == None):
            new_faq_id = 0
        else:
            new_faq_id = new_faq_id["FaqID"]
            new_faq_id += 1
        query = req["QueryString"]
        faqs.insert_one(
            {"CharityID": cid, "EventID": eid, "FaqID": new_faq_id, "QueryString": query, "Answer": "", "Answered": 0})
        return "New FAQ Query added with FaqID %s" % (new_faq_id), 201


api.add_resource(createFAQ, '/charity/event/initQuery')


# ------------------------------------------------------

# Adding replies to existing thread

class answerFAQ(Resource):
    def post(self):
        '''
        Expected json format:
        {   "CharityID": 1, "EventID":  "12","FaqID": 3,"Answer": "No, participants are kindly requested to bring their own refreshments."}
        '''

        req = eval(request.data)
        print(req)
        cid = req["CharityID"]
        eid = req["EventID"]
        fid = req["FaqID"]
        faqs = globals.db.faq
        # Check if corresponding charity, event IDs and FAQ IDs exist
        faq = faqs.find_one({"CharityID": cid, "EventID": eid, "FaqID": fid})
        if (faq == None):
            return "There is no FAQ ID %s and event ID %s for charity ID %s in DB" % (fid, eid, cid), 404
        '''Uncomment when sessions are active'''
        # if (session["logged_in"] == False):
        #     return "Not logged in", 400

        # if(session["logged_in_as"] != "Charity" or session["cid"] != cid):
        #     return "The cid does not match or you are not a charity!", 400

        answer = req["Answer"]
        faqs.update_one({"CharityID": cid, "EventID": eid, "FaqID": fid}, {"$set": {"Answer": answer}})
        faqs.update_one({"CharityID": cid, "EventID": eid, "FaqID": fid}, {"$set": {"Answered": 1}})

        return "New answer", 201


api.add_resource(answerFAQ, '/charity/event/answerQuery')


# ------------------------------------------------------


# Get full thread

class getAnsweredFAQ(Resource):
    def post(self):
        '''
        Expected json format:
        {
            "CharityID": 1,
            "EventID":  "12"
        }
        returned json format:
        [
            {
                "Query": Will participants recieve certificates for finishing event?",
                "Answer":"Yes, they will! Register soon!"
            }
            {
                "Query": Why does this event not help cats?",
                "Answer":"Because dogs are better than cats"
            }
        ]
        '''
        req = eval(request.data)
        cid = req["CharityID"]
        eid = req["EventID"]
        faqs = globals.db.faq

        # Check if corresponding charity, event IDs and FAQ IDs exist
        faq = faqs.find({"CharityID": cid, "EventID": eid, "Answered": 1})
        if (faq == None):
            return "There is no answered FAQs for event ID %s for charity ID %s in DB" % (eid, cid), 204
        ret_val = []
        for i in faq:
            temp = {}
            temp["Query"] = i["QueryString"]
            temp["Answer"] = i["Answer"]
            ret_val.append(temp)
        return ret_val, 200


api.add_resource(getAnsweredFAQ, '/charity/event/getAnsweredFAQ')


class getunAnsweredFAQ(Resource):
    def post(self):
        '''
        Expected json format:
        {
            "CharityID": 1,
            "EventID":  "12"
        }
        returned json format:
        [
            {
                "Query":"Will participants recieve certificates for finishing event?",
                "FaqID": 2
            },
            {
                "Query": "Why does this event not help cats?"
                "FaqID": 2
            }
        ]
        '''
        print(request.args)
        req = eval(request.data)
        cid = req["CharityID"]
        eid = req["EventID"]
        faqs = globals.db.faq

        # Check if corresponding charity, event IDs and FAQ IDs exist
        faq = faqs.find({"CharityID": cid, "EventID": eid, "Answered": 0})
        if (faq == None):
            return "There is no answered FAQs for event ID %s for charity ID %s in DB" % (eid, cid), 204
        ret_val = []
        for i in faq:
            temp = {}
            temp["Query"] = i["QueryString"]
            temp["FaqID"] = i["FaqID"]
            ret_val.append(temp)
        return ret_val, 200


api.add_resource(getunAnsweredFAQ, '/charity/event/getunAnsweredFAQ')


# ------------------------------------------------------


class getUserPage(Resource):
    def post(self):
        '''
        Expected json format:
            {
                "UserID": "USER53537173"
            }
            returned json format:

            {
                "email":"mayankrao16@gmail.com",
                "eventsList":
                [
                    {
                        "charityName": "Ninaada Foundation",
                        "eventTitle": "Raising money for orphaned children in Bangalore:,
                        "eventDate": "22 November, 2019"
                    },
                    {
                        "charityName": "Bro Foundation",
                        "eventTitle": "Raising money for orphaned bros in Bangalore:,
                        "eventDate": "21 November, 2019"
                    }
                ]
            }
        '''
        req = eval(request.data)
        user_c = globals.db.user_details
        events = globals.db.events
        res = user_c.find_one({"uid": req['UserID']})
        eventsList = []
        for i in res['registered-events']:
            print("eid", i)
            temp = events.find_one({'eid': i})
            print("Temp: ", temp)
            temp_dict = {"charityName": temp['foundation-name'], 'eventTitle': temp['event-title'],
                         'eventDate': temp['date']}
            eventsList.append(temp_dict)
        for i in eventsList:
            i['eventDate'] = datetime.datetime.strptime(i['eventDate'], '%a %b %d %Y %X GMT%z (%Z)')

        eventsList = sorted(eventsList, key=lambda i: i['eventDate'], reverse=True)
        response = jsonify({"email": res['email'], "eventsList": eventsList})
        response.status_code = 200
        return response


api.add_resource(getUserPage, '/user/details')

