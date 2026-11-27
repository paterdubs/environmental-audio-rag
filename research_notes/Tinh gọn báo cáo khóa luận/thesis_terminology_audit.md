# Kiểm toán thuật ngữ, biệt ngữ và độ dễ đọc của báo cáo khóa luận (report/final_src)

> Phạm vi: chỉ đọc `report/final_src/00_phan_dau.md` … `07_ket_luan.md`, `90_phan_cuoi.md`, các bảng được `@@INCLUDE@@` (`report/final_tables/*.md`, `docs/thesis/tables/*.md`, `report/tables/*.md`), các script sinh hình và bản PDF `report/Khoa_luan_environmental_audio_rag.pdf` (130 trang, đọc bằng `pdftotext`). Không sửa tệp nào trong repo.
> Công cụ: script nháp `audit.py` và `abbr.py` trong scratchpad (C:\Users\patph\AppData\Local\Temp\claude\85ae35366b529c68\b4942c2f-c1bf-4b4b-81ce-f0801cbaaca1\scratchpad\audit.py, …\abbr.py), chạy bằng `.venv/Scripts/python.exe -I`; kết quả thô ở …\scratchpad\audit.json.
> Quy ước trích dẫn: `[06:346](…)` = `report/final_src/06_ket_qua.md`, dòng 346 (một "dòng" trong nguồn Markdown là cả một đoạn văn). Các con số đếm dưới đây do script sinh; số liệu khóa luận thì trích từ nguồn, không tính lại.
> **Lưu ý đo lường:** "từ" được đếm theo khoảng trắng, nên với tiếng Việt mỗi **âm tiết** là một "từ". Câu "40 từ" ở đây ≈ 40 âm tiết. Bộ tách câu là heuristic (tách sau `. ! ?` khi chữ sau viết hoa hoặc là số); câu chứa dấu chấm phẩy dài vẫn tính là một câu, đúng như người đọc cảm nhận.

## 1. Độ dài, tỷ trọng trang và độ dài câu theo chương

### Takeaway
Thân bài (Ch.1–7) dài 98/130 trang PDF và ~32.500 âm tiết; riêng Chương 6 chiếm 34 trang (35% thân bài) và 37% số chữ, Chương 5 chiếm 19 trang. 187/951 câu thân bài (≈20%) dài hơn 40 âm tiết và 43 câu dài hơn 60; Chương 7 — chương người chấm đọc kỹ nhất — có P90 độ dài câu cao nhất (61) và trung bình 28 âm tiết/câu.

### Cited Findings
- Bảng đo (script `audit.py`; trang lấy từ vị trí tiêu đề chương trong PDF: Ch1 tr.19, Ch2 tr.28, Ch3 tr.36, Ch4 tr.44, Ch5 tr.59, Ch6 tr.78, Ch7 tr.112, TLTK tr.117, Phụ lục tr.121, Nhật kí tr.129) — [PDF](../../report/Khoa_luan_environmental_audio_rag.pdf):

| Tệp | Trang PDF | % trang thân bài (98) | Âm tiết văn xuôi | Âm tiết trong bảng | Âm tiết dòng "Nguồn:" | Tổng | Số câu | TB câu | Trung vị | P90 | Dài nhất | > 40 | > 60 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 00 phần đầu (tóm tắt, cảm ơn, mục lục, viết tắt) | 18 | — | 808 | 529 | 0 | 1.337 | 31 | 26,1 | 24 | 41 | 71 | 4 | 1 |
| 01 Giới thiệu | 9 | 9,2% | 2.156 | 852 | 53 | 3.061 | 67 | 31,1 | 27 | 58 | 93 | 14 | 6 |
| 02 Cơ sở lý thuyết | 8 | 8,2% | 2.980 | 0 | 0 | 2.980 | 113 | 25,9 | 23 | 48 | 82 | 18 | 5 |
| 03 Dữ liệu | 8 | 8,2% | 2.166 | 93 | 38 | 2.297 | 82 | 25,4 | 22 | 42 | 74 | 12 | 2 |
| 04 Phương pháp | 15 | 15,3% | 4.764 | 285 | 97 | 5.146 | 176 | 26,1 | 24 | 46 | 126 | 33 | 4 |
| 05 Triển khai | 19 | 19,4% | 3.824 | 1.241 | 178 | 5.243 | 121 | 29,9 | 29 | 53 | 86 | 30 | 4 |
| 06 Kết quả | 34 | 34,7% | 10.159 | 1.596 | 227 | 11.982 | 336 | 28,5 | 26 | 51 | 92 | 66 | 16 |
| 07 Kết luận | 5 | 5,1% | 1.619 | 200 | 20 | 1.839 | 56 | 28,2 | 23,5 | 61 | 93 | 14 | 6 |
| 90 TLTK + phụ lục + nhật kí | 14 | — | 485 | 1.214 | 20 | 1.719 | 18 | 23,6 | 23,5 | 38 | 46 | 2 | 0 |

