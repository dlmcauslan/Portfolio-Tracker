#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""                       Stock.py
Created on Fri Nov 25 11:32:32 2016

@author: dmcauslan

Stock class that contains the information
- Number owned
- Total cost
- Stock Code
And has a buy method that is used to buy that stock

"""
import datetime


class Stock:
    numberOwned = 0
    totalCost = 0
    
    def __init__(self, stockCode):
      self.stockCode = stockCode
    
    def __str__(self):
         return "{} - number owned: {}, total cost: {}".format(self.stockCode, self.numberOwned, self.totalCost)

      
    def buy(self, numberBought, price, date = datetime.date.today()):
        self.numberOwned += numberBought
        self.totalCost += numberBought*price
        ## Add method here to add to database
    
        
