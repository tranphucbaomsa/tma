# import CrawlerOperation, CsvOperation, DateTimeOperation class in CrawlerLibrary.py
# import StoringData class in sqlite_process.py 
# import constant
from utilities.CrawlerLibrary import CrawlerOperation, CsvOperation, DateTimeOperation 
from data_layer.sqlite_process import StoringData
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
import datetime as dt

# super class 
class BaseScraping: 
     # private data members 
     _url = ""
     _csvPath = ""
     _driverPath = ""

     # protected data members 
     __businessOperation = None
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
     
     # constructor 
     def __init__(self, csvPath):   
          self._url = "https://www.imdb.com" 
          self._csvPath = csvPath 
          self.__businessOperation = BusinessOperation.getInstance()  # Object singleton instantiation of BusinessOperation class

     # private member function
     def _getDriverPath(self):
         return self._driverPath

     # private member function
     def _setDriverPath(self, value):
         self._driverPath = value

     # public member function  
     def scrapWebsite(self): 
          print('This is base scraping')  

     # public member function  
     def saveIMDbData(self,
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
  
# derived class 
class ScrapingNonSelenium(BaseScraping): 
     # private data members
     __crawlerOperation = None
     __csvOperation = None
     __dtOperation = None
     __result = None
     __now = ''

     # constructor  
     def __init__(self, csvPath):
          self.__crawlerOperation = CrawlerOperation.getInstance()  # Object singleton instantiation of CrawlerOperation class
          self.__csvOperation = CsvOperation.getInstance()  # Object singleton instantiation of CsvOperation class
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

                    # we can construct a list of all movie titles
                    titlesTemp =  self.__crawlerOperation.extract_attribute(movies,
                                                            'a')

                    # Release years can be found under the tag span and class lister-item-year text-muted unbold
                    # found in <span class="lister-item-year text-muted unbold">(2020)</span>
                    releases = self.__crawlerOperation.extract_attribute(movies,
                                                            'span',
                                                            'lister-item-year text-muted unbold')
                    
                    titles = []
                    for i in range(len(titlesTemp)):
                         titles.append(titlesTemp[i] + ' ' + releases[i])

                    keys = []
                    for j in range(len(titles)):
                         keys.append(re.sub("[^a-zA-Z0-9]", "", titles[j]))

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
                    df_dict_imdb = { 'Title': titles, 
                                        'Release': releases, 
                                        'Audience_Rating': audience_ratings,
                                        'Runtime': runtimes, 
                                        'Genre': genres, 
                                        'Imdb_Rating': imdb_ratings,
                                        'Votes': votes, 
                                        'Director': directors,
                                        'Actors': actors,
                                        'Desc': descriptions }

                    # export to multi csv file with header
                    print('3. Download data and export title, release, rating, votes,... to %s\imdb__nonselenium_%s.csv file' % (self._csvPath, str(index + 1)))
                    self.__csvOperation.export_csv("imdb_nonselenium_" + str(index + 1),
                                             df_dict_imdb,
                                             self._csvPath)

                    print('4. Save imdb data into database')
                   

                    # Calling method saveIMDbData from the parent's class (BaseScraping)
                    BaseScraping.saveIMDbData(self,
                                                  titles,
                                                  releases,
                                                  audience_ratings,
                                                  runtimes,
                                                  genres,
                                                  imdb_ratings,
                                                  votes,
                                                  directors,
                                                  actors,
                                                  descriptions) 

# derived class 
class ScrapingSelenium(BaseScraping): 
     # private data members
     __csvOperation = None

     # constructor  
     def __init__(self, csvPath):
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
          
          # driver.implicitly_wait(5)
          driver.get(launchUrl)

          # set check in checkbox have "IMDb Top 100" value
          chkGroup100 = driver.find_element_by_xpath("//input[@id='groups-1']")
          chkGroup100.click()

          # ddlSearchCount = driver.find_element_by_id('search-count')
          # for optionSearchCount in ddlSearchCount.find_elements_by_tag_name('option'):
          #     if optionSearchCount.text == '100 per page':
          #         optionSearchCount.click() # select() in earlier versions of webdriver
          #         break

          # set check in checkbox have "G" value
          chkCertificates1 = driver.find_element_by_id('certificates-1') # US Certificates : G
          chkCertificates1.click()

           # set check in checkbox have "PG" value
          chkCertificates2 = driver.find_element_by_id('certificates-2') # US Certificates : PG
          chkCertificates2.click()

           # set check in checkbox have "PG-13" value
          chkCertificates3 = driver.find_element_by_id('certificates-3') # US Certificates : PG-13
          chkCertificates3.click()

           # set check in checkbox have "R" value
          chkCertificates4 = driver.find_element_by_id('certificates-4') # US Certificates : R
          chkCertificates4.click()

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

          print('3. Visit and Extract data from detail website')

          #Beautiful Soup finds all Job Title links on the agency page and the loop begins
          for currentSpan in divMain.findAll('span', attrs={'class':'lister-item-index'}):
               #Selenium visits each Job Title page
               detail_link = driver.find_element_by_xpath('//a[@href="' + currentSpan.findNext('a')["href"] + '"]')
               detail_link.click() #click detail link

               #Selenium hands of the source of the specific job page to Beautiful Soup
               soup_level2 = BeautifulSoup(driver.page_source, 'lxml')
               divTitleOverviewWidget = soup_level2.find("div", id_="title-overview-widget")

               try:
                    titles.append(driver.find_element_by_xpath('//h1[@class=""]').text.strip() if driver.find_element_by_xpath('//h1[@class=""]') != None else "") 
                    releases.append(driver.find_element_by_xpath('//span[@id="titleYear"]').text if driver.find_element_by_xpath('//span[@id="titleYear"]') != None else "")  

                    divSubtext = driver.find_element_by_css_selector('div.subtext')
                    arrSubtext = divSubtext.text.split(" | ") if divSubtext != None else None
                    if arrSubtext != None:
                         audience_ratings.append(arrSubtext[0])
                         runtimes.append(arrSubtext[1])
                         genres.append(arrSubtext[2])

                    divImdbRating = driver.find_element_by_css_selector('div.imdbRating')
                    divRatingValue = divImdbRating.find_element_by_css_selector('div.ratingValue')
                    imdb_ratings.append(divRatingValue.find_element_by_tag_name('strong').find_element_by_tag_name('span').text if divRatingValue.find_element_by_tag_name('strong').find_element_by_tag_name('span') != None else ""   )
                    votes.append(divImdbRating.find_element_by_css_selector('a span.small').text if divImdbRating.find_element_by_css_selector('a span.small') != None else "")
                    descriptions.append(driver.find_element_by_xpath('//div[@class="ipc-html-content ipc-html-content--base"]').text.strip() if driver.find_element_by_xpath('//div[@class="ipc-html-content ipc-html-content--base"]') != None else "")

                    divPlotSummary = driver.find_element_by_css_selector('div.plot_summary')
                    divCreditSummaryItem =  divPlotSummary.find_elements_by_css_selector('div.credit_summary_item')
                    directors.append(divCreditSummaryItem[0].find_element_by_css_selector('a').text if divCreditSummaryItem[0].find_element_by_css_selector('a') != None else "" )
                    arrActor  = divCreditSummaryItem[2].find_elements_by_css_selector('a')

                    # initialize an empty string 
                    actor_item = ""
                    # traverse in the string   
                    for actor in arrActor:  
                         indexActor = arrActor.index(actor)
                         if indexActor < len(arrActor) - 1:
                              # actor_item += "'" + actor.text + "'" + (", " if indexActor < len(arrActor) - 2 else "")
                              actor_item += actor.text + (", " if indexActor < len(arrActor) - 2 else "")

                    actors.append(actor_item)
               except NoSuchElementException:
                    pass

               #Ask Selenium to click the back button
               driver.execute_script("window.history.go(-1)") 
               # tmp_code: driver.back()
               
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
          df_dict_imdb = { 'Title': titles, 
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
          
          print('5. Save imdb data into database')
          # Calling method saveIMDbData from the parent's class (BaseScraping)
          BaseScraping.saveIMDbData(self,
                                        titles,
                                        releases,
                                        audience_ratings,
                                        runtimes,
                                        genres,
                                        imdb_ratings,
                                        votes,
                                        directors,
                                        actors,
                                        descriptions) 


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
          # 1. First, init method or constructor                          
          sd = StoringData.getInstance()
          # 2. Second, connect to the SQLite database by creating a Connection object
          conn = sd.create_connection(os.getcwd() + constant.DB_FILE_PATH)
          with conn:
               # 3. Third, delete all data have empty key by call delete_all_empty_imdb_key def.
               sd.delete_all_empty_imdb_key(conn)
               # 4. Four, check item exist or not by call read_imdb def.
               imdb_select  = sd.read_imdb(conn, imdb[0]) 
               if imdb_select == None:
                    # 4.1 Third, insert data by call create_imdb def.
                    return sd.create_imdb(conn, imdb)  
               else:
                    __now = dt.datetime.now().strftime(constant.SHORT_DATETIME_FORMAT)
                    # 4.2 update Modified_On data by call update_imdb_modifiedOn def.
                    return sd.update_imdb_modifiedOn(conn, __now, imdb_select[0]) 
               sd.vacuum_imdb_sqlite(conn)
          sd.close_connection(conn)