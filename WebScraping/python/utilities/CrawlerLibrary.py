"""
We can then import these at begin
bs4 (beautifulsoup4): Allows us to parse the HTML of the site and convert it to a BeautifulSoup object, which represents the HTML as a nested data structure.
pandas: Python Data Analysis Library (The goto Python package for dataset manipulation)
requests: The package that allows us to connect the site of choice.
constant: define multi variable that called everywhere
app_enum: define multi option that called everywhere
sqlite_process: all function about database (CRUD)
os: Miscellaneous operating system interfaces
"""
import bs4
import pandas as pd
import requests
from utilities import constant
from utilities.app_enum import EnumStatusCode
import os

# all operation about crawler
class CrawlerOperation:
    __instance = None

    @staticmethod 
    def getInstance():
      # Static access method.
      if CrawlerOperation.__instance == None:
         CrawlerOperation()
      return CrawlerOperation.__instance

    def __init__(self):  # init method or constructor   
        # Virtually private constructor.
        if CrawlerOperation.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            CrawlerOperation.__instance = self

    """
    -----// begin public member function: easily accessible from any part of the program //-----
    """
    # titles = [movie.find('a').text for movie in movies]
    # release = [movie.find('span', class_='lister-item-year text-muted unbold').text for movie in movies]
    # imdb_rating = movie.find('div', 'inline-block ratings-imdb-rating')['data-value']
    # votes = movie.findAll('span' , {'name' : 'nv'})[0]['data-value']
    # earnings = movie.findAll('span' , {'name' : 'nv'})[1]['data-value']
    # director = movie.find('p').find('a').text
    # actors = [actor.text for actor in movie.find('p').findAll('a')[1:]]
    def extract_attribute(self, 
                            movies, 
                            tag_1, 
                            class_1='', 
                            tag_2='', 
                            class_2='',
                            text_attribute=True, 
                            order=None, 
                            nested=False,
                            duplicated=False):        
        data_list = []
        for movie in movies:
            if text_attribute:
                if nested:  # Extracting Nested Values: director and actors
                    data_list.append(self.__nested_text_value(movie, tag_1, class_1, tag_2, class_2, order))
                elif duplicated:  # Extracting same class: description
                    data_list.append(self.__order_text_value(movie, tag_1, class_1, order))
                else:  # Extracting text: titles and release year
                    data_list.append(self.__text_value(movie, tag_1, class_1))
            else:  # Extracting Numerical Values: imdb_rating  
                data_list.append(self.__numeric_value(movie, tag_1, class_1, order))
        return data_list

    # Connect to the webpage, extract the HTML behind it and convert it to a BeautifulSoup object
    def get_page_contents(self, url):
        soap = None
        try:
            page = requests.get(url, headers={"Accept-Language": "en-US"})
            if page.status_code == constant.STATUS_OK:
                soap = bs4.BeautifulSoup(page.text, 
                                            "html.parser")
            else:
                # tmp_code: page.raise_for_status()
                print(response_message(page.status_code))
        except Exception as ex:
            print('There was a problem: %s' % (ex)) 
        return soap
    """
    -----// end public member function: easily accessible from any part of the program //-----
    """

    """
    -----// begin private member function: can access within the class only //-----
    """
    # extract numerical values from movie item
    def __numeric_value(self, 
                        movie, 
                        tag, 
                        class_=None, 
                        order=None): 
        if order:
            if len(movie.findAll(tag, class_)) > 1:
                to_extract = movie.findAll(tag, class_)[order]['data-value']
            else:
                # to_extract = None
                to_extract = ''
        else:
            to_extract = movie.find(tag, class_)['data-value']
        return to_extract

    # extract nested values from movie item
    def __nested_text_value(self, 
                            movie, 
                            tag_1, 
                            class_1, 
                            tag_2, 
                            class_2, 
                            order=None):  
        if not order:
            return movie.find(tag_1, class_1).find(tag_2, class_2).text.strip()
        else:
            return [val.text for val in movie.find(tag_1, class_1).findAll(tag_2, class_2)[order]]

    # extract text values from movie item
    def __text_value(self, 
                    movie, 
                    tag, 
                    class_=None):   
        if movie.find(tag, class_):
            return movie.find(tag, class_).text.strip()
        else:
            # return 
            return ''

    # extract numerical values from movie item
    def __order_text_value(self, 
                        movie, 
                        tag, 
                        class_=None, 
                        order=None): 
        if order:
            if len(movie.findAll(tag, class_)) > 1:
                to_extract = movie.findAll(tag, class_)[order].text
            else:
                # to_extract = None
                to_extract = ''
        else:
            to_extract = movie.find(tag, class_).text
        return to_extract.strip() # strip(): removing any leading and trailing whitespaces including tabs (\t)
    """
    -----// end private member function: can access within the class only //-----
    """

# all operation about csv file
class CsvOperation:
    __instance = None

    @staticmethod 
    def getInstance():
      # Static access method.
      if CsvOperation.__instance == None:
         CsvOperation()
      return CsvOperation.__instance

    def __init__(self):  # init method or constructor   
        # Virtually private constructor.
        if CsvOperation.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            CsvOperation.__instance = self

    """
    -----// end public member function: easily accessible from any part of the program //-----
    """
    # extracting all the information we need an turning it into a clean pandas data frame
    # export data frame to csv format
    def export_csv(self, 
                    filename, 
                    df_dict,
                    csv_path):

        df = pd.DataFrame(df_dict)  # We use pandas to visualize the data     

        # export to csv format with header
        df.to_csv(csv_path + "\\" + filename + ".csv", 
                    header=True, 
                    index=False)  
    """
    -----// end public member function: easily accessible from any part of the program //-----
    """

class DateTimeOperation:
    __instance = None

    @staticmethod 
    def getInstance():
      # Static access method.
      if DateTimeOperation.__instance == None:
         DateTimeOperation()
      return DateTimeOperation.__instance

    def __init__(self):  # init method or constructor   
        # Virtually private constructor.
        if DateTimeOperation.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            DateTimeOperation.__instance = self

    def convert_time_to_preferred_format(self, n):
        sec = n * 60
        hour = sec // 3600
        sec %= 3600
        min = sec // 60
        sec %= 60
        return "%dh %02dmin" % (hour, min) 

class PathLibOperation:
    __instance = None

    @staticmethod 
    def getInstance():
      # Static access method.
      if PathLibOperation.__instance == None:
         PathLibOperation()
      return PathLibOperation.__instance

    def __init__(self):  # init method or constructor   
        # Virtually private constructor.
        if PathLibOperation.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            PathLibOperation.__instance = self

    # input path could be a valid directory
    def check_valid_dir_names(self, path):
        if not os.path.exists(os.path.dirname(path)):
            return False
        else:
            return True
            # os.makedirs(os.path.dirname(path))
    


# get error message from status code
def response_message(status_code):
    http_error_msg = u'%s Other Error: ' % status_code

    if 100 <= status_code < 200:
        http_error_msg = u'%s Informational Error: ' % status_code
    elif 200 <= status_code < 299:
        http_error_msg = u'%s Successful Error: ' % status_code
    elif 400 <= status_code < 500:
        http_error_msg = u'%s Client Error: ' % status_code
    elif 500 <= status_code < 600:
        http_error_msg = u'%s Server Error: ' % status_code

    http_error_msg += u'%s' % EnumStatusCode(status_code).name
        
    return http_error_msg   