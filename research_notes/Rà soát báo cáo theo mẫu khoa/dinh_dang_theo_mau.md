# Rà soát ĐỊNH DẠNG báo cáo cuối theo mẫu khoa

> Phạm vi: đối chiếu từng quy tắc định dạng của mẫu khoa (`report/Mau bao cao KLTN_DS (1).docx`, trùng byte với
> `report/Mau bao cao KLTN_DS.docx` — kiểm bằng `cmp`) với bản cuối `report/Khoa_luan_environmental_audio_rag.docx`
> (+ `.pdf`, 112 trang, A4 595.32 × 842.04 pt theo `pdfinfo`). Đọc ngày 24/11/2026, chỉ đọc, không sửa tệp nào trong repo.
>
> Cách đọc: giải nén hai DOCX vào scratchpad, đọc `word/document.xml`, `styles.xml`, `numbering.xml`, `settings.xml`,
> `header1.xml`, `footer1–4.xml` bằng lxml; trích chữ PDF bằng poppler `pdftotext -layout`, phông bằng `pdffonts` và
> `pdftohtml -xml`; dựng ảnh trang bằng `pdftoppm` (trang 1, 2, 3, 5, 7, 11, 17, 18, 22, 34, 83, 84, 101, 105, 111) và xem trực tiếp.
>
> Quy ước trích dẫn: "Mẫu P0270" = phần tử thứ 270 (đếm từ 0) trong `<w:body>` của `word/document.xml` mẫu; "Bản cuối
> P0255" tương tự cho bản cuối; "trang PDF n" = trang thứ n của PDF bản cuối (trang nội dung "1" = trang PDF 17).
> Đổi đơn vị: 567 twip = 1 cm; `sz` tính bằng nửa point (26 = 13 pt); `line` 240 = 1,0 dòng (276 = 1,15; 312 = 1,3; 360 = 1,5);
> `before/after` tính bằng 1/20 pt (120 = 6 pt; 200 = 10 pt; 240 = 12 pt; 480 = 24 pt).
>
> Ghi chú về nguồn: mọi "Source" bên dưới là tệp cục bộ trong repo (không có URL web); đường dẫn tương đối tính từ thư mục ghi chú này.

[MAU]: <../../report/Mau bao cao KLTN_DS (1).docx>
[DOCX]: <../../report/Khoa_luan_environmental_audio_rag.docx>
[PDF]: <../../report/Khoa_luan_environmental_audio_rag.pdf>
[CHECK]: <../../scripts/check_midterm_docx.py>
[QC]: <../../report/quy_cach_bao_cao.md>

## 0. Tổng hợp: quy tắc nào đạt, quy tắc nào lệch, công cụ kiểm có bắt được không? (đọc trước)

### Takeaway
26 quy tắc định dạng của mẫu: phần lớn đạt; vi phạm chắc chắn ở 4 chỗ (Abstract và Tóm tắt dài 2 trang; mục 6.6 chỉ có 1 tiểu mục;
Bảng 6.13 bị cắt giữa trang và 4 dòng "Nguồn:" mồ côi; nhiều từ viết tắt dùng trước khi viết đầy đủ); lệch nhỏ/cần xác nhận ở header,
số trang nhận xét phản biện, định dạng mục web/DOI của tài liệu tham khảo, chữ hoa tên SV trên bìa. `check_midterm_docx` không bắt
được vi phạm nào trong số này. Chi tiết và trích dẫn ở mục 1–13.

### Cited Findings
Bảng dưới tổng hợp các phát hiện của mục 1–13 (nguồn: [mẫu][MAU], [DOCX][DOCX], [PDF][PDF], [check_midterm_docx][CHECK]).

| # | Quy tắc của mẫu (vị trí) | Giá trị đo trên bản cuối | Kết luận | `check_midterm_docx` có kiểm? |
|---|---|---|---|---|
| 1 | A4 210×297 mm, một mặt (Mẫu P0270) | 5/5 section `pgSz` 11906×16838 (section 1: 11907×16840, chép từ mẫu); PDF 595.32×842.04 pt; không `mirrorMargins`, gutter 0 | Đạt | Chỉ kiểm chiều rộng ±2 twip; không kiểm chiều cao, không kiểm "một mặt" |
| 2 | Lề trên 3 / dưới 3 / trái 3,5 / phải 2 cm (P0270) | 1701/1701/1985/1134 twip = 3,00/3,00/3,50/2,00 cm ở cả 5 section | Đạt | Có |
| 3 | TNR 13, giãn 1,5 (P0270) | Normal TNR `sz` 26; Content `line` 360; chữ hiển thị trong PDF toàn TNR (Arial/Calibri chỉ xuất hiện ở ký tự trắng/tab, Symbol ở dấu bullet, Cambria Math ở công thức) | Đạt | Chỉ kiểm `ascii="Times New Roman"` của Normal |
| 4 | Heading 1: TNR 14, đậm, IN HOA, 24/24 pt, 1,15, không thụt, căn trái, "CHƯƠNG 1…" (P0280) | `sz` 28, b, caps, before/after 480/480, line 276, `jc=left`, numId 32 `lvlText "CHƯƠNG %1"`, thêm `pageBreakBefore`; trang PDF 17: "CHƯƠNG 1 GIỚI THIỆU" căn trái | Đạt | Kiểm cỡ/spacing/line/caps; không kiểm đậm, căn, thụt, nhãn "CHƯƠNG" |
| 5 | Heading 2: 13, đậm đứng, 6/12, 1,15, không thụt, trái, 1.1 (P0282) | b, không i, before 120 (kế thừa Normal), after 240, line 276, ind 0, jc left, `%1.%2` | Đạt | Kiểm spacing/line; không kiểm đậm/nghiêng/thụt |
| 6 | Heading 3: 13, đậm nghiêng, 6/12, 1,15 (P0284) | b + i, 120/240/276, ind 0, `%1.%2.%3` | Đạt | Như trên |
| 7 | Heading 4: 13, nghiêng, 6/12, 1,15 (P0286) | i, không b, 120/240/276 — **không có đoạn nào dùng Heading 4** | Đạt (không dùng) | Như trên |
| 8 | Content: 13, before 10, after 0, 1,5, không thụt, căn đều (P0289) | before 200, after 0, line 360, firstLine 0, jc both (kế thừa); 215 đoạn Content, 0 đoạn ghi đè `jc`/`ind` trực tiếp | Đạt | Kiểm spacing/line; không kiểm căn đều/thụt |
| 9 | Caption: 13, 6/12, 1,15, không thụt, giữa (P0291) | `sz` 26, 120/240/276, firstLine 0, jc center, không nghiêng | Đạt | Kiểm spacing/line/nghiêng |
| 10 | Danh mục (Normal): 13, 0/0, 1,15 (P0299) | TOC1–3 và TableofFigures: before 0, after 0, line 276; style Normal gốc vẫn 6 pt/1,3/thụt 1 cm (không dùng cho danh mục) | Đạt (áp lên style danh mục, không lên Normal) | Kiểm TOC1, TableofFigures; không kiểm TOC2, TOC3 |
| 11 | Bullet: 13, 0/0, 1,5, không thụt, trái (P0301) | before 0, after 0, line 360, jc left, ind left 284 hanging 284 (treo 0,5 cm cho ký hiệu) | Đạt | **Không** |
| 12 | Đề mục khác: TNR 10–13, thống nhất (P0303) | TableText 11 pt, TableTextSmall 10 pt, TableNote 11 pt nghiêng, Bibliography1 13 pt | Đạt | **Không** |
| 13 | Header = thông tin khóa luận; footer = thông tin SV (P0272) | Header: "Khóa luận tốt nghiệp năm 2026 – Ngành Khoa học dữ liệu"; footer: "Phạm Hoàng Phát – Thân Trọng Tính – KHDL18A" | Đạt một phần — header không có tên đề tài (mẫu đặt tên tài liệu vào header) | **Không** |
| 14 | Số trang bên phải, phía dưới, từ 1 ở phần nội dung; phụ lục không đánh số (P0271) | Section 3 `pgNumType start=1`, footer2 `jc=right` + `PAGE`; trang PDF 17 in "1" góc dưới phải; section 5 footer4 rỗng, trang PDF 105 không có số | Đạt | Kiểm có `PAGE` chỉ ở footer2; không kiểm vị trí |
| 15 | Tối đa 4 cấp số; mỗi mục đã chia có ≥ 2 tiểu mục (P0273, P0287) | Dùng Heading1 ×7, Heading2 ×46, Heading3 ×9; **mục 6.6 chỉ có 1 tiểu mục (6.6.1)** | **Vi phạm** (1 chỗ) | **Không** |
| 16 | Số bảng/hình/công thức theo chương; tiêu đề bảng ở trên, giữa; chú thích hình ở dưới, giữa; cỡ bằng văn bản; số công thức trong ngoặc, căn phải; công thức dài thì số xuống dòng (P0274) | 56 caption: 0 caption "Bảng" không đứng ngay trên bảng, 0 caption "Hình" không đứng ngay dưới ảnh; `STYLEREF 1 \s` + `SEQ … \s 1`; công thức "(1.1)" bằng tab phải tại 8787 | Đạt | Chỉ đếm field; không kiểm vị trí |
| 17 | Hình/bảng không bị ngắt trang (trừ bảng dài hơn một trang) (P0297) | **Bảng 6.13 (17 hàng) bị tách trang PDF 83→84**; dòng "Nguồn:" của Hình 3.3, Hình 4.1, Hình 6.7, Bảng PL.6 rơi sang trang sau (trang PDF 35, 40, 91, 110); bảng PL.1, PL.2, PL.5/PL.6 tách trang (105–106, 106–107, 108–109) | **Vi phạm** (Bảng 6.13 chắc chắn; phụ lục cần xem bảng có dài hơn một trang không) | **Không** |
| 18 | Viết tắt: viết đầy đủ lần đầu, viết tắt trong ngoặc; > 10 từ thì có danh mục A, B, C (P0275) | Danh mục 27 mục, sắp xếp đúng thứ tự chữ cái (không phân biệt hoa thường); một số từ dùng trước khi viết đầy đủ (ADR, OOF, LBR, nDCG, PSDS, SQL…) | Danh mục đạt; quy tắc "viết đầy đủ lần đầu" **chưa đạt hoàn toàn** | **Không** |
| 19 | Mục lục chỉ đến cấp 3 (P0277) | `TOC \o "1-3" \h \z \u`; TOC3 xuất hiện (6.3.1…6.6.1) | Đạt | Kiểm có đúng 1 `TOC \o` |
| 20 | Thành phần + thứ tự phần đầu (P0206–P0219) | Đủ và đúng thứ tự; chỉ 1 trang nhận xét phản biện (mẫu có "PHẢN BIỆN 1" và "PHẢN BIỆN 2") | Đạt, có 1 điểm cần xác nhận | **Không** |
| 21 | Abstract/Tóm tắt "trình bày trong một trang A4" (P0074, P0086) | **Abstract 2 trang (PDF 4–5), Tóm tắt 2 trang (PDF 6–7)** | **Vi phạm** | **Không** |
| 22 | Toàn bộ trong một tệp Word (P0269) | Một DOCX 5 section, từ bìa đến nhật ký | Đạt | Gián tiếp (5 section) |
| 23 | Tài liệu tham khảo: nhóm ngôn ngữ, alphabet theo họ, định dạng mục, dòng sau lùi 1 cm (P0387–P0411) | Nhóm "Tiếng Việt"/"Tiếng Anh"; 28 mục [1]–[28] đúng alphabet theo họ; Bibliography1 treo 567 twip = 1,0 cm; mục web dùng "(năm)" + "truy cập …" + dấu chấm cuối; mục bài báo kết thúc bằng DOI | Đạt phần chính; **lệch nhỏ** ở mục web và đuôi DOI | **Không** |
| 24 | Phụ lục không đánh số trang, không dày hơn phần chính (P0276) | Phụ lục 6 trang + nhật ký 2 trang so với 84 trang nội dung; không in số | Đạt | **Không** |
| 25 | Bìa cứng, chữ nhũ vàng, nền xanh, gáy (Top: tên SV, MSSV; Middle: tên đề tài; Bottom: năm) (P0265–P0268) | Thuộc khâu in ấn, không nằm trong DOCX | Không kiểm được trên tệp | **Không** |
| 26 | Giới hạn số trang | Mẫu **không** nêu giới hạn tổng số trang; chỉ nêu Abstract 1 trang, poster 1 trang A0, phụ lục ≤ phần chính | — | — |

