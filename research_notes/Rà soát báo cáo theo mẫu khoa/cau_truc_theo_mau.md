# Cấu trúc báo cáo cuối so với mẫu khoa (Khoa CNTT – IUH, ngành Khoa học dữ liệu)

Phạm vi: chỉ cấu trúc (thành phần, chương/mục, nội dung bắt buộc, độ sâu đề mục, ngân sách trang). Không xét định dạng
style chi tiết (đã có ở `report/quy_cach_bao_cao.md`) và không xét nội dung khoa học.

**Nguồn và cách trích dẫn trong ghi chú này**

- **Mẫu** = `report/Mau bao cao KLTN_DS (1).docx`. Đã kiểm bằng `cmp`: giống từng byte với `report/Mau bao cao KLTN_DS.docx`.
  Văn bản được trích bằng cách đọc `word/document.xml` (lxml), mỗi đoạn kèm tên style. "Mẫu ¶N" là đoạn thứ N trong
  danh sách các đoạn có chữ, theo thứ tự tài liệu (389 đoạn; bản trích nằm ở
  `C:\Users\patph\AppData\Local\Temp\claude\85ae35366b529c68\b4942c2f-c1bf-4b4b-81ce-f0801cbaaca1\scratchpad\tpl.txt`).
- **PDF** = `report/Khoa_luan_environmental_audio_rag.pdf` (112 trang PDF, ModDate 24/11/2026 12:55), trích bằng poppler
  `pdftotext -layout`. "PDF p.X" là trang vật lý; "tr. Y" là số trang in. Trang 1 của phần nội dung là PDF p.17
  (tr. Y = PDF p.(Y+16)).
- **Nguồn markdown** = `report/final_src/*.md`, trích dạng `tệp:dòng`.
- Số từ, số đoạn của từng mục do script đếm trên markdown (bỏ dòng bảng `|…|` và chỉ thị `@@…@@`); bản đếm ở
  `C:\Users\patph\AppData\Local\Temp\claude\85ae35366b529c68\b4942c2f-c1bf-4b4b-81ce-f0801cbaaca1\scratchpad\sec.py`.
- Đây là việc đọc tệp cục bộ, không có nguồn web. Theo quy ước của coordinator, "nguồn" ở đây là đường dẫn tệp kèm
  dòng/đoạn/trang.

---

## 1. Cây đề mục (H1–H3) của báo cáo cuối, kèm số trang

### Takeaway
Báo cáo có 7 chương đánh số, 52 mục cấp 2 và 9 mục cấp 3 (chỉ ở Chương 6). Không có mục cấp 4. Phần nội dung dài
84 trang (tr. 1–84); riêng Chương 6 chiếm 33 trang (39%).

### Cited Findings

Lấy từ Mục lục (PDF p.11–12), đối chiếu với tiêu đề `#`/`##`/`###` trong nguồn markdown.

**Phần đầu (PDF p.1–16, không đánh số Ả Rập)**

| PDF p. | Thành phần | Nguồn |
|---|---|---|
| 1 | Bìa chính VI | front_info.yaml |
| 2 | Bìa phụ VI | front_info.yaml |
| 3 | Bìa EN | front_info.yaml |
| 4–5 | ABSTRACT (**2 trang**: từ khóa nằm ở p.5) | 00_phan_dau.md:1 |
| 6–7 | TÓM TẮT (**2 trang**: từ khóa nằm ở p.7) | 00_phan_dau.md:15 |
| 8 | LỜI CẢM ƠN | 00_phan_dau.md:29 |
| 9 | NHẬN XÉT CỦA GIÁO VIÊN HƯỚNG DẪN | 00_phan_dau.md:41 |
| 10 | NHẬN XÉT CỦA GIÁO VIÊN PHẢN BIỆN (**một trang**) | 00_phan_dau.md:47 |
| 11–12 | MỤC LỤC | 00_phan_dau.md:53 |
| 13 | DANH MỤC HÌNH ẢNH (19 hình) | 00_phan_dau.md:59 |
| 14–15 | DANH MỤC BẢNG BIỂU (30 bảng) | 00_phan_dau.md:65 |
| 16 | DANH MỤC CÁC THUẬT NGỮ VIẾT TẮT (27 mục) | 00_phan_dau.md:71 |

**Phần nội dung (tr. 1–84)**

