import threading
import cv2
import time
from inference.models.utils import get_roboflow_model
import paho.mqtt.client as paho
import base64


# Lock for synchronizing access to frames
frames_lock = threading.Lock()
frames = []
outputs = []

# Thread function for detecting drowning
def detect_drowning(id, model):
    while True:
        with frames_lock:
            if len(frames) > id:
                frame = frames[id]
            else:
                continue

        if frame is not None:
            results = model.infer(image=frame, confidence=0.5, iou_threshold=0.5)
            current_output = "no prediction"
            for inference_response in results:
                for prediction in inference_response.predictions:
                    if prediction.class_name != "drowning":
                        current_output = "swimming"
                    else:
                        current_output = "drowning"
            outputs.append(current_output)
    return outputs

# Initialize the model
model_name = "drowning-detection-and-prevention-in-swimming-pools"
model_version = "1"
model = get_roboflow_model(
    model_id="{}/{}".format(model_name, model_version),
    api_key="jt5MwQbmMrzpeeeREwXf"
)

# Start threads for detecting drowning
threads = []
for i in range(0, 11):
    thread = threading.Thread(target=detect_drowning, kwargs={'id': i, 'model': model})
    thread.start()
    threads.append(thread)

# Capture frames from the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

client= paho.Client(paho.CallbackAPIVersion.VERSION2, "streamer")
client.username_pw_set("streamer","stream")

broker="192.168.1.23"  
client.connect(broker)
flag=True
print("started")
start=time.time()
while flag:
    for i in range(0, 11):
        ret, frame = cap.read()
        if not ret:
            flag=False
            break

        with frames_lock:
            if len(frames) > i:
                frames[i] = frame
                temp=frames[i]
            else:
                frames.append(frame)      
    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()

end=time.time()
print(f"Processed in {end-start} seconds")
d=outputs.count("drowning")
s=outputs.count("swimming")
print("Drwoning: ",d)
print("Swimming: ",s)


for thread in threads:
    thread.join()
