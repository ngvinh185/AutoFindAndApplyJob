"""Schema đầu ra của browser-agent: trả `JobRow` của một job để excel-agent ghi vào Excel."""

from typing import Literal

from pydantic import BaseModel, Field


class JobRow(BaseModel):
    """Một dòng job trong topcv_jobs.xlsx (STT tự đánh số)."""

    ten_viec_lam: str = Field(description="Tên việc làm / tiêu đề job")
    cong_ty: str = Field(description="Tên công ty")
    link: str = Field(description="URL trang chi tiết job (khóa chống trùng)")
    muc_luong: str = Field(description='Mức lương, vd "2 - 3 triệu", "Thoả thuận"')
    dia_diem: str = Field(description="Địa chỉ làm việc chi tiết")
    kinh_nghiem: str = Field(description="Yêu cầu kinh nghiệm ghi trên tin")
    cap_bac_hinh_thuc: str = Field(description="Cấp bậc / hình thức: Thực tập, Nhân viên, Full-time...")
    tom_tat_mo_ta: str = Field(description="Tóm tắt mô tả công việc")
    tom_tat_yeu_cau: str = Field(description="Tóm tắt yêu cầu ứng viên: kỹ năng, học vấn, công nghệ")
    tom_tat_quyen_loi: str = Field(description="Tóm tắt quyền lợi: lương thưởng, đào tạo, phúc lợi")
    dia_diem_thoi_gian: str = Field(description="Địa điểm & thời gian làm việc")
    han_nop_thong_tin_khac: str = Field(description="Hạn nộp hồ sơ, số lượng tuyển, thông tin khác")
    trang: int = Field(ge=1, description="Số trang danh sách nơi tìm thấy job")
    human_apply: Literal[0, 1] = Field(default=0, description="Người dùng tự điền; khi ghi dòng mới để 0")
    ai_apply: Literal[0, 1] = Field(default=0, description="Agent đã apply chưa; khi ghi dòng mới để 0")


class BrowserOutput(BaseModel):
    """Kết quả cuối cùng mà browser-agent trả về cho điều phối viên."""

    job: JobRow | None = Field(
        default=None,
        description="Job vừa đọc đầy đủ, sẵn sàng ghi Excel ngay. None nếu không có job nào để ghi.",
    )