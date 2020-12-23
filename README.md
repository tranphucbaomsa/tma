# Overview

Many data analysis, big data, and machine learning projects require scraping websites to gather the data that you’ll be working with. The Python programming language is widely used in the data science community, and therefore has an ecosystem of modules and tools that you can use in your own projects. In this tutorial we will be focusing on the Beautiful Soup module. 

## Getting Started

Web scraping simply means to automatically gather information/data from a website.

For this tutorial on web scraping we’ll go ahead and create a dataset from the 100 highest user rated movies on IMDB:

![Image of Yaktocat](https://miro.medium.com/max/700/1*i0pULjJvx7wtnvFcUGMGKA.png)

## Prerequisites

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

## Source Folder Structure

> Folder structure options and naming conventions for python projects

### A typical top-level directory layout
    .
    ├── business_layer          # the functional business logic. It will act as a bridge of communication for the presentation_layer and data_layer
    ├── data_layer              # comprises of the database/data storage system and data access layer
    ├── db                      # this folder contain database file (sqlite, access,...)
    ├── libs                    # this folder contain extension or tools for run application
    ├── presentation_layer      # the front end layer. The user will interact with to access the features of our application
    ├── utilities               # contains classes and funtions of general utility used in multiple places
    ├── venv                    # an isolated environment for Python projects
    ├── main.py                 # the name of the scope in which top-level code executes
    ├── LICENSE 
    ├── debug.log
    └── README.md

> Use short lowercase names at least for the top-level files and folders except
> `LICENSE`, `README.md`

### Business Logic Layer
    .
    ├── ...
    ├── business_layer                  # Test files (alternatively `spec` or `tests`)
    │   ├── scraping_process.py         # Load and stress tests
    └── ...
    
### Data Access Layer
    .
    ├── ...
    ├── data_layer                      # Test files (alternatively `spec` or `tests`)
    │   ├── sqlite_process.py           # Load and stress tests
    └── ...
    
### DB
    .
    ├── ...
    ├── db                              # Test files (alternatively `spec` or `tests`)
    │   ├── imdb_sqlite.db              # Load and stress tests
    └── ...
    
### Library
    .
    ├── ...
    ├── libs                            # Test files (alternatively `spec` or `tests`)
    │   ├── chromedriver.exe            # Load and stress tests
    └── ...
    
### Presentation (GUI) Layer
    .
    ├── ...
    ├── presentation_layer              # Test files (alternatively `spec` or `tests`)
    │   ├── client_app.py               # Load and stress tests
    └── ...
    
### Utilities
    .
    ├── ...
    ├── utilities                       # Test files (alternatively `spec` or `tests`)
    │   ├── client_app.py               # Load and stress tests
    └── ...
    
### Python Virtual Environments
    .
    ├── ...
    ├── venv                            # Test files (alternatively `spec` or `tests`)
    │   ├── Include                     # Load and stress tests
    │   ├── Lib\site-packages           # Load and stress tests
    │   ├── Scripts                     # Load and stress tests
    │   ├── pyvenv.cfg                  # Load and stress tests
    └── ...
    
    

### Documentation
    
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
*  DB-API 2.0 interface for SQLite databases: https://docs.python.org/3/library/sqlite3.html
*  Function decorator:  https://pypi.org/project/goto-statement/