| Đề mục | Trang bắt đầu | Nguồn | Số từ prose / đoạn | Bảng / hình |
|---|---|---|---|---|
| **CHƯƠNG 1 GIỚI THIỆU** | 1 | 01_gioi_thieu.md:1 | (không có đoạn mở chương) | 3 bảng |
| 1.1 Vì sao chọn đề tài | 1 | :3 | 399 / 4 | |
| 1.2 Bài toán đặt ra | 2 | :13 | 225 / 8 (có 2 công thức) | |
| 1.3 Bối cảnh ứng dụng tại Việt Nam | 2 | :31 | 539 / 3 | Bảng 1.1 |
| 1.4 Mục tiêu và câu hỏi nghiên cứu | 4 | :53 | 285 / 3 | Bảng 1.2 |
| 1.5 Phạm vi và giới hạn | 5 | :71 | 150 / 2 | |
| 1.6 Đóng góp dự kiến | 5 | :77 | 101 / **1** | Bảng 1.3 (bảng lớn) |
| 1.7 Bố cục báo cáo | 6 | :94 | **68 / 1** | |
| **CHƯƠNG 2 CƠ SỞ LÝ THUYẾT** | 8 | 02_co_so_ly_thuyet.md:1 | mở chương 46 từ | **0 bảng, 0 hình** |
| 2.1 Phát hiện sự kiện âm thanh | 8 | :5 | 283 / 3 | |
| 2.2 Cách đánh giá | 8 | :13 | 467 / 13 | |
| 2.3 Từ xác suất thành sự kiện | 10 | :41 | 395 / 3 | |
| 2.4 Học chuyển giao | 10 | :49 | 341 / 4 | |
| 2.5 Mô tả có bám sát sự kiện và ảo giác | 11 | :59 | 348 / 2 | |
| 2.6 Truy hồi và RAG | 12 | :65 | 385 / 4 | |
| 2.7 Vị trí của đề tài | 13 | :75 | 298 / 3 | |
| **CHƯƠNG 3 DỮ LIỆU** | 15 | 03_du_lieu.md:1 | mở chương 73 từ | 2 bảng, 3 hình |
| 3.1 Hai bộ dữ liệu | 15 | :5 | 402 / 4 | |
| 3.2 Các lớp âm thanh | 16 | :15 | 414 / 10 | Hình 3.1, 3.2 |
| 3.3 Quy trình chuẩn bị dữ liệu | 18 | :44 | 800 / 8 | Hình 3.3, Bảng 3.1, 3.2 |
| 3.4 Nhãn thiếu và độ nhất quán của nhãn | 21 | :74 | 376 / 3 | |
| **CHƯƠNG 4 PHƯƠNG PHÁP** | 23 | 04_phuong_phap.md:1 | mở chương 72 từ | 2 bảng, 5 hình |
| 4.1 Kiến trúc tổng thể | 23 | :5 | 161 / 3 | Hình 4.1, Bảng 4.1 |
| 4.2 Mô hình phân loại trên DataSEC | 24 | :34 | 287 / 2 | |
| 4.3 Mô hình phát hiện sự kiện (SED) | 25 | :40 | **1218 / 15** (tr. 25–28) | Hình 4.2–4.4 |
| 4.4 Ghép xác suất thành sự kiện | 29 | :83 | 247 / 4 | |
| 4.5 Sinh mô tả bám sát sự kiện | 30 | :93 | 806 / 14 | Hình 4.5 |
| 4.6 Truy hồi và trả lời có bằng chứng | 32 | :122 | 444 / 4 | Bảng 4.2 |
| 4.7 Cách đánh giá | 33 | :143 | 777 / 12 (tr. 33–35) | |
| **CHƯƠNG 5 TRIỂN KHAI HỆ THỐNG** | 36 | 05_trien_khai.md:1 | mở chương 50 từ | 5 bảng, 3 hình |
| 5.1 Tình huống sử dụng và yêu cầu | 36 | :5 | 298 / 3 | Bảng 5.1 |
| 5.2 Tổ chức mã nguồn | 37 | :31 | 153 / 2 | |
| 5.3 Khối lượng thực hiện | 38 | :37 | 97 / 2 | Bảng 5.2, 5.3 |
| 5.4 Các dịch vụ | 39 | :62 | 624 / 6 | Hình 5.1, 5.2 |
| 5.5 Độ trễ | 42 | :84 | 303 / 2 | Bảng 5.4 |
| 5.6 Chạy demo | 43 | :98 | 321 / 4 | |
| 5.7 Tái lập và kiểm thử | 44 | :108 | 798 / 6 (tr. 44–47) | Bảng 5.5, Hình 5.3 |
| **CHƯƠNG 6 KẾT QUẢ VÀ THẢO LUẬN** | 48 | 06_ket_qua.md:1 | mở chương 182 từ + 4 gạch đầu dòng quy ước | 18 bảng, 8 hình |
| 6.1 Mô hình phân loại DataSEC | 48 | :10 | 471 / 3 | 2 bảng |
| 6.2 RQ1: học thêm từ DataSEC có giúp không? | 50 | :38 | 441 / 5 | 1 bảng, 1 hình |
| 6.3 Mô hình SED tiến bộ ra sao? | 52 | :58 | **0 từ trước 6.3.1** (tr. 52–61, 10 trang) | |
| 6.3.1 Vì sao event-F1 của v1 thấp? | 52 | :60 | 325 / 2 | |
| 6.3.2 Từ v1 đến v2 | 53 | :66 | 335 / 3 | |
| 6.3.3 Vòng chọn S13 và hệ f2 (mốc so sánh) | 54 | :74 | 551 / 5 | 2 bảng |
| 6.3.4 Giai đoạn O: chọn bằng dự đoán ngoài mẫu và hệ B0 | 56 | :96 | 207 / 2 | |
| 6.3.5 LBR và hệ thống cuối | 56 | :102 | 898 / 9 (tr. 56–60) | 3 bảng, 3 hình |
| 6.3.6 PSDS và lưới ngưỡng | 61 | :150 | 283 / 2 | 1 bảng |
| 6.4 Event-F1 khoảng 0,30 là cao hay thấp? | 62 | :160 | 349 / 3 | 2 bảng |
| 6.5 RQ2: mô tả có bám sát sự kiện không? | 64 | :188 | **1113 / 11** trước mục con (tr. 64–68) | 1 bảng, 1 hình |
| 6.5.1 Mô tả so với nhãn gốc: tách lỗi của bộ sinh khỏi lỗi của SED | 67 | :221 | 289 / 2 | 1 bảng |
| 6.5.2 Mô tả gộp theo lớp và rào đón theo điểm tin cậy | 68 | :233 | 467 / 5 | |
| 6.6 RQ3: truy hồi và câu trả lời có bằng chứng | 69 | :245 | **1025 / 7** trước mục con (tr. 69–74) | 3 bảng, 1 hình |
| 6.6.1 Chế độ backfill: giữ bộ lọc cứng và lấp chỗ trống | 73 | :283 | 597 / 5 | 1 bảng, 1 hình |
| 6.7 Bộ phân tích câu hỏi và độ khớp khi phục vụ | 75 | :305 | 230 / 2 | 1 bảng |
| 6.8 Tái sử dụng tập test và mức tin cậy của các so sánh | 76 | :315 | 546 / 6 | 1 hình |
| 6.9 Thảo luận và hạn chế | 78 | :330 | 743 / 12 (tr. 78–80) | |
| **CHƯƠNG 7 KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN** | 81 | 07_ket_luan.md:1 | mở chương 53 từ | 0 |
| 7.1 Kết quả đạt được | 81 | :5 | 302 / 6 | |
| 7.2 Trả lời các câu hỏi nghiên cứu | 82 | :15 | 413 / 3 | |
| 7.3 Mức khẳng định cho các đóng góp | 83 | :23 | 205 / **1** | |
| 7.4 Hạn chế | 83 | :27 | **88 / 1** | |
| 7.5 Hướng phát triển | 83 | :31 | 192 / 5 gạch đầu dòng (tr. 83–84) | |

**Phần cuối**

