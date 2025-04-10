import tkinter as tk
from tkinter import Label, messagebox
from PIL import Image, ImageTk

class TroChoiTruyTimKhoBau:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Trò chơi truy tìm kho báu")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Ảnh nền ban đầu
        self.bg_image = Image.open("background1.jpg").resize((800, 600))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = Label(root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0)

        # Tạo các nút chính
        self.btn_batdau = self.create_button("▶ Bắt đầu", 540, 200, self.bat_dau)
        self.btn_huongdan = self.create_button("📜 Hướng dẫn", 540, 270, self.hien_huong_dan)
        self.btn_thanhtich = self.create_button("🏆 Thành tích", 540, 340, self.thanh_tich)

        # Khởi tạo hướng dẫn
        self.label_lines = []  # Lưu các dòng chữ hiển thị lên ảnh
        self.btn_thoat_huongdan = None

    def create_button(self, text, x, y, command):
        btn = tk.Button(self.root, text=text, font=("Helvetica", 16, "bold"),
                        bg="#f9cb9c", fg="black", activebackground="#f6b26b",
                        command=command, relief="raised", bd=3, cursor="hand2")
        btn.place(x=x, y=y, width=220, height=50)
        btn.bind("<Enter>", lambda e: btn.config(font=("Helvetica", 18, "bold")))
        btn.bind("<Leave>", lambda e: btn.config(font=("Helvetica", 16, "bold")))
        return btn

    def bat_dau(self):
        messagebox.showinfo("Bắt đầu", "Bạn đã bắt đầu chuyến phiêu lưu tìm kho báu!")

    def thanh_tich(self):
        messagebox.showinfo("Thành tích", "Hiện chưa có thành tích nào!")

    def hien_huong_dan(self):
        # Ẩn các nút chính
        self.btn_batdau.place_forget()
        self.btn_huongdan.place_forget()
        self.btn_thanhtich.place_forget()

        # Tạo Canvas nếu chưa có
        self.canvas = tk.Canvas(self.root, width=800, height=600, highlightthickness=0)
        self.canvas.place(x=0, y=0)

        # Hiển thị ảnh nền cuộn giấy
        self.bg_image = Image.open("guide.jpg").resize((800, 600))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

        # Nội dung hướng dẫn
        noi_dung = [
            "🧭 CHÀO MỪNG ĐẾN VỚI CHUYẾN PHIÊU LƯU TRUY TÌM KHO BÁU!",
            "⚓ Mục tiêu: Tìm ra kho báu bị ẩn dưới đáy biển.",
            "🦈 Tránh cá mập và các sinh vật nguy hiểm.",
            "🗺️ Thu thập vật phẩm và bản đồ rải rác khắp nơi.",
            "🏁 Hoàn thành nhiệm vụ để chiến thắng!",
            "🔙 Nhấn 'Thoát' để quay lại!"
        ]

        # Vẽ chữ lên ảnh
        y_start = 200
        for i, line in enumerate(noi_dung):
            text = self.canvas.create_text(400, y_start + i * 50,
                                        text=line,
                                        font=("Georgia", 14, "bold"),
                                        fill="black")
            self.label_lines.append(text)

        # Nút Thoát
        self.btn_thoat_huongdan = tk.Button(self.root, text="❌ Thoát", font=("Arial", 12, "bold"),
                                            bg="#ffb3b3", fg="black", activebackground="#ff6666",
                                            command=self.thoat_huong_dan, relief="raised", bd=3)
        self.btn_thoat_huongdan.place(x=620, y=500, width=100, height=40)

    def thoat_huong_dan(self):
        # Xóa canvas nếu có
        if hasattr(self, "canvas") and self.canvas:
            self.canvas.destroy()

        # Xóa nút Thoát
        if self.btn_thoat_huongdan:
            self.btn_thoat_huongdan.destroy()

        # Trở lại nền ban đầu
        self.bg_image = Image.open("background1.jpg").resize((800, 600))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_label.config(image=self.bg_photo)

        # Hiện lại các nút chính
        self.btn_batdau.place(x=540, y=200, width=220, height=50)
        self.btn_huongdan.place(x=540, y=270, width=220, height=50)
        self.btn_thanhtich.place(x=540, y=340, width=220, height=50)


# Chạy chương trình
if __name__ == "__main__":
    root = tk.Tk()
    app = TroChoiTruyTimKhoBau(root)
    root.mainloop()
