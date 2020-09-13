# Tristan Howell
# Performs DB operations for isItUp.py
# This is certainly vulnerable to SQL injection as is, either regex to validate user in or strip of characters here

import sqlite3


def initialize_table():
    conn = sqlite3.connect('test.db')
    print("Opened database successfully")

    conn.execute('''CREATE TABLE DOMAINSTATS
             (DOMAIN CHAR(50) PRIMARY KEY     NOT NULL,
             PORT           INT    NOT NULL,
             STATUS CHAR(50) NOT NULL);''')

    print("Table created successfully")


def read_table():
    conn = sqlite3.connect('test.db')
    print("Opened database successfully")

    cursor = conn.execute("SELECT domain, port, status from DOMAINSTATS")
    for row in cursor:
       print("DOMAIN = ", row[0])
       print("PORT = ", row[1])
       print("STATUS = ", row[2], "\n")

    print("Print Completed")
    conn.close()


def write_table(domain, port, status):
    conn = sqlite3.connect('test.db')
    print("Opened database successfully")

    conn.execute("INSERT INTO DOMAINSTATS (DOMAIN,PORT,STATUS) \
          VALUES (domain, port, status )")

    conn.commit()
    print("Records created successfully")
    conn.close()
