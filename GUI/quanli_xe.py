# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc # <-- ĐÃ XÓA
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
# PHẦN 2: CÁC HÀM CRUD
# (Đã sửa để nhận 'widgets' và dùng utils.connect_db())
# ================================================================

def set_form_state(is_enabled, widgets):
    """Bật (enable) hoặc Tắt (disable) toàn bộ các trường nhập liệu."""
    if is_enabled:
        widgets['entry_loaixe'].config(state='normal')
        widgets['entry_hangsx'].config(state='normal')
        widgets['entry_dongxe'].config(state='normal')
        widgets['entry_namsx'].config(state='normal')
        widgets['entry_vin'].config(state='normal')
        widgets['date_dangkiem'].config(state='normal')
        widgets['date_baohiem'].config(state='normal')
        widgets['cbb_trangthai'].config(state='readonly')
        widgets['entry_manv'].config(state='normal')
    else:
        widgets['entry_bienso'].config(state='disabled')
        widgets['entry_loaixe'].config(state='disabled')
        widgets['entry_hangsx'].config(state='disabled')
        widgets['entry_dongxe'].config(state='disabled')
        widgets['entry_namsx'].config(state='disabled')
        widgets['entry_vin'].config(state='disabled')
        widgets['date_dangkiem'].config(state='disabled')
        widgets['date_baohiem'].config(state='disabled')
        widgets['cbb_trangthai'].config(state='disabled')
        widgets['entry_manv'].config(state='disabled')

def clear_input(widgets):
    """(NÚT THÊM) Xóa trắng và Mở khóa các trường nhập liệu (Chế độ Thêm mới)."""
    set_form_state(is_enabled=True, widgets=widgets)
    widgets['entry_bienso'].config(state='normal') 
    
    widgets['entry_bienso'].delete(0, tk.END)
    widgets['entry_loaixe'].delete(0, tk.END)
    widgets['entry_hangsx'].delete(0, tk.END)
    widgets['entry_dongxe'].delete(0, tk.END)
    widgets['entry_namsx'].delete(0, tk.END)
    widgets['entry_vin'].delete(0, tk.END)
    widgets['entry_manv'].delete(0, tk.END)
    
    default_date = datetime.date.today() + datetime.timedelta(days=365)
    widgets['date_dangkiem'].set_date(default_date)
    widgets['date_baohiem'].set_date(default_date)
    widgets['cbb_trangthai'].set("Hoạt động")
    
    widgets['entry_bienso'].focus()
    
    tree = widgets['tree']
    if tree.selection():
        tree.selection_remove(tree.selection()[0])

def load_data(widgets):
    """Tải TOÀN BỘ dữ liệu Xe VÀ LÀM MỜ FORM."""
    tree = widgets['tree']
    for i in tree.get_children():
        tree.delete(i)
        
    conn = utils.connect_db() # <-- SỬA
    if conn is None:
        set_form_state(is_enabled=False, widgets=widgets) 
        return
        
    try:
        cur = conn.cursor()
        cur.execute("SELECT BienSoXe, LoaiXe, HangSanXuat, NamSanXuat, TrangThai, NgayHetHanDangKiem FROM Xe")
        rows = cur.fetchall()
        
        for row in rows:
            trang_thai_text = "Hoạt động"
            if row[4] == 0:
                trang_thai_text = "Bảo trì"
            elif row[4] == 2:
                trang_thai_text = "Hỏng"
            
            ngay_dk = str(row[5]) if row[5] else "N/A"
            
            tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], trang_thai_text, ngay_dk))
        
        children = tree.get_children()
        if children:
            first_item = children[0]
            tree.selection_set(first_item) 
            tree.focus(first_item)         
            tree.event_generate("<<TreeviewSelect>>") 
        else:
            widgets['entry_bienso'].config(state='normal')
            set_form_state(is_enabled=True, widgets=widgets)
            widgets['entry_bienso'].delete(0, tk.END)
            widgets['entry_loaixe'].delete(0, tk.END)
            widgets['entry_hangsx'].delete(0, tk.END)
            widgets['entry_dongxe'].delete(0, tk.END)
            widgets['entry_namsx'].delete(0, tk.END)
            widgets['entry_vin'].delete(0, tk.END)
            widgets['entry_manv'].delete(0, tk.END)
            widgets['cbb_trangthai'].set("Hoạt động")
            
    except Exception as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    finally:
        if conn:
            conn.close()
        set_form_state(is_enabled=False, widgets=widgets)

