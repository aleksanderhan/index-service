#!/usr/bin/env python
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
import requests
import config
import urllib, codecs
import json
import re
import sys


class IndexService(Resource):
    """ 
    Index microservice class.
    """

    isLeaf = True

    def __init__(self):
        Resource.__init__(self)
        self.is_daemon = config.run_as_daemon
        self.index_database = DatabaseAPI(config.db_host, config.db_port,
                                 config.db_name, config.db_user, config.db_pass)
        self.indexer = Indexer(config.stopword_file_path, config.tags_to_ignore)

        if self.is_daemon:
            self.run_as_daemon(config.server_port)

    def run_as_daemon(self, port, unit_test=False):
        self.index_database.make_tables("wordfreq", {"articleid" : "VARCHAR", "word" : "VARCHAR", "frequency" : "INTEGER"}, "(articleid, word)")
        if not unit_test:
            host = self.get_service_ip(config.content_module_name)
            self.index_all_articles(host)
        print("\nStarting the indexer as a daemon listening to port %d..." % port)
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
                        self.index_database.make_tables("wordfreq", {"articleid" : "VARCHAR", "word" : "VARCHAR", "frequency" : "INTEGER"}, "(articleid, word)")
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
                    host = self.get_service_ip(config.content_module_name)
                    self.index_all_articles(host)
                reactor.listenTCP(config.server_port, server.Site(self))
                reactor.run()
                break
            elif user_input == 'exit': # End program.
                break
            elif user_input == '': # Yes is default on return.
                continue
            else:
                print(user_input + ": command not found")
                continue

    def index_all_articles(self, host, unit_test=False):
        publish_article_list = host + "/list"
        r = requests.get(publish_article_list)
        article_id_list = r.json()['list']
        total = len(article_id_list)
        for i in range(total):
            sys.stdout.write('\r')
            sys.stdout.write("Indexing article {i} of {total}.".format(i=i+1, total=total))
            sys.stdout.flush()
            article_id = article_id_list[i]['id']
            if unit_test:
                self.index_article(article_id_list[i]['title'], article_id)
            else:
                self.index_article(article_id)
        print("\nIndexing completed.")

    # Fetches the publish host address from the communication backend.
    def get_service_ip(self, service_name):
        try:
            r = requests.get(config.comm_host+service_name)
            url = r.json()
            if url:
                url = "http://" + url
        except:
            print('\nUsing hardcoded value for publish host ip.')
            url = 'http://despina.128.no/publish' # Hardcoded url for testing purposes.
        return url

    # Indexes page.
    def index_article(self, article_id, url=None):
        if url:
            values = self.indexer.make_index(url)
            self.index_database.upsert('wordfreq', article_id, values)
        else:
            host = self.get_service_ip(config.content_module_name)
            url = host + "/article/" + article_id # Articles should be found at: http://<publish_service_host>/article/<article_id> 
            values = self.indexer.make_index(url)
            self.index_database.upsert('wordfreq', article_id, values)

    # Handles POST requests from the other microservices.
    def render_POST(self, request):
        d = json.load(request.content)
        # Returns a list of suggestions of words with given word root:
        if d['task'] == 'getSuggestions': # JSON format: {'task' : 'getSuggestions', 'word' : str}
            word_root = d['word']
            data = self.index_database.query("SELECT DISTINCT word FROM wordfreq WHERE word LIKE %s", (word_root+'%',))
            response = {"suggestions" : [t[0] for t in data]}
            return json.dumps(response)
        # Returns all articles where given word occurs:
        elif d['task'] == 'getArticles': # JSON format: {'task' : 'getArticles', 'word' : str}
            word = d['word']
            data = self.index_database.query("SELECT articleid FROM wordfreq WHERE word = %s", (word,))
            response = {"articleID" : [t[0] for t in data]}
            return json.dumps(response)
        # Returns a list of all words and the total number of occurences of the words:
        elif d['task'] == 'getFrequencyList': # JSON format: {'task' : 'getFrequencyList'}
            data = self.index_database.query("SELECT word, sum(frequency) FROM wordfreq GROUP BY word")
            response = {}
            for value in data:
                response[value[0]] = value[1]
            return json.dumps(response)
        # Indexes published article with given id:
        elif d['task'] == 'publishedArticle':
            article_id = d['articleID']
            self.index_article(article_id)
            return '200 - thanks!'
        # Removes index of article with given id:
        elif d['task'] == 'removedArticle':
            article_id = d['articleID']
            self.index_database.remove(article_id)
            return('200 - ok!')
        else:
            return('404')

   
class Indexer(object):
    """ 
    Basic indexer of HTML pages.
    """

    def __init__(self, stopword_file_path, tags_to_ignore=config.tags_to_ignore):
        self.stopwords = set([''])
        self.tags_to_ignore = tags_to_ignore
        with codecs.open(stopword_file_path, encoding='utf-8') as f:
            for word in f:
                self.stopwords.add(unicode(word.strip()))

    # Takes an url as arguments and indexes the HTML page at that url. Returns a list of tuple values.
    def make_index(self, url):
        # Retriving the HTML source from the url.
        page = urllib.urlopen(url).read().decode('utf-8')

        # Parseing the HTML.
        parser = Parser(self.tags_to_ignore)
        parser.feed(page)
        content = parser.get_content()
        parser.close()

        # Removing stopwords.
        unique_words = set(content).difference(self.stopwords)

        # Making a list of tuples: (word, wordfreq).
        values = []
        for word in unique_words:
            values.append((word, content.count(word)))
        return values


class Parser(HTMLParser):   
    """ 
    Basic parser for parsing of html data.
    """

    def __init__(self, tags_to_ignore):
        HTMLParser.__init__(self)
        self.content = []
        self.tags_to_ignore = set(tags_to_ignore) # Add HTML tags to the set to ignore the data from that tag.
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


if __name__ == '__main__':
    index_service = IndexService()
    index_service.startup_routine()
