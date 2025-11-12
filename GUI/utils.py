# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

# ================================================================
# BỘ MÀU DÙNG CHUNG
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
# HÀM KẾT NỐI CSDL DÙNG CHUNG
# ================================================================
def connect_db():
    """Hàm kết nối đến CSDL SQL Server."""
    try:
        conn_string = (
            r'DRIVER={SQL Server};'
            r'SERVER=LAPTOP-MKC70SQE\SQLEXPRESS;' # Giữ nguyên server của bạn
            r'DATABASE=QL_VanTai;'
            r'Trusted_Connection=yes;' 
        )
        conn = pyodbc.connect(conn_string)
        return conn
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi kết nối CSDL", f"Không thể kết nối đến SQL Server:\n{e}")
        return None
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
        return None

# ================================================================
# HÀM THIẾT KẾ GIAO DIỆN DÙNG CHUNG
# ================================================================
def setup_theme(master_widget):
    """
    Áp dụng toàn bộ theme Light Mode (ttk) cho một widget cha (master).
    'master_widget' có thể là 'root' (khi test) hoặc 'page_frame' (khi chạy thật).
    """
    
    style = ttk.Style(master_widget)
    style.theme_use("clam") 

    # --- Cấu hình chung ---
    style.configure(".", 
        background=theme_colors["bg_main"],
        foreground=theme_colors["text"],
        fieldbackground=theme_colors["bg_entry"],
        bordercolor="#ACACAC", 
        lightcolor=theme_colors["bg_main"],
        darkcolor=theme_colors["bg_main"]
    )
    style.configure("TFrame", background=theme_colors["bg_main"])
    style.configure("TLabel", 
        background=theme_colors["bg_main"],
        foreground=theme_colors["text"],
        font=("Segoe UI", 10)
    )
    style.configure("Title.TLabel", 
        background=theme_colors["bg_main"],
        foreground=theme_colors["accent"], 
        font=("Segoe UI", 20, "bold")
    )
    style.configure("Header.TLabel", 
        background=theme_colors["bg_main"],
        foreground=theme_colors["text"], 
        font=("Segoe UI", 11, "bold")
    )
    style.configure("TEntry",
        font=("Segoe UI", 10),
        fieldbackground=theme_colors["bg_entry"],
        foreground=theme_colors["text"],
        insertcolor=theme_colors["text"] 
    )
    style.map("TEntry",
        fieldbackground=[('disabled', theme_colors["disabled_bg"])],
        foreground=[('disabled', theme_colors["text_disabled"])]
    )
    style.configure("TCombobox",
        font=("Segoe UI", 10),
        fieldbackground=theme_colors["bg_entry"],
        background=theme_colors["bg_entry"],
        foreground=theme_colors["text"]
    )
    
    # Lấy cửa sổ root (Tk hoặc Toplevel) từ widget
    root_window = master_widget.winfo_toplevel()
    root_window.option_add("*TCombobox*Listbox*background", theme_colors["bg_entry"])
    root_window.option_add("*TCombobox*Listbox*foreground", theme_colors["text"])
    root_window.option_add("*TCombobox*Listbox*selectBackground", theme_colors["accent"])
    root_window.option_add("*TCombobox*Listbox*selectForeground", theme_colors["accent_text"])
    
    style.map("TCombobox",
        fieldbackground=[('disabled', theme_colors["disabled_bg"])],
        foreground=[('disabled', theme_colors["text_disabled"])]
    )
    style.configure("TButton",
        background=theme_colors["accent"],
        foreground=theme_colors["accent_text"],
        font=("Segoe UI", 10, "bold"),
        padding=5,
        relief="flat",
        bordercolor=theme_colors["accent"]
    )
    style.map("TButton",
        background=[('active', theme_colors["accent_active"])] 
    )
    style.configure("Treeview",
        background=theme_colors["bg_entry"],
        foreground=theme_colors["text"],
        fieldbackground=theme_colors["bg_entry"],
        rowheight=25, 
        font=("Segoe UI", 10)
    )
    style.map("Treeview",
        background=[('selected', theme_colors["accent"])], 
        foreground=[('selected', theme_colors["accent_text"])]
    )
    style.configure("Treeview.Heading",
        background=theme_colors["accent"],
        foreground=theme_colors["accent_text"],
        font=("Segoe UI", 10, "bold"),
        relief="flat"
    )
    style.map("Treeview.Heading",
        background=[('active', theme_colors["accent_active"])]
    )
    style.configure("Vertical.TScrollbar", 
        background=theme_colors["bg_entry"],
        troughcolor=theme_colors["bg_main"],
        arrowcolor=theme_colors["text"]
    )
    style.map("Vertical.TScrollbar",
        background=[('active', "#C0C0C0")]
    )
    style.configure("Horizontal.TScrollbar", 
        background=theme_colors["bg_entry"],
        troughcolor=theme_colors["bg_main"],
        arrowcolor=theme_colors["text"]
    )
    style.map("Horizontal.TScrollbar",
        background=[('active', "#C0C0C0")]
    )


