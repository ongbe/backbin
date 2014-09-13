__author__ = 'fanbin'

class Constraint():
    def __init__(self, short_sell=False, pos_lim=0.95, leverage=0, drawdown=0.6):
        self.short_sell = short_sell
        self.pos_lim = pos_lim
        self.pos_lim_mark = False
        self.leverage = leverage
        self.leverage_mark = False
        self.drawdown = drawdown
        self.drawdown_mark = False
