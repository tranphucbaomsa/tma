# import CrawlerOperation and CsvOperation class
# defined in CrawlerLibrary.py
from utilities.CrawlerLibrary import CrawlerOperation
from utilities.CrawlerLibrary import CsvOperation

# import the necessary packages
# selenium automates browser
import webbrowser as w
import time
import pandas as pd
import re  # Regular expression operations
from tabulate import tabulate
from bs4 import BeautifulSoup
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.webdriver.common.by import By

class MyListener(AbstractEventListener):
    def before_navigate_to(self, url, driver):
        print("Before navigating to ", url)

    def after_navigate_to(self, url, driver):
        # titles = driver.find_elements_by_css_selector('.lister-item-header a')
        # release = 
        # audience_rating = 
        # runtime = 
        # genre = 
        # imdb_rating = 
        # votes = 
        # earnings = 
        # directors = 
        # actors = 
        print("After navigating to ", url)

    def before_navigate_back(self, driver):
        try:
            divTitleWrapper = driver.find_element_by_css_selector('div.title_wrapper')
            title_item = divTitleWrapper.find_element_by_tag_name('h1').text
            release_item = divTitleWrapper.find_element_by_css_selector('#titleYear').text

            divSubtext = divTitleWrapper.find_element_by_css_selector('div.subtext')
            arrSubtext = divSubtext.text.split(" | ")
            audience_rating_item = arrSubtext[0]
            runtime_item = arrSubtext[1]
            genre_item = arrSubtext[2]

            divImdbRating = driver.find_element_by_css_selector('div.imdbRating')
            divRatingValue = divImdbRating.find_element_by_css_selector('div.ratingValue')
            imdb_rating_item = divRatingValue.find_element_by_tag_name('strong').find_element_by_tag_name('span').text
            earnings_item = divImdbRating.find_element_by_css_selector('a span.small').text

            divPlotSummary = driver.find_element_by_css_selector('div.plot_summary')
            divCreditSummaryItem = divPlotSummary.find_elements_by_css_selector('div.credit_summary_item')
            director_item = divCreditSummaryItem[0].find_element_by_css_selector('a').text
            arrActor  = divCreditSummaryItem[2].find_elements_by_css_selector('a')

            # initialize an empty string 
            actor_item = "["
            # traverse in the string   
            for actor in arrActor:  
                indexActor = arrActor.index(actor)
                if indexActor < len(arrActor) - 1:
                    actor_item += "'" + actor.text + "'" + ("," if indexActor < len(arrActor) - 2 else "")
            actor_item += "]"

            title_item = re.sub("[^a-zA-Z]", "", title_item)
            print("title_item: %s" % title_item)
            print("release_item: %s" % release_item)
            print("audience_rating_item: %s" % audience_rating_item)
            print("runtime_item: %s" % runtime_item)
            print("genre_item: %s" % genre_item)
            print("imdb_rating_item: %s" % imdb_rating_item)
            print("earnings_item: %s" % earnings_item)
            print("director_item: %s" % director_item)
            print("actor_item: %s" % actor_item)
        except NoSuchElementException:
            pass
        print("before navigating back ", driver.current_url)

    def after_navigate_back(self, driver):
        print("After navigating back ", driver.current_url)

    def before_navigate_forward(self, driver):
        print("before navigating forward ", driver.current_url)

    def after_navigate_forward(self, driver):
        print("After navigating forward ", driver.current_url)

    def before_find(self, by, value, driver):
        print("before find")

    def after_find(self, by, value, driver):
        print("after_find")

    def before_click(self, element, driver):
        print("before_click")

    def after_click(self, element, driver):
        print("after_click")

    def before_change_value_of(self, element, driver):
        print("before_change_value_of")

    def after_change_value_of(self, element, driver):
        print("after_change_value_of")

    def before_execute_script(self, script, driver):
        print("before_execute_script")

    def after_execute_script(self, script, driver):
        print("after_execute_script")

    def before_close(self, driver):
        print("tttt")

    def after_close(self, driver):
        print("before_close")

    def before_quit(self, driver):
        print("before_quit")

    def after_quit(self, driver):
        print("after_quit")

    def on_exception(self, exception, driver):
        print("on_exception")


