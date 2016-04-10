# -*- coding: utf-8 -*-
import psycopg2


""" PostgresSQL database API """
class DatabaseAPI:

    conn_string = None 
    conn, cursor = None, None

    def __init__(self, host, port, dbname, user, password):
        self.conn_string = "host="+host+" port="+port+" dbname="+dbname+" user="+user+" password="+password

    # Calls to the function resets the database with a clean table.
    def make_tables(self):
        self.make_connection()
        self.cursor.execute("DROP TABLE IF EXISTS wordFreq")
        self.cursor.execute("CREATE TABLE wordFreq (id serial PRIMARY KEY, url varchar, word varchar, frequency integer);")
        self.close_connection()

    # Fuction for queries against the database. Takes a query string and if present a tuple with values and executes
    # the query, and returns the data.
    def query(self, query, values=None):
        self.make_connection()
        self.cursor.execute(query, values)
        data = self.cursor.fetchall()
        self.close_connection()
        return data

    # Inserts a list, values, with tuples of values into the database.
    def insert(self, values):
        self.make_connection()
        for value in values:
            self.cursor.execute("INSERT INTO wordFreq (url, word, frequency) VALUES (%s, %s, %s)", value)
        self.close_connection()

    # Removes values with 'url'.
    def remove(self, url):
        self.make_connection()
        self.cursor.execute("DELETE FROM wordFreq WHERE (url) EQUALS (%s)", url)
        self.close_connection()
      
    # Starts psycopg2 connection to the postgres database. Must be run before any queries, inserts etc is to be done.
    def make_connection(self):
        self.conn = psycopg2.connect(self.conn_string)
        self.cursor = self.conn.cursor()

    # Closes the connection that 'make_connection' makes. Must be run after any queries, inserts etc to be committed.
    def close_connection(self):
        self.conn.commit()
        self.conn.close()
        self.cursor.close()

