# __init__.py (presentation_layer)
"""
Contains the user layer of python app: web_scraping, web_crawler, etc.
import ViewOperation class in presentation_layer\client_app.py
"""

from . import client_app
from .client_app import ViewOperation 

__all__ = [
        'ViewOperation',
]