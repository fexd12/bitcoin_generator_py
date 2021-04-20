import sqlite3
import csv

def insertMany():
    with open('wallets_generated.csv','r') as f:
        lines = csv.DictReader(f,delimiter=';')
        for row in lines:
            priv = row['private_key']
            add  = row['wallets']
            yield (priv,add,)

with sqlite3.connect('bitcoin_db.db') as conn:

    curr = conn.cursor()

    curr.execute('BEGIN TRANSACTION')

    select_ = """select * from balance where address = ?"""

    insert_= """insert into address (private_key,address) values (?,?)"""

    # arquivo_ = open('teste2.csv','r')

    # for lines in arquivo_.readlines():
    #     try:
    #         priv = lines.split(';')[0]
    #         add  = lines.split(';')[2].split('\n')[0] 

    #         curr.execute(select_,(add,))
    #         curr.executemany()

    #         if curr.fetchone() != None:
    #             curr.execute(insert_,(add,priv,))
    #     except IndexError as e:
    #         continue

    curr.executemany(insert_,insertMany())

    conn.commit()
    curr.close()
    # arquivo_.close()