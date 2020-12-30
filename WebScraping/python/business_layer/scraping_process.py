# import CrawlerOperation, CsvOperation, DateTimeOperation class in CrawlerLibrary.py
# import StoringData class in sqlite_process.py 
# import constant
from utilities.CrawlerLibrary import CrawlerOperation, DateTimeOperation, ExportOperation 
from data_layer.sqlite_process import StoringData
from utilities import constant

# import the necessary packages
# selenium automates browser
import webbrowser as w
import os
from os import path
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re  # Regular expression operations
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import sys

# super class 
class BaseScraping: 
     # protected data members: can access by derived class
     _url = ""
     _csvPath = ""
     _driverPath = ""

     # private data members: can access within the class only
     __businessOperation = None
     __exportOperation = None
     __crawlerOperation = None
     __dtOperation = None

     __imdb = None
     __key_item = ""
     __title_item = ""
     __release_item = ""
     __audience_rating_item = ""
     __runtime_item = ""
     __genre_item = ""
     __imdb_rating_item = ""
     __vote_item = ""
     __director_item = ""
     __actor_item = ""
     __desc_item = ""
     __now = ""

     __keys = None
     __titles = None
     __releases = None
     __audience_ratings = None
     __runtimes = None
     __genres = None 
     __imdb_ratings = None
     __votes = None 
     __directors = None
     __actors = None
     __descriptions = None

     # constructor 
     def __init__(self, csvPath):   
          self._url = "https://www.imdb.com" 
          self._csvPath = csvPath 
          self.__businessOperation = BusinessOperation.getInstance()  # Object singleton instantiation of BusinessOperation class
          self.__exportOperation = ExportOperation.getInstance()  # Object singleton instantiation of BusinessOperation class
          self.__crawlerOperation = CrawlerOperation.getInstance()  # Object singleton instantiation of CrawlerOperation class
          self.__dtOperation = DateTimeOperation.getInstance()  # Object singleton instantiation of DateTimeOperation class

     """
     -----// begin private member function: can access functions by derived class //-----
     """
     def __resource_path(self, 
                         relative_path):
          try:
               base_path = sys._MEIPASS
          except Exception:
               # os.getcwd(): get current working directory
               # os.path.dirname(path): get the directory name from the specified path
               # os.path.abspath(path): get the parent directory
               # os.pardir: a constant string used by the operating system to refer to the parent directory (‘..‘ for UNIX, Windows and ‘::‘ for Mac OS)
               # __file__: get current filename that contain this code
               base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
          return os.path.join(base_path, relative_path)
     """
     -----// end private member function: can access functions by derived class //-----
     """

     """
     -----// begin protected member function: can access within the class only //-----
     """
     def _initProperties(self):
          self.__keys = []
          self.__titles = []
          self.__releases = []
          self.__audience_ratings = []
          self.__runtimes = []
          self.__genres = []
          self.__imdb_ratings = []
          self.__votes = []
          self.__directors = []
          self.__actors = []
          self.__descriptions = []

     def _getDriverPath(self):
         return self._driverPath

     def _setDriverPath(self, value):
         self._driverPath = value

     def _initFirefoxWebDriver(self): 
          # accessing protected member functions of super class 
          _driverPath = self.__resource_path(constant.FIREFOX_GOCKO_DRIVER_PATH)
          # Define Firefox options to open the window in maximized mode
          options = webdriver.FirefoxOptions()
          # options.set_headless(True) # hide browser
          options.add_argument("--start-maximized")
          # the instance of Firefox WebDriver is created
          driver = webdriver.Firefox(executable_path=_driverPath, options=options)
          return driver

     def _initChromeWebDriver(self): 
          # accessing protected member functions of super class 
          _driverPath = self.__resource_path(constant.CHROME_DRIVER_PATH)
          # Define Chrome options to open the window in maximized mode
          options = webdriver.ChromeOptions()
          # options.set_headless(True) # hide browser
          options.add_argument("--start-maximized")
          # create a new Chrome session
          driver = webdriver.Chrome(executable_path=_driverPath, options=options)
          return driver

     def _extract_export_html(self, 
                              html_page_source,
                              filename,
                              extension):
          # soup_list_source: use for parse and extract from html.parser
          soup_list_source = BeautifulSoup(html_page_source, 
                                             "html.parser")

          # We can get a list of all distinct movies and their corresponding HTML by
          movies = soup_list_source.findAll('div',
                                             class_='lister-item-content')

          # we can construct a list of all movie keys
          keysTmp =  self.__crawlerOperation.extract_attribute(movies,
                                                                 'a',
                                                                 href_attribute=True)
          self.keys = []
          for itemKey in keysTmp:
               self.keys.append(itemKey[:itemKey.rindex("/")][-9:]) # href = '/title/tt0111161'

          # we can construct a list of all movie titles
          self.titles =  self.__crawlerOperation.extract_attribute(movies,
                                                                 'a')

          # Release years can be found under the tag span and class lister-item-year text-muted unbold
          # found in <span class="lister-item-year text-muted unbold">(2020)</span>
          self.releases = self.__crawlerOperation.extract_attribute(movies,
                                                                 'span',
                                                                 'lister-item-year text-muted unbold')

          # Audience rating can be found under the tag span and class certificate
          # found in <span class="certificate">TV-MA</span>
          self.audience_ratings = self.__crawlerOperation.extract_attribute(movies,
                                                            'span',
                                                            'certificate')

          # Runtime can be found under the tag span and class runtime
          # found in <span class="runtime">153 min</span>
          runtimeTemp = self.__crawlerOperation.extract_attribute(movies,
                                                  'span',
                                                  'runtime')
          self.runtimes = []
          for itemRuntime in runtimeTemp:
               itemRuntime = itemRuntime.replace('min', '')
               self.runtimes.append(self.__dtOperation.convert_time_to_preferred_format(int(itemRuntime)))

          # Genre can be found under the tag span and class genre
          # found in <span class="genre">Drama</span>
          self.genres = self.__crawlerOperation.extract_attribute(movies,
                                                  'span',
                                                  'genre')

          # IMDB rating value from the data-value attribute we simply need parse the dictionary that the find method returns
          # found in <div class="inline-block ratings-imdb-rating" name="ir" data-value="8.9">
          self.imdb_ratings = self.__crawlerOperation.extract_attribute(movies,
                                                       'div',
                                                       'inline-block ratings-imdb-rating',
                                                       text_attribute=False)

          # we’ll use a dictionary to filter for the attribute name='nv’ in our findAll method and grab the first element
          # found in <span name="nv" data-value="47467">47,467</span>
          self.votes = self.__crawlerOperation.extract_attribute(movies,
                                                  'span' ,
                                                  {'name' : 'nv'},
                                                  order=0,
                                                  duplicated=True)

          # director information is located within an initial p tag and thereafter an a tag — both without class attributes making it necessary to unnest the data
          self.directors = self.__crawlerOperation.extract_attribute(movies,
                                                       'p',
                                                       '',
                                                       'a',
                                                       '',
                                                       text_attribute=True,
                                                       order=0,
                                                       nested=True)

          # actors always correspond to the remaining a tags
          actorsTemp = self.__crawlerOperation.extract_attribute(movies,
                                                  'p',
                                                  '',
                                                  'a',
                                                  '',
                                                  text_attribute=True,
                                                  order=slice(1, 5, None),
                                                  nested=True)
          self.actors = []
          for itemActor in actorsTemp:
               self.actors.append(str(itemActor).replace("[","").replace("]","").replace("'",""))

          self.descriptions =  self.__crawlerOperation.extract_attribute(movies,
                                                  'p',
                                                  'text-muted',
                                                  order=1,
                                                  duplicated=True)

          self._export_to_file(filename,
                                   extension)

     def _extract_export_lxml(self, 
                              key,
                              driver):
          #Selenium hands of the source of the specific job page to Beautiful Soup
          # soup_lxml_source: use for parse and extract from lxml page source
          # soup_lxml_source = BeautifulSoup(driver.page_source, 
          #                                    "lxml")
          self.__keys.append(key)

          title_item = self.__crawlerOperation.extract_single_attribute_lxml(driver,
                                                                                tag_1="div", 
                                                                                class_1="title_wrapper", 
                                                                                tag_2="h1",
                                                                                text_attribute=False,
                                                                                nested=True)
          self.__titles.append(title_item[:title_item.rindex("(")].strip())
          self.__releases.append(self.__crawlerOperation.extract_single_attribute_lxml(driver,
                                                                                     tag_1="span", 
                                                                                     class_1="titleYear", 
                                                                                     text_attribute=False,
                                                                                     id_attribute=True))
          self.__audience_ratings.append(self.__crawlerOperation.extract_single_attribute_lxml(driver,
                                                                                               tag_1="div", 
                                                                                               class_1="subtext", 
                                                                                               text_attribute=False,
                                                                                               split_separator=True,
                                                                                               index_element=0))
          self.__runtimes.append(self.__crawlerOperation.extract_single_attribute_lxml(driver,
                                                                                          tag_1="div", 
                                                                                          class_1="subtext", 
                                                                                          text_attribute=False,
                                                                                          split_separator=True,
                                                                                          index_element=1))
          self.__genres.append(self.__crawlerOperation.extract_single_attribute_lxml(driver,
                                                                                     tag_1="div", 
                                                                                     class_1="subtext", 
                                                                                     text_attribute=False,
                                                                                     split_separator=True,
                                                                                     index_element=2))
          self.__imdb_ratings.append(self.__crawlerOperation.extract_single_attribute_lxml(driver,
                                                                                          tag_1="span", 
                                                                                          class_1="ratingValue", 
                                                                                          text_attribute=False,
                                                                                          order=0,
                                                                                          itemprop_attribute=True))
          self.__votes.append(self.__crawlerOperation.extract_single_attribute_lxml(driver,
                                                                                     tag_1="span", 
                                                                                     class_1="small"))
          self.__directors.append(self.__crawlerOperation.extract_single_attribute_lxml(driver,
                                                                                          tag_1="div", 
                                                                                          class_1="credit_summary_item",
                                                                                          tag_2="a",
                                                                                          text_attribute=False,
                                                                                          order=0,
                                                                                          css_selector_inner=True))
          self.__actors.append(self.__crawlerOperation.extract_single_attribute_lxml(driver,
                                                                                     tag_1="div", 
                                                                                     class_1="credit_summary_item",
                                                                                     tag_2="a",
                                                                                     text_attribute=False,
                                                                                     order=2,
                                                                                     array_value=True))
          # self.__descriptions.append(self.__crawlerOperation.extract_single_attribute_lxml(driver,
          #                                                                                 tag_1="div", 
          #                                                                                 class_1="ipc-html-content"))
          

     def _export_to_file(self, 
                              # df_dict_imdb=None, 
                              filename="imdb", 
                              extension="csv"):
          #combine all pandas dataframes in the list into one big dataframe
          # init dictionary
          df_dict_imdb = { 'Title': self.__titles, 
                              'Release': self.__releases, 
                              'Audience_Rating': self.__audience_ratings,
                              'Runtime': self.__runtimes, 
                              'Genre': self.__genres, 
                              'Imdb_Rating': self.__imdb_ratings,
                              'Votes': self.__votes, 
                              'Director': self.__directors,
                              'Actors': self.__actors } # , 
                              # 'Descriptions': self.__descriptions }
                              
          # export to single csv file with header
          self.__exportOperation.export_data_to_file(df_dict_imdb,
                                                       self._csvPath,
                                                       filename,
                                                       extension) 

     # save every time multi imdb item 
     def _saveIMDbData(self):
          # the first line of input is the number of rows of the array
          size = len(self.__keys)
          imdbs = []
          for i in range(size):
               imdbs.append([ self.__keys[i],
                              self.__titles[i],
                              self.__releases[i], 
                              self.__audience_ratings[i],
                              self.__runtimes[i], 
                              self.__genres[i], 
                              self.__imdb_ratings[i],
                              self.__votes[i], 
                              self.__directors[i],
                              self.__actors[i],
                              self.__descriptions[i] ])
          self.__businessOperation.insert_multi_scrapped_data_by_list(imdbs)
     """
     -----// end protected member function: can access within the class only //-----
     """

     """
     -----// begin public member function: easily accessible from any part of the program //-----
     """
     def scrapWebsite(self): 
          print('This is base scraping')

     # save every time one imdb item 
     def saveSingleIMDbData(self,
                         titles,
                         releases,
                         audience_ratings,
                         runtimes,
                         genres,
                         imdb_ratings,
                         votes,
                         directors,
                         actors,
                         descriptions): 
          __imdb = []

          # iterate over the list using index
          for j in range(len(titles)):
               key_item = re.sub(constant.IMDB_KEY_EXPRESSION, "", titles[j])
               title_item = titles[j]
               release_item = releases[j] 
               audience_rating_item = audience_ratings[j] 
               runtime_item = runtimes[j] 
               genre_item = genres[j]  
               imdb_rating_item = imdb_ratings[j] 
               vote_item = votes[j]
               director_item = directors[j] 
               actor_item = actors[j]
               desc_item = descriptions[j] 
               __now = dt.datetime.now().strftime(constant.SHORT_DATETIME_FORMAT)

               __imdb.clear()
               __imdb.extend(
                    [    key_item.strip(), 
                         title_item.strip(), 
                         release_item.strip(), 
                         audience_rating_item.strip(), 
                         runtime_item.strip(), 
                         genre_item.strip(), 
                         imdb_rating_item.strip(), 
                         vote_item.strip(), 
                         director_item.strip(), 
                         actor_item.strip(), 
                         desc_item.strip(),
                         __now,
                         __now ]
               )
               self.__businessOperation.insert_edit_single_scrapped_data_by_list(__imdb)

     
     """
     -----// end public member function: easily accessible from any part of the program //-----
     """
  
