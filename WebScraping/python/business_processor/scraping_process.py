# import CrawlerOperation, CsvOperation, DateTimeOperation class in CrawlerLibrary.py
# import StoringData class in sqlite_process.py 
# import constant
from utilities.CrawlerLibrary import CrawlerOperation, CsvOperation, DateTimeOperation 
from data_processor.sqlite_process import StoringData
from utilities import constant

# import the necessary packages
# selenium automates browser
import webbrowser as w
import os
from os import path
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import re  # Regular expression operations
from bs4 import BeautifulSoup
import pandas as pd
import datetime

# super class 
class BaseScraping: 
     # protected data members 
     _url = ""
     _csvPath = ""
     _driverPath = ""
     
     # constructor 
     def __init__(self, csvPath):   
          self._url = "https://www.imdb.com" 
          self._csvPath = csvPath 

     # private member function
     def _getDriverPath(self):
         return self._driverPath

     # private member function
     def _setDriverPath(self, value):
         self._driverPath = value

     # public member function  
     def scrapWebsite(self): 
          print('This is base scraping')  
  
# derived class 
class ScrapingNonSelenium(BaseScraping): 
     # private data members
     __crawlerOperation = None
     __csvOperation = None
     __dtOperation = None
     __businessOperation = None

     # constructor  
     def __init__(self, csvPath):
          self.__crawlerOperation = CrawlerOperation.getInstance()  # Object singleton instantiation of CrawlerOperation class
          self.__csvOperation = CsvOperation.getInstance()  # Object singleton instantiation of CsvOperation class
          self.__dtOperation = DateTimeOperation.getInstance()  # Object singleton instantiation of DateTimeOperation class
          self.__businessOperation = BusinessOperation.getInstance()  # Object singleton instantiation of BusinessOperation class
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
          next_link = '/search/title/?groups=top_1000&count=250&start=1&sort=user_rating,desc'
          next_href = []

          w.register('chrome',
                         None,
                         w.BackgroundBrowser(self._driverPath))

          chrome = w.get('chrome')
         
          next_href.append(next_link)

          # Let’s connect to the first page of IMDB website (for 1000 movies)
          result =  self.__crawlerOperation.get_page_contents(base_url + next_link)

          # Let’s connect to the next page of IMDB website and get next link if exist
          # Break to the loop even if the next href is gone:
          while result != None:
               class_next_page = result.find('a', {'class': 'lister-page-next next-page'})

               if class_next_page != None:
                    next_link = class_next_page.get('href')
                    result =  self.__crawlerOperation.get_page_contents(base_url + next_link)
                    next_href.append(next_link)
               else:
                    break

          imdb = []
          key_item = ''
          title_item = ''
          release_item = ''
          audience_rating_item = ''
          runtime_item = ''
          genre_item = '' 
          imdb_rating_item = ''
          vote_item = '' 
          director_item = ''
          actor_item = ''
          desc_item = ''
          now = ''
         
          for item_next_href in next_href:   # Get each item in a next_href list:
               imdb.clear()

               index = next_href.index(item_next_href)

               print('\n')
               print('1. Request-Response from %s' % base_url + item_next_href)
               result =  self.__crawlerOperation.get_page_contents(base_url + item_next_href)
               
               # open current link in chrome browser
               chrome.open(base_url + item_next_href, 
                         new=0, 
                         autoraise=True)
               time.sleep(1)
          
               print('2. Parse and Extract title, release, rating, votes,... from imdb website')
               # We can get a list of all distinct movies and their corresponding HTML by
               movies = result.findAll('div',
                                        class_='lister-item-content')

               # we can construct a list of all movie titles
               titlesTemp =  self.__crawlerOperation.extract_attribute(movies,
                                                       'a')

               # Release years can be found under the tag span and class lister-item-year text-muted unbold
               # found in <span class="lister-item-year text-muted unbold">(2020)</span>
               release = self.__crawlerOperation.extract_attribute(movies,
                                                       'span',
                                                       'lister-item-year text-muted unbold')
               
               titles = []
               for i in range(len(titlesTemp)):
                    titles.append(titlesTemp[i] + ' ' + release[i])

               # Audience rating can be found under the tag span and class certificate
               # found in <span class="certificate">TV-MA</span>
               audience_rating = self.__crawlerOperation.extract_attribute(movies,
                                                                 'span',
                                                                 'certificate')

               # Runtime can be found under the tag span and class runtime
               # found in <span class="runtime">153 min</span>
               runtimeTemp = self.__crawlerOperation.extract_attribute(movies,
                                                       'span',
                                                       'runtime')
              
               runtime = []
               for itemRuntime in runtimeTemp:
                    itemRuntime = itemRuntime.replace('min', '')
                    runtime.append(self.__dtOperation.convert_time_to_preferred_format(int(itemRuntime)))

               # Genre can be found under the tag span and class genre
               # found in <span class="genre">Drama</span>
               genre = self.__crawlerOperation.extract_attribute(movies,
                                                       'span',
                                                       'genre')

               # IMDB rating value from the data-value attribute we simply need parse the dictionary that the find method returns
               # found in <div class="inline-block ratings-imdb-rating" name="ir" data-value="8.9">
               imdb_rating = self.__crawlerOperation.extract_attribute(movies,
                                                            'div',
                                                            'inline-block ratings-imdb-rating',
                                                            text_attribute=False)

               # we’ll use a dictionary to filter for the attribute name='nv’ in our findAll method and grab the first element
               # found in <span name="nv" data-value="47467">47,467</span>
               votes = self.__crawlerOperation.extract_attribute(movies,
                                                       'span' ,
                                                       {'name' : 'nv'},
                                                       text_attribute=False,
                                                       order=0)

               

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
               actors = self.__crawlerOperation.extract_attribute(movies,
                                                       'p',
                                                       '',
                                                       'a',
                                                       '',
                                                       text_attribute=True,
                                                       order=slice(1, 5, None),
                                                       nested=True)

               descriptions =  self.__crawlerOperation.extract_attribute(movies,
                                                       'p',
                                                       'text-muted',
                                                       order=1,
                                                       duplicated=True)

               # init dictionary
               df_dict_imdb = {'Title': titles, 
                              'Release': release, 
                              'Audience_Rating': audience_rating,
                              'Runtime': runtime, 
                              'Genre': genre, 
                              'Imdb_Rating': imdb_rating,
                              'Votes': votes, 
                              'Director': directors,
                              'Actors': actors,
                              'Desc': descriptions }

               # export to multi csv file with header
               print('3. Download data and export title, release, rating, votes,... to %s\imdb__nonselenium_%s.csv file' % (self._csvPath, str(index + 1)))
               self.__csvOperation.export_csv("imdb_nonselenium_" + str(index + 1),
                                        df_dict_imdb,
                                        self._csvPath)

               for j in range(len(titles)):
                    key_item = re.sub("[^a-zA-Z0-9]", "", titlesTemp[j])
                    title_item = titles[j]
                    release_item = release[j]
                    audience_rating_item = audience_rating[j] 
                    runtime_item =  runtime[j]
                    genre_item =  genre[j]
                    imdb_rating_item = imdb_rating[j] 
                    vote_item = votes[j] 
                    director_item = directors[j] 
                    actor_item = actors[j] 
                    desc_item = descriptions[j]
                    now = datetime.datetime.now()

                    imdb.extend(
                         [    key_item, 
                              title_item, 
                              release_item, 
                              audience_rating_item, 
                              runtime_item, 
                              genre_item, 
                              imdb_rating_item, 
                              vote_item, 
                              director_item, 
                              actor_item, 
                              desc_item.strip(),
                              now.strftime(constant.SHORT_DATETIME_FORMAT),
                              now.strftime(constant.SHORT_DATETIME_FORMAT) ]
                    )

                    
               print('imdb key: %s' % imdb[0])
               # print('4. Save imdb data into database')
               # self.__businessOperation.insert_scrapped_data_by_list(imdb)

