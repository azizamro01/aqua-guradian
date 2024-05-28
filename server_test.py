import paho.mqtt.client as paho
from datetime import datetime, timedelta
from srsconfig import config
from chipsrepository import *
from scheduled import timer
import testAAge as ad
import cv2 as cv2
import base64

datasource=config.datasource
broker=config.broker
mqtt_topic=config.topic
camera_confgi=config.camera

def decode_message(message):
    return message.decode("utf-8")

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
            # chid=ad.is_child(cap)
            # if(chid):
            #     client.publish("test/alert","true")
    if(message.topic=="test/cylinder/control"):
        if message.payload.decode("utf-8")=="true":
            client.publish("test/cylinder","true")
            client.publish("test/status","NETUP")
            client.publish("test/log","Rescue's activated")
        if message.payload.decode("utf-8")=="false":    
            client.publish("test/cylinder","false")
            client.publish("test/log","Net returned to idle")
            client.publish("test/status","NETDOWN")

client= paho.Client(paho.CallbackAPIVersion.VERSION2, config.broker.username)#create client object client1.on_publish = on_publish #assign function to callback client1.connect(broker,port) #establish connection client1.publish("house/bulb1","on")
client.username_pw_set(broker.username,broker.password)
timer()
client.on_message=on_message
print("connecting to broker ",broker.ip)
client.connect(broker.ip)
client.subscribe(mqtt_topic.ultra)
client.subscribe(mqtt_topic.ping)
client.subscribe(mqtt_topic.cylinder_control)
client.loop_start()

# cap=cv2.VideoCapture(0)
# while True:
#     ret,frame=cap.read()
#     if not ret:
#         break
#     _, buffer1 = cv2.imencode('.jpg', frame)
#     jpg_as_text1 = base64.b64encode(buffer1)
#     client.publish(mqtt_topic.stream_cam2,jpg_as_text1)

                        


