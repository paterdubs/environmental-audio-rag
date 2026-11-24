# Rà soát nội dung báo cáo theo góc nhìn GVHD và hội đồng (24/11/2026)

Phạm vi: chỉ xét **nội dung** của `report/Khoa_luan_environmental_audio_rag.pdf` (112 trang theo bộ đếm của Word, 113 trang vật lý khi trích bằng pdftotext), dựng từ `report/final_src/*.md`. Định dạng theo mẫu khoa thuộc phần việc của người khác. Mọi vị trí ghi theo `tệp:dòng` của nguồn Markdown, hoặc theo trang vật lý của PDF (trích bằng `pdftotext -enc UTF-8 -layout`, lưu ở scratchpad). Mọi đề xuất đều theo các ràng buộc: không train lại, không mở test thêm, không viết "lần đầu".

Phân bổ trang (trang vật lý, đo từ PDF): Abstract tr. 4–5; Tóm tắt tr. 6–7; Ch.1 tr. 17–23 (7 tr); Ch.2 tr. 24–30 (7); Ch.3 tr. 31–38 (8); Ch.4 tr. 39–51 (13); Ch.5 tr. 52–63 (12); **Ch.6 tr. 64–96 (33 tr, khoảng 39% thân bài)**; Ch.7 tr. 97–100 (4); TLTK tr. 101–104 (28 nguồn); Phụ lục tr. 105–110; Nhật ký tr. 111–112.

## Bộ T0 ★ của bản rà soát 23/11: việc nào đã làm, việc nào còn mở

### Takeaway
Gần như toàn bộ phần nội dung của T0 ★ đã vào báo cáo: RQ3 trả lời thẳng, có C5/C6, có bảng định cỡ, có RQ2 trung thực, có Việt Nam/QCVN, có tình huống sử dụng, có khối lượng, độ trễ, phân công, trang GVPB và mục tái sử dụng test. Còn mở: field test (T0-10a), nhật ký tuần 5–7 và 9, ngày báo cáo GVHD, sơ đồ triển khai dạng hình (T0-11 mới có bảng), số ADR đã lỗi thời, và vòng dựng/đọc chéo cuối (T0-13).

### Cited Findings
- T0-02: đã có trang "Nhận xét của giáo viên phản biện" ([00_phan_dau.md L47–49](../../report/final_src/00_phan_dau.md)). LBR, LLM, OOF và cSEBB đã có trong danh mục viết tắt (L83, L89, L90, L94). **Còn mở:** nhật ký tuần 5, 6, 7, 9 vẫn để trống, cột "Ngày báo cáo GVHD" trống từ tuần 3 ([90_phan_cuoi.md L93–102](../../report/final_src/90_phan_cuoi.md)).
- T0-03: Phụ lục D có bảng phân công 9 mảng và đoạn khai báo dùng công cụ AI ([90_phan_cuoi.md L57–77](../../report/final_src/90_phan_cuoi.md)).
- T0-04: RQ3 đã trả lời thẳng là hybrid thua vector_only trên ba kho, kèm hiệu ghép cặp, bảng theo nhóm câu hỏi và cơ chế độ phủ ([06_ket_qua.md L257–281](../../report/final_src/06_ket_qua.md); [07_ket_luan.md L21](../../report/final_src/07_ket_luan.md)). Abstract cũng đã sửa theo ([00_phan_dau.md L9, L23](../../report/final_src/00_phan_dau.md)).
- T0-05: mục "Tái sử dụng tập test" đã có, kèm ρ = 0,62, cận trên của RQ1 và ba chỗ tái sử dụng thích nghi ([06_ket_qua.md L315–322](../../report/final_src/06_ket_qua.md)). Câu "mỗi cấu hình chỉ mở test một lần" đã thay cho câu cũ "tập test… một lần" ([04_phuong_phap.md L145](../../report/final_src/04_phuong_phap.md)). Câu về λ đã sửa thành "macro-F1 dev giảm 0,0145" ([04_phuong_phap.md L38](../../report/final_src/04_phuong_phap.md)).
- T0-06: C5 (LBR) và C6 (giao thức) đã có trong bảng đóng góp ([01_gioi_thieu.md L89–90](../../report/final_src/01_gioi_thieu.md)). Đã có bảng "LBR trong bối cảnh" với các mốc 0,2335 / 0,2469 / 0,4641 ([06_ket_qua.md L106–112](../../report/final_src/06_ket_qua.md)). Đã định vị so với RED/EPN ([02_co_so_ly_thuyet.md L47](../../report/final_src/02_co_so_ly_thuyet.md)).
- T0-07: có bảng định cỡ theo đồng thuận người và theo DCASE ([06_ket_qua.md L160–186](../../report/final_src/06_ket_qua.md)).
- T0-08: RQ2 đã ghi rõ "0 vi phạm là theo cấu tạo", constrained gần template (BLEU-4 0,358), κ ≈ −0,03, đồng thời chấm thêm so với nhãn gốc ([06_ket_qua.md L214–231](../../report/final_src/06_ket_qua.md)).
- T0-09: có mục "Bối cảnh ứng dụng tại Việt Nam" neo vào QCVN 26:2025 ([01_gioi_thieu.md L31–51](../../report/final_src/01_gioi_thieu.md)); có persona, ba tác vụ và bảng yêu cầu F1–F5/N1–N4 ([05_trien_khai.md L5–29](../../report/final_src/05_trien_khai.md)).
- T0-10: bảng độ trễ có 10 lần đo ([05_trien_khai.md L84–96](../../report/final_src/05_trien_khai.md)). **Field test bằng clip điện thoại chưa có** (CLAUDE.md §3 ghi "chờ clip điện thoại của người dùng").
- T0-11: có bảng khối lượng và bảng thành phần Compose ([05_trien_khai.md L37–60](../../report/final_src/05_trien_khai.md)). Chưa có sơ đồ triển khai riêng; Hình kiến trúc ở Ch.4 thực chất đang làm vai trò này (xem câu hỏi 3).
- T0-14/15/16: đã có hình hành trình (r04), hình phân loại FN (r05), lệch onset (r06) và bảng lịch sử phân loại so với FA2025 ([06_ket_qua.md L18–34](../../report/final_src/06_ket_qua.md)).
- **Số liệu lỗi thời phát sinh sau 23/11:** bảng khối lượng ghi "48 ADR" và chân bảng ghi git `6422322` ([report/final_tables/f12_workload.md](../../report/final_tables/f12_workload.md)); Phụ lục D cũng ghi "48 ADR" ([90_phan_cuoi.md L59](../../report/final_src/90_phan_cuoi.md)). Trong khi đó báo cáo đã trích ADR-0049 và ADR-0050 ([06_ket_qua.md L285, L235](../../report/final_src/06_ket_qua.md)), tức hiện có ít nhất 50 ADR.
- **Không nhất quán số kiểm thử:** bảng khối lượng ghi "890 hàm kiểm thử", còn Ch.5 ghi "pytest đạt 1261 kiểm thử" ([05_trien_khai.md L128](../../report/final_src/05_trien_khai.md)). Hai số có thể cùng đúng (hàm so với ca sau tham số hóa), nhưng báo cáo không giải thích.

### Inferences
- Trọng tâm đã chuyển từ "thiếu nội dung" sang "thừa và rối". Các vòng sửa 23–24/11 thêm 13 hình nghiên cứu, 6 bảng RQ3 và hai cơ chế mới (backfill, mô tả gộp), nên báo cáo dày lên trong khi trục chính khó thấy hơn.
- Muốn đóng các mục còn mở chỉ cần dựng lại bảng `f12_workload` (sinh bằng script, không cần chép tay) và để người dùng tự điền nhật ký.

### Gaps
- Chưa kiểm được badge giao diện (T0-12) trên ảnh thật, vì chỉ đọc nguồn Markdown, không mở PNG demo.
- Chưa biết đã dựng lại `f12_workload` sau 24/11 hay chưa; con số "48 ADR" lấy theo nguồn hiện tại.

## Tóm tắt VI/EN có nêu gọn vấn đề, phương pháp, dữ liệu, số chính và kết luận không?

