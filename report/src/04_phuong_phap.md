# PHƯƠNG PHÁP

Chương này trình bày phương pháp theo luồng dữ liệu của hệ thống: mô hình phân loại DataSEC, các thế hệ mô hình SED, hậu xử lý, sinh mô tả, truy hồi và giao thức đánh giá. Với mỗi lựa chọn kỹ thuật, báo cáo nêu lý do, cách triển khai (kèm tên mô-đun trong mã nguồn) và cách đánh giá. Quyết định kiến trúc của đề tài được ghi thành các bản ghi quyết định kiến trúc (Architecture Decision Record – ADR) đánh số trong thư mục `docs/decisions/`; báo cáo dẫn số ADR khi cần truy nguồn quyết định.

## Kiến trúc tổng thể

Hệ thống gồm năm khối nối tiếp (⟪fig:architecture⟫). Bản ghi âm thanh đi qua dịch vụ suy luận để thành dòng thời gian sự kiện. Dòng thời gian được dùng theo hai nhánh: sinh mô tả có căn cứ, và lưu vào kho sự kiện để truy hồi. Câu hỏi của người dùng được phân tích thành bộ lọc, truy hồi trên kho sự kiện, rồi trả lời kèm bằng chứng. Ranh giới quan trọng nhất là **hậu xử lý thuộc dịch vụ suy luận, không thuộc mô hình**: ngưỡng và tham số hậu xử lý là artifact hiệu chuẩn trên dev, lưu cạnh checkpoint và nạp khi phục vụ. Nhờ vậy, có thể đổi điểm vận hành mà không cần huấn luyện lại.

![](report/figures/m01_architecture.png){width=15.5cm}

@@CAP:fig:architecture|Kiến trúc tổng thể của hệ thống và các dịch vụ triển khai@@

@@NOTE:Nguồn: scripts/build_midterm_figures.py; đối chiếu services/, ml/inference/, docker-compose.yml.@@

Bảng ⟪tbl:codes⟫ giải thích các mã nội bộ được dùng trong báo cáo. Các mã này cần thiết vì đề tài so sánh nhiều thế hệ mô hình và nhiều tổ hợp ensemble, và mỗi mã ứng với một thư mục run có manifest đầy đủ.

@@CAP:tbl:codes|Mã nội bộ của các thế hệ mô hình và ứng viên SED@@

| Mã | Ý nghĩa |
|---|---|
| A, B, C | Ba nhánh khởi tạo của RQ1: học từ đầu; khởi tạo AudioSet; khởi tạo AudioSet rồi huấn luyện thêm trên DataSEC |
| v1 | Công thức SED ban đầu: CNN14 nén thời gian /64, 8 epoch (Mục 4.3.2) |
| v2 | Công thức SED cải tiến: CNN14 nén /8, BiGRU 2×256, 30 epoch, tăng cường dữ liệu (Mục 4.3.3) |
| T2a | Bộ mã hóa BEATs tiền huấn luyện theo khung, đóng băng, cộng đầu BiGRU (Mục 4.3.4) |
| T2b | Bộ mã hóa Frame-MobileNet tiền huấn luyện theo khung, tinh chỉnh toàn bộ (Mục 4.3.4) |
| a – e | Ứng viên dựa trên v1/v2: a = ensemble C của v1; b = một run v2; c = ensemble 3 seed v2; d = ensemble 3 seed C-v2; e = ensemble 6 model B-v2 và C-v2 |
| f1 – f4 | Ứng viên Track 2: f1 = T2a×3; f2 = T2b×3; f3 = T2a×3 + B-v2×3; f4 = T2b×3 + B-v2×3 |
| g1, g2 | Ứng viên dùng focal loss: g1 = T2b focal×3; g2 = g1 kết hợp f2 |
| S13 | Vòng chọn hệ thống SED cuối cùng; hệ được khóa là f2 |

@@NOTE:Nguồn: ADR-0030, ADR-0031 §4, ADR-0032, ADR-0038; docs/measurements/s13_selection_20261018.md.@@

## Mô hình phân loại phân cấp trên DataSEC

