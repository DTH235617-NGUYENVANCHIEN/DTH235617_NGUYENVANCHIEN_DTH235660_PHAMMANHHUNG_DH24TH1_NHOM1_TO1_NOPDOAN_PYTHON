<img width="1117" height="642" alt="image" src="https://github.com/user-attachments/assets/80fbfc62-ba07-40aa-8dcb-843af7c9df5f" />




<p align="center">
    
</p>

**Tác giả:**
*   Nguyễn Văn Chiến - DTH235617
*   Phạm Mạnh Hùng- DTH235660

**Lớp:** DH24TH1

**Giảng viên hướng dẫn:** Ths. Nguyễn Ngọc Minh

---
<img width="1011" height="574" alt="image" src="https://github.com/user-attachments/assets/d7ec0a35-130a-4667-ad16-e89ce2bc9d82" />

---

<img width="1018" height="573" alt="image" src="https://github.com/user-attachments/assets/19477c77-18bb-4605-a076-370c82a6ae4b" />

---

<img width="1017" height="568" alt="image" src="https://github.com/user-attachments/assets/f2dca990-7d50-492f-8241-07d061415b31" />

## 2. KHẢO SÁT HỆ THỐNG

### 2.1. Tình hình thực tế

Qua khảo sát thực tế, tình hình quản lý vận tải tại các doanh nghiệp vừa và nhỏ bộc lộ nhiều hạn chế:

1.  **Phương thức quản lý thủ công (Excel, Sổ sách):**
    * **Tính toàn vẹn dữ liệu:** Dữ liệu phân mảnh, lưu trên nhiều file khác nhau (file theo dõi xe, file chấm công tài xế, file chi phí...). Điều này dẫn đến tình trạng "tam sao thất bản" khi tổng hợp.
    * **Sai sót thao tác:** Việc điều phối (Ai lái xe nào? Xe nào rảnh? Xe nào sắp đến hạn đăng kiểm?) phụ thuộc vào trí nhớ của người quản lý hoặc các file Excel phức tạp, nguy cơ sai sót cao.
    * **Bảo mật:** Dữ liệu chi phí (xăng dầu, sửa chữa) dễ bị mất mát, hư hỏng hoặc chỉnh sửa trái phép do thiếu cơ chế phân quyền.
    * **Khả năng truy xuất:** Việc tra cứu lịch sử (Xe này đã sửa gì? Tài xế này tháng này chạy bao nhiêu chuyến?) tốn rất nhiều thời gian.

2.  **Phương thức quản lý bằng phần mềm chuyên dụng (Hiện có):**
    * Phần lớn các phần mềm quản lý vận tải chuyên nghiệp (các giải pháp SaaS) thường có chi phí cao, phức tạp và dư thừa chức năng so với nhu cầu của doanh nghiệp vừa và nhỏ.
    * Các hệ thống này thường tập trung vào GPS và bản đồ, nhưng bỏ qua nghiệp vụ quản lý chi phí và duyệt chi nội bộ (bảo trì, nhiên liệu) một cách chi tiết.

Từ thực trạng trên, nhu cầu phát triển một hệ thống "cây nhà lá vườn" (in-house) là rất cấp thiết. Hệ thống này cần gọn nhẹ, đúng trọng tâm nghiệp vụ, dễ sử dụng cho cả Admin và Tài xế, và đặc biệt là giải quyết bài toán cốt lõi: **Minh bạch hóa dữ liệu và Chi phí**.

### 2.2. Mục tiêu của đồ án

#### a) Mục tiêu tổng quát

Xây dựng một Hệ thống phần mềm Quản lý Vận tải hoàn chỉnh, hoạt động trên nền tảng Desktop (Python Tkinter). Hệ thống này nhằm mục đích tin học hóa toàn bộ quy trình nghiệp vụ liên quan đến việc quản lý xe và tài xế, thay thế các phương pháp thủ công, đảm bảo tính **Chính xác - An toàn - Nhanh chóng - Minh bạch**.

#### b) Mục tiêu cụ thể

