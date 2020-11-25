# Overview

Many data analysis, big data, and machine learning projects require scraping websites to gather the data that you’ll be working with. The Python programming language is widely used in the data science community, and therefore has an ecosystem of modules and tools that you can use in your own projects. In this tutorial we will be focusing on the Beautiful Soup module. 

## Getting Started

Web scraping simply means to automatically gather information/data from a website.

For this tutorial on web scraping we’ll go ahead and create a dataset from the 100 highest user rated movies on IMDB:

![Image of Yaktocat](https://miro.medium.com/max/700/1*i0pULjJvx7wtnvFcUGMGKA.png)

### Prerequisites

Before working on this tutorial, you should have a local or server-based Python programming environment set up on your machine (https://www.python.org/).

What things you need to install the software and how to install them

```
Python 3.6+
Visual Studio Code
```

Start by open up a terminal session and run the following command to install the packages we’ll need:

```
pip install beautifulsoup4 requests pandas
```

* beautifulsoup4: Allows us to parse the HTML of the site and convert it to a BeautifulSoup object, which represents the HTML as a nested data structure.
* requests: The package that allows us to connect the site of choice.
* pandas: The goto Python package for dataset manipulation  

### Documentation
    
We can then import these at begin:

```
import bs4
import pandas as pd
import requests
```

Let’s connect to the IMDB top 100 movies webpage, extract the HTML behind it and convert it to a BeautifulSoup object:

```
url = 'https://www.imdb.com/search/title/?count=100&groups=top_1000&sort=user_rating'

def get_page_contents(url):
    page = requests.get(url, headers={"Accept-Language": "en-US"})
    return bs4.BeautifulSoup(page.text, "html.parser")
    
soup = get_page_contents(url)
```

After taking a look at the IMDB webpage, we’ll set out to extract (all highlighted in the above screenshot of the page):

*  Movie title
*  Release year
*  Runtime
*  Audience rating
*  Genre
*  IMDB rating
*  Number of votes
*  Box office earnings
*  Director
*  Primary actors

We can get a list of all distinct movies and their corresponding HTML by:

```
movies = soup.findAll('h3', class_='lister-item-header')
```

Thus, we can construct a list of all movie titles

```
titles = [movie.find('a').text for movie in movies]
```

Release years can be found under the tag span and class lister-item-year text-muted unbold. To grab these, we can follow a similar approach as before:

```
release = [movie.find('span', class_='lister-item-year text-muted unbold').text for movie in movies]
```

To grab the IMDB rating value from the data-value attribute we simply need parse the dictionary that the find method returns

```
movie.find('div', 'inline-block ratings-imdb-rating')['data-value']
```

Doing so we can use findAll and grab the first element as votes and the second as earnings

```
votes = movie.findAll('span' , {'name' : 'nv'})[0]['data-value']
earnings = movie.findAll('span' , {'name' : 'nv'})[1]['data-value']
```

The director is the 1st a tag, we can extract this information through:

```
director = movie.find('p').find('a').text
```

and, since the actors always correspond to the remaining a tags, we can grab these through:

```
actors = [actor.text for actor in movie.find('p').findAll('a')[1:]]
```

## Running the code

The above demo should result in a data frame similar to:

![Image of Yaktocat](https://miro.medium.com/max/700/1*pdpHtgtksNsh6gV0x4LIQQ.png)