# derived class 
class ScrapingSelenium(BaseScraping): 
     # private data members
     __businessOperation = None
     __csvOperation = None

     # constructor  
     def __init__(self, csvPath):
          self.__businessOperation = BusinessOperation.getInstance()  # Object singleton instantiation of BusinessOperation class
          self.__csvOperation = CsvOperation.getInstance()  # Object singleton instantiation of CsvOperation class
          BaseScraping.__init__(self, csvPath)  
     
     # public member function  
     def scrapWebsite(self): 
          # accessing protected member functions of super class 
          #os.getcwd(): get current working directory
          self._setDriverPath(os.getcwd() + constant.CHROME_DRIVER_PATH)

          # accessing protected data members of super class  
          launchUrl = self._url + "/search/title"

          # Define Chrome options to open the window in maximized mode
          options = webdriver.ChromeOptions()
          # options.headless = True # hide browser
          options.add_argument("--start-maximized")

          print('1. Visit search imdb website and click submit button with filter (just 100 item, User Rating Descending)')

          # create a new Chrome session
          driver = webdriver.Chrome(executable_path=self._driverPath, options=options)
          
          driver.implicitly_wait(30)
          driver.get(launchUrl)

          # set check in checkbox have "IMDb Top 100" value
          chkGroup100 = driver.find_element_by_xpath("//input[@id='groups-1']")
          chkGroup100.click()

          # ddlSearchCount = driver.find_element_by_id('search-count')
          # for optionSearchCount in ddlSearchCount.find_elements_by_tag_name('option'):
          #     if optionSearchCount.text == '100 per page':
          #         optionSearchCount.click() # select() in earlier versions of webdriver
          #         break

          ddlSort = driver.find_element_by_name('sort')
          for optionSort in ddlSort.find_elements_by_tag_name('option'):
               if optionSort.text.strip() == 'User Rating Descending':
                    optionSort.click() # select() in earlier versions of webdriver
                    break

          #After opening the url above, Selenium clicks the specific submit button
          submit_button = driver.find_element_by_class_name('primary')
          submit_button.click() #click submit button

          print('2. Visit top 100 item website')

          #Selenium hands the page source to Beautiful Soup
          soup_level1 = BeautifulSoup(driver.page_source, 'lxml')
          divMain = soup_level1.find('div', id=re.compile("^main"))

          counter = 1  
          keys = [] #empty list
          titles = [] #empty list 
          releases = []
          audience_ratings = []
          runtimes = []
          genres = [] 
          imdb_ratings = []
          votes = [] 
          directors = []
          actors = []
          descriptions = []
          imdb = []

          key_item = ''
          title_item = ''
          release_item = ''
          audience_rating_item = ''
          runtime_item = ''
          genre_item = '' 
          imdb_rating_item = ''
          vote_item = '' 
          director_item = ''
          actor_item = ''
          desc_item = ''
          now = ''

          print('3. Visit and Extract data from detail website')

          #Beautiful Soup finds all Job Title links on the agency page and the loop begins
          for currentSpan in divMain.findAll('span', attrs={'class':'lister-item-index'}):
               imdb.clear() 
               

               #Selenium visits each Job Title page
               detail_link = driver.find_element_by_xpath('//a[@href="' + currentSpan.findNext('a')["href"] + '"]')
               detail_link.click() #click detail link

               #Selenium hands of the source of the specific job page to Beautiful Soup
               soup_level2 = BeautifulSoup(driver.page_source, 'lxml')
               divTitleOverviewWidget = soup_level2.find("div", id_="title-overview-widget")

               try:
                    title_item = driver.find_element_by_xpath('//h1[@class=""]').text if driver.find_element_by_xpath('//h1[@class=""]') != None else ""    
                    release_item = driver.find_element_by_xpath('//span[@id="titleYear"]').text if driver.find_element_by_xpath('//span[@id="titleYear"]') != None else ""  

                    divSubtext = driver.find_element_by_css_selector('div.subtext')
                    arrSubtext = divSubtext.text.split(" | ") if divSubtext != None else None
                    if arrSubtext != None:
                         audience_rating_item = arrSubtext[0]
                         runtime_item = arrSubtext[1]
                         genre_item = arrSubtext[2]

                    divImdbRating = driver.find_element_by_css_selector('div.imdbRating')
                    divRatingValue = divImdbRating.find_element_by_css_selector('div.ratingValue')
                    imdb_rating_item = divRatingValue.find_element_by_tag_name('strong').find_element_by_tag_name('span').text if divRatingValue.find_element_by_tag_name('strong').find_element_by_tag_name('span') != None else ""   
                    vote_item = divImdbRating.find_element_by_css_selector('a span.small').text if divImdbRating.find_element_by_css_selector('a span.small') != None else ""  
                    desc_item = driver.find_element_by_xpath('//div[@class="ipc-html-content ipc-html-content--base"]').text if driver.find_element_by_xpath('//div[@class="ipc-html-content ipc-html-content--base"]') != None else "" 

                    divPlotSummary = driver.find_element_by_css_selector('div.plot_summary')
                    divCreditSummaryItem =  divPlotSummary.find_elements_by_css_selector('div.credit_summary_item')
                    director_item = divCreditSummaryItem[0].find_element_by_css_selector('a').text if divCreditSummaryItem[0].find_element_by_css_selector('a') != None else ""  
                    arrActor  = divCreditSummaryItem[2].find_elements_by_css_selector('a')

                    # initialize an empty string 
                    actor_item = "["
                    # traverse in the string   
                    for actor in arrActor:  
                         indexActor = arrActor.index(actor)
                         if indexActor < len(arrActor) - 1:
                              actor_item += "'" + actor.text + "'" + ("," if indexActor < len(arrActor) - 2 else "")
                    actor_item += "]"

                    # title_item = re.sub("[^a-zA-Z0-9:' ]", "", title_item)
                    key_item = re.sub("[^a-zA-Z0-9]", "", title_item)
               except NoSuchElementException:
                    pass

               #Store the dataframe in a list
               keys.append(key_item)
               titles.append(title_item.strip())
               releases.append(release_item)
               audience_ratings.append(audience_rating_item)
               runtimes.append(runtime_item)
               genres.append(genre_item)
               imdb_ratings.append(imdb_rating_item)
               votes.append(vote_item)
               directors.append(director_item)
               actors.append(actor_item)
               descriptions.append(desc_item.strip())
               now = datetime.datetime.now()

               imdb.extend(
                    [    key_item, 
                         title_item.strip(), 
                         release_item, 
                         audience_rating_item, 
                         runtime_item, 
                         genre_item, 
                         imdb_rating_item, 
                         vote_item, 
                         director_item, 
                         actor_item, 
                         desc_item.strip(),
                         now.strftime(constant.SHORT_DATETIME_FORMAT),
                         now.strftime(constant.SHORT_DATETIME_FORMAT) ]
               )

               self.__businessOperation.insert_scrapped_data_by_list(imdb)
               
               # #Ask Selenium to click the back button
               driver.execute_script("window.history.go(-1)") 
               # driver.back()
               
               print(' 3.%s. Parse and Extract title, release, rating, vote,... from %s' % (counter, self._url + currentSpan.findNext('a')["href"]))
               
               counter += 1

               if counter == 6:
                    break
               #end loop block
               
          #loop has completed

          #end the Selenium browser session
          driver.quit()

          #combine all pandas dataframes in the list into one big dataframe
          # init dictionary
          df_dict_imdb = {'Title': titles, 
                              'Release': releases, 
                              'Audience_Rating': audience_ratings,
                              'Runtime': runtimes, 
                              'Genre': genres, 
                              'Imdb_Rating': imdb_ratings,
                              'Votes': votes, 
                              'Director': directors,
                              'Actors': actors,
                              'Desc': descriptions }

          # export to single csv file with header
          print('4. Download data and export title, release, rating, votes,... to %s\imdb_selenium.csv file' % self._csvPath)
          self.__csvOperation.export_csv("imdb_selenium",
                                             df_dict_imdb,
                                             self._csvPath) 
          