* **Về mặt Nghiệp vụ (Chức năng):**
    * **Số hóa và Chuẩn hóa:** Quản lý tập trung thông tin phương tiện (`Xe`), nhân sự (`NhanVien`, `TaiXe`), và chi phí (`LichSuBaoTri`, `NhatKyNhienLieu`).
    * **Tự động hóa Quy trình:** Tự động cập nhật trạng thái "Rảnh" / "Đang lái" của tài xế khi họ nhận hoặc hoàn thành chuyến đi.
    * **Phân quyền rõ ràng:** Xây dựng cơ chế phân quyền chi tiết cho 2 nhóm đối tượng:
        * **Quản trị viên (Admin):** Quản lý toàn bộ hệ thống, phân công chuyến đi, duyệt chi phí.
        * **Tài xế (TaiXe):** Thực thi chuyến đi, báo cáo chi phí (nhiên liệu, sửa chữa vặt).
    * **Minh bạch Chi phí:** Cung cấp quy trình báo cáo nhiên liệu (Tài xế tạo -> Admin Duyệt/Từ chối).
* **Về mặt Kỹ thuật:**
    * **Áp dụng công nghệ:** Thiết kế và phát triển hệ thống dựa trên mô hình Client-Server, sử dụng ngôn ngữ Python, thư viện Tkinter và CSDL SQL Server.
    * **Giao diện thân thiện:** Xây dựng giao diện người dùng (UI/UX) trực quan, dễ sử dụng cho cả hai vai trò.
    * **Đảm bảo an toàn:** Đảm bảo tính bảo mật dữ liệu, mã hóa mật khẩu (SHA-256) và ngăn chặn các truy cập trái phép.

---

## 3. CÔNG NGHỆ SỬ DỤNG

* **Ngôn ngữ lập trình:** Python 3.x
* **Giao diện người dùng (GUI):** Tkinter (sử dụng `ttk` và `ttkthemes` để cải thiện giao diện).
* **Thư viện hỗ trợ:**
    * `pyodbc`: Cung cấp kết nối tuân thủ ODBC đến SQL Server.
    * `tkcalendar`: Cung cấp widget Lịch (DateEntry) thân thiện.
    * `hashlib`: Dùng để băm mật khẩu (SHA-256) trước khi lưu vào CSDL.
* **Cơ sở dữ liệu:** Microsoft SQL Server.
* **Môi trường phát triển (IDE):** Visual Studio Code.

---

## 4. THIẾT KẾ VÀ CÀI ĐẶT CHƯƠNG TRÌNH

### 4.1. Thiết kế Cơ sở dữ liệu (CSDL)

CSDL được thiết kế để chuẩn hóa và liên kết các nghiệp vụ cốt lõi.

<p align="center">
    <b></b>
  <i>Hình 4.1: Sơ đồ quan hệ (ERD) của CSDL QL_VanTai</i>
</p>

**Thiết kế các bảng chính:**

*   **Bảng `NhanVien`:** Bảng cha lưu thông tin chung (MaNhanVien, HoVaTen, TrangThai [1=Làm việc, 0=Nghỉ]).
*   **Bảng `TaiXe`:** Bảng con của `NhanVien`, lưu thông tin bằng lái và `TrangThaiTaiXe` (1=Rảnh, 2=Đang lái).
*   **Bảng `TaiKhoan`:** Quản lý đăng nhập, liên kết `TenDangNhap` với `MaNhanVien` và lưu `VaiTro` (Admin/TaiXe).
*   **Bảng `Xe`:** Quản lý phương tiện, chứa khóa ngoại `MaNhanVienHienTai` (liên kết đến `NhanVien`).
*   **Bảng `ChuyenDi`:** Bảng nghiệp vụ chính, liên kết `MaNhanVien` và `BienSoXe`.
*   **Bảng `LichSuBaoTri`:** Chứa khóa ngoại `MaNhanVienNhap` để theo dõi người nhập.
*   **Bảng `NhatKyNhienLieu`:** Chứa khóa ngoại `MaNhanVien` (người đổ) và `TrangThaiDuyet` (0=Chờ, 1=Duyệt, 2=Từ chối).