Mô hình phân loại DataSEC đóng hai vai trò: là bước giữa của nhánh C trong RQ1, và trả lời câu hỏi phụ về việc tách lớp con. Mô hình dùng một bộ mã hóa CNN14 khởi tạo từ checkpoint AudioSet và hai đầu tuyến tính, một cho 22 lớp gộp và một cho 28 lớp con (ADR-0016). Checkpoint gốc có các khối tiền xử lý và đầu phân loại AudioSet mà bộ mã hóa của đề tài không có. Vì vậy, chỉ sáu khối tích chập được chuyển sang với ánh xạ khóa tường minh, chiếm 92,23% tham số; lớp chuẩn hóa đầu vào được thay bằng chuẩn hóa theo thống kê tập huấn luyện DataSEC (ADR-0018). Hàm mất mát gồm ba thành phần:

$$\mathcal{L} = \mathcal{L}_{CE}^{coarse} + \lambda_{sub}\,\mathcal{L}_{CE}^{sub} + \lambda_{cons}\,\mathcal{L}_{cons}, \qquad \mathcal{L}_{cons} = -\frac{1}{|V|}\sum_{i \in V}\log \sum_{k \in \mathcal{F}(y_i)} q_{i,k}$$

⟪eqno:hier⟫

trong đó $q_{i,k}$ là xác suất softmax của lớp con $k$ cho mẫu $i$, $\mathcal{F}(y_i)$ là "gia đình" lớp con thuộc lớp gộp đúng $y_i$, và $V$ là tập mẫu có lớp con (12 lớp gộp không có lớp con bị loại khỏi hai số hạng sau). Số hạng nhất quán $\mathcal{L}_{cons}$ phạt việc đặt khối lượng xác suất vào gia đình sai, điều mà cross-entropy 28 lớp một mình không phạt khi lớp đúng vẫn có xác suất lớn nhất. Trong cài đặt (`ml/models/hierarchical.py`), $\lambda_{sub} = 1$, còn $\lambda_{cons} = 0{,}5$ được chọn bằng quét trên dev với ràng buộc không làm giảm macro-F1. Vì 57,5% dữ liệu thuộc hai lớp, mô hình dùng bộ lấy mẫu cân bằng lớp. Khả năng tái lập được kiểm bằng cách huấn luyện hai lần cùng seed: hai checkpoint có SHA-256 giống hệt nhau.

## Mô hình phát hiện sự kiện âm thanh

### Hàm mất mát và trọng số lớp dương

Mọi mô hình SED dự đoán logit $z_{t,c}$ cho 21 lớp đa âm theo từng khung. Huấn luyện dùng cửa sổ 10 s, và các khung đệm (padding) không được đưa vào hàm mất mát. Hàm mất mát là binary cross-entropy có mặt nạ và trọng số lớp dương (`ml/training/sed.py::masked_bce`):

$$\mathcal{L}_{SED} = \frac{1}{|M|\cdot C}\sum_{t \in M}\sum_{c=1}^{C}\Big[-w_c\,y_{t,c}\log\sigma(z_{t,c}) - (1-y_{t,c})\log\big(1-\sigma(z_{t,c})\big)\Big]$$

⟪eqno:bce⟫

với $M$ là tập khung hợp lệ và $C = 21$. Trọng số $w_c$ bù mất cân bằng giữa thời gian dương và âm của lớp $c$ trên tập huấn luyện:

$$w_c = \min\left(w_{max},\ \max\left(1,\ \frac{T - P_c}{P_c}\right)\right)$$

⟪eqno:posweight⟫

trong đó $T$ là tổng thời lượng huấn luyện, $P_c$ là tổng thời lượng có nhãn dương của lớp $c$, và $w_{max}$ là trần (`estimate_pos_weight`). Trần $w_{max}$ là một siêu tham số: v1 dùng 50, còn từ v2 dùng 10 sau ablation trên dev (ADR-0028).

### Thế hệ v1 và ba nhánh của RQ1

