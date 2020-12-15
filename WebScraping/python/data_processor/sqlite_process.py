import sqlite3
from sqlite3 import Error

class StoringData: 
    __instance = None

    @staticmethod 
    def getInstance():
      # Static access method.
      if StoringData.__instance == None:
         StoringData()
      return StoringData.__instance

    def __init__(self):  # init method or constructor   
        # Virtually private constructor.
        if StoringData.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            StoringData.__instance = self

    def create_connection(self, db_file):
        """ create a database connection to a SQLite database """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
           print("Failed to create connection ", e)

        return conn

    def create_table(self, conn, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = conn.cursor()
            print("Connected to database")
            c.execute(create_table_sql)

            c.close()
        except Error as e:
            print("Failed to create table ", e)
        finally:
            if (conn):
                conn.close()
                print("The Sqlite connection is closed")

    def check_to_create_table(self, db_file):
        sql_create_imdb_table = """CREATE TABLE IF NOT EXISTS IMDb (
                                        Id INTEGER PRIMARY KEY,
                                        Title TEXT,
                                        Release TEXT,
                                        Audience_Rating TEXT,
                                        Runtime TEXT,
                                        Genre TEXT,
                                        Imdb_Rating DECIMAL(1,1),
                                        Votes INTEGER,
                                        Director TEXT,
                                        Actors TEXT,
                                        Desc TEXT
                                    );"""

        # create a database connection
        conn = self.create_connection(db_file)

        # create tables
        if conn is not None:
            # create projects table
            self.create_table(conn, sql_create_imdb_table)
        else:
            print("Error! cannot create the database connection.")

    # If you want to pass arguments to the INSERT statement, you use the question mark (?) as the placeholder for each argument.
    def insert_data(self, conn, imdb):
        """
        Create a new imdb item into the IMDb table
        :param conn:
        :param imdb:
        :return: imdb id
        """
        sql = ''' INSERT INTO IMDb
                (
                    Title,
                    Release,
                    Audience_Rating,
                    Runtime,
                    Genre,
                    Imdb_Rating,
                    Votes,
                    Director,
                    Actors,
                    Desc
                )
                VALUES(
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?) '''

        cur = conn.cursor()
        cur.execute(sql, imdb)
        conn.commit()
        return cur.lastrowid