*(Bạn có thể dán thêm các hình ảnh thiết kế chi tiết từng bảng tại đây nếu muốn)*

### 4.2. Giao diện và Chức năng (Chi tiết)

#### 4.2.1. Giao diện Đăng nhập

<p align="center">
  <b></b>
  <i>Hình 4.2.1: Giao diện Đăng nhập (login.py)</i>
</p>

* **Mục đích:** Xác thực người dùng và phân luồng nghiệp vụ.
* **Luồng nghiệp vụ:**
    1.   Người dùng nhập Tên đăng nhập và Mật khẩu.
    2.   Hệ thống băm (SHA-256) mật khẩu nhập vào.
    3.   Truy vấn CSDL (`TaiKhoan`) để kiểm tra `TenDangNhap` và `MatKhau` (đã hash) có khớp không.
    4.   Nếu khớp, hệ thống lấy ra `VaiTro` (Admin/TaiXe) và `TenDangNhap`.
    5.   Đóng form Đăng nhập, mở form `main.py` và truyền 2 tham số `VaiTro`, `TenDangNhap` sang.
    6.   Nếu không khớp, hiển thị thông báo "Sai tên đăng nhập hoặc mật khẩu".

#### 4.2.2. Giao diện Chính (Main Form) & Phân quyền

<p align="center">
  <b></b>
  <i>Hình 4.2.2: Giao diện chính (Vai trò: Admin)</i>
</p>

* **Mục đích:** Là giao diện điều hướng chính (container) cho tất cả các chức năng.
* **Luồng nghiệp vụ (Phân quyền):**
    1.   Khi form `main.py` được tải, nó nhận 2 tham số `USER_ROLE` và `USER_USERNAME`.
    2.   Một hàm `apply_permissions(role)` được gọi.
    3.   Dựa trên `USER_ROLE`, hàm này sẽ ẩn (dùng `.pack_forget()`) các nút chức năng mà vai trò đó không có quyền truy cập.
    4.   **Ví dụ:** Nếu `USER_ROLE` là "TaiXe", các nút "Quản lý Xe", "Quản lý Tài xế", "Quản lý Nhân viên", "Quản lý Tài khoản" sẽ bị ẩn đi.
    5.   Khi người dùng nhấn vào một nút (ví dụ: "Quản lý Xe"), `main.py` sẽ gọi hàm `create_page` từ file `quanly_xe.py` và hiển thị nó trong khung nội dung chính.

#### 4.2.3. Chức năng Quản lý Nhân viên (Admin)

<p align="center">
  <b></b>
  <i>Hình 4.2.3: Giao diện Quản lý Nhân viên (quanly_nhanvien.py)</i>
</p>

* **Mục đích:** Quản lý hồ sơ gốc của *tất cả* nhân viên trong công ty (bao gồm cả Admin, Kế toán, và Tài xế).
* **Người thực hiện:** Admin.
* **Luồng nghiệp vụ:**
    *   Cung cấp các chức năng CRUD (Thêm, Sửa, Xóa) cơ bản cho nhân viên.
    *   **Logic Sửa/Lưu:** Sử dụng biến nội bộ `current_mode` ("ADD" hoặc "EDIT") để xác định nút "Lưu" sẽ chạy lệnh `INSERT` hay `UPDATE`.
    *   **Xóa:** Khi xóa một nhân viên, hệ thống thực hiện xóa xếp tầng (cascade delete) để xóa tất cả dữ liệu liên quan (tài khoản, thông tin tài xế, chuyến đi,...) trước khi xóa nhân viên gốc, đảm bảo toàn vẹn CSDL.
* **Liên kết CSDL:** Thao tác trực tiếp trên bảng `NhanVien`.

#### 4.2.4. Chức năng Quản lý Tài xế (Admin)

<p align="center">
  <b></b>
  <i>Hình 4.2.4: Giao diện Quản lý Tài xế (quanly_taixe.py)</i>
</p>

