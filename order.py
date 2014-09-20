__author__ = 'fanbin'

import random
import pandas as pd
import math

class OrderEngine():
    def __init__(self, fee_rate=0, tax_rate=0, order_rate=1, slippage_rate=0, missing_rate=0):
        self.fee_rate = fee_rate
        self.tax_rate = tax_rate
        self.order_rate = order_rate
        self.slippage_rate = slippage_rate
        self.missing_rate = missing_rate

    def execute(self, book):
        """execute orders according to book instruction"""
        # portfolio.holding = 0
        for sym in book.symbol:
            # test if today is trading
            if not pd.isnull(book.bar.data.ix[sym, -1, 'Close']):
                # incorporate missing rate for unfilled orders
                actual_execute_amount =  \
                    int( (book.book.ix[sym, book.ind, 'TargetPos'] - \
                    book.book.ix[sym, book.ind, 'PrePos'])
                    * (1 if random.uniform > self.missing_rate else self.missing_rate))
                book.book.ix[sym, book.ind, 'Pos'] = \
                    book.book.ix[sym, book.ind, 'PrePos'] + actual_execute_amount
                actual_execute_price = (1 + \
                    math.copysign(self.slippage_rate, actual_execute_amount)/100) \
                    * float(book.bar.data.ix[sym, -1, 'Close'])
                book.book.ix[sym, book.ind, 'mmk'] = actual_execute_price
                book.book.ix['Cash', book.ind, 'Pos'] -= \
                    actual_execute_amount * actual_execute_price
