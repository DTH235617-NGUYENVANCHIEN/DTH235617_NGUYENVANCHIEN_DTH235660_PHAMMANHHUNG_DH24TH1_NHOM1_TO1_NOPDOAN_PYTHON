# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import sys
import os

# NÂNG CẤP: Import tất cả các file GUI
import quanli_nhanvien
import quanli_xe
import quanli_chuyendi
import quanli_lichsubaotri
import quanli_nhatkinguyenlieu
import quanli_taikhoan
import quanli_taixe 
import thongtin_canhan
import thongtin_taikhoan

# ================================================================
# BỘ MÀU "LIGHT MODE" (Đồng bộ với các file con)
# ================================================================
theme_colors = {
    "bg_main": "#F0F0F0",      # Nền chính (xám rất nhạt)
    "bg_entry": "#FFFFFF",     # Nền cho Entry, Treeview (trắng)
    "text": "#000000",         # Màu chữ chính (đen)
    "text_disabled": "#A0A0A0", # Màu chữ khi bị mờ
    "accent": "#0078D4",       # Màu nhấn (xanh dương)
    "accent_text": "#FFFFFF",   # Màu chữ trên nền màu nhấn (trắng)
    "accent_active": "#005A9E",  # Màu nhấn khi click
    "disabled_bg": "#E0E0E0"   # Nền khi bị mờ
}

# ================================================================
# CẤU HÌNH FONT CHỮ
# ================================================================
NAV_TITLE_FONT = ("Calibri", 13, "bold") 
NAV_BUTTON_FONT = ("Calibri", 12) 

# ================================================================
# CẤU HÌNH MÀU SẮC (SỬA LẠI: Nav-bar vẫn Dark, Content Light)
# ================================================================
# Thanh Nav bên trái (Vẫn giữ Dark Mode)
NAV_BG = theme_colors["bg_entry"] # Màu trắng (#FFFFFF)
NAV_FG = theme_colors["text"]     # Màu đen (#000000)
NAV_HOVER_BG = theme_colors["bg_main"]  # Màu xám siêu nhạt (#F0F0F0)
NAV_HOVER_FG = theme_colors["accent"]   # Màu xanh dương (#0078D4)
NAV_EXIT_FG = "red" # Giữ màu đỏ cho nút Thoát
NAV_DISABLED_FG = theme_colors["text_disabled"] # Màu xám nhạt (#A0A0A0)

# Khung Main bên phải (Chuyển sang Light Mode)
MAIN_BG = theme_colors["bg_main"] # Nền xám nhạt
MAIN_FG = theme_colors["text"] # Chữ đen
MAIN_FOOTER_FG = theme_colors["text_disabled"] # Chữ xám
SEPARATOR_COLOR = "#CCCCCC" # Viền xám sáng

# ================================================================
# LẤY VAI TRÒ (ROLE) TỪ LÚC ĐĂNG NHẬP
# ================================================================
try:
    USER_USERNAME = sys.argv[1] # <--- THÊM DÒNG NÀY
    USER_ROLE = sys.argv[2]     # <--- SỬA THÀNH sys.argv[2]
except IndexError:
    USER_USERNAME = "test_admin" # <--- THÊM (dùng để test)
    USER_ROLE = "Admin" 
    print("Không thấy vai trò, mặc định là Admin để test.")

print(f"Đang chạy Main Menu: User={USER_USERNAME}, Role={USER_ROLE}")

# ================================================================
# NÂNG CẤP: HÀM HIỂN THỊ TRANG
# ================================================================
current_page_frame = None 
current_active_button = None

def show_page(page_creator_func):
    """Xóa frame cũ và hiển thị frame mới trong main_frame."""
    global current_page_frame
    
    if current_page_frame:
        current_page_frame.destroy()
        
    # Truyền main_frame làm 'master' cho trang con
    current_page_frame = page_creator_func(main_frame)
    current_page_frame.pack(fill=tk.BOTH, expand=True)