* **Mục đích:** Chuyên biệt hóa thông tin cho các nhân viên có vai trò là "Tài xế".
* **Người thực hiện:** Admin.
* **Luồng nghiệp vụ:**
    *   Khi "Thêm" tài xế, Admin phải nhập `MaNhanVien` (phải tồn tại trong bảng `NhanVien`), Hạng bằng lái, Ngày hết hạn...
    *   Admin có thể cập nhật trạng thái "Đang làm việc" / "Nghỉ" (ảnh hưởng đến `NhanVien.TrangThai`) và "Rảnh" / "Đang lái" (ảnh hưởng đến `TaiXe.TrangThaiTaiXe`).
* **Liên kết CSDL:** Thao tác trên cả hai bảng `NhanVien` (cập nhật thông tin chung) và `TaiXe` (cập nhật thông tin bằng lái).

#### 4.2.5. Chức năng Quản lý Xe (Admin)

<p align="center">
  <b></b>
  <i>Hình 4.2.5: Giao diện Quản lý Xe (quanly_xe.py)</i>
</p>

* **Mục đích:** Quản lý toàn bộ phương tiện của công ty.
* **Người thực hiện:** Admin.
* **Luồng nghiệp vụ:**
    *   Cung cấp CRUD cho thông tin xe (Biển số, Loại xe, Hãng, VIN, Hạn đăng kiểm...).
    *   **Gán tài xế:** Admin có thể chọn một tài xế từ combobox "Tên người lái" (dữ liệu lấy từ bảng `TaiXe`) để gán cho chiếc xe này (cập nhật cột `Xe.MaNhanVienHienTai`).
    *   **Quản lý trạng thái:** Cập nhật trạng thái xe (Hoạt động, Bảo trì, Hỏng).
* **Liên kết CSDL:** Thao tác chính trên bảng `Xe`. Đọc dữ liệu từ `TaiXe` và `NhanVien` để hiển thị combobox.

#### 4.2.6. Chức năng Quản lý Tài khoản (Admin)

<p align="center">
  <b></b>
  <i>Hình 4.2.6: Giao diện Quản lý Tài khoản (quanly_taikhoan.py)</i>
</p>

* **Mục đích:** Tạo, xóa và phân quyền đăng nhập cho người dùng.
* **Người thực hiện:** Admin.
* **Luồng nghiệp vụ:**
    *   **Thêm:** Admin nhập "Tên đăng nhập", "Mật khẩu", chọn "Nhân viên" (từ combobox) và "Vai trò" (Admin/TaiXe). Mật khẩu được hash SHA-256 trước khi `INSERT` vào CSDL.
    *   **Sửa:** Admin có thể thay đổi "Vai trò" hoặc "Nhân viên" được liên kết. Nếu Admin nhập mật khẩu mới, mật khẩu sẽ được hash và `UPDATE`. Nếu Admin để nguyên placeholder `******`, mật khẩu cũ được giữ nguyên.
* **Liên kết CSDL:** Thao tác trên bảng `TaiKhoan`. Đọc từ `NhanVien` để điền vào combobox.

#### 4.2.7. Chức năng Quản lý Chuyến đi (Admin & Tài xế)

<p align="center">
  <b></b>
  <i>Hình 4.2.7: Giao diện Chuyến đi (Vai trò: Admin)</i>
</p>

* **Mục đích:** Giao diện nghiệp vụ chính để phân công và thực thi công việc.
* **Người thực hiện:** Admin và Tài xế (giao diện thay đổi theo vai trò).
* **Luồng nghiệp vụ (Admin):**
    *   **Tạo chuyến đi:** Admin nhấn "Thêm".
    *   **Lọc thông minh:** Khi Admin chọn một Tài xế (ví dụ: "Nguyễn Văn An") từ combobox "Tài xế", hệ thống sẽ kiểm tra xem tài xế đó có đang giữ xe nào không.
        *   Nếu tài xế **đang giữ xe** (ví dụ: 51G-123.45) -> Combobox "Xe" chỉ hiển thị `[51G-123.45]` và tự động chọn.
        *   Nếu tài xế **rảnh** -> Combobox "Xe" hiển thị tất cả các xe đang rảnh khác.
    *   **Lưu (Gán việc):** Admin nhấn "Lưu", một chuyến đi mới được `INSERT` vào bảng `ChuyenDi` với `TrangThai = 0` (Đã gán).