### Takeaway
Tóm tắt nêu đủ năm thành phần nhưng **vi phạm mẫu khoa vì tràn sang trang thứ hai** (mẫu yêu cầu "trình bày trong một trang A4"). Bản tiếng Việt khoảng 490 từ với khoảng 20 con số; trong đó RQ3 chiếm gần nửa đoạn kết quả, ứng dụng web và bối cảnh Việt Nam không được nhắc, và câu cuối có cụm "lần đầu". Cần viết lại còn khoảng 250–300 từ, giữ 5–6 con số.

### Cited Findings
- Mẫu khoa: "Trang tóm tắt (Abstract) đề tài bằng tiếng Anh, trình bày trong một trang A4"; bản tiếng Việt cũng "trình bày trong một trang A4", và phần nội dung gồm cả "Đánh giá kết luận và hướng phát triển" ([report/Mau bao cao KLTN_DS.docx](../../report/Mau%20bao%20cao%20KLTN_DS.docx), phần ABSTRACT/TÓM TẮT, trích văn bản ra scratchpad `template_clean.txt` L29, L39, L45).
- PDF hiện tại: Abstract chạy sang tr. 5 (đoạn "…rather than firsts. Keywords…"), Tóm tắt chạy sang tr. 7 (đoạn "…không phải lần đầu. Từ khóa…"). Số liệu này có được khi trích PDF bằng pdftotext.
- Độ dài: bản EN 333 từ, bản VI 491 từ (đếm bằng `wc -w` trên [00_phan_dau.md L5–9 và L19–23](../../report/final_src/00_phan_dau.md)).
- Đoạn kết quả VI ([00_phan_dau.md L23](../../report/final_src/00_phan_dau.md)) có khoảng 15 con số kèm khoảng tin cậy (−0,003 [−0,025; +0,020]; 0,181→0,297 [+0,074; +0,159]; 1,000 so với 0,27; −0,075 đến −0,111; +0,040; +0,041 đến +0,097). Riêng RQ3 và backfill chiếm 3 trên 6 câu.
- Tóm tắt không nhắc ứng dụng web/demo (một trong 7 mục tiêu, [01_gioi_thieu.md L55](../../report/final_src/01_gioi_thieu.md)) và không nhắc QCVN 26:2025 hay bối cảnh Việt Nam, dù Ch.1 có cả một mục về Việt Nam ([01_gioi_thieu.md L31](../../report/final_src/01_gioi_thieu.md)).
- Cụm từ bị cấm có trong câu cuối: "không phải lần đầu" ([00_phan_dau.md L23](../../report/final_src/00_phan_dau.md)); bản EN viết "rather than firsts" (L9).
- Tên tiếng Anh "Grounded Environmental Sound Event Detection, Captioning, and RAG-based Retrieval" ([00_phan_dau.md L3](../../report/final_src/00_phan_dau.md)) không phải bản dịch sát của tên tiếng Việt "Xây dựng hệ thống phát hiện, sinh mô tả và truy vấn…" (L17). Bản rà soát 23/11 đã nêu điểm này ở T0-02.

### Inferences
- Bố cục đề xuất cho bản VI, khoảng 270 từ, vừa một trang: (1) vấn đề và QCVN, 2 câu; (2) hệ thống bốn khối và hai bộ dữ liệu, kiểm trùng (11 đoạn), 2 câu; (3) kết quả chỉ giữ năm số: RQ1 âm tính (CI chứa 0); LBR 0,181 → 0,297 [+0,074; +0,159]; ràng buộc đưa ảo giác/bối cảnh về 0 so với dự đoán, nhưng độ đúng với âm thanh do SED quyết định; bộ lọc cứng cho độ đúng ràng buộc 1,000 nhưng không hơn xếp hạng ngữ nghĩa về nDCG, backfill hơn cả hai; ứng dụng chạy cục bộ, 3,9 s cho một bản ghi; (4) một câu hạn chế/hướng phát triển. Bỏ câu "tra cứu văn liệu…"; đổi thành "các đóng góp là áp dụng và mở rộng của kỹ thuật đã có".
- Dịch lại bản EN theo đúng bản VI đã rút gọn để hai bản khớp nhau. Hội đồng thường đối chiếu hai bản.

### Gaps
- Không rõ khoa có giới hạn số từ cụ thể hay không; mẫu chỉ ghi "một trang A4".

## Chương 1: vấn đề, động lực, Việt Nam, mục tiêu, phạm vi, RQ, đóng góp, bố cục

### Takeaway
Chương 1 đủ ý và mạnh hơn hẳn bản 18/11: đã có QCVN 26:2025, có phạm vi loại trừ tội phạm/khẩn cấp, có bảng RQ và bảng đóng góp C1–C6. Còn bốn điểm yếu. (a) Thiếu đoạn "sơ lược kết quả và kết luận" mà mẫu khoa yêu cầu. (b) Bảng đóng góp quá dày chữ: mỗi ô 40–80 từ, cột "Chưa khẳng định" lấn cột bằng chứng. (c) Số kết quả của tập 19 lớp chỉ xuất hiện ở Ch.1, không có ở Ch.6. (d) Còn cụm "lần đầu", và tiêu đề vẫn là "Đóng góp **dự kiến**".

### Cited Findings
- Mẫu khoa yêu cầu chương đầu gồm "đặt vấn đề, thuận lợi và khó khăn, ưu nhược điểm của các phương pháp hoặc giải pháp hiện tại, nội dung chính của đề tài, phương pháp, giải pháp của đề tài, **kết quả thực hiện và sơ lược kết luận, hướng phát triển**" (mẫu khoa, `template_clean.txt` L292). Mục "Bố cục báo cáo" hiện chỉ có một đoạn mục lục ([01_gioi_thieu.md L94–96](../../report/final_src/01_gioi_thieu.md)); Ch.1 không có câu nào tóm tắt kết quả đạt được.
- Tiêu đề "## Đóng góp dự kiến" và cột "Đóng góp dự kiến" ([01_gioi_thieu.md L77, L83](../../report/final_src/01_gioi_thieu.md)) là cách viết của đề cương, nghe lạc lõng trong báo cáo cuối.
- Câu "…nên báo cáo diễn đạt chúng là áp dụng và mở rộng, không phải 'lần đầu'" ([01_gioi_thieu.md L79](../../report/final_src/01_gioi_thieu.md)) vi phạm luật không viết "lần đầu", dù đặt trong câu phủ định.
- Ch.1 L51 ghi số của tập 19 lớp (B0 0,1892; LBR V2 0,3120; V3 recall 83,2%, precision 78,1%) và hứa "giới hạn này được nêu ở Chương 6 và Chương 7". Khi grep "Việt Nam", "19 lớp", "0,1892" trên `06_ket_qua.md` và `07_ket_luan.md`: **không có kết quả nào**. Nghĩa là một kết quả test được báo ở phần Giới thiệu rồi không xuất hiện lại ở phần kết quả, và lời hứa nêu giới hạn ở Ch.6–7 không được thực hiện.
- Câu "đo ba điều mà các hệ thống mô tả âm thanh thường bỏ qua" ([01_gioi_thieu.md L55](../../report/final_src/01_gioi_thieu.md)) là một khẳng định khái quát, không trích nguồn.
- Phạm vi loại trừ (lời nói, tội phạm, khẩn cấp, chấm điểm nguy hiểm, thời gian thực) đã rõ ([01_gioi_thieu.md L71–75](../../report/final_src/01_gioi_thieu.md)), khớp ADR-0001.
- Bảng RQ ([01_gioi_thieu.md L61–65](../../report/final_src/01_gioi_thieu.md)) rõ ràng; ghi chú nguồn trỏ tới `docs/SYSTEM.md §1.3; ADR-0002; ADR-0021`, tức tài liệu nội bộ mà hội đồng không đọc.

