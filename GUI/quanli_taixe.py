# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc # <-- GIỮ LẠI ĐỂ BẮT LỖI
import utils # <-- IMPORT FILE DÙNG CHUNG
from datetime import datetime
import datetime as dt

# ================================================================
# BỘ MÀU "LIGHT MODE"
# (ĐÃ XÓA - Chuyển sang utils.py)
# ================================================================

# ================================================================
# PHẦN 1: KẾT NỐI CSDL
# (ĐÃ XÓA - Chuyển sang utils.py)
# ================================================================

# ================================================================
# PHẦN 2: CÁC HÀM TIỆN ÍCH (Tải Combobox)
# (ĐÃ XÓA - Chuyển sang utils.py)
# ================================================================

# ================================================================
# PHẦN 3: CÁC HÀM CRUD
# (Đã sửa để nhận 'widgets' và dùng utils.connect_db())
# ================================================================

def set_form_state(is_enabled, widgets):
    """Bật (enable) hoặc Tắt (disable) toàn bộ các trường nhập liệu."""
    if is_enabled:
        widgets['entry_hoten'].config(state='normal')
        widgets['entry_sdt'].config(state='normal')
        widgets['entry_diachi'].config(state='normal')
        widgets['entry_banglai'].config(state='normal')
        widgets['date_banglai'].config(state='normal')
        widgets['cbb_trangthai_nv'].config(state='readonly')
        widgets['cbb_trangthai_lx'].config(state='readonly')
    else:
        widgets['entry_manv'].config(state='disabled')
        widgets['entry_hoten'].config(state='disabled')
        widgets['entry_sdt'].config(state='disabled')
        widgets['entry_diachi'].config(state='disabled')
        widgets['entry_banglai'].config(state='disabled')
        widgets['date_banglai'].config(state='disabled')
        widgets['cbb_trangthai_nv'].config(state='disabled')
        widgets['cbb_trangthai_lx'].config(state='disabled')

def clear_input(widgets):
    """(NÚT THÊM) Xóa trắng và Mở khóa các trường nhập liệu (Chế độ Thêm mới)."""
    set_form_state(is_enabled=True, widgets=widgets)
    widgets['entry_manv'].config(state='normal') 
    
    widgets['entry_manv'].delete(0, tk.END)
    widgets['entry_hoten'].delete(0, tk.END)
    widgets['entry_sdt'].delete(0, tk.END)
    widgets['entry_diachi'].delete(0, tk.END)
    widgets['entry_banglai'].delete(0, tk.END)
    
    widgets['date_banglai'].set_date("2025-01-01")
    widgets['cbb_trangthai_nv'].set("Đang làm việc")
    widgets['cbb_trangthai_lx'].set("Rảnh")
    
    widgets['entry_manv'].focus()
    tree = widgets['tree']
    if tree.selection():
        tree.selection_remove(tree.selection()[0])

