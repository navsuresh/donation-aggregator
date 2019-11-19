from flask import Flask, jsonify, request, session 
from flask_restful import Resource, Api
import urllib3
from bs4 import BeautifulSoup
import datetime

app = Flask(__name__)
app.secret_key = 'i love white chocolate'
api = Api(app)

def clean(toclean, toremove):
    toclean = toclean.replace("<"+toremove+">","") # removing the opening tag
    toclean = toclean.replace("</"+toremove+">","") # removing the closing tag
    return toclean # returning cleaned string without tags 

class rssDisasters(Resource):
    def get(self):
        http = urllib3.PoolManager() 
        r = http.request('GET', 'https://www.gdacs.org/xml/rss.xml') # gdacs website provides rss for recent disasters
        content = BeautifulSoup(r.data)
        title = content.find_all("title") # title of the disaster
        description = content.find_all("description") # description of the disaster
        pubdate = content.find_all("pubdate") # published date (date of disaster)
        
        ret = []
        for i in range(1,len(title)): # started from 1 because first title tag is info about the rss not a disaster
            # clean the tags 
            t = clean(str(title[i]),"title") 
            d = clean(str(description[i]),"description")
            p = clean(str(pubdate[i]),"pubdate") 
            ret.append({"title":t,"description":d,"date":p}) # returning list of jsons to the front end
        strtodate = lambda item: datetime.datetime.strptime(item["date"],'%a, %d %b %Y %H:%M:%S %Z') # returning the converted string date to datetime object of item json
        ret = sorted(ret, reverse=True, key=strtodate) # sorting the distasters by lastest disatster
        return jsonify(ret) # list of disasters
api.add_resource(rssDisasters, '/rssDisasters')

if __name__ == '__main__':
    app.run(debug=True)
