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

Modified 29/11/2016:
    * implemented getOwned() method.
    * Stock class now takes as an input the database to save the data in.
    * created stockDownloader.py to help with downloading stock data.
    * stockDownloader stockScrape method works so far. The other methods 
    (in particular stockUpdate) need to be tested.
Modified 30/11/2016:
    * Class now downloads all past stock price data on initialization. Or
    alternatively, if the stock has been added to the database previously, it
    updates the database with the most recent data.
    * Implemented getPrice() and getValue() methods to get the price of the stock
    on a particular date, and the total value of the stock on a particular date.
    * Implemented getPriceRange() method which gets the price of the stock over a
    range of dates.
    * Implemented getValueRange() method which gets a data frame containing Date,
    Total_Owned and Total_Value for a range of dates.
Modified 01/12/2016:
    * Implemented sell() method for selling some of the stock.
    * Implemented remove() method for removing a transaction from the database
    (incase you made an error when adding it)
    * Fixed getValueRange() method so that it works with selling.
    * Removed TOTAL_OWNED column from database as it calculates incorrectly
    when purchases are not added in date order. TOTAL owned column can easily be
    generated in SQL using SUM(NUMBER_PURCHASED) AS TOTAL_OWNED.
    * Split getValueRange() method into getOwnedRange() and getValueRange() methods.
    * Implemented plot method which plots date vs total value, number owned, stock price and profit.
    * Implemented getSpentRange() method which calculates the amount spent over a
    range of dates.
    * Modified contstructor so that it gets the total number of shares owned and
    total amount spent from the data base on initializaiton.
        
    
