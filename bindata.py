from pandas import *
import numpy as np
from datetime import datetime, timedelta
import os, os.path
import fnmatch
import csv
import sys
from abc import ABCMeta, abstractmethod
from event import MarketEvent

class DataHandler(object):
    """
    DataHandler is an  base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) DataHandler object is to output a generated
    set of bars (OLHCVI) for each symbol requested.

    This will replicate how a live strategy would function as current
    market data would be sent "down the pipe". Thus a historic and live
    """
    def init_from_dir(self, directory="./", codelist=[]):
        """Initialize working environment
        Need to assign data directory, default: current directory"""
        self.status = 1
        self.directory = os.path.expanduser(directory)
        self.code = []
        self.stock = {}
        self.desp = {}
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
        next(reader, None) 
        for row in reader:
            self.code.append(row[0])
            self.desp[row[0]]={}
            self.desp[row[0]]['gics']=row[1]
            self.desp[row[0]]['float']=row[2]
            self.desp[row[0]]['total']=row[3]
            self.desp[row[0]]['beg']=row[4]
            self.desp[row[0]]['name']=row[5]
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
        # set begin time
        self.beg   = self.stock.major_axis[0].to_datetime()
        # set end time 
        self.end   = self.stock.major_axis[-1].to_datetime()
        # take datetimeindex as date list
        self.date  = self.stock.major_axis
        self.status_table = pandas.DataFrame(index=self.date, columns=self.code)

    def __init__(self, directory = None, target = None, codelist=[]):
        if (directory is not None):
            # read data from data directory
            print "read data from directory"
            self.init_from_dir(directory, codelist)
            self.compile_table()
        else:
            # create an empty data handler
            # usually waiting for later read data from 
            # database, such as hdf5
            self.status = 1
            self.code = []
            self.stock = {}
            self.desp = {}
            self.active = 0
    
    def compile_table(self):
        mark = np.isnan(self.stock).ix[:,:,1]
        self.status_table=pandas.DataFrame(0,index=mark.index, columns=mark.columns)
        self.status_table[~mark]=1 # set listed stock status to 1
        mark = (self.stock.ix[:,:,6]<0.1)
        self.status_table[mark] = 2 # set halt stock status to 2 
        # set halt stock's data to be NaN
        # this conforms to pandas's misssing data convention
        for i in xrange(7):
            self.stock.ix[:,:,i][mark]=np.nan
        

class BackTestData(object):

    def __init__(self, target, start=None):
        if (start is None):
            # default start from half a year later
            # some computation required history data (correlation)
            self.start_ind = 125
        else:
            self.start_ind = start
        self._stock = target.stock
        self.code = target.code
        sys.stdout.write(" constituting data panel... ")
        self.beg = self._stock.ix[0].index[self.start_ind].to_datetime()
        self.end = self._stock.ix[0].index[-1].to_datetime()
        self.now = self.beg
        
        self.now_ind = 0
        # now_ind is for indexing "data", not "_stock" ; 
        # now_ind = ind - start_ind
        
        self.ind = self.start_ind
        self.date = self._stock.major_axis
        self.data_index = self.date[self.start_ind:]
        self.data = self._stock.ix[:, self.start_ind:self.ind+1]
        self.proceed = "OK"
        print "success"

    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        # increment both index by 1
        self.ind += 1
        self.now_ind += 1
        
        # core: update data view
        self.data = self._stock.ix[:, self.start_ind:self.ind+1]
        
        # set now to be current date
        self.now = self.data.ix[0].index[-1].to_datetime()
        
        # if we are reaching the end, raise the stop flag
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
        return self.latest

    def pick_bar(self, code):
        """pick out OHLCVA of a symbol
        
        Parameters:
        -------
        code: [required]
            the symbol you want, eg: 000001, 300693
            
        Returns:
        -------
        pandas dataframe
        """
        if code not in self.code:
            print "ERROR: cannot find your code "+code
            return
        else:
            return self._stock.ix[code]

    def reset(self):
        """pick out OHLCVA of a symbol
        
        Purpose:
        -------
        Restore evertything to original state.
        Ready for next round of backtest
        """
        sys.stdout.write(" reset context... ")
        self.beg = self._stock.ix[0].index[self.start_ind].to_datetime()
        self.end = self._stock.ix[0].index[-1].to_datetime()
        self.now = self.beg
        self.ind = self.start_ind
        self.data = self._stock.ix[:, self.start_ind:self.ind+1]
        self.proceed = "OK"
        self.date = self._stock.major_axis
        print "success"


raw = DataHandler(directory='~/data/')
