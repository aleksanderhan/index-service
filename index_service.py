# -*- coding: utf-8 -*-
import urllib2
from HTMLParser import HTMLParser
from twisted.web import server, resource
from twisted.internet import reactor
from database_api import DatabaseAPI
import json



class IndexService(resource.Resource):

    isLeaf = True
    index = None
    indexer = None

    def __init__(self, host, port, dbname, user, password, stopword_file_path):
        self.index = DatabaseAPI(host, port, dbname, user, password)
        self.indexer = Indexer(stopword_file_path)
        self.startup_routine()
        
        reactor.listenTCP(8001, server.Site(self))
        reactor.run()

    # Handles POST requests
    def render_POST(self, request):
        d = json.load(request.content)
        if d['Partial'] == "True":
            return "not implemented yet"
        if d['Partial'] == "False":
            word = d['Query']
            print 'ayy'
            data = index.query("SELECT * FROM wordfreq WHERE word=(%s)", (word))
            print data
        else:
            print "you got mail"
            return 'result'

    def startup_routine(self):
        user_input = None
        while user_input != 3:
            print("Options:")
            print("1. Initialize database")
            print("2. Index all articles from content")
            print("3. Start service")
            print(">> ")
            try:
                user_input = int(input())
                if user_input == 1:
                    pass
                if user_input == 2:
                    pass
                if user_input == 3:
                    break
            except:
                print("Option has to be a number between 1 and 3")
                continue

    # Asks content service for all articles. Returns list of urls to articles.
    def get_all_articles():
        pass

    def initialize_database(self):
        self.index.make_tables()

    def index_page(self, url):
        self.index.insert(self.make_index(url))



""" Basic indexer of HTML pages """
class Indexer:

    stopwords = None

    def __init__(self, stopword_file_path):
        self.stopwords = set([''])

        # Reading in the stopword file
        with open(stopword_file_path, 'r') as f:
            for word in f.readlines():
                self.stopwords.add(word.strip())

    def make_index(self, url):
        # Retriving the HTML source from the url
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        page = str(response.read()) #.decode('utf-8'))
        response.close()

        # Parse the HTML
        parser = Parser()
        parser.feed(page)
        content = parser.get_content()
        parser.close()

        # Removing stopwords
        unique_words = set(content).difference(self.stopwords)

        # Making a list of tuples: (url, word, wordfreq)
        values = []
        for word in unique_words:
            values.append((url, word, content.count(word)))

        return values



"""Basic parser for parsing of html data"""
class Parser(HTMLParser):
	
    content = []
    tags_to_ignore = set(["script"]) # Add HTML tags to the set to ignore the data from that tag
    ignore_tag = False

    def handle_starttag(self, tag, attrs):
        if tag in self.tags_to_ignore:
            self.ignore_tag = True
        else:
            self.ignore_tag = False
        
    def handle_data(self, data):
        if data.strip() == "" or self.ignore_tag:
            return

        for word in data.split():
            if word.strip() == "":
                continue
            self.content.append(word.lower().strip("'.,;:/&()=?!`´´}][{-_"))

    def get_content(self):
        return self.content



