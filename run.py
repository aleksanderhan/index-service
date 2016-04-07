# -*- coding: utf-8 -*-
from indexer import Indexer
from databaseAPI import DatabaseAPI
from node_api import *
from twisted.web import server, resource
from twisted.internet import reactor
import json
import sys



class IndexQueries(resource.Resource):
    isLeaf = True
    def render_POST(self, request):
        d = json.load(request.content)
        print("Index received: {}".format(d))
        
        if not 'Partial' in d:
            result = "{'a':1, 'b':5, 'c':120}"
        
        elif d['Partial'] == True:
            word = d['Query']
            completions = ['{}_{}'.format(word,c) for c in ['c1', 'c2', 'c3']]
            result = "{'Result' : %s}" % (completions)
        else:
            word = d['Query']
            locations = ['{}'.format(L) for L in ['http://1', 'http://2', 'http://3']]
            result = "{'Result' : %s}" % (locations)
        print(result)
        #request.write(result)
        #request.finish()
        #return server.NOT_DONE_YET
        print "you got mail"
        return result



# Main
def main():
        
    test_url = "http://instabart.no/"

    stopword_file_path = "stopwords_norwegian.txt"

    #indexed_page = indexer.make_index(test_url)
    #for i in indexed_page:
    #   print(i)

    stopword_file_path = "stopwords_norwegian.txt"
    index = DatabaseAPI(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    indexer = Indexer(index, stopword_file_path)
    indexer.initialize_database()
    indexer.index_page(test_url)


    '''
    while True:

        print("------------------------------------------")
        print("1. Initialize database")
        print("2. Retrive and index articles from content")
        print("3. Start indexing service")
        print("------------------------------------------")

        user_input = int(input(">> "))
        if user_input == 1:
            stopword_file_path = "stopwords_norwegian.txt"
            index = DatabaseAPI(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
            indexer = Indexer(index, stopword_file_path)
            index.make_tables()
        if user_input == 2:
            pass
        if user_input == 3:
            break
    '''
            
            




if __name__ == "__main__":  
    main()
    #endpoints.serverFromString(reactor, "tcp:8080").listen(server.Site(Web_server()))
    #reactor.run()
    site = server.Site(IndexQueries())
    reactor.listenTCP(8050, site)
    reactor.run()