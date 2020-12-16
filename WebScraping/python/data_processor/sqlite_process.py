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
                                        Key TEXT,
                                        Title TEXT,
                                        Release TEXT,
                                        Audience_Rating TEXT,
                                        Runtime TEXT,
                                        Genre TEXT,
                                        Imdb_Rating DECIMAL(1,1),
                                        Votes INTEGER,
                                        Director TEXT,
                                        Actors TEXT,
                                        Desc TEXT,
                                        Created_On TEXT,
                                        Modified_On TEXT
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
    def create_imdb(self, conn, imdb):
        """
        Create a new imdb item into the IMDb table
        :param conn:
        :param imdb:
        :return: imdb id
        """

        lastRowID = 0

        try:
            sql_insert_query = ''' INSERT INTO IMDb
                                    (
                                        Key, Title, Release, Audience_Rating, Runtime, Genre, Imdb_Rating, Votes, Director, Actors, Desc, Created_On, Modified_On
                                    )
                                    VALUES(
                                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                                '''

            # create a Cursor object by calling the cursor method of the Connection object.
            cur = conn.cursor()
            cur.execute(sql_insert_query, imdb)
            conn.commit()
            lastRowID = cur.lastrowid
        except Error as e:
            print("Error insert data from sqlite table", e)
        finally:
            cur.close()
        
        return lastRowID

    # Read imdb item by key
    def read_imdb(self, conn, key):
        """
        Read an imdb item 
        :param conn:
        :param imdb:
        :return: imdb item
        """
        imdb_item = None

        try:
            sql_select_query  = ''' SELECT Id, Key, Title, Release, Audience_Rating, Runtime, Genre, Imdb_Rating, Votes, Director, Actors, Desc, Created_On, Modified_On 
                                    FROM IMDb 
                                    WHERE Key = ?; '''

            # create a Cursor object by calling the cursor method of the Connection object.
            cur = conn.cursor()
            cur.execute(sql_select_query, [key])
            imdb_item = cur.fetchone()
        except Error as e:
            print("Error reading data from sqlite table", e)
        finally:
            cur.close()

        return imdb_item

    # If you want to pass arguments to the UPDATE statement, you use the question mark (?) as the placeholder for each argument.
    def update_imdb(self, conn, imdb):
        """
        Update an exist imdb item into the IMDb table
        :param conn:
        :param imdb:
        :return: imdb id
        """
        lastRowID = 0

        try:
            sql_update_query = ''' UPDATE IMDb 
                                    SET Key = ?,
                                        Title = ?,
                                        Release = ?,
                                        Audience_Rating = ?,
                                        Runtime = ?,
                                        Genre = ?,
                                        Imdb_Rating = ?,
                                        Votes = ?,
                                        Director = ?,
                                        Actors = ?,
                                        Desc = ?,
                                        Modified_On = ?
                                    WHERE Id = ?; '''

            # create a Cursor object by calling the cursor method of the Connection object.
            cur = conn.cursor()
            cur.execute(sql_update_query, (imdb[1], imdb[2], imdb[3], imdb[4], imdb[5], imdb[6], imdb[7], imdb[8], imdb[9], imdb[10], imdb[11], imdb[12], imdb[0],))
            conn.commit()
            lastRowID = cur.lastrowid
        except Error as e:
            print("Error update data from sqlite table", e)
        finally:
            cur.close()

        return lastRowID