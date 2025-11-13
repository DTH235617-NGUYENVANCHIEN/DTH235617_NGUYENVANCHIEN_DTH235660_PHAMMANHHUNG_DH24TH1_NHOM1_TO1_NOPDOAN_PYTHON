# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import utils # <-- IMPORT FILE DÙNG CHUNG
from datetime import datetime
import datetime as dt

# ================================================================
# PHẦN 2: CÁC HÀM TIỆN ÍCH (Tải Combobox)
# ================================================================
def load_taixe_combobox():
    conn = utils.connect_db()
    if conn is None: return []
    try:
        cur = conn.cursor()
        sql = """
        SELECT tx.MaNhanVien, nv.HoVaTen 
        FROM TaiXe tx
        JOIN NhanVien nv ON tx.MaNhanVien = nv.MaNhanVien
        WHERE nv.TrangThai = 1
        ORDER BY nv.HoVaTen
        """
        cur.execute(sql)
        rows = cur.fetchall()
        return [f"{row[0]} - {row[1]}" for row in rows]
    except Exception as e:
        print(f"Lỗi tải combobox tài xế: {e}")
        return []
    finally:
        if conn: conn.close()

def load_xe_combobox():
    conn = utils.connect_db()
    if conn is None: return []
    try:
        cur = conn.cursor()
        sql = "SELECT BienSoXe FROM Xe WHERE TrangThai = 1 ORDER BY BienSoXe"
        cur.execute(sql)
        rows = cur.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Lỗi tải combobox xe: {e}")
        return []
    finally:
        if conn: conn.close()

# === THÊM HÀM MỚI ===
def get_manv_from_username(username):
    """Lấy MaNhanVien từ TenDangNhap để lọc dữ liệu."""
    conn = utils.connect_db()
    if conn is None: return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT MaNhanVien FROM TaiKhoan WHERE TenDangNhap = ?", (username,))
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Lỗi get_manv_from_username: {e}")
        return None
    finally:
        if conn: conn.close()

# ================================================================
# PHẦN 3: CÁC HÀM CRUD
# ================================================================

def set_form_state(is_enabled, widgets):
    """Bật (enable) hoặc Tắt (disable) toàn bộ các trường nhập liệu."""
    widgets['entry_machuyendi'].config(state='disabled')
    
    if is_enabled:
        widgets['cbb_taixe'].config(state='readonly')
        widgets['cbb_xe'].config(state='readonly')
        widgets['entry_diembd'].config(state='normal')
        widgets['entry_diemkt'].config(state='normal')
        widgets['date_bd'].config(state='normal')
        widgets['entry_giobd'].config(state='normal')
        widgets['date_kt'].config(state='normal')
        widgets['entry_giokt'].config(state='normal')
        widgets['cbb_trangthai'].config(state='disabled')
    else:
        widgets['cbb_taixe'].config(state='disabled')
        widgets['cbb_xe'].config(state='disabled')
        widgets['entry_diembd'].config(state='disabled')
        widgets['entry_diemkt'].config(state='disabled')
        widgets['date_bd'].config(state='disabled')
        widgets['entry_giobd'].config(state='disabled')
        widgets['date_kt'].config(state='disabled')
        widgets['entry_giokt'].config(state='disabled')
        widgets['cbb_trangthai'].config(state='disabled')

def clear_input(widgets):
    """(NÚT THÊM) Xóa trắng và Mở khóa các trường nhập liệu (Chế độ Thêm mới)."""
    set_form_state(is_enabled=True, widgets=widgets)
    
    widgets['entry_machuyendi'].config(state='normal')
    widgets['entry_machuyendi'].delete(0, tk.END)
    widgets['entry_machuyendi'].config(state='disabled')
    
    widgets['cbb_taixe'].set("")
    widgets['cbb_xe'].set("")
    widgets['entry_diembd'].delete(0, tk.END)
    widgets['entry_diemkt'].delete(0, tk.END)
    
    now = datetime.now()
    widgets['date_bd'].set_date(now.strftime("%Y-%m-%d"))
    widgets['entry_giobd'].delete(0, tk.END)
    widgets['entry_giobd'].insert(0, now.strftime("%H:%M"))
    
    widgets['date_kt'].set_date(now.strftime("%Y-%m-%d"))
    widgets['entry_giokt'].delete(0, tk.END)
    
    widgets['cbb_trangthai'].set("Đã gán") 
    widgets['cbb_taixe'].focus()
    
    if widgets['tree'].selection():
        widgets['tree'].selection_remove(widgets['tree'].selection()[0])

