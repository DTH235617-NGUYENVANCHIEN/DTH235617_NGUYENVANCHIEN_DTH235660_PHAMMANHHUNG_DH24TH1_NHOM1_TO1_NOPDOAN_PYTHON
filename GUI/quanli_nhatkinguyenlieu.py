# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
# import pyodbc # <-- ĐÃ XÓA
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
# (ĐÃ XÓA - Chuyển sang utils.py, vì utils đã có)
# ================================================================

# ================================================================
# PHẦN 3: CÁC HÀM CRUD
# (Đã sửa để nhận 'widgets' và dùng utils.connect_db())
# ================================================================

def set_form_state(is_enabled, widgets):
    """Bật (enable) hoặc Tắt (disable) toàn bộ các trường nhập liệu."""
    widgets['entry_manhatky'].config(state='disabled')
    
    if is_enabled:
        widgets['cbb_xe'].config(state='readonly')
        widgets['cbb_taixe'].config(state='readonly')
        widgets['date_ngaydo'].config(state='normal')
        widgets['entry_giodo'].config(state='normal')
        widgets['entry_solit'].config(state='normal')
        widgets['entry_tongchiphi'].config(state='normal')
        widgets['entry_soodo'].config(state='normal')
        widgets['cbb_trangthai'].config(state='readonly')
    else:
        widgets['cbb_xe'].config(state='disabled')
        widgets['cbb_taixe'].config(state='disabled')
        widgets['date_ngaydo'].config(state='disabled')
        widgets['entry_giodo'].config(state='disabled')
        widgets['entry_solit'].config(state='disabled')
        widgets['entry_tongchiphi'].config(state='disabled')
        widgets['entry_soodo'].config(state='disabled')
        widgets['cbb_trangthai'].config(state='disabled')

def clear_input(widgets):
    """(NÚT THÊM) Xóa trắng và Mở khóa các trường nhập liệu (Chế độ Thêm mới)."""
    set_form_state(is_enabled=True, widgets=widgets)
    
    widgets['entry_manhatky'].config(state='normal')
    widgets['entry_manhatky'].delete(0, tk.END)
    widgets['entry_manhatky'].config(state='disabled')
    
    widgets['cbb_taixe'].set("")
    widgets['cbb_xe'].set("")
    widgets['entry_solit'].delete(0, tk.END)
    widgets['entry_tongchiphi'].delete(0, tk.END)
    widgets['entry_soodo'].delete(0, tk.END)
    
    now = datetime.now()
    widgets['date_ngaydo'].set_date(now.strftime("%Y-%m-%d"))
    widgets['entry_giodo'].delete(0, tk.END)
    widgets['entry_giodo'].insert(0, now.strftime("%H:%M"))
    
    widgets['cbb_trangthai'].set("Chờ duyệt")
    widgets['cbb_xe'].focus()
    
    tree = widgets['tree']
    if tree.selection():
        tree.selection_remove(tree.selection()[0])

def load_data(widgets):
    """Tải TOÀN BỘ dữ liệu Nhiên liệu VÀ LÀM MỜ FORM."""
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
            nk.MaNhatKy, nk.BienSoXe, nv.HoVaTen, 
            nk.NgayDoNhienLieu, nk.SoLit, nk.TongChiPhi, nk.TrangThaiDuyet
        FROM NhatKyNhienLieu AS nk
        LEFT JOIN NhanVien AS nv ON nk.MaNhanVien = nv.MaNhanVien
        ORDER BY nk.NgayDoNhienLieu DESC
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        trangthai_map = { 0: "Chờ duyệt", 1: "Đã duyệt", 2: "Từ chối" }
        
        for row in rows:
            ma_nk = row[0]
            bienso = row[1]
            ten_tx = row[2] or "N/A"
            ngay_do = row[3].strftime("%Y-%m-%d %H:%M") if row[3] else "N/A"
            so_lit = row[4]
            tong_cp = row[5]
            trangthai_text = trangthai_map.get(row[6], "Không rõ")
            
            tree.insert("", tk.END, values=(ma_nk, bienso, ten_tx, ngay_do, so_lit, tong_cp, trangthai_text))
            
        children = tree.get_children()
        if children:
            first_item = children[0]
            tree.selection_set(first_item) 
            tree.focus(first_item)         
            tree.event_generate("<<TreeviewSelect>>") 
        else:
            set_form_state(is_enabled=True, widgets=widgets)
            clear_input(widgets) 
            
    except Exception as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    finally:
        if conn:
            conn.close()
        set_form_state(is_enabled=False, widgets=widgets)

