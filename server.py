__author__ = 'fanbin'

from strategy import CurrentStrategy
from portfolio import MarketOnClosePortfolio
from optimize import NaiveOptimizer
from constraint import Constraint
import bindata
import json
from gearman import GearmanWorker

gm_worker = GearmanWorker(['127.0.0.1:4730'])

def task_backtest(gearman_worker, gearman_job):
    symbol = ['000001', '603993']
    bars = bindata.BackTestData(bindata.raw)
    # Apply our current strategy on the chosen stock pool
    rfs = CurrentStrategy(symbol, bars)
    # specify constraints, here is the default one
    cons = Constraint()
    # specify a naive optimizer
    opt = NaiveOptimizer(cons)

    data = json.loads(gearman_job.data)
    function_list = {}
    signal_generator = compile(data["code"], '', 'exec')
    exec signal_generator in function_list

    # Create a portfolio
    portfolio = MarketOnClosePortfolio(symbol, bars, rfs, \
                opt, initial_capital=1000000.0)
    portfolio.strategy.sig_generator = function_list["generate_signals"]
    # Backtest our portfolio and store result in book
    book = portfolio.backtest_portfolio(worker=gearman_worker, job=gearman_job)
    ret = book.nav_to_json()
    return json.dumps(ret)


if __name__ == "__main__":
    # gm_worker.set_client_id is optional
    gm_worker.set_client_id('python-worker')
    gm_worker.register_task('backtest', task_backtest)
    # Enter our work loop and call gm_worker.after_poll() after each time we timeout/see socket activity
    gm_worker.work()