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
    
"""
import datetime
import pandas as pd
import stockContract as SC
from bs4 import BeautifulSoup
# Below is the change from urllib2 in python 2.7
from urllib.request import urlopen

##########################
##### Helper methods #####
##########################
# Takes a date string in the format "yyyy-mm-dd" and returns the year, month, day
# in a format that yahoo finance can use
def convertToYahooDate(date):
    [year, month, day] = date.split("-")
    
    if int(month) < 11:
        month = '0' + str(int(month)-1)
    else:
        month = str(int(month)-1)
        
    return year, month, day
    



 
# Class for holding the information of an individual stock.
# Parameters:   numberOwned
#               totalCost
#               stockCode
class Stock:
    numberOwned = 0
    totalCost = 0
    DEFAULT_DATE = str(datetime.date.today())
    
    # Class initializer
    def __init__(self, stockCode, database):
      self.stockCode = stockCode
      self.database = database
    
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
    
        
    # Get the number of the stock owned at date. Default date is today.
    def getOwned(self, date = DEFAULT_DATE):
        sqlQuery = '''SELECT * FROM {} 
            WHERE {} LIKE '{}' 
            AND {} <= date("{}")'''.format(SC.TABLE_NAME, SC.CODE, self.stockCode, SC.DATE, date)
        queryDataFrame = self.database.readDatabase(sqlQuery)
        return sum(queryDataFrame[SC.NUMBER_PURCHASED])
    
    
    # Get the price of the stock at date. Default date is today.
    def getPrice(self, date = DEFAULT_DATE):
        year, month, day = convertDate(date)
        URLPage = "https://au.finance.yahoo.com/q/hp?s={}&a={}&b={}&c={}&d={}&e={}&f={}&g=d".format(self.stockCode, month, day, year, month, day, year)
        print(URLPage)
        #creates soup and dowloads data
        soup = BeautifulSoup(urlopen(URLPage).read(),"lxml")
        table = soup.find('table','yfnc_datamodoutline1')             
        #takes data from soup and processes it into a way that can be used 
        for td in table.tr.findAll("td"):
            print(td)
#            if td.string != None:                    
#                #Only get stock data
#                if 'Dividend' not in td.string and '/' not in td.string:
#                    rowTemp.append(td.string)
#                    # Add entire row to dataFrame
#                    if len(rowTemp)%7==0:
#                        # If date is less than the minimum date then stop getting data
#                        if convertDate([rowTemp[0]])[0] <= minDate:
#                            done = True
#                            break                                
#                        stockDataFrame = stockDataFrame.append(pd.DataFrame([rowTemp], columns=colName), ignore_index=True)
#                        #Clear rowTemp
#                        rowTemp = []
    
    
    
    
    # get the total value of the stock at date. Default date is today.
    def getValue(self, date = DEFAULT_DATE):
        return self.getOwned(date) * self.getPrice(date)
        
