from pandas import *
from datetime import datetime, timedelta
import os, os.path
import fnmatch
import csv
import sys
from abc import ABCMeta, abstractmethod
from event import MarketEvent

class DataHandler(object):
    """
    DataHandler is an abstract base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) DataHandler object is to output a generated
    set of bars (OLHCVI) for each symbol requested.

    This will replicate how a live strategy would function as current
    market data would be sent "down the pipe". Thus a historic and live
    system will be treated identically by the rest of the backtesting suite.
    """

    def __init__(self, directory="./", codelist=[]):
        """Initialize working environment
        Need to assign data directory, default: current directory"""
        self.status = 1
        self.directory = os.path.expanduser(directory)
        self.code = []
        self.stock = {}
        self.active = 0
        for root, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                if fnmatch.fnmatch(filename, 'listcode.csv'):
                    self.status = 0
                else:
                    raise Exception("Must assign proper data directory")
        sys.stdout.write( "1. reading codes...")
        ifile = open(self.directory+'listcode.csv', "r")
        reader = csv.reader(ifile)
        for row in reader:
            self.code.append(row[0])
        print " success"
        if len(codelist) != 0:
            if len(set(self.code) & set(codelist)) == 0:
                print "ERROR: none of your symbols exists in database"
                sys.exit(1)
            newcodelist = list(set(self.code) & set(codelist))
            voidcodelist = list(set(codelist) - set(newcodelist))
            if len(voidcodelist) != 0:
                print "WARNING: following symbols are not in database and ignored"
                print voidcodelist
            self.code = newcodelist

        print "2. reading time series..."
        i = 0
        j = 0

        for s in self.code:
            vp = 20
            increment = 20.0/len(self.code)
            if os.path.exists(self.directory+s+'.csv'):
                self.stock[s] = pandas.read_csv(self.directory+s+'.csv',index_col=0,skipinitialspace=True, parse_dates=True)
                i += 1
            else:
                self.code.remove(s)
                j += 1
            sys.stdout.write("\r[" + "=" * int(i * increment) + " " * int(vp - i * increment) + "] " + str(i)+"/"+str(len(self.code)))
        print "\n Successfully imported "+str(i)+" securities, "+str(j)+" discarded"

        self.stock = pandas.Panel(self.stock)
        self.beg = self.stock.ix[0].index[0].to_datetime()
        self.end = self.stock.ix[0].index[-1].to_datetime()
        self.date = self.stock.major_axis




class BackTestData(object):

    def __init__(self, target):
        self._stock = target.stock
        sys.stdout.write(" constituting data panel... ")
        self.beg = self._stock.ix[0].index[0].to_datetime()
        self.end = self._stock.ix[0].index[-1].to_datetime()
        self.now = self.beg
        self.ind = 0
        self.data = self._stock.ix[:, 0:self.ind+1]
        self.proceed = "OK"
        self.date = self._stock.major_axis
        print "success"

    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        self.ind += 1
        self.data = self._stock.ix[:, 0:self.ind+1]
        self.now = self.data.ix[0].index[-1].to_datetime()
        if (self.end - self.now) < timedelta(days=1):
            self.proceed = "STOP"
        #self.get_latest_bars()

    def get_latest_bars(self, codelist=[]):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        if len(codelist) == 0:
            newcodelist = self.code
        else:
            if len(set(self.code) & set(codelist)) == 0:
                print "ERROR: none of your symbols exists in database"
                sys.exit(1)
            else:
                newcodelist = list(set(self.code) & set(codelist))
                voidcodelist = list(set(codelist) - set(newcodelist))
            if len(voidcodelist) != 0:
                print "WARNING: following symbols are not in database and ignored"
                print voidcodelist
        self.latest = self.data.ix[newcodelist, -1]


    def reset(self):
        sys.stdout.write(" reset context... ")
        self.beg = self._stock.ix[0].index[0].to_datetime()
        self.end = self._stock.ix[0].index[-1].to_datetime()
        self.now = self.beg
        self.ind = 0
        self.data = self._stock.ix[:, 0:self.ind+1]
        self.proceed = "OK"
        self.date = self._stock.major_axis
        print "success"

raw = DataHandler('~/data/')
