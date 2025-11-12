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
# (Sửa connect_db() thành utils.connect_db())
# ================================================================
def load_xe_combobox():
    """Tải danh sách TẤT CẢ xe (BienSoXe) vào Combobox."""
    conn = utils.connect_db() # <-- SỬA
    if conn is None: return []
    
    try:
        cur = conn.cursor()
        sql = "SELECT BienSoXe FROM Xe ORDER BY BienSoXe"
        cur.execute(sql)
        rows = cur.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Lỗi tải combobox xe: {e}")
        return []
    finally:
        if conn: conn.close()

# ================================================================
# PHẦN 3: CÁC HÀM CRUD
# (Đã sửa để nhận 'widgets' làm tham số)
# ================================================================

def set_form_state(is_enabled, widgets):
    """Bật (enable) hoặc Tắt (disable) toàn bộ các trường nhập liệu."""
    widgets['entry_mabaotri'].config(state='disabled')
    
    if is_enabled:
        widgets['cbb_xe'].config(state='readonly')
        widgets['date_ngaybaotri'].config(state='normal')
        widgets['entry_chiphi'].config(state='normal')
        # Style đặc biệt cho tk.Text
        widgets['entry_mota'].config(state='normal', bg=utils.theme_colors["bg_entry"], fg=utils.theme_colors["text"])
    else:
        widgets['cbb_xe'].config(state='disabled')
        widgets['date_ngaybaotri'].config(state='disabled')
        widgets['entry_chiphi'].config(state='disabled')
        widgets['entry_mota'].config(state='disabled', bg=utils.theme_colors["disabled_bg"], fg=utils.theme_colors["text_disabled"])

def clear_input(widgets):
    """(NÚT THÊM) Xóa trắng và Mở khóa các trường nhập liệu (Chế độ Thêm mới)."""
    set_form_state(is_enabled=True, widgets=widgets)
    
    widgets['entry_mabaotri'].config(state='normal')
    widgets['entry_mabaotri'].delete(0, tk.END)
    widgets['entry_mabaotri'].config(state='disabled')
    
    widgets['cbb_xe'].set("")
    widgets['entry_chiphi'].delete(0, tk.END)
    widgets['entry_mota'].delete("1.0", tk.END) 
    
    widgets['date_ngaybaotri'].set_date(datetime.now().strftime("%Y-%m-%d"))
    
    widgets['cbb_xe'].focus()
    
    tree = widgets['tree']
    if tree.selection():
        tree.selection_remove(tree.selection()[0])

def load_data(widgets):
    """Tải TOÀN BỘ dữ liệu Bảo trì VÀ LÀM MỜ FORM."""
    tree = widgets['tree']
    for i in tree.get_children():
        tree.delete(i)
        
    conn = utils.connect_db() # <-- SỬA
    if conn is None:
        set_form_state(is_enabled=False, widgets=widgets) 
        return
        
    try:
        cur = conn.cursor()
        sql = "SELECT MaBaoTri, BienSoXe, NgayBaoTri, ChiPhi, MoTa FROM LichSuBaoTri ORDER BY NgayBaoTri DESC"
        cur.execute(sql)
        rows = cur.fetchall()
        
        for row in rows:
            ma_bt = row[0]
            bienso = row[1]
            ngay_bt = str(row[2]) if row[2] else "N/A"
            chiphi = row[3]
            mota = (row[4] or "")[:50] + "..."
            
            tree.insert("", tk.END, values=(ma_bt, bienso, ngay_bt, chiphi, mota))
            
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

def them_baotri(widgets):
    """(LOGIC THÊM) Thêm một lịch sử bảo trì mới."""
    try:
        bienso = widgets['cbb_xe_var'].get()
        ngay_bt = widgets['date_ngaybaotri'].get_date().strftime('%Y-%m-%d')
        mota = widgets['entry_mota'].get("1.0", tk.END).strip()
        chiphi = widgets['entry_chiphi'].get()

        if not bienso or not ngay_bt:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Xe và Ngày bảo trì")
            return False

        chiphi_dec = float(chiphi) if chiphi else 0.0

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Chi phí không hợp lệ: {e}")
        return False

    conn = utils.connect_db() # <-- SỬA
    if conn is None: return False

    try:
        cur = conn.cursor()
        sql = "INSERT INTO LichSuBaoTri (BienSoXe, NgayBaoTri, MoTa, ChiPhi) VALUES (?, ?, ?, ?)"
        cur.execute(sql, (bienso, ngay_bt, mota, chiphi_dec))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm lịch sử bảo trì thành công")
        return True
        
    except Exception as e:
        conn.rollback() 
        messagebox.showerror("Lỗi SQL", f"Không thể thêm:\n{str(e)}")
        return False
    finally:
        if conn: conn.close()