Ở thế hệ v1, nhánh A dùng một mạng CRNN nhỏ (ba khối tích chập và BiGRU) học từ đầu trên `logmel_v1` 50 khung/s. Nhánh B và C dùng bộ mã hóa CNN14 trên `logmel_panns_v1` 100 khung/s: B khởi tạo từ checkpoint AudioSet, C khởi tạo từ bộ mã hóa của mô hình phân loại DataSEC (ADR-0002, ADR-0020). Ba nhánh có cùng tập chia, cùng ngân sách 8 epoch, cùng cửa sổ 10 s bước 5 s, và cùng quy trình hậu xử lý được hiệu chuẩn độc lập trên dev của từng nhánh.

Phân tích sau đó cho thấy một giới hạn cấu trúc của v1. CNN14 trong mã nguồn đề tài gộp (pooling) trục thời gian ở cả sáu khối, tức nén 64 lần. Ở 100 khung/s, mỗi quyết định vì thế ứng với khối khoảng 0,64 s, và đầu ra được lặp lại (nearest) để khớp nhịp nhãn. Phép "đo trần độ phân giải" (Mục 6.3.1) cho thấy riêng giới hạn này đã chặn event-F1 ở 0,6294, ngay cả khi mô hình nhận dạng hoàn hảo.

### Thế hệ SED v2

SED v2 sửa các nguyên nhân đã đo được thay vì dò siêu tham số (ADR-0030). Thứ nhất, bộ mã hóa chỉ gộp thời gian ở ba khối đầu (nén /8, tức 80 ms mỗi khung), giữ nguyên trọng số tiền huấn luyện. Thứ hai, một BiGRU hai lớp 256 đơn vị chạy ở nhịp bộ mã hóa, sau đó logit mới được lặp lên 100 khung/s. Thứ ba, công thức huấn luyện được mở rộng thành 30 epoch, khởi động (warmup) 1 epoch rồi giảm cosine; tốc độ học của bộ mã hóa là $3\cdot10^{-4}$ (chọn bằng pilot trên dev) và của đầu là $10^{-3}$. Huấn luyện dùng cắt cửa sổ ngẫu nhiên mỗi epoch, mixup với xác suất 0,5 và nhãn mềm [@zhang2018mixup], FilterAugment với xác suất 0,5 trong biên độ ±6 dB [@nam2022filteraugment], và trần trọng số dương 10. Checkpoint được chọn theo macro average precision theo khung trên dev, đại lượng không phụ thuộc ngưỡng. Mỗi thành phần được đánh giá bằng ablation bỏ-từng-phần trên dev (Mục 6.3.2).

### Track 2: bộ mã hóa tiền huấn luyện theo khung

Dựa trên kết quả "đóng băng gần bằng tinh chỉnh" của Schmid và cộng sự [@schmid2025effective], đề tài thử hai bộ mã hóa tiền huấn luyện trên AudioSet Strong với độ phân giải 40 ms (ADR-0032), sau khi mỗi bộ vượt một cổng khả thi về bộ nhớ GPU và độ khớp đầu ra.

- **T2a** dùng BEATs [@chen2022beats] bản đã tiền huấn luyện theo khung, **đóng băng** hoàn toàn (khoảng 90,4 triệu tham số), cộng đầu BiGRU của v2 (khoảng 3,3 triệu tham số huấn luyện). Phổ fbank theo chuẩn Kaldi được viết lại bằng PyTorch và kiểm trùng từng bit với torchaudio.
- **T2b** dùng Frame-MobileNet (`frame_mn10`, khoảng 3 triệu tham số), **tinh chỉnh toàn bộ**, không có mô hình chuỗi. Đầu vào là dạng sóng 16 kHz, biểu diễn 128 mel; đầu ra 250 bước cho 10 s (40 ms mỗi bước) qua một lớp tuyến tính 21 lớp, rồi lặp lên lưới nhãn 10 ms (`ml/models/frame_mn_finetune.py`). Huấn luyện 30 epoch, một tốc độ học $3\cdot10^{-4}$ chọn bằng pilot, chỉ dùng mixup, trần trọng số dương 10.

