from backtesting import Backtest, Strategy
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from backtesting.lib import crossover
from backtesting.test import GOOG

# Download historical data for Google
data = yf.download("GOOG", start="2020-01-01", end="2024-01-01")

class RSI(Strategy):
    RSIupper = 70
    RSIlower = 30
    RSIWin = 14

    def init(self):
        # Calculate RSI
        self.RSI14 = self.I(ta.rsi, self.data.Close, self.RSIWin)

    def next(self):
        # If RSI crosses above the upper threshold, sell
        if crossover(self.RSI14, self.RSIupper):
            self.position.close()
        # If RSI crosses below the lower threshold, buy
        elif crossover(self.RSIlower, self.RSI14):
            self.buy()

# Run the backtesta
bt = Backtest(data, RSI, cash=10_000)
stats = bt.run()
print(stats)
#bt.plot()