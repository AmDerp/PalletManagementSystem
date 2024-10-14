import cv2
import torch
import numpy as np
import time
import requests
import json
import time

# Constants
# Adjusts ROIs/Registers as needed
ROI_REGISTERS = {
    'A': 'FP30',
    'B': 'FP40',
}

# Initialize variables
request_sent = {}
consecutive_detection_count = {}
detection_count = {}
model = torch.hub.load('ultralytics/yolov5', 'custom', path='/home/df/am/yolov5/runs/train/exp17/weights/best.pt')
target_classes = ['Pallet']
pts_list = []
roi_count = 0
cap = cv2.VideoCapture(4)  #Camera used for the image streaming
last_capture_time = time.time()

# Define functions
def draw_polygon(event, x, y, flags, param):
    global pts, roi_count
    if event == cv2.EVENT_LBUTTONDOWN:
        if roi_count < len(pts_list):
            pts_list[roi_count].append([x, y])
        else:
            pts_list.append([[x, y]])
            detection_count[chr(65 + len(pts_list) - 1)] = 0
    elif event == cv2.EVENT_RBUTTONDOWN:
        roi_count += 1

def inside_polygon(point, polygon):
    result = cv2.pointPolygonTest(polygon, (point[0], point[1]), False)
    return result == 1

def preprocess(img):
    height, width = img.shape[:2]
    ratio = height / width
    return cv2.resize(img, (640, int(640 * ratio)))

def send_request(area_label, value):
    register_name = ROI_REGISTERS.get(area_label, 'Unknown Register')
    URL = f"https://dfleet-p2.demo.dfautomation.com/api/v3/registers/{register_name}"
    HEADERS = {
        'Authorization': 'Token 1e928852912af42ac30af76f53e71f4c0385466e',
        'Content-type': 'application/json'
    }
    REQUESTS_BODY = {
        "name": register_name,
        "value": value
    }
    response = requests.put(URL, json=REQUESTS_BODY, headers=HEADERS)
    if response.ok:
        print(f"Alarm triggered in area {area_label} for {'Pallet' if value == '1' else 'No Pallet'}")
    else:
        print(f"Error sending request to API: {response.text}")

# Create a window and set the mouse callback
cv2.namedWindow('Image')
cv2.setMouseCallback('Image', draw_polygon)

# Capture an initial frame from the camera
ret, img = cap.read()
img = preprocess(img)

while True:
    try:
        current_time = time.time()
        if current_time - last_capture_time >= 1:
            ret, img = cap.read()
            last_capture_time = current_time
            img = preprocess(img)
            model.conf = 0.65
            model.iou = 0.45
            results = model(img)

            detected_areas = set()

            for index, row in results.pandas().xyxy[0].iterrows():
                if row['name'] in target_classes:
                    x1, y1, x2, y2, confidence, name = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax']), row['confidence'], row['name']
                    center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 0), 3)
                    cv2.putText(img, name, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                    cv2.circle(img, (center_x, center_y), 5, (0, 0, 255), -1)

                    for i, pts in enumerate(pts_list):
                        if len(pts) >= 4:
                            area_label = chr(65 + i)
                            cv2.drawContours(img, [np.array(pts)], -1, (0, 255, 0), 2)
                            cv2.putText(img, area_label, (pts[0][0], pts[0][1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            if area_label in consecutive_detection_count:
                                cv2.putText(img, f"Count: {consecutive_detection_count[area_label]}", (pts[0][0], pts[0][1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                            if inside_polygon((center_x, center_y), np.array([pts])):
                                print(f"Detection is within ROI {area_label}")
                                detected_areas.add(area_label)
                                if area_label not in consecutive_detection_count:
                                    consecutive_detection_count[area_label] = 0
                                consecutive_detection_count[area_label] += 1
                                print(f"Detection count for ROI {area_label} is now {consecutive_detection_count[area_label]}")
                                if consecutive_detection_count[area_label] >= 3: #Increase or decrease value as needed for detection before updating register
                                    if area_label not in request_sent or not request_sent.get(area_label, False):
                                        send_request(area_label, '1')
                                        request_sent[area_label] = True

            for area_label in consecutive_detection_count:
                if area_label not in detected_areas:
                    print(f"Pallet is no longer within ROI {area_label}")
                    consecutive_detection_count[area_label] = 0
                    if area_label in detection_count:
                        detection_count[area_label] = 0
                    if area_label in request_sent and request_sent[area_label]:
                        send_request(area_label, '0')
                        request_sent[area_label] = False

        cv2.imshow('Image', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except Exception as e:
        print(f"An error occurred: {e}")
        break

cap.release()
cv2.destroyAllWindows()
