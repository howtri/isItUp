# Tristan Howell
# Performs DB operations for isItUp.py
# This is certainly vulnerable to SQL injection as is, either regex to validate user in or strip of characters here

import sqlite3
import logging

logging.basicConfig(filename='./app/logs/dbActions.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

def initialize_table():
    """
    Creates sqlite table DOMAINSTATS with columnds DOMAIN, PORT, STATUS
    """
    conn = sqlite3.connect('cli-test')
    logging.info("Opened database successfully")

    conn.execute('''CREATE TABLE DOMAINSTATS
             (DOMAIN CHAR(50) PRIMARY KEY     NOT NULL,
             PORT           INT    NOT NULL,
             STATUS CHAR(50) NOT NULL);''')

    logging.info("Table created successfully")


def read_table():
    """
    Outputs all rows in DOMAINSTATS as a tuple
    """
    conn = sqlite3.connect('cli-test')
    logging.info("Opened database successfully")
    cursor = conn.execute("SELECT domain, port, status from DOMAINSTATS")
    statuses = [(row[0], row[1], row[2]) for row in cursor]
    logging.info("Rows Returned")
    conn.close()
    return statuses


def write_table(domain, port, status):
    """
    Writes new DOMAIN PORT STATUS to DOMAINSTATS. If the domain is already present then the exception will update
    with the new status
    """
    conn = sqlite3.connect('cli-test')
    logging.info("Opened database successfully")

    # if greater than 10 push out last and write as first

    try:
        conn.execute("INSERT INTO DOMAINSTATS (DOMAIN,PORT,STATUS) \
              VALUES (?,?,?)", (domain, port, status))

    except sqlite3.IntegrityError:
        logging.info(f'Updating {domain} as {status} ')
        cursor = conn.cursor()
        cursor.execute("""UPDATE DOMAINSTATS SET status=? WHERE domain=?;""", (status, domain))
        cursor.close()
        logging.info('Update Successful!')

    conn.commit()
    logging.info(f'Write successful for {domain}:{port} status: {status}')
    conn.close()
