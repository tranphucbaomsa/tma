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

from selenium.webdriver.common.by import By

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
    # this function use to get item attibute in list page
    def extract_attribute(self, 
                            movies, 
                            tag_1, 
                            class_1='', 
                            tag_2='', 
                            class_2='',
                            text_attribute=True, 
                            order=None, 
                            nested=False,
                            duplicated=False,
                            href_attribute=False):
        data_list = []
        for movie in movies:
            if text_attribute:
                if nested:  # Extracting Nested Values: director and actors
                    data_list.append(self.__nested_text_value(movie, tag_1, class_1, tag_2, class_2, order))
                elif duplicated:  # Extracting same class: description
                    data_list.append(self.__order_text_value(movie, tag_1, class_1, order))
                elif href_attribute:  # Extracting href value of anchor link: keys
                    data_list.append(self.__href_value(movie, tag_1, class_1))
                else:  # Extracting text: titles and release year
                    data_list.append(self.__text_value(movie, tag_1, class_1))
            else:  # Extracting Numerical Values: imdb_rating  
                data_list.append(self.__numeric_value(movie, tag_1, class_1, order))
        return data_list

   
    def extract_single_attribute_lxml(self, 
                                        driver, 
                                        tag_1, 
                                        class_1='', 
                                        tag_2='', 
                                        class_2='',
                                        text_attribute=True,
                                        order=None, 
                                        nested=False,
                                        id_attribute=False,
                                        itemprop_attribute=False,
                                        css_selector_inner=False,
                                        array_value=False,
                                        split_separator=None,
                                        index_element=None):
        data = ""
        if not split_separator:
            if not text_attribute:
                if nested:  # Extracting Nested Values: title
                    data = self.__nested_text_value_lxml(driver, tag_1, class_1, tag_2, class_2, order)
                elif id_attribute:  # Extracting value by id attr: release
                    data = self.__text_value_by_id_lxml(driver, tag_1, class_1)
                elif itemprop_attribute:  # Extracting value by itemprop attr: imdb_rating
                    data = self.__order_text_value_by_itemprop_lxml(driver, tag_1, class_1, order)
                elif css_selector_inner: # Extracting value by two tag and class with order: director
                    data = self.__text_value_css_inner_lxml(driver, tag_1, class_1, tag_2, order)
                elif array_value: # Extracting value by array return: actor
                    arrValue = self.__array_item_css_inner_lxml(driver, tag_1, class_1,  tag_2, order)
                    actor_item = ""
                    # traverse in the string   
                    for itemValue in arrValue:  
                            indexActor = arrValue.index(itemValue)
                            if indexActor < len(arrValue) - 1:
                                actor_item += itemValue.text + (", " if indexActor < len(arrValue) - 2 else "")
                    data = actor_item
            else:  # Extracting text: vote
                if class_2:
                    data = self.__text_value_by_two_class_lxml(driver, tag_1, class_1, class_2)
                else:
                    data = self.__text_value_by_class_lxml(driver, tag_1, class_1)
        else: # Extracting array text: audience_rating, runtime, genre
            arrSplit = self.__array_value_lxml(driver, tag_1, class_1, split_separator)
            if arrSplit:
                data = arrSplit[index_element]

        return data

    # Connect to the webpage, extract the HTML behind it and convert it to a BeautifulSoup object
    def get_page_contents(self, url):
        soap = None
        response = None
        try:
            soap = self.__request_to_soap(url)
        except Exception as ex:
            print('There was a problem: %s' % (ex)) 
        return soap

    def __request_to_soap(self, base_url):
        custom_header = {"Accept-Language": "en-US", 
                            "Content-Type": "text/html; charset=utf-8",
                            "Connection": "keep-alive"}
        sub_response = requests.get(base_url, headers=custom_header)
        if sub_response.status_code == constant.STATUS_OK:
            return bs4.BeautifulSoup(sub_response.text, 
                                        "html.parser")
        else:
            # tmp_code: page.raise_for_status()
            print(response_message(sub_response.status_code))
            None

    """
    -----// end public member function: easily accessible from any part of the program //-----
    """

    """
    -----// begin private member function: can access within the class only //-----
    """
    # extract numerical values from movie item
    # imdb_rating = movie.find('div', 'inline-block ratings-imdb-rating')['data-value']
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
    # director = movie.find('p').find('a').text
    # actors = [actor.text for actor in movie.find('p').findAll('a')[1:]]
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
    # titles = [movie.find('a').text for movie in movies]
    # release = [movie.find('span', class_='lister-item-year text-muted unbold').text for movie in movies]
    def __text_value(self, 
                    movie, 
                    tag, 
                    class_=None):   
        if movie.find(tag, class_):
            return movie.find(tag, class_).text.strip()
        else:
            # return 
            return ''

    # extract href values from movie item
    # keys = [movie.find('a').get('href') for movie in movies]
    def __href_value(self, 
                    movie, 
                    tag, 
                    class_=None):   
        if movie.find(tag, class_):
            return movie.find(tag, class_).get('href')
        else:
            return ''

    # extract text in tag with order from movie item
    # votes = movie.findAll('span' , {'name' : 'nv'})[0]['data-value']
    # descriptions = movie.findAll('p' , {'class' : 'text-muted'})[1].text
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
    
    # extract nested values from webdriver
    def __nested_text_value_lxml(self, 
                                    driver, 
                                    tag_1, 
                                    class_1, 
                                    tag_2, 
                                    class_2, 
                                    order=None):
        if not order:
            return driver.find_element(By.XPATH, "//" + tag_1 + "[@class=" + "\"" + class_1 + "\"" + "]/" + tag_2 + "[@class=\"" + class_2 + "\"]").text.strip()
        else:
            return [val.text for val in driver.find_elements(By.XPATH, "//" + tag_1 + "[@class=" + "\"" + class_1 + "\"" + "]/" + tag_2 + "[@class=\"" + class_2 + "\"]")[order]]

     # extract text values by id from webdriver
    def __text_value_by_id_lxml(self, 
                                driver, 
                                tag, 
                                id_=None):   
        if driver.find_element(By.XPATH, "//" + tag + "[@id=\"" + id_ + "\"]"):
            return driver.find_element(By.XPATH, "//" + tag + "[@id=\"" + id_ + "\"]").text.strip()
        else:
            return ''

    # extract text values by class from webdriver
    def __text_value_by_class_lxml(self, 
                                    driver, 
                                    tag, 
                                    class_=None):   
        if driver.find_element(By.XPATH, "//" + tag + "[contains(@class, \"" + class_ + "\")]"):
            return driver.find_element(By.XPATH, "//" + tag + "[contains(@class, \"" + class_ + "\")]").text.strip()
        else:
            return ''

    def __text_value_by_two_class_lxml(self, 
                                    driver, 
                                    tag, 
                                    class_1=None,
                                    class_2=None):   
        if driver.find_element(By.XPATH, "//" + tag + "[@class=\"" + class_1 + "\" or @class=\"" + class_2 + "\"]"):
            return driver.find_element(By.XPATH, "//" + tag + "[@class=\"" + class_1 + "\" or @class=\"" + class_2 + "\"]").text.strip()
        else:
            return ''

    # extract text in tag with order from webdriver
    def __order_text_value_by_itemprop_lxml(self, 
                        driver, 
                        tag, 
                        class_=None, 
                        order=None): 
        if not order:
            to_extract = driver.find_element(By.XPATH, "//" + tag + "[@itemprop=" + "\"" + class_ + "\"" + "]").text
        else:
            to_extract = [val.text for val in driver.find_elements(By.XPATH, "//" + tag + "[@itemprop=" + "\"" + class_ + "\"" + "]")[order]]
        return to_extract.strip() # strip(): removing any leading and trailing whitespaces including tabs (\t)

    # extract array in tag with class and split_separator from webdriver
    def __array_value_lxml(self, 
                        driver, 
                        tag, 
                        class_=None,
                        split_separator=None): 
        if not driver.find_element(By.XPATH, "//" + tag + "[@class=\"" + class_ + "\"]"):
            return []
        else:
            return driver.find_element(By.XPATH, "//" + tag + "[@class=\"" + class_ + "\"]").text.split(" | ")

    # extract inner text values by class from webdriver
    def __text_value_css_inner_lxml(self, 
                                    driver, 
                                    tag, 
                                    class_=None,
                                    tag_inner=None,
                                    order=None):   
        if driver.find_element(By.XPATH, "//" + tag + "[@class=\"" + class_ + "\"]")[order].find_element_by_css_selector(tag_inner):
            return driver.find_element(By.XPATH, "//" + tag + "[@class=\"" + class_ + "\"]")[order].find_element_by_css_selector(tag_inner).text
        else:
            return ''

    # extract array in tag with class and split_separator from webdriver
    def __array_item_css_inner_lxml(self, 
                                    driver, 
                                    tag, 
                                    class_=None,
                                    tag_inner=None,
                                    order=None):   
        if driver.find_element(By.XPATH, "//" + tag + "[@class=\"" + class_ + "\"]")[order].find_element_by_css_selector(tag_inner):
            return driver.find_element(By.XPATH, "//" + tag + "[@class=\"" + class_ + "\"]")[order].find_element_by_css_selector(tag_inner)
        else:
            return []
    
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
    -----// begin public member function: easily accessible from any part of the program //-----
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
    
