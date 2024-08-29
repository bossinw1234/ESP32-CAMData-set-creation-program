import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import csv
import os
import json
from PIL import Image, ImageTk, ImageDraw

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ตีกรอบรูปภาพ")
        
        self.image = None
        self.image_path = None
        self.canvas = tk.Canvas(self, width=500, height=500)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.offset_x = 0
        self.offset_y = 0

        self.image_type_var = tk.StringVar(self)
        self.image_type_var.set("None")

        self.image_types_file = "image_types.json"
        self.image_types = self.load_image_types()

        self.frame_sizes_file = "frame_sizes.json"
        self.frame_sizes = self.load_frame_sizes()
        self.selected_frame_size = tk.StringVar(self)
        if self.frame_sizes:
            self.selected_frame_size.set(f"{self.frame_sizes[0]['width']}x{self.frame_sizes[0]['height']}")
        else:
            self.selected_frame_size.set("None")

        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="เปิดรูปภาพ", command=self.open_image)
        file_menu.add_command(label="บันทึกรูป", command=self.save_image)
        menubar.add_cascade(label="ไฟล์", menu=file_menu)

        self.type_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="เลือกประเภท", menu=self.type_menu)

        self.update_type_menu()

        manage_type_menu = tk.Menu(menubar, tearoff=0)
        manage_type_menu.add_command(label="เพิ่มประเภท", command=self.add_image_type)
        manage_type_menu.add_command(label="แก้ไขประเภท", command=self.edit_image_type)
        manage_type_menu.add_command(label="ลบประเภท", command=self.delete_image_type)
        menubar.add_cascade(label="จัดการประเภท", menu=manage_type_menu)

        self.select_frame_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="เลือกกรอบ", menu=self.select_frame_menu)

        self.update_select_frame_menu()
        
        frame_menu = tk.Menu(menubar, tearoff=0)
        frame_menu.add_command(label="สร้างกรอบใหม่", command=self.create_custom_rectangle)
        frame_menu.add_command(label="บันทึกกรอบ", command=self.save_current_frame)
        frame_menu.add_command(label="จัดการขนาดกรอบ", command=self.manage_frame_sizes)
        menubar.add_cascade(label="จัดการกรอบ", menu=frame_menu)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.csv_file_path = "labelHuman.csv"
        self.create_csv(self.csv_file_path)

    def load_image_types(self):
        if os.path.exists(self.image_types_file):
            with open(self.image_types_file, 'r') as file:
                return json.load(file)
        return ["walk", "sit", "crawl", "no human"]

    def save_image_types(self):
        with open(self.image_types_file, 'w') as file:
            json.dump(self.image_types, file)

    def load_frame_sizes(self):
        if os.path.exists(self.frame_sizes_file):
            with open(self.frame_sizes_file, 'r') as file:
                return json.load(file)
        return []

    def save_frame_sizes(self):
        with open(self.frame_sizes_file, 'w') as file:
            json.dump(self.frame_sizes, file)

    def update_type_menu(self):
        self.type_menu.delete(0, tk.END)
        for image_type in self.image_types:
            self.type_menu.add_radiobutton(label=image_type, variable=self.image_type_var, value=image_type)

    def update_select_frame_menu(self):
        self.select_frame_menu.delete(0, tk.END)
        for frame_size in self.frame_sizes:
            self.select_frame_menu.add_radiobutton(label=f"{frame_size['width']}x{frame_size['height']}", variable=self.selected_frame_size, value=f"{frame_size['width']}x{frame_size['height']}", command=self.select_frame_size)

    def add_image_type(self):
        new_type = simpledialog.askstring("เพิ่มประเภท", "กรุณาใส่ชื่อประเภทใหม่:")
        if new_type and new_type not in self.image_types:
            self.image_types.append(new_type)
            self.update_type_menu()
            self.save_image_types()

    def edit_image_type(self):
        old_type = self.image_type_var.get()
        if old_type in self.image_types:
            new_type = simpledialog.askstring("แก้ไขประเภท", f"กรุณาใส่ชื่อใหม่สำหรับประเภท '{old_type}':")
            if new_type and new_type not in self.image_types:
                index = self.image_types.index(old_type)
                self.image_types[index] = new_type
                self.update_type_menu()
                self.save_image_types()

    def delete_image_type(self):
        delete_type = self.image_type_var.get()
        if delete_type in self.image_types:
            confirm = messagebox.askyesno("ลบประเภท", f"คุณแน่ใจหรือว่าต้องการลบประเภท '{delete_type}'?")
            if confirm:
                self.image_types.remove(delete_type)
                self.image_type_var.set("None")
                self.update_type_menu()
                self.save_image_types()

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image_path = file_path
            self.image = Image.open(file_path)
            self.show_image()

    def show_image(self):
        self.image.thumbnail((500, 500))
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

    def on_press(self, event):
        items = self.canvas.find_withtag("current")
        if items:
            self.rect = items[0]
            self.start_x, self.start_y, _, _ = self.canvas.coords(self.rect)
            self.offset_x = event.x - self.start_x
            self.offset_y = event.y - self.start_y
        else:
            if self.rect:
                self.canvas.delete(self.rect)
            self.start_x = event.x
            self.start_y = event.y

    def on_drag(self, event):
        if self.rect:
            x0, y0, x1, y1 = self.canvas.coords(self.rect)
            new_x0 = event.x - self.offset_x
            new_y0 = event.y - self.offset_y
            new_x1 = new_x0 + (x1 - x0)
            new_y1 = new_y0 + (y1 - y0)
            self.canvas.coords(self.rect, new_x0, new_y0, new_x1, new_y1)
        else:
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="green", width=2)

    def on_release(self, event):
        if self.rect:
            x0, y0, x1, y1 = self.canvas.coords(self.rect)
            self.save_images((int(x0), int(y0), int(x1), int(y1)))

    def crop_image(self, coordinates):
        return self.image.crop(coordinates)

    def save_images(self, coordinates):
        # สร้างสำเนาของภาพต้นฉบับเพื่อวาดกรอบ
        image_with_frame = self.image.copy()
        draw = ImageDraw.Draw(image_with_frame)
        draw.rectangle(coordinates, outline="green", width=2)
        
        # บันทึกภาพที่มีกรอบ
        save_path_with_frame = filedialog.asksaveasfilename(defaultextension=".jpeg", filetypes=[("JPEG files", "*.jpeg")], title="Save image with frame")
        if save_path_with_frame:
            image_with_frame.save(save_path_with_frame, "JPEG")
            self.save_to_csv(save_path_with_frame, coordinates, self.image_type_var.get(), self.image_path)

            # บันทึกภาพที่ถูกครอบ (ไม่มีกรอบ, เพิ่ม _crop ต่อท้ายชื่อ)
            cropped_image = self.crop_image(coordinates)
            save_path_cropped = os.path.splitext(save_path_with_frame)[0] + "_crop.jpeg"
            cropped_image.save(save_path_cropped, "JPEG")

            # บันทึกภาพต้นฉบับ (ไม่มีการแก้ไข, เพิ่ม _old ต่อท้ายชื่อ)
            save_path_original = os.path.splitext(save_path_with_frame)[0] + "_old.jpeg"
            self.image.save(save_path_original, "JPEG")

    def create_csv(self, csv_file_path):
        if not os.path.exists(csv_file_path):
            with open(csv_file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Path', 'Top_Left_X', 'Top_Left_Y', 'Bottom_Right_X', 'Bottom_Right_Y', 'Type', 'Original_Path'])

    def save_to_csv(self, image_path, coordinates, image_type, original_path):
        with open(self.csv_file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([image_path, coordinates[0], coordinates[1], coordinates[2], coordinates[3], image_type, original_path])

    def save_image(self):
        if self.image:
            save_path = filedialog.asksaveasfilename(defaultextension=".jpeg", filetypes=[("JPEG files", "*.jpeg")])
            if save_path:
                self.image.save(save_path, "JPEG")

    def create_custom_rectangle(self):
        width = simpledialog.askinteger("กำหนดความกว้าง", "กรุณาใส่ความกว้างของกรอบ:")
        height = simpledialog.askinteger("กำหนดความสูง", "กรุณาใส่ความสูงของกรอบ:")
        
        if width and height:
            self.start_x = 250 - width // 2
            self.start_y = 250 - height // 2
            end_x = self.start_x + width
            end_y = self.start_y + height
            
            if self.rect:
                self.canvas.delete(self.rect)
            
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline="green", width=2)

    def save_current_frame(self):
        if self.rect:
            x0, y0, x1, y1 = self.canvas.coords(self.rect)
            self.save_images((int(x0), int(y0), int(x1), int(y1)))

    def select_frame_size(self):
        frame_size_str = self.selected_frame_size.get()
        width, height = map(int, frame_size_str.split('x'))
        self.create_rectangle_by_size(width, height)

    def create_rectangle_by_size(self, width, height):
        self.start_x = 250 - width // 2
        self.start_y = 250 - height // 2
        end_x = self.start_x + width
        end_y = self.start_y + height
        
        if self.rect:
            self.canvas.delete(self.rect)
        
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline="green", width=2)

    def manage_frame_sizes(self):
        self.top = tk.Toplevel(self)
        self.top.title("จัดการขนาดกรอบ")
        
        self.frame_listbox = tk.Listbox(self.top)
        self.frame_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        for frame_size in self.frame_sizes:
            self.frame_listbox.insert(tk.END, f"{frame_size['width']}x{frame_size['height']}")
        
        button_frame = tk.Frame(self.top)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        add_button = tk.Button(button_frame, text="เพิ่ม", command=self.add_frame_size)
        add_button.pack(fill=tk.X)
        
        edit_button = tk.Button(button_frame, text="แก้ไข", command=self.edit_frame_size)
        edit_button.pack(fill=tk.X)
        
        delete_button = tk.Button(button_frame, text="ลบ", command=self.delete_frame_size)
        delete_button.pack(fill=tk.X)

    def add_frame_size(self):
        width = simpledialog.askinteger("กำหนดความกว้าง", "กรุณาใส่ความกว้างของกรอบ:")
        height = simpledialog.askinteger("กำหนดความสูง", "กรุณาใส่ความสูงของกรอบ:")
        
        if width and height:
            frame_size = {"width": width, "height": height}
            self.frame_sizes.append(frame_size)
            self.frame_listbox.insert(tk.END, f"{width}x{height}")
            self.save_frame_sizes()
            self.update_select_frame_menu()

    def edit_frame_size(self):
        selected_index = self.frame_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            frame_size = self.frame_sizes[index]
            new_width = simpledialog.askinteger("แก้ไขความกว้าง", "กรุณาใส่ความกว้างใหม่:", initialvalue=frame_size["width"])
            new_height = simpledialog.askinteger("แก้ไขความสูง", "กรุณาใส่ความสูงใหม่:", initialvalue=frame_size["height"])
            
            if new_width and new_height:
                self.frame_sizes[index] = {"width": new_width, "height": new_height}
                self.frame_listbox.delete(index)
                self.frame_listbox.insert(index, f"{new_width}x{new_height}")
                self.save_frame_sizes()
                self.update_select_frame_menu()

    def delete_frame_size(self):
        selected_index = self.frame_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            self.frame_listbox.delete(index)
            del self.frame_sizes[index]
            self.save_frame_sizes()
            self.update_select_frame_menu()

if __name__ == "__main__":
    app = Application()
    app.mainloop()