### Inferences
- Thứ tự ưu tiên sửa (theo mức dễ bị hội đồng nhìn thấy): (1) rút Abstract và Tóm tắt về 1 trang; (2) Bảng 6.13 và các dòng nguồn mồ côi;
  (3) mục 6.6 (nâng 6.6.1 thành 6.7 hoặc tách thêm 6.6.2); (4) viết đầy đủ OOF, LBR, nDCG, PSDS, SEBB, ADR ở lần đầu; (5) quyết định header,
  trang phản biện thứ hai, định dạng mục web.

### Gaps
- Các điểm "cần xác nhận" (header, 1 hay 2 trang phản biện, tên SV IN HOA) không quyết được từ chữ của mẫu; cần GVHD/khoa trả lời.

---

## 1. Khổ giấy, lề, khoảng cách header/footer, font, giãn dòng, căn lề

### Takeaway
Khổ, lề, font, giãn dòng và toàn bộ thông số Heading 1–4/Content/Caption/danh mục/Bullet của bản cuối khớp **hướng dẫn bằng chữ**
của mẫu. Bản cuối chủ động lệch khỏi **style thực tế** của tệp mẫu (vốn lệch chính hướng dẫn chữ) — có ghi trong `quy_cach_bao_cao.md` §3.

### Cited Findings
- Hướng dẫn chữ (nguyên văn): "Soạn thảo văn bản: báo cáo được trình bày trên một mặt giấy trắng khổ A4 (210x297 mm), báo cáo sử dụng font chữ Times New Roman cỡ 13 của hệ soạn thảo Winword hoặc tương đương; mật độ chữ bình thường, dãn dòng đặt ở chế độ 1,5 lines; lề trên 3cm; lề dưới 3cm; lề trái 3,5cm; lề phải 2cm." — [Mẫu P0270][MAU]
- Bản cuối, `sectPr` cả 5 section: `pgMar top=1701 bottom=1701 left=1985 right=1134 gutter=0` (= 3,00/3,00/3,50/2,00 cm); section 2–5 `header=990 footer=810` (1,75 cm / 1,43 cm); section 1 (bìa) `header=340 footer=227` và viền `pgBorders twistedLines1` chép từ mẫu. — [DOCX `word/document.xml`][DOCX]
- Mẫu thực tế: section 2 có lề 1699/1138/1699/1987 twip và header/footer 720/720; section 3–4 dùng 1701/1134/1701/1985, header/footer 990/810. Bản cuối chuẩn hóa mọi section 2–5 về 1701/1134/1701/1985 và 990/810. Mẫu không nêu khoảng cách header/footer bằng chữ. — [Mẫu `document.xml` sectPr][MAU]
- `settings.xml` cả mẫu và bản cuối: chỉ có `defaultTabStop 720`; không có `mirrorMargins`, `gutterAtTop`, `evenAndOddHeaders` (phù hợp in một mặt). — [DOCX `word/settings.xml`][DOCX]
- Style Normal (cả hai tệp): `rFonts ascii/hAnsi/cs = Times New Roman`, `sz 26`, `spacing before 120 after 0 line 312`, `ind firstLine 567`, `jc both`. — [DOCX `word/styles.xml`][DOCX]
- Hướng dẫn chữ Heading 1 (nguyên văn): "Tên chương sử dụng kiểu định dạng (Style) Heading 1 với các thông số: kiểu chữ (font) Times New Roman, cỡ 14, in đậm, sử dụng chữ in hoa, Spacing Before: 24 pt, Spacing After: 24 pt, Line spacing: 1.15 lines, không thụt đầu dòng đoạn văn, căn lề trái. Tên chương được đánh số theo thứ tự CHƯƠNG 1, CHƯƠNG 2, …" — [Mẫu P0280][MAU]
  - Bản cuối Heading1: `b`, `caps`, `sz 28`, `spacing before 480 after 480 line 276`, `jc left`, `keepNext`, `keepLines`, `pageBreakBefore`, numId 32. — [DOCX `styles.xml`][DOCX]
  - Mẫu thực tế Heading1: `before 60 after 480 line 288` (3 pt / 24 pt / 1,2), **không** `caps` trong style; các đoạn chương trong mẫu (P0202, P0279, P0306, P0349, P0369) ghi đè `jc=center`. — [Mẫu `styles.xml`, `document.xml`][MAU]