### Inferences
- Sửa tối thiểu (khoảng 1 giờ): (1) đổi "Đóng góp dự kiến" thành "Đóng góp"; (2) thêm 4–5 câu "Kết quả chính" cuối Ch.1, hoặc ngay sau bảng RQ, có câu trả lời một dòng cho từng RQ; (3) rút bảng C1–C6 còn ba cột ngắn (Mã, Đóng góp, Bằng chứng chính), mỗi ô ≤ 25 từ, chuyển nội dung cột "Chưa khẳng định" sang mục "Mức khẳng định" ở Ch.7, vốn đã có sẵn ([07_ket_luan.md L23–25](../../report/final_src/07_ket_luan.md)); (4) chuyển đoạn số 19 lớp sang Ch.6, cạnh bảng thước ứng dụng, Ch.1 chỉ giữ câu định nghĩa; (5) thêm một gạch đầu dòng "chưa kiểm trên bản ghi thu tại Việt Nam / ngoài DataSED" vào hạn chế ở Ch.6 và Ch.7.
- Hội đồng ngành KHDL thường hỏi "đề tài giải quyết vấn đề gì cho ai". Persona hiện nằm ở Ch.5 ([05_trien_khai.md L7](../../report/final_src/05_trien_khai.md)); có thể đưa một câu tóm tắt persona lên Ch.1, mục "Vì sao chọn đề tài".

### Gaps
- Không kiểm được tên đề tài tiếng Anh đã đăng ký chính thức với khoa.

## Người đọc có nắm được hệ thống chính và kết quả chính trong 10 phút không? Có quá tải thuật ngữ nội bộ không?

### Takeaway
**Chưa.** Không có một hình pipeline phương pháp nào: Hình 4.1 là sơ đồ triển khai (người dùng, React, FastAPI, llama.cpp, Postgres), không cho thấy luồng âm thanh → SED → cSEBB → LBR → dòng thời gian → mô tả/RAG. Cũng không có một bảng "kết quả chính" duy nhất; kết quả rải qua khoảng 18 bảng và 8 hình trong Ch.6. Mã nội bộ xuất hiện dày: B0 76 lần, ADR-xxxx 65 lần, V3 58, f2 57, V2 45, cSEBB 16, S13 12, T2b 11; trong thân bài còn tên commit, tên tệp đo và mã PAPER_NOTES.

### Cited Findings
- Hình kiến trúc `f02_architecture.png` ([04_phuong_phap.md L9](../../report/final_src/04_phuong_phap.md)) gồm các khối Người dùng, Giao diện web, Dịch vụ API, llama.cpp, Dịch vụ suy luận, Kho sự kiện và Quy trình nghiên cứu. Đây là sơ đồ triển khai, trong khi đoạn văn kèm theo lại mô tả "năm khối nối tiếp" của luồng dữ liệu (L7). Kết luận này có được khi xem trực tiếp tệp PNG.
- Ch.1 và Ch.2 không có hình nào; hình đầu tiên của báo cáo xuất hiện ở Ch.3 (đếm `@@CAP:fig` theo chương: Ch.1 0, Ch.2 0, Ch.3 3, Ch.4 5, Ch.5 3, Ch.6 8).
- Không có hình minh họa LBR, đóng góp có số tốt nhất. Ch.4 chỉ mô tả LBR bằng một đoạn văn khoảng 300 từ ([04_phuong_phap.md L69](../../report/final_src/04_phuong_phap.md)) kèm hai hình chẩn đoán lỗi (r05, r06), không có sơ đồ đặc trưng → bộ tinh chỉnh → bộ chấm lại → cross-fit.
- Bảng "mã gọi tắt" có 11 dòng gồm A/B/C, v1, v2, T2a/T2b, a–e, f1–f4, g1/g2, S13, B0, LBR V2/V3 ([04_phuong_phap.md L17–30](../../report/final_src/04_phuong_phap.md)). Người đọc phải nhớ khoảng 20 mã thì mới đọc được Ch.6.
- Tham chiếu nội bộ lộ ra trong thân bài: "PAPER_NOTES S56" ([06_ket_qua.md L98](../../report/final_src/06_ket_qua.md)), "commit `c3f0033`" (L76), "`lbr_diagnosis`" (L62), "`scripts.report_checker_sensitivity`" (L218), "`scripts.report_rq3_failures`" (L273), "`grouped_captions_dev_20261124`" (L235), "`retrieval_backfill_test_20261124`" (L293), "`git.dirty = true`" (L64). Các tên tệp này nên nằm trong dòng "Nguồn:" dưới bảng, không nên chen vào câu văn.
- Thuật ngữ quy trình nội bộ: "giai đoạn O", "giai đoạn P", "tầng S/tầng C", "Track 2", "vòng S13", "S8" ([04_phuong_phap.md L50–59](../../report/final_src/04_phuong_phap.md); [06_ket_qua.md L74–100](../../report/final_src/06_ket_qua.md)).
- Tên hai điểm vận hành bằng tiếng Anh dạng mã: "`recall_first`", "điểm vận hành `f1`" ([04_phuong_phap.md L69](../../report/final_src/04_phuong_phap.md)). "f1" ở đây dễ nhầm với ứng viên "f1" (T2a×3) trong cùng chương ([04_phuong_phap.md L26](../../report/final_src/04_phuong_phap.md)) và với chỉ số F1.
- Trục kết quả chính hiện nằm rải rác: kết quả SED cuối ở bảng `tbl:sedfinal` (giữa Ch.6, khoảng tr. 75–78); RQ2 có 3 bảng và 1 hình; RQ3 có 5 bảng và 2 hình.

### Inferences
- Ba sửa đổi rẻ mà lợi nhất cho "10 phút đầu":
  1. Thêm **một hình pipeline phương pháp** ở cuối Ch.1 hoặc đầu Ch.4: Âm thanh → SED (B0, 5 mô hình) → ghép sự kiện (cSEBB) → LBR (tinh chỉnh biên + chấm lại) → dòng thời gian → {mô tả G1–G3; kho sự kiện → phân tích câu hỏi → lọc cứng + backfill → câu trả lời có bằng chứng}. Ghi kèm RQ1/RQ2/RQ3/C5 ở đúng khối. Có thể vẽ bằng script giống `build_final_figures.py`, khoảng 2–3 giờ. Hình 4.1 hiện tại chuyển về Ch.5 làm "sơ đồ triển khai", qua đó đóng luôn T0-11.
  2. Thêm **một bảng "Kết quả chính"** khoảng 6 dòng ở đầu Ch.6 hoặc trong Ch.7 (RQ1, LBR/SED, RQ2 so với dự đoán, RQ2 so với nhãn gốc, RQ3 hybrid so với vector so với backfill, độ trễ), mỗi dòng gồm con số, CI và câu kết luận một vế. Mọi số lấy từ `final_numbers`/`rq3_modes`/`retrieval_backfill`, nên qua được `check_doc_claims`.
  3. Rút bảng mã còn **5 mã người đọc cần**: v1/v2 (hai công thức), f2 (mốc S13), B0 (hệ SED cuối), LBR V2 / LBR V3. Chuyển a–e, f1–f4, g1/g2, T2a/T2b sang phụ lục cạnh bảng S13. Đổi "`f1`/`recall_first`" thành "điểm cân bằng" / "điểm ưu tiên phát hiện" trong câu văn.
- Số ADR nên rút: giữ khoảng 10 ADR then chốt dưới dạng "(xem ADR-0045)", số còn lại chuyển vào dòng "Nguồn". Hội đồng không đọc ADR; 65 lần nhắc tạo cảm giác hồ sơ kỹ thuật nội bộ chứ không phải khóa luận.

### Gaps
- Chưa thử đo "10 phút đọc" với người thật. Nhận định dựa trên cấu trúc và mật độ thuật ngữ đã đếm.

## Đe dọa tính hợp lệ và hạn chế: có trung thực và nằm ở một chỗ không?

### Takeaway
Rất trung thực, có lẽ trung thực quá mức, nhưng **phân tán ở ít nhất 6 chỗ** (Ch.3 cuối, Ch.4 "phạm vi diễn giải", Ch.5 tái lập, Ch.6 "Tái sử dụng tập test", Ch.6 "Thảo luận và hạn chế" với 11 gạch đầu dòng, Ch.7 "Hạn chế"). Hai thiếu sót thật: (1) **không có dòng hạn chế "chưa thử trên dữ liệu ngoài DataSED/thu tại Việt Nam"** ở Ch.6–7, dù Ch.1 hứa có; (2) **backfill được nảy ý từ phân tích trên test** (hybrid rỗng ở 32/97 truy vấn test của f2), nhưng không được kể vào "ba chỗ tái sử dụng thích nghi".