def scraping_without_selenium(csv_path):
    crawlerOperation = CrawlerOperation.getInstance()  # Object singleton instantiation of CrawlerOperation class
    csvOperation = CsvOperation.getInstance()  # Object singleton instantiation of CsvOperation class
    url = 'https://www.imdb.com'
    next_href = []

    w.register('chrome',
                None,
                w.BackgroundBrowser(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"))
    chrome = w.get('chrome')

    # tmp_code:  next_link = '/search/title/?count=250&groups=top_1000&sort=user_rating%27'
    next_link = '/search/title/?groups=top_1000&count=250&start=1&sort=user_rating,desc'
    next_href.append(next_link)

    # Let’s connect to the first page of IMDB website (for 1000 movies)
    result = crawlerOperation.get_page_contents(url + next_link)

    # Let’s connect to the next page of IMDB website and get next link if exist
    # Break to the loop even if the next href is gone:
    while result != None:
        class_next_page = result.find('a', {'class': 'lister-page-next next-page'})

        if class_next_page != None:
            next_link = class_next_page.get('href')
            result = crawlerOperation.get_page_contents(url + next_link)
            next_href.append(next_link)
        else:
            break

    if result != None:
        for item_next_href in next_href:   # Get each item in a next_href list:
            index = next_href.index(item_next_href)

            print('\n')
            print('1. Request-Response from %s' % url + item_next_href)
            result = crawlerOperation.get_page_contents(url + item_next_href)
            
            # open current link in chrome browser
            chrome.open(url + item_next_href, 
                        new=0, 
                        autoraise=True)
            time.sleep(1)
        
            print('2. Parse and Extract title, release, rating, votes,... from imdb website')
            # We can get a list of all distinct movies and their corresponding HTML by
            movies = result.findAll('div',
                                    class_='lister-item-content')

            # we can construct a list of all movie titles
            titles = crawlerOperation.extract_attribute(movies,
                                                    'a')

            # Release years can be found under the tag span and class lister-item-year text-muted unbold
            # found in <span class="lister-item-year text-muted unbold">(2020)</span>
            release = crawlerOperation.extract_attribute(movies,
                                                    'span',
                                                    'lister-item-year text-muted unbold')

            # Audience rating can be found under the tag span and class certificate
            # found in <span class="certificate">TV-MA</span>
            audience_rating = crawlerOperation.extract_attribute(movies,
                                                            'span',
                                                            'certificate')

            # Runtime can be found under the tag span and class runtime
            # found in <span class="runtime">153 min</span>
            runtime = crawlerOperation.extract_attribute(movies,
                                                    'span',
                                                    'runtime')

            # Genre can be found under the tag span and class genre
            # found in <span class="genre">Drama</span>
            genre = crawlerOperation.extract_attribute(movies,
                                                    'span',
                                                    'genre')

            # IMDB rating value from the data-value attribute we simply need parse the dictionary that the find method returns
            # found in <div class="inline-block ratings-imdb-rating" name="ir" data-value="8.9">
            imdb_rating = crawlerOperation.extract_attribute(movies,
                                                        'div',
                                                        'inline-block ratings-imdb-rating',
                                                        False)

            # we’ll use a dictionary to filter for the attribute name='nv’ in our findAll method and grab the first element
            # found in <span name="nv" data-value="47467">47,467</span>
            votes = crawlerOperation.extract_attribute(movies,
                                                    'span' ,
                                                    {'name' : 'nv'},
                                                    False,
                                                    0)

            # we’ll use a dictionary to filter for the attribute name='nv’ in our findAll method and grab the second element
            # found in <span name="nv" data-value="53,800,000">$53.80M</span>
            earnings = crawlerOperation.extract_attribute(movies,
                                                    'span' ,
                                                    {'name' : 'nv'},
                                                    False,
                                                    1)

            # director information is located within an initial p tag and thereafter an a tag — both without class attributes making it necessary to unnest the data
            directors = crawlerOperation.extract_attribute(movies,
                                                        'p',
                                                        '',
                                                        'a',
                                                        '',
                                                        True,
                                                        0,
                                                        True)

            # actors always correspond to the remaining a tags
            actors = crawlerOperation.extract_attribute(movies,
                                                    'p',
                                                    '',
                                                    'a',
                                                    '',
                                                    True,
                                                    slice(1, 5, None),
                                                    True)

            # init dictionary
            df_dict_imdb = {'Title': titles, 
                        'Relase': release, 
                        'Audience Rating': audience_rating,
                        'Runtime': runtime, 
                        'Genre': genre, 
                        'IMDB Rating': imdb_rating,
                        'Votes': votes, 
                        'Box Office Earnings': earnings, 
                        'Director': directors,
                        'Actors': actors}

            # export to csv with header and something new
            print('3. Download data and export title, release, rating, votes,... to %s\imdb_%s.csv file' % (csv_path, str(index + 1)))
            csvOperation.export_csv("imdb_" + str(index + 1),
                                    df_dict_imdb,
                                    csv_path)

def scraping_with_selenium():
    #launch url
    url = "https://www.imdb.com/search/title"

    # Define Chrome options to open the window in maximized mode
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    # create a new Firefox session
    driver = webdriver.Chrome(executable_path=r'C:\apps\chromedriver.exe', options=options)
    driver.implicitly_wait(30)
    driver.get(url)

    # set check in checkbox have "IMDb Top 100" value
    chkGroup100 = driver.find_element_by_xpath("//input[@id='groups-1']")
    chkGroup100.click()

    ddlSearchCount = driver.find_element_by_id('search-count')
    for optionSearchCount in ddlSearchCount.find_elements_by_tag_name('option'):
        if optionSearchCount.text == '100 per page':
            optionSearchCount.click() # select() in earlier versions of webdriver
            break

    ddlSort = driver.find_element_by_name('sort')
    for optionSort in ddlSort.find_elements_by_tag_name('option'):
        if optionSort.text.strip() == 'User Rating Descending':
            optionSort.click() # select() in earlier versions of webdriver
            break

    #After opening the url above, Selenium clicks the specific submit button
    submit_button = driver.find_element_by_class_name('primary')
    submit_button.click() #click submit button

    #Selenium hands the page source to Beautiful Soup
    soup_level1 = BeautifulSoup(driver.page_source, 'lxml')
    divMain = soup_level1.find('div', id=re.compile("^main"))
    divArtical = divMain.find_all('div')[0]
    divListDetail = divMain.find_all('div')[2]
    divLister = divMain.find_all('div')[0]

    datalist = [] #empty list

    #Beautiful Soup finds all Job Title links on the agency page and the loop begins
    for currentSpan in divLister.findAll('span', attrs={'class':'lister-item-index'}):
        #Selenium visits each Job Title page
        python_button = driver.find_element_by_xpath("//*[contains(text(), '" + currentSpan.findNext('a').text + "')]")
        python_button.click() #click link
        # print('link: %s' % fileName)

        # #Selenium hands of the source of the specific job page to Beautiful Soup
        # soup_level2=BeautifulSoup(driver.page_source, 'lxml')

        # #Beautiful Soup grabs the HTML table on the page
        # table = soup_level2.find_all('table')[0]
        
        # #Giving the HTML table to pandas to put in a dataframe object
        # df = pd.read_html(str(table),header=0)
        
        # #Store the dataframe in a list
        # datalist.append(df[0])
        
        # #Ask Selenium to click the back button
        driver.execute_script("window.history.go(-1)") 
        
        #end loop block
        
    #loop has completed

    #end the Selenium browser session
    driver.quit()

    #combine all pandas dataframes in the list into one big dataframe
    # result = pd.concat([pd.DataFrame(datalist[i]) for i in range(len(datalist))],ignore_index=True)

    # #convert the pandas dataframe to JSON
    # json_records = result.to_json(orient='records')

    # #pretty print to CLI with tabulate
    # #converts to an ascii table
    # print(tabulate(result, headers=["Employee Name","Job Title","Overtime Pay","Total Gross Pay"],tablefmt='psql'))

    # #get current working directory
    # path = os.getcwd()

    # #open, write, and close the file
    # f = open(path + "\\fhsu_payroll_data.json","w") #FHSU
    # f.write(json_records)
    # f.close()
            

# def scraping_with_selenium(csv_path):
#     csvOperation = CsvOperation.getInstance()  # Object singleton instantiation of CsvOperation class

#     url = 'https://www.imdb.com/search/title/?groups=top_100&count=100&start=1&sort=user_rating'

#     # Define Chrome options to open the window in maximized mode
#     options = webdriver.ChromeOptions()
#     # options.headless = True # hide browser
#     options.add_argument("--start-maximized")

#     chrome_driver = webdriver.Chrome(executable_path=r'C:\apps\chromedriver.exe', options=options)
#     edriver = EventFiringWebDriver(chrome_driver, MyListener())

#     chrome_driver.get(url)
#     detailLinkElem = chrome_driver.find_elements_by_css_selector('.lister-item-header a')
#     # nextLinkElem = edriver.find_element_by_class_name('next-page')
#     # detail_href = detailLinkElem[0].get_attribute('href')

    
#     for detailLinkItem in detailLinkElem:
#         detailLinkItem.click()
#         #Ask Selenium to click the back button
#         chrome_driver.execute_script("window.history.go(-1)") 
#     #     print(detailLinkItem.text)
#         # edriver.back()
    
#     # time.sleep(refresh_time_in_seconds)
#     # one step back in browser history
    

#     # open current link in chrome browser
#     # while True:
#     #     try:
            
#     #     except NoSuchElementException:
#     #         break

#     # chrome_browser.implicitly_wait(120)

#     # index = 0

#     # while nextLinkElem != None:
#     #     print('\n')
#     #     print('1. Request-Response from %s' % next_href)
        
#     #     print('2. Parse and Extract title, release, rating, votes,... from imdb website')

#     #     print('3. Download data and export title, release, rating, votes,... to %s\imdb_%s.csv file' % (csv_path, str(index + 1)))
        
#     #     nextLinkElem.click()

#     # next_href = nextLinkElem.get_attribute('href')
#     # chrome_browser.get(next_href)
#     # nextLinkElem = chrome_browser.find_element_by_class_name('next-page')
#     # index += 1

#     chrome_driver.close()

"""
-----// begin private member function: can access within the class only //-----
"""
def __let_user_pick(options):
    print("Please choose:")
    for idx, element in enumerate(options):
        print("{}) {}".format(idx+1,element))
    i = input("Enter number: ")
    try:
        if 0 < int(i) <= len(options):
            return int(i)
    except:
        pass
    return None

def __let_user_input_path():
    path = input("Please enter path will contain csv file (Ex: D:\ExportDocument):   ")
    try:
        if path:
            return path
    except:
        pass
    return None

def __main():
    print('-------WebScraping process start.---------')
    print('\n')

    csv_path = __let_user_input_path() # returns string (Ex: D:\ExportDocument)

    if csv_path != None:
        options = ["Scraping Without Selenium.", "Scraping With Selenium."]
        choice = __let_user_pick(options) # returns integer

        if choice == 1:
            scraping_without_selenium(csv_path)
        elif choice == 2:
            scraping_with_selenium()
        else:
            print('You choose nothing')
    else:
         print('Please enter csv path first')

    print('\n')
    print('-------WebScraping process finish.---------')
"""
-----// end private member function: can access within the class only //-----
"""

if __name__ == "__main__":
    __main()

