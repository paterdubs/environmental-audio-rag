# Quy cách trình bày báo cáo — đối chiếu mẫu khoa

> Nguồn: `report/Mau bao cao KLTN_DS.docx`, đọc trực tiếp ngày 03/10/2026 (cả phần chữ hướng dẫn
> lẫn `word/styles.xml`, `word/numbering.xml`, `word/document.xml`, header/footer).
> Nguyên tắc: **hướng dẫn bằng chữ trong mẫu là căn cứ chính**. Khi style thực tế của file mẫu lệch
> với hướng dẫn chữ, báo cáo chuẩn hóa theo hướng dẫn chữ và ghi lại ở §3.

## 1. Yêu cầu bằng chữ trong mẫu (chương 1–2 của mẫu)

| Hạng mục | Yêu cầu |
|---|---|
| Khổ giấy | A4 210 × 297 mm, một mặt |
| Font | Times New Roman 13, mật độ bình thường, giãn dòng 1,5 lines |
| Lề | Trên 3 cm, dưới 3 cm, trái 3,5 cm, phải 2 cm |
| Số trang | Bên phải, phía dưới; bắt đầu từ 1 ở phần nội dung; **phụ lục không đánh số trang** |
| Header / footer | Header: thông tin khóa luận; footer: thông tin sinh viên |
| Tiểu mục | Tối đa 4 cấp số (số đầu là chương); mỗi mục đã chia thì có **≥ 2 tiểu mục** |
| Bảng / hình / công thức | Số gắn chương (Hình 3.4); tiêu đề bảng **trên**, căn giữa; chú thích hình **dưới**, căn giữa; cỡ chữ bằng văn bản; số công thức trong ngoặc đơn, căn phải |
| Viết tắt | Viết đầy đủ lần đầu, viết tắt trong ngoặc; > 10 từ viết tắt thì có danh mục xếp A, B, C |
| Mục lục | Chỉ đến cấp 3 |
| Heading 1 (chương) | TNR 14, đậm, IN HOA, Before 24 pt, After 24 pt, line 1,15, không thụt, căn trái; đánh số CHƯƠNG 1, 2… |
| Heading 2 | TNR 13, đậm đứng, Before 6, After 12, line 1,15, không thụt, căn trái |
| Heading 3 | TNR 13, đậm nghiêng, Before 6, After 12, line 1,15, không thụt, căn trái |
| Heading 4 | TNR 13, nghiêng, Before 6, After 12, line 1,15, không thụt, căn trái |
| Content | TNR 13, Before 10, After 0, line 1,5, không thụt đầu dòng, căn đều hai bên |
| Caption | TNR 13, Before 6, After 12, line 1,15, không thụt, căn giữa; tạo bằng *Insert Caption* |
| Danh mục (hình, bảng…) | Style Normal: TNR 13, Before 0, After 0, line 1,15 |
| Bullet | TNR 13, Before 0, After 0, line 1,5, không thụt, căn trái |
| Đề mục khác | TNR, cỡ 10–13, thống nhất (bảng nhiều nội dung có thể dùng 10) |
| Hình / bảng | Không ngắt trang giữa hình/bảng (trừ bảng dài hơn một trang) |
| Thành phần | Bìa VI, bìa EN, Abstract, Tóm tắt, Lời cảm ơn, Nhận xét GVHD, Nhận xét GVPB, Mục lục, DM hình, DM bảng, DM viết tắt, Nội dung, TLTK, Phụ lục; **tất cả trong một file Word** |
| Tài liệu tham khảo | Nhóm theo ngôn ngữ (Việt, Anh, Pháp, Đức, Nga, Trung, Nhật); alphabet theo **họ** (tác giả nước ngoài) hoặc **tên** (tác giả Việt); bài báo: tác giả (năm), "tên bài", *tên tạp chí* tập (số), trang.; sách: tác giả (năm), *tên sách*, NXB, nơi XB.; web: tên trang (tháng-năm), địa chỉ; dòng tiếp theo **lùi 1 cm** |
| Bố cục chương | Mẫu chỉ là tham khảo: "Sinh viên tùy theo đề tài mà đặt tên chương mục phù hợp" |
| Nhật ký làm việc | Mẫu có trang "NHẬT KÍ LÀM VIỆC" theo tuần, cột "Nhận xét của GVHD" |

## 2. Cấu trúc thực tế của file mẫu

