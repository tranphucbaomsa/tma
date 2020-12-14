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

We have 2 file in project:

* CrawlerLibrary.py: This is a library file for scraping website.
* main.py: This is the main file of the program using the library file (CrawlerLibrary.py)
    
After taking a look at the IMDB webpage, we’ll set out to extract (all highlighted in the above screenshot of the page):

*  Movie title
*  Release year
*  Runtime
*  Audience rating
*  Genre
*  IMDB rating
*  Number of votes
*  Director
*  Primary actors
*  Description

## Running the code

The top 100 movies will show as:

![Image of Yaktocat](https://miro.medium.com/max/700/1*pdpHtgtksNsh6gV0x4LIQQ.png)


## Reference

*  Beautiful Soup:  https://pypi.org/project/beautifulsoup4/
*  Python Requests Module:  https://pypi.org/project/requests/
*  Python Data Analysis Library:  https://pandas.pydata.org/
*  Convenient Web-browser controller:  https://docs.python.org/3/library/webbrowser.html
*  Regular expression operations:  https://docs.python.org/3/library/re.html
*  Time access and conversions:  https://docs.python.org/3/library/time.html
*  Selenium with Python:  https://selenium-python.readthedocs.io/
*  Miscellaneous operating system interfaces:  https://docs.python.org/3/library/os.html
*  Common pathname manipulations:  https://docs.python.org/3/library/os.path.html
*  Modules in Python 3:  https://www.digitalocean.com/community/tutorials/how-to-import-modules-in-python-3