- Hướng dẫn chữ Heading 2 (nguyên văn): "… Times New Roman, cỡ 13, in đậm và đứng, Spacing Before: 6 pt, Spacing After: 12 pt, Line spacing: 1.15 lines, không thụt đầu dòng đoạn văn, căn lề trái. Tên tiểu mục thứ nhất được đánh số theo thứ tự 1.1, 1.2, …" — [Mẫu P0282][MAU]. Bản cuối: `b`, `after 240 line 276`, before kế thừa 120, `ind left 0 firstLine 0`, `jc left`. Mẫu thực tế Heading2 có `ind left 567` (thụt 1 cm). — [DOCX/Mẫu `styles.xml`][DOCX]
- Hướng dẫn chữ Heading 3 (nguyên văn): "… cỡ 13, in đậm và nghiêng, Spacing Before: 6 pt, Spacing After: 12 pt, Line spacing: 1.15 lines, không thụt đầu hàng, canh lề trái. … 1.1.1, 1.1.2, …" — [Mẫu P0284][MAU]. Bản cuối: `b`, `i`, `after 240 line 276`, ind 0. Mẫu thực tế Heading3 không có spacing riêng (kế thừa Normal: 6 pt / 0 / 1,3). — [styles.xml hai tệp][DOCX]
- Hướng dẫn chữ Heading 4 (nguyên văn): "… cỡ 13, in nghiêng, Spacing Before: 6 pt, Spacing After: 12 pt, Line spacing: 1.15 lines, không thụt đầu dòng đoạn văn, căn lề trái. … 1.1.1.1, 1.1.1.2, …" — [Mẫu P0286][MAU]. Bản cuối: `i` (không `b`), `after 240 line 276`, ind 0; không đoạn nào dùng Heading4. — [DOCX][DOCX]
- Hướng dẫn chữ Content (nguyên văn): "Các phần nội dung sử dụng kiểu định dạng (Style) Content với các thông số: kiểu chữ (font) Times New Roman, cỡ 13, Spacing Before: 10pt, Spacing After: 0 pt, Line spacing: 1.5 lines, không thụt đầu dòng đoạn văn và căn lề hai bên." — [Mẫu P0289][MAU]. Bản cuối Content (giống mẫu): `before 200 line 360 firstLine 0`, after/jc kế thừa 0/both; 215 đoạn Content, không đoạn nào ghi đè `jc`/`ind`. — [DOCX][DOCX]
- Hướng dẫn chữ Caption (nguyên văn): "… Style Caption với các thông số: kiểu chữ (font) Times New Roman, cỡ 13, Spacing Before: 6 pt, Spacing After: 12 pt, Line spacing: 1.15 lines, không thụt đầu dòng đoạn văn và căn lề chính giữa." — [Mẫu P0291][MAU]. Bản cuối: `after 240 line 276 firstLine 0 jc center`, before kế thừa 120, không `i`. Mẫu thực tế Caption: `before 0 after 200 line 240`, **nghiêng**. — [styles.xml][DOCX]
- Hướng dẫn chữ danh mục (nguyên văn): "Các danh mục hình ảnh, bảng biểu, … sử dụng kiểu định dạng (Style) Normal với các thông số: kiểu chữ (font) Times New Roman, cỡ 13, Spacing Before: 0 pt, Spacing After: 0 pt, Line spacing: 1.15 lines." — [Mẫu P0299][MAU]. Bản cuối: TOC1/TOC2/TOC3/TableofFigures `before 0 line 276`, after kế thừa 0, firstLine 0; tab phải dấu chấm tại 8787 twip (≈ mép vùng chữ 15,5 cm). — [DOCX][DOCX]
- Hướng dẫn chữ Bullet (nguyên văn): "Các bullet sử dụng kiểu định dạng (Style) Bullet với các thông số: kiểu chữ (font) Times New Roman, cỡ 13, Spacing Before: 0 pt, Spacing After: 0 pt, Line spacing: 1.5 lines, không thụt đầu dòng đoạn văn và canh lề trái." — [Mẫu P0301][MAU]. Bản cuối Bullet (basedOn Content): `before 0`, after 0, line 360, `ind left 284 hanging 284`, `jc left`, numId 30 (bullet Symbol). 45 đoạn Bullet. — [DOCX][DOCX]
- Hướng dẫn chữ đề mục khác (nguyên văn): "Các đề mục không được đề cập ở trên có thể dùng định dạng tùy ý nhưng phải là kiểu chữ (font) Times New Roman cỡ tối đa là 13, tối thiểu là 10 và phải thống nhất. Ví dụ các bảng biểu có nhiều nội dung có thể dùng cỡ chữ 10." — [Mẫu P0303][MAU]. Bản cuối: mọi đoạn trong bảng dùng TableText (`sz 22` = 11 pt, line 240, before/after 1 pt; 1.389 đoạn) hoặc TableTextSmall (`sz 20` = 10 pt; 333 đoạn), không có `sz` ghi đè trong bảng; TableNote (dòng "Nguồn:") 11 pt nghiêng, line 1,0, trái; FigureParagraph căn giữa. — [DOCX][DOCX]
- Phông thực tế trong PDF (`pdffonts` + `pdftohtml -xml` trên trang 11, 17, 42, 68): mọi chữ hiển thị là Times New Roman (thường/đậm/nghiêng/đậm nghiêng); Calibri chỉ xuất hiện ở 71 ký tự trắng trên trang Mục lục; Arial chỉ ở ký tự trắng/tab sau số đề mục và bullet; SymbolMT là dấu "•"; Cambria Math cho công thức OMML. Nguồn gốc: `Heading1/3 rFonts cs="Arial"`, `Normal-No-Indent rFonts eastAsia="Calibri"` (kế thừa từ mẫu). — [PDF][PDF]

### Inferences
- Theo hướng dẫn chữ (căn cứ chính theo `quy_cach_bao_cao.md`), phần định dạng ký tự và đoạn văn đạt toàn bộ. Nếu hội đồng so với **style thực tế của tệp mẫu** thay vì chữ, sẽ thấy khác ở Heading 1 (mẫu căn giữa, before 3 pt), Heading 2 (mẫu thụt 1 cm), Caption (mẫu nghiêng) — đó là chủ đích, có thể giải thích bằng nguyên văn hướng dẫn.
- Cambria Math trong công thức là mặc định của Word Equation; mẫu không nói gì về phông công thức, nên khó coi là vi phạm "Times New Roman".

### Gaps
- Mẫu không nêu khoảng cách header/footer bằng chữ; chỉ so được với giá trị trong tệp mẫu.
- Không kiểm được cỡ chữ bên trong ảnh (hình PNG) — mẫu cũng không quy định.

## 2. Trang bìa (bìa chính, bìa phụ, bìa tiếng Anh) và gáy

### Takeaway
Bố cục ba trang bìa giữ đúng khung của mẫu (cùng đoạn, cùng cỡ chữ, viền `twistedLines1` ở bìa chính, khung hình chữ nhật ở bìa EN). Lệch nhỏ: tên sinh viên viết thường-hoa thay vì IN HOA như placeholder, bỏ 2 dòng trống giữa tên đề tài và "Ngành", tên đề tài EN để Title Case. Yêu cầu gáy/bìa cứng thuộc khâu in.

### Cited Findings
- Mẫu bìa chính (section 1, có `pgBorders twistedLines1 sz=18`): "BỘ CÔNG THƯƠNG" (13 pt) / "TRƯỜNG ĐẠI HỌC CÔNG NGHIỆP TP. HỒ CHÍ MINH" (14 đậm) / "KHOA CÔNG NGHỆ THÔNG TIN" (14 đậm) / logo / "HỌ VÀ TÊN SINH VIÊN 1", "HỌ VÀ TÊN SINH VIÊN 2" (14 đậm) / tên đề tài "HƯỚNG DẪN VÀ MẪU BÁO CÁO KHÓA LUẬN TỐT NGHIỆP NĂM 2026" (`sz 40` = 20 pt đậm, thụt trái/phải 0,5 cm) / 2 dòng trống / "Ngành: Khoa học dữ liệu" (14 đậm) / "Giảng viên hướng dẫn: TS. Họ và Tên GVHD" (14 đậm) / "THÀNH PHỐ HỒ CHÍ MINH, THÁNG 12 NĂM 2026" (12 pt). Bìa phụ (P0026–P0047) lặp y hệt nhưng ở section 2 (không viền). — [Mẫu P0001–P0047][MAU]
- Bản cuối bìa chính (P0001–P0019) và bìa phụ (P0023–P0041): cùng đoạn/cỡ chữ; tên SV "Phạm Hoàng Phát – 22703861", "Thân Trọng Tính – 22665711" (14 đậm, chữ thường-hoa, có MSSV); tiêu đề `sz 40` đậm "KHÓA LUẬN TỐT NGHIỆP" + ngắt dòng + "XÂY DỰNG HỆ THỐNG PHÁT HIỆN, SINH MÔ TẢ VÀ TRUY VẤN SỰ KIỆN ÂM THANH MÔI TRƯỜNG DỰA TRÊN RAG"; "Ngành: Khoa học dữ liệu" đứng ngay sau tiêu đề (không dòng trống); "Giảng viên hướng dẫn: TS. Huỳnh Công Bằng"; "THÀNH PHỐ HỒ CHÍ MINH, THÁNG 11 NĂM 2026". — [DOCX P0001–P0041][DOCX]
- Ảnh trang PDF 1: viền kép quanh trang, logo IUH, các dòng căn giữa, tiêu đề 3 dòng đậm, "Ngành" sát dưới tiêu đề. Trang PDF 2 (bìa phụ): cùng nội dung, không viền. — [PDF trang 1–2][PDF]
- Bìa EN mẫu (P0050–P0070): "INDUSTRIAL UNIVERSITY OF HO CHI MINH CITY", "FACULTY OF INFORMATION TECHNOLOGY", "FULLNAME OF THE FIRST STUDENT"… tên đề tài IN HOA 20 pt, "Major: Data Science", "Supervisor: Dr. Full name of supervisor", "HO CHI MINH CITY – DECEMBER 2026". Bản cuối (P0044–P0060, trang PDF 3): "Pham Hoang Phat – 22703861", "GRADUATION THESIS" + "Grounded Environmental Sound Event Detection, Captioning, and RAG-based Retrieval" (Title Case), "Major: Data Science", "Supervisor: Dr. Huynh Cong Bang", "HO CHI MINH CITY – NOVEMBER 2026"; có khung chữ nhật (shape `wps`, cả hai tệp đều có 3 shape `wps`). — [Mẫu/DOCX document.xml][DOCX]
- Hướng dẫn chữ về bìa cứng và gáy (nguyên văn): "Bản báo cáo khóa luận tốt nghiệp khi đã bảo vệ thành công phải đóng bìa cứng, in chữ nhũ màu vàng, nền màu xanh, gáy ghi ĐẦY ĐỦ thông tin để nộp lưu trữ." kèm bullet "Top: Họ và tên sinh viên, MSSV", "Middle: Tên đề tài", "Bottom: năm thực hiện". — [Mẫu P0265–P0268][MAU]
- Mẫu không có trang "Lời cam đoan" trong danh sách thành phần (P0206–P0219); bản cuối cũng không có. — [Mẫu P0206–P0219][MAU]

