from backtesting import Backtest, Strategy
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from backtesting.lib import crossover
from backtesting.test import GOOG

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
            self.buy()

# Run the backtest
bt = Backtest(data, RSI, cash=10_000)
stats = bt.run()
bt.plot()