### Cited Findings
- Các vị trí bàn về hạn chế: [03_du_lieu.md L80](../../report/final_src/03_du_lieu.md); [04_phuong_phap.md L153–155](../../report/final_src/04_phuong_phap.md); [05_trien_khai.md L94, L106, L110, L114](../../report/final_src/05_trien_khai.md); [06_ket_qua.md L315–322 và L330–344](../../report/final_src/06_ket_qua.md); [07_ket_luan.md L27–29](../../report/final_src/07_ket_luan.md).
- Ch.7 ghi "Bốn hạn chế quan trọng nhất" (cỡ test, không tất định, PSDS/LBR, bộ đo từ điển) ([07_ket_luan.md L29](../../report/final_src/07_ket_luan.md)). Danh sách này không có: một họ dữ liệu duy nhất / chưa kiểm ngoài miền; không có dữ liệu Việt Nam; trùng nguồn AudioSet; tái sử dụng test.
- Ch.6 hạn chế có 11 gạch đầu dòng ([06_ket_qua.md L334–344](../../report/final_src/06_ket_qua.md)) nhưng không có mục nào về kiểm ngoài miền hoặc Việt Nam. Chỉ Ch.5 L29 nhắc "chưa thử trên bản ghi thu ngoài hai bộ dữ liệu".
- Động cơ của backfill trong báo cáo: "Phân tích trên chỉ ra rằng hybrid thua không phải vì xếp sai mà vì trả quá ít kết quả: ở kho f2, 32/97 truy vấn có danh sách hybrid rỗng" ([06_ket_qua.md L285](../../report/final_src/06_ket_qua.md)). Đây là phân tích trên test (97 truy vấn có liên quan là số của test, L247). Trong khi đó mục "Có ba chỗ tái sử dụng thích nghi" chỉ kể A2/A5, thiết kế LBR và cờ dirty ([06_ket_qua.md L321](../../report/final_src/06_ket_qua.md)). Báo cáo `reports/Cải thiện RAG và sinh mô tả.md` (L3, L22) cho thấy backfill đã được mô phỏng trên validation trước khi ghi ADR-0049, nhưng thân bài báo cáo không nói điều đó.
- Mô tả gộp và ngưỡng rào đón được chọn trên dev V3 rồi báo trên dev ([06_ket_qua.md L235–239](../../report/final_src/06_ket_qua.md)). Số "rào đón đúng 17/98 so với 202/228" là số in-sample trên dev, nhưng câu văn không ghi chữ "in-sample".
- Phần "dirty" được nhắc đi nhắc lại: Ch.5 L94 (đo độ trễ), L110, L114 (17 run bẩn liệt kê từng loại); Ch.6 L64, L321, L339. Đếm chuỗi "dirty": Ch.5 1 lần, Ch.6 3 lần, cộng các câu "cây làm việc chưa sạch".
- Mức đồng thuận 0,5785 và cảnh báo "không phải trần tuyệt đối" lặp ở [03_du_lieu.md L78](../../report/final_src/03_du_lieu.md), [06_ket_qua.md L62, L138, L164, L337](../../report/final_src/06_ket_qua.md) (6 lần xuất hiện của "0,5785").

### Inferences
- Gom lại thành **một mục "Các đe dọa tính hợp lệ"** ở cuối Ch.6, khoảng 1,5 trang, chia 4 nhóm: (a) *Nội tại*: test 139 dùng nhiều lượt, tái sử dụng thích nghi (A2/A5, thiết kế LBR, **backfill nảy ý từ phân tích test RQ3**, mô tả gộp chọn trên dev), cờ dirty; (b) *Kết luận thống kê*: n nhỏ, CI không hiệu chỉnh bội, không tất định; (c) *Cấu trúc/đo lường*: collar 0,2 s chặt hơn đồng thuận nhãn, bộ đo từ điển (κ ≈ 0), PSDS phụ thuộc lưới, độ đúng bộ lọc chỉ so với dự đoán; (d) *Ngoại suy*: một họ dữ liệu cùng tác giả, trùng nguồn AudioSet, **chưa có bản ghi Việt Nam / ngoài miền**, LBR chưa kiểm ở bộ khác. Ch.7 chỉ cần dẫn lại mục này kèm 3–4 dòng.
- Thêm một câu cho backfill: "ý tưởng xuất phát từ phân rã lỗi RQ3 trên test; định nghĩa được ghi trước (ADR-0049) và kiểm trên validation trước khi chạy test một lần". Đây là sửa P0 vì hội đồng chặt sẽ tự nhận ra.
- Bỏ các câu dirty khỏi Ch.5 L94 và L114, giữ một chỗ duy nhất trong mục đe dọa. Câu cảnh báo 0,5785 cũng chỉ nên nói một lần.
- Giọng văn rào đón dày đặc ("không phải bằng chứng", "chỉ để định cỡ", "chưa kiểm bằng thí nghiệm kiểm soát"…) ở mọi đoạn có thể khiến hội đồng đọc thành thiếu tự tin. Nếu đã gom hạn chế về một chỗ thì có thể bỏ bớt các câu rào đón lặp lại trong thân bài.

### Gaps
- Không truy được thời điểm chính xác của mô phỏng backfill trên validation so với lần đọc kết quả test RQ3 (cần `git log` của ADR-0049 và `rq3_modes_20261123`). Đề xuất câu công khai ở trên đúng trong cả hai trường hợp.

## Phần tái lập và kỹ thuật (Ch.5): tỷ lệ có cân đối không?

### Takeaway
Ch.5 dài 12 trang, gần bằng Ch.4 phương pháp (13 trang) và gấp ba Ch.7. Phần có giá trị với hội đồng là: tình huống sử dụng/yêu cầu, ảnh demo, độ trễ, kiểm thử. Phần "Theo dõi thí nghiệm" (bảng 218 run, hình dòng thời gian run, danh sách 17 run bẩn) và các chi tiết vận hành (kẹp biên LBR, parity fp16, cờ `official`, script PowerShell) nên chuyển sang phụ lục hoặc bỏ. Nếu chuyển, tiết kiệm được khoảng 3–4 trang và Ch.5 đọc như chương "hiện thực" của mẫu khoa.

### Cited Findings
- Ch.5 ở tr. 52–63 (12 trang vật lý); Ch.4 ở tr. 39–51 (13 trang); Ch.7 ở tr. 97–100 (4 trang). Số liệu có được khi trích PDF.
- Đoạn "Theo dõi thí nghiệm" khoảng 270 từ, kèm bảng sổ run và hình r12 ([05_trien_khai.md L114–126](../../report/final_src/05_trien_khai.md)). Đoạn này liệt kê từng loại run bẩn và kết luận "không có lần chạy mới nào từ 15/10 đến 06/11" (L114). Câu sau tự công bố một khoảng trống ba tuần, trùng với ba tuần 5–7 để trống trong nhật ký ([90_phan_cuoi.md L97–99](../../report/final_src/90_phan_cuoi.md)).
- Chi tiết vận hành sâu: cờ `official`, kẹp biên LBR ([05_trien_khai.md L64](../../report/final_src/05_trien_khai.md)); ba script PowerShell, kiểm cờ `official` (L102); parity 573/665/691 trên 692 sự kiện (L104), lặp lại gần nguyên văn ở [06_ket_qua.md L313](../../report/final_src/06_ket_qua.md).
- Số "3,7 s / 0,27 s (một lượt đo)" ([05_trien_khai.md L23, L104](../../report/final_src/05_trien_khai.md)) cùng tồn tại với bảng độ trễ có thống kê "trung vị 3,89 s, truy vấn 0,22 s" (L94). Hai bộ số cho cùng một đại lượng, và bảng yêu cầu N2 vẫn trích số một lượt.
- Ch.7 "Hướng phát triển" ghi "đo hiệu năng có thống kê" ([07_ket_luan.md L37](../../report/final_src/07_ket_luan.md)) trong khi Ch.5 đã có bảng độ trễ 10 lần đo.
- Mẫu khoa gợi ý các chương "Phân tích yêu cầu / Thiết kế hệ thống / Hiện thực và triển khai / Đánh giá và thảo luận", và cho phép "tùy theo đề tài mà đặt tên chương mục phù hợp" (`template_clean.txt` L178–203, L290).

