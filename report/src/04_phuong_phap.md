# PHƯƠNG PHÁP

Chương này trình bày phương pháp theo luồng dữ liệu của hệ thống: mô hình phân loại, các thế hệ mô hình SED, bước ghép thành sự kiện, sinh mô tả, truy hồi và cách đánh giá. Mỗi lựa chọn đều nêu lý do. Các quyết định thiết kế được ghi thành bản ghi quyết định kiến trúc (ADR) trong thư mục `docs/decisions/`; báo cáo dẫn số ADR khi cần truy nguồn.

## Kiến trúc tổng thể

Hệ thống gồm năm khối nối tiếp (⟪fig:architecture⟫). Bản ghi âm đi qua dịch vụ suy luận để thành danh sách sự kiện. Danh sách này được dùng theo hai hướng: sinh mô tả bám sát sự kiện, và lưu vào kho sự kiện để truy hồi. Câu hỏi của người dùng được chuyển thành bộ lọc, truy hồi trong kho, rồi trả lời kèm bằng chứng. Ranh giới quan trọng nhất là **bước ghép xác suất thành sự kiện thuộc dịch vụ suy luận, không thuộc mô hình**: ngưỡng và tham số là kết quả hiệu chuẩn trên dev, lưu cạnh checkpoint và nạp khi phục vụ. Nhờ vậy đổi được điểm vận hành mà không cần huấn luyện lại.

![](report/figures/m01_architecture.png){width=13cm}

@@CAP:fig:architecture|Kiến trúc tổng thể của hệ thống@@

@@NOTE:Nguồn: scripts/build_midterm_figures.py; đối chiếu services/, ml/inference/, docker-compose.yml.@@

Đề tài so sánh nhiều thế hệ mô hình nên báo cáo dùng một số mã gọi tắt, giải thích ở ⟪tbl:codes⟫. Mỗi mã ứng với một thư mục huấn luyện có đầy đủ cấu hình để tái lập.

@@CAP:tbl:codes|Các mã gọi tắt của mô hình và ứng viên SED@@

| Mã | Ý nghĩa |
|---|---|
| A, B, C | Ba nhánh của RQ1: học từ đầu; khởi tạo AudioSet; AudioSet rồi huấn luyện thêm trên DataSEC |
| v1 | Công thức SED ban đầu: CNN14 nén thời gian 64 lần, 8 epoch |
| v2 | Công thức cải tiến: nén 8 lần, BiGRU 2×256, 30 epoch, tăng cường dữ liệu |
| T2a, T2b | Bộ mã hóa tiền huấn luyện theo khung: BEATs đóng băng (T2a); Frame-MobileNet tinh chỉnh toàn bộ (T2b) |
| a – e | Ứng viên từ v1/v2: a = ensemble C của v1; b = một run v2; c = ensemble 3 seed v2; d = ensemble 3 seed C-v2; e = ensemble 6 mô hình B-v2 và C-v2 |
| f1 – f4 | Ứng viên Track 2: f1 = T2a×3; f2 = T2b×3; f3 = T2a×3 + B-v2×3; f4 = T2b×3 + B-v2×3 |
| g1, g2 | Ứng viên dùng focal loss: g1 = T2b focal×3; g2 = g1 kết hợp f2 |
| S13 | Vòng chọn hệ thống SED cuối cùng; hệ được khóa là **f2** |

@@NOTE:Nguồn: ADR-0030, ADR-0031 §4, ADR-0032, ADR-0038; docs/measurements/s13_selection_20261018.md.@@

## Mô hình phân loại trên DataSEC

Mô hình phân loại có hai vai trò: là bước giữa của nhánh C trong RQ1, và trả lời câu hỏi phụ về việc tách lớp con. Mô hình gồm bộ mã hóa CNN14 khởi tạo từ checkpoint AudioSet và hai đầu tuyến tính, một cho 22 lớp gộp và một cho 28 lớp con (ADR-0016). Checkpoint gốc có các khối tiền xử lý và đầu phân loại mà bộ mã hóa của nhóm không có, nên chỉ sáu khối tích chập được chuyển sang, chiếm 92,23% tham số (ADR-0018). Lớp chuẩn hóa đầu vào được thay bằng chuẩn hóa theo thống kê tập huấn luyện DataSEC.

