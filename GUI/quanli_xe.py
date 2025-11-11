import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc  # Thư viện để kết nối SQL Server (thay vì mysql.connector)

# ================================================================
# PHẦN 1: KẾT NỐI CSDL (ĐÃ THAY ĐỔI ĐỂ DÙNG SQL SERVER)
# ================================================================
def connect_db():
    """Hàm kết nối đến CSDL SQL Server."""
    try:
        # CẬP NHẬT: Dùng Windows Authentication và Server Name từ hình ảnh
        conn_string = (
            r'DRIVER={SQL Server};'
            r'SERVER=LAPTOP-MKC70SQE\SQLEXPRESS;' 
            r'DATABASE=QL_VanTai;'
            r'Trusted_Connection=yes;' # Dùng Windows Authentication
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
# PHẦN 2: CÁC HÀM CRUD (THEO MẪU)
# ================================================================

def clear_input():
    """Xóa trắng các trường nhập liệu."""
    entry_bienso.config(state='normal') # Mở khóa trường Biển số
    entry_bienso.delete(0, tk.END)
    entry_loaixe.delete(0, tk.END)
    entry_hangsx.delete(0, tk.END)
    entry_dongxe.delete(0, tk.END)
    entry_namsx.delete(0, tk.END)
    entry_vin.delete(0, tk.END)
    
    # Đặt lại ngày về một giá trị mặc định, ví dụ 2025-01-01
    date_dangkiem.set_date("2025-01-01")
    date_baohiem.set_date("2025-01-01")
    
    cbb_trangthai.set("1") # 1 = Hoạt động
    entry_manv.delete(0, tk.END)
    entry_bienso.focus()

def load_data():
    """Tải dữ liệu từ bảng Xe lên Treeview."""
    # Xóa dữ liệu cũ trên treeview
    for i in tree.get_children():
        tree.delete(i)
        
    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        # Lấy các cột chính để hiển thị
        cur.execute("SELECT BienSoXe, LoaiXe, HangSanXuat, NamSanXuat, TrangThai, NgayHetHanDangKiem FROM Xe")
        rows = cur.fetchall()
        
        for row in rows:
            # Chuyển đổi trạng thái số sang chữ để dễ đọc
            trang_thai_text = "Hoạt động"
            if row[4] == 0:
                trang_thai_text = "Bảo trì"
            elif row[4] == 2:
                trang_thai_text = "Hỏng"
            
            # Định dạng ngày (nếu cần)
            ngay_dk = str(row[5]) if row[5] else "N/A"
            
            tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], trang_thai_text, ngay_dk))
            
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def them_xe():
    """Thêm một xe mới vào CSDL."""
    # Lấy dữ liệu từ form
    bienso = entry_bienso.get()
    loaixe = entry_loaixe.get()
    hangsx = entry_hangsx.get()
    dongxe = entry_dongxe.get()
    namsx = entry_namsx.get()
    vin = entry_vin.get()
    
    # SỬA LỖI: Lấy ngày tháng dạng chuỗi 'yyyy-MM-dd' thay vì đối tượng Date
    ngay_dk = date_dangkiem.get() 
    ngay_bh = date_baohiem.get()
    
    # Lấy giá trị trạng thái (0, 1, 2)
    trangthai = cbb_trangthai_var.get().split('=')[0].strip() 
    manv = entry_manv.get()

    # Kiểm tra Biển số xe (Khóa chính)
    if not bienso:
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Biển số xe")
        return

    # Xử lý Mã NV (có thể là NULL)
    manv_sql = manv if manv else None
    
    # Xử lý Năm sản xuất (phải là số)
    try:
        namsx_int = int(namsx) if namsx else None
    except ValueError:
        messagebox.showwarning("Sai định dạng", "Năm sản xuất phải là số")
        return

    conn = connect_db()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        # Dùng dấu ? làm tham số cho pyodbc (thay vì %s)
        sql = """
        INSERT INTO Xe (
            BienSoXe, LoaiXe, HangSanXuat, DongXe, NamSanXuat, 
            SoKhungVIN, NgayHetHanDangKiem, NgayHetHanBaoHiem, 
            TrangThai, MaNhanVienHienTai
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cur.execute(sql, (
            bienso, loaixe, hangsx, dongxe, namsx_int,
            vin, ngay_dk, ngay_bh, int(trangthai), manv_sql
        ))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm xe mới thành công")
        
        clear_input()
        load_data()
        
    except pyodbc.IntegrityError:
        messagebox.showerror("Lỗi Trùng lặp", f"Biển số xe '{bienso}' đã tồn tại.")
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể thêm xe:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def chon_xe_de_sua():
    """Lấy thông tin xe được chọn trên Treeview và điền vào form."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một xe để sửa")
        return

    # Lấy BienSoXe (giá trị đầu tiên) của dòng được chọn
    selected_item = tree.item(selected[0])
    bienso = selected_item['values'][0]
    
    conn = connect_db()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        # Lấy TOÀN BỘ dữ liệu của xe đó
        cur.execute("SELECT * FROM Xe WHERE BienSoXe=?", (bienso,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu xe.")
            return

        # Xóa form trước khi điền
        clear_input()
        
        # Điền dữ liệu vào form
        entry_bienso.insert(0, data.BienSoXe)
        entry_bienso.config(state='disabled') # Khóa trường Biển số khi sửa
        
        entry_loaixe.insert(0, data.LoaiXe or "")
        entry_hangsx.insert(0, data.HangSanXuat or "")
        entry_dongxe.insert(0, data.DongXe or "")
        entry_namsx.insert(0, str(data.NamSanXuat or ""))
        entry_vin.insert(0, data.SoKhungVIN or "")
        
        if data.NgayHetHanDangKiem:
            date_dangkiem.set_date(data.NgayHetHanDangKiem)
        if data.NgayHetHanBaoHiem:
            date_baohiem.set_date(data.NgayHetHanBaoHiem)
            
        cbb_trangthai.set(str(data.TrangThai)) # Đặt lại giá trị combobox
        entry_manv.insert(0, data.MaNhanVienHienTai or "")

    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể lấy dữ liệu xe:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def luu_xe_da_sua():
    """Lưu thay đổi (UPDATE) sau khi sửa."""
    bienso = entry_bienso.get()
    if not bienso:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Biển số xe để cập nhật")
        return

    # Lấy dữ liệu từ form
    loaixe = entry_loaixe.get()
    hangsx = entry_hangsx.get()
    dongxe = entry_dongxe.get()
    namsx = entry_namsx.get()
    vin = entry_vin.get()
    
    # SỬA LỖI: Lấy ngày tháng dạng chuỗi 'yyyy-MM-dd' thay vì đối tượng Date
    ngay_dk = date_dangkiem.get()
    ngay_bh = date_baohiem.get()
    
    trangthai = cbb_trangthai_var.get().split('=')[0].strip()
    manv = entry_manv.get()

    manv_sql = manv if manv else None
    
    try:
        namsx_int = int(namsx) if namsx else None
    except ValueError:
        messagebox.showwarning("Sai định dạng", "Năm sản xuất phải là số")
        return

    conn = connect_db()
    if conn is None:
        return
        
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
            vin, ngay_dk, ngay_bh, int(trangthai), manv_sql,
            bienso  # BienSoXe cho mệnh đề WHERE
        ))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật thông tin xe")
        
        clear_input()
        load_data()
        
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật xe:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

