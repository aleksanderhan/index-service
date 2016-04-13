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
import urllib, json
import codecs, re
import util


""" Index microservice class """
class IndexService(Resource):
    isLeaf = True

    def __init__(self, args):
        Resource.__init__(self)
        host, port = args['db_host'], args['db_port']
        dbname, user, password = args['db_name'], args['db_user'], args['db_pass']   
        stopword_file_path = args['stopword_file_path']
        self.index = DatabaseAPI(host, port, dbname, user, password)
        self.indexer = Indexer(stopword_file_path)
        self.index_on_startup = False
        self.startup_routine()

    # Asks the user for some questions at startup.
    def startup_routine(self):
        indexContent = False
        yes = set(['', 'Y', 'y', 'Yes', 'yes', 'YES'])
        no = set(['N', 'n', 'No', 'no', 'NO'])
        print("Type 'help' for help.")
        while True:
            print(">> ", end="")
            user_input = str(raw_input())
            # Print available commands to user.
            if user_input == 'help':
                print()
                print("         <command>   -       <description>")
                print("         help        -       Help.")
                print("         reset       -       Reset index database.")
                print("         init        -       Index all articles from content service on startup.")
                print("         start       -       Start service.")
                print("         exit        -       Quit.")
                print()
            # Clearing tables in the index database.
            elif user_input == 'reset':
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
            # Toggle on/off indexing on startup
            elif user_input == 'init':
                while True:
                    print("Do you want to index all the articles on startup? [Y/n] ", end="") 
                    user_input = str(raw_input())
                    if user_input in yes:
                        self.index_on_startup = True
                        print("Indexing will begin on start.")
                        break
                    elif user_input in no:
                        print("Indexing will not begin on start.")
                        self.index_on_startup = False
                        break
                    else:
                        print("Abort.")
                        break
            # Start indexing service
            elif user_input == 'start':
                print("Starting index service. Use Ctrl + c to quit.")
                if self.index_on_startup:
                    self.index_all_articles()
                reactor.listenTCP(8001, server.Site(self))
                reactor.run()
                break
            # End program.
            elif user_input == 'exit':
                break
            # Yes is default on return.
            elif user_input == '':
                continue
            else:
                print(user_input + ": command not found")
                continue

    # Indexes all articles from the content microservice.
    def index_all_articles(self):
        # **** TODO: dont index already indexed articles ****
        #host = 'http://127.0.0.1:8002'  # content host - **** TODO: fetched from dht node network ****
        host = self.get_service_ip('publish') + "/list"
        agent = Agent(reactor) 
        d = agent.request("GET", host)
        d.addCallback(self._cbRequest)

    # Callback request
    def _cbRequest(self, response):
        finished = Deferred()
        finished.addCallback(self._index_content)
        response.deliverBody(RequestClient(finished))

    # Callback for _cbRequest. Indexes the articles in the GET response.
    def _index_content(self, response):
        article_id_list = json.loads(response)['list']
        for i in range(len(article_id_list)):
            print("Indexing article ", i+1, " of ", len(article_id_list))
            article_id = article_id_list[i]['id']
            self.index_article(article_id)
        print("Indexing completed")

    # Indexes page.
    def index_article(self, article_id):
        host = self.get_service_ip('publish')
        url = host+'/article/'+article_id # Articles are found at: http://<publish_module_ip>:<port_num>/article/<article_id> 
        values = self.indexer.make_index(url)
        self.index.upsert(article_id, values)

    # Handles POST requests from the other microservices.
    def render_POST(self, request):
        d = json.load(request.content)
        # When suggestions for words are needed:
        if d['task'] == 'getSuggestions': # JSON format: {'task' : 'getSuggestions', 'word' : str}
            word_root = d['word']
            data = self.index.query("SELECT DISTINCT word FROM wordfreq WHERE word LIKE %s", (word_root+'%',))
            response = {"suggestions" : [t[0] for t in data]}
            return json.dumps(response)
        # When articles with a given word is needed:
        elif d['task'] == 'getArticles': # JSON format: {'task' : 'getArticles', 'word' : str}
            word = d['word']
            data = self.index.query("SELECT articleid FROM wordfreq WHERE word = %s", (word,))
            response = {"articleID" : [t[0] for t in data]}
            return json.dumps(response)
        # When the word frequency list is needed:
        elif d['task'] == 'getFrequencyList': # JSON format: {'task' : 'getFrequencyList'}
            data = self.index.query("SELECT word, sum(frequency) FROM wordfreq GROUP BY word")
            response = {}
            for value in data:
                response[value[0]] = value[1]
            return json.dumps(response)
        # When an article is updated:
        elif d['task'] == 'updatedArticle':
            article_id = d['articleID']
            self.index.remove(article_id)
            self.index.upsert(article_id)
            return 'thanks!'
        # When an article is published:
        elif d['task'] == 'publishedArticle':
            article_id = d['articleID']
            self.index.upsert(article_id)
            return 'thanks!'
        # When an article is removed:
        elif d['task'] == 'removedArticle':
            article_id = d['articleID']
            self.index.remove(article_id)
            return('ok!')
        else:
            return('404')

    # Temporary fuction to fetch a services address. Should connect with the dht node somehow
    def get_service_ip(self, service_name):
        return "http://despina.128.no/publish"


""" Request Client """
class RequestClient(Protocol):
    def __init__(self, finished):
        self.finished = finished

    def dataReceived(self, data):
        self.data = data

    def connectionLost(self, reason):
        self.finished.callback(self.data)  # Executes all registered callbacks.

   
""" Basic indexer of HTML pages """
class Indexer(object):
    stopwords = None

    def __init__(self, stopword_file_path):
        self.stopwords = set([''])
        # Reading in the stopword file:
        with codecs.open(stopword_file_path, encoding='utf-8') as f:
            for word in f:
                self.stopwords.add(unicode(word.strip()))

    # Takes an url as arguments and indexes the article at that url. Returns a list of tuple values.
    def make_index(self, url):
        # Retriving the HTML source from the url:
        '''
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        page = response.read() #.decode('UTF-8')
        response.close()
        '''
        page = urllib.urlopen(url).read().decode('utf-8')

        # Parseing the HTML:
        parser = Parser()
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


""" Basic parser for parsing of html data """
class Parser(HTMLParser):	
    tags_to_ignore = set(["script"]) # Add HTML tags to the set to ignore the data from that tag.

    def __init__(self):
        HTMLParser.__init__(self)
        self.content = []
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
        words = filter(None, re.split("[ .,:;()!#¤%&=?+`´*_@£$<>^~/\[\]\{\}\-\"\']+", data))
        for word in words:
            if len(word) > 1:
                self.content.append(word.lower().strip())

    # Get method for content.
    def get_content(self):
        return self.content




