""" ---- begin number constant ---- """
STATUS_OK = 200
CONNECTION_ABORTED = 10054
REFRESH_TIME_IN_SECONDS = 5
""" ---- end number constant ---- """

""" ---- begin text constant ---- """
# When reading the csv:
# - Place 'r' before the path string to read any special characters, such as '\'
# - Don't forget to put the file name at the end of the path + '.csv'
# - Before running the code, make sure that the column names in the CSV files match with the column names in the tables created and in the query below
# - If needed make sure that all the columns are in a TEXT format
CHROME_EXECUTABLE_PATH = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
CHROME_DRIVER_PATH = r"\WebScraping\python\libs\chromedriver.exe"
DB_FILE_PATH = r'\WebScraping\python\db\imdb_sqlite.db'
SHORT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
IMDB_KEY_EXPRESSION = "[^a-zA-Z0-9]"
""" ---- end text constant ---- """



