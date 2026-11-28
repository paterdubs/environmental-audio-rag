# Thuật ngữ tiếng Việt cho học máy, phát hiện sự kiện âm thanh, truy hồi thông tin và LLM: thay tiếng Anh trong bản gọn

> Phạm vi: đọc `report/gon_src/00_phan_dau.md` … `07_ket_luan.md`, `90_phan_cuoi.md`, `display.yaml`; đọc lại ghi chú cũ
> `research_notes/Tinh gọn báo cáo khóa luận/thesis_terminology_audit.md` và `vietnamese_plain_writing.md` (quy tắc ba mức
> dựa trên d2l.aivivn). Ghi chú này **chỉ mở rộng và sửa** quy tắc cũ theo yêu cầu mới của người dùng: ưu tiên tiếng Việt ở
> mọi chỗ có từ Việt được chấp nhận (ví dụ "RQ1" cũng phải có dạng tiếng Việt). Không sửa tệp nào trong repo.
> Đếm từ: script nháp `count.py`, `ascii.py` trong scratchpad
> (C:\Users\patph\AppData\Local\Temp\claude\85ae35366b529c68\b4942c2f-c1bf-4b4b-81ce-f0801cbaaca1\scratchpad\terms\),
> chạy bằng `.venv/Scripts/python.exe -I`. Số đếm là văn xuôi + bảng viết tay trong Ch.1–7 và phần cuối (bỏ dòng `@@…@@`);
> phần Abstract tiếng Anh ở `00_phan_dau.md` được tính riêng vì ở đó tiếng Anh là đúng.
> Quy ước liên kết: `[02:49](…)` = `report/gon_src/02_co_so_ly_thuyet.md`, dòng 49.
> Hai PDF tải về được trích chữ bằng `pdftotext` (bài HOU 2026 và slide HUST IT4853); một PDF (vjs.ac.vn) là ảnh quét nên
> **chỉ có đoạn trích tìm kiếm**, ghi rõ ở từng dòng.

## 1. Những từ tiếng Anh nào còn nằm trong văn xuôi của bản gọn?

### Takeaway
Bản gọn đã Việt hóa phần lớn cụm từ (không còn hybrid, backfill, caption, template, constrained, ensemble, out-of-fold trong
thân bài — chỉ còn ở Abstract tiếng Anh). Tiếng Anh còn lại tập trung ở **nhãn câu hỏi/đóng góp (RQ1–RQ3: 40 lần; C1–C6: 15
lần)**, **tên chỉ số (event-F1 ≈ 45 lần, micro ≈ 34, macro ≈ 13, precision/recall 7/8)**, **từ huấn luyện (seed 14, fold 8,
epoch 4, checkpoint 4, bootstrap 5)** và **từ phần mềm (demo 12, API 17, script 5, web 7)**. Ngoài ra có bốn va chạm tên mới
do chính các từ Việt đã chọn: "độ phủ", "gộp", "tinh chỉnh" và nhãn yêu cầu "F1–F5".

### Cited Findings
**1.1 Tiếng Anh còn trong văn xuôi Ch.1–7 và phần cuối** (đếm bằng `ascii.py`; số đã gộp các biến thể hoa/thường; vị trí là
lần đầu hoặc ví dụ):