| PDF p. | Trang in | Thành phần | Nguồn |
|---|---|---|---|
| 101–104 | a–d | TÀI LIỆU THAM KHẢO | 90_phan_cuoi.md:3 |
| 105 | e | PHỤ LỤC; Phụ lục A. Hệ lớp và số sự kiện đa âm (Bảng PL.1) | 90_phan_cuoi.md:9, :13 |
| 106 | f | Phụ lục B. Artifact đã đóng băng (bảng freeze, sổ ghi test) | :23 |
| 107–109 | g–i | Phụ lục C. Kết quả theo lớp (3 bảng) | :39 |
| 110 | j | Phụ lục D. Phân công công việc và công cụ hỗ trợ | :57 |
| 111–112 | k–(l) | NHẬT KÍ LÀM VIỆC | :81 |

Số trang theo phần (trang vật lý của PDF):

| Phần | Số trang | Tỷ lệ trên 112 |
|---|---:|---:|
| Phần đầu (bìa → danh mục viết tắt) | 16 | 14% |
| Chương 1 | 7 | 6% |
| Chương 2 | 7 | 6% |
| Chương 3 | 8 | 7% |
| Chương 4 | 13 | 12% |
| Chương 5 | 12 | 11% |
| Chương 6 | **33** | **29%** (39% của phần nội dung) |
| Chương 7 | 4 | 4% |
| Tài liệu tham khảo | 4 | 4% |
| Phụ lục A–D | 6 | 5% |
| Nhật kí làm việc | 2 | 2% |

### Inferences
- Phần "kết quả" thực tế còn lấn sang ba chương khác: Chương 1 có số kết quả (1.3, Bảng 1.3), Chương 4 có hình chẩn đoán
  lỗi OOF (Hình 4.3, 4.4), Chương 5 có độ trễ và sổ run (5.5, 5.7). Nếu tính cả những phần này, khối số liệu còn nặng hơn 39%.
- Trong Chương 6, ba khối 6.3 (10 trang), 6.5 (5 trang) và 6.6 (6 trang) chiếm 21/33 trang.

### Gaps
- Không có trình đọc PDF có toạ độ (PyMuPDF/pypdf không cài). Số trang theo mục suy từ số trang bắt đầu trong Mục lục,
  nên số trang của từng mục cấp 2 chỉ là xấp xỉ ±1 trang.

---

## 2. Dàn ý mẫu và mọi chỉ dẫn "nội dung cần có" của mẫu khoa

### Takeaway
Mẫu khoa **không** áp một khung chương cứng. Nó có (a) danh sách 14 thành phần bắt buộc của cuốn báo cáo, (b) một dàn ý
chương 1–8 "có thể gồm" và (c) một chương "BỐ CỤC" mô tả nội dung từng chương "để tham khảo". Mẫu cho phép sinh viên
"tùy theo đề tài mà đặt tên chương mục phù hợp". Mẫu không có chỉ dẫn nào về "đối tượng nghiên cứu", "phương pháp nghiên
cứu", "ý nghĩa khoa học và thực tiễn", "bố cục khóa luận", "tóm tắt chương/tiểu kết", và không có hạn mức số trang hay tỷ
lệ giữa các chương.

### Cited Findings

**(a) Thành phần bắt buộc** — Mẫu ¶151–165, nguyên văn: "Về cơ bản một quyển báo cáo khóa luận gồm các phần cơ bản sau:
Bìa tiếng Việt; Bìa tiếng Anh; Trang Abstract tiếng Anh và Keywords; Trang Abstract tiếng Việt và từ khóa; Trang lời cảm
ơn; Trang Nhận xét và đánh giá của Giáo viên hướng dẫn; Trang Nhận xét và đánh giá của Giáo viên phản biện; Trang Mục lục;
Trang Mục lục hình ảnh; Trang Danh mục bảng biểu; Trang Danh mục từ viết tắt; Nội dung báo cáo; Tài liệu tham khảo; Phụ lục".
- Trong file mẫu thực tế có **hai** trang phản biện: "NHẬN XÉT CỦA GIÁO VIÊN PHẢN BIỆN 1" (Mẫu ¶54) và "NHẬN XÉT CỦA GIÁO
  VIÊN PHẢN BIỆN 2" (Mẫu ¶57), cùng trang GVHD (Mẫu ¶51). Mẫu còn có trang "NHẬT KÍ LÀM VIỆC" sau Phụ lục (Mẫu ¶365–389),
  dù danh sách ¶151–165 không liệt kê trang này.
- Cả bộ trong một tệp: "Toàn bộ báo cáo khóa luận tốt nghiệp (trang bìa, trang giới thiệu… phụ lục) phải được thực hiện
  trên cùng một file word." (Mẫu ¶215).

**Abstract / Tóm tắt** — Mẫu ¶29: "Trang tóm tắt (Abstract) đề tài bằng tiếng Anh, trình bày trong một trang A4, gồm Tên đề
tài, tóm tắt ngắn gọn nội dung và từ khóa." Mẫu ¶30–35: "có thể gồm các phần như: Bối cảnh, thực trạng, lý do chọn đề tài,
Nêu vấn đề cần giải quyết, Giải pháp và phương pháp thực hiện, Các kết quả thực hiện, Đánh giá kết luận và hướng phát triển."
Mẫu ¶36: "Phía cuối của trang tóm tắt là từ khóa (keywords)". Mẫu ¶39–46 lặp lại y hệt cho TÓM TẮT tiếng Việt ("trình bày
trong một trang A4").

**(b) Dàn ý chương mẫu** — Mẫu ¶167: "Nội dung của báo cáo tùy theo mỗi đề tài, có thể gồm các phần như sau:" rồi ¶168–209:
"Chương 1. GIỚI THIỆU · Chương 2. CƠ SỞ LÝ THUYẾT · Chương 3. PHÂN TÍCH YÊU CẦU · Chương 4. THIẾT KẾ HỆ THỐNG · Chương 5.
GIẢI PHÁP CÔNG NGHỆ (NẾU CÓ) · Chương 6. HIỆN THỰC VÀ TRIỂN KHAI · Chương 7. ĐÁNH GIÁ VÀ THẢO LUẬN · Chương 8. KẾT LUẬN ·
TÀI LIỆU THAM KHẢO · PHỤ LỤC". Mỗi chương có mục mẫu "x.1 / x.1.1 / x.1.2 / x.2" và số trang giữ chỗ (1, 12, 21, 35, 51,
61, 71, 81).