# derived class 
# this class stop dev from 23/12/2020 
class ScrapingNonSelenium(BaseScraping): 
     # private data members
     __crawlerOperation = None
     __dtOperation = None
     __result = None
     __now = ''

     # constructor  
     def __init__(self, csvPath):
          self.__crawlerOperation = CrawlerOperation.getInstance()  # Object singleton instantiation of CrawlerOperation class
          self.__dtOperation = DateTimeOperation.getInstance()  # Object singleton instantiation of DateTimeOperation class
          
          BaseScraping.__init__(self, csvPath)
     
     # public member function  
     def scrapWebsite(self): 
          # accessing protected member functions of super class  
          self._setDriverPath(constant.CHROME_EXECUTABLE_PATH)

          # accessing protected data members of super class  
          if not path.exists(self._driverPath):
               print('Please install Chrome first.')
               return

          # accessing protected data members of super class  
          base_url = self._url
          # tmp_code: next_link = '/search/title/?groups=top_1000&count=250&start=1&sort=user_rating,desc'
          next_link = '/search/title/?groups=top_250&count=50&start=1&sort=user_rating,desc&certificates=US%3AG,US%3APG,US%3APG-13,US%3AR'
          next_href = []

          w.register('chrome',
                         None,
                         w.BackgroundBrowser(self._driverPath))
          chrome = w.get('chrome')
         
          next_href.append(next_link)

          # Let’s connect to the first page of IMDB website (for 1000 movies)
          __result =  self.__crawlerOperation.get_page_contents(base_url + next_link)

          # Let’s connect to the next page of IMDB website and get next link if exist
          # Break to the loop even if the next href is gone:
          while __result != None:
               class_next_page = __result.find('a', {'class': 'lister-page-next next-page'})

               if class_next_page != None:
                    next_link = class_next_page.get('href')
                    __result =  self.__crawlerOperation.get_page_contents(base_url + next_link)
                    next_href.append(next_link)
               else:
                    break

          __result = None
         
          for item_next_href in next_href:   # Get each item in a next_href list:
               index = next_href.index(item_next_href)

               print('\n')
               print('1. Request-Response from %s' % base_url + item_next_href)
               __result =  self.__crawlerOperation.get_page_contents(base_url + item_next_href)
               
               if __result != None:
                    # open current link in chrome browser
                    chrome.open(base_url + item_next_href, 
                              new=0, 
                              autoraise=True)
               
                    print('2. Parse and Extract title, release, rating, votes,... from imdb website')
                    # We can get a list of all distinct movies and their corresponding HTML by
                    movies = __result.findAll('div',
                                             class_='lister-item-content')

                    # we can construct a list of all movie keys
                    keysTmp =  self.__crawlerOperation.extract_attribute(movies,
                                                                           'h3',
                                                                           'lister-item-header',
                                                                           href_attribute=True)

                    
                    keys = []
                    for itemKey in keysTmp:
                         print('href: %s' % itemKey)
                         # keys.append(itemKey[:itemKey.index("/?")][-9:]) # href = '/title/tt0111161/?ref_=adv_li_tt'
                         # keys.append(itemKey[:itemKey.rindex("/")][-9:]) # href = '/title/tt0111161'

                    # we can construct a list of all movie titles
                    titles =  self.__crawlerOperation.extract_attribute(movies,
                                                                           'a')

                    # Release years can be found under the tag span and class lister-item-year text-muted unbold
                    # found in <span class="lister-item-year text-muted unbold">(2020)</span>
                    releases = self.__crawlerOperation.extract_attribute(movies,
                                                                           'span',
                                                                           'lister-item-year text-muted unbold')

                    # Audience rating can be found under the tag span and class certificate
                    # found in <span class="certificate">TV-MA</span>
                    audience_ratings = self.__crawlerOperation.extract_attribute(movies,
                                                                      'span',
                                                                      'certificate')

                    # Runtime can be found under the tag span and class runtime
                    # found in <span class="runtime">153 min</span>
                    runtimeTemp = self.__crawlerOperation.extract_attribute(movies,
                                                            'span',
                                                            'runtime')
               
                    runtimes = []
                    for itemRuntime in runtimeTemp:
                         itemRuntime = itemRuntime.replace('min', '')
                         runtimes.append(self.__dtOperation.convert_time_to_preferred_format(int(itemRuntime)))

                    # Genre can be found under the tag span and class genre
                    # found in <span class="genre">Drama</span>
                    genres = self.__crawlerOperation.extract_attribute(movies,
                                                            'span',
                                                            'genre')

                    # IMDB rating value from the data-value attribute we simply need parse the dictionary that the find method returns
                    # found in <div class="inline-block ratings-imdb-rating" name="ir" data-value="8.9">
                    imdb_ratings = self.__crawlerOperation.extract_attribute(movies,
                                                                 'div',
                                                                 'inline-block ratings-imdb-rating',
                                                                 text_attribute=False)

                    # we’ll use a dictionary to filter for the attribute name='nv’ in our findAll method and grab the first element
                    # found in <span name="nv" data-value="47467">47,467</span>
                    votes = self.__crawlerOperation.extract_attribute(movies,
                                                            'span' ,
                                                            {'name' : 'nv'},
                                                            order=0,
                                                            duplicated=True)

                    

                    # director information is located within an initial p tag and thereafter an a tag — both without class attributes making it necessary to unnest the data
                    directors = self.__crawlerOperation.extract_attribute(movies,
                                                                 'p',
                                                                 '',
                                                                 'a',
                                                                 '',
                                                                 text_attribute=True,
                                                                 order=0,
                                                                 nested=True)

                    # actors always correspond to the remaining a tags
                    actorsTemp = self.__crawlerOperation.extract_attribute(movies,
                                                            'p',
                                                            '',
                                                            'a',
                                                            '',
                                                            text_attribute=True,
                                                            order=slice(1, 5, None),
                                                            nested=True)
                    actors = []
                    for itemActor in actorsTemp:
                         actors.append(str(itemActor).replace("[","").replace("]","").replace("'",""))

                    descriptions =  self.__crawlerOperation.extract_attribute(movies,
                                                            'p',
                                                            'text-muted',
                                                            order=1,
                                                            duplicated=True)

                    # init dictionary
                    df_dict_imdb = { 'Key': keys, 
                                        'Title': titles, 
                                        'Release': releases, 
                                        'Audience_Rating': audience_ratings,
                                        'Runtime': runtimes, 
                                        'Genre': genres, 
                                        'Imdb_Rating': imdb_ratings,
                                        'Votes': votes, 
                                        'Director': directors,
                                        'Actors': actors,
                                        'Desc': descriptions }

                    print('3. Download data and export title, release, rating, votes,... to %s\imdb__nonselenium_%s.csv file' % (self._csvPath, str(index + 1)))
                    # export to multi csv file with header

                    print('4. Save imdb data into database')
                    # Calling method saveIMDbData from the parent's class (BaseScraping)
                    # BaseScraping.saveIMDbData(self,
                    #                               titles,
                    #                               releases,
                    #                               audience_ratings,
                    #                               runtimes,
                    #                               genres,
                    #                               imdb_ratings,
                    #                               votes,
                    #                               directors,
                    #                               actors,
                    #                               descriptions) 

