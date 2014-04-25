# random_forecast.py

import numpy as np
import pandas as pd
import bindata
import event


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


    def generate_signals(self):
        """Creates a naive signal"""
        if sum(pd.isnull(bars.data.loc[symbol].ix[:, -1, 'Close']))==len(symbols):
            for sym in self.symbols:
                self.signals[sym] = 0
        else:
            for sym in self.symbols:
                self.signals[sym] = np.sign(np.random.randn())


class OrderEngine():
    def __init__(self, fee_rate, tax_rate, order_rate, slippage_rate):
        self.fee_rate = fee_rate
        self.tax_rate = tax_rate
        self.order_rate = order_rate
        self.slippage_rate = slippage_rate

    def execute(self, bars, capital, position, direction):
        """execute orders according to expectation"""
        for sym in direction:
            position[sym] += direction[sym]
            capital -= direction[sym] * float(bars.data.loc[[sym]].ix[:, -1, 'Close'])


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

    def __init__(self, symbol, bars, signals, initial_capital=100000.0):
        self.symbol = symbol
        self.bars = bars
        self.signals = signals
        self.initial_capital = float(initial_capital)
        self.positions = pd.DataFrame(columns=self.symbol)
        self.position = {}
        self.direction = {}
        self.portfolio = pd.DataFrame(columns=self.symbol)
        for sym in self.symbol:
            self.position[sym] = 0


    def generate_positions(self):
    	"""Creates a 'positions' DataFrame that simply longs or shorts
    	100 of the particular symbol based on the forecast signals of
    	{1, 0, -1} from the signals DataFrame."""
        for sym in self.symbol:
            self.direction[sym] = 100 * self.signals[sym]

        nadd = pd.Series(self.position)
        nadd.name = bars.now
        self.positions = self.positions.append(nadd)


    def optimize_portfolio(self):
        """here it is an empty function
        """


    def backtest_portfolio(self):
    	"""Constructs a portfolio from the positions DataFrame by
    	assuming the ability to trade at the precise market open price
    	of each bar (an unrealistic assumption!).

    	Calculates the total of cash and the holdings (market price of
    	each position per bar), in order to generate an equity curve
    	('total') and a set of bar-based returns ('returns').

    	Returns the portfolio object to be used elsewhere."""

    	# Construct the portfolio DataFrame to use the same index
    	# as 'positions' and with a set of 'trading orders' in the
    	# 'pos_diff' object, assuming market open prices.

        portfolio_line = {}
        cash = self.initial_capital
        holding = 0
        total = cash + holding
        returns = 0

        # first we update data feed
        self.bars.update_bars()

        # then we construct portfolio, we assume tradings occur at close
        portfolio_line['holding'] = sum(self.positions.ix[-1] * self.bars.data.loc[self.symbol].ix[:, -1, 'Close'])

        # Create the 'holdings' and 'cash' series by running through
        # the trades and adding/subtracting the relevant quantity from
        # each column

        portfolio_line['cash'] = cash

        # Finalise the total and bar-based returns based on the 'cash'
        # and 'holdings' figures for the portfolio
        portfolio_line['total'] = portfolio_line['cash'] + portfolio_line['holdings']

        # portfolio_history['returns'] = portfolio_history['total'].pct_change()
        # return portfolio_history


if __name__ == "__main__":
    # Obtain daily bars of 603993
    # from BinData module
    symbol = ['603993']
    dt = bindata.BackTestData('~/data/')
    bars = dt
    # Create a set of random forecasting signals for 603993
    rfs = RandomForecastingStrategy(symbol, bars)
    signals = rfs.generate_signals()

    # Create a portfolio of 603993
    portfolio = MarketOnOpenPortfolio(symbol, bars, signals, initial_capital=100000.0)
    returns = portfolio.backtest_portfolio()
    print returns.tail(10)