**(c) Nội dung từng chương (chương "BỐ CỤC" của mẫu)** — Mẫu ¶290: "Bố cục được xây dựng từ đề cương của đề tài … Chương này
sẽ đưa ra một vài thành phần chính của luận văn để tham khảo. Sinh viên tùy theo đề tài mà đặt tên chương mục phù hợp."
- Giới thiệu (Mẫu ¶292): "Chương đầu tiên của Khóa luận giới thiệu về toàn bộ đề tài, gồm đặt vấn đề, thuận lợi và khó khăn,
  ưu nhược điểm của các phương pháp hoặc giải pháp hiện tại, nội dung chính của đề tài, phương pháp, giải pháp của đề tài,
  kết quả thực hiện và sơ lược kết luận, hướng phát triển."
- Nền tảng/Cơ sở lý thuyết (Mẫu ¶294): "Là chương tóm tắt các vấn đề lý thuyết cơ sở liên quan đến đề tài cũng như thảo luận,
  đánh giá về các đề tài gần đây."
- Phân tích yêu cầu (Mẫu ¶296): "Là chương phân tích các yêu cầu của đề tài, mô hình hóa yêu cầu."
- Thiết kế hệ thống (Mẫu ¶298): "Là chương thiết kế hệ thống, mô hình hóa kiến trúc và các thiết kế hệ thống."
- Giải pháp công nghệ (nếu có) (Mẫu ¶300): "Nếu đề tài có cải tiến hoặc đề xuất giải pháp công nghệ thì mô tả rõ giải pháp."
- Hiện thực và Triển khai (Mẫu ¶302): "Trình bày cụ thể việc hiện thực và triển khai các giải pháp."
- Đánh giá và thảo luận (Mẫu ¶304–305): "Kiểm thử hệ thống và phân tích những đóng góp, những mặt mạnh yếu của hệ thống." và
  "Đo lường, so sánh, phân tích, đánh giá về một hoặc một vài giải pháp công nghệ (nếu có)".
- Kết luận (Mẫu ¶307): "Đưa ra kết luận, những điều làm được, chưa làm được, phân tích tổng quan về đề tài, ưu nhược điểm,
  hạn chế và hướng phát triển của đề tài."

**Quy tắc về đề mục** — Mẫu ¶219: "Các tiểu mục của báo cáo được trình bày và đánh số thành nhóm số, nhiều nhất gồm bốn chữ số
với số thứ nhất là chỉ số chương. Tại mỗi mục, tiểu mục phải có ít nhất là 2 tiểu mục." Mẫu ¶223: "Mục lục chỉ đưa đến nhóm
tiểu mục thứ 3 (tức là đến 3 chữ số)."

**Phụ lục** — Mẫu ¶222: "Phần này bao gồm những nội dung cần thiết nhằm minh họa hoặc bổ trợ cho nội dung báo cáo, như: chương
trình tính, kết quả khảo sát trên mô hình số, các số liệu, mẫu biểu, tranh ảnh... Phụ lục không được đánh số trang, không được
dày hơn phần chính của báo cáo." Mẫu ¶364: "Phần phụ lục bao gồm những bổ sung hỗ trợ cho nội dung báo cáo khóa luận như: số
liệu, biểu mẫu, mã chương trình, hình ảnh, tài liệu minh chứng, kết quả kiểm tra đạo v… nhằm làm rõ các nghiên cứu đã trình
bày trong phần nội dung. Các tính toán đã trình bày tóm tắt trong phần nội dung phải được trình bày chi tiết trong phần phụ lục
này." (chữ "đạo v…" bị cắt ngay trong file mẫu).

**Nhật kí làm việc** — Mẫu ¶366–389: tiêu đề "Đề tài", "Giảng viên hướng dẫn", "Ngày bắt đầu"; bảng cột "Tuần · Từ ngày · Đến
ngày · Ngày báo cáo GVHD · Tóm tắt công việc đã thực hiện · Nhận xét của GVHD", hàng tuần 1–15.

**Những thứ chỉ xuất hiện ở phần poster, không phải cuốn báo cáo** — Mẫu ¶312–319 liệt kê cho poster: "Đặt vấn đề/lý do chọn đề
tài; Mục tiêu đề tài; Kế hoạch thực hiện; Phương pháp nghiên cứu, giải quyết vấn đề đặt ra; Kết quả (lý thuyết và thực nghiệm)
và thảo luận; Kết luận, kiến nghị, đề xuất (nếu có); Tài liệu tham khảo chính." Mẫu ¶254 (trình tự thực hiện) nhắc "phân công
nhiệm vụ trong nhóm" như một phần của kế hoạch.

**Không có trong mẫu** — tìm các cụm "đối tượng", "phạm vi", "ý nghĩa", "tóm tắt chương", "tiểu kết", "kết luận chương",
"giới thiệu chương", "phương pháp nghiên cứu" trong toàn bộ văn bản mẫu: chỉ thấy "Phương pháp nghiên cứu" và "Mục tiêu đề
tài" ở phần poster (Mẫu ¶314, ¶316); các cụm còn lại không có.

### Inferences
- Vì mẫu ghi rõ dàn ý là "có thể gồm" và "để tham khảo", đổi tên chương (ví dụ thêm chương "Dữ liệu", gọi chương 4 là
  "Phương pháp") **không** vi phạm mẫu. Cái cần kiểm là **nội dung** mà mẫu mô tả cho từng chương có mặt trong báo cáo hay không.
- Dàn ý mẫu là dàn ý của đề tài kiểu phần mềm (phân tích yêu cầu → thiết kế → hiện thực). Một đề tài khoa học dữ liệu có
  thực nghiệm mô hình nên ánh xạ "Giải pháp công nghệ" sang "Phương pháp", "Đánh giá và thảo luận" sang "Kết quả và thảo luận".
  Hội đồng có thể vẫn hỏi về "phân tích yêu cầu" và "thiết kế hệ thống" vì đây là hai chương có tên riêng trong mẫu.

### Gaps
- Mẫu không nêu số trang tối thiểu hoặc tối đa. Giới hạn 150 trang mà người dùng nêu không có trong file mẫu (tìm "trang"
  trong toàn bộ văn bản mẫu chỉ ra các quy tắc đánh số trang, không ra hạn mức). Không xác minh được nguồn của con số 150.
- Mẫu không nói rõ hai trang phản biện (PB1, PB2) là bắt buộc hay chỉ minh hoạ: danh sách ¶158 dùng số ít, file mẫu có hai trang.