def load_data(widgets, user_role, user_username):
    """Tải dữ liệu ChuyenDi (lọc theo vai trò) VÀ LÀM MỜ FORM (nếu là Admin)."""
    tree = widgets['tree']
    for i in tree.get_children():
        tree.delete(i)
        
    conn = utils.connect_db()
    if conn is None:
        if user_role == "Admin": # Chỉ Admin mới có form để disable
             set_form_state(is_enabled=False, widgets=widgets) 
        return
        
    try:
        cur = conn.cursor()
        
        # === SỬA SQL: Thêm cd.ThoiGianKetThuc ===
        sql = """
        SELECT 
            cd.MaChuyenDi, nv.HoVaTen, cd.BienSoXe, 
            cd.ThoiGianBatDau, cd.TrangThai, cd.ThoiGianKetThuc
        FROM ChuyenDi AS cd
        LEFT JOIN NhanVien AS nv ON cd.MaNhanVien = nv.MaNhanVien
        """
        
        params = []
        if user_role == "TaiXe":
            manv = get_manv_from_username(user_username) 
            if manv:
                sql += " WHERE cd.MaNhanVien = ?"
                params.append(manv)
            else:
                sql += " WHERE 1=0" 
        
        sql += " ORDER BY cd.ThoiGianBatDau DESC"
        
        cur.execute(sql, params)
        rows = cur.fetchall()
        
        trangthai_map = { 0: "Đã gán", 1: "Đang thực hiện", 2: "Hoàn thành", 3: "Hủy" }
        
        for row in rows:
            ma_cd = row[0]
            ten_tx = row[1] or "N/A"
            bienso = row[2]
            tg_bd = row[3].strftime("%Y-%m-%d %H:%M") if row[3] else "N/A"
            trangthai_text = trangthai_map.get(row[4], "Không rõ")
            
            # === SỬA: Lấy thêm tg_ketthuc (row[5]) ===
            tg_kt = row[5].strftime("%Y-%m-%d %H:%M") if row[5] else "Đang đi"
            
            # === SỬA: Thêm tg_kt vào values ===
            tree.insert("", tk.END, values=(ma_cd, ten_tx, bienso, tg_bd, tg_kt, trangthai_text))
            
        children = tree.get_children()
        if children:
            first_item = children[0]
            tree.selection_set(first_item) 
            tree.focus(first_item)         
            tree.event_generate("<<TreeviewSelect>>") 
        elif user_role == "Admin": 
            set_form_state(is_enabled=True, widgets=widgets)
            clear_input(widgets) 
            
    except Exception as e:
        messagebox.showerror("Lỗi tải dữ liệu", f"Lỗi SQL: {str(e)}")
    finally:
        if conn:
            conn.close()
        
        if user_role == "Admin":
            set_form_state(is_enabled=False, widgets=widgets)

