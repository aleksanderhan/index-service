from __future__ import print_function
import unittest
from database_api import DatabaseAPI
from index_service import IndexService, Indexer, Parser
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

	def run_tests(self):
		print('Testing DatabaseAPI:')
		self.set_up()
		self.test_routine1()
		self.test_routine2()
		print("Passed", self.passed_tests, "out of", self.passed_tests + self.failed_tests)


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
		print("Passed", self.passed_tests, "out of", self.passed_tests + self.failed_tests)




class Indexer_test:
	'''
	Test class for the Indexer class in index_service.py.
	'''

	def set_up(self):
		self.passed_tests = 0
		self.failed_tests = 0

	def run_tests(self):
		print("Testing Indexer:")
		self.set_up()

		print("Passed", self.passed_tests, "out of", self.passed_tests + self.failed_tests)


class IndexService_test:
	'''
	Test class the IndexService class in index_service.py.
	'''

	def set_up(self):
		self.passed_tests = 0
		self.failed_tests = 0
		self.index = IndexService()
	
	def run_tests(self):
		print("Testing IndexService:")
		self.set_up()

		print("Passed", self.passed_tests, "out of", self.passed_tests + self.failed_tests)



if __name__ == "__main__":
	database_test = DatabaseAPI_test()
	database_test.run_tests()
	print()
	parser_test = Parser_test()
	parser_test.run_tests()
	