---

## 3. Bảng ánh xạ: yếu tố mẫu yêu cầu → vị trí trong báo cáo → trạng thái

### Takeaway
Đủ các thành phần lớn và gần như đủ nội dung chương. Có 5 điểm lệch rõ so với chữ của mẫu: Abstract và Tóm tắt mỗi bản dài
2 trang (mẫu: một trang A4); chỉ có 1 trang nhận xét phản biện (mẫu có 2); mục 6.6 chỉ có một tiểu mục 6.6.1 (mẫu: ít nhất 2);
"Phân tích yêu cầu" không có chương riêng và nằm sau phần phương pháp (5.1), không có mô hình hóa yêu cầu bằng sơ đồ; Chương 1
không nhắc hướng phát triển và không có đoạn mở chương.

### Cited Findings

**A. Thành phần của cuốn báo cáo (Mẫu ¶151–165, ¶29–59, ¶365)**

| Yếu tố mẫu | Báo cáo | Trạng thái | Bằng chứng |
|---|---|---|---|
| Bìa tiếng Việt | PDF p.1 (+ bìa phụ p.2) | đủ | Mẫu có bìa chính + bìa phụ (¶1–18) |
| Bìa tiếng Anh | PDF p.3 | đủ | |
| Abstract tiếng Anh + Keywords, "trình bày trong một trang A4" (¶29) | PDF p.4–5 | **quá dài**: chữ tràn sang p.5, Keywords ở p.5 | 00_phan_dau.md:1–11; PDF p.5 bắt đầu bằng "SED predicts; on the high-coverage store…" |
| Abstract có các phần Bối cảnh…, "Đánh giá kết luận và hướng phát triển" (¶35) | Có bối cảnh, vấn đề, giải pháp, kết quả, nhận định về đóng góp | **thiếu một phần**: không có câu nào về hướng phát triển | PDF p.4–5 |
| Tóm tắt tiếng Việt + Từ khóa, "một trang A4" (¶39) | PDF p.6–7 | **quá dài**: tràn sang p.7, Từ khóa ở p.7; cũng không nhắc hướng phát triển | 00_phan_dau.md:15–25 |
| Lời cảm ơn | PDF p.8 | đủ | 00_phan_dau.md:29 |
| Nhận xét GVHD | PDF p.9 | đủ | 00_phan_dau.md:41 |
| Nhận xét GV phản biện (mẫu: PB1 ¶54 và PB2 ¶57) | PDF p.10, một trang, tiêu đề không đánh số | **lệch**: thiếu trang PB2, tiêu đề không có "1" | 00_phan_dau.md:47 |
| Mục lục (đến cấp 3, ¶223) | PDF p.11–12 | đủ (có mục cấp 3 6.3.x, 6.5.x, 6.6.1) | |
| Danh mục hình ảnh | PDF p.13 | đủ | |
| Danh mục bảng biểu | PDF p.14–15 | đủ | |
| Danh mục từ viết tắt (bắt buộc khi > 10 từ, ¶221) | PDF p.16, 27 mục | đủ | 00_phan_dau.md:71 |
| Nội dung báo cáo | Chương 1–7, tr. 1–84 | đủ | |
| Tài liệu tham khảo | tr. a–d | đủ (thể thức TLTK nằm ngoài phạm vi ghi chú này) | 90_phan_cuoi.md:3 |
| Phụ lục ("không được dày hơn phần chính", ¶222) | tr. e–j, 6 trang so với 84 trang nội dung | đủ | 90_phan_cuoi.md:9–77 |
| Phụ lục "không được đánh số trang" (¶222) | Phụ lục mang số chữ e–j trong Mục lục | **lệch nhẹ so với chữ**, nhưng **khớp với cách chính file mẫu làm** (Mục lục mẫu ghi "PHỤ LỤCc", "NHẬT KÍ LÀM VIỆCd", Mẫu ¶108–109) | PDF p.12 |
| Nhật kí làm việc (¶365–389, 15 tuần) | tr. k, 10 tuần | **thiếu nội dung**: tuần 5, 6, 7, 9 để trống; cột "Ngày báo cáo GVHD" chỉ điền tuần 1–2; cột "Nhận xét của GVHD" trống (đúng, vì không được tự viết) | 90_phan_cuoi.md:89–102 |

**B. Nội dung chương (Mẫu ¶292–307)**