# ================================================================
# HÀM TẢI COMBOBOX DÙNG CHUNG (BẠN CẦN THÊM MỚI PHẦN NÀY)
# ================================================================

def load_xe_combobox():
    """Tải danh sách Biển Số Xe cho combobox."""
    conn = connect_db() # Gọi hàm kết nối ở trên
    if conn is None:
        return []
    try:
        cur = conn.cursor()
        cur.execute("SELECT BienSoXe FROM Xe ORDER BY BienSoXe")
        rows = cur.fetchall()
        # Chuyển đổi danh sách các tuple [('51A-123'),] thành ['51A-123']
        return [row[0] for row in rows]
    except Exception as e:
        messagebox.showerror("Lỗi tải Combobox Xe", f"Lỗi SQL: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

# (Nằm trong file utils.py)

def load_taixe_combobox():
    """Tải danh sách Tài xế (MaNhanVien - HoVaTen) cho combobox."""
    conn = connect_db() # Gọi hàm kết nối ở trên
    if conn is None:
        return []
    try:
        cur = conn.cursor()
        
        # === SỬA LẠI CÂU SQL NHƯ SAU ===
        # Chúng ta JOIN NhanVien (để lấy tên) với TaiKhoan (để lọc VaiTro)
        sql_query = """
            SELECT nv.MaNhanVien, nv.HoVaTen 
            FROM NhanVien AS nv
            INNER JOIN TaiKhoan AS tk ON nv.MaNhanVien = tk.MaNhanVien
            WHERE tk.VaiTro = N'TaiXe'
            ORDER BY nv.HoVaTen
        """
        # =================================
        
        cur.execute(sql_query)
        rows = cur.fetchall()
        # Định dạng lại thành: ['NV001 - Nguyễn Văn A', 'NV002 - Trần Thị B']
        return [f"{row[0]} - {row[1]}" for row in rows]
        
    except Exception as e:
        messagebox.showerror("Lỗi tải Combobox Tài xế", f"Lỗi SQL: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def load_nhanvien_combobox():
    """Tải TOÀN BỘ Nhân Viên (MaNhanVien - HoVaTen) cho combobox."""
    conn = connect_db() # Gọi hàm kết nối ở trên
    if conn is None:
        return []
    try:
        cur = conn.cursor()
        
        # Tải tất cả nhân viên (kể cả Admin và Tài xế)
        cur.execute("""
            SELECT MaNhanVien, HoVaTen 
            FROM NhanVien 
            ORDER BY HoVaTen
        """)
        
        rows = cur.fetchall()
        # Định dạng lại thành: ['AD001 - Trần Văn Quản Trị', 'NV001 - Nguyễn Văn A']
        return [f"{row[0]} - {row[1]}" for row in rows]
        
    except Exception as e:
        messagebox.showerror("Lỗi tải Combobox Nhân Viên", f"Lỗi SQL: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()