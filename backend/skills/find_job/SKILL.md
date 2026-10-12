---
name: topcv-job-screening
description: Duyệt trang "Việc làm phù hợp" của TopCV (https://www.topcv.vn/viec-lam-phu-hop), lọc các việc thực tập/fresher tại Hà Nội (yêu cầu kinh nghiệm <= 1 năm), tóm tắt từng job và ghi vào file Excel để LLM khác đánh giá độ phù hợp với CV. Dùng khi người dùng yêu cầu quét/chọn việc làm trên TopCV.
---

# TopCV Job Screening

## Mục tiêu

Lặp qua danh sách việc làm trên https://www.topcv.vn/viec-lam-phu-hop, chỉ giữ job **ở Hà Nội** và **yêu cầu kinh nghiệm < 1 năm hoặc không yêu cầu** (người dùng là intern). Với mỗi job hợp lệ, tóm tắt nội dung và **ghi ngay vào file Excel**. Việc đánh giá độ phù hợp với CV do một LLM khác thực hiện sau, dựa trên bản tóm tắt này.

## Công cụ

- Trình duyệt: các tool điều khiển browser (click, scroll, đọc text trang).
- `read_file`: đọc lại file Excel để biết job nào đã xử lý.
- Tool ghi Excel (`write_excel` / tương đương): ghi/append từng dòng job.

Nếu tên tool khác, dùng tool tương ứng có chức năng đọc file / ghi Excel.

## File Excel

Đường dẫn: `topcv_jobs.xlsx` (sheet `Jobs`). Cột:

| Cột                           | Nội dung                                                                        |
| ----------------------------- | ------------------------------------------------------------------------------- |
| STT                           | Số thứ tự                                                                       |
| Tên việc làm                  | Tiêu đề job                                                                     |
| Công ty                       | Tên công ty                                                                     |
| Link                          | URL trang chi tiết job (dùng làm khóa chống trùng)                              |
| Mức lương                     | Ví dụ "2 - 3 triệu", "Thoả thuận"                                               |
| Địa điểm                      | Địa chỉ làm việc chi tiết                                                       |
| Kinh nghiệm                   | Yêu cầu kinh nghiệm ghi trên tin                                                |
| Cấp bậc / Hình thức           | Thực tập, Nhân viên, Full-time...                                               |
| Tóm tắt mô tả công việc       | Tóm tắt đầy đủ, súc tích                                                        |
| Tóm tắt yêu cầu ứng viên      | Kỹ năng, học vấn, công nghệ yêu cầu                                             |
| Tóm tắt quyền lợi             | Lương thưởng, đào tạo, phúc lợi                                                 |
| Địa điểm & thời gian làm việc | Chi tiết từ mục "Địa điểm làm việc", "Thời gian làm việc"                       |
| Hạn nộp / Thông tin khác      | Hạn nộp hồ sơ, số lượng tuyển, v.v.                                             |
| Trang                         | Số trang danh sách nơi tìm thấy job                                             |
| human_apply                   | Người dùng tự điền: `1` = có (muốn apply), `0` = không. Khi ghi dòng mới để `0` |
| ai_apply                      | `1` = agent đã apply cho rồi, `0` = chưa. Khi ghi dòng mới để `0`               |

## Quy trình (lặp lại cho từng job)

### Bước 0 — Kiểm tra job đã làm chưa

Trước khi click vào **bất kỳ** job nào, gọi `find_job` với tên việc làm + tên công ty (hoặc link) lấy từ thẻ job:

- Kết quả `ĐÃ CÓ` → job đã có trong Excel, **không xét nữa**, chuyển job khác.
- Kết quả `CHƯA CÓ` → tiếp tục Bước 1.

Khi không chắc đã xử lý job nào, cũng gọi `find_job` để kiểm tra. Không đọc toàn bộ file.

### Bước 1 — Chọn job từ danh sách

Trên trang danh sách (thẻ job hiển thị: tên, công ty, lương, tag địa điểm):

1. Bỏ qua job đã có trong Excel (so khớp tên + công ty, hoặc link).
2. **Xem tag địa điểm trên thẻ job** (ví dụ "Hà Nội"). Nếu **không phải Hà Nội** (kể cả "Hồ Chí Minh", "Đà Nẵng", hoặc nhiều địa điểm không có Hà Nội) → **bỏ qua, không click**.
3. Job còn lại → click vào để mở trang chi tiết.

### Bước 2 — Kiểm tra kinh nghiệm

Trên trang chi tiết, tìm mục **Kinh nghiệm** (phần thông tin chung / tổng quan):

- Yêu cầu **> 1 năm** (ví dụ "2 năm", "3 năm", "Trên 5 năm") → **thoát ra** (quay lại danh sách) và chọn job khác ngay. Không đọc thêm, không ghi Excel.
- "Không yêu cầu kinh nghiệm", "Dưới 1 năm", "1 năm" hoặc thực tập → tiếp tục.
- Nếu mục kinh nghiệm không rõ, đọc phần "Yêu cầu ứng viên" để xác định; nếu vẫn yêu cầu rõ > 1 năm thì bỏ.

### Bước 3 — Đọc đầy đủ nội dung

1. Cuộn xuống phần **Mô tả công việc**. Phần này thường bị cắt gọn → **click nút "Xem đầy đủ mô tả công việc"** để mở rộng, rồi đọc hết.
2. Tiếp tục cuộn và đọc kỹ các phần bên dưới:
   - Tổng quan / thông tin chung (lương, cấp bậc, hình thức, số lượng)
   - **Yêu cầu ứng viên**
   - **Quyền lợi ứng viên**
   - **Địa điểm làm việc**
   - **Thời gian làm việc**
   - Cách thức ứng tuyển / hạn nộp
3. Có thể cần cuộn nhiều lần; đảm bảo không bỏ sót phần nào.

### Bước 4 — Tóm tắt và ghi Excel NGAY

Ngay sau khi đọc xong **một** job hợp lệ (ở Hà Nội + kinh nghiệm < 1 năm hoặc không yêu cầu):

1. Viết bản tóm tắt theo các cột ở trên, giữ thông tin cụ thể (công nghệ, nhiệm vụ chính, yêu cầu kỹ năng, quyền lợi, thời gian) để LLM khác đánh giá được mức phù hợp với CV. **Không tự đánh giá/chấm điểm phù hợp** — chỉ tóm tắt khách quan.
2. **Gọi tool ghi Excel để append 1 dòng ngay lập tức.** Không dồn nhiều job rồi ghi một lần.

Job bị loại (không phải Hà Nội / kinh nghiệm > 1 năm) **không ghi** vào Excel.

### Bước 5 — Quay lại và lặp

1. Thoát khỏi trang chi tiết, quay lại danh sách.
2. Chọn job tiếp theo chưa xử lý, lặp từ Bước 1.
3. Nếu mất dấu đang ở đâu → quay lại **Bước 0** (`read_file` Excel).

### Bước 6 — Chuyển trang

Khi đã duyệt hết các job trên trang hiện tại, kéo xuống cuối trang, dùng thanh phân trang (`‹ 1 2 3 ›`) bấm sang **trang kế tiếp**, rồi lặp lại từ Bước 1. Dừng khi hết trang cuối (nút `›` không còn dùng được).

## Quy tắc quan trọng

- Chỉ Hà Nội. Kiểm tra tag địa điểm **trước khi click**.
- Kinh nghiệm > 1 năm → thoát ngay, tìm job khác.
- Luôn mở rộng "Xem đầy đủ mô tả công việc" trước khi tóm tắt.
- Ghi Excel **ngay sau mỗi job hợp lệ**, không để dồn.
- Trước khi xử lý một job, đối chiếu với Excel để tránh làm trùng; khi không nhớ thì `read_file` Excel.
- Không bấm "Ứng tuyển", "Lưu", "Không quan tâm" (nút thùng rác/tim) — chỉ đọc.
- Nếu trang yêu cầu đăng nhập hoặc xuất hiện captcha, dừng lại và báo người dùng.
- Tóm tắt khách quan, bằng tiếng Việt, đủ chi tiết để LLM khác đánh giá độ phù hợp với CV.
