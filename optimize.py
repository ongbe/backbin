__author__ = 'fanbin'
from constraint import Constraint
from abc import ABCMeta, abstractmethod

class Optimizer(object):
    """Strategy is an abstract base class providing an interface for
    all subsequent (inherited) trading strategies.

    The goal of a (derived) Strategy object is to output a list of signals,
    which has the form of a time series indexed pandas DataFrame.

    In this instance only a single symbol/instrument is supported."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def gen_positions(self, signals, book):
        """An implementation is required to return the DataFrame of symbols
        containing the signals to go long, short or hold (1, -1 or 0)."""
        raise NotImplementedError("Must implement gen_position()!")


class NaiveOptimizer(Optimizer):
    def __init__(self, constraints):
        self.constraints = constraints

    def gen_positions(self, signals, book):
        """generate expected position of each symbol
        
        Parameters
        ----------
        signals : signals of each symbol

        book:
            pass in book reference so that I can record expected positions
            into the book
 
        """
        total_asset = book.book.ix["Asset",book.ind,'Pos'] + \
            book.book.ix["Cash",book.ind,'Pos']
        for sym in book.symbol:
            book.book.ix[sym, book.ind, 'TargetPos'] = \
            book.book.ix[sym, book.ind, 'PrePos']+signals[sym]['intensity']
            # short selling constraints
            if not self.constraints.short_sell:
                if book.book.ix[sym, book.ind, 'TargetPos'] < 0:
                    book.book.ix[sym, book.ind, 'TargetPos'] = 0
            # leverage constraints
            borrow = (book.book.ix["Asset",book.ind,'Pos'] + \
                book.book.ix["Cash",book.ind,'Pos']) * self.constraints.leverage
            if book.book.ix["Cash",book.ind,'Pos'] > -1.0 * borrow:
                pass
            else:
                book.book.ix[sym, book.ind, 'TargetPos'] = \
                    book.book.ix[sym, book.ind, 'TargetPos'] \
                    if \
                    book.book.ix[sym, book.ind, 'TargetPos'] < \
                    book.book.ix[sym, book.ind, 'Pos']  \
                    else \
                    book.book.ix[sym, book.ind, 'Pos']
        # drawdown constraints
            if total_asset/book.initial_capital <= self.constraints.drawdown:
                self.constraints.drawdown_mark = True


class MarkowitzOptimizer(Optimizer):
    def gen_positions(self, signals, book):
        pass