from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.charity_agg

# for events
events = db["events"]
event = {"CharityID": 1, "EventID" : "12",
         "EventName": "Dog Pet Fest",
         "Date": "Tue Sep 17 2019 18:35:55 GMT+0530 (IST)",
         "LocationLink": "https://goo.gl/maps/pH8x2uzg23oTwnzV6",
         "Description": "Pet all the Doggos", "Location": "HAL",
         "Coordinators": [{"Name": "Nandoz", "Contact": "9123457362"},
                            {"Name": "Malaika", "Contact": "9148244234"}],
         "tags": ["Doggies", "Cute", "PetFest"]
         }

events.insert(event)

# for charities
charities = db["charities"]

# for users
users = db["users"]

