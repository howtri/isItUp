# Tristan Howell
# Performs DB operations for isItUp.py
# This is certainly vulnerable to SQL injection as is, either regex to validate user in or strip of characters here

import sqlite3


def initialize_table():
    conn = sqlite3.connect('cli-test')
    print("Opened database successfully")

    conn.execute('''CREATE TABLE DOMAINSTATS
             (DOMAIN CHAR(50) PRIMARY KEY     NOT NULL,
             PORT           INT    NOT NULL,
             STATUS CHAR(50) NOT NULL);''')

    print("Table created successfully")


def read_table():
    conn = sqlite3.connect('cli-test')
    print("Opened database successfully")
    cursor = conn.execute("SELECT domain, port, status from DOMAINSTATS")
    # for row in cursor:
    #     statuses.append((row[0], row[1], row[2]))

    statuses = [(row[0], row[1], row[2]) for row in cursor]
    print("Rows Returned")
    conn.close()
    return statuses


def write_table(domain, port, status):
    conn = sqlite3.connect('cli-test')
    print("Opened database successfully")

    # if greater than 10 push out last and write as first

    try:
        conn.execute("INSERT INTO DOMAINSTATS (DOMAIN,PORT,STATUS) \
              VALUES (?,?,?)", (domain, port, status))

    except sqlite3.IntegrityError:
        print('Updating')
        cursor = conn.cursor()
        cursor.execute("""UPDATE DOMAINSTATS SET status=? WHERE domain=?;""", (status, domain))
        cursor.close()
        print('Update Successful!')

    conn.commit()
    print("Records created successfully")
    conn.close()
