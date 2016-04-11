from twisted.web import server, resource
from twisted.internet import reactor
import json


class ContentTestServer(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
    	print("request recieved")
        return json.dumps({"list": [{"id": "http://instabart.no/", "title":"instabart"}]})


reactor.listenTCP(8002, server.Site(ContentTestServer()))
reactor.run()

'''
curl -i -H "Content-Type: application/json" -X POST -d '{"task" : "getSuggestions", "word" : "ta"}' 127.0.0.1:8001
curl -i -H "Content-Type: application/json" -X POST -d '{"task" : "getArticles", "word" : "ta"}' 127.0.0.1:8001
curl -i -H "Content-Type: application/json" -X POST -d '{"task" : "getFrequencyList"}' 127.0.0.1:8001
'''