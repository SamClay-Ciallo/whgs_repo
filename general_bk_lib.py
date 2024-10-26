from backtesting import Backtest, Strategy
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from backtesting.lib import crossover
from backtesting.test import SMA

# Function to collect stock price data
def stock_price_collecting(code, datestart, dateend, period):
    data = yf.Ticker(code)
    prices = data.history(start=datestart, end=dateend, interval=period)
    return prices

# Collect historical price data
data = stock_price_collecting("AAPL" , "2020-01-01", "2024-10-20", "1d")
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

class BollingerPlus(Strategy):
    RSIupper = 70
    RSIlower = 28
    RSIWin = 13
    mawindowS = 15
    mawindowL = 100

    def init(self):
        self.bbans = self.I(bbindicator,self.data)
        self.RSI14 = self.I(ta.rsi,pd.Series(self.data.Close),self.RSIWin)
        self.smaS = self.I(SMA,self.data.Close,self.mawindowS)
        self.smaL = self.I(SMA,self.data.Close,self.mawindowL)
    def next(self):
        lowerBand = self.bbans[0]
        upperBand = self.bbans[1]

        if self.position:
            if self.data.High[-1] > upperBand[-1]:
                self.position.close()
        else:
            if self.data.Low[-1] < lowerBand[-1] and (self.smaS[-1] > self.bbans[1] and self.smaS[-1] > self.smaL[-1]):
                self.buy(size=0.5)

class whatEverStrategy(Strategy):
    def init(self):
        pass
    def next(self):
        if self.position:
            if self.data.Close[-1] < self.data.Close[-2]:
                self.position.close()
        else:
            if self.data.Close[-1] > self.data.Close[-2]:
                self.buy()

bt = Backtest(data,BollingerPlus,cash=100_000)
stat = bt.run()
print(stat)
bt.plot()