Checkpoint ngoài được kiểm SHA-256 và giấy phép mã nguồn (MIT) trước khi dùng. Một nhánh phụ thay binary cross-entropy bằng focal loss $\gamma = 2$ trên T2b (ADR-0038) để thử cải thiện lớp hiếm; nhánh này cho các ứng viên g1 và g2.

### Ensemble và tập ứng viên

Vì huấn luyện SED không tất định ngay cả khi cùng seed và cùng mã nguồn (Mục 6.7), mỗi cấu hình được chạy ba seed và các ứng viên là ensemble trung bình xác suất:

$$\bar{p}_{t,c} = \frac{1}{K}\sum_{k=1}^{K}\sigma\big(z^{(k)}_{t,c}\big)$$

⟪eqno:ensemble⟫

Các thành viên phải khớp tuyệt đối về bản ghi, độ lệch cửa sổ, mặt nạ, nhãn, thứ tự lớp và hash hệ lớp; nếu không, ensemble bị từ chối (`ml/evaluation/ensemble.py`). Danh sách 11 ứng viên của vòng chọn cuối (⟪tbl:codes⟫) và luật chọn được ghi **trước** khi có kết quả (ADR-0031 §4): chọn ứng viên có event-F1 micro cao nhất theo kiểm chứng chéo 5 fold trên dev annotated, chia fold theo nhóm rò rỉ.

⟪fig:sedarch⟫ minh họa kiến trúc của v2 và của hệ f2, hệ được khóa ở vòng chọn cuối.

![](report/figures/m02_sed_architectures.png){width=15.5cm}

@@CAP:fig:sedarch|Kiến trúc SED v1, v2 và hệ f2 (T2b × 3 + cSEBB)@@

@@NOTE:Nguồn: scripts/build_midterm_figures.py; ml/models/panns.py, ml/models/frame_mn_finetune.py, ADR-0030, ADR-0032.@@

## Hậu xử lý và lựa chọn trên dev

### Ngưỡng và ưu tiên thời lượng

Họ hậu xử lý thứ nhất gồm bốn bước: lọc trung vị độ rộng $w_c$, so ngưỡng $\theta$, gộp khoảng trống ngắn hơn $g^{max}_c$, rồi bỏ sự kiện ngắn hơn $d^{min}_c$ (`ml/postprocessing/events.py`). Ba tham số độ dài được suy từ phân bố thời lượng trên tập **huấn luyện**: $d^{min}_c$ là phân vị 5, còn $g^{max}_c$ là phân vị 50 theo ADR-0003 hoặc phân vị 25 theo lựa chọn sau này (ADR-0024). Ngưỡng $\theta$ được quét trên dev trong lưới $\{0{,}05; 0{,}10; \dots; 0{,}95\}$. Ban đầu đề tài dùng ngưỡng riêng cho từng lớp. Ablation A2 cho thấy cách này có 21 bậc tự do và quá khớp tập dev (Mục 6.3.2), nên từ ADR-0024 họ này dùng ngưỡng chung (global) và được chọn bằng kiểm chứng chéo 5 fold trên dev (`scripts/select_postproc_cv.py`).

### Hậu xử lý cSEBB

Họ thứ hai là cSEBB [@ebbers2024sound], được đề tài tự viết lại theo mô tả trong bài báo (`ml/postprocessing/sebb.py`). Đề tài không dùng mã tham chiếu vì mã đó theo giấy phép AGPL. Với độ dài bộ lọc bậc $\tau$ ($h = \tau/2$ khung mỗi phía), chuỗi chênh lệch tại biên khung $t$ là

$$\Delta_c(t) = \frac{1}{h}\sum_{j=0}^{h-1}p_{t+j,c} - \frac{1}{h}\sum_{j=1}^{h}p_{t-j,c}$$

⟪eqno:sebb⟫

