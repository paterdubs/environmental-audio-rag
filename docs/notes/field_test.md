# Field test trên clip tự thu (T0-10)

Mục đích: xem hệ thống chạy ra sao trên âm thanh thật ngoài hai tập dữ liệu, bằng cách nghe. Không có nhãn
chuẩn nên **không** tính event-F1; báo độ chính xác theo người nghe, mức đồng thuận giữa hai người và số
sự kiện bị bỏ sót. Kết quả là định tính, cỡ mẫu nhỏ, và phải ghi đúng như vậy trong báo cáo.

## Thu clip

- 6–10 clip, 1–5 phút, thu bằng điện thoại: đường có xe máy/còi, công trường, mưa, quán nhạc, công viên, quạt.
- Tránh lời nói rõ (riêng tư). **Không commit clip**; chỉ commit phiếu chấm và kết quả.
- Chấp nhận WAV, FLAC, OGG, MP3; định dạng khác (m4a, aac...) được đổi sang WAV bằng ffmpeg.
- Giới hạn của demo: tối đa 50 MB và 10 phút mỗi clip.

## Chạy

Stack demo phải đang chạy (`scripts/demo_up.ps1`, LBR V3).

```bash
.venv/Scripts/python.exe -m scripts.field_test run --clips <thư mục chứa clip>
```

Kết quả ở `docs/measurements/field_test_<ngày>/`: hai phiếu `phieu_cham_A.csv`, `phieu_cham_B.csv` (giống
hệt, mỗi người một bản) và `ket_qua_he_thong.json`. Clip được đặt tên ẩn danh `clip_NN`.

## Chấm (hai người độc lập, không trao đổi trước khi nộp)

Mở phiếu bằng Excel và nghe từng clip.
- Dòng `phat_hien`: điền cột `danh_gia` là `dung` (nghe thấy đúng loại âm thanh trong khoảng onset–offset),
  `sai` (không có hoặc là âm thanh khác) hoặc `khong_ro`.
- Dòng `bo_sot` của mỗi clip: điền `so_bo_sot` (số sự kiện nghe thấy mà hệ thống không phát hiện) và `ghi_chu`.

## Tổng hợp

```bash
.venv/Scripts/python.exe -m scripts.field_test summarise --sheet-a <A.csv> --sheet-b <B.csv>
```

Ra `field_test_<ngày>_summary.{json,md}`: độ chính xác từng người, đồng thuận và kappa, số bỏ sót, theo lớp.
