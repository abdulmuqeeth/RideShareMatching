#!/usr/bin/env python

from dbconfig import *
import MySQLdb
"""
TODO: Convert units
"""

"""
Connect to Database
"""
def make_connection():
    conn = MySQLdb.connect(host=hostname, user=username, passwd=password, db=database)
    
    return conn
"""
Load data from preprocessed .csv files
"""
def get_data(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM trips LIMIT 20")
    result = cur.fetchall()
    print(result)

"""
Perform distance and delay constraint checks
"""
def check():
    pass

"""
Main function
"""
def main():
    conn = make_connection()
    get_data(conn)

    conn.close()
    pass

if __name__ == "__main__":
    main()
