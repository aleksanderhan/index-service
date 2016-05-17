from __future__ import print_function
from database_api import DatabaseAPI
from index_service import IndexService, Indexer, Parser
import multiprocessing as mp
from twisted.web import server, resource
from twisted.internet import reactor
import requests
import json
import config

        
class DatabaseAPI_test:
    ''' 
    Test class for database_api.py. The functions _make_connection() and _close_connection() 
    are implicitly tested when the other functions are tested. 
    '''

    def set_up(self):
        self.index = DatabaseAPI(config.db_host, config.db_port,
                                 config.db_name, config.db_user, config.db_pass)
        self.passed_tests = 0
        self.failed_tests = 0

    # Making a table, inserting a few items, querying the database for said item.
    # Explicitly tests make_table(), upsert() and query() togheter, in database_API.py.
    # Implicitly tests _make_connection() and _close_connection() in database_API.py.
    def test_routine1(self):
        print("Test 1: ",end='')
        self.index.make_tables('wordfreq', {"articleid" : "VARCHAR", "word" : "VARCHAR", "frequency" : "INTEGER"}, "(articleid, word)")
        self.index.upsert(table_name='wordfreq', article_id='test1', values=[('test_word1', 1), ('test_word2', 2)])
        query_data = self.index.query("SELECT articleid, word, frequency FROM wordfreq WHERE word = 'test_word2';")
        if query_data[0][0] == 'test1' and query_data[0][1] == 'test_word2' and query_data[0][2] == 2:
            self.passed_tests += 1
            print('pass')
        else:
            self.failed_tests += 1
            print('failed')

    # More or less the same as test_routine1(), but now also tests remove().
    # Explicitly tests make_table(), upsert(), query() and remove() in database_API.py.
    # Implicitly tests _make_connection() and _close_connection() in database_API.py.
    def test_routine2(self):
        print("Test 2: ", end='')
        self.index.make_tables('wordfreq', {"articleid" : "VARCHAR", "word" : "VARCHAR", "frequency" : "INTEGER"}, "(articleid, word)")
        self.index.upsert(table_name='wordfreq', article_id='test2', values=[('test_word', 1)])
        self.index.remove('wordfreq', 'articleid', 'test2')
        query_data = self.index.query("SELECT articleid, word, frequency FROM wordfreq WHERE articleid = 'test2';")
        if query_data == []:
            self.passed_tests += 1
            print('pass')
        else:
            self.failed_tests += 1
            print('failed')

    # Tests if upsert() updates values correctly.
    def test_routine3(self):
        print("Test 3: ", end='')
        self.index.make_tables('wordfreq', {"articleid" : "VARCHAR", "word" : "VARCHAR", "frequency" : "INTEGER"}, "(articleid, word)")
        self.index.upsert(table_name='wordfreq', article_id='test3', values=[('test_word', 1)])
        self.index.upsert(table_name='wordfreq', article_id='test3', values=[('test_word', 5)])
        query_data = self.index.query("SELECT articleid, word, frequency FROM wordfreq WHERE articleid = 'test3';")
        if query_data[0][2] == 5:
            self.passed_tests += 1
            print('pass')
        else:
            self.failed_tests += 1
            print('failed')

    def run_tests(self):
        print('Testing DatabaseAPI:')
        self.set_up()
        self.test_routine1()
        self.test_routine2()
        self.test_routine3()

    def print_results(self):
        print("DatabaseAPI test results:")
        print("Passed", self.passed_tests, "out of", self.passed_tests + self.failed_tests, "tests.")


