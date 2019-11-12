from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.charity_agg

# for events
events = db["events"]
event = {"CharityID": 2, "EventID" : "15",
         "EventName": "Dog Pet Fest",
         "Date": "Mon Oct 28 2019 10:28:35 GMT+0530 (IST)",
         "LocationLink": "https://goo.gl/maps/pH8x2uzg23oTwnzV6",
         "Description": "Pet all the Doggos", "Location": "HAL",
         "Coordinators": [{"Name": "Nandoz", "Contact": "9123457362"},
                            {"Name": "Malaika", "Contact": "9148244234"}],
         "tags": ["Doggies", "Cute", "PetFest"]
         }

events.insert(event)


