from pandas import *
import numpy as np
from datetime import datetime, timedelta
import os, os.path
import fnmatch
import csv
import sys
from collections import defaultdict
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
        self.indices_code = []
        self.futures_code = []
        self.financial = {}
        self.financial_reports=[]

        self.stock = {}
        self.indices = {}
        self.futures = {}
        self.stock_desp = {}
        self.indices_desp = {}
        self.futures_desp = {}
        self.active = 0
        for root, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                if fnmatch.fnmatch(filename, 'listcode.csv'):
                    self.status = 0
                else:
                    raise Exception("Must assign proper data directory")
        sys.stdout.write( "1. reading symbols...")
        ifile = open(self.directory+'stock/listcode.csv', "r")
        reader = csv.reader(ifile)
        next(reader, None) 
        for row in reader:
            self.code.append(row[0])
            self.stock_desp[row[0]]={}
            self.stock_desp[row[0]]['gics']=row[1]
            self.stock_desp[row[0]]['float']=row[2]
            self.stock_desp[row[0]]['total']=row[3]
            self.stock_desp[row[0]]['beg']=row[4]
            self.stock_desp[row[0]]['name']=row[5]
        print "\n succeed reading stock symbols"
        ifile = open(self.directory+'index/listcode.csv', "r")
        reader = csv.reader(ifile)
        next(reader, None) 
        for row in reader:
            self.indices_code.append(row[0])
            self.indices_desp[row[0]] = {}
            self.indices_desp[row[0]]['name']=row[1]
        print " succeed reading index symbols"
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

        print "2. reading index time series.."
        i = 0
        j = 0
        for s in self.indices_code:
            vp = 20
            increment = 20.0/len(self.indices_code)
            if os.path.exists(self.directory+'index/'+s+'.csv'):
                self.indices[s] = pandas.read_csv(self.directory+'index/'+s+'.csv',index_col=0,skipinitialspace=True, parse_dates=True)
                i += 1
            else:
                self.indices_code.remove(s)
                j += 1
            sys.stdout.write("\r[" + "=" * int(i * increment) + " " * int(vp - i * increment) + "] " + str(i)+"/"+str(len(self.indices_code)))
        print "\n Successfully imported "+str(i)+" indices, "+str(j)+" discarded"
        self.indices = pandas.Panel(self.indices)
         



        print "3. reading stock time series..."
        i = 0
        j = 0
        for s in self.code:
            vp = 20
            increment = 20.0/len(self.code)
            if os.path.exists(self.directory+'stock/'+s+'.csv'):
                self.stock[s] = pandas.read_csv(self.directory + \
                    'stock/'+s+'.csv',index_col=0,skipinitialspace =True, \
                    parse_dates=True)
                i += 1
            else:
                self.code.remove(s)
                j += 1
            sys.stdout.write("\r[" + "=" * int(i * increment) + \
                " " * int(vp - i * increment) + "] " + str(i)+"/" \
                    + str(len(self.code)))
        print "\n Successfully imported "+str(i)+" securities, "+str(j)+ \
            " discarded"
        self.stock = pandas.Panel(self.stock)
         
        print "4. reading stock financials...."
        ifile = open(self.directory+'financial/financial.csv', "r")
        reader = csv.reader(ifile)
        next(reader, None)
        i = 0
        self.financial_code = []
        increment = 20.0/len(self.code)
        code =""
        financial_records=[]
        for row in reader:
            # self.financial.append(row[0])
            if code != row[0]:
                if financial_records:
                    self.financial[code] = \
                        pandas.DataFrame.from_records(financial_records[::-1], \
                        index='rls_date')
                    financial_records = []
                self.financial[row[0]]=[];
                i += 1
                self.financial_code.append(row[0])
                sys.stdout.write("\r[" + "=" * int(i * increment) + \
                    " " * int(20 - i * increment) + "] " + str(i) + \
                    "/"+str(len(self.code)))
                code = row[0]
            newrecord = {}
            newrecord['rpt_date']=datetime.strptime(row[1],'%Y%m%d')
            if not row[2]:
                newrecord['rls_date']=newrecord['rpt_date']
            else:
                newrecord['rls_date']=datetime.strptime(row[2],'%Y%m%d')
            newrecord['eps']=row[3]
            newrecord['eps_ttm']=row[4]
            newrecord['asset_ps']=row[5]
            newrecord['revenue_ps']=row[6]
            newrecord['revenue_ps_ttm']=row[7]
            newrecord['op_fcf_ps']=row[8]
            newrecord['op_fcf_ps_ttm']=row[9]
            newrecord['fcf_ps']=row[10]
            newrecord['fcf_ps_ttm']=row[11]
            newrecord['asset']=row[12]
            newrecord['debt']=row[13]
            newrecord['equity']=row[14]     
            newrecord['revenue']=row[15]  
            newrecord['profit']=row[16]  
            newrecord['net_profit']=row[17]  
            newrecord['revenue_growth']=row[18]  
            newrecord['profit_growth']=row[19]  
            newrecord['al_ratio']=row[20]  
            newrecord['gross_profit_margin']=row[21]  
            newrecord['netROE']=row[22]  
            newrecord['capt_turnover']=row[23]  
            financial_records.append(newrecord)
            newrecord['code']=row[0]  
            self.financial_reports.append(newrecord)
            
        self.financial[row[0]] = \
            pandas.DataFrame.from_records(financial_records[::-1], \
            index='rls_date')
            
        print " \nsucceed reading stock financials"

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
            self.indices = {}
            self.stock_desp = {}
            self.indices_desp = {}
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

    def get_financials(self, symbol, date):
        if symbol not in self._financial:
            return
        ind = self._financial[symbol].index.searchsorted(date)
        if ind==0:
            return 
        else:
            self.financial[symbol] = self._financial[symbol].ix[ind-1].to_dict()         


    def __init__(self, target, start=None):
        if (start is None):
            # default start from half a year later
            # some computation required history data (correlation)
            self.start_ind = 125
        else:
            self.start_ind = start
        # assign data
        self._stock = target.stock
        self._indices = target.indices
        self._financial = target.financial
        self._financial_reports = target.financial_reports[::-1]
        # assign symbols        
        self.code = target.code
        self.indices_code = target.indices_code
        
        sys.stdout.write(" Constituting data panel... ")
        self.beg = self._stock.ix[0].index[self.start_ind].to_datetime()
        self.end = self._stock.ix[0].index[-1].to_datetime()
        self.now = self.beg
        self.financial = defaultdict(dict)
        
        self.now_ind = 0
        # WARNING: now_ind is for indexing "data", not "_stock" ; 
        # now_ind = ind - start_ind
        
        self.ind = self.start_ind
        self.date = self._stock.major_axis
        self.data_indices = self.date[self.start_ind:]
        self.data = self._stock.ix[:, self.start_ind:self.ind+1]
        
        # get all financial ratios
        map(lambda x:self.get_financials(x,self.beg), self.code)

        # raise OK flag
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
        self.data_indices = self._indices.ix[:, self.start_ind:self.ind+1]
       
        # update financial ratios
       
        
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

    def pick_bar(self, code, type='stock'):
        """pick out OHLCVA of a symbol
        
        Parameters:
        -------
        code: [required]
            the symbol you want, eg: 000001, 300693
        type: [optional]
            stock,index, etf, swap, option, and etc
        
            
        Returns:
        -------
        pandas dataframe
        """
        if type=='stock':
            if code not in self.code:
                print "ERROR: cannot find your code "+code
                return
            else:
                return self._stock.ix[code]
        elif type=='index':
            if code not in self.indices_code:
                print "ERROR: cannot find your code "+code
                return
            else:
                return self._indices.ix[code]

    

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
data = BackTestData(raw)