* **Luồng nghiệp vụ (Tài xế):**
    *   Tài xế chỉ thấy các chuyến đi được gán cho mình (lọc bằng `WHERE MaNhanVien = ?`).
    *   **Bắt đầu:** Tài xế chọn chuyến đi (trạng thái "Đã gán") và nhấn "Bắt đầu thực hiện". Hệ thống chạy 2 lệnh SQL:
        1.   `UPDATE ChuyenDi SET TrangThai = 1` (Đang thực hiện).
        2.   `UPDATE TaiXe SET TrangThaiTaiXe = 2` (Đang lái).
    *   **Hoàn thành:** Tài xế nhấn "Xác nhận Hoàn thành". Hệ thống chạy 2 lệnh SQL:
        1.   `UPDATE ChuyenDi SET TrangThai = 2, ThoiGianKetThuc = GETDATE()` (Hoàn thành).
        2.   `UPDATE TaiXe SET TrangThaiTaiXe = 1` (Rảnh).
    *   **Hủy:** Tương tự như Hoàn thành, set `TrangThai = 3` và `TrangThaiTaiXe = 1`.

#### 4.2.8. Chức năng Lịch sử Bảo trì (Admin & Tài xế)

<p align="center">
  <b></b>
  <i>Hình 4.2.8: Giao diện Lịch sử Bảo trì (quanly_lichsubaotri.py)</i>
</p>

* **Mục đích:** Ghi lại nhật ký sửa chữa, bảo dưỡng và chi phí liên quan.
* **Luồng nghiệp vụ:**
    *   **Phân quyền xem:** Admin thấy tất cả. Tài xế chỉ thấy lịch sử của xe mình đang giữ.
    *   **Phân quyền sửa:** Admin có thể Thêm, Sửa, Xóa. Tài xế chỉ có thể Thêm (để báo cáo sửa vặt trên đường), không được Sửa/Xóa.
    *   **Theo dõi người nhập:** Khi Thêm, hệ thống tự động lấy `MaNhanVien` của người đang đăng nhập và lưu vào cột `MaNhanVienNhap`. Bảng hiển thị của Admin sẽ JOIN với bảng `NhanVien` để hiển thị tên người nhập.

#### 4.2.9. Chức năng Nhật ký Nhiên liệu (Admin & Tài xế)

<p align="center">
  <b></b>
  <i>Hình 4.2.9: Giao diện Nhật ký Nhiên liệu (Vai trò: Tài xế)</i>
</p>

* **Mục đích:** Quản lý chi phí nhiên liệu và quy trình duyệt chi.
* **Luồng nghiệp vụ (Tài xế):**
    *   Chỉ thấy nhật ký của mình.
    *   Nhấn "Thêm" để báo cáo (Số lít, Chi phí, Số Odo). Mọi nhật ký mới tạo mặc định `TrangThaiDuyet = 0` (Chờ duyệt).
    *   Tài xế có thể "Sửa" hoặc "Xóa" nhật ký, *chỉ khi* nó còn ở trạng thái "Chờ duyệt".
* **Luồng nghiệp vụ (Admin):**
    *   Thấy tất cả nhật ký. Form nhập liệu bị ẩn.
    *   Admin chọn một nhật ký đang "Chờ duyệt" và nhấn nút **"Duyệt"** (set `TrangThaiDuyet = 1`) hoặc **"Từ chối"** (set `TrangThaiDuyet = 2`).

#### 4.2.10. Chức năng Đổi mật khẩu & Đăng xuất