class BusinessOperation:
     __instance = None

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

     def insert_scrapped_data_by_dict(self, 
                                        df_dict):
          # init method or constructor                          
          sd = StoringData.getInstance()

          # 1. First, connect to the SQLite database by creating a Connection object
          conn = sd.create_connection(os.getcwd() + constant.DB_FILE_PATH)

          # 2.Second, create a Cursor object by calling the cursor method of the Connection object.
          cur = conn.cursor()

          # 3. Third, insert data by dataframe.
          with conn:
               read_clients = pd.DataFrame(df_dict)  # We use pandas to visualize the data
               read_clients.to_sql('IMDb', conn, if_exists='append', index = False) # Insert the values from the dataframe into the table 'IMDb' 


     def insert_scrapped_data_by_list(self, 
                                        imdb):
          # 1. First, init method or constructor                          
          sd = StoringData.getInstance()

          # 2. Second, connect to the SQLite database by creating a Connection object
          conn = sd.create_connection(os.getcwd() + constant.DB_FILE_PATH)

          # 3. Third, insert data by call create_imdb def.
          with conn:
               imdb_select  = sd.read_imdb(conn, imdb[0])
               if imdb_select == None:
                    return sd.create_imdb(conn, imdb)
               else:
                    as_list = list(imdb_select)
                    del as_list[len(as_list) - 2]
                    as_list[len(as_list) - 1] = datetime.datetime.now().strftime(constant.SHORT_DATETIME_FORMAT)
                    return sd.update_imdb(conn, tuple(as_list))