def xoa_xe():
    """Xóa xe được chọn."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một xe để xóa")
        return

    selected_item = tree.item(selected[0])
    bienso = selected_item['values'][0]

    # Xác nhận xóa
    if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa xe '{bienso}'?"):
        return

    conn = connect_db()
    if conn is None:
        return
        
    try:
        cur = conn.cursor()
        # Dùng dấu ?
        cur.execute("DELETE FROM Xe WHERE BienSoXe=?", (bienso,))
        conn.commit()
        
        messagebox.showinfo("Thành công", "Đã xóa xe thành công")
        clear_input()
        load_data()
        
    except pyodbc.IntegrityError:
        messagebox.showerror("Lỗi Ràng buộc", "Không thể xóa xe này.\nXe có thể đang được gán cho một Chuyến đi hoặc có Lịch sử bảo trì.")
    except pyodbc.Error as e:
        messagebox.showerror("Lỗi SQL", f"Không thể xóa xe:\n{str(e)}")
    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn:
            conn.close()

# ================================================================
# PHẦN 3: THIẾT KẾ GIAO DIỆN (THEO MẪU)
# ================================================================

# ===== Cửa sổ chính =====
root = tk.Tk()
root.title("Quản lý Xe (Database QL_VanTai)")

# Hàm căn giữa cửa sổ (lấy từ mẫu)
def center_window(w, h):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

center_window(900, 650) # Kích thước cửa sổ lớn hơn
root.resizable(False, False)

# ===== Tiêu đề =====
lbl_title = tk.Label(root, text="QUẢN LÝ XE", font=("Arial", 18, "bold"))
lbl_title.pack(pady=10)

# ===== Frame nhập thông tin (2 cột) =====
frame_info = tk.Frame(root)
frame_info.pack(pady=5, padx=10, fill="x")

# --- Cột 1 ---
tk.Label(frame_info, text="Biển số xe:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_bienso = tk.Entry(frame_info, width=25)
entry_bienso.grid(row=0, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Loại xe:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_loaixe = tk.Entry(frame_info, width=25)
entry_loaixe.grid(row=1, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Hãng sản xuất:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_hangsx = tk.Entry(frame_info, width=25)
entry_hangsx.grid(row=2, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Dòng xe:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
entry_dongxe = tk.Entry(frame_info, width=25)
entry_dongxe.grid(row=3, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Mã NV lái:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
entry_manv = tk.Entry(frame_info, width=25)
entry_manv.grid(row=4, column=1, padx=5, pady=5, sticky="w")

# --- Cột 2 ---
tk.Label(frame_info, text="Năm sản xuất:").grid(row=0, column=2, padx=15, pady=5, sticky="w")
entry_namsx = tk.Entry(frame_info, width=25)
entry_namsx.grid(row=0, column=3, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Số khung (VIN):").grid(row=1, column=2, padx=15, pady=5, sticky="w")
entry_vin = tk.Entry(frame_info, width=25)
entry_vin.grid(row=1, column=3, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Ngày hết hạn ĐK:").grid(row=2, column=2, padx=15, pady=5, sticky="w")
date_dangkiem = DateEntry(frame_info, width=22, background='darkblue', foreground='white', date_pattern='yyyy-MM-dd')
date_dangkiem.grid(row=2, column=3, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Ngày hết hạn BH:").grid(row=3, column=2, padx=15, pady=5, sticky="w")
date_baohiem = DateEntry(frame_info, width=22, background='darkblue', foreground='white', date_pattern='yyyy-MM-dd')
date_baohiem.grid(row=3, column=3, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Trạng thái:").grid(row=4, column=2, padx=15, pady=5, sticky="w")
trangthai_options = [
    "0 = Bảo trì",
    "1 = Hoạt động",
    "2 = Hỏng"
]
cbb_trangthai_var = tk.StringVar()
cbb_trangthai = ttk.Combobox(frame_info, textvariable=cbb_trangthai_var, values=trangthai_options, width=22, state='readonly')
cbb_trangthai.grid(row=4, column=3, padx=5, pady=5, sticky="w")
cbb_trangthai.set("1 = Hoạt động") # Mặc định

# Cấu hình grid co giãn
frame_info.columnconfigure(1, weight=1)
frame_info.columnconfigure(3, weight=1)

# ===== Frame nút =====
frame_btn = tk.Frame(root)
frame_btn.pack(pady=10)

btn_them = tk.Button(frame_btn, text="Thêm", width=8, command=them_xe)
btn_them.grid(row=0, column=0, padx=5)

btn_luu = tk.Button(frame_btn, text="Lưu", width=8, command=luu_xe_da_sua)
btn_luu.grid(row=0, column=1, padx=5)

btn_sua = tk.Button(frame_btn, text="Sửa", width=8, command=chon_xe_de_sua)
btn_sua.grid(row=0, column=2, padx=5)

btn_huy = tk.Button(frame_btn, text="Hủy", width=8, command=clear_input)
btn_huy.grid(row=0, column=3, padx=5)

btn_xoa = tk.Button(frame_btn, text="Xóa", width=8, command=xoa_xe)
btn_xoa.grid(row=0, column=4, padx=5)

btn_thoat = tk.Button(frame_btn, text="Thoát", width=8, command=root.quit)
btn_thoat.grid(row=0, column=5, padx=5)


# ===== Bảng danh sách xe =====
lbl_ds = tk.Label(root, text="Danh sách xe", font=("Arial", 10, "bold"))
lbl_ds.pack(pady=5, padx=10, anchor="w")

# Frame chứa Treeview và thanh cuộn
frame_tree = tk.Frame(root)
frame_tree.pack(pady=10, padx=10, fill="both", expand=True)

# Thanh cuộn
scrollbar_y = tk.Scrollbar(frame_tree, orient=tk.VERTICAL)
scrollbar_x = tk.Scrollbar(frame_tree, orient=tk.HORIZONTAL)

columns = ("bienso", "loaixe", "hangsx", "namsx", "trangthai", "ngay_dk")
tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                    yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

scrollbar_y.config(command=tree.yview)
scrollbar_x.config(command=tree.xview)

scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

# Định nghĩa các cột
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

# ================================================================
# PHẦN 4: CHẠY ỨNG DỤNG
# ================================================================
load_data()  # Tải dữ liệu ban đầu
root.mainloop()