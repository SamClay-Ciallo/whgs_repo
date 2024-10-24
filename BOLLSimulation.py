import numpy as np 
import yfinance as yf
import matplotlib.pyplot as plt 
import pandas as pd 
#import backtesting as bt
from backtesting import Strategy
from backtesting.lib import crossover
from backtesting import Backtest
# Example OHLC daily data for Google Inc.
from backtesting.test import GOOG

GOOG.tail()

def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()

def BOLL(values, n, m):
    """
    Return Bollinger Bands for `values`, at
    each step taking into account `n` previous values
    and `m` standard deviations away from the mean.
    """
    sma = SMA(values, n)
    std = pd.Series(values).rolling(n).std()
    return sma, sma + m * std, sma - m * std

class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    s1 = 1
    s2 = 2
    s3 = 3
    
    def init(self):
        # Precompute the two moving averages
        self.boll_1 = self.I(BOLL, self.data.Close, 20, self.s1)
        self.boll_2 = self.I(BOLL, self.data.Close, 20, self.s2)
        self.boll_3 = self.I(BOLL, self.data.Close, 20, self.s3)
    
    def next(self):
        # If price is between the lower band of boll_2 and boll_3, AND the price continue to rise for three days, buy
        if self.data.Close[-1] > self.boll_2[-1][2] and self.data.Close[-1] < self.boll_3[-1][2]:
            self.position.close()
            self.buy()
    
        # If price is between the upper band of boll_2 and boll_3, AND the price continue to drop for three days, sell
        elif self.data.Close[-1] < self.boll_2[-1][1] and self.data.Close[-1] > self.boll_3[-1][1]:
            self.position.close()
            self.sell()
            
bt = Backtest(GOOG, SmaCross, cash=10_000, commission=.002)
stats = bt.run()
print(stats)