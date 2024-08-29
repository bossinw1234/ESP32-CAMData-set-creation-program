import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
import os

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("โปรแกรมแปลงวิดีโอเป็นรูปภาพ")
        self.geometry("400x150")
        self.configure(bg="#F0F0F0")
        
        self.label = tk.Label(self, text="โปรแกรมแปลงวิดีโอเป็นรูปภาพ", font=("Helvetica", 16), bg="#F0F0F0")
        self.label.pack(pady=10)

        self.btn_select_video = tk.Button(self, text="เลือกไฟล์วิดีโอ", font=("Helvetica", 14), command=self.select_video)
        self.btn_select_video.pack(pady=10, ipadx=10, ipady=5, fill=tk.X)

    def select_video(self):
        video_path = filedialog.askopenfilename(filetypes=[("ไฟล์วิดีโอ", "*.mp4;*.avi;*.mov")])
        if video_path:
            self.convert_video_to_frames(video_path)
            messagebox.showinfo("สำเร็จ", "การแปลงวิดีโอเป็นรูปภาพเสร็จสมบูรณ์")

    def convert_video_to_frames(self, video_path):
        # เปิดไฟล์วิดีโอ
        cap = cv2.VideoCapture(video_path)

        # ตรวจสอบว่าสามารถเปิดไฟล์วิดีโอได้หรือไม่
        if not cap.isOpened():
            messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถเปิดไฟล์วิดีโอได้")
            return

        # สร้างไดเรกทอรีเพื่อบันทึกรูปภาพ
        frame_dir = os.path.splitext(video_path)[0] + "_frames"
        os.makedirs(frame_dir, exist_ok=True)

        # อ่านและแปลงทุกเฟรมเป็นรูปภาพ
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # บันทึกรูปภาพ
            frame_path = os.path.join(frame_dir, f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_count += 1

        # ปิดไฟล์วิดีโอ
        cap.release()

if __name__ == "__main__":
    app = Application()
    app.mainloop()