# all operation about export to file (csv, xlsx,...)
class ExportOperation:
    __instance = None

    @staticmethod 
    def getInstance():
      # Static access method.
      if ExportOperation.__instance == None:
         ExportOperation()
      return ExportOperation.__instance

    def __init__(self):  # init method or constructor   
        # Virtually private constructor.
        if ExportOperation.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            ExportOperation.__instance = self

    """
    -----// begin public member function: easily accessible from any part of the program //-----
    """
    # extracting all the information we need an turning it into a clean pandas data frame
    # export data frame to csv format
    def export_data_to_file(self, 
                            df_dict,
                            folder_path,
                            filename,
                            extension):
        """Dispatch method"""
        method_name = 'ext_' + str(extension)
        # Get the method from 'self'. Default to a lambda.
        method = getattr(self, method_name, lambda: "Invalid extension")
        # Call the method as we return it
        return method(df_dict, folder_path, filename)

    # extracting all the information we need an turning it into a clean pandas data frame
    # export data frame to csv format
    def ext_csv(self,
                    df_dict,
                    folder_path,
                    filename):
        df = pd.DataFrame(df_dict)  # We use pandas to visualize the data     

        df.to_csv(folder_path + "\\" + filename + ".csv",
                    header=True, 
                    index=False)
        return "df.to_csv"
 
    # export data frame to xlsx format
    def ext_xlsx(self,
                    df_dict,
                    folder_path,
                    filename):
        df = pd.DataFrame(df_dict)  # We use pandas to visualize the data     
        df.to_excel(folder_path + "\\" + filename + ".xlsx", 
                        sheet_name=filename,
                        header=True,
                        index = False)
        return "df.to_excel"
    """
    -----// end public member function: easily accessible from any part of the program //-----
    """

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