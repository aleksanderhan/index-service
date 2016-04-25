# -*- coding: utf-8 -*-

import psycopg2


class DatabaseAPI(object):
    """ 
    PostgresSQL database API 
    """

    conn, cursor = None, None

    def __init__(self, db_host, db_port, db_name, db_user, db_pass):
        self.conn_string = "host="+db_host+" port="+db_port+" dbname="+db_name+" user="+db_user+" password="+db_pass

    # Calls to the function resets the database with a clean table.
    def make_tables(self):
        self._make_connection()
        self.cursor.execute("DROP TABLE IF EXISTS wordfreq")
        self.cursor.execute("CREATE TABLE wordFreq (articleid VARCHAR, word VARCHAR, frequency INTEGER, PRIMARY KEY (articleid, word))")
        self._close_connection()

    # Fuction for custom queries against the database. Takes a query string and if present a tuple with values and executes
    # the query, and returns the data.
    def query(self, query, values = None):
        self._make_connection()
        self.cursor.execute(query, values)
        data = self.cursor.fetchall()
        self._close_connection()
        return data

    # Inserts a list, values, with tuples of values into the database. On conflict update.
    def upsert(self, article_id, values):
        self._make_connection()
        if values:
            for value in values:
                word, freq = value[0], value[1]
                insert_sql = self.cursor.mogrify("INSERT INTO wordfreq (articleid, word, frequency) SELECT %s, %s, %s", (article_id, word, freq))
                update_sql = self.cursor.mogrify("UPDATE wordfreq SET frequency = %s WHERE (articleid, word) = (%s, %s)", (freq, article_id, word))
                upsert_sql = "WITH upsert AS ("+update_sql+" RETURNING *) "+insert_sql+" WHERE NOT EXISTS (SELECT * FROM upsert)"
                self.cursor.execute(upsert_sql)
        else:
            print("no values to insert")
        self._close_connection()

    # Removes values with 'url'.
    def remove(self, article_id):
        self._make_connection()
        self.cursor.execute("DELETE FROM wordfreq WHERE (articleid) = (%s)", (article_id,))
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

