import threading
from datetime import datetime, timedelta
from chipsrepository import *

def task():
    rows=getall(con)
    for row in rows:
        if(row['last_seen']+timedelta(seconds=5)<datetime.now()):
            update(con,row['name'],"OFFLINE")
    print("Task executed")

def timer():
    threading.Timer(8.0, timer).start()
    task()