def them_chuyendi(widgets):
    """(LOGIC THÊM) Thêm một chuyến đi mới."""
    try:
        manv = widgets['cbb_taixe_var'].get().split(' - ')[0]
        bienso = widgets['cbb_xe_var'].get()
        diembd = widgets['entry_diembd'].get()
        diemkt = widgets['entry_diemkt'].get()
        
        # === SỬA LOGIC THỜI GIAN ===
        # Chỉ lấy ngày, không lấy giờ. Giờ sẽ NULL cho đến khi tài xế bắt đầu
        ngay_bd_str = widgets['date_bd'].get_date().strftime('%Y-%m-%d')
        tg_batdau = ngay_bd_str # <--- CHỈ LƯU NGÀY
        
        tg_ketthuc = None # Luôn là NULL khi mới tạo
        
        trangthai_text = widgets['cbb_trangthai_var'].get()
        trangthai_map = {"Đã gán": 0, "Đang thực hiện": 1, "Hoàn thành": 2, "Hủy": 3}
        trangthai_value = trangthai_map.get(trangthai_text, 0)

        if not manv or not bienso or not diembd:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Tài xế, Xe và Điểm bắt đầu")
            return False

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu nhập không hợp lệ: {e}")
        return False

    conn = utils.connect_db() 
    if conn is None: return False

    try:
        cur = conn.cursor()
        sql = """
        INSERT INTO ChuyenDi (
            MaNhanVien, BienSoXe, DiemBatDau, DiemKetThuc, 
            ThoiGianBatDau, ThoiGianKetThuc, TrangThai
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        # === SỬA THAM SỐ ===
        # tg_batdau bây giờ chỉ là ngày (hoặc NULL nếu bạn muốn, nhưng để ngày vẫn tốt hơn)
        cur.execute(sql, (manv, bienso, diembd, diemkt, tg_batdau, tg_ketthuc, trangthai_value))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm chuyến đi mới thành công")
        return True
        
    except Exception as e:
        conn.rollback() 
        messagebox.showerror("Lỗi SQL", f"Không thể thêm chuyến đi:\n{str(e)}")
        return False
    finally:
        if conn: conn.close()

def on_item_select(event, widgets):
    """(SỰ KIỆN CLICK) Đổ dữ liệu lên form (nếu là Admin)."""
    
    tree = widgets['tree']
    selected = tree.selection()
    if not selected: return 

    selected_item = tree.item(selected[0])
    machuyendi = selected_item['values'][0]
    
    conn = utils.connect_db()
    if conn is None: return

    try:
        cur = conn.cursor()
        sql = """
        SELECT cd.*, nv.HoVaTen 
        FROM ChuyenDi cd
        LEFT JOIN NhanVien nv ON cd.MaNhanVien = nv.MaNhanVien
        WHERE cd.MaChuyenDi = ?
        """
        cur.execute(sql, (machuyendi,))
        data = cur.fetchone()
        
        if not data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu chuyến đi.")
            return

        user_role = widgets.get("user_role", "Admin") 

        if user_role == "Admin":
            set_form_state(is_enabled=True, widgets=widgets)
            
        widgets['entry_machuyendi'].config(state='normal')
        
        # Xóa (Luôn luôn chạy)
        widgets['entry_machuyendi'].delete(0, tk.END)
        widgets['cbb_taixe'].set("")
        widgets['cbb_xe'].set("")
        widgets['entry_diembd'].delete(0, tk.END)
        widgets['entry_diemkt'].delete(0, tk.END)
        widgets['entry_giobd'].delete(0, tk.END)
        widgets['entry_giokt'].delete(0, tk.END)
        
        # Điền dữ liệu (Luôn luôn chạy)
        widgets['entry_machuyendi'].insert(0, data.MaChuyenDi)
        
        cbb_taixe_val = f"{data.MaNhanVien} - {data.HoVaTen}" if data.MaNhanVien and data.HoVaTen else ""
        widgets['cbb_taixe'].set(cbb_taixe_val)
        widgets['cbb_xe'].set(data.BienSoXe or "")
        widgets['entry_diembd'].insert(0, data.DiemBatDau or "")
        widgets['entry_diemkt'].insert(0, data.DiemKetThuc or "")
        
        if data.ThoiGianBatDau:
            widgets['date_bd'].set_date(data.ThoiGianBatDau) # <--- SỬA
            widgets['entry_giobd'].insert(0, data.ThoiGianBatDau.strftime("%H:%M"))
        if data.ThoiGianKetThuc:
            widgets['date_kt'].set_date(data.ThoiGianKetThuc) # <--- SỬA
            widgets['entry_giokt'].insert(0, data.ThoiGianKetThuc.strftime("%H:%M"))
        trangthai_map = {0: "Đã gán", 1: "Đang thực hiện", 2: "Hoàn thành", 3: "Hủy"}
        widgets['cbb_trangthai'].set(trangthai_map.get(data.TrangThai, "Đã gán"))

    except Exception as e:
        messagebox.showerror("Lỗi không xác định", f"Lỗi: {str(e)}")
    finally:
        if conn: conn.close()
        widgets['entry_machuyendi'].config(state='disabled') 
        
        user_role = widgets.get("user_role", "Admin")
        if user_role == "Admin":
            set_form_state(is_enabled=False, widgets=widgets)

def chon_chuyendi_de_sua(widgets): 
    selected = widgets['tree'].selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một chuyến đi trong danh sách trước khi nhấn 'Sửa'")
        return
    if not widgets['entry_machuyendi'].get():
         messagebox.showwarning("Lỗi", "Không tìm thấy mã chuyến đi. Vui lòng chọn lại.")
         return
    set_form_state(is_enabled=True, widgets=widgets)
    widgets['entry_machuyendi'].config(state='disabled') 
    widgets['cbb_taixe'].focus() 

def luu_chuyendi_da_sua(widgets):
    """(LOGIC SỬA) Lưu thay đổi (UPDATE) sau khi sửa."""
    machuyendi = widgets['entry_machuyendi'].get()
    if not machuyendi:
        messagebox.showwarning("Thiếu dữ liệu", "Không có Mã chuyến đi để cập nhật")
        return False

    try:
        manv = widgets['cbb_taixe_var'].get().split(' - ')[0]
        bienso = widgets['cbb_xe_var'].get()
        diembd = widgets['entry_diembd'].get()
        diemkt = widgets['entry_diemkt'].get()
        
        # === SỬA LOGIC THỜI GIAN ===
        ngay_bd_str = widgets['date_bd'].get_date().strftime('%Y-%m-%d')
        tg_batdau = ngay_bd_str # <--- CHỈ LƯU NGÀY

        # Lấy thời gian kết thúc từ CSDL (nếu tài xế đã hoàn thành)
        # Chúng ta không cho Admin sửa thời gian kết thúc nữa
        # tg_ketthuc = None (Bỏ qua)
        
        trangthai_text = widgets['cbb_trangthai_var'].get()
        trangthai_map = {"Đã gán": 0, "Đang thực hiện": 1, "Hoàn thành": 2, "Hủy": 3}
        trangthai_value = trangthai_map.get(trangthai_text, 0)
        
        if not manv or not bienso or not diembd:
            messagebox.showwarning("Thiếu dữ liệu", "Tài xế, Xe và Điểm bắt đầu không được rỗng")
            return False

    except Exception as e:
        messagebox.showerror("Lỗi định dạng", f"Dữ liệu nhập không hợp lệ: {e}")
        return False

    conn = utils.connect_db()
    if conn is None: return False
        
    try:
        cur = conn.cursor()
        
        # === SỬA SQL UPDATE ===
        # Bỏ ThoiGianKetThuc ra khỏi lệnh UPDATE của Admin
        sql = """
        UPDATE ChuyenDi SET 
            MaNhanVien = ?, BienSoXe = ?, DiemBatDau = ?, DiemKetThuc = ?,
            ThoiGianBatDau = ?, TrangThai = ?
        WHERE MaChuyenDi = ?
        """
        cur.execute(sql, (
            manv, bienso, diembd, diemkt, 
            tg_batdau, trangthai_value, # <--- BỎ tg_ketthuc
            machuyendi
        ))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã cập nhật thông tin chuyến đi")
        return True
        
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật:\n{str(e)}")
        return False
    finally:
        if conn: conn.close()

def save_data(widgets):
    """Lưu dữ liệu, tự động kiểm tra xem nên Thêm mới (INSERT) hay Cập nhật (UPDATE)."""
    user_role = widgets.get("user_role", "Admin")
    user_username = widgets.get("user_username", "")
    
    if widgets['entry_machuyendi'].get():
        success = luu_chuyendi_da_sua(widgets)
    else:
        success = them_chuyendi(widgets)
    
    if success:
        load_data(widgets, user_role, user_username) 

def xoa_chuyendi_vinhvien(widgets):
    tree = widgets['tree']
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một chuyến đi trong danh sách để xóa")
        return
        
    machuyendi = widgets['entry_machuyendi'].get() 

    if not machuyendi:
        messagebox.showwarning("Lỗi", "Không tìm thấy mã chuyến đi. Vui lòng chọn lại.")
        return

    msg_xacnhan = (
        f"BẠN CÓ CHẮC CHẮN MUỐN XÓA VĨNH VIỄN CHUYẾN ĐI '{machuyendi}'?\n\n"
        "CẢNH BÁO: Thao tác này KHÔNG THỂ hoàn tác.\n"
    )
    if not messagebox.askyesno("XÁC NHẬN XÓA VĨNH VIỄN", msg_xacnhan):
        return

    conn = utils.connect_db()
    if conn is None: return
        
    try:
        cur = conn.cursor()
        
        # Xóa các bản ghi tham chiếu trong NhatKyNhienLieu trước (nếu có)
        # BẠN CẦN KIỂM TRA LẠI CSDL XEM CÓ KHÓA NGOẠI NÀY KHÔNG
        # cur.execute("DELETE FROM NhatKyNhienLieu WHERE MaChuyenDi=?", (machuyendi,))
        
        cur.execute("DELETE FROM ChuyenDi WHERE MaChuyenDi=?", (machuyendi,))
        conn.commit()
        messagebox.showinfo("Thành công", f"Đã xóa vĩnh viễn chuyến đi '{machuyendi}'.")
        
        user_role = widgets.get("user_role", "Admin")
        user_username = widgets.get("user_username", "")
        load_data(widgets, user_role, user_username)
            
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể xóa chuyến đi (Có thể do dữ liệu liên quan):\n{str(e)}")
    finally:
        if conn: conn.close()

# === CÁC HÀM CỦA TÀI XẾ ===
def bat_dau_chuyen_di(widgets, user_username, user_role):
    """(Tài xế) Cập nhật trạng thái chuyến đi thành 'Đang thực hiện'."""
    
    machuyendi = widgets['entry_machuyendi'].get()
    if not machuyendi:
        messagebox.showwarning("Chưa chọn", "Vui lòng chọn một chuyến đi từ danh sách.")
        return

    manv_dang_nhap = get_manv_from_username(user_username)
    conn = utils.connect_db()
    if conn is None: return

    try:
        cur = conn.cursor()
        cur.execute("SELECT TrangThai, MaNhanVien FROM ChuyenDi WHERE MaChuyenDi = ?", (machuyendi,))
        trip = cur.fetchone()

        if not trip or trip.MaNhanVien != manv_dang_nhap:
            messagebox.showerror("Lỗi", "Bạn không có quyền thao tác trên chuyến đi này.")
            return
        
        if trip.TrangThai == 0: # 0 = "Đã gán"
            if messagebox.askyesno("Xác nhận", "Bạn có muốn BẮT ĐẦU chuyến đi này?"):
                sql_update = "UPDATE ChuyenDi SET TrangThai = 1, ThoiGianBatDau = GETDATE() WHERE MaChuyenDi = ?"             
                cur.execute(sql_update, (machuyendi,))
                conn.commit()
                messagebox.showinfo("Thành công", "Bắt đầu chuyến đi.")
        elif trip.TrangThai == 1:
            messagebox.showinfo("Thông báo", "Chuyến đi này đang được thực hiện.")
        else:
            messagebox.showwarning("Không thể", "Chuyến đi đã hoàn thành.")

    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật:\n{str(e)}")
    finally:
        if conn: conn.close()
        load_data(widgets, user_role, user_username)

def xac_nhan_hoan_thanh(widgets, user_username, user_role):
    """(Tài xế) Xác nhận hoàn thành chuyến đi đang thực hiện."""
    
    machuyendi = widgets['entry_machuyendi'].get()
    if not machuyendi:
        messagebox.showwarning("Chưa chọn", "Vui lòng chọn một chuyến đi từ danh sách.")
        return

    manv_dang_nhap = get_manv_from_username(user_username)
    if not manv_dang_nhap:
        messagebox.showerror("Lỗi", "Không tìm thấy mã nhân viên của bạn.")
        return
    
    conn = utils.connect_db()
    if conn is None: return

    try:
        cur = conn.cursor()
        
        cur.execute("SELECT TrangThai, MaNhanVien FROM ChuyenDi WHERE MaChuyenDi = ?", (machuyendi,))
        trip = cur.fetchone()

        if not trip:
            messagebox.showerror("Lỗi", "Không tìm thấy chuyến đi.")
            return
        
        if trip.MaNhanVien != manv_dang_nhap:
            messagebox.showerror("Lỗi", "Bạn không có quyền xác nhận chuyến đi này.")
            return
        
        if trip.TrangThai == 1: # 1 = "Đang thực hiện"
            if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xác nhận HOÀN THÀNH chuyến đi này?"):
                sql_update = """
                UPDATE ChuyenDi 
                SET TrangThai = 2, ThoiGianKetThuc = GETDATE()
                WHERE MaChuyenDi = ?
                """
                cur.execute(sql_update, (machuyendi,))
                conn.commit()
                messagebox.showinfo("Thành công", "Đã xác nhận hoàn thành chuyến đi.")
        elif trip.TrangThai == 2: # 2 = "Hoàn thành"
            messagebox.showinfo("Thông báo", "Chuyến đi này đã được hoàn thành.")
        else:
            messagebox.showwarning("Không thể", "Chỉ có thể xác nhận chuyến đi đang 'Đang thực hiện'.")

    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật:\n{str(e)}")
    finally:
        if conn: conn.close()
        load_data(widgets, user_role, user_username)

def huy_chuyen_di(widgets, user_username, user_role):
    """(Tài xế) Cập nhật trạng thái chuyến đi thành 'Hủy'."""
    
    machuyendi = widgets['entry_machuyendi'].get()
    if not machuyendi:
        messagebox.showwarning("Chưa chọn", "Vui lòng chọn một chuyến đi từ danh sách.")
        return

    manv_dang_nhap = get_manv_from_username(user_username)
    conn = utils.connect_db()
    if conn is None: return

    try:
        cur = conn.cursor()
        cur.execute("SELECT TrangThai, MaNhanVien FROM ChuyenDi WHERE MaChuyenDi = ?", (machuyendi,))
        trip = cur.fetchone()

        if not trip or trip.MaNhanVien != manv_dang_nhap:
            messagebox.showerror("Lỗi", "Bạn không có quyền thao tác trên chuyến đi này.")
            return
        
        if trip.TrangThai in [0, 1]: # Có thể hủy khi "Đã gán" hoặc "Đang thực hiện"
            if messagebox.askyesno("XÁC NHẬN HỦY", "Bạn có chắc chắn muốn HỦY chuyến đi này? Thao tác này không thể hoàn tác.", icon='warning'):
                sql_update = "UPDATE ChuyenDi SET TrangThai = 3 WHERE MaChuyenDi = ?"
                cur.execute(sql_update, (machuyendi,))
                conn.commit()
                messagebox.showinfo("Thành công", "Đã hủy chuyến đi.")
        elif trip.TrangThai == 3:
            messagebox.showinfo("Thông báo", "Chuyến đi này đã bị hủy từ trước.")
        else: # trip.TrangThai == 2 (Hoàn thành)
            messagebox.showwarning("Không thể", "Không thể hủy chuyến đi đã 'Hoàn thành'.")

    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi SQL", f"Không thể cập nhật:\n{str(e)}")
    finally:
        if conn: conn.close()
        load_data(widgets, user_role, user_username)

# ================================================================
# PHẦN 4: HÀM TẠO TRANG (SỬA ĐỂ PHÂN QUYỀN)
# ================================================================

# ================================================================
# PHẦN 4: HÀM TẠO TRANG (SỬA ĐỂ PHÂN QUYỀN VÀ BỎ Ô GIỜ)
# ================================================================

def create_page(master, user_role, user_username): # <-- SỬA SIGNATURE
    """
    Hàm này được main.py gọi. 
    Tạo nội dung trang dựa trên vai trò (user_role).
    """
    
    # 1. TẠO FRAME CHÍNH
    page_frame = ttk.Frame(master, style="TFrame")
    utils.setup_theme(page_frame) 
    
    # === THÊM STYLE CHO NÚT HỦY (MÀU ĐỎ) ===
    try:
        style = ttk.Style()
        danger_color = "#DC3545" # Màu đỏ bootstrap
        danger_active = "#B02A37"
        style.configure("Danger.TButton", 
                        font=("Calibri", 11, "bold"),
                        background=danger_color, 
                        foreground="white",
                        relief="flat",
                        padding=5)
        style.map("Danger.TButton",
                  background=[('active', danger_active)],
                  relief=[('pressed', 'sunken')])
    except Exception as e:
        print(f"Lỗi tạo style Danger.TButton: {e}")
        
    # 2. TẠO GIAO DIỆN
    lbl_title = ttk.Label(page_frame, text="QUẢN LÝ CHUYẾN ĐI", style="Title.TLabel")
    lbl_title.pack(pady=15) 

    # --- Frame Form (Admin) ---
    frame_info = ttk.Frame(page_frame, style="TFrame")
    if user_role == "Admin":
        frame_info.pack(pady=5, padx=20, fill="x")

    # --- Hàng 1 ---
    ttk.Label(frame_info, text="Mã chuyến đi:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
    entry_machuyendi = ttk.Entry(frame_info, width=30, state='disabled')
    entry_machuyendi.grid(row=0, column=1, padx=5, pady=8, sticky="w")
    ttk.Label(frame_info, text="Trạng thái:").grid(row=0, column=2, padx=15, pady=8, sticky="w")
    trangthai_options = ["Đã gán", "Đang thực hiện", "Hoàn thành", "Hủy"]
    cbb_trangthai_var = tk.StringVar()
    cbb_trangthai = ttk.Combobox(frame_info, textvariable=cbb_trangthai_var, values=trangthai_options, width=38, state='readonly')
    cbb_trangthai.grid(row=0, column=3, padx=5, pady=8, sticky="w")
    cbb_trangthai.set("Đã gán")
    
    # --- Hàng 2 ---
    ttk.Label(frame_info, text="Tài xế:").grid(row=1, column=0, padx=5, pady=8, sticky="w")
    cbb_taixe_var = tk.StringVar()
    cbb_taixe = ttk.Combobox(frame_info, textvariable=cbb_taixe_var, width=28, state='readonly')
    cbb_taixe.grid(row=1, column=1, padx=5, pady=8, sticky="w")
    cbb_taixe['values'] = load_taixe_combobox()
    ttk.Label(frame_info, text="Xe:").grid(row=1, column=2, padx=15, pady=8, sticky="w")
    cbb_xe_var = tk.StringVar()
    cbb_xe = ttk.Combobox(frame_info, textvariable=cbb_xe_var, width=38, state='readonly')
    cbb_xe.grid(row=1, column=3, padx=5, pady=8, sticky="w")
    cbb_xe['values'] = load_xe_combobox()
    
    # --- Hàng 3 ---
    ttk.Label(frame_info, text="Điểm bắt đầu:").grid(row=2, column=0, padx=5, pady=8, sticky="w")
    entry_diembd = ttk.Entry(frame_info, width=30)
    entry_diembd.grid(row=2, column=1, padx=5, pady=8, sticky="w")
    ttk.Label(frame_info, text="Điểm kết thúc:").grid(row=2, column=2, padx=15, pady=8, sticky="w")
    entry_diemkt = ttk.Entry(frame_info, width=40)
    entry_diemkt.grid(row=2, column=3, padx=5, pady=8, sticky="w")

    # ==================================
    # === SỬA HÀNG 4 (THỜI GIAN) ===
    # ==================================
    date_entry_style_options = {
        'width': 28, 'date_pattern': 'yyyy-MM-dd', # Sửa width
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

    # Đặt date_bd vào hàng 3, cột 0 (thay cho hàng 4 cũ)
    ttk.Label(frame_info, text="Ngày bắt đầu:").grid(row=3, column=0, padx=5, pady=8, sticky="w")
    date_bd = DateEntry(frame_info, **date_entry_style_options)
    date_bd.grid(row=3, column=1, padx=5, pady=8, sticky="w")

    # Tạo các widget giả (để code không bị lỗi NameError ở dưới)
    # Chúng không được hiển thị (pack/grid)
    entry_giobd = ttk.Entry(frame_info)
    date_kt = DateEntry(frame_info)
    entry_giokt = ttk.Entry(frame_info)
    # ==================================
    # === KẾT THÚC SỬA HÀNG 4 ===
    # ==================================

    frame_info.columnconfigure(1, weight=1)
    frame_info.columnconfigure(3, weight=1)

    # ===== Frame nút (Admin) =====
    frame_btn = ttk.Frame(page_frame, style="TFrame")
    if user_role == "Admin":
        frame_btn.pack(pady=10)

    # ===== Frame nút (Tài xế) =====
    frame_taixe_btn = ttk.Frame(page_frame, style="TFrame")
    if user_role == "TaiXe":
        frame_taixe_btn.pack(pady=10)
        
    # ===== Bảng danh sách chuyến đi (Dùng chung) =====
    lbl_ds = ttk.Label(page_frame, text="Danh sách chuyến đi (Sắp xếp mới nhất)", style="Header.TLabel")
    if user_role == "TaiXe":
        lbl_ds.config(text="Danh sách chuyến đi của bạn")
    lbl_ds.pack(pady=(10, 5), padx=20, anchor="w")

    frame_tree = ttk.Frame(page_frame, style="TFrame")
    frame_tree.pack(pady=10, padx=20, fill="both", expand=True) 
    scrollbar_y = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, style="Vertical.TScrollbar")
    scrollbar_x = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, style="Horizontal.TScrollbar")
    columns = ("ma_cd", "ten_tx", "bienso", "tg_bd", "tg_kt", "trangthai")
    tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10,
                    yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X) 
    tree.heading("ma_cd", text="Mã CĐ")
    tree.column("ma_cd", width=60, anchor="center")
    tree.heading("ten_tx", text="Tên Tài xế")
    tree.column("ten_tx", width=150)
    tree.heading("bienso", text="Biển số xe")
    tree.column("bienso", width=100)
    tree.heading("tg_bd", text="Thời gian bắt đầu")
    tree.column("tg_bd", width=150)
    tree.heading("tg_kt", text="Thời gian kết thúc")
    tree.column("tg_kt", width=150)
    tree.heading("trangthai", text="Trạng thái")
    tree.column("trangthai", width=120, anchor="center")

    tree.pack(fill="both", expand=True)
    
    # 3. TẠO TỪ ĐIỂN 'widgets'
    widgets = {
        "tree": tree,
        "entry_machuyendi": entry_machuyendi,
        "cbb_taixe": cbb_taixe,
        "cbb_xe": cbb_xe,
        "entry_diembd": entry_diembd,
        "entry_diemkt": entry_diemkt,
        "date_bd": date_bd,
        "entry_giobd": entry_giobd,
        "date_kt": date_kt,
        "entry_giokt": entry_giokt,
        "cbb_trangthai": cbb_trangthai,
        "cbb_taixe_var": cbb_taixe_var,
        "cbb_xe_var": cbb_xe_var,
        "cbb_trangthai_var": cbb_trangthai_var,
        "user_role": user_role,
        "user_username": user_username
    }

    # ===== SỬA: Tạo các nút dựa trên vai trò =====
    if user_role == "Admin":
        btn_them = ttk.Button(frame_btn, text="Thêm", width=8, command=lambda: clear_input(widgets)) 
        btn_them.grid(row=0, column=0, padx=10)
        btn_luu = ttk.Button(frame_btn, text="Lưu", width=8, command=lambda: save_data(widgets)) 
        btn_luu.grid(row=0, column=1, padx=10)
        btn_sua = ttk.Button(frame_btn, text="Sửa", width=8, command=lambda: chon_chuyendi_de_sua(widgets)) 
        btn_sua.grid(row=0, column=2, padx=10)
        btn_huy = ttk.Button(frame_btn, text="Hủy", width=8, command=lambda: load_data(widgets, user_role, user_username)) 
        btn_huy.grid(row=0, column=3, padx=10)
        btn_xoa = ttk.Button(frame_btn, text="Xóa", width=8, command=lambda: xoa_chuyendi_vinhvien(widgets)) 
        btn_xoa.grid(row=0, column=4, padx=10)
    
    if user_role == "TaiXe":
        # Nút 1: Bắt đầu (Màu xanh)
        btn_bat_dau = ttk.Button(frame_taixe_btn, text="Bắt đầu thực hiện", 
                                 style="Accent.TButton", 
                                 command=lambda: bat_dau_chuyen_di(widgets, user_username, user_role)
                                 )
        btn_bat_dau.grid(row=0, column=0, padx=10, pady=5)
        
        # Nút 2: Hoàn thành (Màu xanh)
        btn_hoan_thanh = ttk.Button(frame_taixe_btn, text="Xác nhận Hoàn Thành", 
                                     style="Accent.TButton",
                                     command=lambda: xac_nhan_hoan_thanh(widgets, user_username, user_role)
                                     )
        btn_hoan_thanh.grid(row=0, column=1, padx=10, pady=5)
        
        # Nút 3: Hủy (Màu đỏ)
        btn_huy_chuyen = ttk.Button(frame_taixe_btn, text="Hủy chuyến", 
                                 style="Danger.TButton", 
                                 command=lambda: huy_chuyen_di(widgets, user_username, user_role)
                                 )
        btn_huy_chuyen.grid(row=0, column=2, padx=10, pady=5)

    # 4. KẾT NỐI BINDING (SỰ KIỆN CLICK)
    tree.bind("<<TreeviewSelect>>", lambda event: on_item_select(event, widgets)) 

    # 5. TẢI DỮ LIỆU LẦN ĐẦU
    load_data(widgets, user_role, user_username)
    
    # 6. TRẢ VỀ FRAME CHÍNH
    return page_frame
# ================================================================
# PHẦN 5: CHẠY THỬ NGHIỆM
# ================================================================
if __name__ == "__main__":
    
    test_root = tk.Tk()
    test_root.title("Test Quản lý Chuyến Đi")
    
    def center_window(w, h):
        ws = test_root.winfo_screenwidth()
        hs = test_root.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        test_root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    center_window(950, 700)
    test_root.resizable(False, False)
    
    # SỬA: Giả lập chạy với vai trò Admin
    page = create_page(test_root, "Admin", "test_admin") 
    page.pack(fill="both", expand=True)
    
    test_root.mainloop()