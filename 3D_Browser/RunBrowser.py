#!/usr/bin/env python
# encoding: utf-8

"""
This is a manager class to run the SfM Browser and associated methods
"""

import logging 
#import browser_methods
from browser_methods.browser import Browser

logging.basicConfig(level=logging.INFO, format="%(message)s")

manager = Browser()

#manager.prepare_data()

manager.run()

