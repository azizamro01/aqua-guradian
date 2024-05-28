from inference.models.utils import get_roboflow_model
import cv2
import time
import sys
import traceback
import paho.mqtt.client as paho
import base64
from srsconfig import config

broker=config.broker
mqtt_topic=config.topic
camera_config=config.camera


def my_excepthook(exc_type, exc_value, exc_traceback):
    print("Exception type:", exc_type)
    print("Exception value:", exc_value)
    print("Traceback:", traceback.format_tb(exc_traceback))

sys.excepthook = my_excepthook

def detect_drowning():
    # Roboflow model
    model_name = "drowning-detection-and-prevention-in-swimming-pools"
    model_version = "1"

    cap=cv2.VideoCapture(camera_config.pool_camera_source)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    model = get_roboflow_model(
        model_id="{}/{}".format(model_name, model_version),
        api_key="jt5MwQbmMrzpeeeREwXf"
    )

    outputs=[]
    count=0
    start=time.time()
    while True:
        total_conf=0
        while time.time()-start<=1:
            ret, frame = cap.read()
            _, buffer1 = cv2.imencode('.jpg', frame)
            jpg_as_text1 = base64.b64encode(buffer1)
                        
            client.publish(mqtt_topic.stream_cam1, jpg_as_text1)

            if ret:
                results = model.infer(image=frame,
                                confidence=0.5,
                                iou_threshold=0.5)
                current_output="no prediction"
                for inference_response in results:
                    for prediction in inference_response.predictions:
                        if(prediction.class_name=="drowning"):
                            color=(255,0,0)
                            text=(255,255,255)
                        else:
                            color=(0,255,0)
                            text=(0,0,0)    
                        x0 = int(prediction.x-prediction.width/2)
                        y0 = int(prediction.y-prediction.height/2)
                        x1 = int(prediction.x + prediction.width/2)
                        y1 = int(prediction.y + prediction.height/2)
                        current_output=prediction.class_name
                        total_conf+=prediction.confidence
                        cv2.rectangle(frame, (x0, y0), (x1, y1), color, 2)

                        label_text = f"{prediction.class_name}: {prediction.confidence:.2f}"
                        
                        (text_width, text_height), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                        
                        cv2.rectangle(frame, (x0, y0 - text_height - 10), (x0 + text_width, y0), color, -1)
                        
                        cv2.putText(frame, label_text, (x0, y0 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text, 2)
                outputs.append(current_output)                    
              
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("Error: Could not read frame.")
                break
        drowning=outputs.count("drowning")
        no_preds=outputs.count("no prediction")
        preds=(len(outputs)-no_preds)
        rest=len(outputs)-drowning-no_preds
        print("drowning: ",drowning)
        print("not drowning: ",rest)
        if(preds != 0):
            print("total conf: ",total_conf/preds)
            if((drowning/preds)>0.4):
                print(drowning/preds)
                client.publish(mqtt_topic.cylinder,"true")
        outputs=[]
        start=time.time() 
    
client= paho.Client(paho.CallbackAPIVersion.VERSION2, "streamer")
client.username_pw_set("streamer","stream")


client.connect(broker.ip)
client.loop_start()
detect_drowning()