def on_item_select(event, widgets):
    """(SỰ KIỆN CLICK) Khi click vào Treeview, đổ dữ liệu đầy đủ lên form (ở trạng thái mờ)."""
    tree = widgets['tree']
    selected = tree.selection()
    if not selected: return 

    selected_item = tree.item(selected[0])
    mabaotri = selected_item['values'][0]
    
    conn = utils.connect_db() # <-- SỬA
    if conn is None: return

    try:
        cur = conn.cursor()
        sql = "SELECT * FROM LichSuBaoTri WHERE MaBaoTri = ?"
        cur.execute(sql, (mabaotri,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu.")
            return

        set_form_state(is_enabled=True, widgets=widgets)
        widgets['entry_mabaotri'].config(state='normal')
        
        # Xóa
        widgets['entry_mabaotri'].delete(0, tk.END)
        widgets['cbb_xe'].set("")
        widgets['entry_chiphi'].delete(0, tk.END)
        widgets['entry_mota'].delete("1.0", tk.END)
        
        # Điền
        widgets['entry_mabaotri'].insert(0, data.MaBaoTri)
        widgets['cbb_xe'].set(data.BienSoXe or "")
        
        if data.NgayBaoTri:
            widgets['date_ngaybaotri'].set_date(str(data.NgayBaoTri)) 
            
        widgets['entry_chiphi'].insert(0, str(data.ChiPhi or ""))
        widgets['entry_mota'].insert("1.0", data.MoTa or "")

    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()
        widgets['entry_mabaotri'].config(state='disabled') 
        set_form_state(is_enabled=False, widgets=widgets)

def chon_baotri_de_sua(widgets): 
    """(NÚT SỬA) Kích hoạt chế độ sửa, Mở khóa form (trừ MaBaoTri)."""
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một mục trong danh sách trước khi nhấn 'Sửa'")
        return

    if not widgets['entry_mabaotri'].get():
         messagebox.showwarning("Lỗi", "Không tìm thấy mã bảo trì. Vui lòng chọn lại.")
         return

    set_form_state(is_enabled=True, widgets=widgets)
    widgets['entry_mabaotri'].config(state='disabled')
    widgets['cbb_xe'].focus() 

def luu_baotri_da_sua(widgets):
    """(LOGIC SỬA) Lưu thay đổi (UPDATE) sau khi sửa."""
    mabaotri = widgets['entry_mabaotri'].get()
    if not mabaotri:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã bảo trì để cập nhật")
        return False

    try:
        bienso = widgets['cbb_xe_var'].get()
        ngay_bt = widgets['date_ngaybaotri'].get_date().strftime('%Y-%m-%d')
        mota = widgets['entry_mota'].get("1.0", tk.END).strip()
        chiphi = widgets['entry_chiphi'].get()
        
        if not bienso or not ngay_bt:
            messagebox.showwarning("Thiếu dữ liệu", "Xe và Ngày bảo trì không được rỗng")
            return False

        chiphi_dec = float(chiphi) if chiphi else 0.0

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Chi phí không hợp lệ: {e}")
        return False

    conn = utils.connect_db() # <-- SỬA
    if conn is None: return False
        
    try:
        cur = conn.cursor()
        sql = """
        UPDATE LichSuBaoTri SET 
            BienSoXe = ?, NgayBaoTri = ?, MoTa = ?, ChiPhi = ?
        WHERE MaBaoTri = ?
        """
        cur.execute(sql, (bienso, ngay_bt, mota, chiphi_dec, mabaotri))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật lịch sử bảo trì")
        return True
        
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật:\n{str(e)}")
        return False
    finally:
        if conn: conn.close()

def save_data(widgets):
    """Lưu dữ liệu, tự động kiểm tra xem nên Thêm mới (INSERT) hay Cập nhật (UPDATE)."""
    if widgets['entry_mabaotri'].get():
        success = luu_baotri_da_sua(widgets)
    else:
        success = them_baotri(widgets)
    
    if success:
        load_data(widgets)

def xoa_baotri(widgets):
    """Xóa lịch sử bảo trì được chọn."""
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một mục để xóa")
        return
        
    mabaotri = widgets['entry_mabaotri'].get() 

    if not mabaotri:
        messagebox.showwarning("Lỗi", "Không tìm thấy mã bảo trì. Vui lòng chọn lại.")
        return

    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa Lịch sử Mã: {mabaotri}?"):
        return

    conn = utils.connect_db() # <-- SỬA
    if conn is None: return
        
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM LichSuBaoTri WHERE MaBaoTri=?", (mabaotri,))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã xóa lịch sử bảo trì thành công")
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
    lbl_title = ttk.Label(page_frame, text="QUẢN LÝ LỊCH SỬ BẢO TRÌ", style="Title.TLabel")
    lbl_title.pack(pady=15) 

    frame_info = ttk.Frame(page_frame, style="TFrame")
    frame_info.pack(pady=5, padx=20, fill="x")

    # --- Hàng 1 ---
    ttk.Label(frame_info, text="Mã bảo trì:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
    entry_mabaotri = ttk.Entry(frame_info, width=30, state='disabled')
    entry_mabaotri.grid(row=0, column=1, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Ngày bảo trì:").grid(row=0, column=2, padx=15, pady=8, sticky="w")
    date_entry_style_options = {
        'width': 38, 'date_pattern': 'yyyy-MM-dd',
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
    date_ngaybaotri = DateEntry(frame_info, **date_entry_style_options)
    date_ngaybaotri.grid(row=0, column=3, padx=5, pady=8, sticky="w")

    # --- Hàng 2 ---
    ttk.Label(frame_info, text="Xe:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
    cbb_xe_var = tk.StringVar()
    cbb_xe = ttk.Combobox(frame_info, textvariable=cbb_xe_var, width=28, state='readonly')
    cbb_xe.grid(row=1, column=1, padx=5, pady=8, sticky="w")
    cbb_xe['values'] = load_xe_combobox() # <-- SỬA (Hàm này vẫn local)

    ttk.Label(frame_info, text="Chi phí:").grid(row=1, column=2, padx=15, pady=8, sticky="w")
    entry_chiphi = ttk.Entry(frame_info, width=40)
    entry_chiphi.grid(row=1, column=3, padx=5, pady=8, sticky="w")

    # --- Hàng 3 (Mô tả) ---
    ttk.Label(frame_info, text="Mô tả công việc:").grid(row=2, column=0, padx=5, pady=8, sticky="nw")
    entry_mota = tk.Text(frame_info, width=60, height=4, 
        font=("Segoe UI", 10),
        bg=utils.theme_colors["bg_entry"],
        fg=utils.theme_colors["text"],
        relief="solid",
        borderwidth=1,
        insertbackground=utils.theme_colors["text"],
        highlightthickness=1, 
        highlightbackground="#ACACAC",
        highlightcolor=utils.theme_colors["accent"] 
    )
    entry_mota.grid(row=2, column=1, columnspan=3, padx=5, pady=8, sticky="w")

    frame_info.columnconfigure(1, weight=1)
    frame_info.columnconfigure(3, weight=1)

    # ===== Frame nút (SỬA LỖI: Đưa lên TRƯỚC Bảng) =====
    frame_btn = ttk.Frame(page_frame, style="TFrame")
    frame_btn.pack(pady=10)

    # ===== Bảng danh sách (SỬA LỖI: Đưa xuống DƯỚI nút) =====
    lbl_ds = ttk.Label(page_frame, text="Danh sách bảo trì (Sắp xếp mới nhất)", style="Header.TLabel")
    lbl_ds.pack(pady=(10, 5), padx=20, anchor="w")

    frame_tree = ttk.Frame(page_frame, style="TFrame")
    frame_tree.pack(pady=10, padx=20, fill="both", expand=True) # expand=True ở cuối

    scrollbar_y = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, style="Vertical.TScrollbar")
    scrollbar_x = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, style="Horizontal.TScrollbar")

    columns = ("ma_bt", "bienso", "ngay_bt", "chiphi", "mota")
    tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                        yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

    tree.heading("ma_bt", text="Mã BT")
    tree.column("ma_bt", width=60, anchor="center")
    tree.heading("bienso", text="Biển số xe")
    tree.column("bienso", width=100)
    tree.heading("ngay_bt", text="Ngày bảo trì")
    tree.column("ngay_bt", width=100)
    tree.heading("chiphi", text="Chi phí")
    tree.column("chiphi", width=100, anchor="e") 
    tree.heading("mota", text="Mô tả")
    tree.column("mota", width=300)

    tree.pack(fill="both", expand=True)
    
    # 3. TẠO TỪ ĐIỂN 'widgets'
    widgets = {
        "tree": tree,
        "entry_mabaotri": entry_mabaotri,
        "date_ngaybaotri": date_ngaybaotri,
        "cbb_xe": cbb_xe,
        "entry_chiphi": entry_chiphi,
        "entry_mota": entry_mota,
        "cbb_xe_var": cbb_xe_var
    }

    # (Code tạo nút bây giờ nằm trong frame_btn ở trên)
    btn_them = ttk.Button(frame_btn, text="Thêm", width=8, command=lambda: clear_input(widgets)) 
    btn_them.grid(row=0, column=0, padx=10)
    btn_luu = ttk.Button(frame_btn, text="Lưu", width=8, command=lambda: save_data(widgets)) 
    btn_luu.grid(row=0, column=1, padx=10)
    btn_sua = ttk.Button(frame_btn, text="Sửa", width=8, command=lambda: chon_baotri_de_sua(widgets)) 
    btn_sua.grid(row=0, column=2, padx=10)
    btn_huy = ttk.Button(frame_btn, text="Hủy", width=8, command=lambda: load_data(widgets)) 
    btn_huy.grid(row=0, column=3, padx=10)
    btn_xoa = ttk.Button(frame_btn, text="Xóa", width=8, command=lambda: xoa_baotri(widgets)) 
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
    test_root.title("Test Quản lý Bảo Trì")

    # SỬA: Dùng hàm từ utils
    utils.center_window(test_root, 950, 650) 
    
    page = create_page(test_root) 
    page.pack(fill="both", expand=True)
    
    test_root.mainloop()