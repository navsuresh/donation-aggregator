from flask import Flask, jsonify, request, session 
from flask_restful import Resource, Api
import urllib3
from bs4 import BeautifulSoup
import datetime

app = Flask(__name__)
app.secret_key = 'i love white chocolate'
api = Api(app)

def clean(toclean, toremove):
    toclean = toclean.replace("<"+toremove+">","")
    toclean = toclean.replace("</"+toremove+">","")
    return toclean

class rssDisasters(Resource):
    def get(self):
        http = urllib3.PoolManager()
        r = http.request('GET', 'https://www.gdacs.org/xml/rss.xml')
        content = BeautifulSoup(r.data)
        title = content.find_all("title")
        description = content.find_all("description")
        pubdate = content.find_all("pubdate")
        
        ret = []
        for i in range(1,len(title)):
            t = clean(str(title[i]),"title")
            d = clean(str(description[i]),"description")
            p = clean(str(pubdate[i]),"pubdate") 
            ret.append({"title":t,"description":d,"date":p})
        strtodate = lambda item: datetime.datetime.strptime(item["date"],'%a, %d %b %Y %H:%M:%S %Z')
        ret = sorted(ret, reverse=True, key=strtodate)
        return jsonify(ret)
api.add_resource(rssDisasters, '/rssDisasters')

if __name__ == '__main__':
    app.run(debug=True)
