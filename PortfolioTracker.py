#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""                PortfolioTracker.py
Created on Fri Nov 25 11:23:16 2016

@author: dmcauslan

Modified 28/11/2016:
    * Added database funciton in Database class
    * Changed portfolio to be a class that holds all the stocks.
Modified 29/11/2016:
    * Removed purchase function, stock class now takes in the database when
    initialized. Stock class now does all the work.
    * Created stockContract file which holds the database parameters.

To Do:
    * Implement downloading functions.
    * Implement plotting functions.
"""
from Stock import Stock
from Database import Database
import stockContract as SC
import datetime
import os
import os.path
import pandas as pd

# Portfolio class for holding all of the stock objects that the user holds in
# their investment portfolio.
# See stockContract.py for the database contract
class Portfolio:  
    # Class initializer
    def __init__(self, databaseName):
        self.stockList = []
        self.databasePath = "/Users/hplustech/Documents/Canopy/Portfolio Tracker/Databases/" + databaseName + ".db"
        # Create SQL database
        self.stockDatabase = Database(self.databasePath);
        if os.path.isfile(self.databasePath) == False:
            self.stockDatabase.createTable(SC.TABLE_NAME, SC.COLUMN_LIST)

    # Class string method
    def __str__(self):
        returnString = ""
        for stock in self.stockList:
            returnString += str(stock) + "\n"
        return returnString

    
    # Add a new stock with code "stockCode" to the portfolio
    def addStock(self, stockCode):
        newStock = Stock(stockCode, self.stockDatabase)
        self.stockList.append(newStock)
        return newStock
        
    
    # Print a list of stock purchaes in the range dateStart to dateEnd.
    # Setting stockCode to "All" prints all stocks. Otherwise prints list of 
    # purchases for stockCode.    
    def printPurchases(self, stockCode, dateStart = "1800-01-01", dateEnd = str(datetime.date.today())):
        sqlQuery = '''SELECT * FROM {}
            WHERE {} BETWEEN date("{}") and date("{}")'''.format(SC.TABLE_NAME, SC.DATE, dateStart, dateEnd)
        
        if stockCode != "All":
            sqlQuery += ''' AND {} LIKE '{}' '''.format(SC.CODE, stockCode)
      
        queryDataFrame = self.stockDatabase.readDatabase(sqlQuery)
        print(queryDataFrame)
        


            
# Testing code         
myPortfolio = Portfolio("myPortfolio")
vap = myPortfolio.addStock("VAP.AX")
ijr = myPortfolio.addStock("IJR.AX")
veu = myPortfolio.addStock("VEU.AX")
print(myPortfolio)

vap.buy(26, 76.11, "2015-02-26")
#myPortfolio.purchase(vap, 26, 76.11, "2015-02-26")
vap.buy(18, 74.66, "2015-04-29")
vap.buy(1, 71.47, "2015-10-19")
vap.buy(1, 73.32, "2016-01-19")
ijr.buy(61, 115.22, "2014-04-29")
veu.buy(27, 55.25, "2014-05-13")
veu.buy(20, 55.26, "2014-05-20")
veu.buy(25, 56.08, "2014-07-29")
veu.buy(16, 65.60, "2015-07-29")
myPortfolio.printPurchases("All")
myPortfolio.printPurchases("VEU.AX", "2014-01-01", "2015-01-01")
print(myPortfolio)

print(veu.getOwned())
veu.getPrice("2016-11-28")

# The line below is just so we don't readd the data every time.
myPortfolio.stockDatabase.clearTable(SC.TABLE_NAME)

