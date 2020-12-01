# import CrawlerOperation and CsvOperation class
# defined in CrawlerLibrary.py
from utilities.CrawlerLibrary import CrawlerOperation
from utilities.CrawlerLibrary import CsvOperation

import webbrowser as w

# Object instantiation of CrawlerOperation class
crawlerOperation = CrawlerOperation()
# Object instantiation of CsvOperation class
csvOperation = CsvOperation()

start_array = [1, 251, 501, 751]
w.register('chrome',
            None,
            w.BackgroundBrowser("C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
chrome = w.get('chrome')

url = 'https://www.imdb.com'
next_link = '/search/title/?count=250&groups=top_1000&sort=user_rating%27'
next_href = []
next_href.append('/search/title/?count=250&groups=top_1000&sort=user_rating%27')

while crawlerOperation.get_page_contents(url + next_link):
    result = crawlerOperation.get_page_contents(url + next_link)
    class_next_page = result.find('a', {'class': 'lister-page-next next-page'})

    if class_next_page != None:
        next_link = class_next_page.get('href')
        if next_link != None:
            next_href.append(next_link)
    else:
        break

# Let’s connect to the IMDB every 250 movies webpage (for 1000 movies):
for item_href in next_href:
    index = next_href.index(item_href)

    # open url in current browser
    print('Open page %s...' % url + item_href)
    chrome.open(url + item_href, new=0, autoraise=True)

    result = crawlerOperation.get_page_contents(url + item_href)

    if result != None:
        print('Get titles, release, rating, votes,... from imdb webpage')

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

        # export to csv with header and something new
        print('Export to imdb_%s csv file' % str(index + 1))
        csvOperation.export_csv("imdb_" + str(index + 1),
                                titles,
                                release,
                                audience_rating,
                                runtime,
                                genre,
                                imdb_rating,
                                votes,
                                earnings,
                                directors,
                                actors)

print('WebScraping Done.')