* **Mục đích:** Bảo mật tài khoản cá nhân và kết thúc phiên làm việc.
* **Luồng nghiệp vụ:**
    *   **Đổi mật khẩu:** (File `thongtin_taikhoan.py`) Người dùng phải nhập đúng mật khẩu cũ. Mật khẩu mới sau đó được hash và `UPDATE` vào CSDL.
    *   **Đăng xuất:** (File `main.py`) Hiển thị hộp thoại xác nhận. Nếu đồng ý, đóng Form Main và mở lại Form `login.py`. Nút này chỉ hiển thị cho Admin.
    *   **Thoát:** Đóng toàn bộ ứng dụng.

---

## 5. CÀI ĐẶT VÀ CHẠY THỬ

**Yêu cầu:**
*   Python 3.8+
*   Microsoft SQL Server (đã bật TCP/IP)

**Các bước cài đặt:**

1.   **Clone Repository:**
    ```bash
    git clone [https://github.com/ten-cua-ban/ten-du-an.git](https://github.com/ten-cua-ban/ten-du-an.git)
    cd ten-du-an
    ```

2.   **Cài đặt thư viện (Tạo môi trường ảo khuyên dùng):**
    ```bash
    pip install pyodbc tkcalendar ttkthemes
    ```

3.   **Cài đặt CSDL:**
    *   Mở SQL Server Management Studio (SSMS).
    *   Mở và chạy file `QL_VanTai.sql` (hoặc tên tương tự) để tạo CSDL, các bảng và dữ liệu mẫu.

4.   **Cấu hình kết nối:**
    *   Mở file `utils.py`.
    *   Chỉnh sửa chuỗi `connection_string` cho đúng với **Tên Server**, **Database** (`QL_VanTai`), **User ID** (`sa`) và **Password** của bạn.

5.   **Chạy chương trình:**
    ```bash
    python login.py
    ```
    *   (Tài khoản Admin mẫu: `admin` / `123`)
    *   (Tài khoản Tài xế mẫu: `an.nv` / `123`)

---

## 6. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

### Những chức năng đã triển khai
*   **Admin:** Quản lý toàn bộ dữ liệu gốc (Xe, Tài xế, Nhân viên, Tài khoản), phân công chuyến đi, và duyệt chi phí nhiên liệu.
*   **Tài xế:** Nhận và thực thi chuyến đi (Bắt đầu, Hoàn thành, Hủy), báo cáo chi phí (Nhiên liệu, Bảo trì vặt), và tự quản lý mật khẩu.
*   **Hệ thống:** Tự động cập nhật trạng thái Rảnh/Bận cho tài xế, tự động lọc danh sách xe theo tài xế, và theo dõi người nhập chi phí.

### Hướng phát triển trong tương lai
*   **Dashboard (Bảng điều khiển):** Thêm một trang Dashboard chính (trang chủ) hiển thị các biểu đồ (ví dụ: tổng chi phí nhiên liệu theo tháng, % xe đang hoạt động, tài xế có nhiều chuyến nhất).
*   **Cảnh báo tự động:** Tự động tô màu đỏ hoặc gửi thông báo trên giao diện chính khi xe sắp hết hạn đăng kiểm hoặc bảo hiểm trong vòng 30 ngày tới.
*   **Quản lý Lốp/Ắc-quy:** Thêm các module chi tiết hơn để theo dõi tuổi thọ và số km của lốp xe và ắc-quy.
*   **Tích hợp API/GPS:** (Nâng cao) Tích hợp bản đồ để theo dõi vị trí xe thời gian thực.
*   **Phiên bản Mobile:** Phát triển ứng dụng di động gọn nhẹ (ví dụ: dùng React Native hoặc Flutter) cho tài xế để báo cáo nhiên liệu và nhận/trả chuyến đi thuận tiện hơn.

---

## 7. TÀI LIỆU THAM KHẢO

*   (Thêm các link YouTube, Stack Overflow, hoặc tài liệu bạn đã tham khảo tại đây)
*   [GeeksforGeeks - Python Tkinter](https://www.geeksforgeeks.org/python-gui-tkinter/)
*   [pyodbc Wiki](https://github.com/mkleehammer/pyodbc/wiki)

