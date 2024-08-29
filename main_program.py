import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess

def run_program_1():
    root.withdraw()
    url = simpledialog.askstring("Input", "ป้อน URL ของ ESP32-CAM:", initialvalue="http://192.168.175.191/capture")
    root.deiconify()

    if url:
        if not url.startswith("http://") or not url.endswith("/capture"):
            messagebox.showerror("Error", "URL ไม่ถูกต้อง กรุณาป้อน URL ในรูปแบบ 'http://<IP>/capture'")
            return
        
        process = subprocess.Popen(["python", "program1.py", url])
        
    else:
        messagebox.showinfo("Information", "URL ถูกยกเลิก")

def run_program_2():
    root.withdraw()
    url = simpledialog.askstring("Input", "ป้อน URL ของ ESP32-CAM:", initialvalue="http://192.168.175.191/capture")
    root.deiconify()

    if url:
        if not url.startswith("http://") or not url.endswith("/capture"):
            messagebox.showerror("Error", "URL ไม่ถูกต้อง กรุณาป้อน URL ในรูปแบบ 'http://<IP>/capture'")
            return
        
        process = subprocess.Popen(["python", "program2.py", url])
        
    else:
        messagebox.showinfo("Information", "URL ถูกยกเลิก")

def run_program_3():
    process = subprocess.Popen(["python", "program3.py"])


def run_program_4():
    process = subprocess.Popen(["python", "program4.py"])


def check_process(process):
    if process.poll() is None:
        root.after(100, check_process, process)
    else:
        root.quit()

root = tk.Tk()
root.title("โปรแกรมทำชุดข้อมูลของ ESP-32CAM")
root.geometry("400x300")  # กำหนดขนาดของหน้าต่าง


background_color = "#69d2e7"
root.configure(bg=background_color)
# โหลดไอคอน
new_icon_image = tk.PhotoImage(file="D:/Project ESP32-Cam Final program/icon.png")

# เปลี่ยนไอคอนของหน้าต่างหลัก
root.iconphoto(False, new_icon_image)
# ปรับขนาดของปุ่ม
button_width = 30
button_height = 2

button1 = tk.Button(root, text="โปรแกรมตีกรอบแบบ RealTime", command=run_program_1, bg="#4CAF50", fg="white", width=button_width, height=button_height)
button1.pack(pady=10)

button2 = tk.Button(root, text="โปรแกรมตีกรอบโดย AI", command=run_program_2, bg="#4CAF50", fg="white", width=button_width, height=button_height)
button2.pack(pady=10)

button3 = tk.Button(root, text="โปรแกรมตีกรอบโดยผู้ใช้งาน", command=run_program_3, bg="#4CAF50", fg="white", width=button_width, height=button_height)
button3.pack(pady=10)

button4 = tk.Button(root, text="โปรแกรมแปลงไฟล์วิดิโอเป็นรูปภาพ", command=run_program_4, bg="#4CAF50", fg="white", width=button_width, height=button_height)
button4.pack(pady=10)

root.mainloop()