### Inferences
- Placeholder IN HOA ("HỌ VÀ TÊN SINH VIÊN 1", "FULLNAME OF THE FIRST STUDENT") gợi ý tên SV nên viết IN HOA; bản cuối viết thường-hoa. Đây là suy luận từ placeholder, mẫu không có câu chữ nào bắt buộc.
- Bản cuối thêm MSSV lên bìa — mẫu không đòi trên bìa nhưng đòi trên gáy; không mâu thuẫn.
- Việc bỏ 2 dòng trống giữa tiêu đề và "Ngành" (ghi trong `kiem_tra_bao_cao.md` §5 là để tránh tràn trang khi tiêu đề dài) làm dòng "Ngành" dính sát tiêu đề trên ảnh trang 1–3; chỉ ảnh hưởng thẩm mỹ.

### Gaps
- Gáy và bìa cứng không kiểm được trên tệp; cần nhắc ở khâu in (tên SV + MSSV, tên đề tài, năm 2026).

## 3. Thứ tự và sự có mặt của phần đầu

### Takeaway
Đủ mọi thành phần mẫu liệt kê, đúng thứ tự, mỗi mục bắt đầu trang mới. Hai điểm lệch: Abstract và Tóm tắt mỗi cái dài 2 trang (mẫu đòi 1 trang A4); chỉ có 1 trang nhận xét phản biện (mẫu mẫu có 2: PB1, PB2). Lời cảm ơn thiếu dòng ký "Người thực hiện đề tài".

### Cited Findings
- Danh sách thành phần của mẫu (nguyên văn, theo thứ tự): "Bìa tiếng Việt; Bìa tiếng Anh; Trang Abstract tiếng Anh và Keywords; Trang Abstract tiếng Việt và từ khóa; Trang lời cảm ơn; Trang Nhận xét và đánh giá của Giáo viên hướng dẫn; Trang Nhận xét và đánh giá của Giáo viên phản biện; Trang Mục lục; Trang Mục lục hình ảnh; Trang Danh mục bảng biểu; Trang Danh mục từ viết tắt; Nội dung báo cáo; Tài liệu tham khảo; Phụ lục". — [Mẫu P0206–P0219][MAU]
- Thứ tự thực tế trong tệp mẫu: bìa chính → bìa phụ VI → bìa EN → ABSTRACT → TÓM TẮT → LỜI CẢM ƠN → NHẬN XÉT CỦA GIÁO VIÊN HƯỚNG DẪN → NHẬN XÉT CỦA GIÁO VIÊN PHẢN BIỆN 1 → NHẬN XÉT CỦA GIÁO VIÊN PHẢN BIỆN 2 → MỤC LỤC → DANH MỤC HÌNH ẢNH → DANH MỤC BẢNG BIỂU → DANH MỤC CÁC THUẬT NGỮ VIẾT TẮT → chương → TÀI LIỆU THAM KHẢO → PHỤ LỤC → NHẬT KÍ LÀM VIỆC. — [Mẫu P0001–P0428][MAU]
- Thứ tự bản cuối (trang PDF): bìa chính (1) → bìa phụ (2) → bìa EN (3) → ABSTRACT (4–5) → TÓM TẮT (6–7) → LỜI CẢM ƠN (8) → NHẬN XÉT CỦA GIÁO VIÊN HƯỚNG DẪN (9) → NHẬN XÉT CỦA GIÁO VIÊN PHẢN BIỆN (10) → MỤC LỤC (11–12) → DANH MỤC HÌNH ẢNH (13) → DANH MỤC BẢNG BIỂU (14–15) → DANH MỤC CÁC THUẬT NGỮ VIẾT TẮT (16) → Chương 1–7 (17–100) → TÀI LIỆU THAM KHẢO (101–104) → PHỤ LỤC (105–110) → NHẬT KÍ LÀM VIỆC (111–112). — [PDF, `pdftotext -layout`][PDF]
- Yêu cầu một trang (nguyên văn): "Trang tóm tắt (Abstract) đề tài bằng tiếng Anh, trình bày trong một trang A4, gồm Tên đề tài, tóm tắt ngắn gọn nội dung và từ khóa." và "Trang tóm tắt đề tài bằng tiếng Việt, trình bày trong một trang A4, gồm Tên đề tài, tóm tắt ngắn gọn nội dung và từ khóa." — [Mẫu P0074, P0086][MAU]
  - Bản cuối: trang PDF 5 bắt đầu bằng "SED predicts; on the high-coverage store it did (+0.040)…" và kết thúc bằng dòng "Keywords: …"; trang PDF 7 bắt đầu "test) cho nDCG@10 cao hơn cả hai chế độ gốc…" và kết thúc "Từ khóa: …". Abstract (P0063–P0067) gồm dòng "Title: …", 3 đoạn Content, dòng "Keywords:" đậm; Tóm tắt (P0070–P0074) tương tự. — [PDF trang 4–7][PDF]
- Mẫu đặt tên đề tài phía trên chữ "ABSTRACT" (P0072, 14 đậm) và tiêu đề ABSTRACT/TÓM TẮT bằng Normal-No-Indent 14 đậm căn giữa; bản cuối dùng style CoverB (14 đậm IN HOA căn giữa) và đặt "Title: …"/"Tên đề tài: …" đậm ngay dưới tiêu đề. — [Mẫu P0072–P0073, DOCX P0062–P0063][DOCX]
- Trang lời cảm ơn mẫu có khối ký tên căn phải "Người thực hiện đề tài" (P0113, đậm). Bản cuối P0076–P0081: 4 đoạn Content, không có khối ký tên; trang PDF 8 kết thúc bằng "…góp ý của quý thầy cô để hoàn thiện khóa luận." — [Mẫu P0113, DOCX P0076–P0081][DOCX]
- Trang nhận xét: mẫu có 18 dòng trống đậm, ngày "TP. Hồ Chí Minh, ngày…. Tháng …. năm……." căn phải và "CHỮ KÝ CỦA GIẢNG VIÊN"; bản cuối dùng 16 dòng kẻ chấm (style DotLine, tab dấu chấm 8787), ngày căn phải nghiêng, "CHỮ KÝ CỦA GIẢNG VIÊN" đậm. Tiêu đề GVPB bản cuối: "NHẬN XÉT CỦA GIÁO VIÊN PHẢN BIỆN" (một trang); mẫu: "… PHẢN BIỆN 1" (P0138) và "… PHẢN BIỆN 2" (P0163). — [Mẫu P0116–P0183, DOCX P0082–P0120][DOCX]
- Danh mục viết tắt: mẫu là bảng 3 cột "Từ viết tắt | Từ đầy đủ | Nghĩa" (P0198); bản cuối cùng 3 cột, 27 mục (P0253). — [DOCX P0253][DOCX]

### Inferences
- Danh sách chữ của mẫu ghi "Giáo viên phản biện" số ít, còn phần mẫu có hai trang (PB1, PB2). Một trang chung là chấp nhận được về chữ nhưng lệch với tệp mẫu; nếu khoa phân hai phản biện thì nên có hai trang.
- Abstract/Tóm tắt 2 trang là vi phạm rõ chữ "trình bày trong một trang A4". Phần tràn chỉ khoảng 5–6 dòng mỗi bản (trang 5 và 7 chỉ còn một đoạn + từ khóa), nên rút gọn là đủ.

### Gaps
- Không rõ khoa có yêu cầu chữ ký/ngày trên trang lời cảm ơn hay không (chỉ thấy trong mẫu, không có câu chữ hướng dẫn).

## 4. Đánh số trang và section

### Takeaway
Đánh số đúng chữ của mẫu (phải-dưới, bắt đầu 1 ở nội dung, phụ lục không số) và đúng cơ chế tệp mẫu (La Mã ẩn ở phần đầu, chữ cái ẩn ở tài liệu tham khảo). Mục lục hiển thị "xii", "a", "e"… cho các trang không in số — giống hệt mục lục trong tệp mẫu.

