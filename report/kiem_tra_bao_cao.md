# Báo cáo kiểm tra — báo cáo khóa luận giữa kỳ (DOCX)

> Tệp được kiểm: `report/Bao_cao_KLTN_giua_ky_environmental_audio_rag.docx` (63 trang) và bản PDF
> xem trước cùng tên. Đây là **bản viết lại lần 2** (03/10/2026) theo yêu cầu của nhóm: điền thông
> tin sinh viên, viết lại dễ đọc và ngắn hơn (85 → 63 trang), rút gọn bảng/hình, in đậm kết quả
> tốt nhất và tô nền cấu hình đang dùng. Các bảng/hình sinh từ artifact không đổi; mọi số vẫn do
> script sinh (hình `0b2069f`, bảng luận văn `1eb3012`, bảng bổ sung `028f021`).

## 1. Lệnh đã chạy

| Bước | Lệnh | Kết quả |
|---|---|---|
| Lint | `.venv/Scripts/python.exe -m ruff check .` | Sạch |
| Kiểm thử | `.venv/Scripts/python.exe -m pytest -q` | 747 pass, 4 skip (test cần PostgreSQL, Docker tắt), 19 warning |
| Kiểm thử bộ dựng | `.venv/Scripts/python.exe -m pytest -q tests/test_report_docx.py` | 13 pass (thêm 3 test cho tuỳ chọn bảng) |
| Dựng DOCX | `.venv/Scripts/python.exe -m scripts.build_midterm_report` | 9 tệp nguồn, 30 đối tượng đánh số, 14 tài liệu tham khảo, mọi tài liệu đều được trích |
| Cập nhật field + PDF | `powershell -ExecutionPolicy Bypass -File scripts/update_docx_fields.ps1` | Word (COM) cập nhật field hai lượt, lưu DOCX, xuất PDF 63 trang |
| Kiểm cấu trúc | `.venv/Scripts/python.exe -m scripts.check_midterm_docx` | Mọi mục đạt (§2) |

**Không** lệnh nào chạy suy luận, huấn luyện hay đánh giá trên tập test; không đọc
`predictions/test.npz`. Các bảng chỉ đọc measurement/evaluation đã khóa.

## 2. Kiểm tra cấu trúc tự động (`scripts.check_midterm_docx`)

| Kiểm tra | Kết quả | Đạt |
|---|---|:---:|
| Số section | 5 (bìa · phần đầu · nội dung · tài liệu tham khảo · phụ lục) | ✅ |
| Khổ và lề mọi section | A4; 3/3/3,5/2 cm | ✅ |
| Đánh số trang | Bìa không số; phần đầu La Mã; nội dung Ả Rập từ 1; tài liệu tham khảo/phụ lục chữ thường | ✅ |
| Heading 1–4, Content, Caption, TOC, Font Normal | Đúng thông số trong hướng dẫn chữ của mẫu | ✅ |
| Field | TOC 1; TOC hình/bảng 2; SEQ Bảng 15, SEQ Hình 4, SEQ PT 7; STYLEREF 26; REF 20; PAGEREF 78 | ✅ |
| Footer có `PAGE` | Chỉ footer nội dung | ✅ |
| Marker nguồn còn sót | Không | ✅ |
| Placeholder `[CẦN ĐIỀN` | **0** | ✅ |
| `⚠️ CẦN XÁC MINH` | 0 | ✅ |
| Bảng có hàng tiêu đề lặp | 21/21 | ✅ |
| PDF: lỗi tham chiếu field / thực thể XML lọt ra chữ | 0 / 0 | ✅ |

Số trang trong mục lục được đối chiếu với trang thật trong PDF cho cả 7 chương (tiêu đề chương 1–7:
trang 1, 5, 10, 16, 25, 29, 41; chênh lệch 0). Tiêu đề cấp 2–3 và danh mục hình/bảng không đối chiếu
từng mục. Nếu sửa nội dung trong Word, chọn toàn bộ (Ctrl+A) rồi nhấn F9 để cập nhật lại.

## 3. Thay đổi của lần viết lại

