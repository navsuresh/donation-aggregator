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
db = client['SE']
collection = db['user_page']
user_calendar_collection = db['user_calendar_widget'] 

# ------------------------------------------------------

# handles calendar widget requests
class calendarWidget_UserPage(Resource):
    def get(self,uid): # when requesting calendar requests
        # un-comment when session is implemented
        '''
        if(session["logged_in"]==False): # not logged in
            return "Not logged in.",400

        if(session["logged_in_as"]=="user" and session["uid"]!=uid): # not logged in as a user
            return "The uid does not match logged_in id.",400
        '''
        c = user_calendar_collection.find_one({"uid": uid}); # format - {uid:id,caldata:[data_to_be_returned]}
        if(c==None): # check calendar events for requested uid
            return {},204
        else: # returning requested list
            return [eval(i) for i in c["caldata"]],200 # returns with format - [{"somedate": "content","type": "reminder"},{"somedate": "content","type": "reminder"}]    

    def post(self,uid): # when updating calender events
        # un-comment when session is implemented
        '''
        if(session["logged_in"]==False): # not logged in
            return "Not logged in.",400

        if(session["logged_in_as"]=="user" and session["uid"]!=uid): # not logged in as a user
            return "The uid does not match logged_in id.",400
        '''
        try:
            c = user_calendar_collection.find_one({"uid": uid}); # format - {uid:id,caldata[data_to_be_returned]}
            req = eval(request.data) # expecting json format (Ex - '{caldata:[data_to_be_added]}')
            if(c==None): # uid not present in DB, added new entry (Assuming logged in through sessions maintaining security)
                post = {"uid":uid, "caldata":[str(i) for i in req]}
                user_calendar_collection.insert_one(post)
                return "Success"
            else: # when the uid is present in the db
                updated = c["caldata"]
                updated.extend([str(i) for i in req]) # adding new data to prev data
                print(updated)
                myquery = { "uid": uid } # updating this uid
                newvalues = { "$set": { "caldata": updated} } # adding updated data
                user_calendar_collection.update_one(myquery, newvalues) # updating the collection
                return "Success"
        except:
            return "Failed",400
api.add_resource(calendarWidget, '/user/<uid>/calendar')

# ------------------------------------------------------

# creates a document in the collection give the user id
class initUser_UserPage(Resource):
    def post(self):

        req = eval(request.data) # expecting json format (Ex - '{"uid":731821}')
        uid = req["uid"] # uid could be different in final version

        if(collection.find_one({"uid": uid})!=None): # when uid is already present
            return "The uid %s is already present as a document"%(uid),400

        print(collection.find_one({"doc_type": "common"}))
        slot_count = collection.find_one({"doc_type": "common"})["slots_count"] # doc_type common used for getting common data for the collection
        post = {
            "uid": uid, # uid of the user
            "slots": ["_empty" for _ in range(slot_count)] # slots of customisable homepage (_empty means nothing has been asigned to the slot)
        }
        post_id = collection.insert_one(post).inserted_id # ObjectId of the inserted document
        return "User document created in the user_page collection with ObjectId - " + str(post_id),200

api.add_resource(initUser_UserPage, '/user/<uid>/initUser')

# ------------------------------------------------------

# recieve slot widget
class getWidget_UserPage(Resource):
    def get(self, uid, slot_id): # slot id to return and uid of user
        if(collection.find_one({"uid": uid})==None): # when uid is not present
            return "The uid %s is not present in the collection"%(uid),400
        slot_count = int(collection.find_one({"doc_type": "common"})["slots_count"]) # doc_type common used for getting common data for the collection
        
        if(str(slot_id).isdigit()==False or int(slot_id)>slot_count or int(slot_id)<1): # invalid slot_id
            return "The slot_id %s should be between 1 and %s (inclusive)"%(slot_id,slot_count),400
        slots = int(collection.find_one({"uid": str(uid)})["slots"]) # getting the slot ID
        return "Slot is widget "+str(slots[slot_id-1]),200 # -1 as 0 indexed (current return value is temp) 

api.add_resource(getWidget_UserPage, '/user/<uid>/widget/<slot_id>')

# ------------------------------------------------------

# update a slot
class updateSlot_UserPage(Resource):
    def post(self, uid): # uid of the user page
        # un-comment when session is implemented
        '''
        if(session["logged_in"]==False): # not logged in
            return "Not logged in.",400

        if(session["logged_in_as"]=="user" and session["uid"]!=uid): # not logged in as a user
            return "The uid does not match logged_in id.",400
        '''

        if(collection.find_one({"uid": uid})==None): # when uid is not present
            return "The uid %s is not present in the collection"%(uid),400

        req = eval(request.data) # expecting json format (Ex - '{"slot_id":1,"widget_id":2}')
        slot_id = req["slot_id"]
        widget_id = req["widget_id"]

        slot_count = int(collection.find_one({"doc_type": "common"})["slots_count"]) # doc_type common used for getting common data for the collection
        widget_count = int(collection.find_one({"doc_type": "common"})["widget_count"]) # doc_type common used for getting common data for the collection
        
        if(str(slot_id).isdigit()==False or int(slot_id)>slot_count or int(slot_id)<1): # invalid slot_id
            return "The slot_id %s should be between 1 and %s (inclusive)"%(slot_id,slot_count),400

        if(str(widget_id).isdigit()==False or int(widget_id)>widget_count or int(widget_id)<1): # invalid widget_id
            return "The widget_id %s should be between 1 and %s (inclusive)"%(widget_id,widget_count),400

        slots = collection.find_one({"uid": uid})["slots"]
        slots[int(slot_id)-1] = str(widget_id) # -1 for 0 indexing

        myquery = { "uid": uid } # updating this uid
        newvalues = { "$set": { "slots": slots} } # updating slots to the new value
        collection.update_one(myquery, newvalues) # updating the collection

        return "User document updated slot %s with new widget %s."%(slot_id, widget_id),200

api.add_resource(updateSlot_UserPage, '/user/<uid>/updateSlot')

# ------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)

# ------------------------------------------------------

# Potential changes
'''
1) req["uid"] in CreateUserDocument could be different in final integration
2) session["logged_in"], session["logged_in_as"] and session["uid"] must be set with different names
3) In the User collection there must be a docmument similar to {"doc_type":"common","slots_count":"5","widget_count":"10"}
4) req["slot_id"] and req["widget_id"] in updateSlot_UserPage could be different in final integration
5) /User<uid>/widget/<slot_id might change later by frontend people 
6) In calendarWidget the the format of the return value might change
7) Check calendar widget for error checks (i think its done)
'''