Hàm mất mát có thêm một số hạng "nhất quán" phạt việc đặt xác suất lớp con vào sai lớp gộp — điều mà cross-entropy 28 lớp một mình không phạt khi lớp đúng vẫn có xác suất cao nhất. Hệ số của số hạng này là 0,5, chọn bằng quét trên dev với điều kiện không làm giảm macro-F1. Vì `voices` và `music` chiếm 57,5% dữ liệu, huấn luyện dùng lấy mẫu cân bằng lớp. Khi huấn luyện hai lần cùng seed, hai checkpoint có SHA-256 giống hệt nhau.

## Mô hình phát hiện sự kiện (SED)

**Hàm mất mát.** Mô hình SED dự đoán xác suất cho 21 lớp ở từng khung trên cửa sổ 10 s; mất mát là binary cross-entropy có mặt nạ cho khung đệm, kèm trọng số lớp dương có trần (v1: 50; từ v2: 10 sau ablation trên dev, ADR-0028) để bù việc thời gian "có sự kiện" ít hơn nhiều.

**Thế hệ v1 và ba nhánh của RQ1.** Nhánh A dùng mạng CRNN nhỏ (ba khối tích chập và BiGRU) học từ đầu. Nhánh B và C dùng CNN14: B khởi tạo từ AudioSet, C khởi tạo từ bộ mã hóa của mô hình phân loại DataSEC (ADR-0002, ADR-0020). Ba nhánh cùng tập chia, cùng 8 epoch, cùng cửa sổ 10 s bước 5 s, và bước ghép được hiệu chuẩn riêng trên dev của từng nhánh.

Phân tích sau đó cho thấy v1 có một giới hạn cấu trúc: CNN14 trong mã nguồn gộp trục thời gian ở cả sáu khối, tức nén 64 lần, nên mỗi quyết định ứng với khối khoảng 0,64 s. Phép đo ở Chương 6 cho thấy riêng giới hạn này đã chặn event-F1 ở 0,6294, ngay cả khi mô hình nhận dạng hoàn hảo.

**Thế hệ v2.** SED v2 sửa các nguyên nhân đã đo được thay vì dò siêu tham số (ADR-0030): chỉ gộp thời gian ở ba khối đầu (nén 8 lần, 80 ms mỗi khung); thêm BiGRU hai lớp 256 đơn vị; huấn luyện 30 epoch với tốc độ học giảm dần; và dùng tăng cường dữ liệu gồm cắt cửa sổ ngẫu nhiên, mixup [@zhang2018mixup] và FilterAugment [@nam2022filteraugment]. Checkpoint được chọn theo average precision theo khung trên dev, đại lượng không phụ thuộc ngưỡng. Từng thành phần được đánh giá bằng ablation bỏ-từng-phần trên dev.

**Bộ mã hóa tiền huấn luyện theo khung (Track 2).** Dựa trên kết quả "đóng băng gần bằng tinh chỉnh" [@schmid2025effective], nhóm thử hai bộ mã hóa tiền huấn luyện trên AudioSet Strong có độ phân giải 40 ms (ADR-0032), sau khi mỗi bộ vượt cổng kiểm tra về bộ nhớ GPU và độ khớp đầu ra:

- **T2a** dùng BEATs [@chen2022beats] **đóng băng** hoàn toàn (khoảng 90,4 triệu tham số), cộng đầu BiGRU của v2 (khoảng 3,3 triệu tham số được huấn luyện).
- **T2b** dùng Frame-MobileNet (`frame_mn10`, khoảng 3 triệu tham số), **tinh chỉnh toàn bộ**, không có mô hình chuỗi. Đầu vào là sóng âm 16 kHz; đầu ra 250 bước cho 10 s qua một lớp tuyến tính 21 lớp, rồi nội suy lên lưới nhãn 10 ms.

Checkpoint ngoài được kiểm SHA-256 và giấy phép (MIT) trước khi dùng. Một nhánh phụ thay mất mát bằng focal loss trên T2b (ADR-0038) tạo ra ứng viên g1 và g2.

**Gộp nhiều mô hình.** Vì huấn luyện SED không tất định kể cả khi cùng seed, mỗi cấu hình chạy ba seed và ứng viên là trung bình xác suất của các mô hình (ensemble), chỉ được gộp khi bản ghi, mặt nạ, nhãn và hệ lớp khớp tuyệt đối. Danh sách 11 ứng viên và luật chọn được ghi **trước** khi có kết quả (ADR-0031): chọn ứng viên có event-F1 micro cao nhất theo kiểm chứng chéo 5 fold trên dev, chia fold theo nhóm trùng.

## Ghép xác suất thành sự kiện

Có hai cách ghép, và cách nào cũng được chọn trên dev.

