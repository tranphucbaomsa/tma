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
            # create a database connection
            conn = sqlite3.connect(db_file)

            self.__check_to_create_table(conn, db_file)
        except Error as e:
           print("Failed to create connection ", e)
           
        return conn


    def close_connection(self, conn):
        """ close current a database connection to a SQLite database """
        if (conn):
            conn.close()

    def __check_to_create_table(self, conn, db_file):
        """ check if not exist to create a table IMDb
        :param conn: Connection object
        :param db_file: database file path
        :return: 
        """

        # Created_On TEXT,
        # Modified_On TEXT
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
                                        Desc TEXT
                                    );"""

        try:
            cur = conn.cursor()
			
            #get the count of tables with the name
            cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='IMDb' ''')

            #if the count is 1, then table exists
            if cur.fetchone()[0]==0 : 
                # create IMDb table
                cur.execute(sql_create_imdb_table)
                
        except Error as e:
            print("Error create the database connection", e)
        finally:
            cur.close()

    # If you want to pass arguments to the INSERT statement, you use the question mark (?) as the placeholder for each argument.
    def create_imdb(self, conn, imdb):
        """
        Create a new imdb item into the IMDb table
        :param conn:
        :param imdb:
        :return: imdb id
        """

        lastRowID = 0

        # , Created_On, Modified_On
        try:
            sql_insert_query = ''' INSERT INTO IMDb
                                    (
                                        Key, Title, Release, Audience_Rating, Runtime, Genre, Imdb_Rating, Votes, Director, Actors, Desc
                                    )
                                    VALUES
                                    (
                                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                                    );
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

        # , Created_On, Modified_On
        try:
            sql_select_query  = ''' SELECT Id, Key, Title, Release, Audience_Rating, Runtime, Genre, Imdb_Rating, Votes, Director, Actors, Desc 
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

        # Modified_On = ?  , imdb[12]
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
                                        Desc = ?
                                    WHERE Id = ?; '''

            # create a Cursor object by calling the cursor method of the Connection object.
            cur = conn.cursor()
            cur.execute(sql_update_query, (imdb[1], imdb[2], imdb[3], imdb[4], imdb[5], imdb[6], imdb[7], imdb[8], imdb[9], imdb[10], imdb[11], imdb[0],))
            conn.commit()
            lastRowID = cur.lastrowid
        except Error as e:
            print("Error update data from sqlite table", e)
        finally:
            cur.close()

        return lastRowID

    # If you want to pass arguments to the UPDATE statement, you use the question mark (?) as the placeholder for each argument.
    def delete_imdb(self, conn, id):
        """
        Delete a imdb item by id
        :param conn:  Connection to the SQLite database
        :param id: id of the task
        :return: lastRowID
        """

        lastRowID = 0

        # Modified_On = ?  , imdb[12]
        try:
            sql_delete_query = 'DELETE FROM IMDb WHERE Id = ?'

            # create a Cursor object by calling the cursor method of the Connection object.
            cur = conn.cursor()
            cur.execute(sql_delete_query, (id,))
            conn.commit()
            
            lastRowID = cur.lastrowid
        except Error as e:
            print("Error delete item from sqlite table", e)
        finally:
            cur.close()

        return lastRowID

    # If you want to pass arguments to the UPDATE statement, you use the question mark (?) as the placeholder for each argument.
    def delete_all_imdb(self, conn):
        """
        Delete all rows in the IMDb table
        :param conn: Connection to the SQLite database
        :return: lastRowID
        """

        lastRowID = 0

        # Modified_On = ?  , imdb[12]
        try:
            sql_delete_query = 'DELETE FROM IMDb'

            # create a Cursor object by calling the cursor method of the Connection object.
            cur = conn.cursor()
            cur.execute(sql_delete_query)
            conn.commit()
            
            lastRowID = cur.lastrowid
        except Error as e:
            print("Error delete all item from sqlite table", e)
        finally:
            cur.close()

        return lastRowID