"""
import datetime
import pandas as pd
import stockContract as SC
import stockDownloader as downloader
import seaborn as sns
import matplotlib.pyplot as plt

###############
## Constants ##
###############
DEFAULT_DATE = str(datetime.date.today())
DEFAULT_STARTDATE = "1900-01-01"

####################
## Helper Methods ##
####################
# Converts a date in "yyyy-mm-dd" format to a dateTime object
def convertDate(date):
    [year, month, day] = map(int, date.split("-"))
    return datetime.date(year, month, day)


# Class for holding the information of an individual stock.
# Parameters:   numberOwned
#               totalCost
#               stockCode
#               dataBase
class Stock:
    numberOwned = 0
    totalCost = 0
      
    # Class initializer
    def __init__(self, stockCode, database):
      self.stockCode = stockCode
      self.database = database
      # Updates the database with any price data that it does not have.
      downloader.updateStockData(self.stockCode, self.database)
      # Updates the numberOwned and totalCost values
      numOwned = self.getOwned()
      if numOwned != None:
          self.numberOwned = numOwned
      amountSpent = self.getSpent()
      if amountSpent != None:
          self.totalCost = amountSpent
    
      
    # Class string method
    def __str__(self):
         return "{} - number owned: {}, total cost: ${:.2f}".format(self.stockCode, self.numberOwned, self.totalCost)

    
    # Buy a number of stocks at a price and save in the database     
    def buy(self, numberBought, price, date = DEFAULT_DATE):
        self.numberOwned += numberBought
        self.totalCost += numberBought*price
        purchaseData = pd.DataFrame({SC.CODE: [self.stockCode],
                                     SC.DATE: [date],
                                     SC.NUMBER_PURCHASED: [numberBought],
                                     SC.PRICE: [price],
                                     SC.COST: [price*numberBought]})
        self.database.addToDatabase(purchaseData, SC.TABLE_NAME)
    
    # Sell a number of stocks at a price and save in the database     
    def sell(self, numberSold, price, date = DEFAULT_DATE):
        self.numberOwned -= numberSold
        if self.numberOwned < 0:
            self.numberOwned += numberSold      # Not sure if this is necessary
            raise ValueError("Can't sell more shares than you own.")
        self.totalCost -= numberSold*price
        purchaseData = pd.DataFrame({SC.CODE: [self.stockCode],
                                     SC.DATE: [date],
                                     SC.NUMBER_PURCHASED: [-numberSold],
                                     SC.PRICE: [price],
                                     SC.COST: [-price*numberSold]})
        self.database.addToDatabase(purchaseData, SC.TABLE_NAME)
    
        
    # Update a data input, incase of input error. 
    # numberBought is a negative number if its a sale we wish to reverse
    def remove(self, numberBought, price, date):
        self.numberOwned -= numberBought
        self.totalCost -= numberBought*price
        sqlCommand = '''DELETE FROM {} 
            WHERE {} LIKE '{}'
            AND {} == {}
            AND {} == {}
            AND {} == date("{}")''' \
            .format(SC.TABLE_NAME, 
                    SC.CODE, self.stockCode,
                    SC.NUMBER_PURCHASED, numberBought,
                    SC.PRICE, price,
                    SC.DATE, date)
        rowsRemoved = self.database.executeCommand(sqlCommand)
        if rowsRemoved == 0:
            self.numberOwned += numberBought
            self.totalCost += numberBought*price
            raise ValueError("Purchase of {} shares for ${} on {} was not in database".format(numberBought, price, date))
        
        
    # Get the number of the stock owned at date. Default date is today.
    def getOwned(self, date = DEFAULT_DATE):
        sqlQuery = '''SELECT SUM({}) AS {} FROM {} 
            WHERE {} LIKE '{}' 
            AND {} <= date("{}")''' \
            .format(SC.NUMBER_PURCHASED, SC.TOTAL_OWNED, SC.TABLE_NAME, 
                    SC.CODE, self.stockCode, 
                    SC.DATE, date)
        data = self.database.readDatabase(sqlQuery)
        if data.empty:
            raise ValueError(('No data for dates up to {}.'.format(date)))
        return data.get_value(0, SC.TOTAL_OWNED)
        
    
    # Get the number of the stock owned at date. Default date is today.
    def getSpent(self, date = DEFAULT_DATE):
        sqlQuery = '''SELECT SUM({}) AS {} FROM {} 
            WHERE {} LIKE '{}' 
            AND {} <= date("{}")''' \
            .format(SC.COST, SC.TOTAL_SPENT, SC.TABLE_NAME, 
                    SC.CODE, self.stockCode, 
                    SC.DATE, date)
        data = self.database.readDatabase(sqlQuery)
        if data.empty:
            raise ValueError(('No data for dates up to {}.'.format(date)))
        return data.get_value(0, SC.TOTAL_SPENT)
    
    
    # Get the price of the stock at date. Default date is today.
    def getPrice(self, date = DEFAULT_DATE):
        sqlQuery = ''' SELECT {} FROM {}
            WHERE {} LIKE '{}'
            AND {} LIKE '{}' ''' \
            .format(SC.HISTORICAL_PRICE, SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_CODE, self.stockCode, SC.HISTORICAL_DATE, date)
        data = self.database.readDatabase(sqlQuery)
        # If data is empty raise ValueError
        if data.empty:
            raise ValueError(('No price data for {}.'.format(date)))
        return data.get_value(0, SC.HISTORICAL_PRICE)

        
    # get the total value of the stock at date. Default date is today.
    def getValue(self, date = DEFAULT_DATE):
        return self.getOwned(date) * self.getPrice(date)
        
    
    # Get a data fram containing the price of the stock over a range of dates    
    def getPriceRange(self, startDate = DEFAULT_STARTDATE, endDate = DEFAULT_DATE):
        sqlQuery = ''' SELECT {}, {} FROM {}
            WHERE {} LIKE '{}'
            AND {} BETWEEN date("{}") AND date("{}") 
            ORDER BY {} ASC''' \
            .format(SC.HISTORICAL_DATE, SC.HISTORICAL_PRICE, SC.HISTORICAL_TABLE_NAME, 
                    SC.HISTORICAL_CODE, self.stockCode, 
                    SC.HISTORICAL_DATE, startDate, endDate,
                    SC.HISTORICAL_DATE)
        data = self.database.readDatabase(sqlQuery)
        # If data is empty raise ValueError
        if data.empty:
            raise ValueError(('No price data in the range {} - {}.'.format(startDate, endDate)))
        return data
        
    
    # Gets a dataframe containing the number of shares owned over a range of dates    
    def getOwnedRange(self, startDate = DEFAULT_STARTDATE, endDate = DEFAULT_DATE):
        # Perform a left outer join to get the total number of stocks owned at each
        # date in the historical data table.
        sqlQuery = ''' SELECT {}.{}, SUM({}.{}) AS {}, MAX({}.{}) AS {} FROM {}   
            LEFT OUTER JOIN {} ON {}.{} >= {}.{}
            AND {}.{} == {}.{}
            WHERE {}.{} LIKE '{}' 
            AND {} BETWEEN date("{}") AND date("{}")
            GROUP BY {} ORDER BY {} ASC''' \
            .format(SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_DATE, 
                    SC.TABLE_NAME, SC.NUMBER_PURCHASED, SC.TOTAL_OWNED, 
                    SC.TABLE_NAME, SC.DATE, SC.DATE,
                    SC.HISTORICAL_TABLE_NAME, 
                    SC.TABLE_NAME, SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_DATE, SC.TABLE_NAME, SC.DATE,
                    SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_CODE, SC.TABLE_NAME, SC.CODE,
                    SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_CODE, self.stockCode,
                    SC.HISTORICAL_DATE, startDate, endDate,
                    SC.HISTORICAL_DATE, SC.HISTORICAL_DATE)

        data = self.database.readDatabase(sqlQuery)
        # Remove the unwanted Purchase_Date column
        data = data.drop(SC.DATE, 1)
        # For any dates before the first purchase, set the number owned to 0.
        data = data.fillna(0)
        return data
        
        
   # Gets a dataframe containing the total spend on the shares owned over a range of dates    
    def getSpentRange(self, startDate = DEFAULT_STARTDATE, endDate = DEFAULT_DATE):
        # Perform a left outer join to get the total number of stocks owned at each
        # date in the historical data table.
        sqlQuery = ''' SELECT {}.{}, SUM({}.{}) AS {}, MAX({}.{}) AS {} FROM {}   
            LEFT OUTER JOIN {} ON {}.{} >= {}.{}
            AND {}.{} == {}.{}
            WHERE {}.{} LIKE '{}' 
            AND {} BETWEEN date("{}") AND date("{}")
            GROUP BY {} ORDER BY {} ASC''' \
            .format(SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_DATE, 
                    SC.TABLE_NAME, SC.COST, SC.TOTAL_SPENT, 
                    SC.TABLE_NAME, SC.DATE, SC.DATE,
                    SC.HISTORICAL_TABLE_NAME, 
                    SC.TABLE_NAME, SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_DATE, SC.TABLE_NAME, SC.DATE,
                    SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_CODE, SC.TABLE_NAME, SC.CODE,
                    SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_CODE, self.stockCode,
                    SC.HISTORICAL_DATE, startDate, endDate,
                    SC.HISTORICAL_DATE, SC.HISTORICAL_DATE)

        data = self.database.readDatabase(sqlQuery)
        # Remove the unwanted Purchase_Date column
        data = data.drop(SC.DATE, 1)
        # For any dates before the first purchase, set the number owned to 0.
        data = data.fillna(0)
        return data
        
        
    # Get a dataframe containing the total value of the stock over a range of dates
    def getValueRange(self, startDate = DEFAULT_STARTDATE, endDate = DEFAULT_DATE):
        data = pd.merge(self.getPriceRange(startDate, endDate), self.getOwnedRange(startDate, endDate), on=SC.HISTORICAL_DATE)
        # Add a column for the total value of the stock
        data['Total_Value'] = data[SC.HISTORICAL_PRICE] * data[SC.TOTAL_OWNED]
        # For any dates before the first purchase, set the total value to 0.
        data = data.fillna(0)
        # Remove the price and number owned columns
        data = data.drop([SC.HISTORICAL_PRICE, SC.TOTAL_OWNED], 1)
        return data
        

    # Plot stock data in a range of dates
    def plot(self, startDate = DEFAULT_STARTDATE, endDate = DEFAULT_DATE):
        # Format data to be plotted
        date = self.getValueRange(startDate, endDate)[SC.HISTORICAL_DATE].tolist()
        date = list(map(convertDate, date))
        value = self.getValueRange(startDate, endDate)["Total_Value"]
        owned = self.getOwnedRange(startDate, endDate)[SC.TOTAL_OWNED]
        price = self.getPriceRange(startDate, endDate)[SC.HISTORICAL_PRICE]
        spent = self.getSpentRange(startDate, endDate)[SC.TOTAL_SPENT]


        # Do plotting
        fig = plt.figure()
        plt.clf()    
        ax = fig.add_subplot(411)
        plt.title(self.stockCode, fontsize = 16)
        ax.plot(date, value)
        plt.ylabel("Value of shares ($)", fontsize = 14)
        ax = fig.add_subplot(412)
        ax.plot(date, owned)
        plt.ylabel("Number of shares owned", fontsize = 14)
        ax = fig.add_subplot(413)
        plt.plot(date, price)
        plt.ylabel("Stock price ($)", fontsize = 14)
        ax = fig.add_subplot(414)
        plt.plot(date, value - spent)
        plt.ylabel("Profit ($)", fontsize = 14)
        plt.xlabel("Date", fontsize = 14)
#        plt.tight_layout()    
        plt.show() 

        
        
