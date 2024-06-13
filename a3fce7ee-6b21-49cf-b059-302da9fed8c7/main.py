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
      self.ticker_weights = pd.Series(np.zeros(len(self.tickers)), self.tickers)
      std = np.array([0.00044579, 0.00055604, 0.00051888, 0.00068454, 0.00080117,
       0.00110932, 0.00162267, 0.00065973, 0.00069862, 0.00086113,
       0.00080581, 0.00099203, 0.0011805 , 0.00057911, 0.00082099,
       0.00039721, 0.0004349 , 0.00046398, 0.00072686, 0.00050613,
       0.00037251, 0.00039559, 0.0005137 , 0.00053776, 0.00039221,
       0.00061281, 0.00049111, 0.00033921, 0.00038491, 0.00052309,
       0.00054585, 0.00044529, 0.00055282, 0.00057993, 0.0005003 ,
       0.00065213, 0.00046398, 0.00046402, 0.00053135, 0.00038334,
       0.00053261, 0.0004349 , 0.00050653, 0.00058355, 0.0006026 ,
       0.00051529, 0.00075865, 0.00080117, 0.00065973, 0.00069862,
       0.00086113, 0.00083045, 0.00068741, 0.00080581, 0.00075914,
       0.00121803, 0.00070756, 0.00081818, 0.00057911, 0.00082099,
       0.00056341, 0.00068642, 0.00036144, 0.0002576 , 0.00036496,
       0.00053243, 0.00035848, 0.00038705, 0.0003358 ])
      self.std = pd.Series(std, self.tickers)
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