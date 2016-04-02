# -*- coding: utf-8 -*-
from indexer import Indexer
from databaseAPI import DatabaseAPI
import sys
#import requests
from twisted.web import server, resource
from twisted.internet import reactor, endpoints

class Web_server(resource.Resource):
    isLeaf = True
    numberRequests = 0

    def render_GET(self, request):
        self.numberRequests += 1
        request.setHeader(b"content-type", b"text/plain")
        content = u"I am request #{}\n".format(self.numberRequests)
        return content.encode("ascii")




# Main
def main():
        
    test_url = "http://instabart.no/"

    indexer = Indexer("stopwords_norwegian.txt")
    index = DatabaseAPI('localhost', 'my_database', 'postgres', 'secret')

    #indexed_page = indexer.make_index(test_url)
    #for i in indexed_page:
    #   print(i)

    endpoints.serverFromString(reactor, "tcp:8080").listen(server.Site(Web_server()))
    reactor.run()


    while True:

        print("------------------------------------------")
        print("1. Initialize database")
        print("2. Retrive and index articles from content")
        print("3. Quit")
        print("------------------------------------------")

        user_input = int(input(">> "))
        if user_input == 1:
            pass
        if user_input == 2:
            pass
        if user_input == 3:
            reactor.stop()
            break

    





if __name__ == "__main__":
    main()