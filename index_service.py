# -*- coding: utf-8 -*-
from __future__ import print_function
from HTMLParser import HTMLParser
from twisted.web import server, resource
from twisted.web.client import Agent
from twisted.internet.defer import Deferred
from twisted.internet import reactor, protocol
from database_api import DatabaseAPI
import urllib2
import json


""" Index microservice class """
class IndexService(resource.Resource):
    isLeaf = True

    def __init__(self, host, port, dbname, user, password, stopword_file_path):
        self.index = DatabaseAPI(host, port, dbname, user, password)
        self.indexer = Indexer(stopword_file_path)
        self.startup_routine()
        reactor.listenTCP(8001, server.Site(self))
        reactor.run()

    # Asks the user for some questions at startup.
    def startup_routine(self):
        indexContent = False
        while True:
            print("Options:")
            print("1. Initialize database")
            print("2. Index all articles from content")
            print("3. Start service")
            print(">> ", end="")
            user_input = str(raw_input())
            if user_input == '1':
                self.initialize_database()   
            elif user_input == '2':
                self.index_all_articles()
            elif user_input == '3':
                print("Starting index service. Use Ctrl + c to quit.")
                break
            else:
                print("Option has to be a number between 1 and 3")
                continue

    # Creates new clean tables in the database.
    def initialize_database(self):
        yes = set(['Y', 'y', 'Yes', 'yes', 'YES'])
        no = set(['N', 'n', 'No', 'no', 'NO'])
        while True:
            print("This will delete any existing data and reset the database.")
            print("Are you sure you want to continue? [y]es/[n]o")
            print(">> ", end="")
            user_input = str(raw_input())
            if user_input in yes:
                self.index.make_tables()
                break
            elif user_input in no:
                break
            else:
                continue

    # Indexes all articles from the content microservice.
    def index_all_articles(self):
        # **** TODO: dont index already indexed articles ****
        #host = 'http://127.0.0.1:8002'  # content host - **** TODO: fetched from dht node network ****
        host = self.get_service_ip()

        agent = Agent(reactor) 
        d = agent.request("GET", host+"/list")
        d.addCallback(self._cbRequest)

    #
    def _cbRequest(self, response):
        finished = Deferred()
        finished.addCallback(self._index_content)
        response.deliverBody(RequestClient(finished))

    # Indexes the articles in the GET response.
    def _index_content(self, response):
        article_id_list = json.loads(response)['list']
        host = self.get_service_ip()
        for i in range(len(article_id_list)):
            print("Indexing article ", i+1, " of ", len(article_id_list))
            self.index_page(article_id_list[i]['id'])
        print("Indexing completed")


    # Indexes page at url.
    def index_page(self, article_id):
        host = self.get_service_ip()
        url = host+'/article/'+article_id
        values = self.indexer.make_index(url, article_id)
        self.index.upsert(values)

    # Handles POST requests from the Search microservice.
    def render_POST(self, request):
        print('you got mail')
        d = json.load(request.content)
        if d['task'] == 'getSuggestions': # JSON fromat: {'task' : 'getSuggestions', 'word' : str}
            print('getSuggestions')
            word_root = d['word']
            data = self.index.query("SELECT word FROM wordfreq WHERE word LIKE %s", (word_root+'%',))
            response = {"suggestions" : [t[0] for t in data]}
            return json.dumps(response)
        elif d['task'] == 'getArticles': # JSON format: {'task' : 'getArticles', 'word' : str}
            print('getArticles')
            word = d['word']
            data = self.index.query("SELECT url FROM wordfreq WHERE word = %s", (word,))
            response = {"articleID" : [t[0] for t in data]}
            return json.dumps(response)
        elif d['task'] == 'getFrequencyList': # JSON format: {'task' : 'getFrequencyList'}
            print('getFrequencyList')
            data = self.index.query("SELECT word, sum(frequency) FROM wordfreq GROUP BY word")
            response = {}
            for value in data:
                response[value[0]] = value[1]
            return json.dumps(response)
        else:
            return('404')

    def get_service_ip(self):
        return "http://despina.128.no/publish"

""" Request Client """
class RequestClient(protocol.Protocol):
    def __init__(self, finished):
        self.finished = finished

    def dataReceived(self, data):
        self.data = data

    def connectionLost(self, reason):
        self.finished.callback(self.data)  # Executes all registered callbacks.

   
""" Basic indexer of HTML pages """
class Indexer:
    stopwords = None

    def __init__(self, stopword_file_path):
        self.stopwords = set([''])

        # Reading in the stopword file:
        with open(stopword_file_path, 'r') as f:
            for word in f.readlines():
                self.stopwords.add(word.strip())

    # Takes an url as arguments and indexes the article at that url. Returns a list of tuple values.
    def make_index(self, url, articleID):
        # Retriving the HTML source from the url:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        page = str(response.read()) #.encode('utf-8'))
        response.close()

        # Parseing the HTML:
        parser = Parser()
        parser.feed(page)
        content = parser.get_content()
        parser.close()

        # Removing stopwords:
        unique_words = set(content).difference(self.stopwords)

        # Making a list of tuples: (url, word, wordfreq):
        values = []
        for word in unique_words:
            values.append((articleID, word, content.count(word)))

        return values


""" Basic parser for parsing of html data """
class Parser(HTMLParser):	
    content = []
    tags_to_ignore = set(["script"]) # Add HTML tags to the set to ignore the data from that tag.
    ignore_tag = False

    # Keeps track of which tags to ignore data from.
    def handle_starttag(self, tag, attrs):
        if tag in self.tags_to_ignore:
            self.ignore_tag = True
        else:
            self.ignore_tag = False
      
    # Handles data from tags.  
    def handle_data(self, data):
        if data.strip() == "" or self.ignore_tag:
            return

        for word in data.split():
            if word.strip() == "":
                continue
            self.content.append(word.lower().strip("'.,;:/&()=?!`´´}][{-_"))

    # Get method for content.
    def get_content(self):
        return self.content