def them_xe(widgets):
    """(LOGIC THÊM) Thêm một xe mới vào CSDL."""
    bienso = widgets['entry_bienso'].get()
    loaixe = widgets['entry_loaixe'].get()
    hangsx = widgets['entry_hangsx'].get()
    dongxe = widgets['entry_dongxe'].get()
    namsx = widgets['entry_namsx'].get()
    vin = widgets['entry_vin'].get()
    ngay_dk = widgets['date_dangkiem'].get_date().strftime('%Y-%m-%d')
    ngay_bh = widgets['date_baohiem'].get_date().strftime('%Y-%m-%d')
    manv = widgets['entry_manv'].get()

    trangthai_text = widgets['cbb_trangthai_var'].get()
    trangthai_value = 1 # Hoạt động
    if trangthai_text == "Bảo trì":
        trangthai_value = 0
    elif trangthai_text == "Hỏng":
        trangthai_value = 2

    if not bienso or not loaixe:
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Biển số xe và Loại xe")
        return False

    manv_sql = manv if manv else None
    
    try:
        namsx_int = int(namsx) if namsx else None
    except ValueError:
        messagebox.showwarning("Sai định dạng", "Năm sản xuất phải là số")
        return False

    conn = utils.connect_db() # <-- SỬA
    if conn is None: return False

    try:
        cur = conn.cursor()
        sql = """
        INSERT INTO Xe (
            BienSoXe, LoaiXe, HangSanXuat, DongXe, NamSanXuat, 
            SoKhungVIN, NgayHetHanDangKiem, NgayHetHanBaoHiem, 
            TrangThai, MaNhanVienHienTai
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cur.execute(sql, (
            bienso, loaixe, hangsx, dongxe, namsx_int,
            vin, ngay_dk, ngay_bh, trangthai_value, manv_sql
        ))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm xe mới thành công")
        return True
        
    except pyodbc.IntegrityError:
        conn.rollback()
        messagebox.showerror("Lỗi Trùng lặp", f"Biển số xe '{bienso}' đã tồn tại.")
        return False
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể thêm xe:\n{str(e)}")
        return False
    finally:
        if conn: conn.close()

def on_item_select(event, widgets):
    """(SỰ KIỆN CLICK) Khi click vào Treeview, đổ dữ liệu đầy đủ lên form (ở trạng thái mờ)."""
    tree = widgets['tree']
    selected = tree.selection()
    if not selected: return 

    selected_item = tree.item(selected[0])
    bienso = selected_item['values'][0]
    
    conn = utils.connect_db() # <-- SỬA
    if conn is None: return

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Xe WHERE BienSoXe=?", (bienso,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu xe.")
            return

        set_form_state(is_enabled=True, widgets=widgets)
        widgets['entry_bienso'].config(state='normal')
        
        # Xóa
        widgets['entry_bienso'].delete(0, tk.END)
        widgets['entry_loaixe'].delete(0, tk.END)
        widgets['entry_hangsx'].delete(0, tk.END)
        widgets['entry_dongxe'].delete(0, tk.END)
        widgets['entry_namsx'].delete(0, tk.END)
        widgets['entry_vin'].delete(0, tk.END)
        widgets['entry_manv'].delete(0, tk.END)
        
        # Điền
        widgets['entry_bienso'].insert(0, data.BienSoXe)
        widgets['entry_loaixe'].insert(0, data.LoaiXe or "")
        widgets['entry_hangsx'].insert(0, data.HangSanXuat or "")
        widgets['entry_dongxe'].insert(0, data.DongXe or "")
        widgets['entry_namsx'].insert(0, str(data.NamSanXuat or ""))
        widgets['entry_vin'].insert(0, data.SoKhungVIN or "")
        widgets['entry_manv'].insert(0, data.MaNhanVienHienTai or "")
        
        if data.NgayHetHanDangKiem:
            widgets['date_dangkiem'].set_date(data.NgayHetHanDangKiem)
        if data.NgayHetHanBaoHiem:
            widgets['date_baohiem'].set_date(data.NgayHetHanBaoHiem)
            
        trang_thai_text = "Hoạt động"
        if data.TrangThai == 0:
            trang_thai_text = "Bảo trì"
        elif data.TrangThai == 2:
            trang_thai_text = "Hỏng"
        widgets['cbb_trangthai'].set(trang_thai_text)

    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()
        set_form_state(is_enabled=False, widgets=widgets)

def chon_xe_de_sua(widgets): 
    """(NÚT SỬA) Kích hoạt chế độ sửa, Mở khóa form (trừ Biển số)."""
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một xe trong danh sách trước khi nhấn 'Sửa'")
        return

    if not widgets['entry_bienso'].get():
         messagebox.showwarning("Lỗi", "Không tìm thấy biển số xe. Vui lòng chọn lại.")
         return

    set_form_state(is_enabled=True, widgets=widgets)
    widgets['entry_bienso'].config(state='disabled') 
    widgets['entry_loaixe'].focus() 

def luu_xe_da_sua(widgets):
    """(LOGIC SỬA) Lưu thay đổi (UPDATE) sau khi sửa."""
    bienso = widgets['entry_bienso'].get()
    if not bienso:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Biển số xe để cập nhật")
        return False

    loaixe = widgets['entry_loaixe'].get()
    hangsx = widgets['entry_hangsx'].get()
    dongxe = widgets['entry_dongxe'].get()
    namsx = widgets['entry_namsx'].get()
    vin = widgets['entry_vin'].get()
    ngay_dk = widgets['date_dangkiem'].get_date().strftime('%Y-%m-%d')
    ngay_bh = widgets['date_baohiem'].get_date().strftime('%Y-%m-%d')
    manv = widgets['entry_manv'].get()

    trangthai_text = widgets['cbb_trangthai_var'].get()
    trangthai_value = 1 
    if trangthai_text == "Bảo trì":
        trangthai_value = 0
    elif trangthai_text == "Hỏng":
        trangthai_value = 2
        
    if not loaixe:
        messagebox.showwarning("Thiếu dữ liệu", "Loại xe không được rỗng")
        return False

    manv_sql = manv if manv else None
    
    try:
        namsx_int = int(namsx) if namsx else None
    except ValueError:
        messagebox.showwarning("Sai định dạng", "Năm sản xuất phải là số")
        return False

    conn = utils.connect_db() # <-- SỬA
    if conn is None: return False
        
    try:
        cur = conn.cursor()
        sql = """
        UPDATE Xe SET 
            LoaiXe = ?, HangSanXuat = ?, DongXe = ?, NamSanXuat = ?,
            SoKhungVIN = ?, NgayHetHanDangKiem = ?, NgayHetHanBaoHiem = ?,
            TrangThai = ?, MaNhanVienHienTai = ?
        WHERE BienSoXe = ?
        """
        cur.execute(sql, (
            loaixe, hangsx, dongxe, namsx_int,
            vin, ngay_dk, ngay_bh, trangthai_value, manv_sql,
            bienso 
        ))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật thông tin xe")
        return True
        
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật xe:\n{str(e)}")
        return False
    finally:
        if conn: conn.close()

def save_data(widgets):
    """Lưu dữ liệu, tự động kiểm tra xem nên Thêm mới (INSERT) hay Cập nhật (UPDATE)."""
    if widgets['entry_bienso'].cget('state') == 'disabled':
        success = luu_xe_da_sua(widgets)
    else:
        success = them_xe(widgets)
    
    if success:
        load_data(widgets)

def xoa_xe_vinhvien(widgets):
    """(NGUY HIỂM) Xóa vĩnh viễn xe và MỌI DỮ LIỆU LIÊN QUAN."""
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một xe trong danh sách để xóa")
        return
        
    bienso = widgets['entry_bienso'].get() 

    if not bienso:
        messagebox.showwarning("Lỗi", "Không tìm thấy biển số xe. Vui lòng chọn lại.")
        return

    msg_xacnhan = (
        f"BẠN CÓ CHẮC CHẮN MUỐN XÓA VĨNH VIỄN XE '{bienso}'?\n\n"
        "CẢNH BÁO: Thao tác này KHÔNG THỂ hoàn tác.\n"
        "Tất cả Lịch sử chuyến đi, Lịch sử nhiên liệu, và Lịch sử bảo trì của xe này sẽ bị XÓA SẠCH."
    )
    if not messagebox.askyesno("XÁC NHẬN XÓA VĨNH VIỄN", msg_xacnhan):
        return

    conn = utils.connect_db() # <-- SỬA
    if conn is None: return
        
    try:
        cur = conn.cursor()
        
        cur.execute("DELETE FROM NhatKyNhienLieu WHERE BienSoXe=?", (bienso,))
        cur.execute("DELETE FROM LichSuBaoTri WHERE BienSoXe=?", (bienso,))
        cur.execute("DELETE FROM ChuyenDi WHERE BienSoXe=?", (bienso,))
        cur.execute("DELETE FROM Xe WHERE BienSoXe=?", (bienso,))
        
        conn.commit()
        messagebox.showinfo("Thành công", f"Đã xóa vĩnh viễn xe '{bienso}' và tất cả dữ liệu liên quan.")
        load_data(widgets)
        
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể xóa xe:\n{str(e)}")
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
    lbl_title = ttk.Label(page_frame, text="QUẢN LÝ XE", style="Title.TLabel")
    lbl_title.pack(pady=15) 

    frame_info = ttk.Frame(page_frame, style="TFrame")
    frame_info.pack(pady=5, padx=20, fill="x")

    # --- Cột 1 ---
    ttk.Label(frame_info, text="Biển số xe:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
    entry_bienso = ttk.Entry(frame_info, width=30)
    entry_bienso.grid(row=0, column=1, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Loại xe:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
    entry_loaixe = ttk.Entry(frame_info, width=30)
    entry_loaixe.grid(row=1, column=1, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Hãng sản xuất:").grid(row=2, column=0, padx=5, pady=8, sticky="w")
    entry_hangsx = ttk.Entry(frame_info, width=30)
    entry_hangsx.grid(row=2, column=1, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Dòng xe:").grid(row=3, column=0, padx=5, pady=8, sticky="w")
    entry_dongxe = ttk.Entry(frame_info, width=30)
    entry_dongxe.grid(row=3, column=1, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Mã NV lái:").grid(row=4, column=0, padx=5, pady=8, sticky="w")
    entry_manv = ttk.Entry(frame_info, width=30)
    entry_manv.grid(row=4, column=1, padx=5, pady=8, sticky="w")

    # --- Cột 2 ---
    ttk.Label(frame_info, text="Năm sản xuất:").grid(row=0, column=2, padx=15, pady=8, sticky="w")
    entry_namsx = ttk.Entry(frame_info, width=30)
    entry_namsx.grid(row=0, column=3, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Số khung (VIN):").grid(row=1, column=2, padx=15, pady=8, sticky="w")
    entry_vin = ttk.Entry(frame_info, width=30)
    entry_vin.grid(row=1, column=3, padx=5, pady=8, sticky="w")

    date_entry_style_options = {
        'width': 28, 'date_pattern': 'yyyy-MM-dd',
        'background': utils.theme_colors["bg_entry"], 
        'foreground': utils.theme_colors["text"],
        'disabledbackground': utils.theme_colors["disabled_bg"],
        'disabledforeground': utils.theme_colors["text_disabled"],
        'bordercolor': utils.theme_colors["bg_entry"],
        'headersbackground': utils.theme_colors["accent"],
        'headersforeground': utils.theme_colors["accent_text"],
        'selectbackground': utils.theme_colors["accent"],
        'selectforeground': utils.theme_colors["accent_text"]
    }

    ttk.Label(frame_info, text="Ngày hết hạn ĐK:").grid(row=2, column=2, padx=15, pady=8, sticky="w")
    date_dangkiem = DateEntry(frame_info, **date_entry_style_options)
    date_dangkiem.grid(row=2, column=3, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Ngày hết hạn BH:").grid(row=3, column=2, padx=15, pady=8, sticky="w")
    date_baohiem = DateEntry(frame_info, **date_entry_style_options)
    date_baohiem.grid(row=3, column=3, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Trạng thái:").grid(row=4, column=2, padx=15, pady=8, sticky="w")
    trangthai_options = ["Bảo trì", "Hoạt động", "Hỏng"]
    cbb_trangthai_var = tk.StringVar()
    cbb_trangthai = ttk.Combobox(frame_info, textvariable=cbb_trangthai_var, values=trangthai_options, width=28, state='readonly')
    cbb_trangthai.grid(row=4, column=3, padx=5, pady=8, sticky="w")
    cbb_trangthai.set("Hoạt động") 

    frame_info.columnconfigure(1, weight=1)
    frame_info.columnconfigure(3, weight=1)

    # ===== Frame nút (SỬA LỖI: Đưa lên TRƯỚC Bảng) =====
    frame_btn = ttk.Frame(page_frame, style="TFrame")
    frame_btn.pack(pady=10) 

    # ===== Bảng danh sách xe (SỬA LỖI: Đưa xuống DƯỚI nút) =====
    lbl_ds = ttk.Label(page_frame, text="Danh sách xe", style="Header.TLabel")
    lbl_ds.pack(pady=(10, 5), padx=20, anchor="w")

    frame_tree = ttk.Frame(page_frame, style="TFrame")
    frame_tree.pack(pady=10, padx=20, fill="both", expand=True) # expand=True ở cuối

    scrollbar_y = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, style="Vertical.TScrollbar")
    scrollbar_x = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, style="Horizontal.TScrollbar")

    columns = ("bienso", "loaixe", "hangsx", "namsx", "trangthai", "ngay_dk")
    tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                        yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

    tree.heading("bienso", text="Biển số xe")
    tree.column("bienso", width=100, anchor="center")
    tree.heading("loaixe", text="Loại xe")
    tree.column("loaixe", width=150)
    tree.heading("hangsx", text="Hãng sản xuất")
    tree.column("hangsx", width=150)
    tree.heading("namsx", text="Năm SX")
    tree.column("namsx", width=80, anchor="center")
    tree.heading("trangthai", text="Trạng thái")
    tree.column("trangthai", width=100, anchor="center")
    tree.heading("ngay_dk", text="Ngày hết hạn ĐK")
    tree.column("ngay_dk", width=150, anchor="center")

    tree.pack(fill="both", expand=True)
    
    # 3. TẠO TỪ ĐIỂN 'widgets'
    widgets = {
        "tree": tree,
        "entry_bienso": entry_bienso,
        "entry_loaixe": entry_loaixe,
        "entry_hangsx": entry_hangsx,
        "entry_dongxe": entry_dongxe,
        "entry_namsx": entry_namsx,
        "entry_vin": entry_vin,
        "date_dangkiem": date_dangkiem,
        "date_baohiem": date_baohiem,
        "cbb_trangthai": cbb_trangthai,
        "entry_manv": entry_manv,
        "cbb_trangthai_var": cbb_trangthai_var
    }

    # (Code tạo nút bây giờ nằm trong frame_btn ở trên)
    btn_them = ttk.Button(frame_btn, text="Thêm", width=8, command=lambda: clear_input(widgets)) 
    btn_them.grid(row=0, column=0, padx=10)
    btn_luu = ttk.Button(frame_btn, text="Lưu", width=8, command=lambda: save_data(widgets)) 
    btn_luu.grid(row=0, column=1, padx=10)
    btn_sua = ttk.Button(frame_btn, text="Sửa", width=8, command=lambda: chon_xe_de_sua(widgets)) 
    btn_sua.grid(row=0, column=2, padx=10)
    btn_huy = ttk.Button(frame_btn, text="Hủy", width=8, command=lambda: load_data(widgets)) 
    btn_huy.grid(row=0, column=3, padx=10)
    btn_xoa = ttk.Button(frame_btn, text="Xóa", width=8, command=lambda: xoa_xe_vinhvien(widgets)) 
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
    test_root.title("Test Quản lý Xe")

    # SỬA: Dùng hàm từ utils
    utils.center_window(test_root, 900, 650) 
    
    page = create_page(test_root) 
    page.pack(fill="both", expand=True)
    
    test_root.mainloop()