### Inferences
- Giữ ở Ch.5: yêu cầu (bảng F/N), sơ đồ triển khai (Hình 4.1 hiện tại chuyển xuống đây), ba thành phần dịch vụ thu gọn, hai ảnh demo, bảng độ trễ, một đoạn kiểm thử/CI, một đoạn tái lập (manifest, đóng băng SHA-256, ba bộ kiểm tài liệu).
- Chuyển sang phụ lục: bảng sổ run, hình r12, danh sách run bẩn, chi tiết parity. Bỏ: câu "không có lần chạy mới từ 15/10 đến 06/11" (nếu giữ thì phải giải thích nhóm làm gì trong ba tuần đó), chi tiết script PowerShell.
- Đồng bộ N2 theo bảng độ trễ (3,89 s trung vị; RTF 0,072) và sửa dòng hướng phát triển ở Ch.7.

### Gaps
- Chưa rõ GVHD muốn tách thành chương "Phân tích yêu cầu" riêng theo mẫu hay không; báo cáo hiện gộp yêu cầu vào Ch.5, điều mà mẫu cho phép.

## Định vị so với công trình liên quan: có nêu khoảng trống mà không phóng đại không? ("lần đầu")

### Takeaway
Định vị đã thận trọng: C2, C3, C4 được hạ thành "áp dụng và mở rộng", có LA-RAG, ECHO, TAC, RED/EPN. Tuy vậy chuỗi "lần đầu" còn xuất hiện **4 lần** (Abstract EN dạng "firsts", Tóm tắt VI, Ch.1 L79, Ch.7 L25), đều trong câu phủ định. Grep sẽ bắt hết, và việc nhắc lặp lại "không phải lần đầu" tự nó gợi ý đến khẳng định ấy. Ch.2 còn thiếu cơ sở lý thuyết cho chính các kỹ thuật cốt lõi: gradient boosting/cross-fitting dùng trong LBR, bootstrap ghép cặp, giải mã có ràng buộc bằng ngữ pháp.

### Cited Findings
- Các chỗ có "lần đầu": [00_phan_dau.md L23](../../report/final_src/00_phan_dau.md) ("không phải lần đầu"); [01_gioi_thieu.md L79](../../report/final_src/01_gioi_thieu.md) ("không phải 'lần đầu'"); [07_ket_luan.md L25](../../report/final_src/07_ket_luan.md) ("**không** khẳng định 'lần đầu'"); bản EN "rather than firsts" ([00_phan_dau.md L9](../../report/final_src/00_phan_dau.md)). Cụm "baseline đầu tiên" ([02_co_so_ly_thuyet.md L77](../../report/final_src/02_co_so_ly_thuyet.md)) và "trường hợp đầu tiên cSEBB thắng" ([06_ket_qua.md L94](../../report/final_src/06_ket_qua.md)) không vi phạm, nhưng nên đổi cụm sau thành "f2 là hệ duy nhất mà cSEBB thắng".
- Ch.2 có các mục SED, đánh giá, ghép sự kiện (SEBB, RED/EPN), học chuyển giao, ảo giác (ECHO, TAC), RAG (LA-RAG), vị trí đề tài ([02_co_so_ly_thuyet.md](../../report/final_src/02_co_so_ly_thuyet.md)). Không có mục nào về: HistGradientBoosting/cây tăng cường (thành phần lõi của LBR, [04_phuong_phap.md L69](../../report/final_src/04_phuong_phap.md)); cross-fitting/kiểm chứng chéo lồng nhau; bootstrap và kiểm định Welch (chỉ có ở [04_phuong_phap.md L167](../../report/final_src/04_phuong_phap.md)); giải mã có ràng buộc ngữ pháp (GBNF) cho LLM ([04_phuong_phap.md L107](../../report/final_src/04_phuong_phap.md)); vector embedding/HNSW (chỉ có một dòng trong danh mục viết tắt).
- Ch.2 tự giới hạn phạm vi tra cứu: "ba truy vấn mở rộng và đọc sáu bài… không phải tổng quan hệ thống" ([02_co_so_ly_thuyet.md L81](../../report/final_src/02_co_so_ly_thuyet.md)). TLTK có 28 nguồn (PDF tr. 101–104).
- Mẫu khoa định nghĩa chương Cơ sở lý thuyết là "tóm tắt các vấn đề lý thuyết cơ sở liên quan đến đề tài cũng như thảo luận, đánh giá về các đề tài gần đây" (`template_clean.txt` L294).

### Inferences
- Sửa P0 (10 phút): xóa cả bốn câu phủ định "lần đầu"/"firsts". Thay bằng câu khẳng định tích cực: "Các đóng góp được trình bày là áp dụng và mở rộng của các kỹ thuật đã có (Chương 2)". Ở Ch.7 L25, bỏ hẳn mệnh đề đầu.
- Sửa P1 (khoảng 3 giờ, ≤ 2 trang): thêm vào Ch.2 ba mục ngắn, **tự diễn đạt kèm một công thức**, không chép định nghĩa sách: (a) cây tăng cường gradient và cross-fitting (vì sao LBR không nhìn thấy fold nó chấm); (b) bootstrap ghép cặp theo bản ghi; (c) giải mã có ràng buộc bằng ngữ pháp (vì sao "0 vi phạm theo cấu tạo"). Chỉ trích nguồn đã có trong RELATED_WORK ở mức V3. Nếu không có nguồn V3 thì viết như mô tả kỹ thuật của chính đề tài, không trích. Với hội đồng KHDL, thiếu nền cho mô hình lõi (GBM trong LBR) dễ dẫn tới câu hỏi "LBR dùng thuật toán gì, vì sao chọn nó".

### Gaps
- Chưa kiểm RELATED_WORK xem đã có nguồn V3 cho gradient boosting, bootstrap hay constrained decoding chưa. Cần kiểm trước khi thêm trích dẫn.

## Rủi ro Turnitin (<25%) và rủi ro bị nghi văn do máy viết

### Takeaway
Rủi ro trùng lặp **lớn nhất không nằm ở văn bản** mà ở chỗ **repo GitHub đang công khai và chứa nguyên khóa luận** (PDF, DOCX, nguồn Markdown, cả báo cáo giữa kỳ). Nếu nguồn Internet hoặc kho bài nộp của Turnitin đã có các bản này, báo cáo có thể bị khớp với chính nó. Về văn bản, phần dễ khớp nguồn ngoài chỉ gồm vài đoạn định nghĩa/quy chuẩn (QCVN, công thức P/R/F1, định nghĩa ảo giác của Ji et al., RAG). Về phong cách, văn bản có nhiều dấu hiệu "khuôn": 44 lần "không phải", 12 lần "**không**" in đậm, 4 khối "Ba điều… **Một,** **Hai,** **Ba,**", 8 lần "Thứ nhất". Bộ phát hiện AI của Turnitin hiện **không hỗ trợ tiếng Việt**, nên phần tiếng Việt sẽ không có báo cáo AI tự động; rủi ro còn lại là người chấm tự đọc và phần Abstract tiếng Anh.

