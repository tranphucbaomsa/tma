# import CrawlerOperation and CsvOperation class
# defined in CrawlerLibrary.py
from CrawlerLibrary import CrawlerOperation
from CrawlerLibrary import CsvOperation

import webbrowser


# Object instantiation of CrawlerOperation class  
crawlerOperation = CrawlerOperation()
# Object instantiation of CsvOperation class 
csvOperation = CsvOperation()

# Let’s connect to the IMDB top 100 movies webpage:
url = 'https://www.imdb.com/search/title/?count=100&groups=top_1000&sort=user_rating%27'

# open url in current browser 
webbrowser.open_new(url)

result = crawlerOperation.get_page_contents(url)

if result != None:
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
    csvOperation.export_csv(titles, 
                            release, 
                            audience_rating,
                            runtime,
                            genre,
                            imdb_rating,
                            votes,
                            earnings,
                            directors,
                            actors)