Cực đại dương của $\Delta_c$ mở sự kiện, cực tiểu âm đóng sự kiện. Khoảng trống được gộp khi điểm thấp nhất của nó gần đỉnh của cả hai sự kiện kề theo một ngưỡng tuyệt đối hoặc tương đối. Độ tin cậy của mỗi hộp là trung bình posterior trong hộp, và ngưỡng $\lambda$ chỉ quyết định giữ hay bỏ hộp. Lưới chọn trên dev gồm $\tau \in \{0{,}32; 0{,}48; 0{,}64; 0{,}96; 1{,}28\}$ s, sáu kiểu gộp (tuyệt đối 0,15/0,2/0,3; tương đối 1,5/2/3) và $\lambda$ trong lưới ngưỡng chung. Với mỗi ứng viên, họ hậu xử lý (ngưỡng hay cSEBB) và tham số của nó đều được chọn bằng kiểm chứng chéo trên dev. Hệ f2 được khóa với cSEBB $\tau = 0{,}64$ s và gộp tương đối 2.

## Sinh mô tả có căn cứ

### Ba ràng buộc G1–G3

Bộ sinh mô tả nhận **duy nhất** dòng thời gian sau hậu xử lý. Nó không nhận âm thanh, phổ hay siêu dữ liệu bối cảnh. Thiết kế này có chủ ý: bộ sinh không thể bịa một nguồn âm mà nó chưa từng thấy bằng chứng, và căn cứ trở thành một bất biến cấu trúc thay vì một mục tiêu mềm. Mỗi mô tả phải thỏa ba ràng buộc, và mỗi ràng buộc có kiểm thử tự động:

- **G1:** mọi nguồn âm được nhắc thuộc tập lớp của dòng thời gian, kiểm bằng từ điển cụm từ → `class_id`.
- **G2:** mọi lần nhắc có `event_id` làm bằng chứng.
- **G3:** không có từ trong từ điển cấm về nguyên nhân, ý định, bối cảnh hay mức nguy hiểm, chẳng hạn *emergency*, *crime*, *intruder*.

Hai lớp gộp phải giữ mức mơ hồ của bằng chứng (Mục 3.2). Dòng thời gian rỗng được mô tả là "không phát hiện sự kiện thuộc các lớp mục tiêu", không phải "bản ghi im lặng".

### Bốn chế độ sinh

RQ2 so sánh bốn chế độ trên **cùng một** dự đoán SED đã đóng băng:

- **Template** sinh câu tất định từ dòng thời gian. Chế độ này có căn cứ theo thiết kế và dùng để kiểm tra bộ đo hoạt động đúng.
- **Unconstrained** dùng LLM Qwen3.5-9B (bản lượng tử Q4_K_M, chạy cục bộ bằng llama.cpp, nhiệt độ 0, seed cố định) sinh tự do từ dòng thời gian (ADR-0022).
- **Constrained** dùng cùng mô hình và cùng lời nhắc, chỉ thêm một ngữ pháp giải mã phụ thuộc đầu vào, viết theo định dạng GBNF (GGML Backus–Naur Form) của llama.cpp (ADR-0023). Ngữ pháp chỉ cho phép *một* câu liệt kê một dãy con các sự kiện theo thứ tự onset, mỗi sự kiện tối đa một lần, với cụm từ nguồn âm từ từ điển và thời điểm lấy đúng từ sự kiện. Nhờ vậy, ảo giác nguồn âm, từ cấm, thời điểm bịa và sai thứ tự đều bị loại bỏ *theo cấu tạo*; mô hình chỉ còn quyền chọn nhắc sự kiện nào và dừng ở đâu.
- **Constrained-cover** bắt buộc nhắc sự kiện đầu tiên của mỗi lớp (ADR-0026). Bỏ sót lớp vì thế cũng bị loại theo cấu tạo, và khác biệt duy nhất với constrained là đúng một ràng buộc này.

Vì kết quả sinh tham lam của llama.cpp chỉ tất định theo đúng chuỗi yêu cầu (bộ nhớ đệm lời nhắc làm đổi phép tính số thực), việc tái lập phải sinh lại cả tệp theo đúng thứ tự.

### Mô tả tiếng Việt