def them_nhienlieu(widgets):
    """(LOGIC THÊM) Thêm một nhật ký nhiên liệu mới."""
    try:
        bienso = widgets['cbb_xe_var'].get()
        manv = widgets['cbb_taixe_var'].get().split(' - ')[0]
        
        ngay_do_str = widgets['date_ngaydo'].get_date().strftime('%Y-%m-%d')
        gio_do_str = widgets['entry_giodo'].get() or "00:00"
        tg_nhienlieu = f"{ngay_do_str} {gio_do_str}:00"
        
        solit = widgets['entry_solit'].get()
        tongchiphi = widgets['entry_tongchiphi'].get()
        soodo = widgets['entry_soodo'].get()
        
        trangthai_text = widgets['cbb_trangthai_var'].get()
        trangthai_map = {"Chờ duyệt": 0, "Đã duyệt": 1, "Từ chối": 2}
        trangthai_value = trangthai_map.get(trangthai_text, 0)

        if not bienso or not manv or not solit or not tongchiphi:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Xe, Tài xế, Số lít và Chi phí")
            return False

        solit_dec = float(solit) if solit else 0.0
        tongchiphi_dec = float(tongchiphi) if tongchiphi else 0.0
        soodo_int = int(soodo) if soodo else None

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu số (lít, chi phí, odo) không hợp lệ: {e}")
        return False

    conn = utils.connect_db() # <-- SỬA
    if conn is None: return False

    try:
        cur = conn.cursor()
        sql = """
        INSERT INTO NhatKyNhienLieu (
            BienSoXe, MaNhanVien, NgayDoNhienLieu, SoLit, 
            TongChiPhi, SoOdo, TrangThaiDuyet
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cur.execute(sql, (bienso, manv, tg_nhienlieu, solit_dec, tongchiphi_dec, soodo_int, trangthai_value))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm nhật ký nhiên liệu thành công")
        return True
        
    except Exception as e:
        conn.rollback() 
        messagebox.showerror("Lỗi SQL", f"Không thể thêm nhật ký:\n{str(e)}")
        return False
    finally:
        if conn: conn.close()

def on_item_select(event, widgets):
    """(SỰ KIỆN CLICK) Khi click vào Treeview, đổ dữ liệu đầy đủ lên form (ở trạng thái mờ)."""
    tree = widgets['tree']
    selected = tree.selection()
    if not selected: return 

    selected_item = tree.item(selected[0])
    manhatky = selected_item['values'][0]
    
    conn = utils.connect_db() # <-- SỬA
    if conn is None: return

    try:
        cur = conn.cursor()
        sql = """
        SELECT nk.*, nv.HoVaTen 
        FROM NhatKyNhienLieu nk
        LEFT JOIN NhanVien nv ON nk.MaNhanVien = nv.MaNhanVien
        WHERE nk.MaNhatKy = ?
        """
        cur.execute(sql, (manhatky,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu nhật ký.")
            return

        set_form_state(is_enabled=True, widgets=widgets)
        widgets['entry_manhatky'].config(state='normal')
        
        # Xóa
        widgets['entry_manhatky'].delete(0, tk.END)
        widgets['cbb_xe'].set("")
        widgets['cbb_taixe'].set("")
        widgets['entry_giodo'].delete(0, tk.END)
        widgets['entry_solit'].delete(0, tk.END)
        widgets['entry_tongchiphi'].delete(0, tk.END)
        widgets['entry_soodo'].delete(0, tk.END)
        
        # Điền
        widgets['entry_manhatky'].insert(0, data.MaNhatKy)
        widgets['cbb_xe'].set(data.BienSoXe or "")
        
        if data.MaNhanVien:
            cbb_taixe_val = f"{data.MaNhanVien} - {data.HoVaTen}"
            widgets['cbb_taixe'].set(cbb_taixe_val)
        
        if data.NgayDoNhienLieu:
            widgets['date_ngaydo'].set_date(data.NgayDoNhienLieu.strftime("%Y-%m-%d"))
            widgets['entry_giodo'].insert(0, data.NgayDoNhienLieu.strftime("%H:%M"))
            
        widgets['entry_solit'].insert(0, str(data.SoLit or ""))
        widgets['entry_tongchiphi'].insert(0, str(data.TongChiPhi or ""))
        widgets['entry_soodo'].insert(0, str(data.SoOdo or ""))

        trangthai_map = {0: "Chờ duyệt", 1: "Đã duyệt", 2: "Từ chối"}
        widgets['cbb_trangthai'].set(trangthai_map.get(data.TrangThaiDuyet, "Chờ duyệt"))

    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()
        widgets['entry_manhatky'].config(state='disabled') 
        set_form_state(is_enabled=False, widgets=widgets)

def chon_nhienlieu_de_sua(widgets): 
    """(NÚT SỬA) Kích hoạt chế độ sửa, Mở khóa form (trừ MaNhatKy)."""
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một nhật ký trong danh sách trước khi nhấn 'Sửa'")
        return

    if not widgets['entry_manhatky'].get():
         messagebox.showwarning("Lỗi", "Không tìm thấy mã nhật ký. Vui lòng chọn lại.")
         return

    set_form_state(is_enabled=True, widgets=widgets)
    widgets['entry_manhatky'].config(state='disabled') 
    widgets['cbb_xe'].focus() 

def luu_nhienlieu_da_sua(widgets):
    """(LOGIC SỬA) Lưu thay đổi (UPDATE) sau khi sửa."""
    manhatky = widgets['entry_manhatky'].get()
    if not manhatky:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã nhật ký để cập nhật")
        return False

    try:
        bienso = widgets['cbb_xe_var'].get()
        manv = widgets['cbb_taixe_var'].get().split(' - ')[0]
        
        ngay_do_str = widgets['date_ngaydo'].get_date().strftime('%Y-%m-%d')
        gio_do_str = widgets['entry_giodo'].get() or "00:00"
        tg_nhienlieu = f"{ngay_do_str} {gio_do_str}:00"
        
        solit = widgets['entry_solit'].get()
        tongchiphi = widgets['entry_tongchiphi'].get()
        soodo = widgets['entry_soodo'].get()
        
        trangthai_text = widgets['cbb_trangthai_var'].get()
        trangthai_map = {"Chờ duyệt": 0, "Đã duyệt": 1, "Từ chối": 2}
        trangthai_value = trangthai_map.get(trangthai_text, 0)
        
        if not bienso or not manv or not solit or not tongchiphi:
            messagebox.showwarning("Thiếu dữ liệu", "Xe, Tài xế, Số lít và Chi phí không được rỗng")
            return False

        solit_dec = float(solit) if solit else 0.0
        tongchiphi_dec = float(tongchiphi) if tongchiphi else 0.0
        soodo_int = int(soodo) if soodo else None

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu nhập không hợp lệ: {e}")
        return False

    conn = utils.connect_db() # <-- SỬA
    if conn is None: return False
        
    try:
        cur = conn.cursor()
        sql = """
        UPDATE NhatKyNhienLieu SET 
            BienSoXe = ?, MaNhanVien = ?, NgayDoNhienLieu = ?, 
            SoLit = ?, TongChiPhi = ?, SoOdo = ?, TrangThaiDuyet = ?
        WHERE MaNhatKy = ?
        """
        cur.execute(sql, (
            bienso, manv, tg_nhienlieu, 
            solit_dec, tongchiphi_dec, soodo_int, trangthai_value,
            manhatky
        ))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật nhật ký nhiên liệu")
        return True
        
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật:\n{str(e)}")
        return False
    finally:
        if conn: conn.close()

def save_data(widgets):
    """Lưu dữ liệu, tự động kiểm tra xem nên Thêm mới (INSERT) hay Cập nhật (UPDATE)."""
    if widgets['entry_manhatky'].get():
        success = luu_nhienlieu_da_sua(widgets)
    else:
        success = them_nhienlieu(widgets)
    
    if success:
        load_data(widgets)

def xoa_nhienlieu(widgets):
    """Xóa nhật ký được chọn."""
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một nhật ký để xóa")
        return
        
    manhatky = widgets['entry_manhatky'].get() 

    if not manhatky:
        messagebox.showwarning("Lỗi", "Không tìm thấy mã nhật ký. Vui lòng chọn lại.")
        return

    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa Nhật ký Mã: {manhatky}?"):
        return

    conn = utils.connect_db() # <-- SỬA
    if conn is None: return
        
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM NhatKyNhienLieu WHERE MaNhatKy=?", (manhatky,))
        conn.commit()
        
        messagebox.showinfo("Thành công", "Đã xóa nhật ký thành công")
        load_data(widgets)
        
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể xóa:\n{str(e)}")
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
    lbl_title = ttk.Label(page_frame, text="QUẢN LÝ NHẬT KÝ NHIÊN LIỆU", style="Title.TLabel")
    lbl_title.pack(pady=15) 

    frame_info = ttk.Frame(page_frame, style="TFrame")
    frame_info.pack(pady=5, padx=20, fill="x")

    # --- Hàng 1 ---
    ttk.Label(frame_info, text="Mã nhật ký:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
    entry_manhatky = ttk.Entry(frame_info, width=30, state='disabled')
    entry_manhatky.grid(row=0, column=1, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Trạng thái:").grid(row=0, column=2, padx=15, pady=8, sticky="w")
    trangthai_options = ["Chờ duyệt", "Đã duyệt", "Từ chối"]
    cbb_trangthai_var = tk.StringVar()
    cbb_trangthai = ttk.Combobox(frame_info, textvariable=cbb_trangthai_var, values=trangthai_options, width=38, state='readonly')
    cbb_trangthai.grid(row=0, column=3, padx=5, pady=8, sticky="w")
    cbb_trangthai.set("Chờ duyệt")

    # --- Hàng 2 ---
    ttk.Label(frame_info, text="Xe:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
    cbb_xe_var = tk.StringVar()
    cbb_xe = ttk.Combobox(frame_info, textvariable=cbb_xe_var, width=28, state='readonly')
    cbb_xe.grid(row=1, column=1, padx=5, pady=8, sticky="w")
    cbb_xe['values'] = utils.load_xe_combobox() # <-- SỬA

    ttk.Label(frame_info, text="Tài xế đổ:").grid(row=1, column=2, padx=15, pady=8, sticky="w")
    cbb_taixe_var = tk.StringVar()
    cbb_taixe = ttk.Combobox(frame_info, textvariable=cbb_taixe_var, width=38, state='readonly')
    cbb_taixe.grid(row=1, column=3, padx=5, pady=8, sticky="w")
    cbb_taixe['values'] = utils.load_taixe_combobox() # <-- SỬA

    # --- Hàng 3 (Thời gian) ---
    ttk.Label(frame_info, text="Ngày đổ:").grid(row=2, column=0, padx=5, pady=8, sticky="w")
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
    date_ngaydo = DateEntry(frame_info, **date_entry_style_options)
    date_ngaydo.grid(row=2, column=1, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Giờ đổ (HH:MM):").grid(row=2, column=2, padx=15, pady=8, sticky="w")
    entry_giodo = ttk.Entry(frame_info, width=40)
    entry_giodo.grid(row=2, column=3, padx=5, pady=8, sticky="w")

    # --- Hàng 4 (Chi phí) ---
    ttk.Label(frame_info, text="Số lít:").grid(row=3, column=0, padx=5, pady=8, sticky="w")
    entry_solit = ttk.Entry(frame_info, width=30)
    entry_solit.grid(row=3, column=1, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Tổng chi phí:").grid(row=3, column=2, padx=15, pady=8, sticky="w")
    entry_tongchiphi = ttk.Entry(frame_info, width=40)
    entry_tongchiphi.grid(row=3, column=3, padx=5, pady=8, sticky="w")

    # --- Hàng 5 (Odo) ---
    ttk.Label(frame_info, text="Số Odo (Km):").grid(row=4, column=0, padx=5, pady=8, sticky="w")
    entry_soodo = ttk.Entry(frame_info, width=30)
    entry_soodo.grid(row=4, column=1, padx=5, pady=8, sticky="w")


    frame_info.columnconfigure(1, weight=1)
    frame_info.columnconfigure(3, weight=1)

    # ===== Frame nút (SỬA LỖI: Đưa lên TRƯỚC Bảng) =====
    frame_btn = ttk.Frame(page_frame, style="TFrame")
    frame_btn.pack(pady=10)

    # ===== Bảng danh sách (SỬA LỖI: Đưa xuống DƯỚI nút) =====
    lbl_ds = ttk.Label(page_frame, text="Danh sách nhật ký nhiên liệu (Sắp xếp mới nhất)", style="Header.TLabel")
    lbl_ds.pack(pady=(10, 5), padx=20, anchor="w")

    frame_tree = ttk.Frame(page_frame, style="TFrame")
    frame_tree.pack(pady=10, padx=20, fill="both", expand=True) # expand=True ở cuối

    scrollbar_y = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, style="Vertical.TScrollbar")
    scrollbar_x = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, style="Horizontal.TScrollbar")

    columns = ("ma_nk", "bienso", "ten_tx", "ngay_do", "so_lit", "tong_cp", "trangthai")
    tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                        yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

    tree.heading("ma_nk", text="Mã NK")
    tree.column("ma_nk", width=60, anchor="center")
    tree.heading("bienso", text="Biển số xe")
    tree.column("bienso", width=100)
    tree.heading("ten_tx", text="Tên Tài xế")
    tree.column("ten_tx", width=150)
    tree.heading("ngay_do", text="Ngày đổ")
    tree.column("ngay_do", width=150)
    tree.heading("so_lit", text="Số lít")
    tree.column("so_lit", width=80, anchor="e") 
    tree.heading("tong_cp", text="Tổng chi phí")
    tree.column("tong_cp", width=100, anchor="e") 
    tree.heading("trangthai", text="Trạng thái")
    tree.column("trangthai", width=100, anchor="center")

    tree.pack(fill="both", expand=True)
    
    # 3. TẠO TỪ ĐIỂN 'widgets'
    widgets = {
        "tree": tree,
        "entry_manhatky": entry_manhatky,
        "cbb_xe": cbb_xe,
        "cbb_taixe": cbb_taixe,
        "date_ngaydo": date_ngaydo,
        "entry_giodo": entry_giodo,
        "entry_solit": entry_solit,
        "entry_tongchiphi": entry_tongchiphi,
        "entry_soodo": entry_soodo,
        "cbb_trangthai": cbb_trangthai,
        "cbb_xe_var": cbb_xe_var,
        "cbb_taixe_var": cbb_taixe_var,
        "cbb_trangthai_var": cbb_trangthai_var
    }

    # (Code tạo nút bây giờ nằm trong frame_btn ở trên)
    btn_them = ttk.Button(frame_btn, text="Thêm", width=8, command=lambda: clear_input(widgets)) 
    btn_them.grid(row=0, column=0, padx=10)
    btn_luu = ttk.Button(frame_btn, text="Lưu", width=8, command=lambda: save_data(widgets)) 
    btn_luu.grid(row=0, column=1, padx=10)
    btn_sua = ttk.Button(frame_btn, text="Sửa", width=8, command=lambda: chon_nhienlieu_de_sua(widgets)) 
    btn_sua.grid(row=0, column=2, padx=10)
    btn_huy = ttk.Button(frame_btn, text="Hủy", width=8, command=lambda: load_data(widgets)) 
    btn_huy.grid(row=0, column=3, padx=10)
    btn_xoa = ttk.Button(frame_btn, text="Xóa", width=8, command=lambda: xoa_nhienlieu(widgets)) 
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
    test_root.title("Test Quản lý Nhiên liệu")

    # SỬA: Dùng hàm từ utils (cần import utils)
    import utils 
    
    def center_window(w, h): # Giữ lại hàm test nếu utils chưa có
        ws = test_root.winfo_screenwidth()
        hs = test_root.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        test_root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    center_window(950, 700) 
    test_root.resizable(False, False)
    
    page = create_page(test_root) 
    page.pack(fill="both", expand=True)
    
    test_root.mainloop()