# derived class 
class ScrapingChromeSelenium(BaseScraping): 
     # private data members

     # constructor  
     def __init__(self, csvPath):
          BaseScraping.__init__(self, csvPath)  
     
     # public member function  
     def scrapWebsite(self): 
          chrome_driver = self._initChromeWebDriver()

          # accessing protected data members of super class  
          launchUrl = self._url + "/search/title"
          
          try:
               print('1. Visit search imdb website and click submit button with filter (just 100 item, User Rating Descending,...)')
               # tmp_code: driver.implicitly_wait(5)
               # navigate to a page given by the URL
               chrome_driver.get(launchUrl)

               # set check in checkbox have "IMDb Top 100" value
               chkGroup100 = chrome_driver.find_element_by_xpath("//input[@id='groups-1']")
               chkGroup100.click()

               # ddlSearchCount = driver.find_element_by_id('search-count')
               # for optionSearchCount in ddlSearchCount.find_elements_by_tag_name('option'):
               #     if optionSearchCount.text == '100 per page':
               #         optionSearchCount.click() # select() in earlier versions of webdriver
               #         break

               # set check in checkbox have "G" value
               chkCertificates1 = chrome_driver.find_element_by_id('certificates-1') # US Certificates : G
               chkCertificates1.click()

               # set check in checkbox have "PG" value
               chkCertificates2 = chrome_driver.find_element_by_id('certificates-2') # US Certificates : PG
               chkCertificates2.click()

               # set check in checkbox have "PG-13" value
               chkCertificates3 = chrome_driver.find_element_by_id('certificates-3') # US Certificates : PG-13
               chkCertificates3.click()

               # set check in checkbox have "R" value
               chkCertificates4 = chrome_driver.find_element_by_id('certificates-4') # US Certificates : R
               chkCertificates4.click()

               ddlSort = chrome_driver.find_element_by_name('sort')
               for optionSort in ddlSort.find_elements_by_tag_name('option'):
                    if optionSort.text.strip() == 'User Rating Descending':
                         optionSort.click() # select() in earlier versions of webdriver
                         break

               #After opening the url above, Selenium clicks the specific submit button
               submit_button = chrome_driver.find_element_by_class_name('primary')
               submit_button.click() #click submit button


               print('2. Visit top 100 item website')

               #Selenium hands the page source to Beautiful Soup
               soup_level1 = BeautifulSoup(chrome_driver.page_source, 'lxml')
               divMain = soup_level1.find('div', id=re.compile("^main"))

               counter = 1  

               self._initProperties()

               print('3. Visit and Extract data from detail website')
               #Beautiful Soup finds all Job Title links on the agency page and the loop begins
               for currentSpan in divMain.findAll('span', attrs={'class':'lister-item-index'}):
                    detail_link_text = currentSpan.findNext('a')["href"]

                    #Selenium visits each Job Title page
                    detail_link = chrome_driver.find_element_by_xpath('//a[@href="' + detail_link_text + '"]')
                    detail_link.click() #click detail link
                    
                    self._extract_export_lxml(detail_link_text[:detail_link_text.rindex("/")][-9:], 
                                                  chrome_driver)

                    #Ask Selenium to click the back button
                    chrome_driver.back()
                    
                    print(' 3.%s. Parse and Extract title, release, rating, vote,... from %s' % (counter, self._url + detail_link_text))
                    
                    counter += 1

                    if counter == 6:
                         break
                    #end loop block
               #loop has completed

               #end the Selenium browser session
               chrome_driver.quit()

               print('4. Download data and export title, release, rating, votes,... to %s\imdb_selenium.csv file' % self._csvPath)
               # export to single csv file with header
               self._export_to_file(filename="imdb_selenium",
                                        extension="csv")
               
               print('5. Save imdb data into database')
               # Calling method saveIMDbData from the parent's class (BaseScraping)
               # self._saveIMDbData()
          except TimeoutException:
               raise TimeoutError("Your request has been timed out! Try overriding timeout!")
               chrome_driver.quit()
          except NoSuchElementException as __nsee:
               print(__nsee)
               chrome_driver.quit()
          except Exception as __ex:
               print(__ex)
               chrome_driver.quit()

          

