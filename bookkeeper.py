__author__ = 'fanbin'
import pandas as pd
import numpy
import math
import datetime

class Book():
    def __init__(self, symbol, bars, initial_capital=1000000.00):
        """Book Class initialization
        
        Parameters
        ----------
        symbol : list of strings
            list of interested symbols
        bars : 
            pass in data so that I can know its structures
        initial_capital:
            Well, we need some initial capital for investment
            default value is 1 million
 
        """
        self.symbol = symbol
        self.cash = initial_capital
        self.holding = 0
        self.start_ind = bars.now_ind
        self.start = bars.beg
        self.stop_ind = bars.now_ind
        self.stop = bars.beg
        self.index = bars.data_index
        self.end = bars.end
        self.now = self.start
        self.initial_capital = float(initial_capital)
        self.cash = self.initial_capital
        #self.date_list = bars.date
        # following is book structure
        # note we add asset, security and cash to symbols, they are for 
        # compilation purpose Asset = Security + Cash, Security = $\Sum$ symbol
        self.book = pd.Panel(items=['Asset', 'Security', 'Cash']+self.symbol, \
                             major_axis=bars.data_index,
                             minor_axis=["sig", "ext", "Pos", "PrePos", \
                             "TargetPos", "mmk", "Cost", "Close", \
                             "PreClose", "DeltaPL", "PL", "AvgLife", "Slip"])
        self.book = self.book.fillna(0)
        self.bar = bars
        # ind is a poiner, showing current backtest step (a.k.a where are you)
        self.ind = self.bar.now_ind
        # initial cash
        self.book.ix['Cash', self.ind, 'Pos'] = self.cash
        # initial security is void
        self.book.ix['Security', self.ind, 'Pos'] = 0
        self.book.ix['Asset', self.ind, 'Pos'] = self.cash

    def prepare(self):
        """prepare the book for next day's use
        
        Notes:
        -------
        this function is fairly import to prepare book for next's use, 
        call it before start everys backtest time unit
        """
        self.ind = self.bar.now_ind
        self.stop_ind += 1
        self.book.ix[self.symbol, self.ind, 'Close'] = \
            self.bar.data.ix[self.symbol, -1, 'Close']
        if self.ind != 0: # if today is not the first day
            self.book.ix[self.symbol, self.ind, 'PreClose'] =\
                self.bar.data.ix[self.symbol, -2, 'Close']
            self.book.ix[self.symbol, self.ind, 'Pos'] = \
                self.book.ix[self.symbol, self.ind-1, 'Pos']
            self.book.ix[self.symbol, self.ind, 'PrePos'] = \
                self.book.ix[self.symbol, self.ind-1, 'Pos']
            self.book.ix['Cash', self.ind, 'Pos'] = \
                self.book.ix['Cash', self.ind-1, 'Pos']
            self.book.ix['Cash', self.ind, 'PrePos'] = \
                self.book.ix['Cash', self.ind-1, 'Pos']
            self.book.ix['Cash', self.ind, 'DeltaPL'] = 0

            self.book.ix['Asset', self.ind, 'Pos'] = \
                self.book.ix['Asset', self.ind-1, 'Pos']
            self.book.ix['Asset', self.ind, 'PrePos'] = \
                self.book.ix['Asset', self.ind-1, 'Pos']
            self.book.ix["Asset", self.ind, "DeltaPL"] = 0

            self.book.ix['Security', self.ind, 'Pos'] = \
                self.book.ix['Security', self.ind-1, 'Pos']
            self.book.ix['Security', self.ind, 'PrePos'] = \
                self.book.ix['Security', self.ind-1, 'Pos']
            self.book.ix["Security", self.ind, "DeltaPL"] = 0

    def compile(self):
        """Compile book, should be called every time unit
        
        Parameters
        ----------
        
        Returns
        -------
        

        Notes
        -----
        This is an example of autodoc using numpydoc, the Numpy documentation format
        with the numpydoc extension [1]_

        Examples
        --------
 
        """
        if self.ind != 0: # if today is not the first day
            self.book.ix[self.symbol, self.ind, "DeltaPL"] = \
                (self.book.ix[self.symbol, self.ind, 'Close']  \
                - self.book.ix[self.symbol, self.ind, 'PreClose']) \
                * self.book.ix[self.symbol, self.ind, 'PrePos']
            self.book.ix[self.symbol, self.ind, "Slip"] = \
                (self.book.ix[self.symbol, self.ind, 'Close'] \
                - self.book.ix[self.symbol, self.ind, 'mmk']) \
                * (self.book.ix[self.symbol, self.ind, 'Pos'] \
                - self.book.ix[self.symbol, self.ind, 'PrePos'])
            self.book.ix[self.symbol, self.ind, "PL"] = \
                self.book.ix[self.symbol, self.ind, "Slip"] + \
                self.book.ix[self.symbol, self.ind, "DeltaPL"]
            self.book.ix["Security", self.ind, "DeltaPL"] = \
                numpy.nansum(self.book.ix[self.symbol, self.ind, "DeltaPL"])
            self.book.ix["Security", self.ind, "PL"] = \
                numpy.nansum(self.book.ix[self.symbol, self.ind, "PL"])
            self.book.ix["Security", self.ind, "Slip"] = \
                numpy.nansum(self.book.ix[self.symbol, self.ind, "Slip"])
            self.book.ix["Security", self.ind, "Pos"] = \
                numpy.nansum(self.book.ix[self.symbol, self.ind, "Pos"] * \
                 self.book.ix[self.symbol, self.ind, 'Close'])
            self.book.ix["Asset", self.ind, "Pos"] = \
                self.book.ix["Security", self.ind, "Pos"] + \
                self.book.ix["Cash", self.ind, "Pos"]
            self.book.ix["Asset", self.ind, "DeltaPL"] = \
                self.book.ix["Asset", self.ind, "Pos"]/ \
                self.book.ix["Asset", self.ind, "PrePos"]-1

    def print_daily_summary(self):
        """print_daily_summary
        
        Purpose:
        -----
        print relevant data to screen, for debug purpose

        """
        total_asset = self.book.ix['Asset', self.ind, 'Pos']
        print "Date: %s   Total:%.2f  Security:%.2f   Cash:%.2f  NAV:%.4f"%\
              (self.book.ix[0].index[self.ind].to_datetime().strftime('%Y-%m-%d'),
               total_asset, self.book.ix['Security', self.ind, 'Pos'], \
               self.book.ix['Cash', self.ind, 'Pos'],
               total_asset/self.initial_capital)
               
    def finalize(self):
        self.stop = self.index(self.stop_ind)

    def nav_to_json(self):
        """nav_to_json
        
        Purpose:
        -----
        print relevant data to json object, this function is reserved for 
        network purpose

        """
        ren = {}
        series = []
        nav = numpy.array([])
        for i in range(self.start_ind, self.stop_ind, 1):
            total_asset = self.book.ix['Asset', i, 'Pos']
            series.append([ \
                (self.index[i].to_datetime() - \
                datetime.datetime(1970,1,1)).total_seconds()* 1000, \
                total_asset/self.initial_capital])
            nav = numpy.append(nav, self.book.ix['Asset', i, 'DeltaPL'])
        ren["start"] = self.book.ix[0].index[self.start_ind].to_datetime().strftime("%b %d %Y")
        ren["end"] = self.book.ix[0].index[self.stop_ind-1].to_datetime().strftime("%b %d %Y")
        ren["num"] = len(range(self.start_ind, self.stop_ind, 1))
        ren["nav"] = str("{:8.2f}".format(total_asset/self.initial_capital))
        ren["sharpe"] = str("{:8.2f}".format(numpy.average(nav)/numpy.std(nav) ))
        ren["anlz"] = str("{:8.2f}".format((math.pow(float(ren["nav"]), 250.0/float(ren["num"]))-1)*100))
        ren["data"] = series
        ren["max_drawdown"] = 1
        return ren