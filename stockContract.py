#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""                 stockContract
Created on Tue Nov 29 09:34:52 2016

@author: dmcauslan

Holds constants for the stock database
"""
## Stock purchase data table contract
# Table Name
TABLE_NAME = "stockPurchases"

# Table Columns
CODE = "Stock_Code"
DATE = "Purchase_Date"
NUMBER_PURCHASED = "Number_Purchased"
TOTAL_OWNED = "Total_Owned"
PRICE = "Price_$"
COST = "Total_Cost_$"
TOTAL_SPENT = "Total_Spent_$"
COLUMNS = [CODE, DATE, NUMBER_PURCHASED, PRICE, COST]

COLUMN_LIST = "{} TEXT, {} TEXT, {} INT, {} REAL, {} REAL".format(CODE, DATE, NUMBER_PURCHASED, PRICE, COST)


## Historical stock data table contract
# Table Name
HISTORICAL_TABLE_NAME = "historicalStockData"

# Table Columns
HISTORICAL_DATE = "Date"
HISTORICAL_PRICE = "Price_$"
HISTORICAL_CODE = "Stock_Code"
HISTORICAL_COLUMNS = [HISTORICAL_CODE, HISTORICAL_DATE, HISTORICAL_PRICE]

HISTORICAL_COLUMN_LIST = "{} TEXT, {} TEXT, {} REAL".format(HISTORICAL_CODE, HISTORICAL_DATE, HISTORICAL_PRICE)


## Dividends data table contract
# Table Name
DIVIDEND_TABLE_NAME = "dividends"

# Table Columns
DIVIDEND_DATE = "Dividend_Date"
DIVIDEND_CODE = "Stock_Code"
DIVIDEND_AMOUNT = "Amount_$"
DIVIDEND_TOTAL = "Total_Dividend_$"
DIVIDEND_COLUMNS = [DIVIDEND_CODE, DIVIDEND_DATE, DIVIDEND_AMOUNT]

DIVIDEND_COLUMN_LIST = "{} TEXT, {} TEXT, {} REAL".format(DIVIDEND_CODE, DIVIDEND_DATE, DIVIDEND_AMOUNT)