Mô tả tiếng Anh dùng cho đánh giá, mô tả tiếng Việt dùng cho giao diện. Mô tả tiếng Việt được sinh bằng template tất định với từ điển tiếng Việt tách riêng, khớp có giữ dấu (ADR-0025). Từ điển được tách riêng để hash của từ điển tiếng Anh, dùng cho RQ2, không thay đổi. Việc khớp phải giữ dấu vì nếu bỏ dấu, ràng buộc G3 khớp nhầm, ví dụ cụm "tới phạm vi" bị đọc thành "tội phạm".

⟪fig:timeline⟫ đặt cạnh nhau dòng thời gian nhãn gốc và dòng thời gian do hệ f2 dự đoán trên bản ghi dev S-0009. Mô tả constrained-cover sinh từ dự đoán là: *"The sound of jet aircrafts can be heard from 0.3 to 10.0 seconds, followed by the sound of birds from 10.0 to 29.2 seconds and the sound of birds from 90.0 to 108.8 seconds."* Mọi nguồn âm và mốc thời gian trong câu đều có sự kiện dự đoán tương ứng, nên câu mô tả hợp lệ theo G1–G3. Tuy vậy, so với nhãn gốc, câu mô tả đặt tiếng máy bay phản lực sai chỗ và bỏ qua ba sự kiện xung cùng một sự kiện xe chạy qua. Đây chính là khoảng cách giữa "có căn cứ" và "đúng với âm thanh" được phân tích ở Mục 4.7.2 và Mục 6.4.

![](report/figures/m05_dev_timeline.png){width=15.5cm}

@@CAP:fig:timeline|Dòng thời gian nhãn gốc và dự đoán của hệ f2 trên bản ghi dev S-0009@@

@@NOTE:Nguồn: ml/runs/sed_ensemble_s13_f2_20260929T045053Z/captions/constrained_cover_dev.jsonl (tập dev, mức oracle và đầu–cuối); sinh bằng scripts/build_midterm_figures.py.@@

## Truy hồi và trả lời có bằng chứng

### Kho sự kiện và tài liệu truy hồi

Kho sự kiện dùng PostgreSQL 16 với phần mở rộng pgvector (ADR-0005). Lựa chọn này cho phép bộ lọc thuộc tính, vị từ thời gian và xếp hạng vector nằm trong **một** câu truy vấn của ngôn ngữ truy vấn có cấu trúc (Structured Query Language – SQL). Bảng `events` chứa cả nhãn gốc lẫn dự đoán, phân biệt bằng cột `provenance`, để hệ thống không bao giờ đánh giá mô hình trên chính đầu ra của nó. Mỗi bản ghi có một tài liệu truy hồi ghép mô tả template tiếng Anh và tiếng Việt với một tóm tắt sự kiện chuẩn hóa (lớp, thời điểm, số sự kiện, độ đa âm lớn nhất), vì mô tả tự nhiên hay bỏ qua con số (ADR-0027). Tài liệu được nhúng bằng BGE-M3 1024 chiều [@chen2024m3], chuẩn hóa độ dài, và xếp hạng theo khoảng cách cosine.

### Ba chế độ truy hồi và vị từ thời gian

Ba chế độ được so sánh cho RQ3 (`ml/retrieval/store.py`):

- **structured_only** chỉ dùng bộ lọc cứng, xếp kết quả theo onset sớm nhất của lớp được lọc.
- **vector_only** chỉ xếp hạng cosine trên mọi tài liệu, không lọc.
- **hybrid** lọc cứng trước, rồi xếp hạng cosine bên trong tập đã lọc.

Bộ lọc gồm tập lớp phải có mặt, ràng buộc thời lượng và một vị từ thời gian giữa hai lớp $a$, $b$ trong cùng bản ghi (⟪tbl:predicates⟫). Mỗi vị từ được viết **một lần** ở dạng SQL (cho truy hồi) và dạng Python (cho việc tính độ liên quan từ nhãn gốc). Một kiểm thử chạy dạng SQL trên SQLite và so với dạng Python, bảo đảm hai bên cùng ngữ nghĩa (`ml/retrieval/temporal.py`).

@@CAP:tbl:predicates|Bốn vị từ thời gian giữa sự kiện a và b (τ là dung sai khai báo trong truy vấn, mặc định 0)@@

