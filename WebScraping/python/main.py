# import CrawlerOperation and CsvOperation class
# defined in CrawlerLibrary.py
from utilities.CrawlerLibrary import CrawlerOperation
from utilities.CrawlerLibrary import CsvOperation

# import the necessary packages
import webbrowser as w
import time
from selenium import webdriver
import pandas as pd
from selenium.common.exceptions import NoSuchElementException

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
    next_link = '/search/title/?groups=top_1000&count=250&start=1&ref_=adv_nxt'
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
                                                    result,
                                                    'a')

            # Release years can be found under the tag span and class lister-item-year text-muted unbold
            # found in <span class="lister-item-year text-muted unbold">(2020)</span>
            release = crawlerOperation.extract_attribute(movies,
                                                    result,
                                                    'span',
                                                    'lister-item-year text-muted unbold')

            # Audience rating can be found under the tag span and class certificate
            # found in <span class="certificate">TV-MA</span>
            audience_rating = crawlerOperation.extract_attribute(movies,
                                                            result,
                                                            'span',
                                                            'certificate')

            # Runtime can be found under the tag span and class runtime
            # found in <span class="runtime">153 min</span>
            runtime = crawlerOperation.extract_attribute(movies,
                                                    result,
                                                    'span',
                                                    'runtime')

            # Genre can be found under the tag span and class genre
            # found in <span class="genre">Drama</span>
            genre = crawlerOperation.extract_attribute(movies,
                                                    result,
                                                    'span',
                                                    'genre')

            # IMDB rating value from the data-value attribute we simply need parse the dictionary that the find method returns
            # found in <div class="inline-block ratings-imdb-rating" name="ir" data-value="8.9">
            imdb_rating = crawlerOperation.extract_attribute(movies,
                                                        result,
                                                        'div',
                                                        'inline-block ratings-imdb-rating',
                                                        False)

            # we’ll use a dictionary to filter for the attribute name='nv’ in our findAll method and grab the first element
            # found in <span name="nv" data-value="47467">47,467</span>
            votes = crawlerOperation.extract_attribute(movies,
                                                    result,
                                                    'span' ,
                                                    {'name' : 'nv'},
                                                    False,
                                                    0)

            # we’ll use a dictionary to filter for the attribute name='nv’ in our findAll method and grab the second element
            # found in <span name="nv" data-value="53,800,000">$53.80M</span>
            earnings = crawlerOperation.extract_attribute(movies,
                                                    result,
                                                    'span' ,
                                                    {'name' : 'nv'},
                                                    False,
                                                    1)

            # director information is located within an initial p tag and thereafter an a tag — both without class attributes making it necessary to unnest the data
            directors = crawlerOperation.extract_attribute(movies,
                                                        result,
                                                        'p',
                                                        '',
                                                        'a',
                                                        '',
                                                        True,
                                                        0,
                                                        True)

            # actors always correspond to the remaining a tags
            actors = crawlerOperation.extract_attribute(movies,
                                                    result,
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
            

def scraping_with_selenium(csv_path):
    csvOperation = CsvOperation.getInstance()  # Object singleton instantiation of CsvOperation class

    url = 'https://www.imdb.com'
    next_href = url + '/search/title/?groups=top_1000&count=250&start=1&ref_=adv_nxt'

    # Define Chrome options to open the window in maximized mode
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    chrome_browser = webdriver.Chrome(executable_path=r'C:\apps\chromedriver.exe', chrome_options=options)
    # open current link in chrome browser
    chrome_browser.get(next_href)
    isNext = True

    while isNext:
        try:
            titles = chrome_browser.find_elements_by_css_selector('.lister-item-header a')
            print('Title: %s' % titles[0].text)

            nextLinkElem = chrome_browser.find_element_by_class_name('next-page')
            time.sleep(1)
            nextLinkElem.click()
        except NoSuchElementException:
            isNext = False
            break  

    # chrome_browser.maximize_window()
    # chrome_browser.implicitly_wait(120)

    # index = 0

    # while nextLinkElem != None:
    #     print('\n')
    #     print('1. Request-Response from %s' % next_href)
        
    #     print('2. Parse and Extract title, release, rating, votes,... from imdb website')

    #     print('3. Download data and export title, release, rating, votes,... to %s\imdb_%s.csv file' % (csv_path, str(index + 1)))
        
    #     nextLinkElem.click()

        # next_href = nextLinkElem.get_attribute('href')
        # chrome_browser.get(next_href)
        # nextLinkElem = chrome_browser.find_element_by_class_name('next-page')
        # index += 1
        
    chrome_browser.close()

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
            scraping_with_selenium(csv_path)
        else:
            print('You choose nothing')
    else:
         print('You dont enter yet')

    print('\n')
    print('-------WebScraping process finish.---------')
"""
-----// end private member function: can access within the class only //-----
"""

if __name__ == "__main__":
    __main()

