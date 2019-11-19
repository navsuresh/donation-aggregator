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
collection = db['charity_page']
calendar_collection = db['charity_calendar_widget'] 

# ------------------------------------------------------

# handles calendar widget requests
class calendarWidget(Resource):
    def get(self,cid): # when requesting calendar requests
        # un-comment when session is implemented
        '''
        if(session["logged_in"]==False): # not logged in
            return "Not logged in.",400

        if(session["logged_in_as"]=="charity" and session["cid"]!=cid): # not logged in as a charity
            return "The cid does not match logged_in id.",400
        '''
        c = calendar_collection.find_one({"cid": cid}); # format - {cid:id,caldata:[data_to_be_returned]}
        if(c==None): # check calendar events for requested cid
            return {},204
        else: # returning requested list
            return [eval(i) for i in c["caldata"]],200 # returns with format - [{"somedate": "content","type": "reminder"},{"somedate": "content","type": "reminder"}]    

    def post(self,cid): # when updating calender events
        # un-comment when session is implemented
        '''
        if(session["logged_in"]==False): # not logged in
            return "Not logged in.",400

        if(session["logged_in_as"]=="charity" and session["cid"]!=cid): # not logged in as a charity
            return "The cid does not match logged_in id.",400
        '''
        try:
            c = calendar_collection.find_one({"cid": cid}); # format - {cid:id,caldata[data_to_be_returned]}
            req = eval(request.data) # expecting json format (Ex - '{caldata:[data_to_be_added]}')
            if(c==None): # cid not present in DB, added new entry (Assuming logged in through sessions maintaining security)
                post = {"cid":cid, "caldata":[str(i) for i in req]}
                calendar_collection.insert_one(post)
                return "Success"
            else: # when the cid is present in the db
                updated = c["caldata"]
                updated.extend([str(i) for i in req]) # adding new data to prev data
                print(updated)
                myquery = { "cid": cid } # updating this cid
                newvalues = { "$set": { "caldata": updated} } # adding updated data
                calendar_collection.update_one(myquery, newvalues) # updating the collection
                return "Success"
        except:
            return "Failed",400
api.add_resource(calendarWidget, '/charity/<cid>/calendar')

# ------------------------------------------------------

# creates a document in the collection give the charity id
class initCharity_CharityPage(Resource):
    def post(self):

        req = eval(request.data) # expecting json format (Ex - '{"cid":731821}')
        cid = req["cid"] # cid could be different in final version

        if(collection.find_one({"cid": cid})!=None): # when cid is already present
            return "The cid %s is already present as a document"%(cid),400

        print(collection.find_one({"doc_type": "common"}))
        slot_count = collection.find_one({"doc_type": "common"})["slots_count"] # doc_type common used for getting common data for the collection
        post = {
            "cid": cid, # cid of the charity
            "slots": ["_empty" for _ in range(slot_count)] # slots of customisable homepage (_empty means nothing has been asigned to the slot)
        }
        post_id = collection.insert_one(post).inserted_id # ObjectId of the inserted document
        return "Charity document created in the charity_page collection with ObjectId - " + str(post_id),200

api.add_resource(initCharity_CharityPage, '/charity/<cid>/initCharity')

# ------------------------------------------------------

# recieve slot widget
class getWidget_CharityPage(Resource):
    def get(self, cid, slot_id): # slot id to return and cid of charity
        if(collection.find_one({"cid": cid})==None): # when cid is not present
            return "The cid %s is not present in the collection"%(cid),400
        slot_count = int(collection.find_one({"doc_type": "common"})["slots_count"]) # doc_type common used for getting common data for the collection
        
        if(str(slot_id).isdigit()==False or int(slot_id)>slot_count or int(slot_id)<1): # invalid slot_id
            return "The slot_id %s should be between 1 and %s (inclusive)"%(slot_id,slot_count),400
        slots = int(collection.find_one({"cid": str(cid)})["slots"]) # getting the slot ID
        return "Slot is widget "+str(slots[slot_id-1]),200 # -1 as 0 indexed (current return value is temp) 

api.add_resource(getWidget_CharityPage, '/charity/<cid>/widget/<slot_id>')

# ------------------------------------------------------

# update a slot
class updateSlot_CharityPage(Resource):
    def post(self, cid): # cid of the charity page
        # un-comment when session is implemented
        '''
        if(session["logged_in"]==False): # not logged in
            return "Not logged in.",400

        if(session["logged_in_as"]=="charity" and session["cid"]!=cid): # not logged in as a charity
            return "The cid does not match logged_in id.",400
        '''

        if(collection.find_one({"cid": cid})==None): # when cid is not present
            return "The cid %s is not present in the collection"%(cid),400

        req = eval(request.data) # expecting json format (Ex - '{"slot_id":1,"widget_id":2}')
        slot_id = req["slot_id"]
        widget_id = req["widget_id"]

        slot_count = int(collection.find_one({"doc_type": "common"})["slots_count"]) # doc_type common used for getting common data for the collection
        widget_count = int(collection.find_one({"doc_type": "common"})["widget_count"]) # doc_type common used for getting common data for the collection
        
        if(str(slot_id).isdigit()==False or int(slot_id)>slot_count or int(slot_id)<1): # invalid slot_id
            return "The slot_id %s should be between 1 and %s (inclusive)"%(slot_id,slot_count),400

        if(str(widget_id).isdigit()==False or int(widget_id)>widget_count or int(widget_id)<1): # invalid widget_id
            return "The widget_id %s should be between 1 and %s (inclusive)"%(widget_id,widget_count),400

        slots = collection.find_one({"cid": cid})["slots"]
        slots[int(slot_id)-1] = str(widget_id) # -1 for 0 indexing

        myquery = { "cid": cid } # updating this cid
        newvalues = { "$set": { "slots": slots} } # updating slots to the new value
        collection.update_one(myquery, newvalues) # updating the collection

        return "Charity document updated slot %s with new widget %s."%(slot_id, widget_id),200

api.add_resource(updateSlot_CharityPage, '/charity/<cid>/updateSlot')

# ------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)

# ------------------------------------------------------

# Potential changes
'''
1) req["cid"] in CreateCharityDocument could be different in final integration
2) session["logged_in"], session["logged_in_as"] and session["cid"] must be set with different names
3) In the charity collection there must be a docmument similar to {"doc_type":"common","slots_count":"5","widget_count":"10"}
4) req["slot_id"] and req["widget_id"] in updateSlot_CharityPage could be different in final integration
5) /charity<cid>/widget/<slot_id might change later by frontend people 
6) In calendarWidget the the format of the return value might change
7) Check calendar widget for error checks (i think its done)
'''

