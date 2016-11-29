'''                   databaseFunctions.py
Created: 28/11/2016
    Python script that holds the functions for creating, reading and loading from 
    sqlite databases.
'''

import sqlite3
import pandas as pd

class Database():
    
    def __init__(self, databasePath):
      self.databasePath = databasePath
         
    #createTable()
    def createTable(self, tableName, rowList):
        # function which creates the table (tableName) in the database db
        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()        
        #Created database
        sql_command = """ CREATE TABLE {} ({}) """.format(tableName, rowList)
        print(sql_command)    
        cursor.execute(sql_command)
        conn.commit()
        conn.close()
        print("Database created") 
    
    # readDatabase(connect, sqlQuery)
    def clearTable(self, tableName, rows):
        # Deletes all rows from the table specified in connect
        rowDict = dict.fromkeys(rows, [])
        emptyDF = pd.DataFrame(rowDict)
        conn = sqlite3.connect(self.databasePath)
        emptyDF.to_sql(name = tableName, con = conn, if_exists = 'replace', index = False)       
        conn.commit()
        conn.close()

        
    #removeTable()
    def removeTable(self, tableName):
        # function which removes the table (tableName) from the database db
        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()        
        #Remove database
        sql_command = """ DROP TABLE IF EXISTS {} """.format(tableName) 
        cursor.execute(sql_command)
        conn.commit()
        conn.close()
        print("Database removed")
        
            
    # addToDatabase()
    def addToDatabase(self, dataFrame, tableName):
        # function which adds scraped data to database db
        conn = sqlite3.connect(self.databasePath)
        dataFrame.to_sql(name = tableName, con = conn, if_exists = 'append', index = False)       
        conn.commit()
        conn.close()
    
            
    # readDatabase(connect, sqlQuery)
    def readDatabase(self, sqlQuery):
        # Uses the query sqlQuery to read the database specified in connect
        conn = sqlite3.connect(self.databasePath)               
        dataFrame = pd.read_sql(sqlQuery, conn)
        conn.close()
        return dataFrame
    
