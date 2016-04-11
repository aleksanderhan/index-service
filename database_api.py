# -*- coding: utf-8 -*-
import psycopg2


""" PostgresSQL database API """
class DatabaseAPI:
    conn, cursor = None, None

    def __init__(self, host, port, dbname, user, password):
        self.conn_string = "host="+host+" port="+port+" dbname="+dbname+" user="+user+" password="+password

    # Calls to the function resets the database with a clean table.
    def make_tables(self):
        self._make_connection()
        self.cursor.execute("DROP TABLE IF EXISTS wordFreq")
        self.cursor.execute("CREATE TABLE wordFreq (url VARCHAR, word VARCHAR, frequency INTEGER, PRIMARY KEY (url, word))")
        self._close_connection()

    # Fuction for queries against the database. Takes a query string and if present a tuple with values and executes
    # the query, and returns the data.
    def query(self, query, values = None):
        self._make_connection()
        self.cursor.execute(query, values)
        data = self.cursor.fetchall()
        self._close_connection()
        return data

    # Inserts a list, values, with tuples of values into the database. On conflict update.
    def upsert(self, values):
        self._make_connection()
        if values:
            for value in values:
                insert_sql = self.cursor.mogrify("INSERT INTO wordFreq (url, word, frequency) SELECT %s, %s, %s", value)
                update_sql = self.cursor.mogrify("UPDATE wordFreq SET frequency = %s WHERE (url, word) = (%s, %s)", (value[2], value[0], value[1]))
                upsert_sql = "WITH upsert AS ("+update_sql+" RETURNING *) "+insert_sql+" WHERE NOT EXISTS (SELECT * FROM upsert)"
                self.cursor.execute(upsert_sql)
        else:
            print("no values to insert")
        self._close_connection()

    # Removes values with 'url'.
    def remove(self, url):
        self._make_connection()
        self.cursor.execute("DELETE FROM wordFreq WHERE (url) EQUALS (%s)", url)
        self._close_connection()
      
    # Starts psycopg2 connection to the postgres database. Must be run before any queries, inserts etc is to be done.
    def _make_connection(self):
        self.conn = psycopg2.connect(self.conn_string)
        self.cursor = self.conn.cursor()

    # Closes the connection that 'make_connection' makes. Must be run after any queries, inserts etc to be committed.
    def _close_connection(self):
        self.conn.commit()
        self.conn.close()
        self.cursor.close()