| Yêu cầu | Đã làm |
|---|---|
| Điền thông tin | Phạm Hoàng Phát – 22703861; Thân Trọng Tính – 22665711; TS. Huỳnh Công Bằng; lớp KHDL18A (footer); tháng 10/2026; tên đề tài tiếng Anh; ngày báo cáo GVHD 04/10/2026 |
| Lời cảm ơn | Viết ngắn, chỉ cảm ơn thầy hướng dẫn, khoa/trường, tác giả dữ liệu, gia đình bạn bè (không thêm chi tiết cá nhân) |
| Tiêu đề và văn phong | Tiêu đề ngắn, từ phổ thông; ngôi "nhóm"; chương 1–7 viết lại, thuật ngữ giải thích ở lần dùng đầu; bảy chương còn khoảng 15.100 từ so với 19.900 (đếm theo `wc`, gồm cả ký hiệu Markdown) |
| 85 → khoảng 60 trang | 63 trang |
| Bảng/hình | 31 → 21 bảng, 7 → 4 hình trong thân; bảng bỏ khỏi thân: trần chẩn đoán, ablation, cSEBB, parity, điểm cuối API, thời gian chạy, mục tiêu O1–O7, bảng artifact (số liệu vẫn nằm trong văn bản hoặc tệp measurement) |
| Tô đậm | Số in đậm = tốt nhất trong cột (hoặc trong nhóm hàng cùng loại); nền xám = cấu hình đang dùng (f2; mô tả template; kho f2 + hybrid). Có dòng chú thích dưới bảng, ghi rõ in đậm không hàm ý khác biệt có ý nghĩa |

Cách làm tô đậm: bộ dựng (`scripts/report_docx/markdown.py::expand_include`) nhận tuỳ chọn
`keep`, `cols`, `best`, `group`, `used` ở dòng `@@INCLUDE@@`, chỉ đổi cách trình bày; tệp bảng gốc do
script sinh không bị sửa. Bảng RQ1 không in đậm vì C−B không có ý nghĩa thống kê.

## 4. Kiểm tra số liệu và nội dung

- Đã so tập các số xuất hiện trong từng chương giữa bản cũ (HEAD) và bản mới. Số bị bỏ là số mục,
  chiều rộng hình, chi tiết cấu hình phụ (độ cao dải mel, lưới siêu tham số cSEBB…) hoặc con số
  trung gian của bảng bị bỏ; **không có kết quả thực nghiệm nào bị đổi giá trị**. Hai con số
  (Δ lọc trung vị, "không chỉ số nào có p < 0,05") đã được đưa lại sau khi phát hiện bị lược.
- Mọi kết quả âm tính hoặc kém đi vẫn còn: RQ1 âm tính (cả hai công thức), f2 không được gọi là tốt
  hơn v2 (macro và PSDS-1 thấp hơn), RQ3 giảm khi đổi kho sang f2, ECE tăng sau hiệu chuẩn, PSDS không
  tăng, 10/40 lượt đánh giá SED ghi `dirty`.
- Lớp có n_test < 10 vẫn chỉ báo số tuyệt đối (Phụ lục C).
- Vẫn tách "bám sát danh sách sự kiện dự đoán" với "đúng với âm thanh thật".

## 5. Lỗi gặp khi làm và đã sửa

| Lỗi | Xử lý |
|---|---|
| Lệnh `sed` làm mất một số cụm "f2" trong Chương 6 | Phát hiện qua soát chữ dính nhau, khôi phục 8 chỗ, đã rà lại |
| Bìa tiếng Anh tràn một dòng sang trang riêng (tên đề tài dài hơn mẫu) | Bỏ thêm dòng trống sau tiêu đề trên bìa EN (`package.py`) |
| Màu nền F2F2F2 quá nhạt, khó thấy khi in | Đổi sang D9D9D9 |
| Cột bảng RQ3/tiến triển bị bẻ dòng | Đặt `@@COLWIDTHS@@` |
| Lỡ chạy `ruff format scripts` làm định dạng lại 72 tệp không liên quan | Hoàn tác bằng `git checkout`, chỉ giữ các tệp đã sửa chủ ý |

## 6. Giới hạn của việc kiểm tra

- Bố cục kiểm trên PDF do Word trên máy này xuất; máy khác có thể ngắt trang lệch đôi chút. Không
  kiểm bằng LibreOffice.
- Việc "dễ đọc hơn" là đánh giá của người viết, chưa có người đọc ngoài nhóm kiểm lại.
- Lời cảm ơn là bản viết nhanh theo yêu cầu; nhóm nên đọc và sửa lại cho đúng ý.

## 7. Điểm nhóm nên xác nhận

1. Việc bỏ hai trang nhận xét phản biện cho bản giữa kỳ (còn trang nhận xét của GVHD để trống).
2. Việc đưa bảng artifact sang tệp `docs/measurements/artifact_freeze_20261002.md` (không còn trong
   phụ lục).
3. Tên tiếng Anh trên bìa/Abstract; tên không dấu của sinh viên và GVHD trên bìa EN.
4. Footer chỉ ghi tên hai sinh viên và lớp (không ghi MSSV); MSSV có ở bìa.
