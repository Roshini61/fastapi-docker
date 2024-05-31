import cv2
import numpy as np
from ultralytics import YOLO
import tkinter as tk
from tkinter import simpledialog

# Function to handle login
def login():
    root = tk.Tk()
    root.withdraw()
    username = simpledialog.askstring("Login", "Enter username:")
    password = simpledialog.askstring("Login", "Enter password:", show='*')
    if username == "user" and password == "password":
        print(f"Welcome {username} to the object detection model......")
        return True
    else:
        print("Invalid username or password.")
        return False

# Function to preprocess frame
def preprocess_frame(frame, input_size):
    # Ensure the frame is resized to the correct input size
    if frame.shape[:2] != input_size:
        frame = cv2.resize(frame, input_size, interpolation=cv2.INTER_LINEAR)
    return frame

# start webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1920)
cap.set(4, 1080)

# model
model = YOLO("yolov8n.pt")

# object classes
classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]

if login():
    while True:
        success, img = cap.read()
        results = model(img, stream=True)

        # Count variables
        total_chairs = 0
        filled_chairs = 0
        empty_chairs = 0
        total_persons = 0

        # Coordinates
        for r in results:
            boxes = r.boxes

            for box in boxes:
                # Bounding box
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values

                # Object class
                cls = int(box.cls[0])

                # Count objects
                if classNames[cls] == "chair":
                    total_chairs += 1
                    # Check if chair is filled by checking for overlap with person
                    for other_box in boxes:
                        if int(other_box.cls[0]) == classNames.index("person"):
                            # Check if the person is sitting on the chair (simple overlap check)
                            if (x1 < other_box.xyxy[0][2] and x2 > other_box.xyxy[0][0] and
                                    y1 < other_box.xyxy[0][3] and y2 > other_box.xyxy[0][1]):
                                filled_chairs += 1
                                break
                    else:
                        empty_chairs += 1

                elif classNames[cls] == "person":
                    total_persons += 1

        # Create a white background for counts
        count_display = np.ones((img.shape[0], 300, 3), dtype=np.uint8) * 255
        cv2.putText(count_display, f"Total Chairs: {total_chairs}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(count_display, f"Filled Chairs: {filled_chairs}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(count_display, f"Empty Chairs: {empty_chairs}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(count_display, f"Total Persons: {total_persons}", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        # Combine the display with the webcam feed
        combined_display = np.hstack((count_display, img))

        # Show the combined image
        cv2.imshow('Webcam', combined_display)

        if cv2.waitKey(1) == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