def show_homepage():
    """Hiển thị lại trang chủ (Lời chào)."""
    global current_page_frame
    if current_page_frame:
        current_page_frame.destroy()
        current_page_frame = None 
    
    create_main_content(main_frame)
# ================================================================
# THIẾT KẾ GIAO DIỆN CHÍNH
# ================================================================

root = tk.Tk()
root.title(f"Hệ Thống Quản Lý Vận Tải (Vai trò: {USER_ROLE})")
root.state('zoomed') 
# NỀN CHÍNH CỦA ROOT LÀ NỀN LIGHT
root.configure(bg=MAIN_BG) 

# --- Thanh điều hướng bên trái (Vẫn giữ Dark) ---
left_nav_frame = tk.Frame(root, bg=NAV_BG, width=250)
left_nav_frame.pack(side=tk.LEFT, fill=tk.Y)
left_nav_frame.pack_propagate(False) 

# --- Viền Phân Cách (Màu sáng) ---
separator = tk.Frame(root, bg=SEPARATOR_COLOR, width=1)
separator.pack(side=tk.LEFT, fill=tk.Y)

# --- Khung nội dung chính (Nền sáng) ---
main_frame = tk.Frame(root, bg=MAIN_BG) 
main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# ================================================================
# THANH ĐIỀU HƯỚNG BÊN TRÁI (NAV BAR)
# (Giữ nguyên giao diện Dark cho Nav)
# ================================================================

title_btn = tk.Button(left_nav_frame,
                        text="HỆ THỐNG VẬN TẢI", 
                        font=NAV_TITLE_FONT, 
                        bg=NAV_BG, fg=NAV_FG, 
                        
                        # 1. Ra giữa
                        anchor="center", 
                        
                        padx=20,
                        relief="flat", borderwidth=0,
                        
                        # 2. Click-down (Nền không đổi, chữ xanh)
                        activebackground=NAV_BG, 
                        activeforeground=NAV_HOVER_FG,
                        
                        # 3. Active state (Select)
                        command=lambda: (show_homepage(), set_active_button(title_btn))
                       )

# 4. Hover (Nền không đổi, chữ xanh)
title_btn.bind("<Enter>", lambda e: e.widget.config(bg=NAV_BG, fg=NAV_HOVER_FG))
title_btn.bind("<Leave>", lambda e: e.widget.config(bg=NAV_BG, fg=NAV_FG))

# 5. Xuống tí (pady 30, 20)
title_btn.pack(side=tk.TOP, fill=tk.X, pady=(30, 20))

def create_nav_button(parent, text, icon, page_command_func):
    btn_text = f"  {icon}   {text}" 
    
    btn = tk.Button(parent, 
                        text=btn_text, 
                        font=NAV_BUTTON_FONT, 
                        bg=NAV_BG, fg=NAV_FG, 
                        relief="flat", borderwidth=0,
                        anchor="w", padx=20, pady=10,
                        activebackground=NAV_HOVER_BG, 
                        activeforeground=NAV_HOVER_FG, 
                        command=lambda: (page_command_func(), set_active_button(btn))
                   )
    
    btn.bind("<Enter>", lambda e: e.widget.config(bg=NAV_HOVER_BG, fg=NAV_HOVER_FG))
    btn.bind("<Leave>", lambda e: e.widget.config(bg=NAV_BG, fg=NAV_FG))
    
    btn.pack(side=tk.TOP, fill=tk.X, pady=2, padx=10) 
    return btn

# --- Tạo các nút (ĐÃ CẬP NHẬT HOÀN CHỈNH) ---
btn_thongtin = create_nav_button(left_nav_frame, "Thông tin cá nhân", "👤",
                            lambda: show_page(lambda master_frame:thongtin_canhan.create_page(master_frame, USER_USERNAME)))
btn_xe = create_nav_button(left_nav_frame, "Quản lý Xe", "🚗", 
                           lambda: show_page(quanli_xe.create_page))
btn_taixe = create_nav_button(left_nav_frame, "Quản lý Tài Xế", "👤", 
                             lambda: show_page(quanli_taixe.create_page))
