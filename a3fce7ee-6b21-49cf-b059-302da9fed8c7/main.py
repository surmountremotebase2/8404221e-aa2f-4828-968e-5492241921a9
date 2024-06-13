from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.data import Asset, InstitutionalOwnership
import numpy as np
import pandas as pd

def gaussian(x):
   return np.exp(-x**2 / 2)

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
      self.ticker_weights = pd.Series(np.zeros(len(self.tickers)), self.tickers)
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
      P0 = np.prod(gaussian(growth / self.std.loc))

      for group in self.groups:
         group_growth = growth[group]
         mean = np.mean(group_growth)
         P_common = np.prod(gaussian((group_growth - mean) / std.loc[group]))
         P_seperate = P0[group]
         is_up = mean > 0 and P_common > 4 * P_seperate
         is_down = mean < 0 and P_common > 4 * P_seperate
         
         if is_up:
            weight = np.where(group_growth > std, group_growth, std)
            self.ticker_weights[group] = weight
         elif is_down:
            self.ticker_weights[group] = 0

      weights_sum = np.sum(self.ticker_weights)
      self.ticker_weights /= weights_sum
      if np.isclose(weights_sum, 0):
         return TargetAllocation({})
      return TargetAllocation(self.ticker_weights.to_dict())