import psycopg2
import time
from datetime import datetime, timedelta
import psycopg2
from psycopg2 import sql
from srsconfig import config

def connect(db,username,passwd,server,onport):
    return psycopg2.connect(
    dbname=db,
    user=username,
    password=passwd,
    host=server,
    port=onport
)


def update(connection,chip_name,status):
    cur=connection.cursor()
    update_query = sql.SQL("""
    UPDATE chips
    SET last_seen = %s,
    status=%s
    WHERE name = %s""")

# Example data for the update query
    last_seen = datetime.now()
    name = chip_name

# Execute the update query
    cur.execute(update_query, (last_seen,status,chip_name))

# Commit the transaction
    connection.commit()


def getall(connection):
    list=[]
    cur=connection.cursor()
    cur.execute("SELECT * FROM CHIPS")
    rows=cur.fetchall()
    for row in rows:
        list.append({"id":row[0],"name":row[1],"last_seen":row[2],"status":row[3]})

    return list

con=connect(
            db=config.datasource.database,
            username=config.datasource.username,
            passwd=config.datasource.password,
            server=config.datasource.ip,
            onport=config.datasource.port)