import yfinance as yf
import talib
import pandas as pd

from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# Get the historical data for Google from Yahoo Finance
data = pd.read_csv("/workspaces/Trading-Bot-BTC/daily_data/ADA-USD.csv")

class SMA_Crossover(Strategy):
    n1 = 50
    n2 = 200

    def init(self):
        close = self.data.Close
        self.sma1 = self.I(talib.SMA, close, self.n1)
        self.sma2 = self.I(talib.SMA, close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()

class Complex_Strategy(Strategy):
    n1 = 20
    n2 = 50
    n3 = 200
    n4 = 10

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        volume = self.data.Volume
        self.sma1 = self.I(talib.SMA, close, self.n1)
        self.sma2 = self.I(talib.SMA, close, self.n2)
        self.sma3 = self.I(talib.SMA, close, self.n3)
        self.rsi = self.I(talib.RSI, close, timeperiod=14)
        self.adx = self.I(talib.ADX, high, low, close, timeperiod=14)
        self.adxr = self.I(talib.ADXR, high, low, close, timeperiod=14)
        self.macd, self.macd_signal, self.macd_hist = self.I(talib.MACD, close.astype(float), fastperiod=12, slowperiod=26, signalperiod=9)
        self.obv = self.I(talib.OBV, close, volume)
        self.wma = self.I(talib.WMA, close, timeperiod=10)

    def next(self):
        if crossover(self.sma1, self.sma2) and self.rsi > 50 and self.adx > self.adxr:
            self.buy()
        elif crossover(self.sma2, self.sma1) and self.rsi < 50 and self.adx < self.adxr:
            self.sell()
        elif self.macd > self.macd_signal and self.rsi > 60 and self.obv > self.wma:
            self.buy()
        elif self.macd < self.macd_signal and self.rsi < 40 and self.obv < self.wma:
            self.sell()
        else:
            self.hold()


bt = Backtest(data, Complex_Strategy, cash=10000, commission=0.002)
results = bt.run()
print(results)