btn_chuyendi = create_nav_button(left_nav_frame, "Quản lý Chuyến Đi", "🌐", 
    lambda: show_page(lambda master_frame: quanli_chuyendi.create_page(
        master_frame, 
        USER_ROLE, 
        USER_USERNAME
    ))
)
btn_baotri = create_nav_button(left_nav_frame, "Lịch sử Bảo Trì", "🔧", 
    lambda: show_page(quanli_lichsubaotri.create_page))
btn_nhienlieu = create_nav_button(left_nav_frame, "Nhật ký Nhiên Liệu", "🧾", 
    lambda: show_page(lambda master_frame: quanli_nhatkinguyenlieu.create_page(
        master_frame,
        USER_ROLE,
        USER_USERNAME
    ))
)
btn_taikhoan_user = create_nav_button(left_nav_frame, "Tài khoản", "⚙️", 
                            lambda: show_page(lambda master_frame: thongtin_taikhoan.create_page(
                                    master_frame, 
                                    master_frame.winfo_toplevel(), # Đây là cửa sổ 'root' chính
                                    USER_USERNAME, # Gửi tên đăng nhập
                                    USER_ROLE      # Gửi vai trò
                                ))
                        )
btn_taikhoan = create_nav_button(left_nav_frame, "Quản lý Tài Khoản", "🔑", 
                                 lambda: show_page(quanli_taikhoan.create_page))
btn_nhanvien = create_nav_button(left_nav_frame, "Quản lý Nhân Viên", "👥", 
                                 lambda: show_page(quanli_nhanvien.create_page)) 


# --- Nút Thoát (Dưới cùng) ---
btn_thoat = tk.Button(left_nav_frame, 
                        text="  ⏻   Thoát", 
                        font=NAV_BUTTON_FONT, 
                        bg=NAV_BG, fg=NAV_FG, 
                        relief="flat", borderwidth=0,
                        anchor="w", padx=20, pady=10,
                        activebackground=NAV_HOVER_BG, 
                        activeforeground=NAV_EXIT_FG, 
                        command=root.quit)

btn_thoat.bind("<Enter>", lambda e: e.widget.config(bg=NAV_HOVER_BG, fg=NAV_EXIT_FG)) 
btn_thoat.bind("<Leave>", lambda e: e.widget.config(bg=NAV_BG, fg=NAV_FG))
btn_thoat.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 20), padx=10) 

def reset_active_button():
    """Trả nút đang active về trạng thái bình thường."""
    global current_active_button
    if current_active_button:
        try:
            # Trả về màu nền/chữ gốc
            current_active_button.config(bg=NAV_BG, fg=NAV_FG) 
            
            if current_active_button == title_btn:
                # Gắn lại hover CHỮ (cho title_btn)
                current_active_button.bind("<Enter>", lambda e: e.widget.config(bg=NAV_BG, fg=NAV_HOVER_FG))
                current_active_button.bind("<Leave>", lambda e: e.widget.config(bg=NAV_BG, fg=NAV_FG))
            else:
                # Gắn lại hover NỀN (cho các nút khác)
                current_active_button.bind("<Enter>", lambda e: e.widget.config(bg=NAV_HOVER_BG, fg=NAV_HOVER_FG))
                current_active_button.bind("<Leave>", lambda e: e.widget.config(bg=NAV_BG, fg=NAV_FG))
        except tk.TclError:
            pass
    current_active_button = None

def set_active_button(button_widget):
    """Tô màu CHỮ của nút được chọn và gỡ hover."""
    global current_active_button
    
    # 1. Reset nút cũ trước
    reset_active_button()
    
    try:
        # ==================================
        # === SỬA MÀU TẠI ĐÂY ===
        # ==================================
        # Chỉ đổi MÀU CHỮ (fg) thành màu xanh (NAV_HOVER_FG)
        # Giữ nguyên MÀU NỀN (bg) là NAV_BG
        button_widget.config(bg=NAV_BG, fg=NAV_HOVER_FG) 
        
        # 3. Gỡ sự kiện di chuột để nó "dính" màu
        button_widget.unbind("<Enter>")
        button_widget.unbind("<Leave>")
        
        # 4. Lưu lại nút này là nút active
        current_active_button = button_widget
    except tk.TclError:
        pass