| Vị từ | Điều kiện | Ví dụ câu hỏi |
|---|---|---|
| before | $t^{off}_a \le t^{on}_b + \tau$ | Tiếng kính vỡ trước tiếng còi |
| after | $t^{on}_a \ge t^{off}_b - \tau$ | Tiếng còi sau tiếng kính vỡ |
| overlaps | $t^{on}_a < t^{off}_b \ \wedge\ t^{on}_b < t^{off}_a$ | Tiếng nói chồng với tiếng máy |
| within | $t^{on}_a \ge t^{on}_b \ \wedge\ t^{off}_a \le t^{off}_b$ | Tiếng chim trong lúc có tiếng công trường |

@@NOTE:Nguồn: ml/retrieval/temporal.py (bảng PREDICATES).@@

### Bộ phân tích câu hỏi

Để người dùng không phải tự đặt bộ lọc, câu hỏi tiếng Việt hoặc tiếng Anh được chuyển thành bộ lọc JSON bằng cùng LLM cục bộ, với ràng buộc giải mã bằng lược đồ JSON (JavaScript Object Notation) Schema (ADR-0036). Lược đồ được sinh tự động từ 21 lớp đa âm và bốn vị từ, nên mô hình không thể sinh một lớp hay vị từ không tồn tại. Ngữ pháp chỉ bảo đảm *hình thức*, không bảo đảm *nghĩa*: một bộ lọc hợp lược đồ vẫn có thể đảo vai trò $a/b$ hoặc chọn sai vị từ. Vì vậy, độ đúng ngữ nghĩa được đo riêng (Mục 6.6). Trên giao diện, bộ lọc được hiển thị dưới dạng thẻ (chip) cho người dùng sửa trước khi truy vấn. Khi LLM không chạy, giao diện báo lỗi rõ và chuyển sang lọc thủ công.

### Trả lời ràng buộc bằng chứng

Câu trả lời được sinh **tất định** từ các bản ghi đã truy hồi (`ml/retrieval/answer.py`) theo bốn ràng buộc:

- **A1:** mỗi câu nhắc lại một sự kiện bằng chứng (lớp và khoảng thời gian).
- **A2:** không có kết quả thì trả `evidence: []` kèm bộ lọc đã áp, không suy diễn.
- **A3:** không nêu nguyên nhân hay mức nguy hiểm, dùng chung từ điển cấm với G3.
- **A4:** bộ lọc đã áp được trả về nguyên văn để người dùng hiểu vì sao kết quả rỗng.

Một bộ kiểm độc lập đọc lại văn bản câu trả lời và báo mọi khẳng định về lớp hoặc thời gian không có bằng chứng tương ứng; đây là cơ sở của tỷ lệ khẳng định thiếu bằng chứng (unsupported-claim rate).

## Giao thức đánh giá

### Chọn trên dev, kiểm tra một lần

Ba tập trả lời ba câu hỏi khác nhau. Tập train dùng để tối ưu mô hình và suy duration prior. Tập dev dùng để chọn ngưỡng, checkpoint và cấu hình. Tập test chỉ dùng để đo cấu hình đã chọn, **một lần**. Kể từ SED v2, quy trình được siết thêm. Các run huấn luyện không sinh dự đoán test. Lựa chọn trên dev được commit vào git **trước** khi sinh logit test bằng một đường riêng (`scripts/dump_predictions.py`), và tùy chọn `--verify-dev` chứng minh đường này tái tạo trùng từng bit logit dev lúc huấn luyện. Mọi lần chạm test đều được ghi vào một sổ sinh tự động. Tất cả cấu hình đã chạy trên test đều được báo cáo, kể cả cấu hình kém, và không cấu hình nào được chọn lại sau khi xem test.

### Metric cho mô tả và truy hồi

Gọi $\mathcal{M}$ là tập lần nhắc nguồn âm trong một mô tả (trích bằng từ điển) và $\mathcal{C}$ là tập lớp trong dòng thời gian. Tỷ lệ ảo giác và tỷ lệ bỏ sót của một mô tả là

