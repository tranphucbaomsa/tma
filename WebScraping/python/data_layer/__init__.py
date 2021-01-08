# __init__.py (data_layer)
"""
Contains the data layer of python app: mysql, sqlite, etc.
import ViewOperation class in presentation_layer\client_app.py
"""

from . import mysql_process
from .mysql_process import MySqlStoringData 

__all__ = [
        'MySqlStoringData',
]