__author__ = 'fanbin'
import pandas as pd
import numpy
import math

class Book():
    def __init__(self, symbol, bars, initial_capital=100000.0):
        """Book Class initialization
        Parameters
        ----------
        var1 : array_like
            This is a type.
        var2 : int
            This is another var.
        Long_variable_name : {'hi', 'ho'}, optional
            Choices in brackets, default first when optional.
 
        Returns
        -------
            describe : type
            Explanation
        """
        self.symbol = symbol
        self.cash = initial_capital
        self.holding = 0
        self.start_ind = bars.ind
        self.start = bars.beg
        self.stop_ind = 0
        self.stop = bars.end
        self.now = self.start
        self.initial_capital = float(initial_capital)
        self.cash = self.initial_capital
        self.date_list = bars.date
        self.book = pd.Panel(items=['Asset', 'Security', 'Cash']+self.symbol, major_axis=bars.date,
                             minor_axis=["sig", "ext", "Pos", "PrePos", "TargetPos", "mmk", "Cost", "Close",
                                         "PreClose", "DeltaPL", "PL", "AvgLife", "Slip"])
        self.book = self.book.fillna(0)
        self.bar = bars
        self.ind = self.bar.ind
        self.book.ix['Cash', self.bar.ind, 'Pos'] = self.cash
        self.book.ix['Security', self.bar.ind, 'Pos'] = 0
        self.book.ix['Asset', self.bar.ind, 'Pos'] = self.cash

    def update(self):
        """everyday update book
        Parameters
        ----------
 
        Returns
        -------
            describe : type
            Explanation
        """
        self.ind = self.bar.ind
        self.stop_ind += 1
        self.book.ix[self.symbol, self.bar.ind, 'Close'] = self.bar.data.ix[self.symbol, self.bar.ind, 'Close']
        if self.bar.ind != 0:
            self.book.ix[self.symbol, self.bar.ind, 'PreClose'] =\
                self.bar.data.ix[self.symbol, self.bar.ind-1, 'Close']
            self.book.ix[self.symbol, self.bar.ind, 'Pos'] = \
                self.book.ix[self.symbol, self.bar.ind-1, 'Pos']
            self.book.ix[self.symbol, self.bar.ind, 'PrePos'] = \
                self.book.ix[self.symbol, self.bar.ind-1, 'Pos']
            self.book.ix['Cash', self.bar.ind, 'Pos'] = \
                self.book.ix['Cash', self.bar.ind-1, 'Pos']
            self.book.ix['Cash', self.bar.ind, 'PrePos'] = \
                self.book.ix['Cash', self.bar.ind-1, 'Pos']
            self.book.ix['Cash', self.ind, 'DeltaPL'] = 0

            self.book.ix['Asset', self.bar.ind, 'Pos'] = \
                self.book.ix['Asset', self.bar.ind-1, 'Pos']
            self.book.ix['Asset', self.bar.ind, 'PrePos'] = \
                self.book.ix['Asset', self.ind-1, 'Pos']
            self.book.ix["Asset", self.ind, "DeltaPL"] = 0

            self.book.ix['Security', self.bar.ind, 'Pos'] = \
                self.book.ix['Security', self.bar.ind-1, 'Pos']
            self.book.ix['Security', self.bar.ind, 'PrePos'] = \
                self.book.ix['Security', self.ind-1, 'Pos']
            self.book.ix["Security", self.ind, "DeltaPL"] = 0

    def compile(self):
        if self.bar.ind != 0:
            self.book.ix[self.symbol, self.ind, "DeltaPL"] = \
                (self.book.ix[self.symbol, self.ind, 'Close']  \
                - self.book.ix[self.symbol, self.ind, 'PreClose']) \
                * self.book.ix[self.symbol, self.ind, 'PrePos']
            self.book.ix[self.symbol, self.ind, "Slip"] = (self.book.ix[self.symbol, self.ind, 'Close'] \
                                                     - self.book.ix[self.symbol, self.ind, 'mmk']) \
                                                    * (self.book.ix[self.symbol, self.ind, 'Pos'] \
                                                       - self.book.ix[self.symbol, self.ind, 'PrePos'])
            self.book.ix[self.symbol, self.ind, "PL"] = self.book.ix[self.symbol, self.ind, "Slip"] + \
                                                    self.book.ix[self.symbol, self.ind, "DeltaPL"]
            self.book.ix["Security", self.ind, "DeltaPL"] = numpy.nansum(self.book.ix[self.symbol, self.ind, "DeltaPL"])
            self.book.ix["Security", self.ind, "PL"] = numpy.nansum(self.book.ix[self.symbol, self.ind, "PL"])
            self.book.ix["Security", self.ind, "Slip"] = numpy.nansum(self.book.ix[self.symbol, self.ind, "Slip"])
            self.book.ix["Security", self.ind, "Pos"] = numpy.nansum(self.book.ix[self.symbol, self.ind, "Pos"] *
                                                                  self.book.ix[self.symbol, self.ind, 'Close'])
            self.book.ix["Asset", self.ind, "Pos"] = self.book.ix["Security", self.ind, "Pos"] + self.book.ix["Cash", self.ind, "Pos"]
            self.book.ix["Asset", self.ind, "DeltaPL"] = self.book.ix["Asset", self.ind, "Pos"]/self.book.ix["Asset", self.ind, "PrePos"]-1

    def print_daily_summary(self):
        total_asset = self.book.ix['Asset', self.ind, 'Pos']
        print "Date: %s   Total:%.2f  Security:%.2f   Cash:%.2f  NAV:%.4f"%\
              (self.book.ix[0].index[self.ind].to_datetime().strftime('%Y-%m-%d'),
               total_asset, self.book.ix['Security', self.ind, 'Pos'], self.book.ix['Cash', self.ind, 'Pos'],
               total_asset/self.initial_capital)

    def nav_to_json(self):
        ren = {}
        series = []
        nav = numpy.array([])
        for i in range(self.start_ind, self.stop_ind, 1):
            total_asset = self.book.ix['Asset', i, 'Pos']
            series.append([int(self.book.ix[0].index[i].to_datetime().strftime("%s")) * 1000, total_asset/self.initial_capital])
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