**Ngưỡng.** Làm mượt xác suất bằng lọc trung vị, so với ngưỡng $\theta$, gộp khoảng trống ngắn và bỏ sự kiện quá ngắn; hai giới hạn độ dài suy từ tập **huấn luyện** (sự kiện ngắn nhất: phân vị 5; khoảng trống tối đa: phân vị 50 theo ADR-0003 hoặc 25 theo ADR-0024). Ngưỡng riêng cho từng lớp có 21 bậc tự do và quá khớp dev (Chương 6), nên từ ADR-0024 nhóm dùng một ngưỡng chung, chọn bằng kiểm chứng chéo 5 fold trên dev.

**cSEBB.** Nhóm tự cài đặt cSEBB theo bài báo [@ebbers2024sound] (không dùng mã tham chiếu vì giấy phép AGPL). Ý chính: so trung bình xác suất của một cửa sổ ngắn ngay trước và sau mỗi thời điểm; chỗ tăng mạnh nhất mở sự kiện, chỗ giảm mạnh nhất đóng sự kiện; hai sự kiện gần nhau được gộp nếu chỗ lõm giữa chúng không sâu; ngưỡng chỉ quyết định giữ hay bỏ sự kiện, không dời biên. Hệ f2 được khóa với cửa sổ 0,64 s và gộp theo tỷ lệ 2.

## Sinh mô tả bám sát sự kiện

**Ba ràng buộc.** Bộ sinh mô tả chỉ nhận danh sách sự kiện sau khi ghép, không nhận âm thanh hay thông tin bối cảnh. Thiết kế này có chủ ý: bộ sinh không thể bịa một nguồn âm mà nó chưa thấy bằng chứng. Mỗi mô tả phải thỏa ba ràng buộc, đều có kiểm thử tự động:

- **G1:** mọi nguồn âm được nhắc đều thuộc danh sách sự kiện (kiểm bằng từ điển cụm từ → lớp).
- **G2:** mỗi lần nhắc đều gắn với mã sự kiện làm bằng chứng.
- **G3:** không có từ về nguyên nhân, ý định, bối cảnh hay nguy hiểm, như *emergency*, *crime*, *intruder*.

Hai lớp gộp phải giữ mức mơ hồ (Chương 3). Danh sách rỗng được mô tả là "không phát hiện sự kiện thuộc các lớp mục tiêu", không phải "bản ghi im lặng".

**Bốn cách sinh.** RQ2 so bốn cách trên **cùng một** kết quả SED đã khóa:

- **Template**: câu tất định từ danh sách sự kiện; bám sát theo thiết kế, dùng để kiểm tra bộ đo.
- **Unconstrained**: mô hình ngôn ngữ Qwen3.5-9B (bản nén Q4_K_M, chạy cục bộ bằng llama.cpp, nhiệt độ 0) viết tự do (ADR-0022).
- **Constrained**: cùng mô hình và lời nhắc, nhưng bị giới hạn bằng một ngữ pháp giải mã (ADR-0023). Ngữ pháp chỉ cho phép một câu liệt kê một dãy con các sự kiện theo thứ tự bắt đầu, mỗi sự kiện tối đa một lần, với tên nguồn âm lấy từ từ điển và thời điểm lấy đúng từ sự kiện. Nhờ vậy ảo giác nguồn âm, từ cấm, thời điểm bịa và sai thứ tự bị loại *theo cấu tạo*; mô hình chỉ còn chọn nhắc sự kiện nào và dừng ở đâu.
- **Constrained-cover**: như constrained, nhưng bắt buộc nhắc sự kiện đầu tiên của mỗi lớp (ADR-0026), nên bỏ sót lớp cũng bị loại theo cấu tạo.

Mô tả tiếng Anh dùng cho đánh giá; mô tả tiếng Việt dùng cho giao diện, sinh bằng template với từ điển tiếng Việt riêng và khớp có giữ dấu (ADR-0025). Từ điển tách riêng để mã băm của từ điển tiếng Anh dùng cho RQ2 không đổi; giữ dấu vì bỏ dấu sẽ khiến G3 khớp nhầm, như "tới phạm vi" bị đọc thành "tội phạm".

⟪fig:timeline⟫ đặt cạnh nhau danh sách sự kiện từ nhãn gốc và từ dự đoán của hệ f2 trên bản ghi dev S-0009. Mô tả constrained-cover sinh từ dự đoán là: *"The sound of jet aircrafts can be heard from 0.3 to 10.0 seconds, followed by the sound of birds from 10.0 to 29.2 seconds and the sound of birds from 90.0 to 108.8 seconds."* Mọi nguồn âm và mốc thời gian trong câu đều có sự kiện dự đoán tương ứng, nên câu hợp lệ theo G1–G3. Nhưng so với nhãn gốc, câu đặt tiếng máy bay phản lực sai chỗ và bỏ qua ba sự kiện xung và một sự kiện xe chạy qua. Đây là khoảng cách giữa "bám sát dự đoán" và "đúng với âm thanh" được phân tích ở phần đánh giá và Chương 6.