class ScrapingFirefoxSelenium(BaseScraping): 
     # private data members
     
     # constructor  
     def __init__(self, csvPath):
          BaseScraping.__init__(self, csvPath)  
     
     # public member function  
     def scrapWebsite(self): 
          firefox_driver = self._initFirefoxWebDriver()
          wait = WebDriverWait(firefox_driver, 10)

          # accessing protected data members of super class  
          launchUrl = self._url + "/search/title"

          try:
               print('1. Visit search imdb website and click submit button with filter (just 100 item, User Rating Descending,...)')
               # navigate to a page given by the URL
               firefox_driver.get(launchUrl)

               # set check in checkbox have "IMDb Top 100" value
               chkGroup100 = firefox_driver.find_element_by_xpath("//input[@id='groups-1']")
               chkGroup100.click()

               # set check in checkbox have "G" value
               chkCertificates1 = firefox_driver.find_element_by_id('certificates-1') # US Certificates : G
               chkCertificates1.click()

               # set check in checkbox have "PG" value
               chkCertificates2 = firefox_driver.find_element_by_id('certificates-2') # US Certificates : PG
               chkCertificates2.click()

               # set check in checkbox have "PG-13" value
               chkCertificates3 = firefox_driver.find_element_by_id('certificates-3') # US Certificates : PG-13
               chkCertificates3.click()

               # set check in checkbox have "R" value
               chkCertificates4 = firefox_driver.find_element_by_id('certificates-4') # US Certificates : R
               chkCertificates4.click()

               ddlSort = firefox_driver.find_element_by_name('sort')
               for optionSort in ddlSort.find_elements_by_tag_name('option'):
                    if optionSort.text.strip() == 'User Rating Descending':
                         optionSort.click() # select() in earlier versions of webdriver
                         break

               #After opening the url above, Selenium clicks the specific submit button
               submit_button = firefox_driver.find_element_by_class_name('primary')
               submit_button.click() #click submit button

               print('2. Visit list IMDb website')

               #Selenium hands the page source to Beautiful Soup
               soup_level1 = BeautifulSoup(firefox_driver.page_source, 'lxml')
               divMain = soup_level1.find('div', id=re.compile("^main"))

               list_page_source = firefox_driver.page_source

               counter = 1  

               self._initProperties()
               
               print('3. Visit and Extract data from detail website')
               #Beautiful Soup finds all Job Title links on the agency page and the loop begins
               for currentSpan in divMain.findAll('span', attrs={'class':'lister-item-index'}):
                    detail_link_text = currentSpan.findNext('a')["href"]

                    detail_link = wait.until(lambda driver: driver.find_element_by_xpath('//a[contains(@href, "' + detail_link_text + '")]'))
                    detail_link.click()

                    self._extract_export_lxml(detail_link_text[:detail_link_text.rindex("/")][-9:], 
                                                  firefox_driver)

                    #Ask Selenium to click the back button
                    firefox_driver.execute_script("window.history.go(-1)") 
                    
                    print(' 3.%s. Parse and Extract title, release, rating, vote,... from %s' % (counter, self._url + detail_link_text))
                    
                    counter += 1
                    if counter == 6:
                         break
                    #end loop block
               #loop has completed

               #end the Selenium browser session
               firefox_driver.quit()

               print('4. Extract and save title, release, rating, votes,... to %s\imdb_selenium.csv file' % self._csvPath)
               # export to single csv file with header
               self._export_to_file(filename="imdb_selenium",
                                        extension="csv")
               
               print('5. Save imdb data into database')
               # Calling protected method saveIMDbData from the parent's class (BaseScraping)
               # self._saveIMDbData()
          except TimeoutException:
               raise TimeoutError("Your request has been timed out! Try overriding timeout!")
               firefox_driver.quit()
          except NoSuchElementException as __nsee:
               print(__nsee)
               firefox_driver.quit()
          except Exception as __ex:
               print(__ex)
               firefox_driver.quit()


