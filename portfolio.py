__author__ = 'fanbin'

import numpy as np
import pandas as pd
import sys
import bindata
import math
import random
import event

from backtest import Portfolio
from order import OrderEngine
from bookkeeper import Book

class MarketOnClosePortfolio(Portfolio):
    """Inherits Portfolio to create a system that purchases 100 units of
    a particular symbol upon a long/short signal, assuming the market
    open price of a bar.

    In addition, there are zero transaction costs and cash can be immediately
    borrowed for shorting (no margin posting or interest requirements).

    Requires:
    symbol - A stock symbol which forms the basis of the portfolio.
    bars - A DataFrame of bars for a symbol set.
    signals - A pandas DataFrame of signals (1, 0, -1) for each symbol.
    initial_capital - The amount in cash at the start of the portfolio."""

    def __init__(self, symbol, bars, sty, opt, initial_capital=100000.0):
        self.symbol = symbol
        self.cash = initial_capital
        self.holding = 0
        self.start = bars.beg
        self.stop = bars.end
        self.bars = bars
        self.strategy = sty
        self.length = self.bars.date.get_loc(bars.end) - self.bars.date.get_loc(bars.beg) + 1
        self.current_mark = 0
        self.optimizer = opt
        self.initial_capital = float(initial_capital)
        self.positions = pd.DataFrame(columns=self.symbol)
        self.position = {}
        self.direction = {}
        self.portfolio = pd.DataFrame(columns=self.symbol)
        self.order_engine = OrderEngine()
        self.book = Book(self.symbol, self.bars, initial_capital=100000.0)
        self.book.book.ix[self.symbol, self.bars.ind, 'Pos'] = 0
        self.book.book.ix[self.symbol, self.bars.ind, 'PrePos'] = 0
        self.stop_mark = False

    def generate_positions(self):
        """Creates a 'positions' DataFrame that simply longs or shorts
        100 of the particular symbol based on the forecast signals of
        {1, 0, -1} from the signals DataFrame."""
        self.optimizer.gen_positions(self.strategy.signals, self.book)

    def loop(self):
        # update bars for one day, acquiring new data
        self.bars.update_bars()
        # update book values
        self.book.update()
        # then we construct portfolio, we assume tradings occur at close
        # we generate signals
        self.strategy.generate_signals()
        self.current_mark += 1
        if self.strategy.na:
            pass
        else:
            # we generate positions
            self.optimizer.gen_positions(self.strategy.signals, self.book)
            # check if constraints have been violated
            if self.optimizer.constraints.drawdown_mark:
                print "\nStop: Drawdown reaches limit "+str(self.optimizer.constraints.drawdown)
                self.stop_mark = True

            if self.optimizer.constraints.leverage_mark:
                print "\nWarning: leverage reached limit "+str(self.optimizer.constraints.leverage)
            # we execute orders
            self.order_engine.execute(self.book)
        # we compile book
        self.book.compile()


    def backtest_portfolio(self, beg=0, end=0, worker=None, job=None):
    	"""Constructs a portfolio from the positions DataFrame by
        """
        if beg != 0:
            self.start = beg
        if end != 0:
            self.stop = end
        # first we update data feed
        self.book.update()
        incre = 20.0/self.length
        print "-------------"
        print "Start Backtest:"
        j = 0
        while self.bars.proceed == "OK":
            if self.stop_mark:
                break
            self.loop()
            # we provide summary of our daily trading
            if int(float(self.current_mark)/self.length*100.0)>j:
                worker.send_job_status(job, int(float(self.current_mark)/self.length*100.0), 100)
                j = int(float(self.current_mark)/self.length*100.0)

        print "\n\n------------------------------------"
        print "Msg: backtest finished successfully"
        return self.book


    def backtest_portfolio_external(self, beg=0, end=0,):
    	"""Constructs a portfolio from the positions DataFrame by
        """
        if beg != 0:
            self.start = beg
        if end != 0:
            self.stop = end
        # first we update data feed
        self.book.update()
        incre = 20.0/self.length
        print "-------------"
        print "Start Backtest:"
        j = 0
        while self.bars.proceed == "OK":
            if self.stop_mark:
                break
            self.loop()
            # we provide summary of our daily trading
            sys.stdout.write("\r Progress: [" + "=" * int(self.current_mark * incre) +
                            " " * int(20 - self.current_mark * incre) + "] "
                            + str(self.current_mark)+"/"+str(self.length))

        print "\n\n------------------------------------"
        print "Msg: backtest finished successfully"
        return self.book