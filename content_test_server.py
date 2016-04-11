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
