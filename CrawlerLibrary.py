import bs4
import pandas
import requests

def extract_attribute(soup, tag_1, class_1='', tag_2='', class_2='',
                    text_attribute=True, order=None, nested=False):
    movies = soup.findAll('div', class_='lister-item-content')
    data_list = []
    for movie in movies:
        if text_attribute:
            if nested:
                data_list.append(nested_text_value(movie, tag_1, class_1, tag_2, class_2, order))
            else:
                data_list.append(text_value(movie, tag_1, class_1))
        else:
            data_list.append(numeric_value(movie, tag_1, class_1, order))

    return data_list

def numeric_value(movie, tag, class_=None, order=None):
    if order:
        if len(movie.findAll(tag, class_)) > 1:
            to_extract = movie.findAll(tag, class_)[order]['data-value']
        else:
            to_extract = None
    else:
        to_extract = movie.find(tag, class_)['data-value']

    return to_extract

def nested_text_value(movie, tag_1, class_1, tag_2, class_2, order=None):
    if not order:
        return movie.find(tag_1, class_1).find(tag_2, class_2).text
    else:
        return [val.text for val in movie.find(tag_1, class_1).findAll(tag_2, class_2)[order]]

def text_value(movie, tag, class_=None):
    if movie.find(tag, class_):
        return movie.find(tag, class_).text
    else:
        return

def get_page_contents(url):
    page = requests.get(url, headers={"Accept-Language": "en-US"})
    return bs4.BeautifulSoup(page.text, "html.parser")

def export_csv(titles, release, audience_rating, 
                runtime, genre, imdb_rating, votes, 
                earnings, directors, actors):
    df_dict = {'Title': titles, 
            'Relase': release, 
            'Audience Rating': audience_rating,
            'Runtime': runtime, 
            'Genre': genre, 
            'IMDB Rating': imdb_rating,
            'Votes': votes, 
            'Box Office Earnings': earnings, 
            'Director': directors,
            'Actors': actors}
    df = pandas.DataFrame(df_dict)
    df.to_csv("D:\\ExportDocument\\datacamp130818.csv", header=True, index=False)
    