# -*- coding: utf-8 -*-
import psycopg2

""" PostgresSQL database API """
class DatabaseAPI:

    conn_string = None #"host='localhost' dbname='my_database' user='postgres' password='secret'"
    conn, cursor = None, None

    def __init__(self, host, dbname, user, password):
        self.conn_string = "host="+host+" dbname="+dbname+" user="+user+" password="+password

    def make_tables(self):
        self.make_connection()
        self.cursor.execute("DROP TABLE IF EXISTS wordFreq")
        self.cursor.execute("CREATE TABLE wordFreq (id serial PRIMARY KEY, url varchar, word varchar, frequency integer);")
        self.close_connection()

    def query(self, query):
        self.make_connection()
        self.cursor.execute(query)
        data = cursor.fetchall()
        self.close_connection()
        return data

    def insert(self, values):
        self.make_connection()
        for value in values:
            cursor.execute("INSERT INTO wordFreq (url, word, frequency) VALUES (%s, %s, %s)", value)
        self.close_connection()

    def remove(self, url):
        self.make_connection()
        self.cursor.execute("DELETE FROM wordFreq WHERE (url) EQUALS (%s)", url)
        self.close_connection()
        
    def make_connection(self):
        self.conn = psycopg2.connect(self.conn_string)
        self.cursor = conn.cursor()

    def close_connection(self):
        self.conn.commit()
        self.conn.close()
        self.cursor.close()