![](report/figures/m05_dev_timeline.png){width=13cm}

@@CAP:fig:timeline|Sự kiện nhãn gốc và dự đoán của hệ f2 trên bản ghi dev S-0009@@

@@NOTE:Nguồn: ml/runs/sed_ensemble_s13_f2_20260929T045053Z/captions/constrained_cover_dev.jsonl (tập dev, mức oracle và đầu–cuối); sinh bằng scripts/build_midterm_figures.py.@@

## Truy hồi và trả lời có bằng chứng

**Kho sự kiện.** Nhóm dùng PostgreSQL 16 với phần mở rộng pgvector (ADR-0005), để bộ lọc, điều kiện thời gian và xếp hạng vector nằm trong **một** câu truy vấn SQL. Bảng sự kiện chứa cả nhãn gốc lẫn dự đoán, phân biệt bằng một cột nguồn gốc, để không đánh giá mô hình trên chính đầu ra của nó. Mỗi bản ghi có một tài liệu truy hồi ghép mô tả template tiếng Anh, tiếng Việt và một tóm tắt sự kiện chuẩn hóa (lớp, thời điểm, số sự kiện), vì mô tả tự nhiên hay bỏ qua con số (ADR-0027). Tài liệu được nhúng bằng BGE-M3 (1024 chiều) [@chen2024m3] và xếp hạng theo khoảng cách cosine.

**Ba chế độ truy hồi** được so sánh cho RQ3: **structured_only** chỉ lọc cứng; **vector_only** chỉ xếp hạng cosine, không lọc; **hybrid** lọc cứng trước rồi xếp hạng cosine trong tập đã lọc. Bộ lọc gồm tập lớp phải có mặt, ràng buộc thời lượng và một điều kiện thời gian giữa hai lớp $a$, $b$ trong cùng bản ghi (⟪tbl:predicates⟫). Mỗi điều kiện được viết một lần dạng SQL (để truy hồi) và một lần dạng Python (để tính độ liên quan từ nhãn gốc); một kiểm thử so hai dạng trên SQLite để bảo đảm cùng ngữ nghĩa.

@@CAP:tbl:predicates|Bốn điều kiện thời gian giữa sự kiện a và b@@

| Điều kiện | Ý nghĩa | Ví dụ câu hỏi |
|---|---|---|
| before | a kết thúc trước khi b bắt đầu | Tiếng kính vỡ trước tiếng còi |
| after | a bắt đầu sau khi b kết thúc | Tiếng còi sau tiếng kính vỡ |
| overlaps | a và b chồng nhau | Tiếng nói chồng với tiếng máy |
| within | a nằm trọn trong b | Tiếng chim trong lúc có tiếng công trường |

@@NOTE:Nguồn: ml/retrieval/temporal.py (bảng PREDICATES); điều kiện có dung sai τ khai báo trong truy vấn, mặc định 0.@@

**Bộ phân tích câu hỏi.** Câu hỏi tiếng Việt hoặc tiếng Anh được chuyển thành bộ lọc JSON bằng cùng mô hình ngôn ngữ cục bộ, bị ràng buộc bởi lược đồ sinh từ 21 lớp và bốn điều kiện (ADR-0036), nên không thể tạo lớp hay điều kiện không tồn tại. Lược đồ chỉ bảo đảm *hình thức*, không bảo đảm *nghĩa* (vẫn có thể đảo vai trò a/b), nên độ đúng ngữ nghĩa được đo riêng (Chương 6). Trên giao diện, bộ lọc hiện thành thẻ để người dùng sửa trước khi truy vấn.

**Câu trả lời có bằng chứng** được sinh tất định từ các bản ghi đã truy hồi: mỗi câu nhắc lại một sự kiện bằng chứng (lớp, khoảng thời gian); không có kết quả thì trả danh sách bằng chứng rỗng kèm bộ lọc đã áp, không suy diễn; không nêu nguyên nhân hay mức nguy hiểm. Một bộ kiểm độc lập đếm khẳng định không có bằng chứng tương ứng (tỷ lệ khẳng định thiếu bằng chứng).

## Cách đánh giá

