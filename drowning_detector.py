from inference.models.utils import get_roboflow_model
import cv2
import time
import sys
import traceback
import paho.mqtt.client as paho
import base64



def my_excepthook(exc_type, exc_value, exc_traceback):
    print("Exception type:", exc_type)
    print("Exception value:", exc_value)
    print("Traceback:", traceback.format_tb(exc_traceback))

sys.excepthook = my_excepthook

def detect_drowning(camera):
    # Roboflow model
    model_name = "drowning-detection-and-prevention-in-swimming-pools"
    model_version = "1"

    # Open the default camera (usually the built-in webcam)
    #cap = cv2.VideoCapture("C:\\Users\\aziza\Desktop\\Distance_Estimation\\data\\drowning1.mp4")
    #cap=cv2.VideoCapture('C:\\Users\\aziza\\Desktop\\Distance_Estimation\\data\\drowning1.mp4')
    cap=cv2.VideoCapture(1)
    # Check if the webcam is opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    # Get Roboflow face model (this will fetch the model from Roboflow)
    model = get_roboflow_model(
        model_id="{}/{}".format(model_name, model_version),
        #Replace ROBOFLOW_API_KEY with your Roboflow API Key
        api_key="jt5MwQbmMrzpeeeREwXf"
    )

    outputs=[]
    count=0
    while True:
        # Capture frame-by-frame 
        ret, frame = cap.read()
        start = time.time()
        _, buffer1 = cv2.imencode('.jpg', frame)
                    # Converting into encoded bytes
        jpg_as_text1 = base64.b64encode(buffer1)
                    
                    # Publishig the Frame on the Topic home/server
        client.publish("test/stream/cam1", jpg_as_text1)
        end=time.time()
        print(end-start)
  # Read Frame
        # Encoding the Frame
        
    
        #frame=cv2.resize(frame,(480,480))

        # If the frame was read successfully, display it
        if ret:
            # Run inference on the frame
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
                    cv2.rectangle(frame, (x0, y0), (x1, y1), color, 2)  # Draw the bounding box

                    # Prepare the label text with class name and confidence
                    label_text = f"{prediction.class_name}: {prediction.confidence:.2f}"
                    
                    # Get text size to adjust the label position
                    (text_width, text_height), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                    
                    # Draw label background for better readability
                    cv2.rectangle(frame, (x0, y0 - text_height - 10), (x0 + text_width, y0), color, -1)
                    
                    # Put the label text on the frame
                    cv2.putText(frame, label_text, (x0, y0 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text, 2)
            outputs.append(current_output)                    
            # Now you can use these variables as needed
            # Display the resulting frame
            cv2.imshow('Webcam Feed', frame)

            # Press 'q' to quit the video window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Error: Could not read frame.")
            break

    # When everything is done, release the capture and destroy all windows
    cap.release()
    cv2.destroyAllWindows()
    return outputs

client= paho.Client(paho.CallbackAPIVersion.VERSION2, "streamer")#create client object client1.on_publish = on_publish #assign function to callback client1.connect(broker,port) #establish connection client1.publish("house/bulb1","on")
client.username_pw_set("streamer","stream")


broker="192.168.1.23"  
client.connect(broker)
my_list=detect_drowning(0)
drowning=my_list.count("drowning")
no_preds=my_list.count("no prediction")
preds=(len(my_list)-no_preds)
rest=len(my_list)-drowning-no_preds
print("drowning: ",drowning)
print("not drowning: ",rest)
if((drowning/preds)>0.4):
    print(drowning/preds)
    client.publish("test/cylinder","true")
