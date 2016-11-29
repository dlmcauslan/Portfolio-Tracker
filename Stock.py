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
import pandas as pd


class Stock:
    numberOwned = 0
    totalCost = 0
    
    def __init__(self, stockCode):
      self.stockCode = stockCode
    
    def __str__(self):
         return "{} - number owned: {}, total cost: ${:.2f}".format(self.stockCode, self.numberOwned, self.totalCost)

    
    # Buy a number of stocks at a price and save in the database     
    def buy(self, numberBought, price, database, tableName, date = str(datetime.date.today())):
        self.numberOwned += numberBought
        self.totalCost += numberBought*price
        purchaseData = pd.DataFrame({"Stock_Code": [self.stockCode],
                                     "Purchase_Date": [date],
                                     "Number_Purchased": [numberBought],
                                     "Price": [price],
                                     "Total_Cost": [price*numberBought]})
        database.addToDatabase(purchaseData, tableName)
    
    
    # Get the price of the stock at date. Default date is today.
    def getPrice(self, date = str(datetime.date.today())):
        pass
        
