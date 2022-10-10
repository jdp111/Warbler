
from unittest import TestCase
from app import app
from flask import session
import converter
#import forex_python.converter


app.config['TESTING'] = True

class ConverterTests(TestCase):
    # tests the converter.py functions