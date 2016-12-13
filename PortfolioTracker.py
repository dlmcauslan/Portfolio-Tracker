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
Modified 2/12/2016:
    * Modified plotPortfolio method so that it uses an outer join and fills in missing
    data by forward filling.
    * Created new table to hold dividend data. Implemented dividend methods in 
    Stock class. Updated print methods to include dividend data.
Modified 6/12/2016:
    * plotPortfolio now includes dividend data.
    * created ValueStock class which includes extra data for performing value
    averaging calculations
    * created getCurrentPercentage() method, which must be run after creating
    the portfolio and adding the stocks to get each stocks current value
    * created printValues() method which prints the stock list, desired weighting,
    and current weighting.
Modified 7/12/2016:
    * Now check in getCurrentPercentage() method that the desired portfolio weightings
    sum to 100%.
    * Added valuePath() which calculates how much of each stock you should purchase
    based on how much you want to increase the portfolio value by, whether selling is 
    allowed or not and what the minimum transaction is to keep the portfolio weightings
    to the desired allocation.
    

To Do:
    * Test adding stock, but no buys, what errors this gives.
    * Check freezing on print methods when there is no data in HISTORICAL_TABLE
    * Add missing buy and dividend data.
"""

from Stock import Stock
from ValueStock import ValueStock
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
        self.stockDatabase.createTable(SC.DIVIDEND_TABLE_NAME, SC.DIVIDEND_COLUMN_LIST)

        
    # Class string method
    def __str__(self):
        returnString = ""
        for stock in self.stockList:
            returnString += str(stock) + "\n"
        returnString += "Total cost of portfolio is ${:.2f}.\nTotal shares value is ${:.2f}.\
        \nTotal value of dividends earned is ${:.2f}.\nTotal value of shares + dividends is ${:.2f}." \
        .format(self.getCost(DEFAULT_DATE), self.getValue(DEFAULT_DATE), self.getDividends(DEFAULT_DATE), self.getValue(DEFAULT_DATE) + self.getDividends(DEFAULT_DATE))
        return returnString

    
    # Add a new stock with code "stockCode" to the portfolio
    def addStock(self, stockCode, percentage):
        newStock = ValueStock(stockCode, percentage, self.stockDatabase)
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
        
        
    # Calculate the total amount of dividend payments the portfolio has recieved
    # up to a particular date
    def getDividends(self, date = DEFAULT_DATE):
        totalDividend = 0
        for stock in self.stockList:
            totalDividend += stock.totalDividend
        return totalDividend
     
    
    # For each ValueStock in the portfolio calculate its current percentage of the
    # total value and set it to the currentPercentage value in the ValueStock.
    def getCurrentPercentages(self):
        date = DEFAULT_DATE
        result = False
        while not result:
            try:
                totalDesired = 0
                portfolioValue = self.getValue(date)
                for valueStock in self.stockList:
                    stockValue = valueStock.getValue(date)
                    valueStock.currentPercentage = 100*stockValue/portfolioValue
                    totalDesired += valueStock.setPercentage
                result = True
            except:
                # decrement date by one day
                date = decrementDate(date)
                
        # Make sure the desired portfolio percentages add to 0
        if totalDesired != 100:
            raise ValueError("Desired portfolio weightings do not sum to 100%. Current sum = {}%.".format(totalDesired))
            
    
    # Calculate the value path
    # params
    # portfolioIncrease - the value that you wish the portfolio to increase by
    # sellingAllowed - boolean - whether selling is allowed.
    # minimumTransaction - the minimum amount of money that you are willing to 
    #   buy or sell per transaction. Usually want to limit this to avoid excess
    #   transaction fees.
    def valuePath(self, portfolioIncrease, sellingAllowed, minimumTransaction):
        date = DEFAULT_DATE
        result = False
        while not result:
            try:
                currentTotalValue = self.getValue(date)
                desiredTotalValue = currentTotalValue + portfolioIncrease
                totalSpent = 0
                for stock in self.stockList:
                    currentStockValue = stock.getValue(date)
                    desiredStockValue = stock.setPercentage / 100 * desiredTotalValue
                    if desiredStockValue - currentStockValue > minimumTransaction:
                        stock.desiredBuy = round((desiredStockValue - currentStockValue)/stock.getPrice(date))
                    elif sellingAllowed and desiredStockValue - currentStockValue < -minimumTransaction:
                        stock.desiredBuy = round((desiredStockValue - currentStockValue)/stock.getPrice(date))
                    else:
                        stock.desiredBuy = 0
                    totalSpent += stock.desiredBuy * stock.getPrice(date)
                result = True
            except:
                # decrement date by one day
                date = decrementDate(date)
        
        # Print out value path  
        print("\n")
        self.printValues()
        print("\n")
        code = []
        numBuy = []
        price = []
        costArray = []
        desiredAllocation = []
        finalAllocation = []
        
        for stock in self.stockList:
            cost = stock.getPrice(date) * stock.desiredBuy
            finalWeight = 100 * (stock.getValue(date) + cost) / (currentTotalValue + totalSpent)
            numBuy.append(int(stock.desiredBuy))
            code.append(stock.stockCode)
            price.append(stock.getPrice(date))
            costArray.append(cost)
            desiredAllocation.append(stock.setPercentage)
            finalAllocation.append("{:.1f}".format(finalWeight))
        
        valueData = pd.DataFrame({"Stock Code": code,
                                  "To Buy": numBuy,
                                  "Price ($)": price,
                                  "Total Cost ($)": costArray,
                                  "Desired (%)": desiredAllocation,
                                  "Final (%)": finalAllocation
                                  }, columns=['Stock Code', 'To Buy', 'Price ($)', "Total Cost ($)", "Desired (%)", "Final (%)"])
        print(valueData)
        print("Total to spend: ${:.2f}. Total portfolio value after purchase: ${:.2f}.".format(totalSpent, totalSpent + currentTotalValue))
                            
                
    # Print values
    def printValues(self):
        for valueStock in self.stockList:
            print("{} - desired weight: {:.1f}%, current weight: {:.1f}%."
                  .format(valueStock.stockCode, valueStock.setPercentage, valueStock.currentPercentage))
            
            
    # Print a list of stock purchaes in the range dateStart to dateEnd.
    # Setting stockCode to "All" prints all stocks. Otherwise prints list of 
    # purchases for stockCode.    
    def printPurchases(self, stockCode = DEFAULT_STOCKCODE, dateStart = DEFAULT_STARTDATE, dateEnd = DEFAULT_DATE):
        sqlQuery = '''SELECT * FROM {}
            WHERE {} BETWEEN date("{}") and date("{}")'''\
            .format(SC.TABLE_NAME, SC.DATE, dateStart, dateEnd)
        
        if stockCode != DEFAULT_STOCKCODE:
            sqlQuery += ''' AND {} LIKE '{}' '''.format(SC.CODE, stockCode)
        
        sqlQuery += ''' ORDER BY {}, {} '''.format(SC.CODE, SC.DATE)    
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
    
            
    # Plots the total portfolio value, amount spent and profit        
    def plotPortfolio(self, dateStart = DEFAULT_STARTDATE, dateEnd = DEFAULT_DATE):
        plt.close("all")
        # Make an empty dataframe for merging using the date values in the first stock
        # in stockList.
        date = self.stockList[0].getValueRange(dateStart, dateEnd)[SC.HISTORICAL_DATE].tolist()
        spent = pd.DataFrame({SC.HISTORICAL_DATE: date, SC.TOTAL_SPENT: list(np.zeros(len(date)))})
        value = pd.DataFrame({SC.HISTORICAL_DATE: date, "Value": list(np.zeros(len(date)))})
        dividends = pd.DataFrame({SC.HISTORICAL_DATE: date, "DIVIDEND_TOTAL": list(np.zeros(len(date)))})
        
        # Loop over the stocks in stockList merging their data into the total
        # dataFrames (performs outer join).
        for s in self.stockList:
            spent = pd.merge(spent, s.getSpentRange(dateStart, dateEnd), how = "outer", on = SC.HISTORICAL_DATE)
            value = pd.merge(value, s.getValueRange(dateStart, dateEnd), how = "outer", on = SC.HISTORICAL_DATE)
            dividends = pd.merge(dividends, s.getDividendRange(dateStart, dateEnd), how = "outer", on = SC.HISTORICAL_DATE)
        
        # Forward fill missing data, for dates that don't exist in db
        spent = spent.fillna(method = "ffill")
        value = value.fillna(method = "ffill")
        dividends = dividends.fillna(method = "ffill") 
        
        # Create total value column by summing the merged columns (except date)
        spent["Total"] = spent.sum(axis = 1)
        value["Total"] = value.sum(axis = 1)
        dividends["Total"] = dividends.sum(axis = 1)
        
        # Create date column from merged data for plotting
        date = list(map(convertDate, spent[SC.HISTORICAL_DATE]))
        
#         Do plotting
        fig = plt.figure()
        plt.clf()
        
        ax = fig.add_subplot(511)
        plt.title("Portfolio Totals", fontsize = 16)
        ax.plot(date, spent["Total"])
        plt.ylabel("Spent ($)", fontsize = 14)
        
        ax = fig.add_subplot(512)
        ax.plot(date, value["Total"])
        plt.ylabel("Value ($)", fontsize = 14)
        
        ax = fig.add_subplot(513)
        ax.plot(date, dividends["Total"])
        plt.ylabel("Dividends ($)", fontsize = 14)
        
        ax = fig.add_subplot(514)
        plt.plot(date, value["Total"] - spent["Total"])
        plt.plot(date, value["Total"] - spent["Total"] + dividends["Total"])
        plt.legend(["Share Value Profit", "Share Value Profit + Dividend"], loc = "upper left")
        plt.ylabel("Profit ($)", fontsize = 14)
        
        ax = fig.add_subplot(515)
        plt.plot(date, 100*(value["Total"] - spent["Total"])/spent["Total"])
        plt.plot(date, 100*(value["Total"] - spent["Total"] + dividends["Total"])/spent["Total"])
        plt.legend(["Share Value Profit", "Share Value Profit + Dividend"], loc = "upper left")
        plt.ylabel("% Profit ($)", fontsize = 14)
        plt.xlabel("Date", fontsize = 14)
        
        plt.show() 
        


            
# Testing code
try:         
    myPortfolio = Portfolio("myPortfolio")
    vap = myPortfolio.addStock("VAP.AX", 10.0)
    ijr = myPortfolio.addStock("IJR.AX", 25.0)
    veu = myPortfolio.addStock("VEU.AX", 15.0)
    vas = myPortfolio.addStock("VAS.AX", 25.0)
    vgb = myPortfolio.addStock("VGB.AX", 12.5)
    vaf = myPortfolio.addStock("VAF.AX", 12.5)
    myPortfolio.getCurrentPercentages()
    
#    print(myPortfolio)
    
#    vaf.buy(31, 48.22, "2014-04-29")
#    vaf.buy(1, 0, "2015-01-19")
#    vaf.buy(27, 50.39, "2015-04-29")
#    vaf.buy(21, 49.8, "2015-07-29")
#    vaf.buy(1, 0, "2015-10-19")
#    vaf.buy(1, 49.01, "2016-01-19")
#    vaf.buy(1, 49.58, "2016-04-19")
#    vaf.buy(1, 50.02, "2016-07-18")
#    vaf.buy(1, 49.92, "2016-10-19")
#    
#    vgb.buy(32, 46.81, "2014-04-29")
#    vgb.buy(74, 47.51, "2014-10-29")
#    vgb.buy(1, 0, "2015-01-19")
#    vgb.buy(1, 49.74, "2015-20-04")
#    vgb.buy(1, 0, "2015-10-19")
#    vgb.buy(1, 48.57, "2016-01-19")
#    vgb.buy(1, 50.53, "2016-07-18")
#    vgb.buy(1, 50.47, "2016-10-19")
#    
#    vas.buy(44, 70.87, "2014-07-29")
#    vas.buy(14, 70.90, "2014-07-31")
#    vas.buy(14, 68.98, "2014-10-29")
#    vas.buy(1, 0, "2015-01-19")
#    vas.buy(20, 75.22, "2015-02-26")
#    vas.buy(1, 74.66, "2015-04-15")
#    vas.buy(17, 74.46, "2015-04-29")
#    vas.buy(1, 69.25, "2015-07-16")
#    vas.buy(17, 71.54, "2015-07-29")
#    vas.buy(2, 0, "2015-10-19")
#    vas.buy(2, 67.00, "2016-01-19")
#    vas.buy(1, 64.35, "2016-04-19")
#    vas.buy(1, 66.68, "2016-07-18")
#    vas.buy(2, 69.68, "2016-10-19")
#    
#    vap.buy(26, 76.11, "2015-02-26")
#    vap.buy(18, 74.66, "2015-04-29")
#    vap.buy(1, 0, "2015-10-19")
#    vap.buy(1, 74.56, "2016-01-19")
#    vap.buy(1, 84.44, "2016-07-18")
#    
#    ijr.buy(61, 115.22, "2014-04-29")
#    
#    veu.buy(27, 55.25, "2014-05-13")
#    veu.buy(20, 55.26, "2014-05-20")
#    veu.buy(25, 56.08, "2014-07-29")
#    veu.buy(16, 65.60, "2015-07-29")
    
#    vap.remove(1, 0, "2016-04-19")
#    vap.remove(1, 0, "2016-10-18")

#    veu.sell(10, 100, "2016-06-01")
#    veu.buy(20, 100, "2016-06-02")
#    veu.sell(10, 100, "2014-06-01")
#    veu.remove(-10, 52.3, "2014-06-01")
#    veu.remove(20, 59.3, "2016-06-02")
#    veu.remove(-10, 59.3, "2016-06-01")
##    veu.remove(100, 100, "2016-12-01")
    
#    vaf.addDividend(19.10, "2014-07-16")
#    vaf.addDividend(14.61, "2014-10-17")
#    vaf.addDividend(16.85, "2015-01-19")
#    vaf.addDividend(13.97, "2015-04-20")
#    vaf.addDividend(28.10, "2015-07-16")
#    vaf.addDividend(42.88, "2015-10-19")
#    vaf.addDividend(40.18, "2016-01-19")
#    vaf.addDividend(35.02, "2016-04-19")
#    vaf.addDividend(78.50, "2016-07-18")
#    vaf.addDividend(35.35, "2016-10-19")
#    
#    vap.addDividend(14.63, "2015-04-20")
#    vap.addDividend(56.19, "2015-07-16")
#    vap.addDividend(25.04, "2015-10-19")
#    vap.addDividend(53.65, "2016-01-19")
#    vap.addDividend(27.02, "2016-04-19")
#    vap.addDividend(68.13, "2016-07-18")
#    vap.addDividend(27.07, "2016-10-19")
#    
#    vas.addDividend(56.65, "2014-10-17")
#    vas.addDividend(54.51, "2015-01-19")
#    vas.addDividend(62.95, "2015-04-20")
#    vas.addDividend(61.32, "2015-07-16")
#    vas.addDividend(121.75, "2015-10-19")
#    vas.addDividend(142.11, "2016-01-19")
#    vas.addDividend(112.61, "2016-04-19")
#    vas.addDividend(24.22, "2016-07-18")
#    vas.addDividend(137.72, "2016-10-19")
#    
#    veu.addDividend(25.88, "2014-07-17")
#    veu.addDividend(18.82, "2014-10-17")
#    veu.addDividend(28.34, "2015-01-19")
#    veu.addDividend(12.80, "2015-04-29")
#    veu.addDividend(45.71, "2015-07-28")
#    veu.addDividend(23.55, "2015-10-28")
#    veu.addDividend(36.34, "2016-01-25")
#    veu.addDividend(14.52, "2016-04-18")
#    veu.addDividend(52.75, "2016-07-14")
#    veu.addDividend(25.05, "2016-10-13")
#    
#    vgb.addDividend(24.42, "2014-07-16")
#    vgb.addDividend(11.40, "2014-10-17")
#    vgb.addDividend(35.16, "2015-01-19")
#    vgb.addDividend(33.83, "2015-04-20")
#    vgb.addDividend(36.84, "2015-07-16")
#    vgb.addDividend(31.40, "2015-10-19")
#    vgb.addDividend(34.17, "2016-01-19")
#    vgb.addDividend(35.35, "2016-04-19")
#    vgb.addDividend(34.87, "2016-07-18")
#    vgb.addDividend(32.41, "2016-10-19")
#    
#    ijr.addDividend(17.49, "2014-07-16")
#    ijr.addDividend(18.60, "2014-10-17")
#    ijr.addDividend(28.78, "2015-01-28")
#    ijr.addDividend(28.12, "2015-04-27")
#    ijr.addDividend(24.96, "2015-07-23")
#    ijr.addDividend(25.45, "2015-10-27")
#    ijr.addDividend(37.23, "2016-01-28")
#    ijr.addDividend(27.93, "2016-04-27")
#    ijr.addDividend(0, "2016-07-14")
#    ijr.addDividend(0, "2016-10-13")
    
#    vgb.addDividend(100)
#    vgb.removeDividend(100, "2016-12-05")
    
    
    myPortfolio.printPurchases()
#    myPortfolio.printPurchases("VEU.AX", "2014-01-01", "2015-01-01")
#    myPortfolio.printPurchases("VAF.AX")
    print(myPortfolio)
#    myPortfolio.printValues()
    myPortfolio.valuePath(3000, False, 500)
    

    
#    print(veu.getOwned())
#    print(veu.getPrice("2016-11-28"))
#    print("VEU ${:.2f} ${:.2f}".format(veu.getValue("2016-11-29"), veu.totalCost))
#    print("IJR ${:.2f} ${:.2f}".format(ijr.getValue("2016-11-29"), ijr.totalCost))
#    print("VAP ${:.2f} ${:.2f}".format(vap.getValue("2016-11-29"), vap.totalCost))
#    print(vap.getPriceRange("2015-02-26", "2016-01-19"))
#    print(veu.getOwnedRange("2016-05-26"))
#    print(vas.getValueRange("2014-05-12"))
#    print(vas.getPriceRange("2014-05-12"))
#    print(vas.getDividendRange("2014-01-01"))
#    veu.plot("2014-03-01")

#    myPortfolio.plot([vas, ijr, vap], "2014-01-01")
#    myPortfolio.plotPortfolio("2014-01-01")
    
#    sqlQuery = '''SELECT * FROM {} 
#    WHERE Stock_Code LIKE 'VGB.AX' 
#    AND Date BETWEEN date("2014-01-01") AND date("2016-12-02")'''.format(SC.HISTORICAL_TABLE_NAME)
#    print(myPortfolio.stockDatabase.readDatabase(sqlQuery))
    

# The line below is just so we don't readd the data every time.
finally:
    print("\n")
#    myPortfolio.stockDatabase.removeTable(SC.TABLE_NAME)
#    myPortfolio.stockDatabase.clearTable(SC.DIVIDEND_TABLE_NAME)
#    myPortfolio.stockDatabase.clearTable(SC.TABLE_NAME)


