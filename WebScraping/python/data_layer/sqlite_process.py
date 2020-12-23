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

    # create a database connection to a SQLite database
    def create_connection(self, db_file):
        conn = None
        try:
            # create a database connection
            conn = sqlite3.connect(db_file)
            self.__check_to_create_table(conn, db_file)
        except Error as e:
           print("Failed to create connection ", e)
        return conn

    # close current a database connection to a SQLite database
    def close_connection(self, conn):
        if (conn):
            conn.close()

    # check if not exist to create a table IMDb
    # :param conn: current connection to the SQLite database
    # :param db_file: database file path
    def __check_to_create_table(self, conn, db_file):
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
        try:
            cur = conn.cursor()
            #get the count of tables with the name
            cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='IMDb' ''')
            #if the count is 1, then table exists
            if cur.fetchone()[0]==0 : 
                # create IMDb table
                cur.execute(sql_create_imdb_table)
        except Error as e:
            if conn:
                conn.rollback()
            print("Error create the database connection", e)
        finally:
            cur.close()

    # If you want to pass arguments to the INSERT statement, you use the question mark (?) as the placeholder for each argument.
    # Create a new IMDb item 
    # :param conn: current connection to the SQLite database
    # :param imdb: IMDb item (Key, Title, Release, Audience_Rating, Runtime, Genre, Imdb_Rating, Votes, Director, Actors, Desc, Created_On, Modified_On)
    # :return: lastrowid (the AUTO_INCREMENT value for the new row)
    def create_imdb(self, conn, imdb):
        lastRowID = 0
        try:
            sql_insert_query = ''' INSERT INTO IMDb
                                    (
                                        Key, Title, Release, Audience_Rating, Runtime, Genre, Imdb_Rating, Votes, Director, Actors, Desc, Created_On, Modified_On
                                    )
                                    VALUES
                                    (
                                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                                    );
                                '''
            # create a Cursor object by calling the cursor method of the Connection object.
            cur = conn.cursor()
            cur.execute(sql_insert_query, imdb)
            conn.commit()
            lastRowID = cur.lastrowid
        except Error as e:
            if conn:
                conn.rollback()
            print("Error insert data from sqlite table", e)
        finally:
            cur.close()
        return lastRowID

     # If you want to pass arguments to the INSERT statement, you use the question mark (?) as the placeholder for each argument.
    # Create a new multi IMDb item 
    # :param conn: current connection to the SQLite database
    # :param imdbs: multi IMDb item (Key, Title, Release, Audience_Rating, Runtime, Genre, Imdb_Rating, Votes, Director, Actors, Desc, Created_On, Modified_On)
    # :return: result (row count after inserted)
    def create_multi_imdb(self, conn, imdbs):
        result = 0
        try:
            # , Desc, Created_On, Modified_On
            sql_insert_query = ''' INSERT INTO IMDb
                                    (
                                        Key, Title, Release, Audience_Rating, Runtime, Genre, Imdb_Rating, Votes, Director, Actors
                                    )
                                    VALUES
                                    (
                                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                                    );
                                '''
            # create a Cursor object by calling the cursor method of the Connection object.
            cur = conn.cursor()
            cur.executemany(sql_insert_query, imdbs)
            conn.commit()
            result = cur.rowcount 
        except Error as e: # the changes are rolled back and an error message is printed to the terminal.
            if conn:
                conn.rollback()
            print("Error insert data from sqlite table", e)
        finally:
            cur.close()
        return result

    # Read an IMDb item by key
    # :param conn:  current connection to the SQLite database
    # :param key: Key of IMDb
    # :return: IMDb item(Id, Key, Title, Release, Audience_Rating, Runtime, Genre, Imdb_Rating, Votes, Director, Actors, Desc, Created_On, Modified_On)
    def read_imdb(self, conn, key):
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
            if conn:
                conn.rollback()
            print("Error reading data from sqlite table", e)
        finally:
            cur.close()
        return imdb_item

    # If you want to pass arguments to the UPDATE statement, you use the question mark (?) as the placeholder for each argument.
    # Update an exist IMDb item into the IMDb table
    # :param conn: current connection to the SQLite database
    # :param imdb: IMDb item(Id, Key, Title, Release, Audience_Rating, Runtime, Genre, Imdb_Rating, Votes, Director, Actors, Desc, Created_On, Modified_On)
    # :return: lastrowid (imdb id updated)
    def update_imdb(self, conn, imdb):
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
            if conn:
                conn.rollback()
            print("Error update data from sqlite table", e)
        finally:
            cur.close()
        return lastRowID

    # If you want to pass arguments to the UPDATE statement, you use the question mark (?) as the placeholder for each argument.
    # Update an exist Modified_On into the IMDb table
    # :param conn: current connection
    # :param modifiedOn: Modified_On of IMDb table
    # :param Id: Id of IMDb table
    # :return: lastrowid (imdb id updated)
    def update_imdb_modifiedOn(self, conn, modifiedOn, Id):
        lastRowID = 0
        try:
            sql_update_query = ''' UPDATE IMDb 
                                    SET Modified_On = ?
                                    WHERE Id = ?; '''
            # create a Cursor object by calling the cursor method of the Connection object.
            cur = conn.cursor()
            cur.execute(sql_update_query, (modifiedOn, Id, ))
            conn.commit()
            lastRowID = cur.lastrowid
        except Error as e:
            if conn:
                conn.rollback()
            print("Error update data from sqlite table", e)
        finally:
            cur.close()
        return lastRowID

    # If you want to pass arguments to the DELETE statement, you use the question mark (?) as the placeholder for each argument.
    # Delete a IMDb item by id
    # :param conn:  Connection to the SQLite database
    # :param id: id of the task
    # :return: result (row count after deleted)
    def delete_imdb_by_Id(self, conn, id):
        result = 0
        try:
            sql_delete_query = 'DELETE FROM IMDb WHERE Id = ?'
            # create a Cursor object by calling the cursor method of the Connection object.
            cur = conn.cursor()
            cur.execute(sql_delete_query, (id,))
            conn.commit()
            result = cur.rowcount
        except Error as e:
            if conn:
                conn.rollback()
            print("Error delete item from sqlite table", e)
        finally:
            cur.close()
        return result

    # Delete all rows in the IMDb table
    # :param conn: Connection to the SQLite database
    # :return: result (row count after deleted)
    def delete_all_imdb(self, conn):
        result = 0
        try:
            sql_delete_query = 'DELETE FROM IMDb'

            # create a Cursor object by calling the cursor method of the Connection object.
            cur = conn.cursor()
            cur.execute(sql_delete_query)
            conn.commit()
            result = cur.rowcount
        except Error as e:
            if conn:
                conn.rollback()
            print("Error delete all item from sqlite table", e)
        finally:
            cur.close()
        return result

    # Delete all rows in the IMDb table
    # :param conn: Connection to the SQLite database
    # :return: lastRowID
    def delete_all_empty_imdb_key(self, conn):
        result = 0
        try:
            sql_delete_query = "DELETE FROM IMDb WHERE Key = '' " 
            # create a Cursor object by calling the cursor method of the Connection object.
            cur = conn.cursor()
            cur.execute(sql_delete_query)
            conn.commit()
            result = cur.rowcount
        except Error as e:
            if conn:
                conn.rollback()
            print("Error delete all empty item from sqlite table", e)
        finally:
            cur.close()
        return result


    # VACUUM imdb_sqlite database
    # ---First, solve the database file size remains unchanged
    # ---Second, the database that has a high number of inserts, updates, and deletes
    # ---Third, decreases the number of rows that can be stored in a single page, increases the number of pages to hold a table
    # :param conn:  Connection to the SQLite database
    def vacuum_imdb_sqlite(self, conn):
        try:
            sql_vacuum_query  = ''' VACUUM; '''

            # create a Cursor object by calling the cursor method of the Connection object.
            cur = conn.cursor()
            cur.execute(sql_vacuum_query)
        except Error as e:
            if conn:
                conn.rollback()
            print("Error vacuum imdb_sqlite", e)
        finally:
                cur.close()