| Yêu cầu của mẫu | Vị trí trong báo cáo | Trạng thái |
|---|---|---|
| **Giới thiệu**: đặt vấn đề | 1.1 (tr. 1), 1.2 (tr. 2, có hai công thức hình thức hóa bài toán) | đủ |
| …thuận lợi và khó khăn | 1.1 đoạn 2 nêu ba khó khăn (01_gioi_thieu.md:7); đoạn 3 nêu điểm thuận lợi là hai bộ dữ liệu cùng miền và nguy cơ trùng (:9) | **lệch tên / gộp**: có nội dung, không có mục riêng, "thuận lợi" chỉ một câu |
| …ưu nhược điểm của các phương pháp hoặc giải pháp hiện tại | 1.1 câu đầu nêu hạn chế của đo mức ồn trung bình (:5); so sánh với công trình liên quan nằm ở 2.7 "Vị trí của đề tài" (02_co_so_ly_thuyet.md:75) | **mỏng ở Chương 1**, phần chính dời sang Chương 2 |
| …nội dung chính của đề tài | 1.4: bảy việc (01_gioi_thieu.md:55) | đủ |
| …phương pháp, giải pháp của đề tài | 1.1 đoạn 4 (hệ thống bốn bước, :11); cột "Cách trả lời" của Bảng 1.2 (:61–65); đoạn cuối 1.4 (:69) | đủ về nội dung; **không có mục tên "Phương pháp nghiên cứu"** (mẫu không bắt buộc tên này) |
| …kết quả thực hiện và sơ lược kết luận | Số kết quả ở 1.3 (:51, event-F1 19 lớp) và cột "Bằng chứng đã có" của Bảng 1.3 (:83–90) | đủ về nội dung; **không có mục "Kết quả đạt được" ở Chương 1**, kết quả nằm rải trong bảng đóng góp |
| …hướng phát triển | Không có ở Chương 1; 1.7 chỉ nói "Chương 7 nêu kết luận, hạn chế và hướng phát triển" (:96) | **thiếu** |
| (thông lệ, không có trong mẫu) Đối tượng và phạm vi | 1.5 "Phạm vi và giới hạn" (:71) | có phạm vi; **không có "đối tượng nghiên cứu"** — mẫu không yêu cầu |
| (thông lệ, không có trong mẫu) Ý nghĩa khoa học và thực tiễn | Thực tiễn: 1.3 "Bối cảnh ứng dụng tại Việt Nam" (:31–51); khoa học: 1.6 "Đóng góp dự kiến" (:77–92) | có nội dung, **không có mục cùng tên** — mẫu không yêu cầu |
| (thông lệ, không có trong mẫu) Bố cục khóa luận | 1.7 "Bố cục báo cáo" (:94–96), 68 từ, 1 đoạn | đủ, nhưng ngắn |
| **Cơ sở lý thuyết**: lý thuyết cơ sở | 2.1–2.6 | đủ |
| …thảo luận, đánh giá về các đề tài gần đây | 2.7 "Vị trí của đề tài" (02_co_so_ly_thuyet.md:75–80), có Weck & Serra, Wijngaard, LA-RAG | đủ |
| **Phân tích yêu cầu**: phân tích yêu cầu, mô hình hóa yêu cầu | 5.1 "Tình huống sử dụng và yêu cầu" (05_trien_khai.md:5–27), Bảng 5.1 "Yêu cầu, tính năng đáp ứng và bằng chứng" | **sai thứ tự và gộp**: mẫu đặt trước thiết kế, báo cáo đặt ở Chương 5, sau Chương 4 Phương pháp; **thiếu mô hình hóa** (không có sơ đồ use case hay sơ đồ luồng; chỉ có bảng) |
| **Thiết kế hệ thống**: mô hình hóa kiến trúc và các thiết kế hệ thống | 4.1 "Kiến trúc tổng thể" + Hình 4.1 (04_phuong_phap.md:5–13); 5.2 tổ chức mã nguồn; 5.4 "Các dịch vụ" (05_trien_khai.md:62–70) mô tả 7 bảng CSDL, API, giao diện bằng lời; Bảng 5.3 các thành phần | **gộp và mỏng**: không có chương riêng; không có sơ đồ CSDL, sơ đồ tuần tự hay bảng endpoint API (grep "lược đồ/ERD/sequence/endpoint" trong Chương 4–5 không ra sơ đồ nào) |
| **Giải pháp công nghệ (nếu có)**: mô tả rõ giải pháp cải tiến/đề xuất | Chương 4 "Phương pháp" (4.2–4.6), đặc biệt 4.3 SED và LBR (04_phuong_phap.md:40–81) | đủ, **lệch tên** (hợp lệ theo ¶290) |
| **Hiện thực và Triển khai** | Chương 5 "Triển khai hệ thống" (5.2–5.7) | đủ |
| **Đánh giá và thảo luận**: kiểm thử hệ thống | 5.7 "Tái lập và kiểm thử" (05_trien_khai.md:108–129); 6.7 độ khớp khi phục vụ | đủ, nhưng **tách đôi**: kiểm thử phần mềm ở Chương 5, không ở chương đánh giá |
| …phân tích đóng góp, mặt mạnh yếu | 6.9 "Thảo luận và hạn chế" (06_ket_qua.md:330–344) — đoạn "Tóm lại…" rồi danh sách hạn chế | **lệch**: mặt yếu (hạn chế) được liệt kê kỹ; mặt mạnh chỉ có ở đoạn tóm tắt đầu 6.9, không có mục/đoạn riêng |
| …đo lường, so sánh, phân tích | 6.1–6.8 | đủ (rất đầy đủ) |
| **Kết luận**: những điều làm được | 7.1 "Kết quả đạt được" | đủ |
| …chưa làm được | 7.4 "Hạn chế" (07_ket_luan.md:27–29, 1 đoạn, dẫn ngược về 6.9) và 7.5 | **mỏng**: không có câu "chưa làm được" đối chiếu với bảy việc ở 1.4 |
| …phân tích tổng quan, ưu nhược điểm | 7.3 "Mức khẳng định cho các đóng góp" (1 đoạn) | **lệch**: nói về mức khẳng định tính mới, không có ưu điểm/nhược điểm của hệ thống |
| …hạn chế và hướng phát triển | 7.4, 7.5 | đủ |

**C. Quy tắc đề mục (Mẫu ¶219, ¶223)**

| Quy tắc | Báo cáo | Trạng thái |
|---|---|---|
| Tối đa 4 cấp số | Sâu nhất 3 cấp (6.3.1…6.6.1) | đủ |
| Mục lục đến 3 chữ số | Có 6.3.x, 6.5.x, 6.6.1 trong Mục lục | đủ |
| "Tại mỗi mục, tiểu mục phải có ít nhất là 2 tiểu mục" | 6.3 có 6 tiểu mục; 6.5 có 2; **6.6 chỉ có 6.6.1** (06_ket_qua.md:245, :283) | **vi phạm ở 6.6** |

### Inferences
- Ba lệch có thể sửa mà không động vào nội dung khoa học: (1) rút Abstract/Tóm tắt về một trang, thêm một câu hướng phát triển;
  (2) thêm trang "NHẬN XÉT CỦA GIÁO VIÊN PHẢN BIỆN 2" và đánh số "1" cho trang hiện có; (3) với 6.6, hoặc tách phần trước 6.6.1
  thành một tiểu mục (ví dụ "6.6.1 Ba chế độ truy hồi", "6.6.2 Chế độ backfill"), hoặc hạ 6.6.1 thành đoạn có tiêu đề in đậm.
- Lệch về "Phân tích yêu cầu" và "Thiết kế hệ thống" là lệch thật nhưng hợp lý cho đề tài thực nghiệm. Nếu muốn khớp mẫu hơn
  mà không thêm chương: đưa 5.1 lên đầu Chương 4 hoặc cuối Chương 1, và thêm một sơ đồ (luồng xử lý một yêu cầu, hoặc lược đồ
  7 bảng CSDL) vào 5.4.
- Chương 1 có gần đủ ý mẫu yêu cầu, chỉ thiếu "hướng phát triển" và "kết quả thực hiện" dạng tóm tắt riêng. Một đoạn 3–4 câu ở
  1.7 (hoặc một mục "Kết quả đạt được và hướng phát triển" ngắn) sẽ phủ cả hai.

