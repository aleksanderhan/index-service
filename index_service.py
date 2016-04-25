# -*- coding: utf-8 -*-

from __future__ import print_function
from HTMLParser import HTMLParser
from twisted.web import server
from twisted.web.resource import Resource
from twisted.web.client import Agent
from twisted.internet.defer import Deferred
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from database_api import DatabaseAPI
import urllib, codecs
import json
import re
import sys


class IndexService(Resource):
    """ 
    Index microservice class 
    """

    isLeaf = True

    def __init__(self, kwargs):
        Resource.__init__(self)
        self.content_module_name = kwargs['content_module_name']
        self.is_daemon = kwargs['daemon']
        self.index = DatabaseAPI(**kwargs)
        self.indexer = Indexer(**kwargs)

        if not self.is_daemon:
            self.startup_routine()
        else:
            self.run_as_daemon(8001)

    def run_as_daemon(self, port):
        self.index_all_articles()
        print("Starting the indexer as a daemon listening to port %d..." % port)
        reactor.listenTCP(port, server.Site(self))
        reactor.run()

    # Asks the user for some questions at startup.
    def startup_routine(self):
        indexContent = False
        yes = set(['', 'Y', 'y', 'Yes', 'yes', 'YES'])
        no = set(['N', 'n', 'No', 'no', 'NO'])
        index_on_startup = False
        print("Type 'help' for help.")
        while True:
            print(">> ", end="")
            user_input = str(raw_input())
            if user_input == 'help': # Print available commands to user.
                print()
                print("         <command>   -       <description>")
                print("         help        -       Help.")
                print("         reset       -       Reset index database.")
                print("         init        -       Index all articles from content service on startup.")
                print("         start       -       Start service.")
                print("         exit        -       Quit.")
                print()
            elif user_input == 'reset': # Clearing tables in the index database.
                print("This will delete any existing data and reset the database.")
                print("Are you sure you want to continue? [Y/n] ", end="")
                while True:
                    user_input = str(raw_input())
                    if user_input in yes:
                        self.index.make_tables()
                        print("Reset.")
                        break
                    else:
                        print("Abort.")
                        break
            elif user_input == 'init': # Toggle on/off indexing on startup.
                while True:
                    print("Do you want to index all the articles on startup? [Y/n] ", end="") 
                    user_input = str(raw_input())
                    if user_input in yes:
                        index_on_startup = True
                        print("Indexing will begin on start.")
                        break
                    elif user_input in no:
                        print("Indexing will not begin on start.")
                        index_on_startup = False
                        break
                    else:
                        print("Abort.")
                        break
            elif user_input == 'start': # Start indexing service.
                print("Starting index service. Use Ctrl + c to quit.")
                if index_on_startup:
                    self.index_all_articles()
                reactor.listenTCP(8001, server.Site(self))
                reactor.run()
                break
            elif user_input == 'exit': # End program.
                break
            elif user_input == '': # Yes is default on return.
                continue
            else:
                print(user_input + ": command not found")
                continue

    # Indexes all articles from the content microservice.
    def index_all_articles(self):
        # **** TODO: dont index already indexed articles ****
        #host = 'http://127.0.0.1:8002'  # content host - **** TODO: fetched from dht node network ****
        publish_host = self.get_service_ip(self.content_module_name) + "/list"
        agent = Agent(reactor) 
        d = agent.request("GET", publish_host)
        d.addCallback(self._cbRequestIndex)

    # Callback request.
    def _cbRequestIndex(self, response):
        finished = Deferred()
        finished.addCallback(self._index_content)
        response.deliverBody(RequestClient(finished))

    # Callback for _cbRequest. Indexes the articles in the GET response.
    def _index_content(self, response):
        print(response)
        article_id_list = json.loads(response)['list']
        total = len(article_id_list)
        for i in range(total):
            sys.stdout.write('\r')
            sys.stdout.write("Indexing article {i} of {total}.".format(i=i+1, total=total))
            sys.stdout.flush()
            article_id = article_id_list[i]['id']
            self.index_article(article_id)
        print("\nIndexing completed.")

    # Temporary fuction to fetch a services address. Should connect with the dht node somehow.
    def get_service_ip(self, service_name):        
        return "http://despina.128.no:32785"
        
    # Indexes page.
    def index_article(self, article_id):
        host = self.get_service_ip(self.content_module_name)
        url = host+'/article/'+article_id # Articles are found at: http://<publish_module_ip>:<port_num>/article/<article_id> 
        values = self.indexer.make_index(url)
        self.index.upsert(article_id, values)

    # Handles POST requests from the other microservices.
    def render_POST(self, request):
        d = json.load(request.content)
        if d['task'] == 'getSuggestions': # JSON format: {'task' : 'getSuggestions', 'word' : str}
            word_root = d['word']
            data = self.index.query("SELECT DISTINCT word FROM wordfreq WHERE word LIKE %s", (word_root+'%',))
            response = {"suggestions" : [t[0] for t in data]}
            return json.dumps(response)
        elif d['task'] == 'getArticles': # JSON format: {'task' : 'getArticles', 'word' : str}
            word = d['word']
            data = self.index.query("SELECT articleid FROM wordfreq WHERE word = %s", (word,))
            response = {"articleID" : [t[0] for t in data]}
            return json.dumps(response)
        elif d['task'] == 'getFrequencyList': # JSON format: {'task' : 'getFrequencyList'}
            data = self.index.query("SELECT word, sum(frequency) FROM wordfreq GROUP BY word")
            response = {}
            for value in data:
                response[value[0]] = value[1]
            return json.dumps(response)
        elif d['task'] == 'updatedArticle':
            article_id = d['articleID']
            self.index.remove(article_id)
            self.index_article(article_id)
            return 'thanks!'
        elif d['task'] == 'publishedArticle':
            article_id = d['articleID']
            self.index.upsert(article_id)
            return 'thanks!'
        elif d['task'] == 'removedArticle':
            article_id = d['articleID']
            self.index.remove(article_id)
            return('ok!')
        else:
            return('404')