$$H = 1 - \frac{|\{m \in \mathcal{M} : m \in \mathcal{C}\}|}{|\mathcal{M}|}, \qquad O = 1 - \frac{|\{c \in \mathcal{C} : c \text{ được nhắc}\}|}{|\mathcal{C}|}$$

⟪eqno:halluc⟫

rồi lấy trung bình trên các bản ghi. Bỏ sót được tính theo **lớp**, không theo sự kiện. Khi một cụm từ mơ hồ ánh xạ được tới nhiều lớp, cách tính nghiêng về phía có lợi cho mô tả, nên hiệu số giữa hai chế độ là một cận dưới. Ngoài ra, đề tài báo tỷ lệ cặp lần nhắc đúng thứ tự onset (không phải Kendall τ), tỷ lệ gọi tên quá cụ thể (ví dụ nói "xe cứu thương" khi lớp chỉ là `sirens_and_alarms`), tỷ lệ thêm bối cảnh, và tỷ lệ từ cấm.

**Phạm vi diễn giải của metric này cần được nêu rõ.** Ở mức đầu–cuối, $\mathcal{C}$ là tập lớp của dòng thời gian **dự đoán**. Vì vậy, $H = 0$ chỉ có nghĩa là mô tả trung thành với đầu ra SED, không có nghĩa là mô tả đúng với âm thanh. Một sự kiện mà SED phát hiện sai sẽ được mô tả "có căn cứ" nhưng vẫn sai so với thực tế. Mức oracle, dùng nhãn gốc làm dòng thời gian, tách riêng phần lỗi do bộ sinh mô tả.

Với truy hồi, gọi $R_q$ là tập bản ghi liên quan của truy vấn $q$, tính từ **nhãn gốc** bằng đúng ngữ nghĩa vị từ của bộ lọc, và $r_i$ là bản ghi xếp hạng $i$. Cài đặt (`scripts/evaluate_retrieval.py`) dùng độ liên quan nhị phân:

$$\text{Recall@}k = \frac{|\{r_1..r_k\} \cap R_q|}{|R_q|}, \qquad \text{nDCG@}10 = \frac{\sum_{i=1}^{10}\mathbb{1}[r_i \in R_q]/\log_2(i+1)}{\sum_{i=1}^{\min(|R_q|,10)}1/\log_2(i+1)}$$

⟪eqno:ndcg⟫

MRR là nghịch đảo hạng của kết quả liên quan đầu tiên. Độ đúng bộ lọc (filter exactness) là tỷ lệ kết quả trả về thỏa **mọi** bộ lọc cứng trên sự kiện đã lưu. Chế độ structured_only và hybrid phải đạt 1,000; thấp hơn là lỗi kiến trúc chứ không phải hiệu năng kém. Bộ truy vấn gồm 100 câu thuộc bốn nhóm (21 một lớp, 27 nhiều lớp, 30 quan hệ thời gian, 22 thời lượng), được chọn theo nhãn gốc của tập **train** trước khi xem kết quả. Trên test có 97/100 câu có ít nhất một bản ghi liên quan.

### Khoảng tin cậy bootstrap

Khung thời gian không độc lập với nhau, nên đơn vị lấy mẫu lại là **bản ghi**. Với thống kê $S$ (event-F1, PSDS, tỷ lệ ảo giác…), khoảng tin cậy 95% là khoảng phân vị của $S$ trên $B = 1000$ mẫu lại có hoàn lại, mỗi mẫu gồm $n$ bản ghi rút từ $n$ bản ghi gốc (`ml/evaluation/bootstrap.py`, seed 20260922). Với truy hồi, đơn vị lấy mẫu lại là truy vấn. Khi so hai hệ thống trên cùng tập, hiệu số được bootstrap **ghép cặp**. Với so sánh nhiều seed, đề tài dùng thêm kiểm định t của Welch trên giá trị của từng run. Quy tắc diễn giải là: chênh lệch nằm trong khoảng tin cậy chồng lấp, hoặc nhỏ hơn độ lệch chuẩn giữa các fold hay giữa các seed, **không** được gọi là cải thiện.