### Cited Findings
- Hướng dẫn chữ (nguyên văn): "Số trang: được đánh bên phải, phía dưới mỗi trang giấy bắt đầu từ trang số 1 tính từ phần nội dung báo cáo khóa luận tốt nghiệp, không đánh số trang phần phụ lục. Nếu có bảng biểu, hình vẽ trình bày theo chiều ngang khổ giấy thì đầu bảng là lề trái của trang." — [Mẫu P0271][MAU]
- Section bản cuối: (1) bìa — không footer, không pgNumType; (2) phần đầu — `pgNumType fmt=lowerRoman start=1`, footer1 rỗng; (3) nội dung — `pgNumType start=1`, header1 + footer2 (`jc=right`, tên SV + field `PAGE`); (4) tài liệu tham khảo — `lowerLetter start=1`, footer3 (tên SV, không `PAGE`); (5) phụ lục + nhật ký — `lowerLetter` (không `start`, đánh tiếp), footer4 rỗng. Mẫu: giống hệt trừ section 5 mẫu là `start=1` thập phân, `type=continuous`. — [DOCX/Mẫu sectPr][DOCX]
- Ảnh trang PDF 17: footer có đường kẻ, dòng "Phạm Hoàng Phát – Thân Trọng Tính – KHDL18A" căn phải, số "1" căn phải ngay dưới. Trang PDF 101: footer tên SV, không số. Trang PDF 105: không footer, không số. — [PDF trang 17, 101, 105][PDF]
- Section 4–5 không có `headerReference` nên kế thừa header1 — trang PDF 101–112 vẫn in "Khóa luận tốt nghiệp năm 2026 – Ngành Khoa học dữ liệu"; mẫu cũng vậy (section 4–5 mẫu không có headerReference). — [DOCX sectPr; PDF trang 101–112][PDF]
- Mục lục bản cuối: "DANH MỤC HÌNH ẢNH…xii", "TÀI LIỆU THAM KHẢO…a", "PHỤ LỤC…e", "Phụ lục A…e", "Phụ lục B…f", "Phụ lục C…g", "Phụ lục D…j", "NHẬT KÍ LÀM VIỆC…k". Mục lục trong tệp mẫu (sdt P0188) cũng hiện "TÀI LIỆU THAM KHẢOa", "PHỤ LỤCc", "NHẬT KÍ LÀM VIỆCd". — [DOCX P0123–P0194; Mẫu P0188][DOCX]
- Không section nào xoay ngang (mọi `pgSz` dọc, không `orient`), nên quy tắc "đầu bảng là lề trái" không phát sinh. — [DOCX sectPr][DOCX]
- Header mẫu (header1): "Hướng dẫn và mẫu báo cáo khóa luận tốt nghiệp năm 2026" (tức tên tài liệu); footer2 mẫu: "Tên sinh viên 1 – Tên sinh viên 2" + PAGE, căn phải, có đường kẻ. Hướng dẫn chữ (nguyên văn): "Header thể hiện thông tin khóa khóa luận tốt nghiệp, footer thể hiện thông tin sinh viên thực hiện khóa khóa luận tốt nghiệp." Bản cuối header: "Khóa luận tốt nghiệp năm 2026 – Ngành Khoa học dữ liệu"; footer thêm lớp "KHDL18A". — [Mẫu P0272, `header1.xml`, `footer2.xml`][MAU]

### Inferences
- Header bản cuối thỏa câu chữ "thông tin khóa luận" ở mức chung, nhưng tệp mẫu đặt **tên tài liệu** vào header. Nếu GVHD hiểu "thông tin khóa luận" là tên đề tài thì cần đổi header (hoặc tên đề tài rút gọn). Đây là điểm cần xác nhận, không phải lỗi chắc chắn.
- Mục lục trỏ tới số trang chữ cái không in trên trang (a, e, f…) là kế thừa thiết kế của mẫu; người đọc bản in không tra được, nhưng sửa sẽ lệch tệp mẫu.

### Gaps
- Không rõ khoa muốn số La Mã hiện ở phần đầu hay không (tệp mẫu để footer1 rỗng; chữ không nhắc).

## 5. Tiêu đề chương và tiểu mục

### Takeaway
Chương đánh "CHƯƠNG n" bằng numbering tự động, tiểu mục 1.1 / 1.1.1, sâu tối đa 3 cấp số (giới hạn của mẫu là 4). Có **một vi phạm** quy tắc "mỗi mục đã chia phải có ít nhất 2 tiểu mục": mục 6.6 chỉ có 6.6.1.

### Cited Findings
- Hướng dẫn chữ (nguyên văn): "Tiểu mục: Các tiểu mục của báo cáo được trình bày và đánh số thành nhóm số, nhiều nhất gồm bốn chữ số với số thứ nhất là chỉ số chương. Tại mỗi mục, tiểu mục phải có ít nhất là 2 tiểu mục." và "Việc đánh số các tiểu mục sử dụng tối đa 4 chữ số." — [Mẫu P0273, P0287][MAU]
- `numbering.xml` bản cuối (giống mẫu): numId 32 → abstractNum 20: ilvl0 `"CHƯƠNG %1"` (Heading1), ilvl1 `"%1.%2"`, ilvl2 `"%1.%2.%3"`, ilvl3 `"%1.%2.%3.%4"`. — [DOCX `numbering.xml`][DOCX]
- Đếm đề mục bản cuối: Heading1 7, Heading2 46, Heading3 9, Heading4 0. Chương 1: 7 mục; Ch.2: 7; Ch.3: 4; Ch.4: 7; Ch.5: 7; Ch.6: 9 (6.3 có 6 tiểu mục, 6.5 có 2, **6.6 có 1 — "6.6.1 Chế độ backfill: giữ bộ lọc cứng và lấp chỗ trống"**); Ch.7: 5. Phụ lục dùng Heading2N không số (Phụ lục A–D). — [DOCX, script đếm theo style][DOCX]
- Mục lục bản cuối liệt kê "6.6 RQ3: truy hồi và câu trả lời có bằng chứng…69" rồi "6.6.1 Chế độ backfill…73" và không có 6.6.2. — [DOCX P0177–P0178][DOCX]
- Hướng dẫn chữ (nguyên văn): "Mục lục: Mục lục chỉ đưa đến nhóm tiểu mục thứ 3 (tức là đến 3 chữ số)." Bản cuối: field `TOC \o "1-3" \h \z \u`, có mục TOC3 (6.3.1…6.6.1). — [Mẫu P0277; DOCX P0123][DOCX]
- Ảnh trang PDF 17: "CHƯƠNG 1      GIỚI THIỆU" in đậm 14 pt, căn trái, sát lề trái; "1.1   Vì sao chọn đề tài" đậm. Trang PDF 83: "6.5.1 Mô tả so với nhãn gốc…" đậm nghiêng. — [PDF trang 17, 83][PDF]
- Mẫu chỉ là bố cục tham khảo (nguyên văn): "Sinh viên tùy theo đề tài mà đặt tên chương mục phù hợp." — [Mẫu P0350][MAU]

### Inferences
- Sửa 6.6: hoặc nâng 6.6.1 thành 6.7 (đánh lại số sau), hoặc tách nội dung 6.6 thành 6.6.1 (gold/parsed) + 6.6.2 (backfill). Tệp mẫu tự nó cũng vi phạm quy tắc này (mục 2.1 chỉ có 2.1.1) nhưng không nên dựa vào đó.

### Gaps
- Chưa kiểm "≥ 2 tiểu mục" cho phụ lục (Heading2N không đánh số — A, B, C, D là 4 mục, thỏa).

## 6. Bảng, hình, chú thích, dòng nguồn, tham chiếu chéo, ngắt trang

### Takeaway
Vị trí và cách đánh số chú thích đạt 100% (56/56). Vi phạm thật nằm ở **ngắt trang**: Bảng 6.13 (17 hàng, ngắn hơn một trang) bị cắt giữa trang 83–84, và bốn dòng "Nguồn:" bị đẩy sang trang sau, tách khỏi hình/bảng của nó. Bảng phụ lục đánh "Bảng PL.n" bằng chữ tĩnh, không vào danh mục bảng.

