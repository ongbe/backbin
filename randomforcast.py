# random_forecast.py
__author__ = 'fanbin'


import bindata

import math
import random
import event
import talib
import asyncore
from server import start_server

if __name__ == "__main__":

    # computation engine initialized
    print "Computation engine set up"
    # event loop start
    print "Waiting for backtesting request"
    start_server()