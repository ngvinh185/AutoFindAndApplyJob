---
name: topcv-auto-apply
description: Tự động ứng tuyển các job trên TopCV mà người dùng đã đánh dấu muốn apply trong file Excel (human_apply = 1) và agent chưa apply (ai_apply = 0), bằng cách mở trực tiếp link trong Excel. Dùng khi người dùng yêu cầu agent tự động nộp đơn / apply việc làm TopCV. Chạy sau skill topcv-job-screening.
---

# TopCV Auto Apply

## Mục tiêu
Đọc `topcv_jobs.xlsx`, tìm các job người dùng muốn apply nhưng agent chưa apply, mở job theo link trong Excel, nộp đơn bằng CV gần nhất, rồi cập nhật Excel.

## Công cụ
- `read_file`: đọc `topcv_jobs.xlsx`.
- Tool ghi/cập nhật Excel: cập nhật cột `ai_apply` của đúng dòng.
- Trình duyệt: mở URL, click, cuộn, đọc trang, tick checkbox.

## Cột Excel liên quan
`Tên việc làm`, `Công ty`, `Link`, `human_apply`, `ai_apply` (`1` = có, `0` = không).

## Điều kiện chọn job
Chỉ apply dòng thỏa **cả hai**: `human_apply = 1` **và** `ai_apply = 0`. Mọi dòng khác bỏ qua tuyệt đối (không apply job người dùng chưa đánh dấu `1`).

## Quy trình (lặp cho từng job)

### Bước 0 — Đọc Excel
Gọi `read_file` đọc `topcv_jobs.xlsx`, lập danh sách các dòng có `human_apply = 1` và `ai_apply = 0`. Nếu danh sách rỗng → báo người dùng không có job cần apply và dừng.

Khi không chắc đã apply job nào, đọc lại Excel.

### Bước 1 — Mở job
Mở trực tiếp URL trong cột `Link` của dòng đó. Nếu link không mở được hoặc tin đã hết hạn/bị gỡ → bỏ qua job này, ghi chú lại để báo người dùng, **không** đặt `ai_apply = 1`.

### Bước 2 — Xác nhận đúng job
Trên trang chi tiết, kiểm tra tiêu đề và công ty khớp với dòng Excel. Nếu trang báo **đã ứng tuyển** rồi → cập nhật `ai_apply = 1` và chuyển job khác (không nộp lại).

### Bước 3 — Nộp đơn
1. Bấm nút **"Ứng tuyển ngay"**.
2. Trong form/popup: chọn **CV tải lên gần nhất** (CV có thời gian cập nhật/tải lên mới nhất).
3. Tick ô **"Tôi đồng ý với thỏa thuận…"**.
4. Bấm **"Nộp hồ sơ ứng tuyển"**.
5. Xác nhận trang hiển thị thông báo nộp thành công (hoặc trạng thái "Đã ứng tuyển").

### Bước 4 — Cập nhật Excel NGAY
Sau khi **xác nhận thành công**, gọi tool Excel đặt `ai_apply = 1` cho đúng dòng đó (khớp theo Link, hoặc tên việc làm + công ty). Không sửa các cột khác, đặc biệt không đổi `human_apply`. Ghi ngay sau mỗi job, không dồn.

### Bước 5 — Lặp
Làm job kế trong danh sách từ Bước 0. Cuối cùng báo người dùng: đã apply bao nhiêu job, job nào bỏ qua/lỗi và lý do.

## Quy tắc quan trọng
- Chỉ apply khi `human_apply = 1` và `ai_apply = 0`.
- Chỉ đặt `ai_apply = 1` khi đã thấy xác nhận thành công; lỗi/không chắc → để `0` và báo lại.
- Luôn kiểm tra tên việc làm và công ty khớp trước khi bấm ứng tuyển, tránh nộp nhầm job.
- Không nộp lại job đã ứng tuyển.
- Nếu form yêu cầu thông tin bổ sung ngoài quy trình (thư giới thiệu, câu hỏi tùy chỉnh, chỉnh sửa thông tin cá nhân), hoặc có đăng nhập/captcha → **dừng và hỏi người dùng**, không tự bịa nội dung.
- Không bấm các nút khác ("Lưu", thùng rác, tim) ngoài các bước trên.