### Cited Findings
- Hướng dẫn chữ (nguyên văn): "Bảng, hình vẽ, công thức: Việc đánh số bảng, hình vẽ, công thức gắn với số chương (ví dụ Hình 3.4 có nghĩa là hình thứ 4 trong chương 3). Tiêu đề của bảng biểu ghi phía trên bảng, canh giữa, tiêu đề của hình vẽ ghi phía dưới hình, canh giữa, cỡ chữ phải bằng cỡ chữ sử dụng trong văn bản báo cáo, số công thức để trong ngoặc đơn và canh phải. Trong trường hợp công thức dài hơn một dòng thì số công thức được đánh ở dòng dưới canh phải." — [Mẫu P0274][MAU]
- Hướng dẫn chữ (nguyên văn): "Hình (bao gồm hình vẽ, hình chụp, đồ thị, lưu đồ, …), bảng biểu, công thức cần có chú thích (caption). Các chú thích này được tạo ra bằng chức năng Insert Caption (trong tab References) để dễ dàng quản lý và thay đổi thứ tự." — [Mẫu P0294][MAU]
- Hướng dẫn chữ (nguyên văn): "Các hình, bảng biểu phải được trình bày trong một trang (ngoại trừ các bảng dài hơn một trang), không để ngắt trang xảy ra ở giữa hình, bảng biểu. Để tránh việc ngắt trang này, có thể sử dụng một Text box (với layout có Wrapping style là Inline with text) để chứa các hình, bảng biểu cùng với các chú thích." — [Mẫu P0297][MAU]
- Caption mẫu: "Hình 2.1 Hình minh họa" = `Hình {STYLEREF 1 \s}.{SEQ Hình \* ARABIC \s 1}`; tương tự "Bảng 2.1". — [Mẫu P0293, P0295][MAU]
- Bản cuối: 56 đoạn Caption; script kiểm phần tử kề: 0 caption "Bảng" mà phần tử ngay sau không phải bảng, 0 caption "Hình" mà phần tử ngay trước không phải đoạn chứa ảnh (FigureParagraph, `keepNext`, căn giữa). Field: `SEQ Bảng` 30, `SEQ Hình` 19, `SEQ PT` 7, `STYLEREF` 56, `REF` 51, `PAGEREF` 121. Danh mục hình 19 mục (Hình 3.1–6.8), danh mục bảng 30 mục (Bảng 1.1–6.18). — [DOCX; kết quả `check_midterm_docx --docx …`][CHECK]
- Dưới mỗi bảng/hình có một đoạn TableNote "Nguồn: …" (56 đoạn, 11 pt nghiêng). Mẫu không yêu cầu dòng nguồn. — [DOCX][DOCX]
- Ngắt trang (từ `pdftotext` + ảnh trang): Bảng 6.13 "Ảo giác và bỏ sót của mô tả đầu–cuối…" (17 hàng): caption + 3 hàng cuối trang PDF 83, 13 hàng còn lại + dòng nguồn ở đầu trang PDF 84 (có lặp hàng tiêu đề). Trang PDF 35, 40, 91, 110 bắt đầu bằng dòng "Nguồn:" của Hình 3.3, Hình 4.1, Hình 6.7 và Bảng PL.6 (caption hình nằm dòng cuối trang PDF 34 và 39). Bảng PL.1 (23 hàng) tách trang 105→106, PL.2 (26 hàng) tách 106→107, một trong PL.5/PL.6 (22 hàng) tách 108→109. Danh mục viết tắt (28 hàng) tách trang 16. — [PDF trang 34–35, 39–40, 83–84, 90–91, 105–110][PDF]
- Style Caption bản cuối **không** có `keepNext` (chỉ caption PL.1 có `keepNext` trực tiếp); FigureParagraph có `keepNext` nên ảnh luôn đi cùng caption; TableNote không có gì giữ với phần trước. — [DOCX `styles.xml`][DOCX]
- Bảng phụ lục: caption "Bảng PL.1 … PL.7" là chữ tĩnh (không có field SEQ), không xuất hiện trong DANH MỤC BẢNG BIỂU. — [DOCX P0743–P0768][DOCX]
- Mọi bảng (39/39) có hàng tiêu đề lặp (`tblHeader`). — [kết quả `check_midterm_docx`][CHECK]

### Inferences
- Bảng 6.13 ngắn hơn một trang nên bị cắt là vi phạm trực tiếp "không để ngắt trang xảy ra ở giữa … bảng biểu". Cách sửa ít tốn: thêm `keepNext` cho mọi hàng (hoặc `cantSplit` + keep with next) hoặc chèn ngắt trang trước caption.
- Dòng "Nguồn:" bị tách khỏi hình là vi phạm tinh thần "cùng với các chú thích"; sửa bằng `keepNext` trên Caption của hình (để caption kéo theo dòng nguồn) hoặc `keepLines`/`keepNext` hợp lý.
- Bảng phụ lục dài 22–26 hàng: cần xem trên PDF có thực sự dài hơn một trang không; nếu không thì cũng thuộc loại vi phạm như Bảng 6.13.

### Gaps
- Mẫu không nói cách đánh số bảng trong phụ lục, cũng không nói bảng phụ lục có vào danh mục bảng hay không — "Bảng PL.n" là lựa chọn hợp lý nhưng không đối chiếu được.

## 7. Công thức

### Takeaway
Đạt: số công thức theo chương, trong ngoặc đơn, căn phải bằng tab phải; công thức căn giữa bằng tab giữa.

### Cited Findings
- Quy tắc (nguyên văn, như mục 6): "… số công thức để trong ngoặc đơn và canh phải. Trong trường hợp công thức dài hơn một dòng thì số công thức được đánh ở dòng dưới canh phải." — [Mẫu P0274][MAU]
- Bản cuối: 7 đoạn style Equation (basedOn Content, before/after 6 pt, line 1,15), mỗi đoạn có `tabs center 4393 + right 8787`, công thức OMML, số "({STYLEREF 1 \s}.{SEQ PT \s 1})" → (1.1), (1.2), (2.1)–(2.3), (4.1), (4.2). — [DOCX P0263, P0265, P0300, P0302, P0305, P0442, P0446][DOCX]
- Ảnh trang PDF 18: công thức (1.1) và (1.2) nằm giữa dòng, số căn phải sát lề. — [PDF trang 18][PDF]

### Inferences
- Không thấy công thức nào dài quá một dòng trên các trang đã xem; trường hợp "số xuống dòng dưới" không phát sinh.

### Gaps
- Chỉ xem ảnh trang 18; công thức (2.1)–(2.3), (4.1), (4.2) chưa xem ảnh, chỉ xác nhận cấu trúc tab.

## 8. Tài liệu tham khảo và trích dẫn

### Takeaway
Nhóm theo ngôn ngữ, alphabet theo họ, đánh "[n].", dòng sau lùi 1 cm, tên tạp chí/kỷ yếu in nghiêng, tên bài trong ngoặc kép — đạt. Lệch nhỏ: mục web dùng "(năm)" thay "(tháng-năm)", có "truy cập dd/mm/yyyy" và dấu chấm cuối; mục bài báo đuôi bằng DOI thay vì kết bằng số trang; một mục (Schmid [25]) viết tắt tên đệm khác các mục còn lại.

### Cited Findings
- Hướng dẫn chữ (nguyên văn): "Tài liệu tham khảo được xếp theo nhóm ngôn ngữ với thứ tự tiếng: Việt, Anh, Pháp, Đức, Nga, Trung, Nhật; giữ nguyên văn tiếng nước ngoài, không phiên dịch." và "Danh mục tài liệu tham khảo được xếp theo thứ tự bảng chữ cái (alphabet) về họ hoặc tên tác giả theo thông lệ từng nước: - Tác giả là người nước ngoài: xếp thứ tự bảng chữ cái đối với họ; - Tác giả là người Việt Nam: xếp thứ tự bảng chữ cái theo tên, không đảo tên trước họ; - Tài liệu không có tên tác giả: xếp thứ tự theo bảng chữ cái đối với từ đầu tiên của tên cơ quan đã ấn hành tài liệu…" — [Mẫu P0387–P0391][MAU]
- Định dạng bài báo/kỷ yếu/sách (nguyên văn): "- tên các tác giả (có dấu phẩy ngăn cách giữa các tên tác giả) - (năm công bố), (đặt trong ngoặc đơn, có dấu phẩy sau ngoặc đơn) - “tên bài báo”, (trong ngoặc kép, không in nghiêng, dấu phẩy ngay sau đóng ngoặc kép) - tên tạp chí (in nghiêng, cuối tên không có dấu phẩy) hoặc tên sách, (in nghiêng, dấu phẩy cuối tên) - tập (không có dấu ngăn cách) - (số), (đặt trong ngoặc đơn, dấu phẩy sau ngoặc đơn) - các số trang. (gạch ngang giữa hai chữ số, và dấu chấm để kết thúc)". — [Mẫu P0392–P0399][MAU]
- Trang web (nguyên văn): "- tên trang web (có dấu phẩy ngăn cách giữa các tên) - (tháng-năm xuất bản), (đặt trong ngoặc đơn, dấu phẩy sau ngoặc đơn) - địa chỉ trang web (không cần dấu chấm kết thúc)"; ví dụ "[16]. National Center for Bio-technology (Oct. 2005), http://www.ncbi.nlm.nih.gov". — [Mẫu P0407–P0410, P0425][MAU]
- Lùi dòng (nguyên văn): "Khi nội dung tài liệu vượt quá một dòng, những dòng tiếp sau cần phải lùi vào 1cm so với dòng đầu tiên để làm rõ mục tài liệu tham khảo." — [Mẫu P0411][MAU]
- Bản cuối: tiêu đề nhóm "Tiếng Việt" (P0709) với [1] "Bộ Nông nghiệp và Môi trường (2025), *QCVN 26:2025/BNNMT: …*, …, https://…pdf, truy cập 23/11/2026."; "Tiếng Anh" (P0711) với [2]–[28]: Artuso, Bilen, Bruch, Chen J., Chen S., DCASE ×4, Ebbers, Fredianelli, goyumsamuditha, Guo, Hegde, Ji, Kong, Kuan, Kumar, Lewis, Mesaros ×2, Nam, Schmid ×2, Weck, Wijngaard, Zhang — đúng alphabet theo họ. — [DOCX P0708–P0738][DOCX]
- Style Bibliography1: `ind left 567 hanging 567` (dòng đầu ở lề, dòng sau lùi 1,0 cm), before 0 after 6 pt, line 1,15, TNR 13; ảnh trang PDF 101 cho thấy dòng thứ hai trở đi lùi vào. — [DOCX `styles.xml`; PDF trang 101][PDF]
- Mẫu ví dụ tiếng Anh: "[11]. Jeffrey Inman, Russell S. Winer, Rosellina F. (2009), “The Interplay …”, Jour. of Marketing, Vol.73 (2), pp.19-29." Bản cuối ví dụ: "[22]. Annamaria Mesaros, Toni Heittola, Tuomas Virtanen, Mark D. Plumbley (2021), “Sound Event Detection: A Tutorial”, *IEEE Signal Processing Magazine*, Vol. 38 (5), pp. 67–83, DOI: 10.1109/MSP.2021.3090678." — [Mẫu P0421–P0422; DOCX P0732][DOCX]
- Thống kê đuôi mục bản cuối: 13/28 mục có DOI ở cuối (sau số trang nếu có); 9 mục arXiv kết thúc "arXiv preprint arXiv:…vN."; 6 mục web/GitHub/QCVN kết thúc "truy cập dd/mm/yyyy."; mục web DCASE ghi "(2016)", "(2022)", "(2023)" (năm, không tháng-năm). Mục [25] "Florian Schmid, C. I. Tang, S. Parekh, V. K. Ithapu, …" viết tắt tên đệm, khác các mục khác viết đủ tên. — [DOCX P0710–P0738][DOCX]
- Trích dẫn trong thân dạng số "[22]", "[3, 21]" tương ứng số trong danh mục (đã nhóm + alphabet). Mẫu không quy định cách trích trong thân; danh mục mẫu dùng "[n].". — [PDF trang 17, 29][PDF]

