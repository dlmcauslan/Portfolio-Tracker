#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""                PortfolioTracker.py
Created on Fri Nov 25 11:23:16 2016

@author: dmcauslan

Modified 28/22/2016:
    * Added database funciton in Database class
    * Changed portfolio to be a class that holds all the stocks.

To Do:
    * Implement downloading functions.
    * Implement plotting functions.
"""
#import Stock as s
from Stock import Stock
from Database import Database
import datetime
import os
import os.path
import pandas as pd

class Portfolio:  
    tableName = "stockPurchases"
    rowList = "Stock_Code TEXT, Purchase_Date TEXT, Number_Purchased INT, Price REAL, Total_Cost REAL"
    rows = ["Stock_Code", "Purchase_Date", "Number_Purchased", "Price", "Total_Cost"]

    
    def __init__(self, databaseName):
        self.stockList = []
        self.databasePath = "/Users/hplustech/Documents/Canopy/Portfolio Tracker/Databases/" + databaseName + ".db"
        # Create SQL database
        self.stockDatabase = Database(self.databasePath);
        if os.path.isfile(self.databasePath) == False:
            self.stockDatabase.createTable(self.tableName, self.rowList)

    
    def __str__(self):
        returnString = ""
        for stock in self.stockList:
            returnString += str(stock) + "\n"
        return returnString

        
    def addStock(self, stockCode):
        newStock = Stock(stockCode)
        self.stockList.append(newStock)
        return newStock
       
        
    def purchase(self, stock, numberBought, price, date = str(datetime.date.today())):
        stock.buy(numberBought, price, self.stockDatabase, self.tableName, date)
        
    
    def printPurchases(self, stockCode, dateStart = "1800-01-01", dateEnd = str(datetime.date.today())):
        if stockCode == "All":
            sqlQuery = '''SELECT * FROM {}'''.format(self.tableName)
        else:
            sqlQuery = '''SELECT * FROM {} 
            WHERE Stock_Code LIKE '{}' 
            AND Purchase_Date BETWEEN date("{}") and date("{}")'''.format(self.tableName, stockCode, dateStart, dateEnd)
            print(dateStart)
        queryDataFrame = self.stockDatabase.readDatabase(sqlQuery)
        print(queryDataFrame)
        


            
# Testing code         
myPortfolio = Portfolio("myPortfolio")
vap = myPortfolio.addStock("VAP.AX")
ijr = myPortfolio.addStock("IJR.AX")
veu = myPortfolio.addStock("VEU.AX")
print(myPortfolio)

#datetime.date.today()
#myPortfolio.purchase(vas, 10, 32.30, datetime.date(2016, 12, 19))
myPortfolio.purchase(vap, 26, 76.11, "2015-02-26")
myPortfolio.purchase(vap, 18, 74.66, "2015-04-29")
myPortfolio.purchase(vap, 1, 71.47, "2015-10-19")
myPortfolio.purchase(vap, 1, 73.32, "2016-01-19")
myPortfolio.purchase(ijr, 61, 115.22, "2014-04-29")
myPortfolio.purchase(veu, 27, 55.25, "2014-05-13")
myPortfolio.purchase(veu, 20, 55.26, "2014-05-20")
myPortfolio.purchase(veu, 25, 56.08, "2014-07-29")
myPortfolio.purchase(veu, 16, 65.60, "2015-07-29")
myPortfolio.printPurchases("All")
myPortfolio.printPurchases("IJR.AX", "2014-01-01", "2015-01-01")
# The line below is just so we don't readd the data every time.
myPortfolio.stockDatabase.clearTable(myPortfolio.tableName, myPortfolio.rows)

print(myPortfolio)