class RequestClient(Protocol):
    """ 
    Request Client 
    """

    def __init__(self, finished):
        self.finished = finished

    def dataReceived(self, data):
        self.data = data

    def connectionLost(self, reason):
        self.finished.callback(self.data)

   
class Indexer(object):
    """ 
    Basic indexer of HTML pages 
    """

    stopwords = None

    def __init__(self, stopword_file_path, **kwargs):
        self.kwargs = kwargs
        self.stopwords = set([''])
        # Reading in the stopword file:
        with codecs.open(stopword_file_path, encoding='utf-8') as f:
            for word in f:
                self.stopwords.add(unicode(word.strip()))

    # Takes an url as arguments and indexes the article at that url. Returns a list of tuple values.
    def make_index(self, url):
        # Retriving the HTML source from the url:
        page = urllib.urlopen(url).read().decode('utf-8')

        # Parseing the HTML:
        parser = Parser(**self.kwargs)
        parser.feed(page)
        content = parser.get_content()
        parser.close()

        # Removing stopwords:
        unique_words = set(content).difference(self.stopwords)

        # Making a list of tuples: (word, wordfreq):
        values = []
        for word in unique_words:
            values.append((word, content.count(word)))
        return values


class Parser(HTMLParser):   
    """ 
    Basic parser for parsing of html data 
    """
    
    tags_to_ignore = set() # Add HTML tags to the set to ignore the data from that tag.

    def __init__(self, tags_to_ignore, **kwargs):
        HTMLParser.__init__(self)
        self.content = []
        self.tags_to_ignore = set(tags_to_ignore)
        self.ignore_tag = False  

    # Keeps track of which tags to ignore data from.
    def handle_starttag(self, tag, attrs):
        if tag in self.tags_to_ignore:
            self.ignore_tag = True
        else:
            self.ignore_tag = False
      
    # Handles data from tags.  
    def handle_data(self, data):
        if self.ignore_tag:
            return
        words = re.split("[ .,:;()!#¤%&=?+`´*_@£$<>^~/\[\]\{\}\-\"\']+", data)
        for word in words:
            if len(word) > 1:
                self.content.append(word.lower().strip())

    # Get method for content.
    def get_content(self):
        return self.content