### Inferences
- Thêm DOI và ngày truy cập là thông lệ học thuật tốt, nhưng trái chữ "dấu chấm để kết thúc" sau số trang và "không cần dấu chấm kết thúc" ở mục web. Nếu GVHD soát chặt định dạng thì đây là chỗ dễ bị nhắc; nếu không, giữ DOI có lợi cho truy vết.
- Gạch nối số trang: bản cuối dùng "–" (en dash), mẫu ví dụ dùng "-"; chữ chỉ nói "gạch ngang" nên coi là đạt.

### Gaps
- Không kiểm xem mọi mục trong danh mục đều được trích trong thân (đó là nội dung, không phải định dạng; `kiem_tra_bao_cao.md` bản giữa kỳ ghi là đã kiểm).

## 9. Phụ lục và nhật ký làm việc

### Takeaway
Đạt: phụ lục ở section riêng không in số trang, mỏng hơn hẳn phần chính; có trang "NHẬT KÍ LÀM VIỆC" đúng cột của mẫu.

### Cited Findings
- Hướng dẫn chữ (nguyên văn): "Phụ lục của báo cáo: Phần này bao gồm những nội dung cần thiết nhằm minh họa hoặc bổ trợ cho nội dung báo cáo, như: chương trình tính, kết quả khảo sát trên mô hình số, các số liệu, mẫu biểu, tranh ảnh... Phụ lục không được đánh số trang, không được dày hơn phần chính của báo cáo." — [Mẫu P0276][MAU]
- Phần mẫu PHỤ LỤC (nguyên văn): "Phần phụ lục bao gồm những bổ sung hỗ trợ cho nội dung báo cáo khóa luận như: số liệu, biểu mẫu, mã chương trình, hình ảnh, tài liệu minh chứng, kết quả kiểm tra đạo v… nhằm làm rõ các nghiên cứu đã trình bày trong phần nội dung. Các tính toán đã trình bày tóm tắt trong phần nội dung phải được trình bày chi tiết trong phần phụ lục này." — [Mẫu P0427][MAU]
- Bản cuối: PHỤ LỤC (Heading1N) + Phụ lục A–D (Heading2N, vào mục lục cấp 2), trang PDF 105–110 (6 trang) + NHẬT KÍ LÀM VIỆC trang PDF 111–112, so với nội dung chính 84 trang (PDF 17–100); không in số trang (footer4 rỗng). — [PDF][PDF]
- Nhật ký: mẫu có "Đề tài: …", "Giảng viên hướng dẫn: …", "Ngày bắt đầu: …/…/…" (đậm) và bảng 16 hàng "Tuần | Từ ngày | Đến ngày | Ngày báo cáo GVHD | Tóm tắt công việc đã thực hiện | Nhận xét của GVHD". Bản cuối: cùng ba dòng (đề tài đầy đủ, TS. Huỳnh Công Bằng, 22/09/2026) và bảng 11 hàng cùng 6 cột. — [Mẫu P0428–P0432; DOCX P0772–P0776][DOCX]

### Inferences
- Mẫu không cấm có tiêu đề cấp 2 trong phụ lục; Heading2N không đánh số là hợp lý.

### Gaps
- Mẫu không nói nhật ký nằm trước hay sau phụ lục — cả mẫu và bản cuối đều đặt sau.

## 10. Giới hạn số trang

### Takeaway
Mẫu khoa **không** đặt giới hạn tổng số trang. Ràng buộc về độ dài trong mẫu chỉ có: Abstract/Tóm tắt 1 trang A4 (đang vi phạm), poster 1 trang A0, phụ lục không dày hơn phần chính (đạt).

### Cited Findings
- Tìm mọi câu có "trang", "tối đa", "tối thiểu", "giới hạn" trong chữ của mẫu: chỉ thấy các quy định đã nêu (P0074, P0086, P0271, P0276, P0287, P0297, P0303, P0385 "Mỗi nhóm chỉ trình bày trong 1 trang A0"). — [Mẫu, toàn văn][MAU]
- Bản cuối 112 trang PDF: 16 trang phần đầu, 84 trang nội dung, 4 trang tài liệu tham khảo, 6 trang phụ lục, 2 trang nhật ký. — [PDF, `pdfinfo` + `pdftotext`][PDF]

### Inferences
- Giới hạn 150 trang mà dự án đang dùng không đến từ mẫu khoa (nguồn khác: người dùng/GVHD).

### Gaps
- Không có quy định số trang tối thiểu/tối đa trong mẫu để đối chiếu.

## 11. Kiểm tra trực quan trên PDF

### Takeaway
Ảnh trang xác nhận bố cục đúng ở bìa, mục lục, đầu chương, trang bảng, trang hình, tài liệu tham khảo, phụ lục, nhật ký; đồng thời lộ ra các lỗi ngắt trang ở mục 6.

### Cited Findings
- Trang 1 (bìa chính): viền kép quanh trang, logo IUH, chữ căn giữa, tiêu đề 3 dòng đậm lớn, "Ngành: Khoa học dữ liệu" sát dưới tiêu đề, dòng tháng/năm ở đáy. Trang 2: bìa phụ giống trang 1, không viền. Trang 3: bìa EN có khung chữ nhật mảnh, tiêu đề Title Case 3 dòng. — [PDF trang 1–3][PDF]
- Trang 11 (MỤC LỤC): tiêu đề đậm căn giữa; dòng TOC1 "CHƯƠNG 1   GIỚI THIỆU ……… 1" IN HOA, TOC2 lùi nhẹ, dấu chấm dẫn tới số trang căn phải; không có header/footer hiển thị. — [PDF trang 11][PDF]
- Trang 17 (đầu Chương 1): header "Khóa luận tốt nghiệp năm 2026 – Ngành Khoa học dữ liệu" + đường kẻ; "CHƯƠNG 1 GIỚI THIỆU" căn trái đậm; thân căn đều, giãn 1,5, không thụt đầu dòng, khoảng cách đoạn rõ; footer tên SV + lớp căn phải, số "1" phía dưới bên phải. — [PDF trang 17][PDF]
- Trang 22 (bảng): caption "Bảng 1.3 …" căn giữa phía trên bảng; bảng 4 cột chữ 10–11 pt, hàng tiêu đề đậm nền xám; dòng "Nguồn: …" nghiêng dưới bảng; tiếp theo "1.7 Bố cục báo cáo". — [PDF trang 22][PDF]
- Trang 34 (hình): hình 3.2 + caption căn giữa dưới hình + dòng nguồn; hình 3.3 + caption ở cuối trang, **dòng nguồn của hình 3.3 sang trang 35**. — [PDF trang 34–35][PDF]
- Trang 83–84: caption Bảng 6.13 và 3 hàng đầu ở cuối trang 83, phần còn lại trang 84 (bảng bị cắt). — [PDF trang 83–84][PDF]
- Trang 101 (TÀI LIỆU THAM KHẢO): tiêu đề căn giữa đậm; nhóm "Tiếng Việt", "Tiếng Anh" đậm; mục "[n]." với dòng sau lùi vào; tên tạp chí nghiêng; header vẫn in, footer chỉ tên SV, không số trang. — [PDF trang 101][PDF]
- Trang 105 (PHỤ LỤC): tiêu đề căn giữa; "Phụ lục A. …" đậm; caption "Bảng PL.1 …" trên bảng; không footer, không số trang. Trang 111 (NHẬT KÍ LÀM VIỆC): tiêu đề căn giữa, ba dòng thông tin đậm/thường. — [PDF trang 105, 111][PDF]

### Inferences
- Không thấy lỗi field ("Error! Reference…") hay ký tự thực thể XML — khớp kết quả kiểm tự động.