class Parser_test:
    '''
    Test class for the Parser class in index_service.py.
    '''

    def set_up(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.html = '''
                    <!DOCTYPE html>
                    <html lang="en" style="font-family: Verdana">
                        <head>
                            <meta charset="UTF-8">
                      
                            <title>
                                title
                            </title>
                        </head>
                        <body>

                            <p>
                                text
                            </p>
                            <div>
                                ignore
                            </div>

                        </body>
                    </html>
                    '''
        self.parser = Parser(['div'])

    # Tests if the Parser ingores the right tags.
    def test1(self):
        print('Test 1: ', end='')
        self.set_up()
        self.parser.feed(self.html)
        content = set(self.parser.get_content())
        self.parser.close()
        if 'ignore' in content:
            self.failed_tests += 1
            print('failed')
        elif 'title' in content and 'text' in content:
            self.passed_tests += 1
            print('pass')
        else:
            self.failed_tests += 1
            print('failed')

    def run_tests(self):
        print("Testing Parser:")
        self.test1()

    def print_results(self):
        print("Parser test results:")
        print("Passed", self.passed_tests, "out of", self.passed_tests + self.failed_tests, "tests.")


class Indexer_test:
    '''
    Test class for the Indexer class in index_service.py.
    '''

    def set_up(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.indexer = Indexer(config.stopword_file_path, ['h1'])

    # Tests if the Indexer makes the correct index for sample page.
    def test1(self):
        print('Test 1: ', end='')
        url = 'http://folk.ntnu.no/alekh/it2805/index.html'
        index = dict(self.indexer.make_index(url))
        correct_result = {'it2805' : 1, 'prosjekt' : 1, 'to' : 11, 'link' : 11, 'homework' : 11}
        for k, v in correct_result.items():
            if index[k] != v:
                self.failed_tests += 1
                print('failed')
                return
        self.passed_tests += 1
        print('pass')

    def run_tests(self):
        print("Testing Indexer:")
        self.set_up()
        self.test1()

    def print_results(self):
        print("Indexer test results:")
        print("Passed", self.passed_tests, "out of", self.passed_tests + self.failed_tests, "tests.")


class IndexService_test:
    '''
    Test class for the IndexService class in index_service.py.
    '''

    def set_up(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.index = IndexService()
        reactor.listenTCP(8002, server.Site(PublishTestServer()))
        self.test_publish_server_thread = mp.Process(target=reactor.run)
        self.test_publish_server_thread.start()
        self.test_index_service_thread = mp.Process(target=self.index.run_as_daemon, args=(8001, True))
        self.test_index_service_thread.start()
        #self.test_publish_server_thread.join()
        #self.test_index_service_thread.join()

    def init(self):
        self.index.index_database.make_tables("wordfreq", {"articleid" : "VARCHAR", "word" : "VARCHAR", "frequency" : "INTEGER"}, "(articleid, word)")
        self.index.index_all_articles('http://127.0.0.1:8002', unit_test=True)

    # Tests if if the IndexService indexes all articles from a given publish service. Implicitly tests index_articles() too.
    def test1(self):
        self.init()
        query_data1 = dict(self.index.index_database.query("SELECT word, frequency FROM wordfreq WHERE articleid = 'test1';"))
        correct_result1 = {'it2805' : 2, 'prosjekt' : 1, 'to' : 11, 'link' : 11, 'homework' : 11, 'web' : 1, 'course' : 1, 'asd' : None}
        print("Test 1: ", end='')
        for k, v in correct_result1.items():
            if query_data1.get(k) != v:
                self.failed_tests += 1
                print('failed')
                return
        query_data2 = dict(self.index.index_database.query("SELECT word, frequency FROM wordfreq WHERE articleid = 'test2';"))
        correct_result2 = {'it2805' : None, 'site' : 1, 'tabels' : 1, 'links' : 1, 'homework' : 1, 'assignment' : 1, 'course' : None}
        for k, v in correct_result2.items():
            if query_data2.get(k) != v:
                self.failed_tests += 1
                print('failed')
                return
        self.passed_tests += 1
        print('pass')

    # Testing render_post() with task getSuggestions.
    def test2(self):
        self.init()
        r = requests.post('http://127.0.0.1:8001', data = json.dumps({'task' : 'getSuggestions', 'word' : 'lin'}))
        correct_result =set(['link', 'links'])
        print("Test 2: ", end='')
        for s in r.json()['suggestions']:
            if s not in correct_result:
                self.failed_tests += 1
                print('failed')
                return
        self.passed_tests += 1
        print('pass')

    # Testing render_post() with task getArticles.
    def test3(self):
        self.init()
        r = requests.post('http://127.0.0.1:8001', data = json.dumps({'task' : 'getArticles', 'word' : 'coding'}))
        print("Test 3: ", end='')
        if r.json()['articleID'] == ['test2']:
            self.passed_tests += 1
            print('pass')
        else:
            self.failed_tests += 1

    # Testing render_post() with task getFrequencyList.
    def test4(self):
        self.init()
        r = requests.post('http://127.0.0.1:8001', data = json.dumps({'task' : 'getFrequencyList'}))
        results = r.json()
        correct_result = {'homework' : 12, 'course' : 1, 'link' : 11, 'links' : 1, 'it2805' : 2, 'to' : 11, 'html' : 1}
        print('Test 4: ', end='')
        for k, v in correct_result.items():
            if results.get(k) != v:
                self.failed_tests += 1
                print('failed')
                return
        self.passed_tests += 1
        print('pass')

    '''
    # Testing render_post() with task publishedArticle.
    def test5(self):
        self.index.index_database.make_tables("wordfreq", {"articleid" : "VARCHAR", "word" : "VARCHAR", "frequency" : "INTEGER"}, "(articleid, word)")
        r = requests.post('http://127.0.0.1:8001', data = json.dumps({'task' : 'publishedArticle' 'articleID' : 'http://folk.ntnu.no/alekh/it2805/index.html'}))

    # Testing render_post() with task removedArticle.
    def test6(self):
        self.init()
    '''

    def run_tests(self):
        print("Testing IndexService:")
        self.set_up()
        self.test1()
        self.test2()
        self.test3()
        self.test4()
        # No need for further testing since the other functions are implicitly tested.
        #self.test5() 
        #self.test6()
        self.test_publish_server_thread.terminate()
        self.test_index_service_thread.terminate()

    def print_results(self):
        print('IndexService test results:')
        print("Passed", self.passed_tests, "out of", self.passed_tests + self.failed_tests, "tests.")


class PublishTestServer(resource.Resource):
    '''
    Publish test server for serving get requests from IndexService_test.
    '''

    isLeaf = True

    def render_GET(self, request):
        return json.dumps({"list": [{"id" : "http://folk.ntnu.no/alekh/it2805/index.html", "title" : "test1"}, {"id" : "http://folk.ntnu.no/alekh/it2805/02/index.html", "title" : "test2"}]})


if __name__ == "__main__":
    database_test = DatabaseAPI_test()
    database_test.run_tests()
    print()
    parser_test = Parser_test()
    parser_test.run_tests()
    print()
    indexer_test = Indexer_test()
    indexer_test.run_tests()
    print()
    index_service_test = IndexService_test()
    index_service_test.run_tests()
    print()
    database_test.print_results()
    parser_test.print_results()
    indexer_test.print_results()
    index_service_test.print_results()

    
'''
DatabaseAPI test results:
Passed 3 out of 3 tests.
Parser test results:
Passed 1 out of 1 tests.
Indexer test results:
Passed 1 out of 1 tests.
IndexService test results:
Passed 4 out of 4 tests.
'''