| Từ | Số lần | Ví dụ vị trí | Ghi chú |
|---|---:|---|---|
| RQ1 / RQ2 / RQ3 | 16 / 13 / 11 | [01:67](../../report/gon_src/01_gioi_thieu.md#L67) định nghĩa "Ba câu hỏi nghiên cứu (Research Question – RQ)"; bảng [01:73–75](../../report/gon_src/01_gioi_thieu.md#L73); tiêu đề mục 6 "RQ1: …", "RQ2: …", "RQ3: …" ([06:137](../../report/gon_src/06_ket_qua.md#L137), [06:169](../../report/gon_src/06_ket_qua.md#L169)) | Người dùng yêu cầu thay bằng dạng Việt |
| C1 … C6 | 2–3 mỗi mã | bảng đóng góp [01:95–100](../../report/gon_src/01_gioi_thieu.md#L95); [01:87](../../report/gon_src/01_gioi_thieu.md#L87) "gần với C2, C3 và C4"; Ch.7 | Chữ "C" còn là nhánh C của RQ1 ([01:77](../../report/gon_src/01_gioi_thieu.md#L77)) |
| event-F1 / Event-F1 | 37 / 8 | [01:99](../../report/gon_src/01_gioi_thieu.md#L99), [02:15](../../report/gon_src/02_co_so_ly_thuyet.md#L15), 20+ lần ở Ch.6 | Danh mục thuật ngữ đã có "F1 theo đoạn" cho segment-F1 ([00:132](../../report/gon_src/00_phan_dau.md#L132)) nhưng giữ "Event-F1" ([00:131](../../report/gon_src/00_phan_dau.md#L131)) |
| micro / macro (+ macro-F1) | 34 / 13 | định nghĩa [02:27–33](../../report/gon_src/02_co_so_ly_thuyet.md#L27); "macro-F1 0,8466" [06:20](../../report/gon_src/06_ket_qua.md#L20) | Công thức dùng $F_1^{micro}$, $F_1^{macro}$ ([02:29](../../report/gon_src/02_co_so_ly_thuyet.md#L29)) |
| precision / recall | 7 / 8 | [02:21](../../report/gon_src/02_co_so_ly_thuyet.md#L21), [04:66](../../report/gon_src/04_phuong_phap.md#L66), [06:89](../../report/gon_src/06_ket_qua.md#L89), [06:167](../../report/gon_src/06_ket_qua.md#L167) | display.yaml còn "Precision lớp / Recall lớp" ([display.yaml:62–63](../../report/gon_src/display.yaml#L62)) |
| seed | 14 | [03:66](../../report/gon_src/03_du_lieu.md#L66), [04:44](../../report/gon_src/04_phuong_phap.md#L44), [06:43](../../report/gon_src/06_ket_qua.md#L43), [06:73](../../report/gon_src/06_ket_qua.md#L73) "gộp 3 seed" | Danh mục thuật ngữ giữ "Seed" ([00:129](../../report/gon_src/00_phan_dau.md#L129)) |
| fold | 8 | [04:26](../../report/gon_src/04_phuong_phap.md#L26), [04:46](../../report/gon_src/04_phuong_phap.md#L46) "kiểm chứng chéo 5 fold" | Danh mục ghi "Kiểm chứng chéo, fold" ([00:127](../../report/gon_src/00_phan_dau.md#L127)) |
| demo | 12 | [04:28](../../report/gon_src/04_phuong_phap.md#L28), [05:56](../../report/gon_src/05_trien_khai.md#L56), [05:130](../../report/gon_src/05_trien_khai.md#L130) | [01:65](../../report/gon_src/01_gioi_thieu.md#L65) đã có "ứng dụng web minh họa" |
| bootstrap | 5 | [02:89](../../report/gon_src/02_co_so_ly_thuyet.md#L89), [04:46](../../report/gon_src/04_phuong_phap.md#L46), [04:155](../../report/gon_src/04_phuong_phap.md#L155) | |
| epoch / checkpoint | 4 / 4 | [04:38](../../report/gon_src/04_phuong_phap.md#L38), [04:137](../../report/gon_src/04_phuong_phap.md#L137), [05:48](../../report/gon_src/05_trien_khai.md#L48) | |
| vector | 11 | [02:67](../../report/gon_src/02_co_so_ly_thuyet.md#L67), [04:107](../../report/gon_src/04_phuong_phap.md#L107) | Chính tả "vector" vs "vectơ" chưa chọn |
| log-mel / mel | 3 / 2 | [02:11](../../report/gon_src/02_co_so_ly_thuyet.md#L11), [04:42](../../report/gon_src/04_phuong_phap.md#L42) | |
| token, cosine, collar, onset/offset, pooling, cross-fit, cross-entropy, mixup, parser, split, endpoint | 1–2 mỗi từ | token [02:75](../../report/gon_src/02_co_so_ly_thuyet.md#L75); cosine [03:56](../../report/gon_src/03_du_lieu.md#L56), [05:70](../../report/gon_src/05_trien_khai.md#L70); collar trong ngoặc [02:15](../../report/gon_src/02_co_so_ly_thuyet.md#L15); onset/offset trong ngoặc [01:9](../../report/gon_src/01_gioi_thieu.md#L9); pooling [02:49](../../report/gon_src/02_co_so_ly_thuyet.md#L49); cross-fit [02:83](../../report/gon_src/02_co_so_ly_thuyet.md#L83); cross-entropy, mixup [04:36–40](../../report/gon_src/04_phuong_phap.md#L36); parser [06:213](../../report/gon_src/06_ket_qua.md#L213); split [03:66](../../report/gon_src/03_du_lieu.md#L66); endpoint trong ngoặc [05:58](../../report/gon_src/05_trien_khai.md#L58) | Phần lớn đã kèm từ Việt trong ngoặc |
| script, git, manifest | 5, 4, 2 | "script sinh từ tệp kết quả" [06:3](../../report/gon_src/06_ket_qua.md#L3); Phụ lục B | |
| API, CPU, GPU, HTTP, Docker, PyTorch, web | 17, 6, 3, 1, 3, 4, 7 | Ch.5 | Từ viết tắt/tên riêng chuẩn |

- **Không còn trong thân bài** (chỉ ở Abstract EN, dòng 5–9 của [00_phan_dau.md](../../report/gon_src/00_phan_dau.md#L5)):
  hybrid, backfill, caption, grounded, hallucination, template, constrained, unconstrained, vector_only, structured_only,
  ensemble, out-of-fold, event store, embedding, retrieval. Bản gọn đã thay bằng "kết hợp", "bổ sung", "mô tả", "theo
  mẫu/tự do/ràng buộc", "gộp mô hình", "dự đoán ngoài mẫu", "kho sự kiện", "truy hồi" (đếm bằng `count.py`).
- **Tiếng Anh trong bảng hiển thị** do `display.yaml` đổi tên lúc dựng còn sót: "Precision lớp", "Recall lớp"
  ([display.yaml:62–63](../../report/gon_src/display.yaml#L62)); "Loss huấn luyện" trong nhãn hình
  ([display.yaml:147](../../report/gon_src/display.yaml#L147)); "gộp 3 seed" ([display.yaml:23–24](../../report/gon_src/display.yaml#L23));
  "fold" ([display.yaml:17](../../report/gon_src/display.yaml#L17), [144–148](../../report/gon_src/display.yaml#L144)).

**1.2 Va chạm tên do chính các từ Việt đã chọn** (dễ bị hội đồng bắt hơn cả từ tiếng Anh):
- **"độ phủ"** đang dùng 10 lần cho *coverage* (độ phủ sự kiện khi truy hồi, "hiệu ứng độ phủ") — [01:106](../../report/gon_src/01_gioi_thieu.md#L106), [06:179](../../report/gon_src/06_ket_qua.md#L179), [06:231](../../report/gon_src/06_ket_qua.md#L231), [07:5](../../report/gon_src/07_ket_luan.md#L5) — và cho mức phủ của mô tả ([02:61](../../report/gon_src/02_co_so_ly_thuyet.md#L61)). Đây lại là một cách dịch phổ biến của *recall* (xem mục 2), nên không thể dùng "độ phủ" cho recall.
- **"độ chính xác"** dùng cho *accuracy* của bộ phân loại ("độ chính xác 0,9135 (676 trên 740 đoạn)", [06:20](../../report/gon_src/06_ket_qua.md#L20)) và theo nghĩa thường cho biên ("đổi độ phủ lấy độ chính xác của biên", [06:107](../../report/gon_src/06_ket_qua.md#L107); [06:179](../../report/gon_src/06_ket_qua.md#L179)). Đây cũng là cách dịch phổ biến của *precision*.
- **"gộp"** có bốn nghĩa: lớp cấp trên của DataSEC ("22 lớp gộp và 28 lớp con", [03:11](../../report/gon_src/03_du_lieu.md#L11), [06:20](../../report/gon_src/06_ket_qua.md#L20)); lớp gộp nhiều nguồn âm (`sirens_and_alarms`, [03:22](../../report/gon_src/03_du_lieu.md#L22)); *pooling* ("các lớp gộp (pooling)", [02:49](../../report/gon_src/02_co_so_ly_thuyet.md#L49)); *ensemble* ("gộp mô hình", [04:44](../../report/gon_src/04_phuong_phap.md#L44), [00:128](../../report/gon_src/00_phan_dau.md#L128)); cộng thêm "gộp xác suất theo trọng số tam giác" ([04:7](../../report/gon_src/04_phuong_phap.md#L7), [04:74](../../report/gon_src/04_phuong_phap.md#L74)) và "mô tả gộp theo lớp" ([04:95](../../report/gon_src/04_phuong_phap.md#L95)).
- **"tinh chỉnh"** vừa là LBR ("Tinh chỉnh biên học được", [00:99](../../report/gon_src/00_phan_dau.md#L99)) vừa là cách dịch chuẩn của *fine-tuning* theo d2l (mục 2).
- **"F1"–"F5"** là mã yêu cầu chức năng ở bảng yêu cầu Ch.5 ([05:17–21](../../report/gon_src/05_trien_khai.md#L17), N1–N3 ở [05:22–24](../../report/gon_src/05_trien_khai.md#L22)), trong khi chính ô của dòng F2 ghi "Event-F1 micro 0,2965" ([05:18](../../report/gon_src/05_trien_khai.md#L18)).
- **"Tập kiểm định"** xuất hiện một lần trong bảng so sánh văn liệu ([06:34](../../report/gon_src/06_ket_qua.md#L34)), trong khi danh mục chỉ định "tập phát triển" cho dev ([00:125](../../report/gon_src/00_phan_dau.md#L125)).
- **"mô tả có căn cứ"** (từ khóa [00:21](../../report/gon_src/00_phan_dau.md#L21), mục tiêu [01:63](../../report/gon_src/01_gioi_thieu.md#L63), [05:82](../../report/gon_src/05_trien_khai.md#L82)) và **"bám sát sự kiện"** (RQ2 [01:74](../../report/gon_src/01_gioi_thieu.md#L74), C1/C2 [01:95–96](../../report/gon_src/01_gioi_thieu.md#L95), tiêu đề [02:57](../../report/gon_src/02_co_so_ly_thuyet.md#L57), [04:76](../../report/gon_src/04_phuong_phap.md#L76)) cùng dịch *grounded*.

### Inferences
- Lượng tiếng Anh còn lại nhỏ (dưới 250 lần trên ~30.000 âm tiết) và phần lớn tập trung ở 8 từ: RQ, C1–C6, event-F1, micro,
  macro, seed, fold, demo. Thay 8 từ này là đủ để bản gọn "đọc như tiếng Việt" với hội đồng.
- Bốn va chạm ở 1.2 phải sửa **cùng lúc** với việc Việt hóa precision/recall/ensemble/pooling, nếu không việc Việt hóa sẽ
  tạo lỗi mới (ví dụ dịch recall là "độ phủ" sẽ làm "hiệu ứng độ phủ" ở [06:179](../../report/gon_src/06_ket_qua.md#L179) đổi nghĩa).

### Gaps
- Bộ đếm theo khoảng trắng không phân biệt chữ Anh trong công thức LaTeX với chữ trong văn (ví dụ `F_1^{micro}`); các mã
  `tbl:`, `fig:` đã được loại bằng tay khi đọc kết quả, nhưng có thể còn vài lần đếm trùng. Không đếm chữ trong các bảng
  được `@@INCLUDE@@` (chỉ đếm các thay thế còn sót trong `display.yaml`).

## 2. Thuật ngữ tiếng Việt đã được dùng cho từng khái niệm, và xung đột giữa các nguồn

### Takeaway
Không có chuẩn quốc gia (TCVN, từ điển bách khoa) cho thuật ngữ học máy; các nguồn có uy tín **mâu thuẫn ở đúng những từ
quan trọng nhất**: d2l.aivivn và Machine Learning Cơ Bản giữ nguyên *precision, recall, embedding, epoch, token, checkpoint*;
giáo trình truy hồi thông tin của HUST dịch *precision* = "độ chính xác", *recall* = "độ đầy đủ"; bản tiếng Việt của Google
dịch cả *accuracy* lẫn *precision* là "độ chính xác". Với yêu cầu "ưu tiên tiếng Việt", cách an toàn là chọn từ Việt **có
nguồn** và **không va chạm với từ khác trong chính khóa luận**, kèm tiếng Anh in nghiêng ở lần đầu.

### Cited Findings
**2.1 Dữ kiện từ nguồn (đã đọc trực tiếp):**
- **d2l.aivivn, Bảng thuật ngữ** (bản dịch "Đắm mình vào Học Sâu"): accuracy → "độ chính xác"; precision → "precision"; recall
  → "recall"; F1 score → "chỉ số F1"; embedding → "embedding"; cross validation → "kiểm định chéo"; k-fold cross validation →
  "kiểm định chéo gập k-lần"; fine-tuning → "tinh chỉnh"; pre-train → "tiền huấn luyện"; epoch → "epoch (khi huấn luyện)";
  batch → "batch"; checkpoint → "checkpoint (của mô hình)"; token → "token"; logit → "logit"; pipeline → "pipeline";
  transformer → "transformer"; vector → "vector"; cosine → "cô-sin"; hyperparameter → "siêu tham số"; training set → "tập
  huấn luyện"; validation set → "tập kiểm định"; dev set → "tập phát triển"; test set → "tập kiểm tra"; ground truth → "nhãn
  gốc"; inference → "dự đoán / suy luận"; feature → "đặc trưng"; feature extraction → "trích xuất đặc trưng"; posterior →
  "hậu nghiệm"; prior → "tiên nghiệm"; confidence interval → "khoảng tin cậy"; sampling with replacement → "lấy mẫu có hoàn
  lại"; metric → "phép đo"; evaluation metric → "phép đánh giá"; loss function → "hàm mất mát"; end-to-end → "đầu-cuối";
  query → "(câu) truy vấn"; corpus → "kho ngữ liệu"; dataset → "tập dữ liệu"; pooling → "gộp"; GRU → "nút hồi tiếp có cổng";
  timestep → "bước thời gian"; frozen weight → "trọng số bị đóng băng"; data augmentation → "tăng cường dữ liệu"; transfer
  learning → "học truyền tải"; benchmark → "đánh giá xếp hạng"; overfit → "quá khớp"; beam search → "tìm kiếm chùm".
  **Không có trong bảng:** ensemble, bootstrap, fold, seed, encoder (đứng riêng), baseline, ablation, threshold, label,
  spectrogram, mel, latency, retrieval, ranking, cosine similarity, hallucination, prompt, schema, grammar, mixup,
  distillation, gradient boosting, frame. Quy tắc của bảng: "Các thuật ngữ cần được dịch theo chuẩn trong tập tin này"; từ
  chưa có thì mở thảo luận; mục giữ tiếng Anh là mục có cột Việt trùng cột Anh. — [d2l.aivivn.com, Bảng thuật ngữ](https://d2l.aivivn.com/glossary.html)
- **Machine Learning Cơ Bản (bài "Các phương pháp đánh giá một hệ thống phân lớp")**: "accuracy (độ chính xác)"; tiêu đề
  "Precision và Recall" giữ tiếng Anh; "F1-score"; "Macro-average precision", "Micro-average precision" giữ tiếng Anh;
  "confusion matrix", "True Positive (TP)", "False Positive (FP)", "False Negative (FN)" giữ tiếng Anh; "một ngưỡng
  (threshold)"; "ROC curve", "AUC" giữ tiếng Anh. — [machinelearningcoban.com, 31/08/2017](https://machinelearningcoban.com/2017/08/31/evaluation/)
- **HUST, học phần IT4853 "Tìm kiếm và trình diễn thông tin", Bài 7 "Đánh giá kết quả tìm kiếm"** (Bộ môn Hệ thống thông
  tin, Viện CNTT&TT; trích bằng `pdftotext`): "Độ chính xác là tỉ lệ văn bản phù hợp trên số văn bản được trả về Precision =
  …"; "Độ đầy đủ là tỉ lệ văn bản phù hợp được trả về trên số văn bản phù hợp … Recall = …"; "Ký hiệu P: độ chính xác; R: độ
  đầy đủ"; "Độ đo F kết hợp độ chính xác và độ đầy đủ"; "Ký hiệu độ đo F với β = 1 là F1"; "Đường cong P/R"; dùng "tìm kiếm"
  cho *retrieval*, "văn bản phù hợp" cho *relevant*, "truy vấn" cho *query*. — [users.soict.hust.edu.vn, IT4853 L07](https://users.soict.hust.edu.vn/hieunk/courses/IT4853/L07.pdf)
- **Google Machine Learning Crash Course, bản `hl=vi`:** tiêu đề trang (thấy trong kết quả tìm kiếm) là "Phân loại: Độ chính
  xác, mức độ ghi nhớ, độ chính xác và các chỉ số liên quan" — tức *accuracy* và *precision* cùng là "độ chính xác", *recall*
  là "mức độ ghi nhớ". Khi tải trang bằng công cụ, nội dung trả về tiếng Anh nên không đọc được thân bài tiếng Việt. —
  [developers.google.com, accuracy-precision-recall?hl=vi](https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall?hl=vi)
- **Bài báo tiếng Việt về RAG, Tạp chí Khoa học Trường ĐH Mở Hà Nội (HOU) 2026**, "Xây dựng hệ thống chatbot hỏi đáp trên tài
  liệu kỹ thuật sử dụng Retrieval-Augmented Generation", DOI 10.59266/houjs.2026.1173 (trích bằng `pdftotext`): "hiện tượng
  ảo giác (hallucination)"; "sinh vector nhúng và lập chỉ mục"; "mô hình nhúng đa ngôn ngữ BAAI/bge-m3"; "truy xuất ngữ
  nghĩa, xếp hạng lại"; "ba chế độ truy xuất (dense, keyword, hybrid)" — giữ tiếng Anh cho tên chế độ; "truy xuất thông tin
  (Information Retrieval - IR)"; "mô hình ngôn ngữ lớn"; "bộ kiểm thử gồm 25 câu hỏi có gán nhãn"; "độ trễ"; "Chỉ số đánh
  giá"; "pipeline RAG", "chunking", "reranking", "embedding", "cosine similarity" vẫn để tiếng Anh ở nhiều chỗ. Từ khóa của
  chính bài này lại dùng "truy hồi": "tạo sinh truy hồi tăng cường, truy hồi dày đặc, tái xếp thứ hạng". Mục đóng góp viết
  "Các đóng góp chính của nghiên cứu bao gồm:" rồi liệt kê, không đánh mã. — [jshou.edu.vn, HOU 2026](https://jshou.edu.vn/houjs/article/download/1173/1001/1705)

**2.2 Dữ kiện chỉ có qua đoạn trích tìm kiếm (chưa đọc được trang gốc):**
- Một bài trên Tạp chí Tin học và Điều khiển học dùng "Độ chính xác (Precision)", "Độ phủ (Recall)", "Độ đo F1" (PDF là ảnh
  quét, không trích được chữ để kiểm). — [vjs.ac.vn (đoạn trích)](https://vjs.ac.vn/index.php/jcc/article/download/469/pdf/1694)
- Một bộ slide đánh giá truy hồi thông tin ghi recall là "độ phủ", còn gọi "True Positive Rate hay Sensitivity (độ nhạy)". —
  [scribd.com (đoạn trích)](https://www.scribd.com/document/714866697/5-Evaluation-IR)
- Tên tiếng Việt của RAG ở trang công nghiệp: "Tạo tăng cường truy xuất" (AWS), "Tạo sinh tăng cường truy xuất" (Perplexity);
  DataCamp dùng "tìm kiếm lai", "xếp hạng lại". — [AWS (vi)](https://aws.amazon.com/vi/what-is/retrieval-augmented-generation/); [Perplexity (vi)](https://www.perplexity.ai/vi/hub/blog/rag); [DataCamp (vi)](https://www.datacamp.com/vi/blog/rag-advanced)
- *Ensemble learning* được gọi "học tổ hợp" (blog interdata); slide ĐH Cần Thơ (Đỗ Thanh Nghị) gọi "phương pháp tập hợp mô
  hình" và mô tả bootstrap là lấy mẫu N phần tử có hoàn lại (trang gốc trả 404 khi tải). — [interdata.vn (đoạn trích)](https://interdata.vn/blog/?p=26805); [cit.ctu.edu.vn (đoạn trích)](https://cit.ctu.edu.vn/~dtnghi/ml/ens.pdf); [DataCamp, bootstrapping (vi, đoạn trích)](https://www.datacamp.com/vi/tutorial/bootstrapping)
- Bảng thuật ngữ tiếng Việt của Ultralytics có mục "ảo giác" trong LLM; Google Codelabs bản tiếng Việt dùng "nội dung nhúng
  vectơ" (tiêu đề trang). — [Ultralytics (vi)](https://www.ultralytics.com/vi/glossary/hallucination-in-llms); [Google Codelabs (vi)](https://codelabs.developers.google.com/codelabs/using-textembedding-gecko?hl=vi)
- Một bài phân loại âm thanh nhạc cụ trên tạp chí HOU giữ "Mel-spectrogram" bằng tiếng Anh. — [jshou.edu.vn/houjs/article/view/729 (đoạn trích)](https://jshou.edu.vn/houjs/article/view/729)

**2.3 Bảng thuật ngữ đề xuất cho bản gọn.** Cột "Đã thấy" và "Nguồn" là dữ kiện; cột "Đề xuất" và "Mức" là **suy luận** của
người nghiên cứu (lý do ở cột Ghi chú). Ký hiệu nguồn: **d2l** = [d2l.aivivn](https://d2l.aivivn.com/glossary.html);
**MLCB** = [Machine Learning Cơ Bản](https://machinelearningcoban.com/2017/08/31/evaluation/); **HUST** =
[IT4853 L07](https://users.soict.hust.edu.vn/hieunk/courses/IT4853/L07.pdf); **GG** = [Google MLCC vi](https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall?hl=vi);
**HOU** = [bài RAG HOU 2026](https://jshou.edu.vn/houjs/article/download/1173/1001/1705); **ĐT** = chỉ có đoạn trích (2.2);
**KL** = cách khóa luận đang dùng (gon_src). Mức: **1** = luôn tiếng Việt (tiếng Anh chỉ ở Danh mục thuật ngữ);
**2** = tiếng Việt, kèm tiếng Anh *in nghiêng* trong ngoặc ở lần đầu và trong Danh mục; **3** = giữ nguyên tiếng Anh/tên riêng,
giải nghĩa một lần.

*Đánh giá và chỉ số*

| Tiếng Anh | Đề xuất | Đã thấy | Nguồn | Mức | Ghi chú |
|---|---|---|---|---|---|
| accuracy | tỷ lệ phân loại đúng | độ chính xác | d2l, MLCB, GG | 2 | Chỉ dùng 1 lần ([06:20](../../report/gon_src/06_ket_qua.md#L20)). Đổi khỏi "độ chính xác" để nhường từ này cho precision; nếu giữ "độ chính xác" cho accuracy thì precision phải giữ tiếng Anh |
| precision | độ chính xác | precision; độ chính xác | d2l, MLCB (giữ EN); HUST, ĐT vjs (dịch) | 2 | Chỉ an toàn khi accuracy đã đổi tên và các câu "độ chính xác của biên" ([06:107](../../report/gon_src/06_ket_qua.md#L107), [06:179](../../report/gon_src/06_ket_qua.md#L179)) được viết lại ("độ khớp của biên") |
| recall | độ đầy đủ | recall; độ đầy đủ; độ phủ; mức độ ghi nhớ; độ nhạy (sensitivity) | d2l, MLCB (giữ EN); HUST; ĐT vjs, scribd; GG | 2 | **Không dùng "độ phủ"**: khóa luận đã dùng "độ phủ" cho coverage 10 lần. "Độ nhạy" là sensitivity (y học). "Độ đầy đủ" có nguồn giáo trình HUST và không va chạm |
| F1 / F1 score | chỉ số F1 | chỉ số F1; độ đo F; F1-score | d2l; HUST; MLCB | 1 ("F1" là ký hiệu) | |
| event-based F1 | F1 theo sự kiện | event-F1 (KL) | KL (cặp với "F1 theo đoạn") | 2 | Song song với "F1 theo đoạn" đã có ([00:132](../../report/gon_src/00_phan_dau.md#L132)); thay ~45 lần "event-F1" |
| segment-based F1 | F1 theo đoạn | — | KL | 2 | Giữ |
| micro-average | (F1) gộp chung | Micro-average (giữ EN) | MLCB | 2 hoặc 3 | Không tìm thấy "vi mô" trong nguồn học máy tiếng Việt. Hoặc giữ "micro" làm nhãn (khớp công thức $F_1^{micro}$), giải nghĩa "cộng dồn TP, FP, FN của mọi lớp" ở Ch.2 |
| macro-average | (F1) trung bình lớp | Macro-average (giữ EN) | MLCB | 2 hoặc 3 | Như trên; "trung bình theo lớp" mô tả đúng phép tính |
| TP / FP / FN | phát hiện đúng / báo nhầm / bỏ sót | True Positive… (giữ EN) | MLCB | 3 (ký hiệu) + 1 (lời) | KL đã có trong Danh mục viết tắt ([00:93](../../report/gon_src/00_phan_dau.md#L93)) |
| threshold | ngưỡng | ngưỡng (threshold) | MLCB | 1 | KL đã dùng 32 lần |
| confidence interval | khoảng tin cậy | khoảng tin cậy | d2l | 1 | "KTC" là viết tắt từ tiếng Việt — xem mục 4 |
| bootstrap | lấy mẫu lại có hoàn lại (*bootstrap*) | lấy mẫu có hoàn lại (sampling with replacement) | d2l; ĐT DataCamp, CTU | 2 | "bootstrap" là tên phương pháp; viết "khoảng tin cậy bootstrap" sau lần đầu là chấp nhận được |
| metric | chỉ số | phép đo; phép đánh giá; độ đo; chỉ số đánh giá | d2l; HUST; HOU | 1 | KL đã chọn "chỉ số" |
| calibration (ECE) | hiệu chuẩn | — | KL | 1 | "temperature scaling" → "hiệu chuẩn nhiệt độ" (đã có ở [display.yaml:98](../../report/gon_src/display.yaml#L98)) |
| ground truth / reference | nhãn gốc | nhãn gốc | d2l | 1 | |
| relevance / relevant | mức liên quan / phù hợp | văn bản phù hợp | HUST | 1 | |
| nDCG@10, PSDS, mAP, MRR, Hit@k | giữ | giữ | HOU (Hit@1, MRR giữ EN) | 3 | Tên chỉ số; giải nghĩa một lần (đã có trong Danh mục viết tắt) |
| hallucination | ảo giác | ảo giác (hallucination) | HOU; ĐT Ultralytics | 2 | KL đã dùng 30 lần |
| omission | bỏ sót | — | KL | 1 | |
| oracle | trường hợp lý tưởng (biết trước nhãn gốc) | — | (không tìm thấy nguồn) | 2 | |
| ablation | thí nghiệm lược bỏ | — | (không tìm thấy nguồn) | 2 | |
| baseline | hệ so sánh / mốc so sánh | — | (không có trong d2l) | 1 | **Không dùng "hệ cơ sở"** cho nghĩa chung vì KL đã gán "hệ cơ sở" = B0 ([00:134](../../report/gon_src/00_phan_dau.md#L134)) |
| benchmark | bộ dữ liệu chuẩn / bài toán chuẩn | đánh giá xếp hạng | d2l | 1 | Cách dịch của d2l khó hiểu với hội đồng ngoài ngành |

*Dữ liệu và huấn luyện*

| Tiếng Anh | Đề xuất | Đã thấy | Nguồn | Mức | Ghi chú |
|---|---|---|---|---|---|
| training / dev / test set | tập huấn luyện / tập phát triển / tập kiểm tra | như đề xuất; validation set = "tập kiểm định"; "bộ kiểm thử" | d2l; HOU | 1 | Sửa "Tập kiểm định" ở [06:34](../../report/gon_src/06_ket_qua.md#L34) thành "tập phát triển" |
| (data) split | cách chia dữ liệu / tập chia | — | KL ("Mã băm tập chia", display.yaml) | 1 | |
| label | nhãn | — | — | 1 | |
| data leakage | rò rỉ dữ liệu | — | KL (từ khóa [00:21](../../report/gon_src/00_phan_dau.md#L21)) | 2 | Không tìm thấy nguồn từ điển |
| cross-validation | kiểm định chéo **hoặc** kiểm chứng chéo (chọn một) | kiểm định chéo | d2l; KL dùng "kiểm chứng chéo" 5 lần | 2 | d2l là nguồn duy nhất đã kiểm. "Kiểm định" trong thống kê còn có nghĩa kiểm định giả thuyết (kiểm định t Welch), nên giữ "kiểm chứng chéo" cũng có lý; quan trọng là một tên |
| fold | phần (gấp) | "gập" (k-fold = "gập k-lần") | d2l | 2 | Viết "kiểm chứng chéo 5 phần", "mô hình của từng phần"; tránh "fold" trần |
| out-of-fold prediction | dự đoán ngoài mẫu | — | KL | 2 | Giữ |
| random seed | hạt giống ngẫu nhiên (*seed*) | — | (không có trong d2l) | 2 | Trong văn nên diễn đạt lại: "3 lần huấn luyện với 3 hạt giống khác nhau", "gộp 3 lần chạy" thay cho "gộp 3 seed". Chưa tìm thấy nguồn tiếng Việt cho *seed* |
| epoch | vòng huấn luyện (*epoch*) | epoch (khi huấn luyện) | d2l giữ EN | 2 | Người dùng muốn tiếng Việt; "vòng" dễ hiểu, kèm EN lần đầu |
| batch | lô (*batch*) | batch | d2l giữ EN | 2/3 | Ít dùng trong bản gọn |
| checkpoint | bản lưu trọng số (*checkpoint*) | checkpoint (của mô hình) | d2l giữ EN | 2 | 4 lần |
| hyperparameter | siêu tham số | siêu tham số | d2l | 1 | |
| loss (function) | hàm mất mát; giá trị mất mát | hàm mất mát | d2l | 1 | Sửa nhãn hình "Loss huấn luyện" ([display.yaml:147](../../report/gon_src/display.yaml#L147)) thành "Mất mát khi huấn luyện" |
| cross-entropy | entropy chéo | — | (chưa kiểm d2l) | 2 | |
| overfitting | quá khớp | quá khớp (overfit) | d2l | 1 | |
| pre-training | tiền huấn luyện | tiền huấn luyện | d2l | 1 | KL đã dùng 13 lần |
| fine-tuning | huấn luyện tiếp (toàn bộ mô hình) | tinh chỉnh | d2l | 2 | d2l dịch "tinh chỉnh", nhưng KL dành "tinh chỉnh biên" cho LBR. Chọn "huấn luyện tiếp" cho fine-tuning (KL đã viết "huấn luyện thêm trên DataSEC" ở RQ1) và chú thích một lần "(*fine-tuning*, d2l gọi là tinh chỉnh)" |
| frozen (encoder) | đóng băng | trọng số bị đóng băng | d2l | 1 | Phân biệt với "khóa" (tập dữ liệu, cấu hình đã khóa) |
| transfer learning | học chuyển giao | học truyền tải | d2l | 2 | KL dùng "học chuyển giao" ([00:21](../../report/gon_src/00_phan_dau.md#L21), [01:11](../../report/gon_src/01_gioi_thieu.md#L11)). Chưa tìm được nguồn cho "học chuyển giao"; nếu muốn bám d2l thì đổi thành "học truyền tải" |
| data augmentation | tăng cường dữ liệu | tăng cường dữ liệu | d2l | 1 | mixup, FilterAugment là tên riêng → mức 3 |
| knowledge distillation | chưng cất tri thức | — | KL ([04:46](../../report/gon_src/04_phuong_phap.md#L46)) | 2 | Không có trong d2l |
| ensemble | tổ hợp mô hình | gộp mô hình (KL); học tổ hợp; tập hợp mô hình | ĐT interdata, CTU | 2 | Đổi khỏi "gộp" (va chạm 1.2). Không dùng "kết hợp" vì KL đã dành "kết hợp" cho hybrid retrieval |
| gradient boosting (GBM) | cây tăng cường gradient | — | (không có trong d2l; d2l giữ "gradient" trong "hạ gradient") | 2 | |
| cross-fitting | khớp chéo (*cross-fit*) | — | (không tìm thấy nguồn) | 2 | KL đã đặt trong ngoặc ([02:83](../../report/gon_src/02_co_so_ly_thuyet.md#L83)) |
| inference | suy luận | dự đoán / suy luận | d2l | 1 | |

*Âm thanh và phát hiện sự kiện*

| Tiếng Anh | Đề xuất | Đã thấy | Nguồn | Mức | Ghi chú |
|---|---|---|---|---|---|
| sound event detection (SED) | phát hiện sự kiện âm thanh (SED) | — | KL | 2 + 3 (viết tắt) | Giữ viết tắt SED vì dùng ~85 lần |
| polyphonic | đa âm (nhiều nguồn âm chồng nhau) | — | KL | 2 | |
| onset / offset | thời điểm bắt đầu / thời điểm kết thúc | — | KL | 1 | Đã đúng ([01:9](../../report/gon_src/01_gioi_thieu.md#L9)) |
| collar | dung sai (thời gian) | — | KL | 2 | Đã đúng ([02:15](../../report/gon_src/02_co_so_ly_thuyet.md#L15)) |
| frame | khung (thời gian) | — | KL (20 lần) | 1 | |
| posterior (frame-level) | xác suất đầu ra (theo khung) | hậu nghiệm | d2l | 1 | "Hậu nghiệm" đúng về thống kê nhưng khó hiểu; trong SED "posterior" chỉ là đầu ra sigmoid |
| (log-)mel spectrogram | phổ mel (thang log) | Mel-spectrogram (giữ EN) | ĐT bài HOU nhạc cụ | 2 | "mel" là tên thang đo → giữ chữ "mel" |
| feature | đặc trưng | đặc trưng | d2l | 1 | |
| encoder | bộ mã hóa | — | KL (8 lần) | 1 | |
| (classification) head | đầu ra (của mạng) | — | KL ([04:32](../../report/gon_src/04_phuong_phap.md#L32) "hai đầu ra") | 1 | |
| logit | logit | logit | d2l | 3 | |
| pooling | phép gộp (*pooling*) | gộp | d2l | 2 | Giữ "gộp" chỉ cho pooling và lớp gộp nhiều nguồn; đổi "22 lớp gộp" (coarse) thành "22 lớp cấp trên" |
| coarse class / subclass | lớp cấp trên / lớp con | lớp gộp / lớp con (KL) | KL | 1 | Xem va chạm "gộp" |
| merged class (`sirens_and_alarms`) | lớp gộp (nhiều nguồn âm) | — | KL | 1 | |
| boundary refinement (LBR) | tinh chỉnh biên học được (LBR) | — | KL | 2 + 3 | Giữ viết tắt LBR |
| class_id (`glass_breaking`) | tên Việt + mã trong ngoặc: "tiếng kính vỡ (`glass_breaking`)" | — | (quy ước dự án: không dịch mã) | 3 (mã) | Không đổi mã, chỉ thêm tên Việt khi mã xuất hiện trong văn |

*Truy hồi, RAG và LLM*

| Tiếng Anh | Đề xuất | Đã thấy | Nguồn | Mức | Ghi chú |
|---|---|---|---|---|---|
| retrieval | truy hồi | truy xuất; truy hồi; tìm kiếm | HOU (cả hai); AWS, Perplexity (truy xuất); HUST (tìm kiếm) | 2 | KL dùng "truy hồi" 42 lần, "truy xuất" 1 lần → giữ "truy hồi", sửa lần "truy xuất" còn lại. "Truy xuất" phổ biến hơn ở trang công nghiệp |
| retrieval-augmented generation (RAG) | sinh tăng cường truy hồi (RAG) | tạo sinh tăng cường truy xuất; tạo tăng cường truy xuất; tạo sinh truy hồi tăng cường | ĐT Perplexity, AWS; HOU | 2 + 3 | Giữ viết tắt RAG |
| hybrid retrieval | truy hồi kết hợp | tìm kiếm lai; hybrid (giữ EN) | ĐT DataCamp; HOU | 1 | KL đã chọn |
| semantic / vector-only | chỉ theo ngữ nghĩa | truy xuất ngữ nghĩa | HOU | 1 | KL đã chọn |
| backfill | bổ sung | — | KL | 1 | |
| reranking | xếp hạng lại | xếp hạng lại; tái xếp thứ hạng | HOU; ĐT DataCamp | 1 | |
| query | câu truy vấn / câu hỏi | (câu) truy vấn | d2l; HUST | 1 | |
| ranking | xếp hạng | — | HUST | 1 | |
| embedding | vectơ nhúng (*embedding*); mô hình nhúng | embedding (giữ EN); vector nhúng; nội dung nhúng vectơ | d2l; HOU; ĐT Google Codelabs | 2 | KL đã có "mô hình nhúng" trong Danh mục ([00:80](../../report/gon_src/00_phan_dau.md#L80)) |
| vector | vectơ **hoặc** vector (chọn một) | vector | d2l, HOU | 1 | Chọn một chính tả cho cả bài |
| vector index (HNSW) | chỉ mục vectơ | lập chỉ mục | HOU | 1 | |
| cosine similarity | độ tương đồng cô-sin | cô-sin; độ tương đồng; cosine similarity | d2l; HOU | 1 | d2l viết "cô-sin" |
| event store | kho sự kiện | — | KL | 1 | |
| timeline | dòng thời gian sự kiện | — | KL | 1 | |
| corpus | kho (văn bản) | kho ngữ liệu | d2l | 1 | |
| grounded / grounding | bám sát sự kiện (chọn một; bỏ "có căn cứ") | — | KL | 2 | Xem va chạm 1.2 |
| caption / captioning | mô tả / sinh mô tả âm thanh | — | KL | 1 | |
| constrained decoding | giải mã có ràng buộc | — | KL | 2 | |
| grammar (GBNF) | ngữ pháp (GBNF) | — | KL | 1 + 3 | |
| JSON schema | lược đồ JSON | — | KL (display.yaml "Hợp lược đồ") | 2 | |
| parser | bộ phân tích câu hỏi | — | KL | 1 | Sửa "parser" ở [06:213](../../report/gon_src/06_ket_qua.md#L213) |
| prompt | câu lệnh (*prompt*) | Prompt hệ thống (giữ EN) | HOU | 2 | Không tìm được từ Việt ổn định có nguồn |
| token | token (đơn vị từ con) | token | d2l | 3 | Giải nghĩa một lần ở [02:75](../../report/gon_src/02_co_so_ly_thuyet.md#L75) |
| large language model (LLM) | mô hình ngôn ngữ lớn (LLM) | mô hình ngôn ngữ lớn | HOU | 2 + 3 | |
| few-shot / zero-shot | vài ví dụ mẫu / không ví dụ mẫu | — | (không tìm thấy nguồn) | 2 | |

*Hệ thống và phần mềm*

| Tiếng Anh | Đề xuất | Đã thấy | Nguồn | Mức | Ghi chú |
|---|---|---|---|---|---|
| pipeline | chuỗi xử lý / quy trình | pipeline (giữ EN) | d2l, HOU giữ EN | 1 | Bản gọn chỉ còn trong mã sơ đồ |
| end-to-end | từ đầu đến cuối | đầu-cuối | d2l | 1 | KL đã dùng "từ đầu đến cuối" ([01:65](../../report/gon_src/01_gioi_thieu.md#L65)) |
| latency | độ trễ | độ trễ | HOU | 1 | |
| demo | ứng dụng minh họa | — | KL ([01:65](../../report/gon_src/01_gioi_thieu.md#L65)) | 1 | Thay 12 lần "demo" |
| upload | tải lên | — | KL | 1 | |
| frontend / backend | giao diện người dùng / dịch vụ phía máy chủ | backend (giữ EN) | HOU | 1 | |
| endpoint | điểm truy cập API (*endpoint*) | — | KL | 2 | |
| container | vùng chứa (*container*) | — | (không tìm thấy nguồn) | 2/3 | Có thể giữ "container Docker" |
| script | chương trình (Python) | — | KL | 1 | Sửa [06:3](../../report/gon_src/06_ket_qua.md#L3) |
| run | lần chạy | — | KL | 1 | |
| commit, git, manifest, artifact | (chỉ ở phụ lục) "bản ghi thay đổi (commit)", "tệp mô tả lần chạy", "tệp kết quả" | — | KL | 2 | |
| API, CPU, GPU, HTTP, SQL, JSON, Docker, PostgreSQL, pgvector, llama.cpp, PyTorch | giữ | — | — | 3 | Có trong Danh mục viết tắt hoặc là tên riêng |

### Inferences
- **Cặp precision/recall là điểm quyết định.** Nếu dịch, cặp duy nhất vừa có nguồn giáo trình vừa không va chạm trong khóa
  luận là "độ chính xác (*precision*) / độ đầy đủ (*recall*)" (HUST), với điều kiện đổi *accuracy* thành "tỷ lệ phân loại
  đúng" ở chỗ duy nhất nó xuất hiện. Nếu không muốn đổi accuracy, cách bảo vệ được là giữ "precision"/"recall" (d2l, MLCB)
  và giải thích một lần — nhưng như vậy trái yêu cầu "ưu tiên tiếng Việt" của người dùng. Tuyệt đối không dùng "độ phủ".
- **"F1 theo sự kiện"** là thay đổi đáng giá nhất: thay ~45 lần "event-F1", tạo cặp đối xứng với "F1 theo đoạn" đã có.
- Với **micro/macro**, không có từ Việt đã được dùng trong nguồn học máy tiếng Việt mà người nghiên cứu tìm được; hai cách
  hợp lý là (a) giữ "micro/macro" như nhãn kỹ thuật (khớp công thức $F_1^{micro}$), hoặc (b) dùng tên mô tả "gộp chung" /
  "trung bình lớp". Cách (b) dễ hiểu với hội đồng ngoài ngành nhưng dài hơn trong bảng.
- Các từ d2l giữ nguyên (epoch, checkpoint, batch, embedding) **vẫn có thể Việt hóa** theo yêu cầu người dùng nếu kèm tiếng Anh ở
  lần đầu, vì lý do d2l giữ tiếng Anh là thiếu từ Việt ổn định, không phải cấm dịch; khóa luận có Danh mục thuật ngữ để
  khóa nghĩa. Ngoại lệ: token, logit — không có từ Việt ngắn gọn, giữ nguyên.
- Bảng d2l dịch *transfer learning* là "học truyền tải" trong khi khóa luận dùng "học chuyển giao"; cả hai đều hiểu được, nhưng
  chỉ "học truyền tải" là có nguồn đã kiểm.

### Gaps
- Không tìm thấy TCVN hay từ điển thuật ngữ do cơ quan nhà nước ban hành cho học máy/truy hồi thông tin; mọi lựa chọn dựa trên
  bản dịch cộng đồng (d2l), giáo trình đại học (HUST) và bài báo trong nước.
- Không đọc được thân bài tiếng Việt của Google MLCC (trang trả về tiếng Anh) — chỉ có tiêu đề trong kết quả tìm kiếm.
- Không đọc được bài vjs.ac.vn (ảnh quét) và slide CTU (404); các cách gọi "độ phủ (recall)", "tập hợp mô hình" chỉ có ở đoạn trích.
- Không tìm thấy nguồn tiếng Việt cho: seed, oracle, ablation, cross-fitting, few-shot, collar, frame, data leakage, "vi mô/vĩ mô"
  cho micro/macro, "kiểm chứng chéo" (chỉ có "kiểm định chéo" của d2l), "học chuyển giao", "vectơ" (chính tả sách giáo khoa toán).
- Không tìm được luận văn tiếng Việt về phát hiện sự kiện âm thanh để đối chiếu thuật ngữ chuyên ngành (onset/offset, collar,
  polyphonic, PSDS); tìm kiếm chỉ ra bài phân loại âm thanh nhạc cụ giữ "Mel-spectrogram".

## 3. Khóa luận và bài báo tiếng Việt đánh nhãn câu hỏi nghiên cứu, đóng góp, giả thuyết thế nào?

### Takeaway
Không tìm thấy quy ước tiếng Việt thống nhất cho nhãn câu hỏi nghiên cứu ("CH1", "CHNC1" hay "Câu hỏi nghiên cứu 1" đều không
thấy trong luận văn CNTT nào tìm được). Các luận án/bài báo tiếng Việt tìm được thường **liệt kê bằng chữ** ("thứ nhất, thứ
hai…") hoặc **gạch đầu dòng không mã**; mã giả thuyết "H1, H2" phổ biến ở khoa học xã hội. Đồng thời nhiều quy định trường
khuyên **không viết tắt từ tiếng Việt**, nên "CH1" là lựa chọn rủi ro. Dạng an toàn nhất là viết đủ chữ, ngắn: "Câu hỏi 1",
"Đóng góp 1", "Giả thuyết 1".

### Cited Findings
- Bài báo RAG tiếng Việt HOU 2026 nêu đóng góp bằng "Các đóng góp chính của nghiên cứu bao gồm:" và ba gạch đầu dòng không có
  mã (Đề xuất và hiện thực…; So sánh và phân tích…; Đánh giá định lượng…). — [jshou.edu.vn, HOU 2026](https://jshou.edu.vn/houjs/article/download/1173/1001/1705)
- Tóm tắt luận án tiến sĩ về hỏi đáp tự động (UET, ĐHQGHN) trình bày mục tiêu thành các bài toán "thứ nhất", "thứ hai", "thứ
  ba" sau câu "luận án đi vào giải quyết các bài toán sau" (đoạn trích tìm kiếm). — [uet.edu.vn, Tóm tắt LATS (đoạn trích)](https://uet.edu.vn/wp-content/uploads/2021/01/Tomtat_LATS_Tu.pdf)
- Tìm kiếm "CHNC1", "câu hỏi nghiên cứu 1" + "CH1", "RQ1" + "câu hỏi nghiên cứu" trên tạp chí khoa học tiếng Việt không cho kết
  quả nào dùng các nhãn này trong luận văn/bài báo CNTT (ba lượt tìm, kết quả âm tính; ví dụ trang trả về: mẫu bài Tạp chí
  ĐH Thái Nguyên chỉ yêu cầu nêu "mục đích nghiên cứu", không đánh mã RQ). — [tnu.edu.vn, mẫu bài (đoạn trích)](https://tnu.edu.vn/upload/2006712/20240907/58197_TeamplateHoi_thaoKHGD2023_d2506.docx)
- Trong nghiên cứu xã hội học, giả thuyết là "câu trả lời giả định có căn cứ khoa học cho câu hỏi nghiên cứu", thường thể hiện
  bằng quan hệ giữa các biến (ký hiệu H1, H2… theo đoạn trích). — [luatminhkhue.vn (đoạn trích)](https://luatminhkhue.vn/cac-giai-doan-thuc-hien-mot-cuoc-nghien-cuu-xa-hoi-hoc.aspx)
- Quy định viết tắt (từ ghi chú nghiên cứu trước, `vietnamese_plain_writing.md` §1): một quy định (không rõ đơn vị) ghi "Từ
  ngữ, thuật ngữ, tên địa danh tiếng Việt không được phép viết tắt"; FIT NEU: "Không lạm dụng viết tắt", chỉ viết tắt thuật
  ngữ xuất hiện nhiều lần, viết đầy đủ lần đầu; Học viện Tài chính cho viết tắt sau lần viết đầy đủ đầu tiên. —
  [docs.google.com (không rõ đơn vị)](https://docs.google.com/document/d/19GQblHZSPmZYedulP8aQ3Lee6bW-r-BF/export?format=pdf); [FIT NEU](https://fit.neu.edu.vn/post/mot-so-quy-dinh-viet-bao-cao-khoa-luan); [HVTC 2022](https://saudaihoc.hvtc.edu.vn/Upload/VanBan/19062026025950Hướng%20dẫn%20trình%20bày%20luận%20văn,%20đề%20án,%20luận%20án%202022.pdf)
- Hiện trạng khóa luận: "Ba câu hỏi nghiên cứu (Research Question – RQ)" ([01:67](../../report/gon_src/01_gioi_thieu.md#L67)),
  RQ có trong Danh mục viết tắt ([00:107](../../report/gon_src/00_phan_dau.md#L107)); đóng góp đánh mã C1–C6 trong bảng
  ([01:95–100](../../report/gon_src/01_gioi_thieu.md#L95)); "bốn giả thuyết ghi trước" ở phụ lục ([90:98](../../report/gon_src/90_phan_cuoi.md#L98));
  tên hệ đã Việt hóa: hệ mốc, hệ cơ sở, LBR chính, LBR ứng dụng ([00:133–136](../../report/gon_src/00_phan_dau.md#L133));
  nhánh A/B/C cho RQ1 ([01:77](../../report/gon_src/01_gioi_thieu.md#L77)); yêu cầu F1–F5, N1–N3 ([05:17–24](../../report/gon_src/05_trien_khai.md#L17)).

### Inferences
- **Câu hỏi nghiên cứu:** đổi "RQ1–RQ3" thành **"Câu hỏi 1", "Câu hỏi 2", "Câu hỏi 3"** (viết hoa chữ đầu như tên riêng của
  mục), bỏ mục RQ khỏi Danh mục viết tắt. Lần đầu ở [01:67](../../report/gon_src/01_gioi_thieu.md#L67): "Ba câu hỏi nghiên cứu
  (gọi tắt là Câu hỏi 1–3) …". Tiêu đề mục ở Ch.6–7 có thể thêm tên ngắn: "Câu hỏi 1 — Huấn luyện thêm trên DataSEC",
  "Câu hỏi 2 — Mô tả bám sát sự kiện", "Câu hỏi 3 — Truy hồi kết hợp". Không dùng "CH1": đó là viết tắt từ tiếng Việt và
  không thấy dùng trong luận văn CNTT nào. Nếu cần nhãn rất ngắn trong ô bảng hẹp, "CH 1" vẫn rủi ro hơn "Câu hỏi 1"; "RQ1"
  chỉ nên còn ở Abstract tiếng Anh.
- **Đóng góp:** đổi "C1–C6" thành **"Đóng góp 1–6"**. Việc này đồng thời gỡ va chạm chữ "C" với nhánh C. Câu ở
  [01:87](../../report/gon_src/01_gioi_thieu.md#L87) thành "gần với Đóng góp 2, 3 và 4".
- **Giả thuyết:** dùng "Giả thuyết 1–4" thay cho H1–H4 (ở phụ lục); H1/H2 là quy ước khoa học xã hội, không có lợi gì trong
  văn CNTT tiếng Việt.
- **Nhánh của Câu hỏi 1:** có thể giữ chữ A/B/C nhưng gọi kèm tên một lần ("nhánh A — học từ đầu; nhánh B — tiền huấn luyện
  AudioSet; nhánh C — AudioSet rồi DataSEC"), vì chữ cái ngắn hữu ích trong bảng; sau khi bỏ C1–C6 thì "C" chỉ còn một nghĩa.
- **Mã yêu cầu F1–F5, N1–N3:** đổi thành "Chức năng 1–5" và "Phi chức năng 1–3" (hoặc "Yêu cầu chức năng 1…"), để "F1" chỉ còn
  là chỉ số F1.
- **Tên hệ:** giữ bộ tên đã khóa (hệ mốc, hệ cơ sở, LBR chính, LBR ứng dụng); "LBR" là viết tắt tiếng Anh đã định nghĩa nên
  không vi phạm luật "không viết tắt từ tiếng Việt".

### Gaps
- Không tìm thấy hướng dẫn của IUH (hay Bộ GD&ĐT) về cách đánh nhãn câu hỏi nghiên cứu; không tìm được khóa luận CNTT tiếng
  Việt nào có dùng "CH1"/"Câu hỏi nghiên cứu 1" để làm ví dụ đối chứng. Kết luận "không có quy ước" dựa trên kết quả tìm kiếm
  âm tính, không phải trên một nguồn khẳng định.
- Không mở được toàn văn tóm tắt luận án UET và tài liệu luatminhkhue; dữ kiện chỉ ở mức đoạn trích.

## 4. Từ nào nên giữ tiếng Anh, và trình bày thế nào?

### Takeaway
Giữ tiếng Anh cho **tên riêng** (DataSEC, AudioSet, PANNs, BEATs, BGE-M3, PostgreSQL, pgvector, llama.cpp, Qwen), **tên chỉ số và
ký hiệu** (F1 như ký hiệu, PSDS, nDCG@10, MRR, TP/FP/FN), **viết tắt chuẩn** (SED, RAG, LLM, API, CPU, GPU, SQL, JSON),
**token, logit**, và **mã trong mã nguồn** (`class_id`, tên thư viện `sed_eval`). Thuật ngữ Việt hóa ở mức 2 thì kèm tiếng Anh
*in nghiêng trong ngoặc ở lần đầu* và đưa vào Danh mục thuật ngữ; mã định danh để dạng chữ đơn cách (monospace), có tên Việt đi
trước.

### Cited Findings
- ĐH Cần Thơ: thuật ngữ nước ngoài dùng để chú giải "đặt trong dấu ngoặc đơn và in nghiêng"; HCMUTE: chú thích tiếng nước
  ngoài trong ngoặc đơn và có thể lập "danh mục đối chiếu thuật ngữ"; mẫu IUH: tài liệu tham khảo "giữ nguyên văn tiếng nước
  ngoài, không phiên dịch" (theo ghi chú nghiên cứu trước). — [CTU 2026](https://se.ctu.edu.vn/images/upload/bmnv/2026Quydinhtrinhbayluanvanvatieuluantotnghiep); [HCMUTE](https://sdh.hcmute.edu.vn/Resources/Docs/SubDomain/sdh/Bieu%20mau/2026_BieuMau_NCS/III.1.%20Huong%20dan%20trinh%20bay%20LATS,%20TLTQ,%20CD_Nhom%20nganh%20Giao%20duc%20(Ver%201).docx); [Mẫu báo cáo KLTN_DS (tệp cục bộ)](../../report/Mau%20bao%20cao%20KLTN_DS.docx)
- d2l giữ nguyên token, logit, transformer, batch, embedding, epoch, checkpoint, pipeline, vector; MLCB giữ ROC, AUC, TP/FP/FN,
  F1-score. — [d2l.aivivn.com](https://d2l.aivivn.com/glossary.html); [machinelearningcoban.com](https://machinelearningcoban.com/2017/08/31/evaluation/)
- Bài báo tiếng Việt HOU 2026 giữ tên chỉ số Hit@k, MRR và tên mô hình (BAAI/bge-m3, Qwen2.5-7B-Instruct) bằng tiếng Anh, và
  dùng mẫu "tiếng Việt (tiếng Anh)" ở lần đầu: "ảo giác (hallucination)", "truy xuất thông tin (Information Retrieval - IR)". —
  [jshou.edu.vn, HOU 2026](https://jshou.edu.vn/houjs/article/download/1173/1001/1705)
- Khóa luận đã có hai bảng phù hợp: Danh mục thuật ngữ viết tắt ([00:75–113](../../report/gon_src/00_phan_dau.md#L75)) và Danh
  mục thuật ngữ "Tên trong báo cáo | Tiếng Anh | Nghĩa" ([00:117–141](../../report/gon_src/00_phan_dau.md#L117)); danh mục
  viết tắt có cả viết tắt tiếng Việt "KTC" ([00:98](../../report/gon_src/00_phan_dau.md#L98)), "QCVN", "TCVN".
- Quy định "không viết tắt từ tiếng Việt" (một đơn vị không rõ tên) và quy định chỉ viết tắt thuật ngữ dùng nhiều lần (FIT NEU) —
  xem nguồn ở mục 3.

### Inferences
- **Cách trình bày đề xuất:**
  1. Mức 2, lần đầu: "độ đầy đủ (*recall*)", "tổ hợp mô hình (*ensemble*)", "vòng huấn luyện (*epoch*)" — tiếng Anh in nghiêng
     trong ngoặc, sau đó chỉ dùng tên Việt. Lần đầu tính theo **chương đầu tiên xuất hiện** trong thân bài, không tính Tóm tắt.
  2. Mức 3: viết bình thường, không in nghiêng (tên riêng, viết tắt). Giải nghĩa một lần trong câu hoặc trong Danh mục viết tắt.
  3. Mã: chữ đơn cách, tên Việt đi trước — "tiếng kính vỡ (`glass_breaking`)", "thư viện `sed_eval`".
- **Danh mục thuật ngữ** ([00:117–141](../../report/gon_src/00_phan_dau.md#L117)) nên thêm: độ chính xác/độ đầy đủ
  (precision/recall), F1 theo sự kiện, gộp chung/trung bình lớp (micro/macro) nếu dịch, tổ hợp mô hình (ensemble), hạt giống
  ngẫu nhiên (seed), phần (fold), vòng huấn luyện (epoch), bản lưu trọng số (checkpoint), lấy mẫu lại có hoàn lại (bootstrap),
  vectơ nhúng (embedding), phép gộp (pooling), lớp cấp trên (coarse class), huấn luyện tiếp (fine-tuning), ứng dụng minh họa
  (demo). Đổi các dòng hiện còn tiếng Anh ở cột trái: "Seed" ([00:129](../../report/gon_src/00_phan_dau.md#L129)), "Event-F1"
  ([00:131](../../report/gon_src/00_phan_dau.md#L131)), "Kiểm chứng chéo, fold" ([00:127](../../report/gon_src/00_phan_dau.md#L127)),
  "Gộp mô hình" ([00:128](../../report/gon_src/00_phan_dau.md#L128)).
- **"KTC":** vì có quy định cấm viết tắt từ tiếng Việt (dù không rõ đơn vị) và vì chỉ dùng 3 lần trong văn, nên viết đủ "khoảng
  tin cậy 95%" trong văn; nếu cần cho tiêu đề cột bảng thì giữ "KTC 95%" và để trong Danh mục viết tắt (HVTC cho phép viết tắt
  sau lần viết đầy đủ). Đây là rủi ro thấp; quyết định thuộc về người dùng/GVHD.
- **Thứ tự sửa theo lợi ích:** (1) RQ → Câu hỏi, C → Đóng góp, F1–F5 → Chức năng; (2) event-F1 → F1 theo sự kiện; (3) gỡ va chạm
  "độ phủ", "gộp", "tinh chỉnh"; (4) precision/recall, micro/macro (sau khi người dùng chọn phương án); (5) seed, fold, epoch,
  checkpoint, demo, script, parser; (6) các nhãn còn sót trong `display.yaml` ("Precision lớp", "Recall lớp", "Loss huấn luyện",
  "gộp 3 seed", "fold").

### Gaps
- Không có nguồn chính thức của IUH quy định in nghiêng thuật ngữ nước ngoài; đề xuất in nghiêng dựa trên quy định CTU.
- Không kiểm được việc đổi tên trong `display.yaml` có ảnh hưởng tới các kiểm tra tự động của bộ dựng (ví dụ test so tên bảng);
  việc này cần kiểm khi sửa.