| Section | Nội dung | Đánh số trang | Footer / header |
|---|---|---|---|
| 1 | Bìa chính (có viền trang `twistedLines1`) | — | Không có |
| 2 | Bìa phụ VI, bìa EN, Abstract, Tóm tắt, Lời cảm ơn, Nhận xét, Mục lục, DM | La Mã thường, bắt đầu i | `footer1` (trống — số La Mã chỉ hiện trong mục lục) |
| 3 | Nội dung chương | Ả Rập, bắt đầu 1 | `header1` (thông tin khóa luận) + `footer2` (tên SV + `PAGE` bên phải) |
| 4 | Tài liệu tham khảo | chữ thường a, b, c | `footer3` (tên SV, không số trang) |
| 5 | Phụ lục, Nhật ký | — | `footer4` (trống) |

- Heading 1 dùng numbering `numId 32` với `lvlText "CHƯƠNG %1"`; Heading 2–4 dùng `%1.%2`, `%1.%2.%3`, `%1.%2.%3.%4`.
- Caption: `Hình {STYLEREF 1 \s}.{SEQ Hình \* ARABIC \s 1}` và tương tự cho `Bảng`.
- Ba TOC: `TOC \o "1-3" \h \z \u`, `TOC \h \z \c "Hình"`, `TOC \h \z \c "Bảng"`.
- Tiêu đề không đánh số (TÀI LIỆU THAM KHẢO, PHỤ LỤC, DANH MỤC…) dùng style `Heading1N` (căn giữa, outline 0 → vào mục lục).
- Tiêu đề trang bìa phụ (LỜI CẢM ƠN, NHẬN XÉT…) dùng style `CoverB`.

## 3. Sai khác giữa style thực tế và hướng dẫn chữ — cách chuẩn hóa

| Style | Mẫu thực tế (`styles.xml`) | Hướng dẫn chữ | Báo cáo dùng |
|---|---|---|---|
| Normal | firstLine 1 cm, Before 6, line 1,3 | (danh mục) 0/0, line 1,15 | Normal giữ cho văn bản đặc biệt; **TOC1–3, Table of Figures** đặt 0/0, line 1,15, không thụt |
| Heading 1 | Before 3, After 24, line 1,2 | 24/24, line 1,15 | 24/24, line 1,15, IN HOA (caps) |
| Heading 2 | thụt trái 1 cm (style) | không thụt | indent 0 |
| Heading 3 | After 0, line 1,3 | 6/12, line 1,15 | 6/12, line 1,15 |
| Heading 4 | thụt từ numbering | không thụt | indent 0 |
| Caption | nghiêng, Before 0, After 10, line 1,0 | 6/12, line 1,15, không nói nghiêng | 6/12, line 1,15, **không nghiêng** |
| Content | Before 10, line 1,5, no indent, căn đều (kế thừa Normal) | như nhau | Giữ nguyên — dùng cho mọi đoạn văn thân bài |
| Bullet | `numId 30`, thụt 0,5 cm treo | "không thụt đầu dòng" | Giữ thụt treo của ký hiệu (cần cho bullet), Before/After 0, line 1,5 |
| TOC1/TOC3 | tab phải tại 8772 twip | — | Giữ tab dấu chấm, đặt lại vị trí theo vùng chữ 15,5 cm |

Lề: section 2 của mẫu có lề 1699/1138/1699/1987 twip (lệch < 0,01 cm so với 3/2/3/3,5 cm);
báo cáo đặt đúng 1701/1134/1701/1985 twip cho mọi section.

## 4. Quyết định trình bày cho báo cáo giữa kỳ

| Quyết định | Lý do |
|---|---|
| Bỏ hai trang Nhận xét GVPB, giữ trang Nhận xét GVHD | Báo cáo giữa kỳ do GVHD nhận xét; phản biện chưa được phân công |
| Thêm dòng "BÁO CÁO GIỮA KỲ" trên bìa | Phân biệt với cuốn khóa luận cuối kỳ |
| Bảng số liệu dùng TNR 11 (bảng rộng có thể 10) | Mẫu cho phép 10–13 cho bảng nhiều nội dung |
| Trích dẫn dạng số `[n]` theo thứ tự danh mục (đã nhóm ngôn ngữ, sắp alphabet) | Mẫu dùng số `[n].` trong danh mục; không dùng thứ tự xuất hiện kiểu IEEE |
| Phụ lục E "Nhật ký làm việc" điền tuần đã qua, cột nhận xét GVHD để trống | Mẫu có trang này; không được tự viết nhận xét của giảng viên |
| Thông tin cá nhân là `[CẦN ĐIỀN: …]` | Không lấy thông tin minh họa trong mẫu làm thông tin thật |
| Thuật ngữ tiếng Anh giữ nguyên ở lần đầu trong ngoặc, `class_id` không dịch | Quy ước dự án (CLAUDE §5) |