- Phân bố âm tiết theo mục lớn (đếm văn xuôi, không tính bảng): mục dài nhất là Ch4 "Mô hình phát hiện sự kiện (SED)" 1.242, Ch6 "RQ2" 1.113, Ch6 "Ba chế độ truy hồi" 1.025, Ch5 "Tái lập và kiểm thử" 1.014, Ch6 "LBR và hệ thống cuối" 974, Ch4 "Sinh mô tả" 978, Ch6 "Thảo luận và hạn chế" 919, Ch4 "Giao thức đánh giá" 889 — [04](../../report/final_src/04_phuong_phap.md), [05](../../report/final_src/05_trien_khai.md), [06](../../report/final_src/06_ket_qua.md).
- Câu dài nhất toàn bài 126 âm tiết (một câu liệt kê bốn phép đo phụ) — [04:159](../../report/final_src/04_phuong_phap.md#L159). Hai câu 93 âm tiết ở [01:57](../../report/final_src/01_gioi_thieu.md#L57) (bảy mục tiêu trong một câu) và [07:49](../../report/final_src/07_ket_luan.md#L49) (năm hạn chế trong một câu); câu 92 âm tiết ở [06:346](../../report/final_src/06_ket_qua.md#L346).
- Có 25 hình (`@@CAP:fig:`) và 41 bảng (66 `@@CAP` trừ 25 hình), cộng 66 dòng "Nguồn:" hiển thị trong PDF (đếm bằng `grep -c "Nguồn:"` trên văn bản PDF) — [PDF](../../report/Khoa_luan_environmental_audio_rag.pdf).
- Mật độ phủ định cao: 412 lần "không" trong văn xuôi Ch.1–7 (≈13 lần/1.000 âm tiết), trong đó 45 lần "không phải" — nhiều câu được viết theo kiểu "X, không phải Y; không có nghĩa là Z" (đếm bằng grep trên [final_src](../../report/final_src/)).

### Inferences
- Chương 6 nặng gấp ~3 lần Ch.2/Ch.3 và gần bằng Ch.1–3 cộng lại; đây là chỗ cắt hiệu quả nhất. Chương 5 (19 trang) dài hơn Chương 4 (15 trang) dù chủ yếu là mô tả phần mềm và quy trình tái lập — ứng viên chính để chuyển sang phụ lục.
- Âm tiết/câu trung bình 25–31 là chấp nhận được với văn học thuật tiếng Việt, nhưng P90 ≥ 46 ở Ch.1, 4, 5, 6, 7 cho thấy cứ 10 câu có một câu "bức tường" — thường là câu ghép bằng dấu chấm phẩy, liệt kê số liệu kèm KTC trong ngoặc.
- Mật độ "không/không phải" cao làm văn mang giọng phòng thủ; nhiều câu rào đón có thể gom về một mục "Cách đọc số liệu" thay vì lặp ở mọi đoạn.

### Gaps
- Trang PDF theo chương dựa trên trang bắt đầu của tiêu đề chương; không đo được trang chính xác của từng mục con (pdftotext không giữ cấu trúc tiêu đề). Ngưỡng "câu dài" chuẩn cho văn học thuật tiếng Việt không có trong nguồn đã đọc ở đây (xem ghi chú `vietnamese_plain_writing.md` của nhóm nghiên cứu khác).

## 2. Từ tiếng Anh, viết tắt và mã nội bộ: tần suất, lần xuất hiện đầu, có định nghĩa không

### Takeaway
Văn bản dùng ~110 thuật ngữ/viết tắt tiếng Anh; các mã nội bộ của dự án (B0, V2, V3, f2, S13, T2a/T2b, ADR-00xx, D0–D4, T1–T3, G1–G3, H1–H4, A2/A5, giai đoạn O/P, tầng S/C) xuất hiện 254 lần (riêng nhóm mã hệ SED) cộng 56 lần ADR-xxxx trong văn xuôi, tập trung ở Ch.4 và Ch.6. Nhiều thuật ngữ được dùng trước khi định nghĩa (đặc biệt trong bảng Đóng góp ở Ch.1 và trong Tóm tắt), và có các va chạm tên nguy hiểm: `v2` (công thức SED) vs `V2` (biến thể LBR); `f1` (ứng viên) vs `F1` (chỉ số) vs "điểm f1"; `T2` (tầng khử trùng) vs `T2a/T2b`; chữ "C" vừa là nhánh C, tầng C, vừa là đóng góp C1–C6.

### Cited Findings
**2.1 Thuật ngữ/viết tắt tiếng Anh chính** (đếm trong văn xuôi + chú thích; "Bảng" = số lần trong bảng được include; "DM" = có trong Danh mục từ viết tắt [00:75–118](../../report/final_src/00_phan_dau.md#L75)):

| Thuật ngữ | Văn xuôi | Bảng | Lần đầu | Định nghĩa ở lần đầu? | DM |
|---|---:|---:|---|---|---|
| test | 144 | 31 | [00:7](../../report/final_src/00_phan_dau.md#L7) | Không (tập test không bao giờ được định nghĩa bằng lời; vai trò tập nêu ở [04:157](../../report/final_src/04_phuong_phap.md#L157)) | Không |
| SED | 97 | 34 | [00:5](../../report/final_src/00_phan_dau.md#L5) | Có (cả Abstract, Tóm tắt, [01:7](../../report/final_src/01_gioi_thieu.md#L7)) | Có |
| LBR | 85 | 55 | [00:7](../../report/final_src/00_phan_dau.md#L7) | Có (Tóm tắt [00:19](../../report/final_src/00_phan_dau.md#L19); [01:91](../../report/final_src/01_gioi_thieu.md#L91)) | Có |
| dev | 81 | 11 | [02:11](../../report/final_src/02_co_so_ly_thuyet.md#L11) | Không — "tập dev" chưa từng được giải thích | Không |
| event-F1 | 63 (+13 "Event-F1") | 10 | Tóm tắt [00:19](../../report/final_src/00_phan_dau.md#L19), rồi [01:53](../../report/final_src/01_gioi_thieu.md#L53) | Không; định nghĩa ở [02:21](../../report/final_src/02_co_so_ly_thuyet.md#L21) | Không |
| micro / macro | 58 / 24 | 21 / 12 | [00:7](../../report/final_src/00_phan_dau.md#L7) | Không; định nghĩa ở [02:29](../../report/final_src/02_co_so_ly_thuyet.md#L29) | Không |
| PSDS (PSDS-1/2) | 52 | 23 | [00:7](../../report/final_src/00_phan_dau.md#L7) | Không ở Tóm tắt; giải thích trong ô bảng [01:91](../../report/final_src/01_gioi_thieu.md#L91) và [02:37](../../report/final_src/02_co_so_ly_thuyet.md#L37) | Có |
| hybrid | 43 | 11 | [00:7](../../report/final_src/00_phan_dau.md#L7) (EN); trong văn Việt lần đầu [01:90](../../report/final_src/01_gioi_thieu.md#L90) | Không; "truy hồi kết hợp (lai)" ở [02:69](../../report/final_src/02_co_so_ly_thuyet.md#L69), mã `hybrid` ở [04:136](../../report/final_src/04_phuong_phap.md#L136) | Không |
| seed | 28 | 7 | bảng [01:91](../../report/final_src/01_gioi_thieu.md#L91), văn [03:66](../../report/final_src/03_du_lieu.md#L66) | Không, chưa bao giờ định nghĩa | Không |
| backfill | 27 | 7 | Tóm tắt [00:19](../../report/final_src/00_phan_dau.md#L19) (không dịch, không giải thích) | Giải thích trong ngoặc ở bảng [01:90](../../report/final_src/01_gioi_thieu.md#L90); đủ ở [04:149](../../report/final_src/04_phuong_phap.md#L149) | Không |
| constrained / constrained-cover / unconstrained | 26 / — / 7 | 12 / — / 6 | [00:7](../../report/final_src/00_phan_dau.md#L7) | Mã định nghĩa ở [04:113–116](../../report/final_src/04_phuong_phap.md#L113) | Không |
| fold | 22 | 3 | [04:7](../../report/final_src/04_phuong_phap.md#L7) ("Năm mô hình fold của B0") | Không; ngầm hiểu qua [04:61](../../report/final_src/04_phuong_phap.md#L61) | Không |
| template | 21 | 12 | bảng [01:87](../../report/final_src/01_gioi_thieu.md#L87) ("câu template") | Không; định nghĩa [04:113](../../report/final_src/04_phuong_phap.md#L113) | Không |
| vector_only / structured_only | 20 / 9 | 5 / 3 | bảng [01:90](../../report/final_src/01_gioi_thieu.md#L90) | Không; định nghĩa [04:136](../../report/final_src/04_phuong_phap.md#L136) | Không |
| collar | 20 | 3 | [02:15](../../report/final_src/02_co_so_ly_thuyet.md#L15) | Có ("dung sai (collar)") | Không |
| nDCG@10 | 18 | 3 | [01:67](../../report/final_src/01_gioi_thieu.md#L67) | Có (trong ô bảng RQ) | Có |
| cSEBB | 17 | 6 | [02:45](../../report/final_src/02_co_so_ly_thuyet.md#L45) | Có | Có |
| checkpoint | 16 | 0 | [04:9](../../report/final_src/04_phuong_phap.md#L9) | Không | Không |
| AudioSet | 16 | 9 | [01:65](../../report/final_src/01_gioi_thieu.md#L65) | Mô tả ở [02:51](../../report/final_src/02_co_so_ly_thuyet.md#L51) | Không (tên riêng) |
| ensemble | 14 | 17 | bảng [01:91](../../report/final_src/01_gioi_thieu.md#L91) | Không; định nghĩa [04:59](../../report/final_src/04_phuong_phap.md#L59) | Không |
| commit / git | 14 | 1 | [04:157](../../report/final_src/04_phuong_phap.md#L157) | Không | Không |
| gold / parsed | 12 / 3 | 2 / 0 | [06:261](../../report/final_src/06_ket_qua.md#L261) | Có ("bộ lọc chuẩn (gold)") | Không |
| precision / recall | 12 / 10 | 6 / 5 | [02:21](../../report/final_src/02_co_so_ly_thuyet.md#L21) | Có (công thức) | Không |
| llama.cpp | 11 | 5 | [02:85](../../report/final_src/02_co_so_ly_thuyet.md#L85) | Không giải thích là gì | Không |
| ECHO / CHAIR / TAC / FLAM / BRACE | 10 | 3 | bảng [01:88](../../report/final_src/01_gioi_thieu.md#L88) | Không; ECHO/TAC giải thích ở [02:63](../../report/final_src/02_co_so_ly_thuyet.md#L63) | Không |
| RED / EPN | 9 | 5 | bảng [01:91](../../report/final_src/01_gioi_thieu.md#L91) | Không; giải thích ở [02:47](../../report/final_src/02_co_so_ly_thuyet.md#L47) | Có |
| validation | 9 | 2 | [04:134](../../report/final_src/04_phuong_phap.md#L134) | Không — dùng song song với "dev" cho cùng tập | Không |
| bootstrap / cross-fit | 8 / 5 | 1 / 3 | [02:87–89](../../report/final_src/02_co_so_ly_thuyet.md#L87) | Có | Không |
| OOF | 5 (+33 "ngoài mẫu") | 8 | bảng [01:91](../../report/final_src/01_gioi_thieu.md#L91) | Có (trong ô bảng) | Có |
| LA-RAG | 1 | 1 | bảng [01:90](../../report/final_src/01_gioi_thieu.md#L90) | Không; giải thích ở [02:71](../../report/final_src/02_co_so_ly_thuyet.md#L71) | Không |
| parity | 4 | 1 | [05:158](../../report/final_src/05_trien_khai.md#L158) | Không ("Parity trên CPU" để nguyên tiếng Anh) | Không |
| manifest / artifact | 5 / 3 | 1 / 5 | [05:43](../../report/final_src/05_trien_khai.md#L43), [04:159](../../report/final_src/04_phuong_phap.md#L159) | Không | Không |
| dirty | 4 | 1 | [05:164](../../report/final_src/05_trien_khai.md#L164) | Có ("cây làm việc có thay đổi chưa commit") | Không |
| recall_first | 4 | 5 | bảng [04:32](../../report/final_src/04_phuong_phap.md#L32) | Định nghĩa ở [04:71](../../report/final_src/04_phuong_phap.md#L71) | Không |
| epoch | ~8 | có | bảng [04:24](../../report/final_src/04_phuong_phap.md#L24) | Không | Không |
| in-sample, zero-shot, linear probe, focal loss, mixup, FilterAugment, HistGradientBoosting, GBNF, HNSW, B-tree/GIN, decorator, migration, rollback, xfail | 1–3 mỗi từ | — | ví dụ [06:74](../../report/final_src/06_ket_qua.md#L74), [06:26](../../report/final_src/06_ket_qua.md#L26), [04:71](../../report/final_src/04_phuong_phap.md#L71), [05:96](../../report/final_src/05_trien_khai.md#L96), [05:182](../../report/final_src/05_trien_khai.md#L182) | Phần lớn không | Chỉ HNSW |
- Đã thuần Việt tốt (0 lần trong văn xuôi): rescorer, refiner, posterior, provenance, prompt, corpus (chỉ còn trong tiêu đề bảng `f05_rq3.md` cột "Corpus") — [audit.json](../../report/final_src/), [f05_rq3](../../report/final_tables/f05_rq3.md).

**2.2 Danh mục từ viết tắt** ([00:75–118](../../report/final_src/00_phan_dau.md#L75), 42 mục):
- Có trong danh mục nhưng **không xuất hiện ở thân bài**: `UI` (chỉ ở dòng 118), `ERD` (chỉ ở dòng 96; chú thích hình dùng "Sơ đồ bảng") — [00:96](../../report/final_src/00_phan_dau.md#L96), [05:100](../../report/final_src/05_trien_khai.md#L100). `AAC`, `BLEU`, `RRF`, `TCVN`, `ECE`, `AP` chỉ dùng 1–3 lần.
- Dùng trong thân bài nhưng **thiếu trong danh mục** (đếm bằng `abbr.py`): TP/FP/FN (7/4/4, [02:21](../../report/final_src/02_co_so_ly_thuyet.md#L21)), HTTP (3), MD5 (2), GBNF (2), EQ ("gain/EQ", 3, [04:61](../../report/final_src/04_phuong_phap.md#L61)), SVM ([06:40](../../report/final_src/06_ket_qua.md#L40)), GT ("Trích đúng GT", bảng [f05_rq3](../../report/final_tables/f05_rq3.md)), SD ("SD fold", bảng S13 [docs/thesis/tables/06](../../docs/thesis/tables/06_s13_ranking_test.md)), CV ("Hạng CV", cùng bảng), Nsys/Nref (bảng [f01_sed](../../report/final_tables/f01_sed.md)), AGPL/MIT ([04:57](../../report/final_src/04_phuong_phap.md#L57), [04:97](../../report/final_src/04_phuong_phap.md#L97)), PSD-ROC ([04:179](../../report/final_src/04_phuong_phap.md#L179)), GBM (trong hình s02, đã xem trực tiếp `report/final_figures/s02_lbr.png`), PCM16 (hình s01), GVHD (nhật kí), MAESTRO ([06:195](../../report/final_src/06_ket_qua.md#L195)), GiB ([05:148](../../report/final_src/05_trien_khai.md#L148)), p95, NaN ([05:168](../../report/final_src/05_trien_khai.md#L168)).
- Mục `CI` gánh hai nghĩa (khoảng tin cậy và tích hợp liên tục) và tự thừa nhận "trong bảng ghi CI 95%, văn bản ghi KTC 95%" — [00:84](../../report/final_src/00_phan_dau.md#L84). Mục `EPN` không có dạng đầy đủ ("(tên mạng trong bài của Schmid và cộng sự)") — [00:95](../../report/final_src/00_phan_dau.md#L95).
- Mâu thuẫn dịch: danh mục ghi `RED = Recurrent Event Detection` nhưng Ch.2 gọi RED là "truy hồi sự kiện khả vi" — trong khi cả báo cáo dùng "truy hồi" cho *retrieval* — [00:110](../../report/final_src/00_phan_dau.md#L110), [02:47](../../report/final_src/02_co_so_ly_thuyet.md#L47).

**2.3 Mã nội bộ của dự án** (hội đồng sẽ không hiểu nếu không lật lại bảng mã):
- Nhóm mã hệ SED (B0, V2, V3, f1–f4, g1–g2, T2a/T2b, B-v2/C-v2): 254 lần trong văn xuôi, trong đó B0 76, V3 60, f2 55, V2 43; Ch.6 chiếm 187 lần; lần đầu ở [01:81](../../report/final_src/01_gioi_thieu.md#L81) kèm lời hẹn "giải thích ở bảng mã (Chương 4)"; bảng mã ở [04:19–32](../../report/final_src/04_phuong_phap.md#L19) có 11 dòng mã (A/B/C, v1, v2, T2a/T2b, a–e, f1–f4, g1/g2, S13, B0, LBR V2/V3).
- ADR-xxxx: 56 lần trong văn xuôi (Ch.4: 28), 25 số ADR khác nhau; lần đầu [01:37](../../report/final_src/01_gioi_thieu.md#L37) (có giải thích ADR). Tổng cụm "ADR-00" kể cả dòng nguồn: 66.
- Tên giai đoạn/vòng: "giai đoạn O" dùng ở [02:47](../../report/final_src/02_co_so_ly_thuyet.md#L47) trước khi được định nghĩa ở [04:31](../../report/final_src/04_phuong_phap.md#L31)/[04:61](../../report/final_src/04_phuong_phap.md#L61); "S13" lần đầu trong bảng đóng góp [01:92](../../report/final_src/01_gioi_thieu.md#L92) trước định nghĩa [04:30](../../report/final_src/04_phuong_phap.md#L30); **"S8" không được định nghĩa ở đâu** ([05:168](../../report/final_src/05_trien_khai.md#L168), nhật kí [90:94](../../report/final_src/90_phan_cuoi.md#L94)); "Track 2" trong bảng mã [04:28](../../report/final_src/04_phuong_phap.md#L28) trước khi giải thích [04:52](../../report/final_src/04_phuong_phap.md#L52); "tầng S / tầng C" chỉ ở [04:61](../../report/final_src/04_phuong_phap.md#L61), [04:71](../../report/final_src/04_phuong_phap.md#L71); "P1×3" trong bảng [f10](../../report/final_tables/f10_lbr_context.md) không được giải thích.
- Mã cổng/kiểm thử: D0–D4 (Ch.3, 21 lần), T1–T3, G1–G3 (G3 7 lần), H1–H4 ([06:166](../../report/final_src/06_ket_qua.md#L166)), A2/A5 ([06:335](../../report/final_src/06_ket_qua.md#L335)) — tổng 44 lần.
- Tên tệp, run ID, tên script trong **văn xuôi** (không tính dòng nguồn): `per_class_metrics_datasec_20260923` [06:20](../../report/final_src/06_ket_qua.md#L20); `lbr_diagnosis` [06:72](../../report/final_src/06_ket_qua.md#L72); `git.dirty = true` [06:74](../../report/final_src/06_ket_qua.md#L74); `sed_ensemble_B0_final_test_20261014T085016Z_eval_phase_lbr_annotated.md` [06:160](../../report/final_src/06_ket_qua.md#L160); `scripts.report_checker_sensitivity` [06:230](../../report/final_src/06_ket_qua.md#L230); `scripts.report_caption_vs_gt` [06:235](../../report/final_src/06_ket_qua.md#L235); `grouped_captions_dev_20261124` [06:247](../../report/final_src/06_ket_qua.md#L247); `scripts.report_rq3_failures` [06:287](../../report/final_src/06_ket_qua.md#L287); `retrieval_backfill_test_20261124` [06:307](../../report/final_src/06_ket_qua.md#L307); `docs/evaluation_protocol.md §3.3` [02:37](../../report/final_src/02_co_so_ly_thuyet.md#L37); `docs/decisions/` [04:3](../../report/final_src/04_phuong_phap.md#L3); `logs/history.json` [04:63](../../report/final_src/04_phuong_phap.md#L63); `requirements-*.txt, package.json, docker-compose.yml` [05:33](../../report/final_src/05_trien_khai.md#L33); `docs/REPRODUCE.md` [05:166](../../report/final_src/05_trien_khai.md#L166); `scripts.freeze_artifacts`, `docs/measurements/artifact_freeze_20261111.md` [90:25](../../report/final_src/90_phan_cuoi.md#L25); băm hệ lớp `67ca8a8c…` [03:17](../../report/final_src/03_du_lieu.md#L17); tham số thư viện `alpha_st`, `geomspace(1e-5, 0,99; 48)` [04:179](../../report/final_src/04_phuong_phap.md#L179), [06:166](../../report/final_src/06_ket_qua.md#L166).
- Tên lớp dạng `snake_case` tiếng Anh xuất hiện dày trong văn (ví dụ `vehicle_pass_by` 10, `workshop` 9, `birds` 9, `propeller_aircrafts` 8, `crows_seagulls_magpies` 6, `dog_barkings_and_howlings` 6) — quy ước "không dịch class_id" của dự án, nhưng trong văn xuôi người đọc không có tên tiếng Việt kèm theo — ví dụ [06:138](../../report/final_src/06_ket_qua.md#L138), [06:160](../../report/final_src/06_ket_qua.md#L160).

**2.4 Va chạm tên (dễ bị bắt lỗi nhất):**
- `v1`/`v2` (công thức SED, chữ thường) và `V1`/`V2`/`V3` (biến thể LBR, chữ hoa) cùng xuất hiện trong một chương — [04:24–32](../../report/final_src/04_phuong_phap.md#L24), bảng [f10](../../report/final_tables/f10_lbr_context.md) ("LBR V1").
- `f1` (ứng viên BEATs ×3), `F1` (chỉ số) và "điểm f1" (điểm vận hành tối đa F1 của LBR) — [04:28](../../report/final_src/04_phuong_phap.md#L28), [06:92](../../report/final_src/06_ket_qua.md#L92), [06:114](../../report/final_src/06_ket_qua.md#L114), bảng [f01_sed](../../report/final_tables/f01_sed.md) ("LBR V2, điểm f1").
- `T1/T2/T3` (ba tầng khử trùng, [03:56](../../report/final_src/03_du_lieu.md#L56)) và `T2a/T2b` (bộ mã hóa Track 2, [04:26](../../report/final_src/04_phuong_phap.md#L26)).
- "C": nhánh C (RQ1), "tầng C" (vòng chọn ngoài mẫu), đóng góp C1–C6; "B": nhánh B vs hệ B0 vs B-v2.
- "tầng" dùng cho 5 nghĩa: tầng khử trùng T1–T3, tầng chọn S/C, tầng 1/2 của backfill [06:299](../../report/final_src/06_ket_qua.md#L299), "tầng LBR" [05:140](../../report/final_src/05_trien_khai.md#L140), "hai tầng sau" (bộ sinh và truy hồi) [07:5](../../report/final_src/07_ket_luan.md#L5).
- "nhánh" dùng cho A/B/C và cho cách sinh ("nhánh constrained-cover") — [07:13](../../report/final_src/07_ket_luan.md#L13).

### Inferences
- Mã nội bộ là nguồn khó đọc lớn nhất của Ch.6: trung bình mỗi trang Ch.6 có ~5,5 mã hệ SED. Có thể giảm xuống 4 tên dài có nghĩa (ví dụ "mốc S13 (f2)" → "hệ mốc", "B0" → "hệ phát hiện cơ sở", "LBR V2" → "LBR (cấu hình chấm điểm)", "LBR V3" → "LBR (cấu hình ưu tiên phát hiện)") và dồn mọi mã khác (a–e, f1/f3/f4, g1/g2, T2a, S8, P1×3, tầng S/C, H1–H4, A2/A5) xuống phụ lục.
- Mọi tên tệp/run/script trong văn xuôi có thể chuyển vào cột "Nguồn" của một bảng phụ lục duy nhất; trong thân bài chỉ cần "(Phụ lục B, mục X)".
- Các thuật ngữ cốt lõi nên được định nghĩa một lần ở Ch.1 hoặc đầu Ch.2 và thêm vào danh mục: tập huấn luyện/phát triển/kiểm tra (train/dev/test), seed, fold, ensemble, checkpoint, epoch, event-F1 micro/macro, backfill, hybrid/vector_only/structured_only, template/constrained/unconstrained.

### Gaps
- Không kiểm được dạng đầy đủ chính xác của RED/EPN và cSEBB trong bài gốc (không đọc lại PDF bài báo); chỉ ghi nhận mâu thuẫn nội bộ giữa danh mục và Ch.2. Đếm "Bảng" có thể thiếu các bảng `report/tables/m0x` không phải nguồn final.

## 3. Thuật ngữ không nhất quán (một khái niệm, nhiều cách gọi)

### Takeaway
Phần văn xuôi đã Việt hóa khá đều (mô tả 137 vs caption 11; sự kiện 215 vs event 8), nhưng **các bảng sinh tự động vẫn dùng tiếng Anh và dấu thập phân kiểu Anh**, và một số cặp khái niệm cốt lõi (dev/validation, hybrid/kết hợp/lai, template/mẫu cố định/mô tả mẫu, constrained/có ràng buộc/LLM ràng buộc, KTC/CI) được gọi tới 3 cách — đúng loại lỗi hội đồng "bắt từng chữ".

### Cited Findings
Đếm trong văn xuôi + chú thích (không tính bảng), toàn bộ final_src:

| Khái niệm | Các cách gọi (số lần) | Ghi chú |
|---|---|---|
| Caption | mô tả 137; caption 11 (5 ở Abstract EN; Ch.2: 1, Ch.5: 1, Ch.6: 4) | Bảng sổ test dùng "Caption (RQ2)", "Caption: lớp gộp / wiring" — [f07_ledger](../../report/final_tables/f07_ledger.md) |
| Retrieval | truy hồi 54; truy vấn 36; retrieval 7 (5 ở Abstract); truy xuất 1 ([02:71](../../report/final_src/02_co_so_ly_thuyet.md#L71)); tìm kiếm 0 | "truy hồi" còn dùng cho RED [02:47](../../report/final_src/02_co_so_ly_thuyet.md#L47); bảng ghi "Retrieval (RQ3)" |
| Tập phát triển | dev 81; validation 9; không có tên Việt | Bảng chia tập ghi cột "Validation" ([docs/thesis/tables/01](../../docs/thesis/tables/01_data_split.md)); "kho validation" [04:134](../../report/final_src/04_phuong_phap.md#L134), [06:317](../../report/final_src/06_ket_qua.md#L317), [07:57](../../report/final_src/07_ket_luan.md#L57) |
| Bản ghi | bản ghi 145; đoạn 51; tệp 73; recording 6; clip 3 | "đoạn" vừa là clip DataSEC vừa là "F1 theo đoạn" (segment) vừa là "đoạn thời gian" |
| Hybrid | hybrid 43; (truy hồi) kết hợp 9; lai 3 | Tóm tắt dùng "truy hồi kết hợp", Ch.6/7 dùng "hybrid" |
| Vector_only | vector_only 20; "chỉ (xếp hạng) ngữ nghĩa" 6 | |
| Structured_only | structured_only/structured 9; "chỉ lọc" 3 | |
| Template | template 21; "mô tả mẫu" 4; "mẫu cố định" 1 | Hình RQ2 gọi "mẫu cố định", "LLM ràng buộc + phủ" — bộ tên thứ ba — [06:210](../../report/final_src/06_ket_qua.md#L210) |
| Constrained | constrained 16; có ràng buộc 8; LLM ràng buộc 2 | |
| Unconstrained | unconstrained 7; viết tự do 8; LLM tự do 3 | Bảng RQ2 ghi "Unconstrained — bỏ sót" [f04_rq2](../../report/final_tables/f04_rq2.md) |
| Out-of-fold | (dự đoán) ngoài mẫu 33; OOF 5; out-of-fold 1 | OOF chỉ dùng ở Ch.4 |
| Ensemble | ensemble 15; "gộp nhiều mô hình" 1 (tiêu đề [04:59](../../report/final_src/04_phuong_phap.md#L59)) | |
| Run | lần chạy 25; lượt 17; run 5 | Bảng: "n run", "Run / tệp", "run phụ" |
| Khoảng tin cậy | khoảng tin cậy 30; KTC 4; CI 3 (văn) + 8 (bảng: "CI 95%", "95% CI micro", "Δ micro [95% CI]") | Danh mục tự thừa nhận hai cách ghi [00:84](../../report/final_src/00_phan_dau.md#L84) |
| Onset/offset | onset 12; offset 5; (thời điểm) bắt đầu 18; kết thúc 9; biên đầu/biên cuối 4 | Hình s02 ghi "Δonset, Δoffset" |
| Segment F1 | F1 theo đoạn (văn); segment-F1 (Abstract [00:7](../../report/final_src/00_phan_dau.md#L7)); "Segment-F1 1 s" (bảng [f02](../../report/final_tables/f02_intersection.md)) | |
| Metric | "chỉ số" (phổ biến); "metric" 3 ([02:15](../../report/final_src/02_co_so_ly_thuyet.md#L15)); "thước" 12 ("thước ứng dụng", "thước giao nhau", "thước đo") | "thước" là cách gọi lạ, chỉ có trong báo cáo này |
| Calibration | hiệu chuẩn 6 (ECE, ngưỡng, máy đo); định cỡ 3 ("định cỡ độ khó") | Mục "Event-F1 khoảng 0,30 là cao hay thấp?" dùng bảng tên `tbl:calibration` nhưng nghĩa là "định cỡ" |
| Đóng băng | khóa 46; đóng băng 13; freeze 3 (phụ lục) | |
| Kho | kho sự kiện 9; event store 4 (2 ở Abstract, 2 ở [07:27](../../report/final_src/07_ket_luan.md#L27)); "Corpus" (cột bảng f05) | |
| Nhãn gốc | nhãn gốc 30; tham chiếu 22; GT 1 (bảng) | |
| Ảo giác | ảo giác 36; bịa 8; hallucination 5 | |
| Parser | bộ phân tích câu hỏi 12; parser 2 (Ch.6) | Bảng "Bảng đánh giá parser L2" (tiêu đề tệp nguồn), cột "Parse success/Exact match/Predicate accuracy" — [docs/thesis/tables/10](../../docs/thesis/tables/10_parser_l2.md) |
| Tinh chỉnh | "tinh chỉnh biên/bộ tinh chỉnh" (LBR) 12; "tinh chỉnh toàn bộ" (fine-tune) 3 | Cùng một từ cho hai kỹ thuật khác nhau |
| Nhật ký | "NHẬT KÍ LÀM VIỆC" [90:81](../../report/final_src/90_phan_cuoi.md#L81) vs "Nhật ký huấn luyện" [04:67](../../report/final_src/04_phuong_phap.md#L67) | Chính tả không thống nhất |

- **Dấu thập phân:** văn xuôi dùng dấu phẩy và chấm phẩy trong KTC ("0,2965 [0,2293; 0,3603]"), nhưng hầu hết bảng include dùng dấu chấm và dấu phẩy ("0.2965 [0.2293, 0.3603]") — bảng [f01_sed](../../report/final_tables/f01_sed.md), [f02](../../report/final_tables/f02_intersection.md), [f04_rq2](../../report/final_tables/f04_rq2.md), [f05_rq3](../../report/final_tables/f05_rq3.md), [f10](../../report/final_tables/f10_lbr_context.md), [docs/thesis/tables/03_rq1](../../docs/thesis/tables/03_rq1.md), [06_s13](../../docs/thesis/tables/06_s13_ranking_test.md), [04_sed_progress](../../docs/thesis/tables/04_sed_progress.md), [10_parser](../../docs/thesis/tables/10_parser_l2.md), [report/tables/m01](../../report/tables/m01_classifier.md); riêng [f00_key_results](../../report/final_tables/f00_key_results.md) và bảng viết tay [06:32–40](../../report/final_src/06_ket_qua.md#L32) dùng dấu phẩy. Bảng RQ1 còn dùng dấu gạch nối "-0.0071" thay cho dấu trừ "−".
- **Tiêu đề cột/giá trị tiếng Anh trong bảng hiển thị:** "Hạng CV, Model, Dev micro, SD fold, csebb, theta" ([06_s13](../../docs/thesis/tables/06_s13_ranking_test.md)); "Parse success, Exact match, Class precision, Class recall, Predicate accuracy, n temporal, template, paraphrase" ([10_parser](../../docs/thesis/tables/10_parser_l2.md)); "Dataset, File, Validation, Nhóm leakage, SHA split" ([01_data_split](../../docs/thesis/tables/01_data_split.md)); "Cặp ứng viên T1/T2/T3, Nhóm duplicate, xuyên dataset, Clip pretraining, PASS, Audit 3 tầng" ([02_leakage](../../docs/thesis/tables/02_leakage_d3_d4.md)); "Corpus, structured/en, vector/en, hybrid/en, Trích đúng GT" ([f05_rq3](../../report/final_tables/f05_rq3.md)); "Nsys/Nref, Δ micro so B0" ([f01_sed](../../report/final_tables/f01_sed.md)); "Caption: lớp gộp / wiring, Retrieval (RQ3), Ablation, Parity phục vụ, git dirty" ([f07_ledger](../../report/final_tables/f07_ledger.md)); "Served B0 system (ADR-0042), B0 OOF h5 (… postproc source), tree" ([f08_freeze](../../report/final_tables/f08_freeze.md)); "ECE sau temperature scaling, n_test" ([m01](../../report/tables/m01_classifier.md)).
- Hình hộp–mũi tên cũng trộn Anh–Việt: s01 có "Frame-MobileNet × 5 fold", "template gộp theo lớp", "Mô tả EN / VI", "PCM16", "B-tree, GIN, HNSW"; s02 có "GBM", "Cross-fit lồng nhau (5 fold …)", "Δonset, Δoffset"; m04 có "xuyên dataset", "T1/T2/T3" (xem trực tiếp các tệp PNG `report/final_figures/s01_data_flow.png`, `s02_lbr.png`, `report/figures/m04_data_pipeline.png`).

### Inferences
- Sửa bảng ở script sinh (`scripts/build_final_tables.py`, `scripts/build_thesis_tables.py`, `scripts/build_midterm_tables.py`) có lợi gấp nhiều lần sửa tay: một lần đổi định dạng số và tên cột sẽ áp cho ~15 bảng.
- Cần một "bảng thuật ngữ thống nhất" (một tên Việt cho mỗi khái niệm, tên Anh chỉ ở lần đầu trong ngoặc), áp cho cả văn, bảng và hình. Đề xuất: tập huấn luyện/phát triển/kiểm tra; mô tả; truy hồi; lần chạy; kết hợp (hybrid); chỉ ngữ nghĩa (vector_only); chỉ lọc (structured_only); mô tả theo mẫu (template); LLM có ràng buộc; LLM viết tự do; dự đoán ngoài mẫu; khoảng tin cậy (KTC) — và bỏ "thước".

### Gaps
- Không mở được DOCX để kiểm tra phông/định dạng số trong ô bảng sau khi dựng; nhận định về dấu thập phân dựa trên nguồn Markdown của bảng (bộ dựng `expand_include` chỉ chép nguyên hàng bảng, không đổi dấu — [scripts/report_docx/markdown.py:108–130](../../scripts/report_docx/markdown.py#L108)).

## 4. Từ ngữ khẳng định quá mức hoặc rủi ro

### Takeaway
Bản hiện tại đã gỡ gần hết "lần đầu" (các lần còn lại đều mang nghĩa nội bộ hoặc đã phủ định) và rào đón kỹ con số "0 ảo giác". Rủi ro còn lại nằm ở các khẳng định tuyệt đối về kiến trúc ("bảo đảm", "tuyệt đối", "luôn đúng", "không bao giờ"), ở câu luận điểm lặp 4 lần nói "không thêm lỗi" trong khi bộ phân tích câu hỏi có lỗi đo được, và ở một mâu thuẫn nội tại về việc "không bao giờ" dùng test để chọn.

### Cited Findings
Đếm trong văn xuôi + chú thích (regex, không phân biệt hoa thường):

| Từ | Số lần | Vị trí đáng chú ý |
|---|---:|---|
| lần đầu / đầu tiên | 6 | Đều vô hại: [02:99](../../report/final_src/02_co_so_ly_thuyet.md#L99) ("không khẳng định… baseline đầu tiên"), [06:104](../../report/final_src/06_ket_qua.md#L104) ("trường hợp đầu tiên cSEBB thắng"), [04:116](../../report/final_src/04_phuong_phap.md#L116), [04:120](../../report/final_src/04_phuong_phap.md#L120), [05:140](../../report/final_src/05_trien_khai.md#L140) (nghĩa kỹ thuật) |
| tốt nhất / mạnh nhất | 8 / 4 | "bằng chứng tốt nhất của đề tài" [07:27](../../report/final_src/07_ket_luan.md#L27); "LBR trở thành kết quả định lượng mạnh nhất" [06:64](../../report/final_src/06_ket_qua.md#L64); "hệ tốt nhất có event-F1 micro chỉ 0,2965" [06:231](../../report/final_src/06_ket_qua.md#L231); rào tốt: "không phải hệ được chứng minh là tốt nhất" [06:94](../../report/final_src/06_ket_qua.md#L94) |
| bảo đảm / đảm bảo | 17 | **Rủi ro:** "bộ lọc cứng bảo đảm đúng ràng buộc tuyệt đối (1,000…)" [06:346](../../report/final_src/06_ket_qua.md#L346); "Ràng buộc ngữ pháp và bộ lọc cứng bảo đảm hai tầng sau không thêm lỗi ngoài lỗi của SED" [07:5](../../report/final_src/07_ket_luan.md#L5); "Quy trình bảo đảm mọi tệp đều có nguồn gốc" [03:3](../../report/final_src/03_du_lieu.md#L3) |
| tuyệt đối | 9 | "đúng ràng buộc tuyệt đối" [06:346](../../report/final_src/06_ket_qua.md#L346); các lần khác là nghĩa kỹ thuật (thời gian tuyệt đối, số tuyệt đối) |
| luôn | 9 | "bộ lọc cứng luôn đúng điều kiện" [01:98](../../report/final_src/01_gioi_thieu.md#L98) và bảng kết quả chính "Lọc cứng luôn đúng điều kiện" [f00](../../report/final_tables/f00_key_results.md); "điểm chọn luôn cao hơn điểm test" (5 điểm dữ liệu) [06:148](../../report/final_src/06_ket_qua.md#L148) |
| không bao giờ | 7 | **Mâu thuẫn:** "số trên test… không bao giờ dùng để chọn lại" [06:8](../../report/final_src/06_ket_qua.md#L8) đặt cạnh "Có bốn chỗ tái sử dụng thích nghi" (A2/A5 và backfill có ý tưởng từ test) [06:335](../../report/final_src/06_ket_qua.md#L335), [04:149](../../report/final_src/04_phuong_phap.md#L149); "để độ tương đồng ngữ nghĩa không bao giờ ghi đè bộ lọc" [02:69](../../report/final_src/02_co_so_ly_thuyet.md#L69) trong khi backfill nối thêm kết quả không thỏa bộ lọc [04:149](../../report/final_src/04_phuong_phap.md#L149); "không bao giờ có tệp âm thanh không có dòng bản ghi" [05:78](../../report/final_src/05_trien_khai.md#L78); "demo không bao giờ phơi bày dữ liệu test" [05:156](../../report/final_src/05_trien_khai.md#L156) |
| chứng minh / minh chứng | 4 | "Cổng này được chứng minh không đạt rỗng" (dựa trên một phép thử ngược) [03:72](../../report/final_src/03_du_lieu.md#L72); "minh chứng trực tiếp cho sai số khi chọn mô hình trên tập dev nhỏ" (một vòng xếp hạng) [06:92](../../report/final_src/06_ket_qua.md#L92) |
| 0 ảo giác / không còn ảo giác / không vi phạm | 5 | Đều có vế "so với danh sách sự kiện" ([00:19](../../report/final_src/00_phan_dau.md#L19), [01:98](../../report/final_src/01_gioi_thieu.md#L98), [06:226](../../report/final_src/06_ket_qua.md#L226)); bảng mục tiêu ghi gọn "Không vi phạm so với dự đoán" [07:41](../../report/final_src/07_ket_luan.md#L41) |
| có ý nghĩa (thống kê) | 10 | Tóm tắt "thấp hơn có ý nghĩa" [00:19](../../report/final_src/00_phan_dau.md#L19) — trong khi [06:336](../../report/final_src/06_ket_qua.md#L336) thừa nhận KTC không hiệu chỉnh so sánh bội |
| hơn hẳn / cao hơn hẳn | 3 | "Riêng LBR V3 cao hơn hẳn" [06:269](../../report/final_src/06_ket_qua.md#L269) (rồi tự nói là hiệu ứng độ phủ) |
| mọi | 55 | Ví dụ "Mọi con số trong chương do script tính" [03:3](../../report/final_src/03_du_lieu.md#L3) và "Mọi hình và bảng… đều do script đọc thẳng" [05:3](../../report/final_src/05_trien_khai.md#L3), trong khi [05:166](../../report/final_src/05_trien_khai.md#L166) nói số trong văn xuôi được "đối chiếu tay" |
| chưa ai | 1 | "không khẳng định chưa ai đo" [02:63](../../report/final_src/02_co_so_ly_thuyet.md#L63) (đã phủ định, an toàn) |

- Câu luận điểm "ràng buộc ngữ pháp và bộ lọc cứng không thêm lỗi ngoài lỗi của SED" ([01:100](../../report/final_src/01_gioi_thieu.md#L100), [06:346](../../report/final_src/06_ket_qua.md#L346), [07:5](../../report/final_src/07_ket_luan.md#L5), Tóm tắt [00:19](../../report/final_src/00_phan_dau.md#L19)) bỏ qua hai nguồn lỗi đã đo: bộ phân tích câu hỏi đúng hoàn toàn chỉ 0,855 (mẫu) và độ chính xác điều kiện thời gian 0,767 — [06:321](../../report/final_src/06_ket_qua.md#L321); bộ chấm ảo giác chỉ bắt 62% nguồn âm ngoài taxonomy — [06:230](../../report/final_src/06_ket_qua.md#L230).
- "Độ đúng bộ lọc 1,000" được nhắc 14 lần (Ch.1, 3, 4, 5, 6, 7) dù chính báo cáo nói nó là yêu cầu kiến trúc ("thấp hơn là lỗi kiến trúc") và truy vấn rỗng được tính bằng 1 — [04:177](../../report/final_src/04_phuong_phap.md#L177), [06:317](../../report/final_src/06_ket_qua.md#L317).

### Inferences
- Hội đồng có thể hỏi: "Nếu bộ lọc luôn đúng 1,000 theo định nghĩa thì đó có phải là kết quả không?" và "Luận điểm nói không thêm lỗi, nhưng parser sai 14,5%?". Nên (a) viết luận điểm thành "bộ sinh có ràng buộc không tự thêm nguồn âm ngoài danh sách sự kiện; bộ lọc cứng chỉ trả bản ghi thỏa điều kiện trên sự kiện đã lưu", (b) gọi 1,000 là "kiểm tra đúng thiết kế", không phải kết quả.
- Thay "bảo đảm/luôn/tuyệt đối/không bao giờ" bằng mô tả hành vi đo được ("trong mọi lần đo, …", "được thiết kế để …, và kiểm thử X xác nhận").
- Sửa câu [06:8](../../report/final_src/06_ket_qua.md#L8) thành "không dùng số test để chọn lại cấu hình đã khóa" để khớp với phần thừa nhận tái sử dụng thích nghi.

### Gaps
- Không kiểm theo ngữ cảnh toàn bộ 55 lần "mọi"; chỉ nêu các ví dụ có rủi ro rõ.

## 5. Bình luận quy trình (meta-commentary) và chi tiết nguồn gốc không giúp người đọc

### Takeaway
Ngoài 66 dòng "Nguồn:" (158 lần nhắc tệp `docs/…`/`.json`/measurement và 42 lần nhắc script nằm trong các dòng này), văn xuôi còn ~180 lần nhắc chi tiết quy trình (56 ADR-xxxx, 32 commit/git/dirty, 26 đóng băng/artifact/manifest, 19 script, 17 "ghi trước", 13 tệp đo, 11 sổ test). Phần lớn dồn ở Ch.5 "Tái lập và kiểm thử" (1.014 âm tiết + 2 bảng + 1 hình) và các đoạn lịch sử trong Ch.6 — đây là các ứng viên chuyển sang phụ lục.

### Cited Findings
- Đếm (văn xuôi / dòng nguồn): script–`.py` 19 / 42; commit–git–cây làm việc–dirty 32 / 0 (Ch.5: 15, Ch.6: 13); sổ test–chạm test 11; đóng băng–freeze–artifact–manifest 26 / 14; `docs/`–`.json`–tệp đo 13 / 158; ADR-xxxx 56 / 9; run ID 1 / 9; "ghi trước" 17 (Ch.6: 11); "thăm dò/script nháp" 6; ngày dd/mm/2026 trong văn 6 — đếm bằng `audit.py` trên [final_src](../../report/final_src/).
- Đoạn thuần quy trình trong thân bài (ví dụ):
  - Liệt kê 17 lần chạy "cây bẩn" theo ngày và lý do [05:168](../../report/final_src/05_trien_khai.md#L168); bảng sổ đăng ký 218 lần chạy + hình phân bố theo ngày [05:170–180](../../report/final_src/05_trien_khai.md#L170).
  - Ba bộ kiểm tài liệu, `docs/REPRODUCE.md`, script dựng DOCX và kiểm định dạng [05:166](../../report/final_src/05_trien_khai.md#L166); số mục pytest 1261/xfail [05:182](../../report/final_src/05_trien_khai.md#L182); bảng "Khối lượng thực hiện" (456 commit, 58.916 dòng Python…) [05:186–192](../../report/final_src/05_trien_khai.md#L186), [f12](../../report/final_tables/f12_workload.md).
  - "Phép đo chạy khi cây làm việc chưa sạch vì chính script đo chưa được commit lúc chạy" [05:148](../../report/final_src/05_trien_khai.md#L148).
  - "hai tệp đo được sinh khi cây làm việc có thay đổi chưa commit (`git.dirty = true`)" [06:74](../../report/final_src/06_ket_qua.md#L74).
  - Sự cố llama.cpp hết bộ nhớ GPU và tính tất định theo chuỗi yêu cầu [06:255](../../report/final_src/06_ket_qua.md#L255).
  - "hai số này đo bằng script nháp trước khi có ADR-0045 và chưa có artifact sinh bằng script của repo" [06:116](../../report/final_src/06_ket_qua.md#L116).
  - "Lượt chạy test này chỉ đọc danh sách đã lưu và được ghi vào sổ test như một lượt riêng" [06:315](../../report/final_src/06_ket_qua.md#L315).
  - "lựa chọn được commit trước khi sinh dự đoán test… (mã commit được ghi trong tệp đo của vòng chọn)" [06:86](../../report/final_src/06_ket_qua.md#L86); "lựa chọn trên dev được commit vào git trước khi sinh dự đoán test bằng một đường riêng, và một tùy chọn kiểm chứng đường này tái tạo trùng từng bit" [04:157](../../report/final_src/04_phuong_phap.md#L157).
  - Lịch sử quy ước: "Từ 26/09/2026 macro được ghi trước… Trước ngày này, số chính của dự án là micro" [02:35](../../report/final_src/02_co_so_ly_thuyet.md#L35).
  - Lý do tự cài cSEBB vì giấy phép AGPL [04:97](../../report/final_src/04_phuong_phap.md#L97); giấy phép MIT của BEATs [04:57](../../report/final_src/04_phuong_phap.md#L57).
  - Phiên bản đọc từ `requirements-*.txt`, `package.json`, `docker-compose.yml` [05:33](../../report/final_src/05_trien_khai.md#L33); "decorator", "migration SQL" [05:96–104](../../report/final_src/05_trien_khai.md#L96).
- Dòng "Nguồn:" dưới hình/bảng có đường dẫn nội bộ dài, ví dụ "Nguồn: logs/history.json của năm run thành viên trong ml/runs/sed_served_B0_20261107T175659Z/manifest.json" [04:69](../../report/final_src/04_phuong_phap.md#L69); "ml/runs/sed_ensemble_s13_f2_20260929T045053Z/captions/constrained_cover_dev.jsonl" [04:130](../../report/final_src/04_phuong_phap.md#L130); "Bảng sinh tự động bởi script, không sửa tay" được bộ dựng tự thêm vào mọi bảng include ([scripts/report_docx/markdown.py:121](../../scripts/report_docx/markdown.py#L121)).
- Mục/đoạn có thể chuyển phụ lục (âm tiết văn xuôi đo được): Ch.5 "Tái lập và kiểm thử" 1.014 + bảng f14, f12, hình r12; Ch.6 "Tái sử dụng tập test…" 589; Ch.6 "PSDS và lưới ngưỡng" 283 + bảng f06; Ch.6 "Vòng chọn S13 và hệ f2" 559 + 2 bảng; đoạn "Về cSEBB" [06:104](../../report/final_src/06_ket_qua.md#L104); đoạn parity [06:327](../../report/final_src/06_ket_qua.md#L327) (trùng [05:158](../../report/final_src/05_trien_khai.md#L158)); đoạn sự cố llama.cpp [06:255](../../report/final_src/06_ket_qua.md#L255); bảng mã 11 dòng [04:19–32](../../report/final_src/04_phuong_phap.md#L19); bảng API [05:106–110](../../report/final_src/05_trien_khai.md#L106) và bảng công nghệ (517 âm tiết trong ô bảng, [f15](../../report/final_tables/f15_tech_stack.md)).

### Inferences
- Nếu chuyển các khối trên sang một "Phụ lục: Quy trình tái lập và nhật ký thí nghiệm", thân bài giảm ước tính ~3.500–4.500 âm tiết (~10–12 trang), Ch.5 còn ~12 trang, Ch.6 còn ~26 trang.
- Thay mọi dòng "Nguồn: <đường dẫn>" trong thân bài bằng mã nguồn ngắn ("Nguồn: kết quả đo N, Phụ lục B") và đưa bảng tra mã → đường dẫn vào phụ lục; vẫn giữ được tính truy nguồn mà hội đồng không phải đọc đường dẫn.
- Giữ trong thân bài một đoạn ngắn về nguyên tắc chống "chọn theo test" (chọn trên dev → khóa → đo test một lần) vì đó là lập luận phương pháp; còn commit, cờ dirty, sổ test, SHA-256 là bằng chứng → phụ lục.

### Gaps
- Ước tính số trang tiết kiệm dựa trên tỷ lệ âm tiết/trang trung bình của từng chương (≈330–350 âm tiết/trang), không dựng lại DOCX để đo.

## 6. Nội dung lặp lại giữa các chương

### Takeaway
Câu luận điểm xuất hiện nguyên văn hoặc gần nguyên văn ở 4 nơi (Tóm tắt, Ch.1, Ch.6, Ch.7) cộng bảng kết quả chính; các con số trụ cột lặp nhiều lần (0,2965: 13 lần; 1,000: 14; +0,1159: 8; 0,1806: 7; 0,5785: 6); ba khối nội dung được giải thích gần như trùng ở hai–ba chương (vai trò thật của các cách sinh; mô tả gộp theo lớp; parity) và danh sách hạn chế được nhắc ở ít nhất 5 chỗ.

### Cited Findings
- Câu luận điểm: [00:19](../../report/final_src/00_phan_dau.md#L19), [01:100](../../report/final_src/01_gioi_thieu.md#L100), [06:346](../../report/final_src/06_ket_qua.md#L346), [07:5](../../report/final_src/07_ket_luan.md#L5); cùng mạch ở [06:10](../../report/final_src/06_ket_qua.md#L10) và bảng [f00](../../report/final_tables/f00_key_results.md). Cụm 9 âm tiết "trong hệ thống này độ đúng của mô tả" trùng ở 01:100, 06:346, 07:5 (dò bằng shingle 9 âm tiết trong `audit.py`; 166 shingle trùng giữa các chương).
- "ứng dụng không dùng mô hình ngôn ngữ để viết mô tả": [04:118](../../report/final_src/04_phuong_phap.md#L118), [06:226](../../report/final_src/06_ket_qua.md#L226), [07:27](../../report/final_src/07_ket_luan.md#L27), và bảng đóng góp [01:87](../../report/final_src/01_gioi_thieu.md#L87). Đoạn "Vai trò thật của từng cách sinh" [04:118](../../report/final_src/04_phuong_phap.md#L118) và "Cách đọc đúng RQ2 cần thừa nhận ba điều" [06:226](../../report/final_src/06_ket_qua.md#L226) có cùng ba ý và cùng số BLEU-4 0,358 / CIDEr 3,60.
- Mô tả gộp theo lớp, cùng ví dụ "Phát hiện: tiếng chim, 2 lần, 0,0–20,0 giây." và nhãn "Có thể có (độ tin cậy thấp)": [04:120](../../report/final_src/04_phuong_phap.md#L120), [05:114](../../report/final_src/05_trien_khai.md#L114), [06:247](../../report/final_src/06_ket_qua.md#L247).
- Parity LBR V3 "573/692, 665 lệch ≤ 1 khung, 691 trong collar, lệch xác suất 0,0020, chưa đo CPU": [05:158](../../report/final_src/05_trien_khai.md#L158) và [06:327](../../report/final_src/06_ket_qua.md#L327); nhắc lại ở hướng phát triển [07:58](../../report/final_src/07_ket_luan.md#L58).
- Giai đoạn O/P: [04:61](../../report/final_src/04_phuong_phap.md#L61) và [06:106–110](../../report/final_src/06_ket_qua.md#L106) (cùng ý "ba ứng viên qua sàng lọc dev đều đảo chiều", "thêm seed, chưng cất tri thức, cửa sổ 20 s, gain/EQ"); cũng ở bảng đóng góp C6 [01:92](../../report/final_src/01_gioi_thieu.md#L92) và [06:333](../../report/final_src/06_ket_qua.md#L333).
- Nguyên tắc "mỗi cấu hình đã khóa chỉ mở test một lần": [04:157](../../report/final_src/04_phuong_phap.md#L157), [06:331](../../report/final_src/06_ket_qua.md#L331); "một lần" xuất hiện 32 lần.
- Cảnh báo về LBR (thiết kế thăm dò trên chính tập chọn; đánh đổi PSDS-2 và F1 theo đoạn; chưa kiểm trên dữ liệu khác): bảng C5 [01:91](../../report/final_src/01_gioi_thieu.md#L91), [06:116](../../report/final_src/06_ket_qua.md#L116), [06:335](../../report/final_src/06_ket_qua.md#L335), [06:350](../../report/final_src/06_ket_qua.md#L350), [07:27](../../report/final_src/07_ket_luan.md#L27).
- Backfill được gợi ý từ test: [04:149](../../report/final_src/04_phuong_phap.md#L149), [06:299](../../report/final_src/06_ket_qua.md#L299), [06:335](../../report/final_src/06_ket_qua.md#L335).
- Hạn chế "chưa đo trên bản ghi Việt Nam": [01:53](../../report/final_src/01_gioi_thieu.md#L53), [05:29](../../report/final_src/05_trien_khai.md#L29), [06:160](../../report/final_src/06_ket_qua.md#L160), [06:357](../../report/final_src/06_ket_qua.md#L357), [07:43](../../report/final_src/07_ket_luan.md#L43), [07:49](../../report/final_src/07_ket_luan.md#L49), [07:53](../../report/final_src/07_ket_luan.md#L53). Danh sách hạn chế đầy đủ 12 gạch đầu dòng ở [06:348–359](../../report/final_src/06_ket_qua.md#L348) rồi tóm lại ở [07:49](../../report/final_src/07_ket_luan.md#L49) và bảng mục tiêu [07:35–43](../../report/final_src/07_ket_luan.md#L35).
- "Phạm vi tra cứu ở mức khóa luận, không phải tổng quan hệ thống": [01:81](../../report/final_src/01_gioi_thieu.md#L81), [02:103](../../report/final_src/02_co_so_ly_thuyet.md#L103), [06:359](../../report/final_src/06_ket_qua.md#L359). "áp dụng và mở rộng": 5 lần (Ch.1 ×2, Ch.2, Ch.7 ×2).
- Định nghĩa hậu xử lý lặp giữa Ch.2 và Ch.4 ("gộp khoảng trống ngắn và bỏ sự kiện quá ngắn"; "ngưỡng chỉ quyết định giữ hay bỏ sự kiện") — [02:43](../../report/final_src/02_co_so_ly_thuyet.md#L43)/[04:95](../../report/final_src/04_phuong_phap.md#L95), [02:45](../../report/final_src/02_co_so_ly_thuyet.md#L45)/[04:97](../../report/final_src/04_phuong_phap.md#L97).
- Số RQ2 "0,259 đến 0,403" và "0,126 đến 0,140" lặp ở [06:220](../../report/final_src/06_ket_qua.md#L220), [06:226](../../report/final_src/06_ket_qua.md#L226), [07:21](../../report/final_src/07_ket_luan.md#L21) (hai lần trong cùng một mục Ch.6).
- Tần suất số trụ cột (grep trên final_src): 0,2965 ×13 (01:2, 05:1, 06:7, 07:3); 1,000 ×14; +0,1159 ×8; 0,1806 ×7; 0,5785 ×6; "8 cặp" ×9; "bị chặn bởi" ×7.

### Inferences
- Giữ luận điểm ở 3 vị trí chiến lược (Tóm tắt, cuối Ch.1, đầu Ch.7) và để Ch.6 dẫn chiếu thay vì lặp.
- Gộp "vai trò thật của từng cách sinh" vào một chỗ (Ch.4 hoặc Ch.6, không cả hai); mô tả gộp theo lớp chỉ cần định nghĩa ở Ch.4, Ch.5 dẫn chiếu hình giao diện, Ch.6 chỉ báo số; parity chỉ giữ ở một chỗ.
- Danh sách hạn chế: một danh sách duy nhất ở Ch.7 (hoặc Ch.6), nơi còn lại dẫn chiếu.

### Gaps
- Phép dò trùng dùng shingle 9 âm tiết nên chỉ bắt trùng gần nguyên văn; các đoạn lặp ý nhưng diễn đạt khác chỉ được xác định bằng đọc tay.

## 7. 20 câu khó đọc nhất và đề xuất viết lại

### Takeaway
Các câu khó nhất thuộc ba kiểu: (a) câu liệt kê dài nối bằng dấu chấm phẩy (4–7 ý trong một câu), (b) câu nhồi số kèm KTC và mã hệ (mật độ token số/Anh 30–56%), (c) câu rào đón lồng nhiều mệnh đề phủ định. Cách sửa chung: tách câu, chuyển danh sách thành gạch đầu dòng, đưa KTC vào bảng, thay mã bằng tên có nghĩa.

### Cited Findings
(Độ dài = âm tiết; "mật độ" = tỷ lệ token chứa số hoặc là từ tiếng Anh/mã, đo bằng `audit.py`.)

1. [04:159](../../report/final_src/04_phuong_phap.md#L159) — 126 âm tiết. Gốc: "Ngoài các chỉ số chính, Chương 6 báo bốn phép đo chỉ đọc lại artifact đã có, không huấn luyện và không chạy lại mô hình: (1) chấm mô tả so với nhãn gốc… (4) độ chính xác của mệnh đề có và không có rào đón trong mô tả gộp." → Viết lại: "Chương 6 còn báo bốn phép đo phụ. Các phép đo này chỉ đọc lại kết quả đã lưu, không huấn luyện lại mô hình:" + 4 gạch đầu dòng: "chấm mô tả so với nhãn gốc, để tách lỗi của bước phát hiện khỏi lỗi của bộ sinh; cố ý chèn lỗi vào mô tả để xem bộ chấm bắt được bao nhiêu; tìm nguyên nhân khi truy hồi không tìm thấy bản ghi đúng; kiểm tra nhãn "độ tin cậy thấp" có đặt đúng chỗ không."
2. [01:57](../../report/final_src/01_gioi_thieu.md#L57) — 93 âm tiết, bảy mục tiêu trong một câu. → "Cụ thể, khóa luận có bảy mục tiêu:" + danh sách đánh số 1–7, mỗi mục một dòng.
3. [07:49](../../report/final_src/07_ket_luan.md#L49) — 93 âm tiết, năm hạn chế trong một câu. → "Năm hạn chế quan trọng nhất là:" + 5 gạch đầu dòng ngắn: "chưa thử trên bản ghi thu ở Việt Nam; tập kiểm tra nhỏ (139 bản ghi) nên khoảng tin cậy rộng; kết quả huấn luyện thay đổi giữa các lần chạy nên phải chạy nhiều lần; LBR cải thiện độ khớp biên nhưng làm giảm hai chỉ số khác; bộ chấm mô tả dựa trên từ điển và mới được một người đọc đối chiếu."
4. [06:346](../../report/final_src/06_ket_qua.md#L346) — 92 âm tiết. → "Với RQ3, mọi kết quả của bộ lọc cứng đều thỏa điều kiện trên các sự kiện đã lưu. Tuy vậy, về chất lượng xếp hạng (nDCG@10), cách kết hợp lọc và tìm theo nghĩa thua cách chỉ tìm theo nghĩa ở ba trên bốn kho, vì bước phát hiện bỏ sót nhiều sự kiện. Chỉ ở kho V3, nơi phát hiện được nhiều sự kiện hơn, cách kết hợp mới thắng. Chế độ bổ sung (backfill) thắng cả hai ở cả bốn kho."
5. [06:184](../../report/final_src/06_ket_qua.md#L184) — 84 âm tiết, mật độ 0,36 (30 token số/mã). → "PSDS của đề tài cùng cỡ với hệ cơ sở của DCASE trên bộ DESED (Bảng X). Tuy vậy hai bộ dữ liệu khác nhau nhiều: DESED gồm đoạn 10 giây, 10 lớp, phần lớn là âm thanh tổng hợp; DataSED gồm bản ghi dài trung bình 94 giây, 21 lớp, chỉ 564 bản ghi có nhãn để huấn luyện. Vì vậy nhóm không coi hai kết quả là tương đương." (đưa mọi số vào bảng `tbl:dcase`).
6. [06:317](../../report/final_src/06_ket_qua.md#L317) (câu 1) — 83 âm tiết. → "Độ đúng bộ lọc 1,000 chỉ cho biết kết quả khớp với bộ lọc và với các sự kiện hệ thống đã dự đoán. Nó không cho biết kết quả có đúng ý người hỏi, hay đúng với âm thanh thật. Ngoài ra, câu hỏi không có kết quả nào cũng được tính là đúng, nên cần đọc con số này cùng số câu hỏi có trả lời (58–65 trên 97)."
7. [06:116](../../report/final_src/06_ket_qua.md#L116) — 80 âm tiết. → "Có ba điểm cần lưu ý khi đọc kết quả LBR:" + 3 gạch: "thiết kế của LBR được thử và chọn trên chính tập dữ liệu dùng để đo, nên kết quả có thể hơi lạc quan; cách học chéo chỉ ngăn mô hình nhìn thấy bản ghi đang chấm, không ngăn việc chọn thiết kế theo kết quả; ngưỡng của cấu hình ưu tiên phát hiện nằm ở biên dưới của dải đã thử."
8. [06:317](../../report/final_src/06_ket_qua.md#L317) (câu 2) — 75 âm tiết, 21 token số/mã. → "Các kết quả trên giả định câu hỏi luôn được hiểu đúng. Khi để mô hình ngôn ngữ tự chuyển câu hỏi thành bộ lọc, điểm nDCG@10 chỉ giảm 0,006–0,015 trên tập kiểm tra."
9. [06:210](../../report/final_src/06_ket_qua.md#L210) — 73 âm tiết, dùng bộ tên thứ ba ("mẫu cố định", "LLM ràng buộc + phủ"). → "Hình X vẽ lại ba cột chính của bảng. Mô tả theo mẫu và mô tả có ràng buộc bắt buộc phủ không mắc lỗi nào ở cả bốn hệ. Mô tả có ràng buộc không bịa nguồn âm nhưng có bỏ sót, nhiều nhất ở hệ V3 (8% số lớp). Chỉ cách viết tự do thêm bối cảnh không có thật, ở 26–40% số mô tả."
10. [05:168](../../report/final_src/05_trien_khai.md#L168) — 72 âm tiết, 18 token số/mã. → "Có 17 lần chạy được ghi nhận khi mã nguồn còn thay đổi chưa lưu; tất cả diễn ra trước ngày 29/09 và chi tiết được liệt kê ở Phụ lục B." (chuyển danh sách sang phụ lục).
11. [06:102](../../report/final_src/06_ket_qua.md#L102) — 72 âm tiết. → "Hệ f2 chỉ dự đoán 295 sự kiện, trong khi nhãn có 740. Có 349 sự kiện thật không có dự đoán nào chồng lên. Vì vậy hạn chế chính của f2 là bỏ sót sự kiện." (chi tiết sed_eval → chú thích).
12. [03:9](../../report/final_src/03_du_lieu.md#L9) — 71 âm tiết. → "Nhóm không dùng số thống kê trong bài báo vì chúng không khớp với tệp tải về. Bài báo ghi DataSEC có 4.292 tệp, còn bản 3 mà nhóm dùng có 5.048 tệp do thừa tệp lớp Music. Bản 4, ra ngày 02/10/2026 sau khi dữ liệu của đề tài đã khóa, đã sửa lỗi này. Số tệp và thời lượng của DataSED trong bài cũng khác tệp nén."
13. [04:61](../../report/final_src/04_phuong_phap.md#L61) (câu định nghĩa B0) — 71 âm tiết. → "Hệ cuối của giai đoạn này, gọi là B0, gồm:" + 5 gạch: "cùng kiến trúc Frame-MobileNet; bỏ các bản ghi thiếu nhãn khỏi tập huấn luyện; xử lý các cặp bản ghi trùng được gán nhãn hai lần; năm mô hình, mỗi mô hình học trên một phần dữ liệu; cửa sổ trượt chồng nhau 5 giây."
14. [06:348](../../report/final_src/06_ket_qua.md#L348) — 68 âm tiết, 22 token số. → "Với 139 bản ghi kiểm tra, khoảng tin cậy của một hiệu số rộng khoảng ±0,02 đến ±0,04. Vì vậy, chênh lệch F1 nhỏ hơn mức này không tách được khỏi sai số do chọn mẫu." (số chi tiết → bảng).
15. [01:53](../../report/final_src/01_gioi_thieu.md#L53) (câu cuối) — 67 âm tiết. → "Nhóm chưa đo hệ thống trên bản ghi thu ở Việt Nam. Hai bộ dữ liệu đều là dữ liệu công bố sẵn, chưa rõ nơi thu, nên không thể khẳng định chúng đại diện cho âm thanh đô thị Việt Nam. Hạn chế này được bàn lại ở Chương 7."
16. [06:335](../../report/final_src/06_ket_qua.md#L335) (ý "Một") — 64 âm tiết, 4 mã (A2, A5, ADR-0024). → "Thứ nhất, hai lựa chọn hậu xử lý — dùng một ngưỡng chung cho mọi lớp và độ dài khoảng trống cho phép — được gợi ý từ kết quả trên tập kiểm tra của các hệ cũ. Sau đó nhóm chọn lại chúng trên tập phát triển theo luật định trước, nhưng ý tưởng ban đầu vẫn đến từ tập kiểm tra."
17. [06:243](../../report/final_src/06_ket_qua.md#L243) (ý "Một") — 61 âm tiết, 13 token số/mã. → "So với nhãn gốc, mọi cách sinh mô tả đều bỏ sót khoảng 34–42% số nguồn âm có thật ở ba hệ f2, B0 và V2 — kể cả cách theo mẫu, vốn không bỏ sót gì so với danh sách dự đoán. Ở hệ V3, phát hiện nhiều hơn nên bỏ sót giảm còn khoảng 11%, nhưng nhắc sai nguồn âm tăng lên 18–23%."
18. [06:160](../../report/final_src/06_ket_qua.md#L160) — 58 âm tiết, có tên tệp. → "Nếu chỉ tính 19 lớp phù hợp đô thị Việt Nam (bỏ máy bay cánh quạt và nhóm quạ–mòng biển–ác là), F1 của B0 là 0,19 và của LBR V2 là 0,31. Cấu hình V3 tìm được 83% sự kiện, với 78% dự đoán là đúng." (bỏ tên tệp khỏi câu).
19. [06:138](../../report/final_src/06_ket_qua.md#L138) (câu V3 `recall_first`) — 37 âm tiết, mật độ 0,38. → "Cấu hình V3 được đặt để ít bỏ sót. Nó dự đoán 668 sự kiện (nhãn có 740), tìm thấy 82% sự kiện thật nếu chỉ cần chồng lên nhau, và 78% dự đoán là đúng; đổi lại, F1 theo sự kiện chỉ còn 0,23."
20. [06:287](../../report/final_src/06_ket_qua.md#L287) (câu "Có thể đếm trực tiếp…") — nhắc `scripts.report_rq3_failures`, structured_only. → "Có thể đếm trực tiếp tác động này. Khi bộ lọc trả ít hơn 10 bản ghi, danh sách đó đã là toàn bộ bản ghi thỏa điều kiện; bản ghi đúng nằm ngoài danh sách chắc chắn bị loại vì bước phát hiện đã bỏ sót sự kiện của nó."
- Câu luận điểm (bổ sung, vì lặp 4 lần) [07:5](../../report/final_src/07_ket_luan.md#L5) — 62–87 âm tiết tùy bản. → "Kết luận chính: lỗi của mô tả và câu trả lời chủ yếu đến từ bước phát hiện sự kiện. Bộ sinh có ràng buộc không tự thêm nguồn âm ngoài danh sách sự kiện, và bộ lọc chỉ trả bản ghi thỏa điều kiện. Vì vậy, muốn hệ thống đúng hơn cần cải thiện bước phát hiện (như LBR) và giảm phụ thuộc vào sự kiện bị bỏ sót khi truy hồi (như backfill)."

### Inferences
- Các viết lại trên giảm trung bình 30–50% âm tiết mỗi câu và loại bỏ phần lớn mã/tên tệp; số liệu chi tiết nên chuyển về bảng thay vì nằm trong câu.
- Một số viết lại dùng tên Việt chưa thống nhất (ví dụ "chế độ bổ sung" cho backfill) — cần chốt trong bảng thuật ngữ ở mục 3 trước khi áp.

### Gaps
- Danh sách 20 câu chọn theo độ dài và mật độ token số/mã; không có người đọc thật để xác nhận đây đúng là 20 câu khó nhất. Các con số trong bản viết lại được làm tròn từ nguồn (ví dụ 0,1892 → 0,19; 0,8319 → 83%) và cần đối chiếu lại khi áp dụng.

## 8. Hình: sơ đồ hộp–mũi tên hay đồ thị/ảnh chụp, và script sinh

### Takeaway
Báo cáo có 25 hình: 7 sơ đồ hộp–mũi tên (ứng viên vẽ lại bằng shape Word có thể sửa), 15 đồ thị dữ liệu và 3 ảnh chụp giao diện. Sáu sơ đồ hệ thống do `scripts/build_system_figures.py` vẽ bằng matplotlib (`FancyBboxPatch`), sơ đồ quy trình dữ liệu và hình dòng thời gian từ `scripts/build_midterm_figures.py`; các đồ thị nghiên cứu từ `scripts/build_research_figures.py`. Các sơ đồ hiện chứa nhãn Anh–Việt lẫn lộn.

### Cited Findings

| Nhãn | Tệp ảnh | Vị trí | Loại | Script sinh |
|---|---|---|---|---|
| fig:dataprofile | report/research_figures/r01_data_profile.png | [03:30](../../report/final_src/03_du_lieu.md#L30) | Đồ thị | scripts/build_research_figures.py |
| fig:duration | r02_event_duration.png | [03:38](../../report/final_src/03_du_lieu.md#L38) | Đồ thị | build_research_figures.py |
| fig:pipeline | report/figures/m04_data_pipeline.png | [03:48](../../report/final_src/03_du_lieu.md#L48) | **Sơ đồ hộp–mũi tên** (5 hộp D0–D4) | scripts/build_midterm_figures.py |
| fig:dataflow | report/final_figures/s01_data_flow.png | [04:11](../../report/final_src/04_phuong_phap.md#L11) | **Sơ đồ hộp–mũi tên** (12 hộp + khung ngoại tuyến) | scripts/build_system_figures.py |
| fig:training | r03_training_curves.png | [04:65](../../report/final_src/04_phuong_phap.md#L65) | Đồ thị | build_research_figures.py |
| fig:fnbreakdown | r05_fn_breakdown.png | [04:73](../../report/final_src/04_phuong_phap.md#L73) | Đồ thị | build_research_figures.py |
| fig:onsetbias | r06_onset_bias.png | [04:79](../../report/final_src/04_phuong_phap.md#L79) | Đồ thị | build_research_figures.py |
| fig:lbr | report/final_figures/s02_lbr.png | [04:85](../../report/final_src/04_phuong_phap.md#L85) | **Sơ đồ hộp–mũi tên** (6 hộp + khung cross-fit) | build_system_figures.py |
| fig:timeline | report/figures/m05_dev_timeline.png | [04:126](../../report/final_src/04_phuong_phap.md#L126) | Đồ thị (dòng thời gian nhãn vs dự đoán) | build_midterm_figures.py |
| fig:architecture | s03_deployment.png | [05:49](../../report/final_src/05_trien_khai.md#L49) | **Sơ đồ hộp–mũi tên** (kiến trúc triển khai) | build_system_figures.py |
| fig:uploadflow | s04_upload_flow.png | [05:80](../../report/final_src/05_trien_khai.md#L80) | **Sơ đồ luồng** | build_system_figures.py |
| fig:queryflow | s05_query_flow.png | [05:88](../../report/final_src/05_trien_khai.md#L88) | **Sơ đồ luồng** | build_system_figures.py |
| fig:erd | s06_erd.png | [05:98](../../report/final_src/05_trien_khai.md#L98) | **Sơ đồ ERD** (đọc từ migration SQL, chỉ hiện 9 cột đầu) | build_system_figures.py |
| fig:demo1 | report/final_figures/f03a_demo_upload_timeline.png | [05:116](../../report/final_src/05_trien_khai.md#L116) | Ảnh chụp giao diện (Playwright) ghép | scripts/build_final_figures.py |
| fig:demochip | docs/demo_screenshots/03-filter-chip.png | [05:124](../../report/final_src/05_trien_khai.md#L124) | Ảnh chụp giao diện | Playwright; tham chiếu trong scripts/build_thesis_figures.py |
| fig:demo2 | f03b_demo_query_evidence.png | [05:132](../../report/final_src/05_trien_khai.md#L132) | Ảnh chụp giao diện ghép | build_final_figures.py |
| fig:runtimeline | r12_run_timeline.png | [05:176](../../report/final_src/05_trien_khai.md#L176) | Đồ thị (ứng viên phụ lục) | build_research_figures.py |
| fig:rq1seeds | r09_rq1_seeds.png | [06:58](../../report/final_src/06_ket_qua.md#L58) | Đồ thị | build_research_figures.py |
| fig:sedfinal | f01_sed_final.png | [06:132](../../report/final_src/06_ket_qua.md#L132) | Đồ thị | build_final_figures.py |
| fig:perclass | r07_per_class.png | [06:142](../../report/final_src/06_ket_qua.md#L142) | Đồ thị | build_research_figures.py |
| fig:journey | r04_sed_journey.png | [06:150](../../report/final_src/06_ket_qua.md#L150) | Đồ thị | build_research_figures.py |
| fig:rq2errors | r10_rq2_errors.png | [06:212](../../report/final_src/06_ket_qua.md#L212) | Đồ thị | build_research_figures.py |
| fig:rq3queries | r11_rq3_queries.png | [06:281](../../report/final_src/06_ket_qua.md#L281) | Đồ thị | build_research_figures.py |
| fig:rq3backfill | r13_rq3_backfill.png | [06:309](../../report/final_src/06_ket_qua.md#L309) | Đồ thị | build_research_figures.py |
| fig:devtest | r08_dev_vs_test.png | [06:338](../../report/final_src/06_ket_qua.md#L338) | Đồ thị (ứng viên phụ lục cùng mục tái sử dụng test) | build_research_figures.py |

- Ánh xạ tệp ảnh → script xác định bằng grep tên tệp trong `scripts/` (mỗi tên PNG chỉ xuất hiện trong đúng một script sinh; m04/m05 còn được `scripts/midterm_slides/part_a.py`, `part_c.py` dùng lại cho slide). `build_system_figures.py` (565 dòng) dùng `matplotlib.patches.FancyBboxPatch` — [scripts/build_system_figures.py:254–264](../../scripts/build_system_figures.py#L254).
- Nội dung nhãn đã xem trực tiếp ở s01, s02, m04: có "Frame-MobileNet × 5 fold", "template gộp theo lớp", "Mô tả EN / VI", "PCM16", "B-tree, GIN, HNSW", "GBM", "Cross-fit lồng nhau (5 fold theo bản ghi)", "Δonset, Δoffset", "xuyên dataset", "T1/T2/T3" ([s01](../../report/final_figures/s01_data_flow.png), [s02](../../report/final_figures/s02_lbr.png), [m04](../../report/figures/m04_data_pipeline.png)).
- Điểm dễ gây thắc mắc trong s01: hộp 2 ghi "log-mel 128 dải, 100 khung/s" và hộp 5 ghi "21 lớp × khung 10 ms", trong khi Ch.3 nói đặc trưng PANNs là "64 mel, 100 khung/s" [03:54](../../report/final_src/03_du_lieu.md#L54) và Ch.4 nói T2b nhận "sóng âm 16 kHz", ra "250 bước cho 10 s" rồi nội suy lên lưới 10 ms [04:55](../../report/final_src/04_phuong_phap.md#L55); văn bản [04:7](../../report/final_src/04_phuong_phap.md#L7) cũng ghi 128 dải.

### Inferences
- 7 sơ đồ (m04, s01–s06) là ứng viên vẽ lại bằng shape Word: chữ sửa được, dễ Việt hóa, đúng phông của báo cáo. s06 (ERD) có thể giữ dạng ảnh nhưng nên Việt hóa tên cột hiển thị hoặc ghi chú. Đồ thị và ảnh chụp nên giữ dạng ảnh, chỉ Việt hóa nhãn trục/chú giải trong script.
- r12 (dòng thời gian lần chạy) và r08 (dev vs test) phục vụ lập luận quy trình — có thể chuyển phụ lục cùng các mục tương ứng.
- Cần một câu giải thích nhất quán về đầu vào của B0 (sóng âm → log-mel 128 dải bên trong mô hình?) để s01, Ch.3, Ch.4 không mâu thuẫn bề ngoài.

### Gaps
- Chưa xem trực tiếp s03–s06 và các đồ thị r01–r13 để liệt kê đủ nhãn tiếng Anh trong từng hình; chưa kiểm hình nào có cỡ chữ dưới mức đọc được khi in. Chưa xác minh đầu vào thực của Frame-MobileNet trong mã (`ml/inference/pipeline.py`) — chỉ ghi nhận sự khác nhau giữa các đoạn mô tả.