### Gaps
- Không xác định được hội đồng IUH chấm theo dàn ý 8 chương của mẫu chặt đến mức nào; mẫu tự nói là tham khảo (¶290).

---

## 4. Đoạn mở chương, tóm tắt cuối chương, liên kết sang chương sau

### Takeaway
Mẫu không yêu cầu đoạn giới thiệu chương hay tiểu kết. Trong báo cáo, Chương 2–7 có đoạn mở chương; **Chương 1 không có**.
**Không chương nào có đoạn tóm tắt cuối chương**, và chỉ vài chương có câu chuyển sang chương sau.

### Cited Findings
- Chương 1: tiêu đề `# GIỚI THIỆU` (01_gioi_thieu.md:1) theo ngay sau là `## Vì sao chọn đề tài` (:3), không có đoạn mở.
- Chương 2: đoạn mở 46 từ (02_co_so_ly_thuyet.md:3: "Chương này tóm tắt những kiến thức nền mà đề tài dùng…"). Đoạn cuối 2.7
  (:80) kết bằng "Phạm vi tra cứu … không phải tổng quan hệ thống đầy đủ", không chuyển sang Chương 3.
- Chương 3: đoạn mở 73 từ (03_du_lieu.md:3). Câu cuối chương (:80) chuyển sang "phần hạn chế của Chương 6", không sang Chương 4.
- Chương 4: đoạn mở 72 từ (04_phuong_phap.md:3). Kết chương bằng quy tắc diễn giải khoảng tin cậy (4.7, :167), không tóm tắt.
- Chương 5: đoạn mở 50 từ (05_trien_khai.md:3). Kết chương bằng một đoạn về lỗi ghép cửa sổ dự đoán (:129).
- Chương 6: đoạn mở 182 từ + 4 quy ước đọc số (06_ket_qua.md:3–8). Mục 6.9 bắt đầu bằng "Tóm lại, nhóm có một hệ thống đầu–cuối
  chạy được…" (:332) — đây là đoạn tổng kết duy nhất có tính chất tóm tắt chương, nằm trước danh sách hạn chế; chương kết thúc
  bằng một gạch đầu dòng hạn chế ("Tra cứu văn liệu ở mức khóa luận…", :344).
- Chương 7: đoạn mở 53 từ (07_ket_luan.md:3), có dẫn về Chương 1 và Chương 6.
- 1.7 "Bố cục báo cáo" mô tả nội dung Chương 2–7 khớp với tên chương thực tế (01_gioi_thieu.md:96), nhưng không nhắc Tài liệu
  tham khảo, Phụ lục và Nhật kí.
- Mục 6.3 không có câu dẫn nào trước 6.3.1 (06_ket_qua.md:58–60; 0 từ). Ngược lại, 6.5 có 1.113 từ và 6.6 có 1.025 từ trước
  tiểu mục đầu tiên.

### Inferences
- Thêm một đoạn mở cho Chương 1 (2–3 câu) giúp đồng bộ với sáu chương còn lại.
- Tiểu kết cuối chương không bắt buộc theo mẫu. Nếu thêm, nên làm ngắn (2–3 câu) cho Chương 3, 4, 5, vì ba chương này kết bằng
  chi tiết kỹ thuật, người đọc dễ mất mạch sang chương sau.
- Thêm một câu dẫn dưới tiêu đề 6.3 sẽ báo trước cho người đọc 6 tiểu mục kéo dài 10 trang.

### Gaps
- Không có tiêu chí khách quan trong mẫu để đánh giá "liên kết sang chương sau"; nhận định trên là đọc trực tiếp câu đầu/cuối.

---

## 5. Độ sâu đề mục, mục quá ngắn, mục quá dài, trùng tên

### Takeaway
Độ sâu nằm trong giới hạn (≤ 3 cấp). Có ba loại mất cân đối: các mục một đoạn ở Chương 1 và 7; các khối rất dài ở 4.3, 6.3.5,
6.5, 6.6; hai cặp mục trùng hoặc gần trùng tên giữa Chương 2 và Chương 4.

### Cited Findings
- **Mục rất ngắn (≤ 1 đoạn prose):** 1.6 Đóng góp dự kiến (101 từ, 1 đoạn + Bảng 1.3; 01_gioi_thieu.md:77); 1.7 Bố cục báo cáo
  (68 từ; :94); 7.3 Mức khẳng định cho các đóng góp (205 từ, 1 đoạn; 07_ket_luan.md:23); 7.4 Hạn chế (88 từ, 1 đoạn; :27).
  Ngắn tương đối: 5.3 Khối lượng thực hiện (97 từ + 2 bảng; 05_trien_khai.md:37), 4.1 Kiến trúc tổng thể (161 từ; 04_phuong_phap.md:5),
  6.3.4 Giai đoạn O và hệ B0 (207 từ; 06_ket_qua.md:96) — đây là mục giới thiệu hệ cơ sở B0 của hệ thống cuối.
- **Mục rất dài:** 4.3 Mô hình SED (1.218 từ, 15 đoạn, 3 hình, tr. 25–28; 04_phuong_phap.md:40); 6.3.5 LBR và hệ thống cuối (898 từ,
  3 bảng, 3 hình, tr. 56–60; 06_ket_qua.md:102); 6.5 RQ2 (1.113 từ trước tiểu mục, cả mục tr. 64–68; :188); 6.6 RQ3 (1.025 từ trước
  6.6.1, cả mục tr. 69–74; :245); 3.3 Quy trình chuẩn bị dữ liệu (800 từ; 03_du_lieu.md:44); 4.5 (806 từ), 4.7 (777 từ), 5.7 (798 từ).
- **Trùng/gần trùng tên:** "2.2 Cách đánh giá" (02_co_so_ly_thuyet.md:13) và "4.7 Cách đánh giá" (04_phuong_phap.md:143); "2.3 Từ xác
  suất thành sự kiện" (02_co_so_ly_thuyet.md:41) và "4.4 Ghép xác suất thành sự kiện" (04_phuong_phap.md:83).
- **Hạn chế viết hai lần:** danh sách đầy đủ ở 6.9 (06_ket_qua.md:334–344), bản rút gọn ở 7.4 dẫn ngược về 6.9 (07_ket_luan.md:29).
- Chương 2 không có bảng hay hình nào (danh mục hình/bảng PDF p.13–15 không có mục "2.x").

