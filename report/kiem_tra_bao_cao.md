# Báo cáo kiểm tra — báo cáo khóa luận giữa kỳ (DOCX)

> Tệp được kiểm: `report/Bao_cao_KLTN_giua_ky_environmental_audio_rag.docx` (85 trang) và bản PDF
> xem trước cùng tên, dựng ngày 03/10/2026 từ commit có các bảng/hình sinh trên cây sạch
> (hình `0b2069f`, bảng luận văn `1eb3012`, bảng bổ sung `028f021`).

## 1. Lệnh đã chạy

| Bước | Lệnh | Kết quả |
|---|---|---|
| Lint | `.venv/Scripts/python.exe -m ruff check .` | Sạch |
| Kiểm thử | `.venv/Scripts/python.exe -m pytest -q` | 744 pass, 4 skip (test cần PostgreSQL, Docker tắt), 19 warning |
| Kiểm thử bộ dựng | `.venv/Scripts/python.exe -m pytest -q tests/test_report_docx.py` | 10 pass |
| Hình | `.venv/Scripts/python.exe -m scripts.build_midterm_figures` | 5 hình, `report/figures/manifest.json` ghi `dirty=false` |
| Bảng luận văn | `.venv/Scripts/python.exe -m scripts.build_thesis_tables` | 12 bảng; chỉ dòng revision và ô `global\|25` đổi, không số nào đổi |
| Bảng bổ sung | `.venv/Scripts/python.exe -m scripts.build_midterm_tables` | 8 bảng; kiểm tổng sự kiện tham chiếu = 740 khớp evaluation đã lưu |
| Dựng DOCX | `.venv/Scripts/python.exe -m scripts.build_midterm_report` | 9 tệp nguồn, 48 đối tượng đánh số, 14 tài liệu tham khảo, mọi tài liệu đều được trích |
| Cập nhật field + PDF | `powershell -ExecutionPolicy Bypass -File scripts/update_docx_fields.ps1` | Microsoft Word 16 (COM) cập nhật mọi field hai lượt, lưu DOCX, xuất PDF 85 trang |
| Kiểm cấu trúc | `.venv/Scripts/python.exe -m scripts.check_midterm_docx` | Bảng §2, mọi mục đạt |
| Render để xem | `pdftoppm -r 45` (toàn bộ) và `-r 110` (trang chọn lọc) | Xem §3 |

**Không** lệnh nào chạy suy luận, huấn luyện hay đánh giá trên tập test; không đọc
`predictions/test.npz`. Các bảng chỉ đọc measurement/evaluation đã khóa.

## 2. Kiểm tra cấu trúc tự động (`scripts.check_midterm_docx`)

| Kiểm tra | Kết quả | Đạt |
|---|---|:---:|
| Số section | 5 (bìa · phần đầu · nội dung · tài liệu tham khảo · phụ lục) | ✅ |
| Khổ và lề mọi section | 21,0 × 29,7 cm; trên/dưới 1701, trái 1985, phải 1134 twip (3/3/3,5/2 cm) | ✅ |
| Đánh số trang | Bìa không số; phần đầu La Mã từ i; nội dung Ả Rập từ 1; tài liệu tham khảo chữ thường từ a; phụ lục tiếp chữ thường, footer không in số | ✅ |
| Heading 1 | 14 pt, đậm, in hoa, 24/24 pt, giãn 1,15, sang trang mới, đánh số `CHƯƠNG n` | ✅ |
| Heading 2 / 3 / 4 | 13 pt; 6/12 pt; giãn 1,15; không thụt; H3 đậm nghiêng, H4 nghiêng | ✅ |
| Content | 13 pt, before 10 pt, after 0, giãn 1,5, căn đều, không thụt | ✅ |
| Caption | 13 pt, 6/12 pt, giãn 1,15, căn giữa, không nghiêng | ✅ |
| TOC, Table of Figures | 0/0 pt, giãn 1,15 | ✅ |
| Font Normal | Times New Roman 13 | ✅ |
| Field | TOC `\o "1-3"` 1; TOC `\c` 2 (Hình, Bảng); SEQ Bảng 24, SEQ Hình 7, SEQ PT 13; STYLEREF 44; REF 36; PAGEREF 142 (do Word sinh khi cập nhật mục lục) | ✅ |
| Footer có `PAGE` | Chỉ footer nội dung (`footer2`) | ✅ |
| Marker nguồn còn sót (`@@`, `⟪`, `[@`) | Không | ✅ |
| Bảng có hàng tiêu đề lặp | 31/31 | ✅ |
| PDF: lỗi tham chiếu field ("Error! Reference…") | 0 | ✅ |
| PDF: thực thể XML lọt ra chữ (`&lt;`…) | 0 | ✅ |
| Placeholder `[CẦN ĐIỀN` trong DOCX | 18 lần (xem §4) | — |
| `⚠️ CẦN XÁC MINH` | 0 | — |

## 3. Kiểm tra bố cục bằng mắt

Đã render toàn bộ 85 trang PDF (do chính Word xuất) thành ảnh và xem từng trang ở độ phân giải thấp,
một số trang ở độ phân giải cao. Các lỗi phát hiện và đã sửa trong quá trình dựng:

| Lỗi | Cách sửa |
|---|---|
| Ngày tháng trên bìa tràn sang trang 2 (tiêu đề dài hơn mẫu) | Bỏ hai dòng trống sau tiêu đề trên bìa |
| Abstract và Tóm tắt dài quá một trang | Rút gọn còn 232 từ (EN) và 323 âm tiết (VI) |
| Cột bảng bị ép thành chữ dọc (bảng 3.2, 6.x) | Thuật toán độ rộng cột theo từ dài nhất; tỷ lệ cột tường minh cho bảng phụ lục |
| Bảng ngắn và dòng "Nguồn" bị tách sang trang sau | `keepNext` cho mọi hàng của bảng ≤ 16 hàng |
| Ô `global\|25` làm vỡ cột bảng cSEBB | Escape `\|` trong builder bảng |
| `p &lt; 0,05` (escape hai lần) | Bỏ escape trước khi tách run tham chiếu |
| Chữ trong sơ đồ quá nhỏ khi co về 15,5 cm | Vẽ lại sơ đồ ở khổ 6,6 inch |
| Hình pipeline cũ (`02_data_pipeline_d0_d4.png`) chữ ~4 pt; hình theo lớp cũ (`05_…`) báo F1 cho lớp 9 sự kiện | Thay bằng hình mới (đọc manifest) và bảng phụ lục C |

Còn lại, chấp nhận được:

- Một số trang có khoảng trắng cuối trang do giữ bảng/hình cùng caption.
- Bảng RQ3 (18 hàng) trải sang trang sau, có lặp hàng tiêu đề.
- Công thức (4.1) dài hơn một dòng nên số công thức xuống dòng dưới, căn phải, đúng quy định của mẫu.
- Ảnh chụp giao diện (Hình 5.1) ghép bốn ảnh nên chữ trong ảnh nhỏ; ảnh chỉ mang tính minh họa.

**Giới hạn của việc kiểm tra:**

- Bố cục được kiểm trên bản PDF do Word trên máy này xuất (font Times New Roman cài sẵn). Máy khác có
  thể ngắt trang lệch đôi chút.
- Không kiểm bằng LibreOffice.
- Mục lục và danh mục đã được Word cập nhật. Số trang trong mục lục đã được đối chiếu qua Word COM
  (`Range.Information`) với trang thật của **mọi** tiêu đề cấp 1, tiêu đề không đánh số và tiêu đề
  phụ lục: 17/17 khớp (chương 1–7: 1, 7, 15, 22, 36, 43, 60; tài liệu tham khảo a; phụ lục c–g).
  Tiêu đề cấp 2–3 và danh mục hình/bảng không được đối chiếu từng mục. Nếu sửa nội dung trong Word,
  chọn toàn bộ (Ctrl+A) rồi nhấn F9 để cập nhật lại.

## 4. Mục người dùng cần hoàn thiện

| Vị trí | Nội dung cần điền | Sửa ở |
|---|---|---|
| Bìa VI, bìa phụ | Họ tên sinh viên (1 hoặc 2 người), MSSV; học hàm/học vị và họ tên GVHD; tháng nộp | `report/src/front_info.yaml` |
| Bìa EN, Abstract | Tên đề tài tiếng Anh đã được duyệt; tên sinh viên viết tiếng Anh; GVHD; tháng | `front_info.yaml`, `report/src/00_phan_dau.md` dòng 3 |
| Footer nội dung, tài liệu tham khảo | Họ tên – MSSV – Lớp | `front_info.yaml` (`footer`) |
| Lời cảm ơn | Sinh viên tự viết | `00_phan_dau.md` |
| Nhật ký làm việc | Ngày báo cáo GVHD tuần 1–2; tên GVHD | `report/src/90_phan_cuoi.md` |
| Trang nhận xét GVHD, cột "Nhận xét của GVHD" | Để trống cho giảng viên — **không** được tự viết | — |

Sau khi điền, dựng lại bằng hai lệnh:

```powershell
.venv/Scripts/python.exe -m scripts.build_midterm_report
powershell -ExecutionPolicy Bypass -File scripts/update_docx_fields.ps1
```

## 5. Điểm cần người dùng xác nhận về nội dung

1. Bố cục 7 chương và việc bỏ hai trang nhận xét phản biện cho bản giữa kỳ (quy_cach §4).
2. Kiểu trích dẫn số `[n]`, xếp theo danh mục đã nhóm ngôn ngữ và sắp alphabet theo họ (mẫu khoa
   không nêu rõ thứ tự số trong bài).
3. Bảng phụ lục dùng nhãn tĩnh "Bảng PL.n", không vào danh mục bảng (phụ lục không có số chương để
   đánh số theo field).
4. Văn phong khách quan ("đề tài", "báo cáo") thay cho ngôi "chúng tôi", vì số sinh viên chưa rõ.
5. Việc nhắc mã nội bộ (v1, v2, T2a, T2b, f2, S13) có bảng giải thích (Bảng 4.1); có thể đổi tên
   nếu giảng viên yêu cầu.
