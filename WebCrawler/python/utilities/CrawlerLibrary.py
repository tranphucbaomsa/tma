"""
We can then import these at begin
bs4 (beautifulsoup4): Allows us to parse the HTML of the site and convert it to a BeautifulSoup object, which represents the HTML as a nested data structure.
pandas: The goto Python package for dataset manipulation  
requests: The package that allows us to connect the site of choice.
"""
import bs4
import pandas as pd
import requests

# all operation about crawler
class CrawlerOperation:
    # init method or constructor   
    def __init__(self): 
        pass

    """
    titles = [movie.find('a').text for movie in movies]
    release = [movie.find('span', class_='lister-item-year text-muted unbold').text for movie in movies]
    imdb_rating = movie.find('div', 'inline-block ratings-imdb-rating')['data-value']
    votes = movie.findAll('span' , {'name' : 'nv'})[0]['data-value']
    earnings = movie.findAll('span' , {'name' : 'nv'})[1]['data-value']
    director = movie.find('p').find('a').text
    actors = [actor.text for actor in movie.find('p').findAll('a')[1:]]
    """
    def extract_attribute(self, movies, soup, tag_1, class_1='', tag_2='', class_2='',
                    text_attribute=True, order=None, nested=False):        
        data_list = []
        for movie in movies:
            if text_attribute:
                # Extracting Nested Values: director and actors
                if nested:
                    data_list.append(self.nested_text_value(movie, tag_1, class_1, tag_2, class_2, order))
                # Extracting text: titles and release year
                else:
                    data_list.append(self.text_value(movie, tag_1, class_1))
            # Extracting Numerical Values: imdb_rating        
            else:
                data_list.append(self.numeric_value(movie, tag_1, class_1, order))

        return data_list

    # extract numerical values from movie item
    def numeric_value(self, movie, tag, class_=None, order=None):
        if order:
            if len(movie.findAll(tag, class_)) > 1:
                to_extract = movie.findAll(tag, class_)[order]['data-value']
            else:
                to_extract = None
        else:
            to_extract = movie.find(tag, class_)['data-value']

        return to_extract

    # extract nested values from movie item
    def nested_text_value(self, movie, tag_1, class_1, tag_2, class_2, order=None):
        if not order:
            return movie.find(tag_1, class_1).find(tag_2, class_2).text
        else:
            return [val.text for val in movie.find(tag_1, class_1).findAll(tag_2, class_2)[order]]

    # extract text values from movie item
    def text_value(self, movie, tag, class_=None):
        if movie.find(tag, class_):
            return movie.find(tag, class_).text
        else:
            return

    # Connect to the webpage, extract the HTML behind it and convert it to a BeautifulSoup object
    def get_page_contents(self, url):
        soap = None
        try:
            page = requests.get(url, headers={"Accept-Language": "en-US"})

            if page.status_code == 200:
                soap = bs4.BeautifulSoup(page.text, "html.parser")
            else:
                print(response_message(page.status_code))
           
        except requests.RequestException as requestEx:
            print(requestEx) 
        except Exception as ex:
            print(ex) 
        
        return soap


# all operation about csv file
class CsvOperation:
    # init method or constructor   
    def __init__(self): 
        pass

    # extracting all the information we need an turning it into a clean pandas data frame
    # export data frame to csv format
    def export_csv(self, titles, release, audience_rating, 
                    runtime, genre, imdb_rating, votes, 
                    earnings, directors, actors):

        # init dictionary
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

        # We use pandas to visualize the data       
        df = pd.DataFrame(df_dict)

        # export to csv format with header
        df.to_csv("D:\\ExportDocument\\datacamp130818.csv", header=True, index=False)



# HTTP response status codes
def response_message(status_code):
    switcher={
            # Informational responses (100–199)
            100:'Continue',
            101:'Switching Protocol',
            102:'Processing',
            103:'Early Hints',
            # Successful responses (200–299)
            200:'OK',
            201:'Created',
            202:'Accepted',
            203:'Non-Authoritative Information',
            204:'No Content',
            # Redirects (300–399)
            # Client error responses (400–499)
            400:'Bad Request',
            401:'Unauthorized',
            402:'Payment Required',
            403:'Forbidden',
            404:'This page could not be found', # Not found
            408:'Request Timeout',
            414:'URI Too Long',
            429:'Too Many Requests',
            # Server errors (500–599)
            500:'Internal Server Error',
            501:'Not Implemented',
            502:'Bad Gateway',
            503:'Service Unavailable',
            504:'Gateway Timeout',
            505:'HTTP Version Not Supported'
        }
    return switcher.get(status_code,"An request exception occurred")    