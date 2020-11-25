# importing  extract_attribute, get_page_contents, export_csv function
# defined in CrawlerLibrary.py
from CrawlerLibrary import extract_attribute, get_page_contents, export_csv

# url = 'https://www.imdb.com/search/title/?count=100&groups=top_1000&sort=user_rating'
url = 'https://www.imdb.com/search/title/?count=100&groups=top_1000&sort=user_rating%27'
soup = get_page_contents(url)

titles = extract_attribute(soup, 'a')
release = extract_attribute(soup, 'span', 'lister-item-year text-muted unbold')
audience_rating = extract_attribute(soup, 'span', 'certificate')
runtime = extract_attribute(soup, 'span', 'runtime')
genre = extract_attribute(soup, 'span', 'genre')
imdb_rating = extract_attribute(soup, 'div', 'inline-block ratings-imdb-rating', False)
votes = extract_attribute(soup, 'span' , {'name' : 'nv'}, False, 0)
earnings = extract_attribute(soup, 'span' , {'name' : 'nv'}, False, 1)
directors = extract_attribute(soup, 'p', '', 'a', '', True, 0, True)
actors = extract_attribute(soup, 'p', '', 'a', '', True, slice(1, 5, None), True)

export_csv(titles, 
            release, 
            audience_rating,
            runtime,
            genre,
            imdb_rating,
            votes,
            earnings,
            directors,
            actors)
#print(df)