def load_data(widgets):
    """Tải TOÀN BỘ dữ liệu tài xế (JOIN) VÀ LÀM MỜ FORM."""
    tree = widgets['tree']
    for i in tree.get_children():
        tree.delete(i)
        
    conn = utils.connect_db() # <-- SỬA
    if conn is None:
        set_form_state(is_enabled=False, widgets=widgets) 
        return
        
    try:
        cur = conn.cursor()
        sql = """
        SELECT 
            nv.MaNhanVien, nv.HoVaTen, nv.SoDienThoai, 
            tx.HangBangLai, nv.TrangThai, tx.TrangThaiTaiXe
        FROM NhanVien AS nv
        JOIN TaiXe AS tx ON nv.MaNhanVien = tx.MaNhanVien
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        for row in rows:
            trang_thai_nv_text = "Đang làm việc" if row[4] == 1 else "Nghỉ"
            trang_thai_lx_text = "Rảnh" if row[5] == 1 else "Đang lái"
            
            tree.insert("", tk.END, values=(
                row[0], row[1], row[2], row[3], 
                trang_thai_nv_text, trang_thai_lx_text
            ))
        
        children = tree.get_children()
        if children:
            first_item = children[0]
            tree.selection_set(first_item) 
            tree.focus(first_item)         
            tree.event_generate("<<TreeviewSelect>>") 
        else:
            widgets['entry_manv'].config(state='normal')
            set_form_state(is_enabled=True, widgets=widgets)
            widgets['entry_manv'].delete(0, tk.END)
            widgets['entry_hoten'].delete(0, tk.END)
            widgets['entry_sdt'].delete(0, tk.END)
            widgets['entry_diachi'].delete(0, tk.END)
            widgets['entry_banglai'].delete(0, tk.END)
            widgets['date_banglai'].set_date("2025-01-01")
            widgets['cbb_trangthai_nv'].set("Đang làm việc")
            widgets['cbb_trangthai_lx'].set("Rảnh")
            
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()
        set_form_state(is_enabled=False, widgets=widgets)

def them_taixe(widgets):
    """(LOGIC THÊM) Thêm một tài xế mới (vào cả 2 bảng NhanVien và TaiXe)."""
    manv = widgets['entry_manv'].get()
    hoten = widgets['entry_hoten'].get()
    sdt = widgets['entry_sdt'].get()
    diachi = widgets['entry_diachi'].get()
    banglai = widgets['entry_banglai'].get()
    ngay_bl = widgets['date_banglai'].get_date().strftime('%Y-%m-%d')
    
    trangthai_nv_text = widgets['cbb_trangthai_nv_var'].get()
    trangthai_nv_value = 1 if trangthai_nv_text == "Đang làm việc" else 0
    
    trangthai_lx_text = widgets['cbb_trangthai_lx_var'].get()
    trangthai_lx_value = 1 if trangthai_lx_text == "Rảnh" else 2 

    if not manv or not hoten or not banglai:
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Mã NV, Họ Tên và Hạng Bằng Lái")
        return False

    conn = utils.connect_db() # <-- SỬA
    if conn is None: return False

    try:
        cur = conn.cursor()
        
        sql_nhanvien = "INSERT INTO NhanVien (MaNhanVien, HoVaTen, SoDienThoai, DiaChi, TrangThai) VALUES (?, ?, ?, ?, ?)"
        cur.execute(sql_nhanvien, (manv, hoten, sdt, diachi, trangthai_nv_value))
        
        sql_taixe = "INSERT INTO TaiXe (MaNhanVien, HangBangLai, NgayHetHanBangLai, TrangThaiTaiXe) VALUES (?, ?, ?, ?)"
        cur.execute(sql_taixe, (manv, banglai, ngay_bl, trangthai_lx_value))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm tài xế mới thành công")
        return True
        
    except pyodbc.IntegrityError:
        conn.rollback()
        messagebox.showerror("Lỗi Trùng lặp", f"Mã nhân viên '{manv}' đã tồn tại.")
        return False
    except pyodbc.Error as e:
        conn.rollback() 
        messagebox.showerror("Lỗi SQL", f"Không thể thêm tài xế:\n{str(e)}")
        return False
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
        return False
    finally:
        if conn: conn.close()

def on_item_select(event, widgets):
    """(SỰ KIỆN CLICK) Khi click vào Treeview, đổ dữ liệu đầy đủ lên form (ở trạng thái mờ)."""
    tree = widgets['tree']
    selected = tree.selection()
    if not selected: return 

    selected_item = tree.item(selected[0])
    manv = selected_item['values'][0]
    
    conn = utils.connect_db() # <-- SỬA
    if conn is None: return

    try:
        cur = conn.cursor()
        sql = "SELECT * FROM NhanVien nv JOIN TaiXe tx ON nv.MaNhanVien = tx.MaNhanVien WHERE nv.MaNhanVien = ?"
        cur.execute(sql, (manv,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu tài xế.")
            return

        set_form_state(is_enabled=True, widgets=widgets)
        widgets['entry_manv'].config(state='normal')
        
        # Xóa
        widgets['entry_manv'].delete(0, tk.END)
        widgets['entry_hoten'].delete(0, tk.END)
        widgets['entry_sdt'].delete(0, tk.END)
        widgets['entry_diachi'].delete(0, tk.END)
        widgets['entry_banglai'].delete(0, tk.END)
        
        # Điền
        widgets['entry_manv'].insert(0, data.MaNhanVien)
        widgets['entry_hoten'].insert(0, data.HoVaTen or "")
        widgets['entry_sdt'].insert(0, data.SoDienThoai or "")
        widgets['entry_diachi'].insert(0, data.DiaChi or "")
        widgets['cbb_trangthai_nv'].set("Đang làm việc" if data.TrangThai == 1 else "Nghỉ")
        widgets['entry_banglai'].insert(0, data.HangBangLai or "")
        if data.NgayHetHanBangLai:
            widgets['date_banglai'].set_date(data.NgayHetHanBangLai)
        else:
            widgets['date_banglai'].set_date("2025-01-01")
        widgets['cbb_trangthai_lx'].set("Rảnh" if data.TrangThaiTaiXe == 1 else "Đang lái")

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể lấy dữ liệu tài xế:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()
        set_form_state(is_enabled=False, widgets=widgets)

def chon_taixe_de_sua(widgets): 
    """(NÚT SỬA) Kích hoạt chế độ sửa, Mở khóa form (trừ MaNV)."""
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một tài xế trong danh sách trước khi nhấn 'Sửa'")
        return

    if not widgets['entry_manv'].get():
         messagebox.showwarning("Lỗi", "Không tìm thấy mã nhân viên. Vui lòng chọn lại.")
         return

    set_form_state(is_enabled=True, widgets=widgets)
    widgets['entry_manv'].config(state='disabled') 
    widgets['entry_hoten'].focus() 

def luu_taixe_da_sua(widgets):
    """(LOGIC SỬA) Lưu thay đổi (UPDATE) sau khi sửa (vào cả 2 bảng)."""
    manv = widgets['entry_manv'].get()
    if not manv:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã Nhân Viên để cập nhật")
        return False

    hoten = widgets['entry_hoten'].get()
    sdt = widgets['entry_sdt'].get()
    diachi = widgets['entry_diachi'].get()
    banglai = widgets['entry_banglai'].get()
    ngay_bl = widgets['date_banglai'].get_date().strftime('%Y-%m-%d')
    
    trangthai_nv_text = widgets['cbb_trangthai_nv_var'].get()
    trangthai_nv_value = 1 if trangthai_nv_text == "Đang làm việc" else 0
    
    trangthai_lx_text = widgets['cbb_trangthai_lx_var'].get()
    trangthai_lx_value = 1 if trangthai_lx_text == "Rảnh" else 2 

    if not hoten or not banglai:
        messagebox.showwarning("Thiếu dữ liệu", "Họ Tên và Hạng Bằng Lái không được rỗng")
        return False

    conn = utils.connect_db() # <-- SỬA
    if conn is None: return False
        
    try:
        cur = conn.cursor()
        
        sql_nhanvien = "UPDATE NhanVien SET HoVaTen = ?, SoDienThoai = ?, DiaChi = ?, TrangThai = ? WHERE MaNhanVien = ?"
        cur.execute(sql_nhanvien, (hoten, sdt, diachi, trangthai_nv_value, manv))
        
        sql_taixe = "UPDATE TaiXe SET HangBangLai = ?, NgayHetHanBangLai = ?, TrangThaiTaiXe = ? WHERE MaNhanVien = ?"
        cur.execute(sql_taixe, (banglai, ngay_bl, trangthai_lx_value, manv))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật thông tin tài xế")
        return True
        
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật tài xế:\n{str(e)}")
        return False
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
        return False
    finally:
        if conn: conn.close()

def save_data(widgets):
    """Lưu dữ liệu, tự động kiểm tra xem nên Thêm mới (INSERT) hay Cập nhật (UPDATE)."""
    if widgets['entry_manv'].cget('state') == 'disabled':
        success = luu_taixe_da_sua(widgets)
    else:
        success = them_taixe(widgets)
    
    if success:
        load_data(widgets) 

def xoa_taixe_vinhvien(widgets):
    """(NGUY HIỂM) Xóa vĩnh viễn tài xế và MỌI DỮ LIỆU LIÊN QUAN."""
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một tài xế trong danh sách để xóa")
        return
        
    manv = widgets['entry_manv'].get() 

    if not manv:
        messagebox.showwarning("Lỗi", "Không tìm thấy mã nhân viên. Vui lòng chọn lại.")
        return

    msg_xacnhan = (
        f"BẠN CÓ CHẮC CHẮN MUỐN XÓA VĨNH VIỄN TÀI XẾ '{manv}'?\n\n"
        "CẢNH BÁO: Thao tác này KHÔNG THỂ hoàn tác.\n"
        "Tất cả Lịch sử chuyến đi, Lịch sử nhiên liệu, Tài khoản, và thông tin Tài xế/Nhân viên sẽ bị XÓA SẠCH."
    )
    if not messagebox.askyesno("XÁC NHẬN XÓA VĨNH VIỄN", msg_xacnhan):
        return

    conn = utils.connect_db() # <-- SỬA
    if conn is None: return
        
    try:
        cur = conn.cursor()
        
        cur.execute("DELETE FROM NhatKyNhienLieu WHERE MaNhanVien=?", (manv,))
        cur.execute("DELETE FROM ChuyenDi WHERE MaNhanVien=?", (manv,))
        cur.execute("DELETE FROM TaiKhoan WHERE MaNhanVien=?", (manv,))
        cur.execute("DELETE FROM TaiXe WHERE MaNhanVien=?", (manv,))
        cur.execute("UPDATE Xe SET MaNhanVienHienTai = NULL WHERE MaNhanVienHienTai = ?", (manv,))
        cur.execute("DELETE FROM NhanVien WHERE MaNhanVien=?", (manv,))
        
        conn.commit()
        
        messagebox.showinfo("Thành công", f"Đã xóa vĩnh viễn tài xế '{manv}' và tất cả dữ liệu liên quan.")
        load_data(widgets)
        
    except pyodbc.Error as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể xóa tài xế:\n{str(e)}")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()

# ================================================================
# PHẦN 4: HÀM TẠO TRANG (HÀM CHÍNH ĐỂ MAIN.PY GỌI)
# ================================================================

def create_page(master):
    """
    Hàm này được main.py gọi. 
    Nó tạo ra toàn bộ nội dung trang và đặt vào 'master' (là main_frame).
    """
    
    # 1. TẠO FRAME CHÍNH
    page_frame = ttk.Frame(master, style="TFrame")
    
    # === CÀI ĐẶT STYLE (CHỈ CẦN 1 DÒNG) ===
    utils.setup_theme(page_frame) 
    # ==================================

    
    # 2. TẠO GIAO DIỆN (ĐẶT VÀO 'page_frame')
    lbl_title = ttk.Label(page_frame, text="QUẢN LÝ TÀI XẾ", style="Title.TLabel")
    lbl_title.pack(pady=15) 

    frame_info = ttk.Frame(page_frame, style="TFrame")
    frame_info.pack(pady=5, padx=20, fill="x")

    # --- Cột 1 ---
    ttk.Label(frame_info, text="Mã nhân viên:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
    entry_manv = ttk.Entry(frame_info, width=30)
    entry_manv.grid(row=0, column=1, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Họ và tên:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
    entry_hoten = ttk.Entry(frame_info, width=30)
    entry_hoten.grid(row=1, column=1, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Số điện thoại:").grid(row=2, column=0, padx=5, pady=8, sticky="w")
    entry_sdt = ttk.Entry(frame_info, width=30)
    entry_sdt.grid(row=2, column=1, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Địa chỉ:").grid(row=3, column=0, padx=5, pady=8, sticky="w")
    entry_diachi = ttk.Entry(frame_info, width=30)
    entry_diachi.grid(row=3, column=1, padx=5, pady=8, sticky="w")

    # --- Cột 2 ---
    ttk.Label(frame_info, text="Hạng bằng lái:").grid(row=0, column=2, padx=15, pady=8, sticky="w")
    entry_banglai = ttk.Entry(frame_info, width=30)
    entry_banglai.grid(row=0, column=3, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Ngày hết hạn BL:").grid(row=1, column=2, padx=15, pady=8, sticky="w")
    date_banglai = DateEntry(frame_info, width=28, date_pattern='yyyy-MM-dd',
        background=utils.theme_colors["bg_entry"], 
        foreground=utils.theme_colors["text"],
        disabledbackground=utils.theme_colors["disabled_bg"],
        disabledforeground=utils.theme_colors["text_disabled"],
        bordercolor=utils.theme_colors["bg_entry"],
        headersbackground=utils.theme_colors["accent"],
        headersforeground=utils.theme_colors["accent_text"],
        selectbackground=utils.theme_colors["accent"],
        selectforeground=utils.theme_colors["accent_text"]
    )
    date_banglai.grid(row=1, column=3, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Trạng thái NV:").grid(row=2, column=2, padx=15, pady=8, sticky="w")
    trangthai_nv_options = ["Nghỉ", "Đang làm việc"]
    cbb_trangthai_nv_var = tk.StringVar()
    cbb_trangthai_nv = ttk.Combobox(frame_info, textvariable=cbb_trangthai_nv_var, values=trangthai_nv_options, width=28, state='readonly')
    cbb_trangthai_nv.grid(row=2, column=3, padx=5, pady=8, sticky="w")
    cbb_trangthai_nv.set("Đang làm việc") 

    ttk.Label(frame_info, text="Trạng thái Lái:").grid(row=3, column=2, padx=15, pady=8, sticky="w")
    trangthai_lx_options = ["Rảnh", "Đang lái"]
    cbb_trangthai_lx_var = tk.StringVar()
    cbb_trangthai_lx = ttk.Combobox(frame_info, textvariable=cbb_trangthai_lx_var, values=trangthai_lx_options, width=28, state='readonly')
    cbb_trangthai_lx.grid(row=3, column=3, padx=5, pady=8, sticky="w")
    cbb_trangthai_lx.set("Rảnh") 

    frame_info.columnconfigure(1, weight=1)
    frame_info.columnconfigure(3, weight=1)

    # ===== Frame nút (SỬA LỖI: Đưa lên TRƯỚC Bảng) =====
    frame_btn = ttk.Frame(page_frame, style="TFrame")
    frame_btn.pack(pady=10)

    # ===== Bảng danh sách tài xế (SỬA LỖI: Đưa xuống DƯỚI nút) =====
    lbl_ds = ttk.Label(page_frame, text="Danh sách tài xế", style="Header.TLabel")
    lbl_ds.pack(pady=(10, 5), padx=20, anchor="w")

    frame_tree = ttk.Frame(page_frame, style="TFrame")
    frame_tree.pack(pady=10, padx=20, fill="both", expand=True) # expand=True ở cuối

    scrollbar_y = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, style="Vertical.TScrollbar")
    scrollbar_x = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, style="Horizontal.TScrollbar")

    columns = ("manv", "hoten", "sdt", "banglai", "trangthai_nv", "trangthai_lx")
    tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                        yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

    tree.heading("manv", text="Mã NV")
    tree.column("manv", width=80, anchor="center")
    tree.heading("hoten", text="Họ Tên")
    tree.column("hoten", width=150)
    tree.heading("sdt", text="Số điện thoại")
    tree.column("sdt", width=120)
    tree.heading("banglai", text="Hạng Bằng Lái")
    tree.column("banglai", width=100, anchor="center")
    tree.heading("trangthai_nv", text="Trạng thái NV")
    tree.column("trangthai_nv", width=120, anchor="center")
    tree.heading("trangthai_lx", text="Trạng thái Lái")
    tree.column("trangthai_lx", width=120, anchor="center")

    tree.pack(fill="both", expand=True)
    
    # 3. TẠO TỪ ĐIỂN 'widgets'
    widgets = {
        "tree": tree,
        "entry_manv": entry_manv,
        "entry_hoten": entry_hoten,
        "entry_sdt": entry_sdt,
        "entry_diachi": entry_diachi,
        "entry_banglai": entry_banglai,
        "date_banglai": date_banglai,
        "cbb_trangthai_nv": cbb_trangthai_nv,
        "cbb_trangthai_lx": cbb_trangthai_lx,
        "cbb_trangthai_nv_var": cbb_trangthai_nv_var,
        "cbb_trangthai_lx_var": cbb_trangthai_lx_var
    }

    # (Code tạo nút bây giờ nằm trong frame_btn ở trên)
    btn_them = ttk.Button(frame_btn, text="Thêm", width=8, command=lambda: clear_input(widgets)) 
    btn_them.grid(row=0, column=0, padx=10)
    btn_luu = ttk.Button(frame_btn, text="Lưu", width=8, command=lambda: save_data(widgets)) 
    btn_luu.grid(row=0, column=1, padx=10)
    btn_sua = ttk.Button(frame_btn, text="Sửa", width=8, command=lambda: chon_taixe_de_sua(widgets)) 
    btn_sua.grid(row=0, column=2, padx=10)
    btn_huy = ttk.Button(frame_btn, text="Hủy", width=8, command=lambda: load_data(widgets)) 
    btn_huy.grid(row=0, column=3, padx=10)
    btn_xoa = ttk.Button(frame_btn, text="Xóa", width=8, command=lambda: xoa_taixe_vinhvien(widgets)) 
    btn_xoa.grid(row=0, column=4, padx=10)
    # (Bỏ nút Thoát)
    
    # 4. KẾT NỐI BINDING
    tree.bind("<<TreeviewSelect>>", lambda event: on_item_select(event, widgets)) 

    # 5. TẢI DỮ LIỆU LẦN ĐẦU
    load_data(widgets) 
    
    # 6. TRẢ VỀ FRAME CHÍNH
    return page_frame

# ================================================================
# PHẦN 5: CHẠY THỬ NGHIỆM
# ================================================================
if __name__ == "__main__":
    
    test_root = tk.Tk()
    test_root.title("Test Quản lý Tài xế")

    # SỬA: Dùng hàm từ utils (cần import utils)
    import utils 
    
    utils.center_window(test_root, 900, 650) 
    
    page = create_page(test_root) 
    page.pack(fill="both", expand=True)
    
    test_root.mainloop()