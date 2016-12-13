#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""                  stockDownloader.py       
Created on Tue Nov 29 11:28:12 2016

@author: hplustech
"""
import stockContract as SC
from bs4 import BeautifulSoup
# Below is the change from urllib2 in python 2.7
from urllib.request import urlopen
import pandas as pd
import re
import datetime


# Takes a date string in the format "yyyy-mm-dd" and returns the year, month, day
# in a format that the yahoo finance URL can use
def convertToURLDate(date):
    [year, month, day] = date.split("-")
    
    if int(month) < 11:
        month = '0' + str(int(month)-1)
    else:
        month = str(int(month)-1)
        
    return year, month, day
    
    
# cleans dataframe data        
def dataClean(inptFrame):
    inptFrame[SC.HISTORICAL_DATE] = convertDate(inptFrame[SC.HISTORICAL_DATE].tolist())   
    return inptFrame
    
    
#takes a date input as a list of strings in the format 'mmm d, yyyy' and converts it to
#yyyy-mm-dd
def convertDate(dateString):
    # a dictionary to convert months to a number
    monthDict = {'Jan': '01', 'Feb':'02', 'Mar':'03','Apr':'04','May':'05','Jun':'06',
    'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
    
    for n in range(len(dateString)):
        #splits the string
        splitDate = re.split('\W+',dateString[n])
        # cconverts the date into date object
        dateString[n] = datetime.date(int(splitDate[2]),int(monthDict[splitDate[1]]),int(splitDate[0])).isoformat() #y,m,d
    return dateString


# Takes in a date in the format "yyyy-mm-dd" and increments it by one day. Or if the 
# day is a Friday, increment by 3 days, so the next day of data we get is the next
# Monday.
def incrementDate(dateString):
    [year, month, day] = dateString.split("-")
    dateTime = datetime.date(int(year), int(month), int(day))
    # If the day of the week is a friday increment by 3 days.
    if dateTime.isoweekday() == 5:
        datePlus = dateTime + datetime.timedelta(3)
    else:
        datePlus = dateTime + datetime.timedelta(1)
    return str(datePlus)
    
    
# Checks whether stock is in database, if not it stockScrape to get all the data.
# If it is in data base it checks whether the stock information is up to date and only fetches new data
def updateStockData(stockCode, database):
    # Reads database
    sqlQuery = """SELECT {} FROM {} WHERE {} = '{}'; """ \
    .format(SC.HISTORICAL_CODE, SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_CODE, stockCode)
    
#    print(sqlQuery)
    stockData = database.readDatabase(sqlQuery)
           
    # Checks whether any previous data has been added for the particular stock code
    # if not then run initialStockScrape to get all past data
    if stockData.empty:
        print('Running stockScrape() on {}. --First run.'.format(stockCode))
        #self.URL = 'http://finance.yahoo.com/q/hp?s='+self.stockName+'&d=02&e=25&f=2016&g=d&a=00&b=01&c=2015&z=66&y=' #Test URL
        stockScrape(stockCode, database)
    else:
        #access database to get latestDate
        print('Running stockScrape() on {}. --Updating data.'.format(stockCode))
        # Performs SQL query to get the latest stock data date in database
        sqlQuery = """SELECT {}, max({}) AS Date FROM {} WHERE {} = '{}' GROUP BY {}""" \
        .format(SC.HISTORICAL_CODE, SC.HISTORICAL_DATE, SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_CODE, stockCode, SC.HISTORICAL_CODE)
        
        y = database.readDatabase(sqlQuery)  
        minDate = y.Date[0]    # minDate is the earliest data of data that the program needs to download
        # Increment date by 1 day
        minDate = incrementDate(minDate)
        
        # Updates stock data
        stockScrape(stockCode, database, minDate)                     
    
    
# function which does the first time initialization of the stock and 
#downloads all past stock data, returns array of dates, and array of data
def stockScrape(stockCode, database, minDate = '1900-01-01'):
    # Initialize pandas dataframe to hold stock data    
    stockDataFrame =  pd.DataFrame({SC.HISTORICAL_CODE: [], SC.HISTORICAL_DATE: [], SC.HISTORICAL_PRICE: []});
    # Base URL to download data
    endYear, endMonth, endDay = convertToURLDate(str(datetime.date.today()))
    startYear, startMonth, startDay = convertToURLDate(minDate)
    
    baseURL = "https://au.finance.yahoo.com/q/hp?s={}&a={}&b={}&c={}&d={}&e={}&f={}&g=d&z=66&y=" \
    .format(stockCode, startMonth, startDay, startYear, endMonth, endDay, endYear)
#    print(baseURL)
    
    # Putting into a loop to download all pages of data
    done = False
    pageIndex = 0
    
    # This loops over the different pages of data. Each page stores at most 66
    # rows in the table.
    while not done:
        print(pageIndex)
        URLPage = baseURL + str(pageIndex)        
        #creates soup and dowloads data
        soup = BeautifulSoup(urlopen(URLPage).read(),"lxml")
        table = soup.find('table','yfnc_datamodoutline1')
        #breaks loop if it doesnt find a table
        if table == None:
            done = True
            break                

        # Loop over rows in table, adding date and price data to stockDataFrame
        for row in table.tr.td.find_all("tr"):
            columns = row.find_all("td")
            # This checks if its a data column
            if len(columns) == 7:
                rowDate = columns[0].string
                rowPrice = columns[4].string
                rowTemp = [stockCode, rowDate, rowPrice]
                stockDataFrame = stockDataFrame.append(pd.DataFrame([rowTemp], columns = SC.HISTORICAL_COLUMNS), ignore_index=True)
        
        #increment pageIndex
        pageIndex += 66
           
    # Cleans the numerical data before saving
    dataClean(stockDataFrame)
    
    # Add to SQL database
    database.addToDatabase(stockDataFrame, SC.HISTORICAL_TABLE_NAME)
    
    
    
## Testing code
#testPath = '/Users/hplustech/Documents/Canopy/Portfolio Tracker/Databases/test.db'
#testDB = Database(testPath)
##testDB.createTable(SC.HISTORICAL_TABLE_NAME, SC.HISTORICAL_COLUMN_LIST)
#updateStockData("VAP.AX", testDB)
##stockScrape("IJR.AX", testDB, "1990-11-10")
#print(testDB.readDatabase('''SELECT * FROM {}'''.format(SC.HISTORICAL_TABLE_NAME)))