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
    updates the database with the most recent data.
    * Implemented getPrice() and getValue() methods to get the price of the stock
    on a particular date, and the total value of the stock on a particular date.
    * Implemented getPriceRange() method which gets the price of the stock over a
    
"""
import datetime
import pandas as pd
import stockContract as SC
import stockDownloader as downloader

###############
## Constants ##
###############
DEFAULT_DATE = str(datetime.date.today())


# Class for holding the information of an individual stock.
# Parameters:   numberOwned
#               totalCost
#               stockCode
class Stock:
    numberOwned = 0
    totalCost = 0
      
    # Class initializer
    def __init__(self, stockCode, database):
      self.stockCode = stockCode
      self.database = database
      # Updates the database with any price data that it does not have.
      downloader.updateStockData(self.stockCode, self.database)
    
      
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
                                     SC.TOTAL_OWNED: [self.getOwned(date) + numberBought],
                                     SC.PRICE: [price],
                                     SC.COST: [price*numberBought]})
        self.database.addToDatabase(purchaseData, SC.TABLE_NAME)
    
        
    # Get the number of the stock owned at date. Default date is today.
    def getOwned(self, date = DEFAULT_DATE):
        sqlQuery = '''SELECT {} FROM {} 
            WHERE {} LIKE '{}' 
            AND {} <= date("{}")'''.format(SC.NUMBER_PURCHASED, SC.TABLE_NAME, SC.CODE, self.stockCode, SC.DATE, date)
        queryDataFrame = self.database.readDatabase(sqlQuery)
        return sum(queryDataFrame[SC.NUMBER_PURCHASED])

    
    
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
        
    
    # Get the price of the stock over a range of dates    
    def getPriceRange(self, startDate = "1900-01-01", endDate = DEFAULT_DATE):
        sqlQuery = ''' SELECT {}, {} FROM {}
            WHERE {} LIKE '{}'
            AND {} BETWEEN date("{}") AND date("{}") ''' \
            .format(SC.HISTORICAL_DATE, SC.HISTORICAL_PRICE, SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_CODE, self.stockCode, SC.HISTORICAL_DATE, startDate, endDate)
        data = self.database.readDatabase(sqlQuery)
        # If data is empty raise ValueError
        if data.empty:
            raise ValueError(('No price data in the range {} - {}.'.format(startDate, endDate)))
        return data
        
    
    # Get the total value of the stock over a range of dates
    def getValueRange(self, startDate = "1900-01-01", endDate = DEFAULT_DATE):
        # Perform a left outer join to get the total number of stocks owned at each
        # date in the historical data table.
        sqlQuery = ''' SELECT {}.{}, {}.{}, MAX({}.{}) AS {} FROM {}   
            LEFT OUTER JOIN {} ON {}.{} >= {}.{}
            AND {}.{} == {}.{}
            WHERE {}.{} LIKE '{}' 
            AND {} BETWEEN date("{}") AND date("{}")
            GROUP BY {}''' \
            .format(SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_DATE, SC.HISTORICAL_TABLE_NAME, 
                    SC.HISTORICAL_PRICE, SC.TABLE_NAME, SC.TOTAL_OWNED, SC.TOTAL_OWNED,
                    SC.HISTORICAL_TABLE_NAME, 
                    SC.TABLE_NAME, SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_DATE, SC.TABLE_NAME, SC.DATE,
                    SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_CODE, SC.TABLE_NAME, SC.CODE,
                    SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_CODE, self.stockCode,
                    SC.HISTORICAL_DATE, startDate, endDate,
                    SC.HISTORICAL_DATE)

        data = self.database.readDatabase(sqlQuery)
        # Add a column for the total value of the stock
        data['Total_Value'] = data[SC.HISTORICAL_PRICE] * data[SC.TOTAL_OWNED]
        # For any dates before the first purchase, set the total owned and
        # total value to 0.
        data = data.fillna(0)
        # Remove the price column
        data = data.drop(SC.HISTORICAL_PRICE, 1)
        return data

        
        
