#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""                PortfolioTracker.py
Created on Fri Nov 25 11:23:16 2016

@author: dmcauslan
"""
#import Stock as s
from Stock import Stock
import datetime

# Testing code        
vas = Stock("VAS.AX")
print(vas)
vas.buy(10, 32.30, datetime.date(2016, 12, 19))
print(vas)
vas.buy(36, 12.26, datetime.date(2016, 12, 19))
print(vas)

ijr = Stock("IJR.AX")
print(ijr)
ijr.buy(10, 50, datetime.date(2016, 12, 19))
ijr.buy(23, 12.86)
print(ijr)
print(vas)