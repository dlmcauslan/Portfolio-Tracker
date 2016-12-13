#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""                 ValueStock.py
Created on Tue Dec  6 11:37:23 2016

@author: hplustech

Value Stock class that inherits from Stock. Contains extra information that can
be used when performing value avering, such as what percentage of the portfolio
it should be.

"""
from Stock import Stock


class ValueStock(Stock):
    setPercentage = 0
    currentPercentage = None
    desiredBuy = 0
    
    # Class initializer, calls initializer from parent class
    def __init__(self, stockCode, percentage, database):
      super().__init__(stockCode, database)
      self.setPercentage = percentage
      
    # Class string method
    def __str__(self):
         return super().__str__()[:-1] + ", portfolio weighting: {}%.".format(self.setPercentage)
         