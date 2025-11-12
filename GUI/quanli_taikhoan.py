# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
# import pyodbc # <-- ĐÃ XÓA
import utils # <-- IMPORT FILE DÙNG CHUNG
from datetime import datetime
import hashlib 

# ================================================================
# BỘ MÀU "LIGHT MODE"
# (ĐÃ XÓA - Chuyển sang utils.py)
# ================================================================

# Biến tạm để xử lý Mật khẩu
PASSWORD_PLACEHOLDER = "******"

# ================================================================
# PHẦN 1: KẾT NỐI CSDL
# (ĐÃ XÓA - Chuyển sang utils.py)
# ================================================================

# ================================================================
# PHẦN 2: CÁC HÀM TIỆN ÍCH & LOGIC BẢO MẬT
# (ĐÃ XÓA load_nhanvien_combobox - Chuyển sang utils.py)
# ================================================================
def hash_password(password):
    """Hàm băm mật khẩu bằng SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# ================================================================
# PHẦN 3: CÁC HÀM CRUD
# (Đã sửa để nhận 'widgets' và dùng utils.connect_db())
# ================================================================

def set_form_state(is_enabled, widgets):
    """Bật (enable) hoặc Tắt (disable) các trường ngoại trừ PK."""
    if is_enabled:
        widgets['entry_matkhau'].config(state='normal')
        widgets['cbb_nhanvien'].config(state='readonly')
        widgets['cbb_vaitro'].config(state='readonly')
    else:
        widgets['entry_matkhau'].config(state='disabled')
        widgets['cbb_nhanvien'].config(state='disabled')
        widgets['cbb_vaitro'].config(state='disabled')
        widgets['entry_tendangnhap'].config(state='disabled')

def clear_input(widgets):
    """(NÚT THÊM) Xóa trắng và Mở khóa PK."""
    set_form_state(is_enabled=True, widgets=widgets)
    
    widgets['entry_tendangnhap'].config(state='normal')
    widgets['entry_tendangnhap'].delete(0, tk.END)
    
    widgets['entry_matkhau'].delete(0, tk.END)
    widgets['cbb_nhanvien'].set("")
    widgets['cbb_vaitro'].set("TaiXe") 
    
    widgets['entry_tendangnhap'].focus()
    
    tree = widgets['tree']
    if tree.selection():
        tree.selection_remove(tree.selection()[0])

def load_data(widgets):
    """Tải TOÀN BỘ dữ liệu Tài khoản VÀ LÀM MỜ FORM."""
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
            tk.TenDangNhap, tk.MaNhanVien, nv.HoVaTen, tk.VaiTro
        FROM TaiKhoan AS tk
        LEFT JOIN NhanVien AS nv ON tk.MaNhanVien = nv.MaNhanVien
        ORDER BY tk.TenDangNhap
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        for row in rows:
            tendn = row[0]
            manv = row[1]
            hoten = row[2] or "N/A"
            vaitro = row[3]
            
            tree.insert("", tk.END, values=(tendn, manv, hoten, vaitro))
            
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
        if conn: conn.close()
        set_form_state(is_enabled=False, widgets=widgets)
        widgets['entry_tendangnhap'].config(state='disabled')


def them_taikhoan(widgets):
    """(LOGIC THÊM) Thêm một tài khoản mới."""
    try:
        tendn = widgets['entry_tendangnhap'].get()
        matkhau = widgets['entry_matkhau'].get()
        manv = widgets['cbb_nhanvien_var'].get().split(' - ')[0]
        vaitro = widgets['cbb_vaitro_var'].get()

        if not tendn or not matkhau:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Tên đăng nhập và Mật khẩu")
            return False
        
        if matkhau == PASSWORD_PLACEHOLDER:
            messagebox.showwarning("Lỗi mật khẩu", "Vui lòng nhập mật khẩu mới")
            return False

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu nhập không hợp lệ (chưa chọn nhân viên?): {e}")
        return False

    conn = utils.connect_db() # <-- SỬA
    if conn is None: return False

    try:
        cur = conn.cursor()
        hashed_mk = hash_password(matkhau)
        
        sql = "INSERT INTO TaiKhoan (TenDangNhap, MatKhau, MaNhanVien, VaiTro) VALUES (?, ?, ?, ?)"
        cur.execute(sql, (tendn, hashed_mk, manv, vaitro))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm tài khoản mới thành công")
        return True
        
    except Exception as e:
        conn.rollback() 
        # Cần import pyodbc ở đầu file để bắt lỗi cụ thể
        try:
            if "PRIMARY KEY" in str(e):
                messagebox.showerror("Lỗi Trùng lặp", f"Tên đăng nhập '{tendn}' đã tồn tại.")
            elif "FOREIGN KEY" in str(e):
                messagebox.showerror("Lỗi Trùng lặp", f"Nhân viên '{manv}' có thể đã có tài khoản.")
            else:
                messagebox.showerror("Lỗi SQL", f"Không thể thêm:\n{str(e)}")
        except: # Fallback
             messagebox.showerror("Lỗi SQL", f"Không thể thêm:\n{str(e)}")
        return False
    finally:
        if conn: conn.close()

def on_item_select(event, widgets):
    """(SỰ KIỆN CLICK) Lấy thông tin tài khoản và điền vào form (ở chế độ mờ)."""
    tree = widgets['tree']
    selected = tree.selection()
    if not selected: return 

    selected_item = tree.item(selected[0])
    tendn = selected_item['values'][0]
    
    conn = utils.connect_db() # <-- SỬA
    if conn is None: return

    try:
        cur = conn.cursor()
        sql = "SELECT tk.*, nv.HoVaTen FROM TaiKhoan tk LEFT JOIN NhanVien nv ON tk.MaNhanVien = nv.MaNhanVien WHERE tk.TenDangNhap = ?"
        cur.execute(sql, (tendn,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu tài khoản.")
            return

        set_form_state(is_enabled=True, widgets=widgets)
        widgets['entry_tendangnhap'].config(state='normal')
        
        # Xóa
        widgets['entry_tendangnhap'].delete(0, tk.END)
        widgets['entry_matkhau'].delete(0, tk.END)
        widgets['cbb_nhanvien'].set("")
        
        # Điền
        widgets['entry_tendangnhap'].insert(0, data.TenDangNhap)
        widgets['entry_matkhau'].insert(0, PASSWORD_PLACEHOLDER)
        
        if data.MaNhanVien:
            cbb_nhanvien_val = f"{data.MaNhanVien} - {data.HoVaTen}"
            widgets['cbb_nhanvien'].set(cbb_nhanvien_val)
        
        widgets['cbb_vaitro'].set(data.VaiTro or "TaiXe")

    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()
        widgets['entry_tendangnhap'].config(state='disabled') 
        set_form_state(is_enabled=False, widgets=widgets)


def chon_taikhoan_de_sua(widgets): 
    """(NÚT SỬA) Kích hoạt chế độ sửa, Mở khóa các ô nhập liệu (trừ Tên đăng nhập)."""
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một tài khoản trong danh sách trước khi nhấn 'Sửa'")
        return

    if not widgets['entry_tendangnhap'].get():
         messagebox.showwarning("Lỗi", "Không tìm thấy Tên đăng nhập. Vui lòng chọn lại.")
         return

    set_form_state(is_enabled=True, widgets=widgets)
    widgets['entry_tendangnhap'].config(state='disabled')
    widgets['entry_matkhau'].focus() 

def luu_taikhoan_da_sua(widgets):
    """(LOGIC SỬA) Lưu thay đổi (UPDATE) sau khi sửa."""
    tendn = widgets['entry_tendangnhap'].get()
    if not tendn:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Tên đăng nhập để cập nhật")
        return False

    try:
        matkhau_moi = widgets['entry_matkhau'].get()
        manv = widgets['cbb_nhanvien_var'].get().split(' - ')[0]
        vaitro = widgets['cbb_vaitro_var'].get()
    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu nhập không hợp lệ (chưa chọn nhân viên?): {e}")
        return False

    conn = utils.connect_db() # <-- SỬA
    if conn is None: return False
        
    try:
        cur = conn.cursor()
        
        if matkhau_moi != PASSWORD_PLACEHOLDER and matkhau_moi:
            hashed_mk_moi = hash_password(matkhau_moi)
            sql = "UPDATE TaiKhoan SET MatKhau = ?, MaNhanVien = ?, VaiTro = ? WHERE TenDangNhap = ?"
            cur.execute(sql, (hashed_mk_moi, manv, vaitro, tendn))
        else: 
            sql = "UPDATE TaiKhoan SET MaNhanVien = ?, VaiTro = ? WHERE TenDangNhap = ?"
            cur.execute(sql, (manv, vaitro, tendn))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật tài khoản")
        return True
        
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật:\n{str(e)}")
        return False
    finally:
        if conn: conn.close()

def save_data(widgets):
    """Lưu dữ liệu, tự động kiểm tra xem nên Thêm mới (INSERT) hay Cập nhật (UPDATE)."""
    if widgets['entry_tendangnhap'].cget('state') == 'disabled' and widgets['entry_tendangnhap'].get():
        success = luu_taikhoan_da_sua(widgets)
    else:
        success = them_taikhoan(widgets)
    
    if success:
        load_data(widgets)

def xoa_taikhoan(widgets):
    """Xóa tài khoản được chọn."""
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một tài khoản để xóa")
        return
 
    tendn = widgets['entry_tendangnhap'].get() 
    
    if not tendn:
        messagebox.showwarning("Lỗi", "Không tìm thấy Tên đăng nhập. Vui lòng chọn lại.")
        return

    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa tài khoản '{tendn}'?"):
        return

    conn = utils.connect_db() # <-- SỬA
    if conn is None: return
        
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM TaiKhoan WHERE TenDangNhap=?", (tendn,))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã xóa tài khoản thành công")
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
    lbl_title = ttk.Label(page_frame, text="QUẢN LÝ TÀI KHOẢN", style="Title.TLabel")
    lbl_title.pack(pady=15) 

    frame_info = ttk.Frame(page_frame, style="TFrame")
    frame_info.pack(pady=5, padx=20, fill="x")

    # --- Hàng 1 ---
    ttk.Label(frame_info, text="Tên đăng nhập:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
    entry_tendangnhap = ttk.Entry(frame_info, width=30)
    entry_tendangnhap.grid(row=0, column=1, padx=5, pady=8, sticky="w")

    ttk.Label(frame_info, text="Mật khẩu:").grid(row=0, column=2, padx=15, pady=8, sticky="w")
    entry_matkhau = ttk.Entry(frame_info, width=30, show="*") 
    entry_matkhau.grid(row=0, column=3, padx=5, pady=8, sticky="w")

    # --- Hàng 2 ---
    ttk.Label(frame_info, text="Nhân viên:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
    cbb_nhanvien_var = tk.StringVar()
    cbb_nhanvien = ttk.Combobox(frame_info, textvariable=cbb_nhanvien_var, width=28, state='readonly')
    cbb_nhanvien.grid(row=1, column=1, padx=5, pady=8, sticky="w")
    cbb_nhanvien['values'] = utils.load_nhanvien_combobox() # <-- SỬA

    ttk.Label(frame_info, text="Vai trò:").grid(row=1, column=2, padx=15, pady=8, sticky="w")
    vaitro_options = ["Admin", "TaiXe"]
    cbb_vaitro_var = tk.StringVar()
    cbb_vaitro = ttk.Combobox(frame_info, textvariable=cbb_vaitro_var, values=vaitro_options, width=28, state='readonly')
    cbb_vaitro.grid(row=1, column=3, padx=5, pady=8, sticky="w")
    cbb_vaitro.set("TaiXe")

    frame_info.columnconfigure(1, weight=1)
    frame_info.columnconfigure(3, weight=1)
    
    # ===== Frame nút (SỬA LỖI: Đưa lên TRƯỚC Bảng) =====
    frame_btn = ttk.Frame(page_frame, style="TFrame")
    frame_btn.pack(pady=15)

    # ===== Bảng danh sách (SỬA LỖI: Đưa xuống DƯỚI nút) =====
    lbl_ds = ttk.Label(page_frame, text="Danh sách tài khoản (Không hiển thị mật khẩu)", style="Header.TLabel")
    lbl_ds.pack(pady=(10, 5), padx=20, anchor="w")

    frame_tree = ttk.Frame(page_frame, style="TFrame")
    frame_tree.pack(pady=10, padx=20, fill="both", expand=True) # expand=True ở cuối

    scrollbar_y = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, style="Vertical.TScrollbar")
    scrollbar_x = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, style="Horizontal.TScrollbar")

    columns = ("tendn", "manv", "hoten", "vaitro")
    tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                        yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

    tree.heading("tendn", text="Tên đăng nhập")
    tree.column("tendn", width=150)
    tree.heading("manv", text="Mã NV")
    tree.column("manv", width=100, anchor="center")
    tree.heading("hoten", text="Họ Tên Nhân Viên")
    tree.column("hoten", width=200)
    tree.heading("vaitro", text="Vai trò")
    tree.column("vaitro", width=100, anchor="center")

    tree.pack(fill="both", expand=True)
    
    # 3. TẠO TỪ ĐIỂN 'widgets'
    widgets = {
        "tree": tree,
        "entry_tendangnhap": entry_tendangnhap,
        "entry_matkhau": entry_matkhau,
        "cbb_nhanvien": cbb_nhanvien,
        "cbb_vaitro": cbb_vaitro,
        "cbb_nhanvien_var": cbb_nhanvien_var,
        "cbb_vaitro_var": cbb_vaitro_var
    }

    # (Code tạo nút bây giờ nằm trong frame_btn ở trên)
    btn_them = ttk.Button(frame_btn, text="Thêm", width=8, command=lambda: clear_input(widgets))
    btn_them.grid(row=0, column=0, padx=10)
    btn_luu = ttk.Button(frame_btn, text="Lưu", width=8, command=lambda: save_data(widgets)) 
    btn_luu.grid(row=0, column=1, padx=10)
    btn_sua = ttk.Button(frame_btn, text="Sửa", width=8, command=lambda: chon_taikhoan_de_sua(widgets)) 
    btn_sua.grid(row=0, column=2, padx=10)
    btn_huy = ttk.Button(frame_btn, text="Hủy", width=8, command=lambda: load_data(widgets)) 
    btn_huy.grid(row=0, column=3, padx=10)
    btn_xoa = ttk.Button(frame_btn, text="Xóa", width=8, command=lambda: xoa_taikhoan(widgets))
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
    test_root.title("Test Quản lý Tài khoản")

    # SỬA: Dùng hàm từ utils (cần import utils)
    import utils 
    
    utils.center_window(test_root, 900, 600) 
    
    page = create_page(test_root) 
    page.pack(fill="both", expand=True)
    
    test_root.mainloop()