from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.data import Asset, InstitutionalOwnership
import numpy as np
import scipy
import pandas as pd

def SMAVol(ticker, data, length):
   '''Calculate the moving average of trading volume

   :param ticker: a string ticker
   :param data: data as provided from the OHLCV data function
   :param length: the window

   :return: list with float SMA
   '''
   close = [i[ticker]["volume"] for i in data]
   d = ta.sma(pd.Series(close), length=length)
   if d is None:
      return None
   return d.tolist()

class TradingStrategy(Strategy):
   def __init__(self):
      self.groups = [
         ["MSFT", "AMZN", "GOOG", "META"],
         ["AMAT", "AMD", "ARM", "ASML", "ASX", "AVGO", "LRCX", "MU", "NVDA", "STM", "TSM"],
         ["BRK-B", "PRU", "JPM"],
         ["LLY", "NVO"],
         ["V", "MA"],
         ["WMT", "COST"],
         ['BP', 'CNQ', 'CVX', 'SHEL', 'TTE', 'XOM'],
         #['CHD', 'CL', 'KMB', 'PG'],
         #['KO', 'PEP', 'MDLZ'],
         #['HD', 'LOW'],
         ['BAC', 'BK', 'C', 'FITB', 'GS', 'HBAN', 'JPM', 'MET', 'MTB', 'PFG', 'PNC', 'PRU', 'STT', 'TFC', 'USB', 'WFC'],
         ['ADI', 'AMAT', 'ASML', 'ASX', 'AVGO', 'ENTG', 'KLAC', 'LRCX', 'MCHP', 'MRVL', 'NXPI', 'QCOM', 'STM', 'TSM', 'TXN', 'UMC'],
         ['SAP', 'RELX'],
         #['TMO', 'DHR', 'A'],
         #['ABT', 'MDT'],
         ['HSBC', 'BCS', 'ING', 'DB', 'UBS'],
         #['PM', 'MO'],
      ]
      self.tickers = sum(self.groups, start=[])
      self.std = pd.read_csv("std.csv")
      self.data_list = []

   @property
   def interval(self):
      return "1min"

   @property
   def assets(self):
      return self.tickers

   @property
   def data(self):
      return self.data_list

   def run(self, data):
      data = data.loc[self.tickers, "ohlcv"]
      growth = (data["close"] - data["open"]) / data["open"]
      P0 = np.prod(scipy.stats.norm.pdf(growth / self.std.loc))

      for group in self.groups:
         group_growth = growth[group]
         mean = np.mean(group_growth)
         P_common = np.prod(scipy.stats.norm.pdf((group_growth - mean) / std.loc[group]))
         P_seperate = P0[group]
         is_up = mean > 0 and P_common > 4 * P_seperate
         is_down = mean < 0 and P_common > 4 * P_seperate
         
      
      return TargetAllocation({"VIRT": min(0.95, (out*5)**(1/3))})