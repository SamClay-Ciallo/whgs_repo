import yfinance as yf 
import pandas_ta as ta 
import pandas as pd 
import numpy as np
from backtesting import Strategy,Backtest
from backtesting.lib import crossover

# Function to collect stock price data
def stock_price_collecting(code, datestart, dateend, period):
    data = yf.Ticker(code)
    prices = data.history(start=datestart, end=dateend, interval=period)
    return prices

# Collect historical price data
stockdata = stock_price_collecting("BILI" , "2019-01-01", "2024-10-20", "1d")
stockdata = pd.DataFrame(stockdata)

def Dochian(data, high_length, low_length):
    """
    Return Dochian Channel for `values`, at
    each step taking into account `n` previous values
    """
    return ta.donchian(data.High.s, data.Low.s, low_length, high_length, talib=False)

def ATR(data, n):
    return np.array(ta.atr(high=data.High.s, low=data.Low.s, close=data.Close.s, length=n, talib=False))
    
    # tr = pd.Series(np.maximum(high - low, high - close, close - low))
    # return tr.rolling(n).mean()
class turtleTrading(Strategy):
    # Define the two MA lags as *class variables*
    
    def init(self):
        print(ATR(self.data, 20))
        self.atr = self.I(ATR, self.data, 20)
        self.donchian = self.I(Dochian, self.data, 150, 10)
        self.last_buy_price = 0
        self.last_buy_atr = 0
    def next(self):
        if not self.position:
        # If today's close exceeds the donchian_upper_bound, buy, record price and ATR
            if self.data.High == self.donchian[2]:
                self.buy()
                self.last_buy_price = self.data.Close[-1]
                self.last_buy_atr = self.atr[-1]
        if self.position:
        # If today's close is below the donchian_lower_bound, sell (end trade)
            if self.donchian[0] == self.data.Low:
                self.position.close()
        # If price decreases by 1.5 times ATR from the last buy point, sell all (stop loss)
            if self.data.Low[-1] < (self.last_buy_price - 2 * self.last_buy_atr):
                self.position.close()

bt = Backtest(stockdata,turtleTrading, cash=100_000)
stats = bt.run()
print(stats)
bt.plot()