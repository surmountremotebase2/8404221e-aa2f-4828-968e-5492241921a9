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
      groups = [
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
      self.tickers = sum(groups, start=[])
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

      vols = [i["VIRT"]["volume"] for i in data["ohlcv"]]
      smavols = SMAVol("VIRT", data["ohlcv"], 30)
      smavols2 = SMAVol("VIRT", data["ohlcv"], 10)

      if len(vols)<=4:
            return TargetAllocation({})

      try:
         if smavols2[-1]/smavols[-1]-1>0:
               out = smavols2[-1]/smavols[-1]-1
         else: out = 0
      except: return None
      return TargetAllocation({"VIRT": min(0.95, (out*5)**(1/3))})