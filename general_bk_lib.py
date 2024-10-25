from backtesting import Backtest, Strategy
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from backtesting.lib import crossover

# Function to collect stock price data
def stock_price_collecting(code, datestart, dateend, period):
    data = yf.Ticker(code)
    prices = data.history(start=datestart, end=dateend, interval=period)
    return prices

# Collect historical price data
data = stock_price_collecting("BTC-USD" , "2020-01-01", "2024-10-20", "1d")
data = pd.DataFrame(data)

def bbindicator(data):
    bbans = ta.bbands(close=data.Close.s,std = 2, length=30)
    return bbans.to_numpy().T[:3]

class RSI(Strategy):
    RSIupper = 70
    RSIlower = 30
    RSIWin = 14
    def init(self):
        self.RSI14 = self.I(ta.rsi,pd.Series(self.data.Close),self.RSIWin)

    def next(self):
        if crossover(self.RSI14,self.RSIupper):
            self.position.close()
        elif crossover(self.RSIlower,self.RSI14):
            self.buy(size=0.5)

class BBstrategy(Strategy):
    def init(self):
        self.bbans = self.I(bbindicator,self.data)
    def next(self):
        lowerBand = self.bbans[0]
        upperBand = self.bbans[1]

        if self.position:
            if self.data.Close[-1] > upperBand[-1]:
                self.position.close()
        else:
            if self.data.Close[-1] < lowerBand[-1]:
                self.buy(size=0.5)

bt = Backtest(data,RSI,cash=100_000)
stat = bt.run()
print(stat)
bt.plot()