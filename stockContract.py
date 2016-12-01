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

# Database Columns
CODE = "Stock_Code"
DATE = "Purchase_Date"
NUMBER_PURCHASED = "Number_Purchased"
TOTAL_OWNED = "Total_Owned"
PRICE = "Price"
COST = "Total_Cost"
COLUMNS = [CODE, DATE, NUMBER_PURCHASED, TOTAL_OWNED, PRICE, COST]

COLUMN_LIST = "{} TEXT, {} TEXT, {} INT, {} INT, {} REAL, {} REAL".format(CODE, DATE, NUMBER_PURCHASED, TOTAL_OWNED, PRICE, COST)


## Historical stock data table contract
# Table Name
HISTORICAL_TABLE_NAME = "historicalStockData"

# Database Columns
HISTORICAL_DATE = "Date"
HISTORICAL_PRICE = "Price"
HISTORICAL_CODE = "Stock_Code"
HISTORICAL_COLUMNS = [HISTORICAL_CODE, HISTORICAL_DATE, HISTORICAL_PRICE]

HISTORICAL_COLUMN_LIST = "{} TEXT, {} TEXT, {} REAL".format(HISTORICAL_CODE, HISTORICAL_DATE, HISTORICAL_PRICE)