### Gaps
- Chỉ dựng ảnh 15/112 trang; các trang khác chỉ kiểm qua chữ trích (`pdftotext`), nên có thể còn ngắt trang xấu chưa phát hiện ngoài các mẫu đã quét tự động (trang bắt đầu bằng hàng tiêu đề lặp hoặc bằng "Nguồn:").

## 12. Những gì `check_midterm_docx` KHÔNG kiểm (và lỗi vận hành của nó)

### Takeaway
Công cụ kiểm hiện chỉ kiểm khổ ngang, lề, spacing/line của 8 style, phông Normal, số field, footer có PAGE và vài dấu hiệu sót. Gần như mọi vi phạm tìm thấy ở trên (Abstract 2 trang, 6.6 một tiểu mục, bảng bị cắt, dòng nguồn mồ côi, viết tắt trước định nghĩa, định dạng TLTK) nằm ngoài phạm vi kiểm. Ngoài ra đường dẫn mặc định của nó trỏ vào **bản giữa kỳ**.

### Cited Findings
- Hằng số `DOCX = ROOT / "report" / "Bao_cao_KLTN_giua_ky_environmental_audio_rag.docx"` — chạy không có `--docx` sẽ kiểm bản giữa kỳ, không phải bản cuối. — [scripts/check_midterm_docx.py dòng 19][CHECK]
- `EXPECTED_STYLES` chỉ có Heading1–4, Content, Caption, TOC1, TableofFigures với (cỡ, before, after, line); cỡ chỉ kiểm cho Heading1. Không kiểm: đậm/nghiêng/IN HOA của Heading 2–4 (chỉ in ra), `jc`, `ind`, phông của heading, TOC2/TOC3, Bullet, Heading1N, CoverB, TableText/TableNote, Bibliography1. — [scripts/check_midterm_docx.py dòng 23–32, 125–135][CHECK]
- Section: kiểm lề 4 cạnh và chiều rộng `abs(w − 11906) ≤ 2`; **không** kiểm chiều cao trang, gutter, khoảng cách header/footer; `pgNumType` chỉ được in ra, không so với kỳ vọng (dòng "Đạt" chỉ dựa vào lề + khổ ngang). — [dòng 103–123][CHECK]
- "Font Normal" chỉ đạt/không theo `w:ascii="Times New Roman"`; không kiểm cỡ 26 trong điều kiện đạt. — [dòng 136–145][CHECK]
- Field: điều kiện đạt chỉ là `TOC \o` = 1 và `TOC \h` = 2; không kiểm mức "1-3". — [dòng 146–153][CHECK]
- Footer: chỉ kiểm danh sách footer chứa chữ "PAGE" là đúng `footer2.xml`; không kiểm vị trí phải/dưới, nội dung header/footer. — [dòng 154–157][CHECK]
- Các dòng "Placeholder [CẦN ĐIỀN", "CẦN XÁC MINH", "Bảng có hàng tiêu đề lặp", "Ảnh trong thân" luôn trả `True` (chỉ thông tin, không chặn). — [dòng 161–171][CHECK]
- PDF: chỉ đếm số trang, chuỗi lỗi field và thực thể XML. — [dòng 175–190][CHECK]
- Kết quả chạy `--docx report/Khoa_luan_environmental_audio_rag.docx` ngày 24/11: mọi dòng ✅ (5 section; style Heading1 sz=28/480/480/276/caps; Heading2–4 120/240/276; Content 200/0/360; Caption 120/240/276 không nghiêng; TOC1, TableofFigures 0/0/276; field PAGEREF 121, REF 51, SEQ Bảng 30, SEQ Hình 19, SEQ PT 7, STYLEREF 56, TOC \h 2, TOC \o 1; bảng 39/39 lặp tiêu đề; 25 ảnh; PDF 112 trang; 0 lỗi field; 0 thực thể). — [chạy `scripts.check_midterm_docx`][CHECK]

Danh sách quy tắc của mẫu **không** được kiểm tự động:
1. Chiều cao A4 và "một mặt giấy".
2. Đậm/nghiêng/căn trái/không thụt của Heading 1–4; nhãn "CHƯƠNG n".
3. Căn đều và không thụt của Content; định dạng Bullet.
4. Cỡ 10–13 TNR cho "đề mục khác" (bảng, dòng nguồn).
5. Nội dung header (thông tin khóa luận) và footer (thông tin SV); vị trí số trang phải-dưới; phụ lục không in số.
6. Quy tắc ≥ 2 tiểu mục; độ sâu ≤ 4 cấp; mục lục ≤ 3 cấp (chỉ đếm có field).
7. Vị trí caption (bảng trên, hình dưới) và cỡ caption bằng văn bản.
8. Không ngắt trang giữa hình/bảng và chú thích.
9. Số công thức trong ngoặc, căn phải.
10. Viết tắt: viết đầy đủ lần đầu; danh mục khi > 10 từ, sắp A–Z.
11. Thứ tự và sự có mặt các trang phần đầu; Abstract/Tóm tắt 1 trang.
12. Tài liệu tham khảo: nhóm ngôn ngữ, alphabet theo họ/tên, mẫu mục, lùi 1 cm.
13. Phụ lục không dày hơn phần chính.
14. Toàn bộ trong một file Word (chỉ gián tiếp qua số section).

### Inferences
- Nếu muốn khóa các lỗi đã tìm, các kiểm rẻ nhất để thêm là: (a) số trang PDF giữa "ABSTRACT" và "TÓM TẮT" = 1, giữa "TÓM TẮT" và "LỜI CẢM ƠN" = 1; (b) đếm Heading3 dưới mỗi Heading2 ≠ 1; (c) trang PDF bắt đầu bằng "Nguồn:" hoặc bằng hàng tiêu đề lặp của bảng ngắn; (d) đổi đường dẫn mặc định sang bản cuối.

### Gaps
- Không chạy lại `update_docx_fields.ps1`/Word nên không biết ngắt trang có đổi khi Word trên máy khác dựng lại (bố cục PDF là do Word trên máy này xuất, như `kiem_tra_bao_cao.md` §6 đã ghi).

## 13. Quy tắc viết tắt — chi tiết phần "viết đầy đủ lần đầu"

### Takeaway
Danh mục 27 từ đạt (có, sắp A–Z). Nhưng nhiều từ xuất hiện lần đầu trong thân **trước** khi được viết đầy đủ (hoặc không bao giờ được viết đầy đủ trong thân), trái câu "Viết tắt sau lần viết đầy đủ thứ nhất".

### Cited Findings
- Hướng dẫn chữ (nguyên văn): "Viết tắt: Chỉ viết tắt những từ, cụm từ hoặc thuật ngữ được sử dụng nhiều lần trong báo cáo. Viết tắt sau lần viết đầy đủ thứ nhất và chữ viết tắt để trong ngoặc đơn. Nếu báo cáo có nhiều hơn 10 chữ viết tắt thì phải có bảng danh mục các chữ viết tắt (xếp theo thứ tự A, B, C) ở phần đầu báo cáo." — [Mẫu P0275][MAU]
- Danh mục bản cuối (27): AAC, ADR, API, BiGRU, CI, CNN, CPU, CRNN, cSEBB, DCASE, ECE, GPU, HNSW, JSON, LBR, LLM, MFCC, MRR, nDCG, OOF, PANNs, PSDS, RAG, RQ, SEBB, SED, SQL — đúng thứ tự chữ cái (không phân biệt hoa thường). — [DOCX P0253][DOCX]
- Lần xuất hiện đầu trong thân (trang nội dung 1–84, từ `pdftotext`): viết đúng kiểu "đầy đủ (VIẾT TẮT)" ở SED (tr.1 "Sound Event Detection – SED"), RAG (tr.1), RQ (tr.4), CRNN/CNN (tr.8), CI (tr.38), AAC (tr.12). Xuất hiện trước/không kèm dạng đầy đủ: OOF (tr.3, "số OOF của các tập lớp"), ADR (tr.3, "theo ADR-0001"), LBR (tr.4, "của LBR V2 là 0,3120"), nDCG (tr.4), PSDS và SEBB và SQL (tr.6, trong Bảng 1.3 — PSDS được giải thích ở tr.9), DCASE (tr.9), cSEBB (tr.10), GPU (tr.11), MRR (tr.13), MFCC (tr.19), JSON (tr.33), API (tr.38), CPU (tr.39), HNSW (tr.40), ECE (tr.49, trong bảng), LLM (lần khớp đầu ở tr.65). — [PDF trang 17–100, quét tự động][PDF]

### Inferences
- Một số từ (API, CPU, GPU, JSON, SQL) là thông dụng, hội đồng ít bắt bẻ; các từ riêng của đề tài (OOF, LBR, nDCG, PSDS, SEBB/cSEBB, ADR) nên được viết đầy đủ ở lần đầu trong Chương 1.

### Gaps
- Quét bằng `pdftotext -layout` có thể đảo thứ tự chữ trong bảng nhiều cột; kết quả "lần đầu" của các từ nằm trong bảng (PSDS, SEBB, SQL, ECE) và của LLM cần xác minh thủ công trên DOCX.
