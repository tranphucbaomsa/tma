# __init__.py (business_layer)
"""
Contains the business logic of python app: scraping, crawler, etc.
import ScrapingNonSelenium and ScrapingSelenium class in business_layer\scraping_process.py
"""

from . import scraping_process 
from .scraping_process import ScrapingChromeSelenium, ScrapingFirefoxSelenium

__all__ = [
        'ScrapingChromeSelenium',
        'ScrapingFirefoxSelenium',
]