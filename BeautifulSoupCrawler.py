# import CrawlerLib class
# defined in CrawlerLibrary.py
from CrawlerLibrary import CrawlerLib


# Object instantiation of CrawlerLib class  
libCrawler = CrawlerLib()

# Let’s connect to the IMDB top 100 movies webpage:
url = 'https://www.imdb.com/search/title/?count=100&groups=top_1000&sort=user_rating%27'
soup = libCrawler.get_page_contents(url)

# We can get a list of all distinct movies and their corresponding HTML by
movies = soup.findAll('div', 
                        class_='lister-item-content')

# we can construct a list of all movie titles
titles = libCrawler.extract_attribute(movies,
                                        soup,
                                        'a')

# Release years can be found under the tag span and class lister-item-year text-muted unbold
# found in <span class="lister-item-year text-muted unbold">(2020)</span>
release = libCrawler.extract_attribute(movies,
                                        soup, 
                                        'span', 
                                        'lister-item-year text-muted unbold')

# Audience rating can be found under the tag span and class certificate
# found in <span class="certificate">TV-MA</span>
audience_rating = libCrawler.extract_attribute(movies,
                                                soup, 
                                                'span', 
                                                'certificate')

# Runtime can be found under the tag span and class runtime
# found in <span class="runtime">153 min</span>
runtime = libCrawler.extract_attribute(movies,
                                        soup, 
                                        'span', 
                                        'runtime')

# Genre can be found under the tag span and class genre
# found in <span class="genre">Drama</span>
genre = libCrawler.extract_attribute(movies,
                                        soup, 
                                        'span', 
                                        'genre')

# IMDB rating value from the data-value attribute we simply need parse the dictionary that the find method returns
# found in <div class="inline-block ratings-imdb-rating" name="ir" data-value="8.9">
imdb_rating = libCrawler.extract_attribute(movies,
                                            soup, 
                                            'div', 
                                            'inline-block ratings-imdb-rating', 
                                            False)

# we’ll use a dictionary to filter for the attribute name='nv’ in our findAll method and grab the first element
# found in <span name="nv" data-value="47467">47,467</span>
votes = libCrawler.extract_attribute(movies,
                                        soup, 
                                        'span' , 
                                        {'name' : 'nv'}, 
                                        False, 
                                        0)

# we’ll use a dictionary to filter for the attribute name='nv’ in our findAll method and grab the second element
# found in <span name="nv" data-value="53,800,000">$53.80M</span>
earnings = libCrawler.extract_attribute(movies,
                                        soup, 
                                        'span' , 
                                        {'name' : 'nv'}, 
                                        False, 
                                        1)

# director information is located within an initial p tag and thereafter an a tag — both without class attributes making it necessary to unnest the data
directors = libCrawler.extract_attribute(movies,
                                            soup, 
                                            'p', 
                                            '', 
                                            'a', 
                                            '', 
                                            True, 
                                            0, 
                                            True)

# actors always correspond to the remaining a tags
actors = libCrawler.extract_attribute(movies,
                                        soup, 
                                        'p', 
                                        '', 
                                        'a', 
                                        '', 
                                        True, 
                                        slice(1, 5, None), 
                                        True)

libCrawler.export_csv(titles, 
                        release, 
                        audience_rating,
                        runtime,
                        genre,
                        imdb_rating,
                        votes,
                        earnings,
                        directors,
                        actors)





