import paho.mqtt.client as paho
from datetime import datetime, timedelta
import psycopg2
from psycopg2 import sql
import testAAge as ad

#username: srs
#

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


def get_chip_status(chip_name):
    chips=getall(con)
    for chip in chips:
        if chip['name']==chip_name:
            return chip['status']
        



con=connect("srs","aziz","root","localhost","5432")


broker="192.168.1.23"                                                                
#define callback
def on_message(client, userdata, message):
    if(message.topic=="ping"):
        print("pinged" ,message.payload)
        update(con,message.payload.decode("utf-8"),"ONLINE")
        recieved_message=(message.payload.decode("utf-8"))
        pinged_about=recieved_message
        client.publish("ping/response","ONLINE"+pinged_about) 
    if(message.topic=="test/ultra"):       
        if message.payload.decode("utf-8")=="true":
            client.publish("test/log","Motion's detected around the pool entrance")
            age=ad.get_Age(0)
            if(age=="(25-32)"):
                client.publish("test/alert","true")
    if(message.topic=="test/cylinder/control"):
        if message.payload.decode("utf-8")=="true":
            client.publish("test/cylinder","true")
            client.publish("test/status","NETUP")
            client.publish("test/log","Rescue's activated")
        if message.payload.decode("utf-8")=="false":    
            client.publish("test/cylinder","false")
            client.publish("test/log","Net returned to idle")
            client.publish("test/status","NETDOWN")

import threading


def task():
    offline_cylinders=[]
    ultra=True
    alert=True
    rows=getall(con)
    for row in rows:
        if(row['last_seen']+timedelta(seconds=5)<datetime.now()):
            if(row['name']=="ALERT"):
                alert=False
            elif(row['name']=="ULTRA"):
                ultra=False
                client.publish("test/status","ALERTFALSE")        
            elif(row['name'] in ["CYLINDER 1","CYLINDER 2","CYLINDER 3","CYLINDER 4"]):
                offline_cylinders.append(row['name'])            
            update(con,row['name'],"OFFLINE")
    if(ultra and not alert):
        client.publish("test/status","ALERTBAD")        
    if(len(offline_cylinders)==1):
        client.publish("test/status","RESCUEBAD")
    elif(len(offline_cylinders)>1):
        client.publish("test/status","RESCUEFALSE")
    elif(len(offline_cylinders)==0):
        client.publish("test/status","RESCUETRUE")    
    if(alert and ultra):
        client.publish("test/status","ALERTTRUE")    
    print("Task executed")

def timer():
    threading.Timer(8.0, timer).start()
    task()

client= paho.Client(paho.CallbackAPIVersion.VERSION2, "MANAGER")
client.username_pw_set("MANAGER","strong")


timer()

client.on_message=on_message
print("connecting to broker ",broker)
client.connect(broker)#connect
client.subscribe("test/ultra")#subscribe
client.subscribe("ping")
client.subscribe("test/cylinder/control")
client.loop_forever()