### Inferences
- Đổi tên để tách vai trò: ví dụ 2.2 "Chỉ số đánh giá SED" (lý thuyết) và 4.7 "Giao thức đánh giá" (cách dự án áp dụng); 2.3 "Hậu xử lý
  frame thành sự kiện" và 4.4 "Hậu xử lý của hệ thống".
- 4.3 và 6.3.5 là chỗ hợp lý nhất để tách thêm tiểu mục cấp 3 (mỗi chỗ ≥ 2 tiểu mục theo ¶219), vừa giúp Mục lục, vừa chia khối dài.
- 7.3 và 7.4 có thể gộp thành một mục, hoặc 7.4 viết rõ "chưa làm được" đối chiếu bảy việc ở 1.4, để khớp chữ "những điều làm được,
  chưa làm được" của mẫu (¶307).
- Một sơ đồ cho Chương 2 (ví dụ minh hoạ event-F1 với collar, hoặc sơ đồ RAG) sẽ làm chương lý thuyết bớt khô; không bắt buộc.

### Gaps
- "Quá ngắn/quá dài" là nhận định tương đối trong báo cáo này; mẫu không đặt độ dài mục.

---

## 6. Phụ lục

### Takeaway
Bốn phụ lục A–D (6 trang) đều thuộc loại mẫu nêu ("số liệu", "tài liệu minh chứng"); mẫu không bắt buộc phụ lục cụ thể nào. Chưa có
phụ lục "mã chương trình" hay "kết quả kiểm tra đạo văn" mà mẫu liệt kê như ví dụ.

### Cited Findings
- A. Hệ lớp và số sự kiện đa âm (Bảng PL.1) — 90_phan_cuoi.md:13–21; PDF p.105.
- B. Artifact đã đóng băng (bảng freeze SHA-256, sổ ghi các lần chạm test) — :23–37; PDF p.106.
- C. Kết quả theo lớp (phân loại DataSEC; event-F1 theo lớp của B0/LBR V2 và f2) — :39–55; PDF p.107–109.
- D. Phân công công việc (9 mảng, người phụ trách chính và kiểm chéo) và đoạn "Công cụ hỗ trợ" về việc dùng mô hình ngôn ngữ lớn —
  :57–77; PDF p.110. Mẫu nhắc "phân công nhiệm vụ trong nhóm" ở phần kế hoạch (Mẫu ¶254).
- Ví dụ phụ lục trong mẫu: "chương trình tính, kết quả khảo sát trên mô hình số, các số liệu, mẫu biểu, tranh ảnh" (¶222); "số liệu,
  biểu mẫu, mã chương trình, hình ảnh, tài liệu minh chứng, kết quả kiểm tra đạo v…" (¶364). Mẫu yêu cầu "Các tính toán đã trình
  bày tóm tắt trong phần nội dung phải được trình bày chi tiết trong phần phụ lục này" (¶364).
- Tiêu đề phụ lục dùng `HEADING2N` (không đánh số chương) — 90_phan_cuoi.md:13, :23, :39, :57.

### Inferences
- Theo ¶364, các phép tính chỉ được tóm tắt trong thân bài nên có chi tiết ở phụ lục. Ứng viên: bảng lưới siêu tham số / cấu hình
  huấn luyện B0 và LBR, danh sách 100 truy vấn RAG (hoặc trích mẫu), ví dụ mô tả đầy đủ theo bốn cách sinh, danh sách endpoint API
  hay lược đồ CSDL (cũng bù cho phần "Thiết kế hệ thống"). Một phụ lục "mã nguồn/tái lập" (đường dẫn kho, lệnh chạy) cũng khớp ví dụ
  "mã chương trình".
- Nếu khoa yêu cầu nộp kết quả kiểm tra đạo văn, phụ lục là nơi mẫu gợi ý đặt nó (¶364).

### Gaps
- Không rõ khoa có bắt buộc nộp kết quả kiểm tra đạo văn trong cuốn báo cáo hay không; mẫu chỉ nêu như một ví dụ (và chữ bị cắt).

---

## 7. Ngân sách trang: 112 trang so với giới hạn 150

### Takeaway
Còn dư 38 trang so với giới hạn 150 (giới hạn này không có trong file mẫu). Phần lớn khối lượng nằm ở Chương 6 (33 trang) và Chương
4–5 (25 trang). Chương 1, 2 và 7 cộng lại 18 trang. Mẫu không đặt tỷ lệ; số trang giữ chỗ trong dàn ý mẫu chỉ gợi ý mỗi chương
khoảng 9–14 trang.

### Cited Findings
- Tổng 112 trang PDF (pdfinfo). Phần đầu 16 · nội dung 84 · TLTK 4 · phụ lục 6 · nhật kí 2 (mục 1 ở trên).
- Dàn ý mẫu ghi số trang giữ chỗ ở mục x.1 của từng chương: 1, 12, 21, 35, 51, 61, 71, 81 (Mẫu ¶169–204). Khoảng cách giữa các mốc là
  11, 9, 14, 16, 10, 10, 10 trang. Đây là số minh hoạ trong dàn ý "có thể gồm", không phải quy định.
- Chương 6 = 33/84 = 39% phần nội dung; Chương 1 + 2 = 14/84 = 17%; Chương 7 = 4/84 = 5%.
- Phụ lục 6 trang, nhỏ hơn nhiều so với phần chính 84 trang (điều kiện ¶222 thỏa).

### Inferences
- So với mốc minh hoạ của mẫu, Chương 6 dài gấp khoảng 3 lần một chương mẫu, Chương 7 ngắn hơn một nửa. Đây không phải vi phạm, nhưng
  là điểm hội đồng dễ nhận thấy khi lật Mục lục.
- Có chỗ để thêm (trong 38 trang dư) mà không cần cắt: sơ đồ yêu cầu và thiết kế (1–3 trang), đoạn mở/tiểu kết chương (≈ 1–2 trang),
  phụ lục cấu hình và truy vấn (3–6 trang). Ngược lại, việc rút Abstract và Tóm tắt về mỗi bản 1 trang sẽ bớt 2 trang ở phần đầu.

### Gaps
- Không tìm thấy nguồn chính thức cho giới hạn 150 trang trong file mẫu; nếu khoa có văn bản riêng quy định số trang thì cần đối chiếu
  văn bản đó.
