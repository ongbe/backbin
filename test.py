__author__ = 'fanbin'

from strategy import CurrentStrategy
from portfolio import MarketOnClosePortfolio
from optimize import NaiveOptimizer
from constraint import Constraint
import bindata
import json
import cProfile
import re


def task_backtest():
    symbol = ['000001', '603993']
    bars = bindata.BackTestData(bindata.raw)
    # Apply our current strategy on the chosen stock pool
    rfs = CurrentStrategy(symbol, bars)
    # specify constraints, here is the default one
    cons = Constraint()
    # specify a naive optimizer
    opt = NaiveOptimizer(cons)
    function_list = {}
    exec generate_signals in function_list
    # Create a portfolio
    portfolio = MarketOnClosePortfolio(symbol, bars, rfs, opt, initial_capital=1000000.0)
    exec generate_signals in function_list

    portfolio.strategy.sig_generator = function_list["generate_signals"]
    # Backtest our portfolio and store result in book

    book = portfolio.backtest_portfolio_external()
    ret = book.nav_to_json()
    print ret
    return json.dumps(ret)


generate_signals = compile('''
import numpy as np
def generate_signals(signals):
    symbols = signals.columns.tolist()
    for sym in symbols:
        if signals[sym]["mark"]==1:
            signals[sym]['signal'] = np.sign(np.random.randn())
            signals[sym]['intensity'] = 100 * signals[sym]['signal']
            signals[sym]['credibility'] = 0
''', '<string>', 'exec')

if __name__ == "__main__":
    task_backtest()