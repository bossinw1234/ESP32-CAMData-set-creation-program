import cv2
import numpy as np
import urllib.request
import csv
import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import messagebox
import sys

# ตัวแปรโกลบอล
drawing = False  # จริงหากมีการกดเมาส์
ix, iy = -1, -1
img = None
img_original = None  # เก็บภาพต้นฉบับ
counter = 0  # เริ่มตั้งค่าตัวแปรนับไฟล์
csv_filename = 'labelHuman.csv'  # ชื่อไฟล์ CSV

# Mouse callback function
def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, img, img_original, counter

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_temp = img.copy()
            cv2.rectangle(img_temp, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('Image', img_temp)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        counter += 1  # เพิ่มค่านับไฟล์ที่บันทึกไว้

        # ให้ผู้ใช้เลือกตำแหน่งที่ต้องการบันทึกภาพ
        file_path = choose_save_location()
        # ให้ผู้ใช้ป้อนประเภทของรูปภาพ
        image_type = choose_image_type()

        # บันทึกภาพต้นฉบับที่ไม่มีการแก้ไข
        original_path = file_path.replace('.jpg', '_old.jpg')
        save_image(img_original, original_path)

        # บันทึกภาพที่มีกรอบ
        cv2.rectangle(img, (ix, iy), (x, y), (0, 255, 0), 2)
        annotated_path = file_path
        save_image(img, annotated_path)

        # บันทึกภาพที่ถูกครอปตามกรอบ
        crop_img = img_original[iy:y, ix:x]
        cropped_path = file_path.replace('.jpg', '_crop.jpg')
        save_image(crop_img, cropped_path)

        # บันทึกพิกัดและประเภทภาพในไฟล์ CSV
        save_coordinates(annotated_path, (ix, iy), (x, y), image_type, original_path)

# ฟังก์ชันในการเลือกตำแหน่งที่ต้องการบันทึกภาพ
def choose_save_location():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("Image files", "*.jpg"), ("All files", "*.*")])
    # แสดงตำแหน่งที่เลือก
    messagebox.showinfo("Location", f"คุณเลือกตำแหน่งที่: {file_path}")
    # ปิดหน้าต่างหลังจากผู้ใช้เลือกตำแหน่ง
    root.destroy()
    return file_path

# ฟังก์ชันในการเลือกประเภทภาพผ่าน GUI
def choose_image_type():
    root = tk.Tk()
    root.withdraw()
    user_input = simpledialog.askstring("Input", "ป้อนประเภทของรูปภาพ:")
    # แสดงประเภทที่เลือก
    messagebox.showinfo("Type", f"ประเภทของรูปภาพ: {user_input}")
    # ปิดหน้าต่างหลังจากผู้ใช้ป้อนประเภท
    root.destroy()
    return user_input

# ฟังก์ชันในการจับภาพจาก ESP32-CAM
def capture_image(url):
    try:
        with urllib.request.urlopen(url) as response:
            img_array = np.array(bytearray(response.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)
        if img is None:
            raise ValueError("ไม่สามารถดีโค้ดภาพได้")
    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการจับภาพ: {e}")
        return None
    return img

# ฟังก์ชันในการบันทึกภาพ
def save_image(img, filename):
    cv2.imwrite(filename, img)
    print("บันทึกภาพเป็น", filename)

# ฟังก์ชันในการบันทึกพิกัดและประเภทภาพในไฟล์ CSV
def save_coordinates(file_path, top_left, bottom_right, image_type, original_path):
    with open(csv_filename, 'a+', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # เขียนหัวข้อเฉพาะครั้งแรก
        if csvfile.tell() == 0:
            writer.writerow(['Path', 'Top_Left_X', 'Top_Left_Y', 'Bottom_Right_X', 'Bottom_Right_Y', 'Type', 'Original_Path'])
        writer.writerow([file_path, top_left[0], top_left[1], bottom_right[0], bottom_right[1], image_type, original_path])

def main(url):
    global img, img_original

    cv2.namedWindow('Image')
    cv2.setMouseCallback('Image', draw_rectangle)

    while True:
        # จับภาพจาก ESP32-CAM
        img = capture_image(url)
        if img is None:
            break  # หากจับภาพไม่ได้ ให้หยุดการทำงาน

        img_original = img.copy()  # เก็บภาพต้นฉบับ

        # แสดงภาพ
        cv2.imshow('Image', img)

        # รอปุ่ม 'q' เพื่อออก
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        
        # ตรวจสอบการปิดหน้าต่าง
        if cv2.getWindowProperty('Image', cv2.WND_PROP_VISIBLE) < 1:
            break

    cv2.destroyAllWindows()
    sys.exit(0)  # เพิ่มบรรทัดนี้เพื่อให้โปรแกรมหยุดทำงาน


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python program1.py <ESP32-CAM URL>")
        sys.exit(1)

    url = sys.argv[1]
    main(url)