**Chọn trên dev, kiểm tra một lần.** Tập train dùng để tối ưu mô hình và suy giới hạn độ dài. Tập dev dùng để chọn ngưỡng, checkpoint và cấu hình. Tập test chỉ dùng để đo cấu hình đã chọn, **một lần**. Từ SED v2, quy trình được siết thêm: các lần huấn luyện không sinh dự đoán test; lựa chọn trên dev được commit vào git **trước** khi sinh dự đoán test bằng một đường riêng, và một tùy chọn kiểm chứng đường này tái tạo trùng từng bit dự đoán dev. Mọi lần chạm test được ghi vào một sổ sinh tự động. Mọi cấu hình đã chạy trên test đều được báo cáo, kể cả cấu hình kém, và không cấu hình nào được chọn lại sau khi xem test.

**Chỉ số cho mô tả.** Gọi $\mathcal{M}$ là tập nguồn âm được nhắc trong một mô tả (trích bằng từ điển) và $\mathcal{C}$ là tập lớp trong danh sách sự kiện. Tỷ lệ ảo giác $H$ và tỷ lệ bỏ sót $O$ là

$$H = 1 - \frac{|\{m \in \mathcal{M} : m \in \mathcal{C}\}|}{|\mathcal{M}|}, \qquad O = 1 - \frac{|\{c \in \mathcal{C} : c \text{ được nhắc}\}|}{|\mathcal{C}|}$$

⟪eqno:halluc⟫

rồi lấy trung bình trên các bản ghi. Bỏ sót tính theo **lớp**, không theo sự kiện. Khi một cụm từ mơ hồ ứng với nhiều lớp, cách tính nghiêng về phía có lợi cho mô tả, nên hiệu số giữa hai cách sinh là một cận dưới. Nhóm còn báo tỷ lệ cặp nhắc đúng thứ tự thời gian, tỷ lệ gọi tên quá cụ thể (ví dụ nói "xe cứu thương" khi lớp chỉ là `sirens_and_alarms`), tỷ lệ thêm bối cảnh và tỷ lệ dùng từ cấm.

**Phạm vi diễn giải cần nêu rõ.** Ở mức đầu–cuối, $\mathcal{C}$ là tập lớp của danh sách **dự đoán**. Vì vậy $H = 0$ chỉ có nghĩa là mô tả trung thành với đầu ra SED, không có nghĩa là đúng với âm thanh: một sự kiện SED phát hiện sai vẫn được mô tả "có căn cứ" nhưng sai so với thực tế. Mức oracle, dùng nhãn gốc làm danh sách, tách riêng phần lỗi do bộ sinh mô tả.

**Chỉ số cho truy hồi.** Gọi $R_q$ là tập bản ghi liên quan của truy vấn $q$, tính từ **nhãn gốc** bằng đúng ngữ nghĩa của bộ lọc, và $r_i$ là bản ghi xếp thứ $i$. Với độ liên quan nhị phân:

$$\text{Recall@}k = \frac{|\{r_1..r_k\} \cap R_q|}{|R_q|}, \qquad \text{nDCG@}10 = \frac{\sum_{i=1}^{10}\mathbb{1}[r_i \in R_q]/\log_2(i+1)}{\sum_{i=1}^{\min(|R_q|,10)}1/\log_2(i+1)}$$

⟪eqno:ndcg⟫

MRR là nghịch đảo hạng của kết quả liên quan đầu tiên. Độ đúng bộ lọc là tỷ lệ kết quả thỏa **mọi** bộ lọc cứng; structured_only và hybrid phải đạt 1,000, thấp hơn là lỗi kiến trúc chứ không phải hiệu năng kém. Bộ truy vấn gồm 100 câu thuộc bốn nhóm (21 một lớp, 27 nhiều lớp, 30 quan hệ thời gian, 22 thời lượng), chọn theo nhãn tập **train** trước khi xem kết quả; trên test có 97/100 câu có ít nhất một bản ghi liên quan.

**Khoảng tin cậy.** Các khung thời gian không độc lập, nên đơn vị lấy mẫu lại là **bản ghi**: khoảng tin cậy 95% là khoảng phân vị của chỉ số trên 1000 mẫu lại có hoàn lại (seed 20260922); với truy hồi, đơn vị là truy vấn. Khi so hai hệ thống trên cùng tập, hiệu số được bootstrap **ghép cặp**; khi so nhiều seed, nhóm dùng thêm kiểm định t của Welch. Quy tắc diễn giải: chênh lệch có khoảng tin cậy chồng lấp, hoặc nhỏ hơn độ lệch chuẩn giữa các fold hay các seed, **không** được gọi là cải thiện.
