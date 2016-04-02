import psycopg2

class Database:

    conn_string = "host='localhost' dbname='my_database' user='postgres' password='secret'"

    def __init__(self):
        pass

    def make_tables():
        conn, cursor = self.make_connection()

        cursor.execute("DROP TABLE IF EXISTS title")
        cursor.execute("DROP TABLE IF EXISTS wordFreq")
        #cursor.execute("CREATE TABLE title (id serial PRIMARY KEY, num integer, data varchar);")
        #cursor.execute("CREATE TABLE wordFreq (id serial PRIMARY KEY, num integer, data varchar);")
        cursor.execute("CREATE TABLE title (id serial PRIMARY KEY, url varchar, title varchar);")
        cursor.execute("CREATE TABLE wordFreq (id serial PRIMARY KEY, word varchar, frequency integer);")

        conn.commit()
        conn.close()
        cursor.close()

    def query(query):
        conn, cursor = self.make_connection()
        cursor.execute(query)
        data = cursor.fetchall()

        conn.commit()
        conn.close()
        cursor.close()
        return data

    def insert(table, values):
        conn, cursor = self.make_connection()
        cursor.execute(statement)

        if table == "title":
            sstring = "(%s, %s)"
        if table == "wordFreq":
            sstring = "(%s, %s, %s)"

        SQL = cur.mogrify("INSERT INTO "+ title +" (url, title) VALUES "+ sstring, values)
        cursor.execute(SQL)

        conn.commit()
        conn.close()
        cursor.close()

    def update(statement):
        conn, cursor = self.make_connection()

        conn.commit()
        conn.close()
        cursor.close()

    def remove(statement):
        conn, cursor = self.make_connection()

        conn.commit()
        conn.close()
        cursor.close()

    def make_connection():
        conn = psycopg2.connect(self.conn_string)
        cursor = conn.cursor()
        return conn, cursor
