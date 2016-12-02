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
Modified 30/11/2016:
    * On initialization now creates a table in the database for holding historical
    price information for the stocks.
    * Implemented getValue() and getCost() methods to calculate the total 
    value and cost of the portfolio on specific date.
Modified 1/12/2016:
    * Implemented plot method which plots a selection of stocks in the portfolio
    over a date range.
    * Implemented plotPortfolio method which plots the performance of the entire
    portfolio.

To Do:
    * Try to get plotPortfolio working with an outer join.
    * Check that getValueRange() etc methods give results ordered by date.
"""
from Stock import Stock
from Database import Database
import stockContract as SC
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

###############
## Constants ##
###############
DEFAULT_DATE = str(datetime.date.today())
DEFAULT_STARTDATE = "1900-01-01"
DEFAULT_STOCKCODE = "All"

####################
## Helper Methods ##
####################
# Takes in a date in the format "yyyy-mm-dd" and decrements it by one day. 
def decrementDate(dateString):
    [year, month, day] = dateString.split("-")
    dateTime = datetime.date(int(year), int(month), int(day))
    dateMinus = dateTime - datetime.timedelta(1)
    return str(dateMinus)
    
# Converts a date in "yyyy-mm-dd" format to a dateTime object
def convertDate(date):
    [year, month, day] = map(int, date.split("-"))
    return datetime.date(year, month, day)
    
    
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
        # Create tables
        self.stockDatabase.createTable(SC.TABLE_NAME, SC.COLUMN_LIST)
        self.stockDatabase.createTable(SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_COLUMN_LIST)

        
    # Class string method
    def __str__(self):
        returnString = ""
        for stock in self.stockList:
            returnString += str(stock) + "\n"
        returnString += "Total cost of portfolio is ${:.2f}.\nTotal portfolio value is ${:.2f}." \
        .format(self.getCost(DEFAULT_DATE), self.getValue(DEFAULT_DATE))
        return returnString

    
    # Add a new stock with code "stockCode" to the portfolio
    def addStock(self, stockCode):
        newStock = Stock(stockCode, self.stockDatabase)
        self.stockList.append(newStock)
        return newStock
     
        
    # Calculate the total value of the portfolio on a particular date
    def getValue(self, date = DEFAULT_DATE):
        result = None
        while result is None:
            try:
                totalValue = 0
                for stock in self.stockList:
                    totalValue += stock.getValue(date)
                result = totalValue
            except:
                # decrement date by one day
                date = decrementDate(date)

        return result
        
        
    # Calculate the total cost of the portfolio on a particular date
    def getCost(self, date = DEFAULT_DATE):
        totalSpent = 0
        for stock in self.stockList:
            totalSpent += stock.totalCost
        return totalSpent
     
        
    # Print a list of stock purchaes in the range dateStart to dateEnd.
    # Setting stockCode to "All" prints all stocks. Otherwise prints list of 
    # purchases for stockCode.    
    def printPurchases(self, stockCode = DEFAULT_STOCKCODE, dateStart = DEFAULT_STARTDATE, dateEnd = DEFAULT_DATE):
        sqlQuery = '''SELECT * FROM {}
            WHERE {} BETWEEN date("{}") and date("{}")'''.format(SC.TABLE_NAME, SC.DATE, dateStart, dateEnd)
        
        if stockCode != DEFAULT_STOCKCODE:
            sqlQuery += ''' AND {} LIKE '{}' '''.format(SC.CODE, stockCode)
        
        sqlQuery += ''' ORDER BY {} '''.format(SC.DATE)    
        queryDataFrame = self.stockDatabase.readDatabase(sqlQuery)
        print(queryDataFrame)
        
    
    # Plots the stocks in the list stockList over the daterange. If stockList == "All",
    # it plots all of the stocks in the portfolio.
    def plot(self, stockList = DEFAULT_STOCKCODE, dateStart = DEFAULT_STARTDATE, dateEnd = DEFAULT_DATE):
        plt.close("all")
        if stockList == DEFAULT_STOCKCODE:
            stockList = self.stockList
        for stock in stockList:
            stock.plot(dateStart, dateEnd)
        
    def plotPortfolio(self, dateStart = DEFAULT_STARTDATE, dateEnd = DEFAULT_DATE):
        plt.close("all")
        # Plot portfolio totals
        date = self.stockList[0].getValueRange(dateStart, dateEnd)[SC.HISTORICAL_DATE].tolist()
        
        spent = pd.DataFrame({SC.HISTORICAL_DATE: date, SC.TOTAL_SPENT: list(np.zeros(len(date)))})
        value = pd.DataFrame({SC.HISTORICAL_DATE: date, "Value": list(np.zeros(len(date)))})
        
        for s in self.stockList:
            spent = pd.merge(spent, s.getSpentRange(dateStart, dateEnd), how = "inner", on = SC.HISTORICAL_DATE)
#            spent = spent.fillna(0)
            value = pd.merge(value, s.getValueRange(dateStart, dateEnd), how = "inner", on = SC.HISTORICAL_DATE)
#            value = value.fillna(0)

            
#        print(spent)
        spent["Total"] = spent.sum(axis = 1)
        value["Total"] = value.sum(axis = 1)
#        print(spent)
        

        date = list(map(convertDate, spent[SC.HISTORICAL_DATE]))
        
#        print(spent)
        print(len(date))
        print(len(list(spent["Total"])))
#         Do plotting
        fig = plt.figure()
        plt.clf()    
        ax = fig.add_subplot(311)
        plt.title("Portfolio Totals", fontsize = 16)
        ax.plot(date, spent["Total"])
        plt.ylabel("Spent ($)", fontsize = 14)
        ax = fig.add_subplot(312)
        ax.plot(date, value["Total"])
        plt.ylabel("Value ($)", fontsize = 14)
        ax = fig.add_subplot(313)
        plt.plot(date, value["Total"] - spent["Total"])
        plt.ylabel("Profit ($)", fontsize = 14)
        plt.xlabel("Date", fontsize = 14)
#        plt.tight_layout()    
        plt.show() 
        


            
# Testing code
try:         
    myPortfolio = Portfolio("myPortfolio")
    vap = myPortfolio.addStock("VAP.AX")
    ijr = myPortfolio.addStock("IJR.AX")
    veu = myPortfolio.addStock("VEU.AX")
#    print(myPortfolio)
    
#    vap.buy(26, 76.11, "2015-02-26")
#    vap.buy(18, 74.66, "2015-04-29")
#    vap.buy(1, 0, "2015-10-19")
#    vap.buy(1, 0, "2016-01-19")
#    ijr.buy(61, 115.22, "2014-04-29")
#    veu.buy(27, 55.25, "2014-05-13")
#    veu.buy(20, 55.26, "2014-05-20")
#    veu.buy(25, 56.08, "2014-07-29")
#    veu.buy(16, 65.60, "2015-07-29")
#    veu.sell(10, 100, "2016-06-01")
#    veu.buy(20, 100, "2016-06-02")
#    veu.sell(10, 100, "2014-06-01")
#    veu.remove(-10, 52.3, "2014-06-01")
#    veu.remove(20, 59.3, "2016-06-02")
#    veu.remove(-10, 59.3, "2016-06-01")
##    veu.remove(100, 100, "2016-12-01")


    myPortfolio.printPurchases("All")
#    myPortfolio.printPurchases("VEU.AX", "2014-01-01", "2015-01-01")
    myPortfolio.printPurchases("VEU.AX")
    print(myPortfolio)
    
#    print(veu.getOwned())
#    print(veu.getPrice("2016-11-28"))
#    print("VEU ${:.2f} ${:.2f}".format(veu.getValue("2016-11-29"), veu.totalCost))
#    print("IJR ${:.2f} ${:.2f}".format(ijr.getValue("2016-11-29"), ijr.totalCost))
#    print("VAP ${:.2f} ${:.2f}".format(vap.getValue("2016-11-29"), vap.totalCost))
#    print(vap.getPriceRange("2015-02-26", "2016-01-19"))
#    print(veu.getOwnedRange("2016-05-26"))
#    print(veu.getSpentRange("2014-05-12"))
#    veu.plot("2014-03-01")
#    myPortfolio.plot("All", "2014-01-01")
    myPortfolio.plotPortfolio("2014-01-01")
    
#    sqlQuery = '''SELECT * FROM {} '''.format(SC.HISTORICAL_TABLE_NAME)
#    print(myPortfolio.stockDatabase.readDatabase(sqlQuery))
    

# The line below is just so we don't readd the data every time.
finally:
    print("\n")
#    myPortfolio.stockDatabase.removeTable(SC.TABLE_NAME)
#    myPortfolio.stockDatabase.clearTable(SC.TABLE_NAME)


