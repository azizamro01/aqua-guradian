import cv2 as cv
import time
from collections import Counter

# Paths to models
faceProto = "modelNweight\\opencv_face_detector.pbtxt"
faceModel = "modelNweight\\opencv_face_detector_uint8.pb"
ageProto = "modelNweight\\age_deploy.prototxt"
ageModel = "modelNweight\\age_net.caffemodel"

# Load network models
ageNet = cv.dnn.readNet(ageModel, ageProto)
faceNet = cv.dnn.readNet(faceModel, faceProto)

# Constants
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
padding = 20

fourcc = cv.VideoWriter_fourcc(*'XVID')
out = cv.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

# Function to get face bounding box
def getFaceBox(net, frame, conf_threshold=0.7):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]
    blob = cv.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], True, False)
    net.setInput(blob)
    detections = net.forward()
    bboxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            bboxes.append([x1, y1, x2, y2])
            cv.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return frame, bboxes

# Function to detect age
def age_detector(frame, age_predictions):
    frameFace, bboxes = getFaceBox(faceNet, frame)
    if bboxes:
        bbox = bboxes[0]  # consider only the first detected face for simplicity
        face = frame[max(0, bbox[1]-padding):min(bbox[3]+padding, frame.shape[0]-1),
                     max(0, bbox[0]-padding):min(bbox[2]+padding, frame.shape[1]-1)]
        if face.size == 0:
            return frameFace, None
        blob = cv.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
        ageNet.setInput(blob)
        agePreds = ageNet.forward()
        age = ageList[agePreds[0].argmax()]
        age_predictions.append(age)
        label = "{}".format(age)
        cv.putText(frameFace, label, (bbox[0], bbox[1]-10), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv.LINE_AA)
        print(age)
        most=Counter(age_predictions)
    return frameFace, age_predictions

# Main function to process the video
def get_Age(cap):
    # cap = cv.VideoCapture(camera)
    if not cap.isOpened():
        print("Error: Failed to open camera.")
        return

    start_time = time.time()
    age_predictions = []

    while time.time() - start_time < 7:  # run for 3 seconds
        ret, frame = cap.read()
        if not ret:
            break
        frame, age_predictions = age_detector(frame, age_predictions)
        out.write(frame)

    if age_predictions:
        most_common_age = Counter(age_predictions).most_common(1)[0][0]
        return most_common_age
    return "No age detected"

def is_child(camera):
    most_common_age=get_Age(camera)
    if most_common_age in ['(0-2)', '(4-6)', '(8-12)']:
        return True
    else:
        return False

cap= cv.VideoCapture(0)
print("most common: ",get_Age(cap))