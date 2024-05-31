import cv2
import numpy as np
import time
from datetime import datetime
from ultralytics import YOLO

# Define login credentials
username = "admin"
password = "1234" 

# Login screen function
def login_screen():
    window_name = "Login"
    cv2.namedWindow(window_name)
    width, height = 600, 400  # Increased size

    # Load a background image
    login_img = cv2.imread("C:/Users/HP/Downloads/pic.jpg")
    login_img = cv2.resize(login_img, (width, height))

    cv2.putText(login_img, "Username:", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    cv2.putText(login_img, "Password:", (20, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    cv2.imshow(window_name, login_img)

    user_input = ""
    pass_input = ""
    user_done = False

    while True:
        key = cv2.waitKey(0)
        if key == 13:  # Enter key
            if user_done:
                break
            user_done = True
        elif key == 8:  # Backspace key
            if user_done:
                pass_input = pass_input[:-1]
            else:
                user_input = user_input[:-1]
        elif 32 <= key <= 126:  # Printable ASCII range
            if user_done:
                pass_input += chr(key)
            else:
                user_input += chr(key)

        display_img = login_img.copy()
        cv2.putText(display_img, user_input, (200, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        cv2.putText(display_img, "*" * len(pass_input), (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        cv2.imshow(window_name, display_img)

    cv2.destroyWindow(window_name)
    return user_input, pass_input

# Show login screen and validate
while True:
    input_username, input_password = login_screen()
    if input_username == username and input_password == password:
        break
    else:
        print("Invalid credentials. Try again.")

print("Login successful! Hello, user.")

# Load YOLOv8 model (higher precision model)
model = YOLO('yolov8n.pt')  # More accurate model

# Initialize video capture
video_path = "https://youtu.be/fBE_2sHDt4E?si=9Rx5AZNEl7B6hBk1"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

confidence_threshold = 0.5  # Define a confidence threshold for detections

def detect_objects(frame):
    results = model(frame)
    detected_person_bboxes = []
    detected_chair_bboxes = []
    detected_laptop_bboxes = []
    
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()  # Extracting bounding boxes
        confidences = result.boxes.conf.cpu().numpy()  # Extracting confidence scores
        class_ids = result.boxes.cls.cpu().numpy().astype(int)  # Extracting class IDs
        
        for box, confidence, class_id in zip(boxes, confidences, class_ids):
            if confidence > confidence_threshold:
                x1, y1, x2, y2 = box
                w, h = x2 - x1, y2 - y1
                if class_id == 0:  # Person class ID in COCO dataset
                    detected_person_bboxes.append((x1, y1, w, h))
                elif class_id == 56:  # Chair class ID in COCO dataset
                    detected_chair_bboxes.append((x1, y1, w, h))
                elif class_id == 63:  # Laptop class ID in COCO dataset
                    detected_laptop_bboxes.append((x1, y1, w, h))
                    
    return detected_person_bboxes, detected_chair_bboxes, detected_laptop_bboxes

def is_overlap(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
    yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])
    overlap = (xA < xB) and (yA < yB)
    return overlap

# Calculate FPS
prev_time = time.time()
frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (1280, 720))

    # Increment frame count
    frame_count += 1

    # Calculate fps every frame to ensure minimum of 120 FPS
    current_time = time.time()
    time_elapsed = current_time - prev_time
    if time_elapsed > 0:
        fps = frame_count / time_elapsed
    if fps < 120:
        frame_count = 0
        prev_time = current_time

    # Detect objects in the current frame
    detected_person_bboxes, detected_chair_bboxes, detected_laptop_bboxes = detect_objects(frame)

    # Count the objects
    person_count = len(detected_person_bboxes)
    chair_count = len(detected_chair_bboxes)
    laptop_count = len(detected_laptop_bboxes)

    # Draw bounding boxes for persons
    for bbox in detected_person_bboxes:
        x, y, w, h = map(int, bbox)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, 'Person', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Draw bounding boxes for chairs
    for bbox in detected_chair_bboxes:
        x, y, w, h = map(int, bbox)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(frame, 'Chair', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    # Draw bounding boxes for
    # Draw bounding boxes for laptops
    for bbox in detected_laptop_bboxes:
        x, y, w, h = map(int, bbox)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(frame, 'Laptop', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    # Determine and display the number of empty and filled chairs
    filled_chairs = 0
    for chair_bbox in detected_chair_bboxes:
        for person_bbox in detected_person_bboxes:
            if is_overlap(chair_bbox, person_bbox):
                filled_chairs += 1
                break
    empty_chairs = chair_count - filled_chairs

    # Display the current date and time with milliseconds
    now = datetime.now()
    current_time_str = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    cv2.putText(frame, current_time_str, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Display FPS
    cv2.putText(frame, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display counts
    cv2.putText(frame, f'Persons: {person_count}', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f'Chairs: {chair_count}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(frame, f'Laptops: {laptop_count}', (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display empty and filled chairs
    cv2.putText(frame, f'Filled Chairs: {filled_chairs}', (10, 230), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(frame, f'Empty Chairs: {empty_chairs}', (10, 270), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Show the frame
    cv2.imshow("Object Detection and Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