class BusinessOperation:
     __instance = None
     __now = ''

     @staticmethod 
     def getInstance():
          # Static access method.
          if BusinessOperation.__instance == None:
               BusinessOperation()
          return BusinessOperation.__instance

     def __init__(self):  # init method or constructor   
          # Virtually private constructor.
          if BusinessOperation.__instance != None:
               raise Exception("This class is a singleton!")
          else:
               BusinessOperation.__instance = self

     def insert_edit_scrapped_data_by_dict(self, 
                                             df_dict, 
                                             isClearAll):
          # init method or constructor                          
          sd = StoringData.getInstance()

          # 1. First, connect to the SQLite database by creating a Connection object
          conn = sd.create_connection(os.getcwd() + constant.DB_FILE_PATH)

          # 2. Second, insert data by dataframe.
          with conn:
               if isClearAll:
                    sd.delete_all_imdb(conn)
               read_clients = pd.DataFrame(df_dict)  # We use pandas to visualize the data
               read_clients.to_sql('IMDb', conn, if_exists='append', index = False) # Insert/Update the values from the dataframe into the table 'IMDb'
               # read_clients.set_index('Key', inplace=True)  

          sd.close_connection(conn)

     # insert or edit single item imdb
     def insert_edit_single_scrapped_data_by_list(self, 
                                             imdb):
          # 1. init method or constructor                          
          sd = StoringData.getInstance()
          # 2. connect to the SQLite database by creating a Connection object
          conn = sd.create_connection(os.getcwd() + constant.DB_FILE_PATH)
          with conn:
               # 3. check item exist or not by call read_imdb def.
               imdb_select  = sd.read_imdb(conn, imdb[0]) 
               if imdb_select == None:
                    # 3.1 insert data by call create_imdb def.
                    return sd.create_imdb(conn, imdb)  
               else:
                    __now = dt.datetime.now().strftime(constant.SHORT_DATETIME_FORMAT)
                    # 3.2 update Modified_On data by call update_imdb_modifiedOn def.
                    return sd.update_imdb_modifiedOn(conn, __now, imdb_select[0]) 
               sd.vacuum_imdb_sqlite(conn)
          sd.close_connection(conn)

     # insert multi item imdb
     def insert_multi_scrapped_data_by_list(self, 
                                             imdbs):
          # 1. init method or constructor                          
          sd = StoringData.getInstance()
          # 2. connect to the SQLite database by creating a Connection object
          conn = sd.create_connection(os.getcwd() + constant.DB_FILE_PATH)
          with conn:
               # 3. delete all by call delete_all_imdb def.
               sd.delete_all_imdb(conn)
               # 4. insert data by call create_imdb def.
               return sd.create_multi_imdb(conn, imdbs) 
               sd.vacuum_imdb_sqlite(conn)
          sd.close_connection(conn)