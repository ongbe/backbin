# random_forecast.py

import numpy as np
import pandas as pd
import bindata
import event
import talib

from backtest import Strategy, Portfolio

class RandomForecastingStrategy(Strategy):
    """Derives from Strategy to produce a set of signals that
    are randomly generated long/shorts. Clearly a nonsensical
    strategy, but perfectly acceptable for demonstrating the
    backtesting infrastructure!"""

    def __init__(self, symbols, bars):
    	"""Requires the symbol ticker and the pandas DataFrame of bars"""
        self.symbols = symbols
        self.bars = bars
        self.signals = {}
        self.na = False


    def generate_signals(self):
        """Creates a naive signal"""
        if sum(pd.isnull(bars.data.ix[symbol, -1, 'Close']))==len(self.symbols):
            for sym in self.symbols:
                self.signals[sym] = 0
            self.na = True
        else:
            for sym in self.symbols:
                if pd.isnull(bars.data.ix[sym,-1,'Close'])==False :
                    self.signals[sym] = np.sign(np.random.randn())
                else:
                    self.signals[sym] = 0
            self.na = False


class OrderEngine():
    def __init__(self, fee_rate=0, tax_rate=0, order_rate=1, slippage_rate=0):
        self.fee_rate = fee_rate
        self.tax_rate = tax_rate
        self.order_rate = order_rate
        self.slippage_rate = slippage_rate

    def execute(self, portfolio):
        """execute orders according to expectation"""
        portfolio.holding = 0
        for sym in portfolio.direction:
            portfolio.position[sym] += portfolio.direction[sym]
            if pd.isnull(portfolio.bars.data.ix[sym, -1, 'Close'])==False:
                portfolio.holding += portfolio.position[sym] * float(portfolio.bars.data.ix[sym, -1, 'Close'])
                portfolio.cash -= portfolio.direction[sym] * float(portfolio.bars.data.ix[sym, -1, 'Close'])


class MarketOnOpenPortfolio(Portfolio):
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

    def __init__(self, symbol, bars, sty, initial_capital=100000.0):
        self.symbol = symbol
        self.cash = initial_capital
        self.holding = 0
        self.start = bars.beg
        self.stop = bars.end
        self.bars = bars
        self.strategy = sty
        self.initial_capital = float(initial_capital)
        self.positions = pd.DataFrame(columns=self.symbol)
        self.position = {}
        self.direction = {}
        self.portfolio = pd.DataFrame(columns=self.symbol)
        self.order_engine = OrderEngine()
        for sym in self.symbol:
            self.position[sym] = 0


    def generate_positions(self):
    	"""Creates a 'positions' DataFrame that simply longs or shorts
    	100 of the particular symbol based on the forecast signals of
    	{1, 0, -1} from the signals DataFrame."""
        for sym in self.symbol:
            self.direction[sym] = 100 * self.strategy.signals[sym]

    def position_analysis(self):
        nadd = pd.Series(self.position)
        nadd.name = self.bars.now
        self.positions = self.positions.append(nadd)

    def optimize_portfolio(self):
        """ it is an empty function right now
        """
        pass

    def backtest_portfolio(self, beg=0, end=0):
    	"""Constructs a portfolio from the positions DataFrame by
    	assuming the ability to trade at the precise market open price
    	of each bar (an unrealistic assumption!).

    	Calculates the total of cash and the holdings (market price of
    	each position per bar), in order to generate an equity curve
    	('total') and a set of bar-based returns ('returns').

    	Returns the portfolio object to be used elsewhere."""

        portfolio_line = {}
        total = self.cash + self.holding
        returns = 0
        if beg != 0:
            self.start = beg
        if end != 0:
            self.stop = end
        # first we update data feed
        while self.bars.proceed == "OK":
            self.bars.update_bars()
            print bars.now
            # then we construct portfolio, we assume tradings occur at close
            # we generate signals

            self.strategy.generate_signals()
            if self.strategy.na:
                portfolio_line['holding'] = 0
                portfolio_line['cash'] = self.cash

            else:
                # we generate positions
                self.generate_positions()
                # we execute orders
                self.order_engine.execute(self)
                # we provide summary of our daily trading
                self.position_analysis()
                portfolio_line['holding'] = self.holding
                portfolio_line['cash'] = self.cash
                # Finalise the total and bar-based returns based on the 'cash'
                # and 'holdings' figures for the portfolio
                portfolio_line['total'] = portfolio_line['cash'] + portfolio_line['holding']
                portfolio_line['date'] = bars.now
                print portfolio_line


if __name__ == "__main__":
    # Obtain daily bars of 603993
    # from BinData module
    symbol = ['000001','603993']
    bars = bindata.BackTestData('~/data/')
    # Create a set of random forecasting signals for 603993
    rfs = RandomForecastingStrategy(symbol, bars)

    # Create a portfolio of 603993
    portfolio = MarketOnOpenPortfolio(symbol, bars, rfs, initial_capital=100000.0)
    portfolio.backtest_portfolio()
