from utils import *

import yaml
import mysql.connector
from mysql.connector import Error as MySqlError

class MySqlStoringData:
    yaml.warnings({'YAMLLoadWarning': False})
    __instance = None
    __pathLibOperation = None

    @staticmethod
    def getInstance():
        # Static access method.
        if MySqlStoringData.__instance == None:
            MySqlStoringData()
        return MySqlStoringData.__instance

    """
    -----// begin private member function: can access functions by derived class //-----
    """
    def __init__(self):  # init method or constructor
        # Virtually private constructor.
        if MySqlStoringData.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.__pathLibOperation = PathLibOperation.getInstance()
            MySqlStoringData.__instance = self

    def __get_db_config(self):
        configFile = self.__pathLibOperation.resource_path("./settings/config.yml")

        # create a database connection
        with open(configFile, "r") as ymlfile:
            cfg = yaml.load(ymlfile)

        connection_config_dict = {
            'host': cfg["databases"]["mysql"]["host"],
            'port': cfg["databases"]["mysql"]["port"],
            'user': cfg["databases"]["mysql"]["user"],
            'password': cfg["databases"]["mysql"]["passwd"],
            'database': cfg["databases"]["mysql"]["db"],
            'raise_on_warnings': cfg["databases"]["mysql"]["raise_on_warnings"],
            'use_pure': cfg["databases"]["mysql"]["use_pure"],
            'autocommit': cfg["databases"]["mysql"]["autocommit"],
            'pool_size': cfg["databases"]["mysql"]["pool_size"],
            'connection_timeout': cfg["databases"]["mysql"]["connection_timeout"]
        }

        return connection_config_dict

    # create a database connection to a SQLite database
    def __create_connection(self):
        conn = None

        try:
            conn_config_dict = self.__get_db_config()
            conn = mysql.connector.connect(host=conn_config_dict.get('host'),
                                            port=int(conn_config_dict.get('port')),
                                            database=conn_config_dict.get('database'),
                                            user=conn_config_dict.get('user'),
                                            password=conn_config_dict.get('password'), 
                                            connection_timeout=int(conn_config_dict.get('connection_timeout')))
            self.__check_to_create_table(conn)
        except MySqlError as __mse:
            print("Error while connecting to MySQL", __mse)
        return conn

    # close current a database connection to a SQLite database
    def __close_connection(self, conn):
        if (conn):
            conn.close()

    # check if not exist to create a table IMDb
    # :param conn: current connection to the SQLite database
    # :param db_file: database file path
    def __check_to_create_table(self, conn):
        sql_create_imdb_table = """ CREATE TABLE IF NOT EXISTS `imdb` (
                                        `Id` INT(11) NOT NULL AUTO_INCREMENT,
                                        `Key` TINYTEXT NULL COLLATE 'utf8_unicode_ci',
                                        `Title` TEXT NULL COLLATE 'utf8_unicode_ci',
                                        `Release` TINYTEXT NULL COLLATE 'utf8_unicode_ci',
                                        `Audience_Rating` TINYTEXT NULL COLLATE 'utf8_unicode_ci',
                                        `Runtime` TINYTEXT NULL COLLATE 'utf8_unicode_ci',
                                        `Genre` TINYTEXT NULL COLLATE 'utf8_unicode_ci',
                                        `Imdb_Rating` DECIMAL(2,1) NULL DEFAULT NULL,
                                        `Votes` INT(11) NULL DEFAULT NULL,
                                        `Director` TINYTEXT NULL COLLATE 'utf8_unicode_ci',
                                        `Actors` TEXT NULL COLLATE 'utf8_unicode_ci',
                                        PRIMARY KEY (`Id`)
                                    )
                                    COLLATE='utf8_unicode_ci'
                                    ENGINE=InnoDB;
                                    """

        sql_create_datalog_table = """ CREATE TABLE IF NOT EXISTS `data_log` (
                                        `Id` INT(11) NOT NULL AUTO_INCREMENT,
                                        `LogName` TEXT NULL COLLATE 'utf8_unicode_ci',
                                        `ModifiedOn` DATETIME NULL,
                                        `UserName` TEXT NULL COLLATE 'utf8_unicode_ci',
                                        `Type` CHAR(1) NULL,
                                        PRIMARY KEY (`Id`)
                                    )
                                    COLLATE='utf8_unicode_ci'
                                    ENGINE=InnoDB;
                                    """

        sql_after_insert_imdb_trigger = """ CREATE TRIGGER after_imdb_insert 
                                        AFTER INSERT ON `imdb`
                                        FOR EACH ROW 
                                    INSERT INTO `data_log`
                                    SET `LogName`= NEW.`Key`, 
                                            `ModifiedOn` = NOW(),  
                                            `UserName` = USER(),
                                            `LogType` = 'I';
                                    """

        sql_after_update_imdb_trigger = """ CREATE TRIGGER after_imdb_update
                                        AFTER UPDATE ON `imdb`
                                        FOR EACH ROW 
                                    INSERT INTO `data_log`
                                    SET `LogName`= NEW.`Key`, 
                                            `ModifiedOn` = NOW(), 
                                            `UserName` = USER(),
                                            `LogType` = 'U';
                                    """

        sql_after_delete_imdb_trigger = """ CREATE TRIGGER after_imdb_delete
                                        AFTER DELETE ON `imdb`
                                        FOR EACH ROW 
                                    INSERT INTO `data_log`
                                    SET `LogName`= OLD.`Key`,
                                            `ModifiedOn` = NOW(), 
                                            `UserName` = USER(),
                                            `LogType` = 'D';
                                    """

        try:
            cur = conn.cursor()
            # create IMDb table
            cur.execute(sql_create_imdb_table)
            cur.execute(sql_create_datalog_table)
        except MySqlError as __mse:
            if conn:
                conn.rollback()
            print("Failed to create table in MySQL: {}".format(__mse))
        finally:
            cur.close()
    """
    -----// end private member function: can access functions by derived class //-----
    """

    """
    -----// begin public member function: easily accessible from any part of the program //-----
    """
    # If you want to pass arguments to the INSERT statement, you use the question mark (?) as the placeholder for each argument.
    # Create a new IMDb item 
    # :param conn: current connection to the SQLite database
    # :param imdb: IMDb item (Key, Title, Release, Audience_Rating, Runtime, Genre, Imdb_Rating, Votes, Director, Actors)
    # :return: lastrowid (the AUTO_INCREMENT value for the new row)
    def create_imdb(self, imdb):
        rowCnt = 0
        conn = None
        cur = None
        try:
            sql_insert_query = ''' INSERT INTO `imdb`
                                    (
                                        `Key`, 
                                        `Title`, 
                                        `Release`, 
                                        `Audience_Rating`, 
                                        `Runtime`, 
                                        `Genre`, 
                                        `Imdb_Rating`, 
                                        `Votes`, 
                                        `Director`, 
                                        `Actors`
                                    )
                                    VALUES
                                    (
                                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                                    );
                                '''

            print("imdb: %s" % imdb)
            val = ( imdb["Key"],
                    imdb["Title"],
                    imdb["Release"],
                    imdb["Audience_Rating"],
                    imdb["Runtime"],
                    imdb["Genre"],
                    imdb["Imdb_Rating"],
                    imdb["Votes"],
                    imdb["Director"],
                    imdb["Actors"] )

            # create a Cursor object by calling the cursor method of the Connection object.
            conn = self.__create_connection()
            if conn:
                cur = conn.cursor()
                cur.execute(sql_insert_query, val)
                conn.commit()
                rowCnt = cur.rowcount
        except MySqlError as __mse:
            if conn:
                conn.rollback()
            print ("Error while connecting to MySQL:", __mse)
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
        return rowCnt

    # Read an IMDb item by key/ read all
    # :param conn:  current connection to the SQLite database
    # :param key: Key of IMDb
    # :return: one/multi IMDb item (Id, Key, Title, Release, Audience_Rating, Runtime, Genre, Imdb_Rating, Votes, Director, Actors)
    def read_imdb(self, key):
        result = None
        conn = None
        cur = None
        try:
            sql_select_query  = ''' SELECT `Id`, 
                                            `Key`, 
                                            `Title`, 
                                            `Release`, 
                                            `Audience_Rating`, 
                                            `Runtime`, 
                                            `Genre`, 
                                            `Imdb_Rating`, 
                                            `Votes`, 
                                            `Director`, 
                                            `Actors`
                                    FROM `imdb` '''

            # create a Cursor object by calling the cursor method of the Connection object.
            conn = self.__create_connection()
            if conn:
                cur = conn.cursor()
                if not key:
                    cur.execute(sql_select_query)
                else:
                    sql_select_query += ''' WHERE `Key` = %s '''
                    val = ( key, )
                    cur.execute(sql_select_query, val)
                result = cur.fetchall()
        except MySqlError as __mse:
            if conn:
                conn.rollback()
            print ("Error while connecting to MySQL:", __mse)
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
        return result
    """
    -----// end public member function: easily accessible from any part of the program //-----
    """
     


    