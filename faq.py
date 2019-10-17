from flask import Flask, jsonify, request, session 
from flask_restful import Resource, Api
from pymongo import MongoClient

# ------------------------------------------------------

# Flask app
app = Flask(__name__)
app.secret_key = 'i love white chocolate'
api = Api(app)


# ------------------------------------------------------

# Connecting to the carity_page collection
client = MongoClient('localhost', 27017)
db = client['charity_agg']


# ------------------------------------------------------

# Creating a FAQ thread

class createFAQ(Resource):
    def post(self):
        '''
        Expected json format:
        {
            "CharityID": 1, 
            "EventID":  "12",
            "UserID": 25,
            "QueryString": "Will refreshments be provided at the event?"
        }
        '''
        req = eval(request.data)
        cid = req["CharityID"]
        eid = req["EventID"]
        uid = req["UserID"]

        events = db["events"]
        # Check if corresponding charity and event IDs exist
        if(events.find_one({"CharityID": cid, "EventID": eid}) == None):
            return "There is no event ID %s for charity ID %s in DB"%(eid, cid), 404
        faqs = db["faqs"]
        # Check if any faqs exist for this event. If yes, get max value of ++FaqID as new FaqID
        new_faq_id = faqs.find_one({"CharityID": cid, "EventID": eid}, sort = [("FaqID", -1)])
        if(new_faq_id == None):
            new_faq_id = 0
        else:
            new_faq_id = new_faq_id["FaqID"]
            new_faq_id += 1
        query = req["QueryString"]
        faqs.insert_one({"CharityID": cid, "EventID": eid, "FaqID" : new_faq_id, "QueryOwnerID": uid,  "QueryString": query, "Replies" : []})
        return "New FAQ Query added with FaqID %s"%(new_faq_id), 201


api.add_resource(createFAQ, '/charity/event/initThread')

# ------------------------------------------------------

# Adding replies to existing thread

class replyFAQ(Resource):
    def post(self):
        '''
        Expected json format:
        {
            "CharityID": 1, 
            "EventID":  "12",
            "FaqID": 3,
            "ReplyString": "No, participants are kindly requested to bring their own refreshments.",
            "UserID": 54
        }
        *** Changes required: UserID of the collaborators to be added to the collaborators sub-collection of events collection
        '''
        req = eval(request.data)
        cid = req["CharityID"]
        eid = req["EventID"]
        fid = req["FaqID"]
        uid = req["UserID"]
        faqs = db["faqs"]
        # Check if corresponding charity, event IDs and FAQ IDs exist
        faq = faqs.find_one({"CharityID": cid, "EventID": eid, "FaqID":fid})
        if(faq == None):
            return "There is no FAQ ID %s and event ID %s for charity ID %s in DB"%(fid, eid, cid), 404
        # Check if answer is by event coordinator. If yes, then mark reply as highlighted answer
        event = db["events"].find_one({"CharityID": cid, "EventID": eid})
        is_answer = 0
        if(any(d["UserID"] == uid for d in event['Coordinators'])):
            is_answer = 1
        print("faq[Replies] IS: ", faq["Replies"])
        # Check if any replies exist for this event. If yes, get max value of ++ReplyID as new ReplyID
        if(len(faq["Replies"]) == 0):
            new_reply_id = 0
        else:
            seq = [x["ReplyID"] for x in faq["Replies"]]
            new_reply_id = max(seq) + 1
        reply = req["ReplyString"]
        new_replies = faq["Replies"]
        new_replies.append({"ReplyID": new_reply_id, "ReplyString": reply, "isAnswer" : is_answer, "Replier": uid})
        faqs.update_one({"CharityID": cid, "EventID": eid, "FaqID":fid}, {"$set" : {"Replies" : new_replies}})
        return "New reply added with ReplyID %s"%(new_reply_id), 201

api.add_resource(replyFAQ, '/charity/event/replyThread')

# ------------------------------------------------------

# Modifying/deleting replies to existing thread