### Cited Findings
- Repo `paterdubs/environmental-audio-rag` đang **công khai**: GitHub API trả `"private": false, "visibility": "public"`, `pushed_at` 2026-11-24 (truy vấn `api.github.com/repos/paterdubs/environmental-audio-rag` ngày 24/11/2026). Git đang theo dõi `report/Khoa_luan_environmental_audio_rag.pdf`, `.docx`, `report/final_src/*.md`, `report/Bao_cao_KLTN_giua_ky_environmental_audio_rag.pdf`, `report/REPORT.docx/.pdf` (kết quả `git ls-files`). Repo cũng công khai `CLAUDE.md`, `AGENTS.md` và docs/AGENT_SYNC.md, vốn mô tả quy trình làm việc với agent; bản rà soát 23/11 đã nêu điểm này ([reports/Đánh giá khóa luận audio RAG.md L41](../../reports/Đánh%20giá%20khóa%20luận%20audio%20RAG.md)). Trang bìa trong PDF công khai có cả họ tên và MSSV.
- Turnitin đối chiếu bài nộp với trang Internet và kho bài nộp trước đó của sinh viên. Theo hướng dẫn của Johns Hopkins, bản nháp nộp trước (vào kho) có thể hiện ra như bị đạo văn; theo một trường khác, mức khớp 100% với một bài của sinh viên thường có nghĩa nguồn chính là bài của sinh viên đó ([JHU Canvas – Turnitin](https://canvas.jhu.edu/faculty-resources/third-party-tools/turnitin); [Reading TEL](https://sites.reading.ac.uk/TEL-Support-Staff/?p=2421); [Teesside](https://eatsupport.tees.ac.uk/staff/knowledgebase/turnitin-understanding-the-contents-of-a-similarity-report/)). Không tìm thấy nguồn nào xác nhận Turnitin có thu thập GitHub hay không.
- Phát hiện AI của Turnitin hỗ trợ tiếng Anh, Tây Ban Nha, Nhật, Ả Rập, và từ 06/10/2026 thêm Hà Lan, Đức, Thổ Nhĩ Kỳ ([PR Newswire, 06/10/2026](https://www.prnewswire.com/da/pressemeddelelser/turnitin-now-offers-ai-writing-detection-for-dutch-german-and-turkish-language-submissions-302899374.html)). Ngôn ngữ không được hỗ trợ sẽ không có báo cáo AI, và tài liệu trộn ngôn ngữ cũng không được hỗ trợ ([Turnitin AI writing detection – tổng hợp kết quả tìm kiếm, trang trợ giúp Turnitin](https://helpcenter.turnitin.com/hc/en-us/articles/46468418712461-Why-can-t-I-see-the-AI-writing-detection-report)). Trang hướng dẫn chính thức `guides.turnitin.com` trả 403 nên chưa đọc trực tiếp được.
- Không tìm được quy định ngưỡng trùng lặp của IUH trên web. Một trường khác (ĐH Kinh tế – Luật) dùng ngưỡng dưới 30% (kết quả tìm kiếm). Ngưỡng 25% của nhóm lấy theo giao việc.
- Các đoạn dễ khớp nguồn ngoài: (1) đoạn QCVN với khung giờ, mức dBA, các bậc nới ngưỡng ([01_gioi_thieu.md L33–35](../../report/final_src/01_gioi_thieu.md)), vốn diễn đạt sát văn bản quy chuẩn; (2) định nghĩa và công thức P/R/F1, micro/macro ([02_co_so_ly_thuyet.md L15–33](../../report/final_src/02_co_so_ly_thuyet.md)), thuộc loại câu chuẩn có nhiều trên mạng; (3) câu trích Ji et al. "vô nghĩa hoặc không trung thành với nguồn được cung cấp" (L61); (4) mô tả PANNs/AudioSet "hơn 5.000 giờ, 527 lớp" (L51); (5) số thống kê trong bảng (ít bị tính). Nhìn chung các đoạn này ngắn, đã Việt hóa và có trích nguồn, nên rủi ro thấp.
- Dấu hiệu văn khuôn (đếm bằng grep trên Ch.1–7): "không phải" 44 lần; "**không**" in đậm 12; "theo cấu tạo" 5; "Ba điều" 4; "**Một,**" 3; "Thứ nhất" 8; "Đây là" 9; "ghi trước" 15; "khoảng tin cậy" 26. Số cụm in đậm: Ch.6 74 cặp `**`, Ch.4 59. Ví dụ cấu trúc lặp:
  - "Ba điều cần đọc cùng nhau. **Một,** … **Hai,** … **Ba,** …" ([06_ket_qua.md L273](../../report/final_src/06_ket_qua.md)); "Cách đọc đúng RQ2 cần thừa nhận ba điều. **Một,** …" (L214); "Ba điều rút ra. **Một,** …" (L231); "Ba điều cần nói thẳng: …" (L106).
  - Mẫu "X, không phải Y" / "không có nghĩa là": "Đây không phải khẳng định 'ngang người'" (L164); "không phải một khám phá bất ngờ" ([04_phuong_phap.md L110](../../report/final_src/04_phuong_phap.md)); "Đó là điều kiện cần, không phải bảo đảm" (L95); "chỉ để định cỡ, không phải bảng xếp hạng" ([06_ket_qua.md L162](../../report/final_src/06_ket_qua.md)).
  - Mở đầu chương theo cùng một khuôn "Chương này …. Mọi con số do script…": [03_du_lieu.md L3](../../report/final_src/03_du_lieu.md), [05_trien_khai.md L3](../../report/final_src/05_trien_khai.md), [06_ket_qua.md L3](../../report/final_src/06_ket_qua.md), [07_ket_luan.md L3](../../report/final_src/07_ket_luan.md).
  - Câu siêu dài, nhồi nhiều mệnh đề chấm phẩy: [06_ket_qua.md L332](../../report/final_src/06_ket_qua.md) (đoạn tóm tắt một câu khoảng 150 từ); [04_phuong_phap.md L69](../../report/final_src/04_phuong_phap.md) (khoảng 300 từ một đoạn).
- Ít gạch đầu dòng (Ch.1, Ch.2 không có; Ch.6 có 24), nên rủi ro "quá nhiều bullet" thấp. Rủi ro chính là nhịp câu đối lập và rào đón đều đặn.

### Inferences
- **P0, quyết định của người dùng (không phải sửa báo cáo):** trước khi nộp Turnitin, cân nhắc chuyển repo sang private, hoặc gỡ `report/*.pdf|docx` và `report/final_src` khỏi nhánh công khai, sau khi hỏi GVHD. Nếu phải giữ công khai (ví dụ để chấm mã) thì báo trước với GVHD/người quét để loại trừ nguồn GitHub và báo cáo giữa kỳ. Việc này cũng giảm lộ MSSV và tệp agent. Agent rà soát không tự thay đổi việc này.
- **P1, phong cách:** gom các khối "Một, Hai, Ba" thành văn xuôi thường hoặc bảng nhỏ; giảm "**không**" in đậm còn 2–3 chỗ thật quan trọng; cắt khoảng một nửa số câu "X không phải Y" (giữ câu ở hạn chế, bỏ câu ở thân bài); viết lại bốn câu mở chương cho khác nhau; tách câu dài trên 60 từ. Làm được trong 3–4 giờ và cũng giúp rút ngắn báo cáo.
- Đoạn QCVN nên viết lại theo kiểu tóm ý ("quy chuẩn đặt giới hạn theo loại nguồn, khung giờ và thời lượng phát ra") và đưa con số cụ thể vào bảng. Như vậy giảm câu chạy sát văn bản pháp quy.

### Gaps
- Không xác minh được Turnitin có thu thập GitHub hay không, và báo cáo giữa kỳ đã từng được nộp lên Turnitin chưa. Cả hai quyết định mức rủi ro thực tế của việc tự khớp.
- Không tìm được quy định chính thức của IUH về ngưỡng trùng lặp hay về công cụ phát hiện AI; cần hỏi GVHD (bản rà soát 23/11, T0-01, đã nêu).

## Độ dài: cắt hoặc chuyển phần nào sang phụ lục, ảnh hưởng số trang ra sao

### Takeaway
Giới hạn số trang không phải vấn đề (112/150). Vấn đề là **Ch.6 dài 33 trang và kể theo trình tự thời gian** (v1 → v2 → S13 → O → P → LBR) trước khi tới kết quả chính. Nếu tái cấu trúc Ch.6 theo thứ tự "hệ cuối → RQ1 → RQ2 → RQ3 → đe dọa", gói lịch sử vào một tiểu mục kèm hình hành trình, rồi chuyển khoảng 10 bảng/hình phụ sang phụ lục, thân bài giảm khoảng 10–14 trang (ước tính), còn khoảng 95–100 trang tổng, và trục chính hiện rõ.

### Cited Findings
- Ch.6 ở tr. 64–96 (33 trang), có 18 bảng và 8 hình (đếm `@@CAP`); thứ tự tiểu mục: phân loại → RQ1 → "SED tiến bộ ra sao" (6 tiểu mục: v1 thấp, v1→v2, S13, giai đoạn O, LBR, PSDS) → định cỡ → RQ2 (2 tiểu mục) → RQ3 (1 tiểu mục) → parser → tái sử dụng test → thảo luận ([06_ket_qua.md](../../report/final_src/06_ket_qua.md), danh sách heading lấy bằng grep `^#`).
- Mẫu khoa: "Tại mỗi mục, tiểu mục phải có ít nhất là 2 tiểu mục" (`template_clean.txt` L219). Mục RQ3 chỉ có **một** tiểu mục "### Chế độ backfill" ([06_ket_qua.md L283](../../report/final_src/06_ket_qua.md)), tức vi phạm.
- Mẫu khoa: "Phụ lục… không được dày hơn phần chính" (`template_clean.txt` L222). Phụ lục hiện khoảng 6 trang, nên còn nhiều chỗ.
- Ứng viên cắt hoặc chuyển, với ước lượng trang:
  - Ch.6 "Vì sao v1 thấp", "Từ v1 đến v2", "Vòng chọn S13" kèm bảng 11 ứng viên, "Giai đoạn O/P", phần cSEBB ([06_ket_qua.md L58–100](../../report/final_src/06_ket_qua.md)): gộp thành một tiểu mục "Hành trình cải tiến SED" khoảng 1,5 trang, dựa trên hình r04 sẵn có; chuyển bảng S13, bảng tiến triển, hình dev–test r08 sang phụ lục. **Ước tính −4 đến −5 trang.**
  - "PSDS và lưới ngưỡng" kèm bảng chẩn đoán PSDS (L150–158): giữ một đoạn, bảng sang phụ lục. **Ước tính −1 trang.**
  - RQ3: 5 bảng + 2 hình (rq3final, rq3paired, rq3groups, rq3backfill, r11, r13). Gộp rq3final và rq3paired, chuyển r11 (từng truy vấn) sang phụ lục. **Ước tính −1,5 trang.**
  - RQ2: đoạn sự cố llama.cpp OOM ([06_ket_qua.md L243](../../report/final_src/06_ket_qua.md)) chuyển vào ghi chú hoặc phụ lục; "Mô tả gộp theo lớp" (L233–239) là tính năng ứng dụng, nên chuyển sang Ch.5 cạnh mô tả giao diện. **Ước tính −0,5 đến −1 trang** ở Ch.6.
  - Ch.5 "Theo dõi thí nghiệm" kèm bảng sổ run và hình r12 ([05_trien_khai.md L114–126](../../report/final_src/05_trien_khai.md)), chi tiết parity (L104): sang phụ lục. **Ước tính −2 trang.**
  - Ch.4: bảng mã 11 dòng rút còn 5 dòng; hình nhật ký huấn luyện r03 ([04_phuong_phap.md L61–67](../../report/final_src/04_phuong_phap.md)) sang phụ lục; lặp parity ở [06_ket_qua.md L313](../../report/final_src/06_ket_qua.md) thì bỏ. **Ước tính −1,5 trang.**
  - Ch.1 bảng đóng góp rút ngắn: **ước tính −0,5 trang.** Abstract/Tóm tắt gọn lại một trang mỗi bản: **−2 trang** ở phần đầu.
- Phần thêm vào (bù lại): hình pipeline phương pháp (+1), bảng kết quả chính (+0,5), mục đe dọa gộp (thay cho các đoạn rải rác, khoảng ±0), ba mục lý thuyết Ch.2 (+1,5 đến 2).

### Inferences
- Cân đối ròng ước tính: khoảng −12 trang cắt/chuyển, +3 đến 3,5 trang thêm, nên tổng khoảng 100–103 trang; Ch.6 còn khoảng 20–22 trang. Các con số là ước lượng theo mật độ trang hiện tại, cần dựng lại để biết chính xác.
- Thứ tự Ch.6 đề xuất: 6.1 Hệ SED cuối (B0+LBR, bảng sedfinal, định cỡ) → 6.2 Hành trình cải tiến (gọn) → 6.3 RQ1 → 6.4 RQ2 (so với dự đoán; so với nhãn gốc) → 6.5 RQ3 (ba chế độ; backfill), khi đó RQ3 có hai tiểu mục và hết vi phạm mẫu → 6.6 Bộ phân tích câu hỏi → 6.7 Đe dọa tính hợp lệ. Bộ phân loại DataSEC có thể là 6.0 hoặc gộp vào RQ1, vì nó là bước giữa của nhánh C.
- Mọi bảng hoặc hình chuyển sang phụ lục giữ nguyên script sinh, nên `check_doc_claims` không bị ảnh hưởng. Chỉ đổi vị trí `@@INCLUDE`.

### Gaps
- Chưa dựng thử bản rút gọn, nên số trang chỉ là ước lượng.
- Chưa rõ GVHD thích chương kết quả kể theo hành trình (thể hiện quá trình) hay theo RQ. Một số hội đồng đánh giá cao phần "quá trình"; khi đó nên giữ hình r04 ở thân bài.

## Danh sách ưu tiên P0 / P1 / P2 (không train lại, không mở test, ≤ 3 ngày)

### Takeaway
Có 9 việc P0, tổng khoảng 10–13 giờ: Abstract/Tóm tắt về một trang, xóa "lần đầu", hạn chế ngoài miền/Việt Nam, công khai nguồn gốc backfill, bảng kết quả chính + hình pipeline, tiểu mục RQ3, cập nhật số lỗi thời, quyết định repo công khai, và nhật ký. Các việc P1 làm báo cáo gọn và dễ đọc hơn. Các việc P2 bỏ qua.

### Cited Findings
- (Tổng hợp từ các mục trên; vị trí và bằng chứng đã dẫn ở từng mục.)

### Inferences
**P0, phải xong trước 28/11**

| # | Việc | Vị trí | Vì sao hội đồng quan tâm | Sửa tối thiểu | Ước giờ |
|---|---|---|---|---|---|
| P0-1 | Abstract và Tóm tắt về **một trang** mỗi bản; giảm còn 5–6 con số; thêm ứng dụng và câu Việt Nam/QCVN; thống nhất tên EN | [00_phan_dau.md L3–25](../../report/final_src/00_phan_dau.md); PDF tr. 4–7 | Vi phạm mẫu khoa; là trang đọc đầu tiên | Viết lại khoảng 270 từ VI, dịch EN tương ứng | 1,5 |
| P0-2 | Xóa mọi chuỗi "lần đầu"/"firsts" | 00 L9, L23; [01 L79](../../report/final_src/01_gioi_thieu.md); [07 L25](../../report/final_src/07_ket_luan.md) | Luật dự án; câu phủ định vẫn gợi ý khẳng định | Thay bằng "áp dụng và mở rộng kỹ thuật đã có"; chạy grep xác nhận 0 kết quả | 0,25 |
| P0-3 | Thêm hạn chế "chưa kiểm trên bản ghi ngoài DataSED / thu tại Việt Nam; một họ dữ liệu cùng tác giả"; chuyển số tập 19 lớp sang Ch.6 | [06 L334–344](../../report/final_src/06_ket_qua.md); [07 L29](../../report/final_src/07_ket_luan.md); [01 L51](../../report/final_src/01_gioi_thieu.md) | Ch.1 hứa mà không thực hiện; câu hỏi "không thực tế" | Một gạch đầu dòng ở Ch.6 và Ch.7; dời đoạn số 19 lớp | 0,5 |
| P0-4 | Công khai: ý tưởng backfill xuất phát từ phân rã lỗi RQ3 trên test; mô tả gộp và rào đón là số in-sample trên dev | [06 L285, L321, L235–239](../../report/final_src/06_ket_qua.md) | Đúng loại "chọn theo test" mà hội đồng chặt sẽ bắt | Thêm mục thứ tư vào "tái sử dụng thích nghi"; thêm chữ "trên dev, in-sample" | 0,5 |
| P0-5 | **Bảng "Kết quả chính"** (khoảng 6 dòng) ở đầu Ch.6 hoặc trong Ch.7, kèm 4–5 câu "kết quả và sơ lược kết luận" ở Ch.1 | Ch.1 cuối; Ch.6 đầu; [07 L5–13](../../report/final_src/07_ket_luan.md) | Mẫu khoa đòi Ch.1 có kết quả; giúp đọc trong 10 phút | Lấy số từ `final_numbers`, `rq3_modes`, `retrieval_backfill`, `latency`; chạy `check_doc_claims` | 1,5 |
| P0-6 | **Hình pipeline phương pháp** (âm thanh → SED → cSEBB → LBR → dòng thời gian → mô tả/RAG, gắn RQ1–3/C5); Hình 4.1 hiện tại chuyển sang Ch.5 làm sơ đồ triển khai | [04 L5–13](../../report/final_src/04_phuong_phap.md) | Hiện không có hình nào cho thấy phương pháp; LBR không có sơ đồ | Vẽ bằng script cùng kiểu `build_final_figures.py` | 2–3 |
| P0-7 | RQ3 phải có ≥ 2 tiểu mục (thêm "### Ba chế độ truy hồi" trước "### Backfill") | [06 L245–283](../../report/final_src/06_ket_qua.md) | Vi phạm quy tắc tiểu mục của mẫu khoa | Thêm một heading | 0,1 |
| P0-8 | Cập nhật số lỗi thời: "48 ADR" (hiện ≥ 50), git ghi chú bảng khối lượng, giải thích 890 hàm so với 1261 ca kiểm thử; N2 dùng số độ trễ có thống kê; bỏ "đo hiệu năng có thống kê" khỏi hướng phát triển | [f12_workload.md](../../report/final_tables/f12_workload.md); [90 L59](../../report/final_src/90_phan_cuoi.md); [05 L23, L128](../../report/final_src/05_trien_khai.md); [07 L37](../../report/final_src/07_ket_luan.md) | Số tự mâu thuẫn bị bắt ngay khi đọc chéo | Dựng lại `build_final_tables`; sửa 3 câu | 0,5 |
| P0-9 | **(Người dùng quyết)** Repo GitHub công khai chứa toàn văn khóa luận, báo cáo giữa kỳ, MSSV và tệp agent; nhật ký tuần 5–7 và 9 trống trong khi tuần 1 gánh gần như toàn bộ hệ thống; Ch.5 tự ghi "không có lần chạy từ 15/10 đến 06/11" | Repo `paterdubs/environmental-audio-rag`; [90 L93–102](../../report/final_src/90_phan_cuoi.md); [05 L114](../../report/final_src/05_trien_khai.md) | Rủi ro Turnitin tự khớp; câu hỏi "ba tuần làm gì", "một tuần làm hết?" | Hỏi GVHD rồi chuyển private hoặc gỡ tệp báo cáo trước khi quét; nhóm tự điền nhật ký thật (viết báo cáo giữa kỳ, đọc tài liệu…), chia lại tuần 1 cho đúng thực tế; bỏ câu L114 hoặc giải thích | 1–2 (người dùng) |

**P1, nên làm nếu còn thời gian (ưu tiên từ trên xuống)**

| # | Việc | Vị trí | Lợi ích | Ước giờ |
|---|---|---|---|---|
| P1-1 | Tái cấu trúc Ch.6: hệ cuối trước, hành trình gọn 1,5 trang, chuyển S13/tiến triển/r08/PSDS-diag/r11 sang phụ lục | [06_ket_qua.md L58–158, L265–271](../../report/final_src/06_ket_qua.md) | −6 đến −8 trang; trục chính rõ | 3–4 |
| P1-2 | Gom mọi hạn chế về một mục "Đe dọa tính hợp lệ" 4 nhóm; Ch.7 dẫn lại; bỏ câu dirty/0,5785 lặp | Ch.3 L80; Ch.4 L153–155; Ch.5 L94, L110, L114; Ch.6 L315–344; Ch.7 L27–29 | Hết rải rác; giọng văn bớt phòng thủ | 2 |
| P1-3 | Rút bảng mã còn 5 mã; đổi "`f1`/`recall_first`" thành "điểm cân bằng/ưu tiên phát hiện"; đưa tên tệp, commit, PAPER_NOTES ra khỏi câu văn vào dòng "Nguồn"; giảm ADR còn khoảng 10 lần nhắc | [04 L17–30](../../report/final_src/04_phuong_phap.md); [06 L62, L64, L76, L98, L218, L235, L273, L293](../../report/final_src/06_ket_qua.md) | Giảm quá tải thuật ngữ | 2 |
| P1-4 | Ch.2: ba mục ngắn tự diễn đạt (cây tăng cường + cross-fitting; bootstrap ghép cặp; giải mã có ràng buộc ngữ pháp) | [02_co_so_ly_thuyet.md](../../report/final_src/02_co_so_ly_thuyet.md) | Nền cho mô hình lõi; trả lời "LBR dùng thuật toán gì" | 3 |
| P1-5 | Ch.5: chuyển "Theo dõi thí nghiệm" (bảng sổ run, r12, 17 run bẩn), chi tiết parity và PowerShell sang phụ lục; chuyển "Mô tả gộp theo lớp" từ Ch.6 sang Ch.5 | [05 L64, L98–104, L114–126](../../report/final_src/05_trien_khai.md); [06 L233–243](../../report/final_src/06_ket_qua.md) | −2 đến −3 trang; Ch.5 đúng vai "hiện thực" | 1 |
| P1-6 | Giảm văn khuôn: gỡ 4 khối "Ba điều… Một, Hai, Ba"; giảm "**không**" in đậm; cắt khoảng nửa số câu "X không phải Y"; viết lại 4 câu mở chương; tách câu trên 60 từ; viết lại đoạn QCVN theo kiểu tóm ý | [06 L106, L214, L231, L273, L332](../../report/final_src/06_ket_qua.md); [04 L69, L95, L110](../../report/final_src/04_phuong_phap.md); [01 L33](../../report/final_src/01_gioi_thieu.md) | Giảm nghi ngờ văn máy và khớp nguồn | 3–4 |
| P1-7 | Ch.1: đổi "Đóng góp dự kiến" thành "Đóng góp"; bảng C1–C6 rút còn 3 cột; thêm 1 câu persona | [01 L77–91](../../report/final_src/01_gioi_thieu.md) | Gọn, đúng giọng báo cáo cuối | 0,75 |
| P1-8 | Ch.7: bảng "Mục tiêu (7 việc) → đạt / đạt một phần / chưa" (ví dụ: field test VN chưa; LLM mô tả không dùng trong ứng dụng; thời gian thực, xác thực chưa) | [07_ket_luan.md L5–13](../../report/final_src/07_ket_luan.md); [01 L55](../../report/final_src/01_gioi_thieu.md) | Mẫu khoa đòi nêu "làm được, chưa làm được" | 0,75 |

**P2, bỏ qua trước 28/11**
- Field test định lượng hoặc mở rộng đối chiếu người đọc: cần dữ liệu và công người; chỉ thêm nếu clip điện thoại đã có sẵn, và khi đó trình bày như kiểm tra định tính.
- Đổi tên chương cho khớp từng chữ với mẫu ("Phân tích yêu cầu", "Thiết kế hệ thống"…): mẫu cho phép tùy đề tài.
- Viết thêm tổng quan văn liệu hệ thống, hoặc so sánh trực tiếp với EPN/LA-RAG: cần chạy mới.
- Tinh chỉnh thêm bảng lịch sử phân loại so với FA2025 hoặc dự án GitHub: đã đủ để trả lời câu hỏi.
- Thêm thí nghiệm hay chỉ số mới cho RAG/mô tả: rủi ro scope creep sát hạn, và mỗi lượt đọc test thêm phải ghi sổ.

### Gaps
- Ước giờ dựa trên khối lượng chữ; chưa tính hai vòng dựng DOCX/PDF và chạy `check_doc_claims`, `check_doc_commands`, `check_doc_links`, `check_midterm_docx` (bản 23/11 dự trù 3–4 giờ cho T0-13).
- Các việc P0-9 thuộc quyền quyết định của người dùng và GVHD; agent không tự đổi trạng thái repo hay điền nhật ký.
