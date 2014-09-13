__author__ = 'fanbin'

import numpy as np
import pandas as pd
from optimize import Optimizer
import bindata
import math
import random
import event
"""import talib"""


from backtest import Strategy


class CurrentStrategy(Strategy):
    """Derives from Strategy to produce a set of signals that
    are randomly generated long/shorts. Clearly a nonsensical
    strategy, but perfectly acceptable for demonstrating the
    backtesting infrastructure!"""

    def __init__(self, symbols, bars):
        """Requires the symbol ticker and the pandas DataFrame of bars"""
        self.symbols = symbols
        self.bars = bars
        self.signals = pd.DataFrame(columns=self.symbols, index=["mark", "signal", "intensity", "credibility", "risk"])
        self.na = False
        self.sig_generator = None

    def check_halt(self):
        pass

    def all_halt(self):
        return sum(pd.isnull(self.bars.data.ix[self.symbols, -1, 'Close'])) == len(self.symbols)

    def halt(self, sym):
        return pd.isnull(self.bars.data.ix[sym, -1, 'Close'])

    def generate_signals(self):
        """Creates a naive signal"""
        if self.all_halt():
            self.na = True
        else:
            self.na = False
            for sym in self.symbols:
                if pd.isnull(self.bars.data.ix[sym, -1, 'Close']):
                    self.signals[sym]['intensity'] = 0
                    self.signals[sym]['credibility'] = 0
                    self.signals[sym]["mark"] = 0
                else:
                    self.signals[sym]["mark"] = 1
            self.sig_generator(self.signals)
            # function_list["generate_signals"](self.signals)

    def sig_generator(self, signals):
        """Creates a naive signal"""
        symbols = signals.columns.tolist()
        for sym in symbols:
            if signals[sym]["mark"]==1:
                signals[sym]['signal'] = np.sign(np.random.randn())
                signals[sym]['intensity'] = 100 * signals[sym]['signal']
                signals[sym]['credibility'] = 0
