import cv2
import numpy as np
import urllib.request
import csv
import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog
import sys

# ตัวแปรโกลบอล
csv_filename = 'labelHuman.csv'
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

def capture_image(url):
    try:
        with urllib.request.urlopen(url) as response:
            img_array = np.array(bytearray(response.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)
        return img
    except Exception as e:
        print("Error capturing image:", e)
        return None

def save_image(img, filename):
    try:
        cv2.imwrite(filename, img)
        print("Saved image as", filename)
    except Exception as e:
        print("Error saving image:", e)

def save_coordinates(file_path, top_left, bottom_right, image_type, original_path):
    try:
        with open(csv_filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if csvfile.tell() == 0:
                writer.writerow(['Path', 'Top_Left_X', 'Top_Left_Y', 'Bottom_Right_X', 'Bottom_Right_Y', 'Type', 'Original_Path'])
            writer.writerow([file_path, top_left[0], top_left[1], bottom_right[0], bottom_right[1], image_type, original_path])
    except Exception as e:
        print("Error saving coordinates:", e)

def detect_person_and_get_coordinates(img):
    height, width, channels = img.shape
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5 and class_id == 0:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                # ปรับค่าพิกัดที่ติดลบและขนาดกรอบ
                x = max(0, x)
                y = max(0, y)
                w = min(w, width - x)
                h = min(h, height - y)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
    
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    coordinates = []
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            coordinates.append(((x, y), (x + w, y + h)))
    return coordinates

def draw_rectangle(img, coordinates):
    for (top_left, bottom_right) in coordinates:
        cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
    return img

def choose_save_location():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("Image files", "*.jpg"), ("All files", "*.*")])
    root.destroy()
    return file_path

def choose_image_type():
    root = tk.Tk()
    root.withdraw()
    user_input = simpledialog.askstring("Input", "ป้อนประเภทของรูปภาพ:")
    root.destroy()
    return user_input

def main(url):
    while True:
        img = capture_image(url)
        if img is not None:
            coordinates = detect_person_and_get_coordinates(img)
            img_with_rect = img.copy()
            if coordinates:
                img_with_rect = draw_rectangle(img_with_rect, coordinates)
            cv2.imshow('Image', img_with_rect)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c'):
                if coordinates:
                    file_path = choose_save_location()
                    if file_path:
                        image_type = choose_image_type()
                        original_path = file_path[:-4] + '_old.jpg'
                        save_image(img, original_path)
                        save_image(img_with_rect, file_path)
                        for idx, (top_left, bottom_right) in enumerate(coordinates):
                            crop_img = img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                            crop_path = file_path[:-4] + f'_crop_{idx}.jpg'
                            save_image(crop_img, crop_path)
                            save_coordinates(crop_path, top_left, bottom_right, image_type, original_path)
            if key == ord('q'):
                break

        # ตรวจสอบการปิดหน้าต่าง
        if cv2.getWindowProperty('Image', cv2.WND_PROP_VISIBLE) < 1:
            break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python program2.py <ESP32-CAM URL>")
        sys.exit(1)

    url = sys.argv[1]
    main(url)
