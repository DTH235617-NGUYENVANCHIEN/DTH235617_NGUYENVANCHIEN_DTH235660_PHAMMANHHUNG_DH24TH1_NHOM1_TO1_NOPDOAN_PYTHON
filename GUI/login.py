import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import subprocess
import sys
import os
import hashlib 
import utils
# ================================================================
# KẾT NỐI CSDL (Giữ nguyên)
# ================================================================


# ================================================================
# HÀM XỬ LÝ ĐĂNG NHẬP (Giữ nguyên)
# ================================================================

def hash_password(password):
    """Hàm băm mật khẩu bằng SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_login(event=None): # Thêm event=None để bắt sự kiện Enter
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Tên đăng nhập và Mật khẩu.")
        return

    # SỬA: Dùng hàm connect_db từ utils
    conn = utils.connect_db() 
    if conn is None:
        return

    try:
        cur = conn.cursor()
        sql = "SELECT MatKhau, VaiTro FROM TaiKhoan WHERE TenDangNhap = ?"
        cur.execute(sql, (username,))
        record = cur.fetchone()

        if record:
            # Tên đăng nhập ĐÚNG, kiểm tra mật khẩu
            db_hashed_password = record[0] 
            db_role = record[1]
            input_hashed_password = hash_password(password)
            
            if input_hashed_password == db_hashed_password:
                # MẬT KHẨU ĐÚNG
                messagebox.showinfo("Thành công", f"Đăng nhập thành công với vai trò: {db_role}")
                login_window.destroy()
                
                # SỬA QUAN TRỌNG: Truyền 'username' sang
                open_main_menu(username, db_role) 
            else:
                messagebox.showerror("Sai thông tin", "Sai Mật khẩu. Vui lòng thử lại.")
        
        else: 
            # Tên đăng nhập SAI
            messagebox.showerror("Sai thông tin", "Không tìm thấy Tên đăng nhập.")

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Lỗi truy vấn:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def open_main_menu(username, role):
    """
    Hàm này chạy file main.py và truyền vai trò (role) vào.
    """
    print(f"Mở Main Menu: User={username}, Role={role}")
    
    python_executable = sys.executable
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_menu_path = os.path.join(current_dir, "main.py") 

    if not os.path.exists(main_menu_path):
        messagebox.showerror("Lỗi", "Không tìm thấy file: main.py")
        return

    try:
        subprocess.Popen([python_executable, main_menu_path, username, role])
    except Exception as e:
        messagebox.showerror("Lỗi khi mở Main Menu", f"Không thể khởi chạy main.py:\n{e}")

# ================================================================
# THIẾT KẾ GIAO DIỆN ĐĂNG NHẬP (HIỆN ĐẠI)
# ================================================================

# --- Cấu hình màu sắc & font chữ ---
COLOR_PRIMARY = "#0078D7"  # Xanh dương
COLOR_LIGHT_BLUE = "#E0EFFF"
COLOR_DARK_BLUE = "#005a9e"
COLOR_WHITE = "#ffffff"
COLOR_BLACK = "#1f1f1f"
COLOR_GREY = "#a0a0a0"
COLOR_LIGHT_GREY = "#f0f0f0"

FONT_BIG = ("Arial", 24, "bold")
FONT_MEDIUM = ("Arial", 14, "bold")
FONT_NORMAL = ("Arial", 12)
FONT_NORMAL_BOLD = ("Arial", 12, "bold")

# --- Cửa sổ chính ---
login_window = tk.Tk()
login_window.title("Đăng nhập - Hệ thống Quản lý Vận tải")

# Căn giữa cửa sổ (Lớn hơn)
w = 700
h = 450
ws = login_window.winfo_screenwidth()
hs = login_window.winfo_screenheight()
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
login_window.geometry('%dx%d+%d+%d' % (w, h, x, y))
login_window.resizable(False, False)
login_window.configure(bg=COLOR_WHITE)

# --- Bố cục 2 cột ---
login_window.grid_columnconfigure(0, weight=2) # Cột trái
login_window.grid_columnconfigure(1, weight=3) # Cột phải
login_window.grid_rowconfigure(0, weight=1)

# --- CỘT TRÁI (Graphic) ---
left_frame = tk.Frame(login_window, bg=COLOR_PRIMARY)
left_frame.grid(row=0, column=0, sticky="nsew")
left_frame.pack_propagate(False) # Ngăn co lại

# Các widget trong cột trái
tk.Label(left_frame, text="🚛", font=("Arial", 100), bg=COLOR_PRIMARY, fg=COLOR_WHITE).pack(pady=(80, 0)) 
tk.Label(left_frame, text="HỆ THỐNG", font=("Arial", 20), bg=COLOR_PRIMARY, fg=COLOR_WHITE).pack()

# === SỬA LỖI HIỂN THỊ TẠI ĐÂY ===
tk.Label(left_frame, text="QUẢN LÝ\nVẬN TẢI", font=FONT_BIG, bg=COLOR_PRIMARY, fg=COLOR_WHITE, justify=tk.CENTER).pack() # Thêm \n
# ===============================

tk.Label(left_frame, text="Đăng nhập để tiếp tục", font=FONT_NORMAL, bg=COLOR_PRIMARY, fg=COLOR_LIGHT_BLUE).pack(pady=10)


# --- CỘT PHẢI (Form) ---
right_frame = tk.Frame(login_window, bg=COLOR_WHITE, padx=50, pady=50)
right_frame.grid(row=0, column=1, sticky="nsew")

# Tiêu đề
tk.Label(right_frame, text="ĐĂNG NHẬP", font=FONT_BIG, bg=COLOR_WHITE, fg=COLOR_BLACK).pack(pady=(30, 20))

# --- Ô Tên đăng nhập ---
tk.Label(right_frame, text="Tên đăng nhập", font=FONT_NORMAL, bg=COLOR_WHITE, fg=COLOR_BLACK, anchor="w").pack(fill="x", pady=(10,0))
entry_username = tk.Entry(right_frame, font=FONT_MEDIUM, bg=COLOR_LIGHT_GREY, bd=0, relief="flat", insertbackground=COLOR_BLACK)
entry_username.pack(fill="x", ipady=8, pady=(5, 10)) # ipady = padding bên trong

# --- Ô Mật khẩu ---
tk.Label(right_frame, text="Mật khẩu", font=FONT_NORMAL, bg=COLOR_WHITE, fg=COLOR_BLACK, anchor="w").pack(fill="x", pady=(10,0))
entry_password = tk.Entry(right_frame, font=FONT_MEDIUM, bg=COLOR_LIGHT_GREY, bd=0, relief="flat", show="*", insertbackground=COLOR_BLACK)
entry_password.pack(fill="x", ipady=8, pady=(5, 20)) # ipady = padding bên trong

# --- Nút đăng nhập ---
btn_login = tk.Button(right_frame, 
                      text="Đăng nhập", 
                      font=FONT_NORMAL_BOLD,
                      bg=COLOR_PRIMARY,
                      fg=COLOR_WHITE,
                      activebackground=COLOR_DARK_BLUE,
                      activeforeground=COLOR_WHITE,
                      relief="flat",
                      bd=0,
                      pady=10,
                      cursor="hand2", # Con trỏ hình bàn tay
                      command=check_login)
btn_login.pack(fill="x")

# --- Hiệu ứng Hover cho nút ---
def on_btn_enter(e):
    e.widget.config(background=COLOR_DARK_BLUE)
def on_btn_leave(e):
    e.widget.config(background=COLOR_PRIMARY)

btn_login.bind("<Enter>", on_btn_enter)
btn_login.bind("<Leave>", on_btn_leave)

# Bắt sự kiện nhấn Enter
login_window.bind('<Return>', check_login)

# Đặt focus vào ô username
entry_username.focus()

login_window.mainloop()