# ================================================================
# KHUNG NỘI DUNG CHÍNH (BÊN PHẢI) - SỬA SANG LIGHT MODE
# ================================================================

def create_main_content(parent):
    """Tạo nội dung gốc (Lời chào) cho main_frame."""
    # Frame này sẽ bị xóa khi show_page được gọi
    # SỬA: Dùng MAIN_BG (xám nhạt)
    home_frame = tk.Frame(parent, bg=MAIN_BG)
    
    lbl_title_main = tk.Label(home_frame, 
                             text="HỆ THỐNG VẬN TẢI", 
                             font=("Calibri", 24, "bold"),
                             bg=MAIN_BG, fg=MAIN_FG) # SỬA: Dùng biến
    lbl_title_main.pack(pady=(40, 20), fill='x', anchor='center')

    lbl_welcome_main = tk.Label(home_frame, 
                                text=f"Chào mừng {USER_ROLE}!", 
                                font=("Calibri", 16),
                                bg=MAIN_BG, fg=MAIN_FG) # SỬA: Dùng biến
    lbl_welcome_main.pack(pady=20, fill='x', expand=True, anchor='center')

    lbl_footer_main = tk.Label(home_frame, 
                              text="Phát triển bởi [Tên Nhóm Của Bạn]", 
                              font=("Calibri", 10),
                              bg=MAIN_BG, fg=MAIN_FOOTER_FG) # SỬA: Dùng biến
    lbl_footer_main.pack(pady=10, side=tk.BOTTOM, anchor='center')
    
    global current_page_frame
    current_page_frame = home_frame
    current_page_frame.pack(fill=tk.BOTH, expand=True) 

# ================================================================
# PHÂN QUYỀN (CẤU TRÚC MỚI DỄ MỞ RỘNG)
# ================================================================

def disable_button(btn):
    """Hàm tùy chỉnh để vô hiệu hóa tk.Button (vì 'state' làm xấu)."""
    btn.config(fg=NAV_DISABLED_FG, command=lambda: None) 
    btn.unbind("<Enter>")
    btn.unbind("<Leave>")

def apply_permissions(role):
    """
    Áp dụng phân quyền: Vô hiệu hóa các nút không thuộc vai trò (role) này.
    """
    
    # 1. Liệt kê TẤT CẢ các nút cần phân quyền
    all_buttons = {
        "thongtin": btn_thongtin,
        "xe": btn_xe,
        "taixe": btn_taixe,
        "chuyendi": btn_chuyendi,
        "baotri": btn_baotri,
        "nhienlieu": btn_nhienlieu,
        "taikhoan": btn_taikhoan,
        "nhanvien": btn_nhanvien,
        "taikhoan_user": btn_taikhoan_user
    }

    # 2. Định nghĩa vai trò nào được thấy nút nào
    permissions = {
        "Admin": [
            "xe", "taixe", "chuyendi", "baotri", 
            "nhienlieu", "taikhoan", "nhanvien"
        ],
        "TaiXe": [
            "thongtin", "chuyendi", "baotri", "nhienlieu", "taikhoan_user"
        ]
        # Thêm vai trò khác ở đây
    }

    # 3. Lấy danh sách các nút ĐƯỢC PHÉP của vai trò hiện tại
    allowed_keys = permissions.get(role, [])

    # 4. Duyệt qua TẤT CẢ các nút
    for key, button in all_buttons.items():
        if key not in allowed_keys:
            button.pack_forget()

# ================================================================
# CHẠY ỨNG DỤNG
# ================================================================
apply_permissions(USER_ROLE) # Áp dụng phân quyền
create_main_content(main_frame) # Tải trang chủ lần đầu
set_active_button(title_btn)
root.mainloop()