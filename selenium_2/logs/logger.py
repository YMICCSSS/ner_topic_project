import logging
import os
from datetime import datetime

dir_path = 'C:/Users/Mia/PycharmProjects/selenium/logs/'
filename = '{:%Y-%m-%d}'.format(datetime.now())

def create