class modifyFAQ(Resource):
    def put(self):
        '''
        Expected json format:
        {
            "CharityID": 1, 
            "EventID":  "12",
            "FaqID": 3,
            "ReplyString": "No, participants are kindly requested to bring their own refreshments.",
            "ReplyID": 4,
            "UserID" : 23
        }
        if replyID == -1, replyString will contain replacement value for QueryString
        '''
        req = eval(request.data)
        cid = req["CharityID"]
        eid = req["EventID"]
        fid = req["FaqID"]
        rid = req["ReplyID"]
        new_reply = req["ReplyString"]
        faqs = db["faqs"]
        # Check if corresponding charity, event IDs and FAQ IDs exist
        faq = faqs.find_one({"CharityID": cid, "EventID": eid, "FaqID":fid})
        if(faq == None):
            return "There is no FAQ ID %s and event ID %s for charity ID %s in DB"%(fid, eid, cid), 404

        else:
            if(rid != -1):
                modified_reply = faq["Replies"]
                flag = 0
                for i in range(len(modified_reply)):
                    if(modified_reply[i]["ReplyID"] == rid):
                        modified_reply[i]["ReplyString"] = new_reply
                        flag = 1
                if(flag):
                    faqs.update_one({"CharityID": cid, "EventID": eid, "FaqID":fid}, {'$set': {"Replies" : modified_reply}})        
                    return "Reply modified", 200
                else:
                    return "There is no reply ID %s for FAQ ID %s,event ID %s and charity ID %s in DB"%(rid, fid, eid, cid), 404
            else:
                faqs.update_one({"CharityID": cid, "EventID": eid, "FaqID":fid}, {'$set':{"QueryString" : new_reply}})
                return "Updated", 200
    def delete(self):
        '''
        Expected json format: 
        {
            "CharityID": 1, 
            "EventID":  "12",
            "FaqID": 3,
            "ReplyID": 4,
            "DeleteThread": 0
        }

        DeleteThread = 0 if only the specified reply is to be deleted. Else DeleteThread = 1, and ReplyID sent as -1
        '''
        req = eval(request.data)
        cid = req["CharityID"]
        eid = req["EventID"]
        fid = req["FaqID"]
        rid = req["ReplyID"]
        isDelete = req["DeleteThread"]
        faqs = db["faqs"]
        # Check if corresponding charity, event IDs and FAQ IDs exist
        faq = faqs.find_one({"CharityID": cid, "EventID": eid, "FaqID":fid})
        if(faq == None):
            return "There is no FAQ ID %s and event ID %s for charity ID %s in DB"%(fid, eid, cid), 404
        else:
            if(isDelete):
                faqs.delete_one({"CharityID": cid, "EventID": eid, "FaqID": fid})
                return "Thread succesfully deleted", 200
            else:
                new_replies = faq["Replies"]
                for i in range(len(new_replies)):
                    if(new_replies[i]["ReplyID"] == rid):
                        new_replies.remove(new_replies[i])
                        faqs.update_one({"CharityID": cid, "EventID": eid, "FaqID": fid}, {"$set" : {"Replies": new_replies}})
                        return "Reply succesfully deleted", 200

                return "There is no Reply ID %s for FAQ ID %s,event ID %s and charity ID %s in DB"%(rid,fid, eid, cid), 404
                    
        

api.add_resource(modifyFAQ, '/charity/event/modifyFAQ')
# ------------------------------------------------------


# Get full thread

class getFAQ(Resource):
    def get(self):
        '''
        Expected json format:
        {
            "CharityID": 1, 
            "EventID":  "12",
            "FaqID": 3,
        }

        returned json format:
        {
            "Query": 
                    {
                        "content": "Will participants recieve certificates for finishing event?",
                        "owner": 23
                    }
            "Replies":
                    [
                        {
                            "content" : "Yes, they will! Register soon!",
                            "owner": 25
                            "isAnswer": 1
                        },
                        {
                            "content" : "I wanted to know this as well, please do reply coordinators!",
                            "owner": 29
                            "isAnswer": 0
                        }
                    ]
        }

        '''
        req = eval(request.data)
        cid = req["CharityID"]
        eid = req["EventID"]
        fid = req["FaqID"]
        faqs = db["faqs"]

        # Check if corresponding charity, event IDs and FAQ IDs exist
        faq = faqs.find_one({"CharityID": cid, "EventID": eid, "FaqID":fid})
        if(faq == None):
            return "There is no FAQ ID %s and event ID %s for charity ID %s in DB"%(fid, eid, cid), 404
        else:
            ret_val = {}
            ret_val["Query"] = {"content": faq["QueryString"], "owner": faq["QueryOwnerID"]}
            ret_val["Replies"] = []
            
            for i in faq["Replies"]:
                ret_val["Replies"].append({"content": i["ReplyString"], "owner": i["Replier"], "isAnswer": i["isAnswer"]})
            return ret_val, 200

            


api.add_resource(getFAQ, '/charity/event/getFAQ')

# ------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)

# ------------------------------------------------------
