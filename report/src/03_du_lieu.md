# DỮ LIỆU VÀ QUY TRÌNH CHUẨN BỊ DỮ LIỆU

Chương này mô tả hai bộ dữ liệu, hệ lớp và quy trình chuẩn bị dữ liệu D0–D4. Quy trình được thiết kế để mọi tệp đều có nguồn gốc, mọi tệp bị loại đều có lý do, và mọi tập chia đều được đóng băng bằng hash trước khi huấn luyện. Mọi con số trong chương được sinh từ các tệp kiểm kê (manifest) và báo cáo đo do script tạo ra; tệp nguồn ghi dưới mỗi bảng.

## Hai bộ dữ liệu

Hai bộ dữ liệu được công bố trên Zenodo theo giấy phép CC-BY-NC-SA-4.0 và được mô tả trong một bài báo trên *Scientific Data* [@fredianelli2025environmental]. Thông tin giấy phép lấy từ bản ghi Zenodo, vì hai tệp nén không chứa tệp LICENSE. Ràng buộc "chia sẻ tương tự" (share-alike) có nghĩa là nếu công bố mô hình huấn luyện từ dữ liệu này thì mô hình cũng phải theo cùng giấy phép.

Đề tài không dùng các con số thống kê trong bài báo. Lý do là phiên bản DataSEC mà bài báo mô tả (4.292 tệp) cũ hơn phiên bản đề tài tải về, còn phần DataSED trong bài có số tệp và tổng thời lượng khác với tệp nén thực tế. Mọi thống kê dưới đây được đo trực tiếp từ tệp nén. Toàn vẹn của tệp nén được kiểm bằng kích thước và MD5 trước khi giải nén: DataSEC 6.414.663.316 byte, DataSED 4.510.378.259 byte, cả hai khớp giá trị công bố.

### DataSEC

DataSEC (bản ghi Zenodo 17033970, phiên bản 3) gồm 5.048 tệp WAV đơn kênh 44,1 kHz, tổng 23,71 giờ. Nhãn được suy từ cây thư mục và có hai cấp: 22 lớp gộp (coarse) và 28 lớp con thuộc 10 lớp gộp. Phân bố lớp lệch mạnh. Hai lớp `voices` (1.900 tệp, 37,6%) và `music` (1.001 tệp, 19,8%) chiếm 57,5% bộ dữ liệu, trong khi lớp nhỏ nhất chỉ có 50 tệp, tức tỷ lệ khoảng 38:1. Ở cấp lớp con, bốn nút có dưới 25 tệp (`crickets`, `olive_shaker`, `magpies`, `lawn_mower`), nên mỗi nút chỉ có 3–4 mẫu test. Hệ quả cho phương pháp là phải lấy mẫu cân bằng lớp khi huấn luyện (Mục 4.2) và chỉ báo số tuyệt đối cho các nút có ít hơn 10 mẫu test.

### DataSED

DataSED (bản ghi Zenodo 15346092) gồm 717 bản ghi WAV 44,1 kHz (716 đơn kênh, 1 hai kênh), tổng 18,68 giờ, độ dài trung bình khoảng 94 s. Bộ dữ liệu có hai phiên bản nhãn mạnh trên cùng tập âm thanh. Bản đa âm (polyphonic) gồm 4.034 sự kiện thuộc 21 lớp và phủ 703 bản ghi; bản đơn âm (monophonic) gồm 4.309 sự kiện thuộc 22 lớp và phủ đủ 717 bản ghi. Độ dài sự kiện đa âm trải rộng, từ 0,41 s tới 296,5 s, trung vị 5,8 s. Đề tài lấy bản đa âm làm benchmark chính vì môi trường thực tế là đa âm và vì nhiệm vụ yêu cầu phát hiện các sự kiện chồng lấp.

## Hệ lớp: 22 lớp gộp và 21 lớp đa âm

Hệ lớp phiên bản 0.1 (SHA-256 `67ca8a8c…`) định nghĩa 22 `class_id` dạng snake_case tiếng Anh, ánh xạ một–một từ nhãn gốc. Ánh xạ này được xác minh trực tiếp trên tệp nén: 22/22 lớp gộp và 10/10 nhóm lớp con khớp, không có nhãn nào nằm ngoài hệ lớp. Bảng đầy đủ ở Phụ lục A. Nhãn gốc (`source_label`) được giữ nguyên để truy nguồn gốc; nhãn lạ làm quy trình dừng thay vì được ánh xạ mềm.

Cần phân biệt rõ hai tập lớp được dùng trong đề tài:

- **22 lớp** của hệ lớp được dùng cho phân loại DataSEC và cho bản nhãn đơn âm của DataSED.
- **21 lớp đa âm** được dùng cho đầu ra của mô hình SED. Lớp `wind_turbine` không có trong bản nhãn đa âm, nên đầu SED phải lấy danh sách lớp từ `polyphonic_class_ids` (21) chứ không phải `class_ids` (22).

Kết quả trên 21 lớp đa âm và trên 22 lớp đơn âm **không được so sánh trực tiếp**, vì khác tập lớp, khác định nghĩa nhãn và khác mẫu số khi tính macro.

Hai lớp gộp `sirens_and_alarms` và `thunder_fireworks_gunshot` chứa các nguồn âm khác bản chất (còi báo động khác chuông báo; sấm khác pháo hoa và tiếng súng). DataSED chỉ có nhãn ở cấp lớp gộp, nên mọi mô tả về sự kiện thuộc hai lớp này phải giữ đúng mức mơ hồ của bằng chứng. Chẳng hạn, mô tả được viết "một âm thanh xung giống sấm, pháo hoa hoặc tiếng súng", không được viết "một tiếng súng". Ràng buộc này được kiểm thử trong phần sinh mô tả (Mục 4.5).

## Quy trình chuẩn bị dữ liệu D0–D4

Quy trình gồm các cổng kiểm tra nối tiếp; cổng sau chỉ chạy khi cổng trước đạt (⟪fig:pipeline⟫).

![](report/figures/m04_data_pipeline.png){width=15.5cm}

@@CAP:fig:pipeline|Quy trình chuẩn bị dữ liệu D0–D4 và các artifact đóng băng@@

@@NOTE:Nguồn: scripts/build_midterm_figures.py, đọc data/manifests/{datasec,datased}_inventory_summary.json, datased_preparation_audit.json, duplicate_audit.json và hai tệp split đóng băng.@@

### Kiểm chứng tệp nén và kiểm kê (D0–D1)

Cổng D0 đọc thư mục trung tâm của tệp ZIP và kiểm kích thước cùng MD5 **trước** khi giải nén, đồng thời đối chiếu cây nhãn với hệ lớp. Một lỗi được phát hiện ngay ở bước này: tùy chọn bỏ qua kiểm MD5 ban đầu khiến kết luận luôn là "sai checksum". Sau khi sửa, việc bỏ qua kiểm tra được ghi thành một kết luận riêng, `pass_unverified_md5`, để không bao giờ bị đọc nhầm thành "đạt". Cổng D1 kiểm kê từng tệp, ghi tần số lấy mẫu, số kênh, thời lượng và SHA-256. Hai bộ đặc trưng log-mel được trích trước để không giải mã lại âm thanh ở mỗi epoch: `logmel_v1` (16 kHz, 64 mel, bước 320 mẫu, tức 50 khung/s) cho mô hình học từ đầu, và `logmel_panns_v1` (32 kHz, 64 mel, bước 320 mẫu, tức 100 khung/s, 50–14.000 Hz) cho các bộ mã hóa họ PANNs.

### Hợp đồng chú giải (D2)

Cổng D2 chuẩn hóa nhãn DataSED thành bảng sự kiện có mã sự kiện, mã bản ghi, nhãn gốc, `class_id`, onset và offset tính bằng giây. Kiểm tra cho thấy không có dòng nhãn trùng và độ vượt biên cuối bản ghi lớn nhất chỉ khoảng 5 ms. Nhãn gốc không bao giờ bị sửa. Khi nghi ngờ một nhãn, đề tài ghi lại phân tích lỗi thay vì chỉnh dữ liệu.

### Khử trùng lặp nội bộ và xuyên bộ dữ liệu (D3)

D3 là cổng quan trọng nhất đối với RQ1. Hai bộ dữ liệu có cùng sáu tác giả, cùng miền đo và công bố cách nhau bốn tháng. Vì vậy, giả định mặc định của đề tài là hai bộ *có khả năng* dùng chung bản ghi gốc, cho tới khi đo được điều ngược lại. Việc tìm trùng lặp được thực hiện ba tầng, cả trong từng bộ dữ liệu lẫn xuyên hai bộ:

- **T1** so SHA-256 của byte tệp để tìm tệp giống hệt nhau.
- **T2** so SHA-256 của tín hiệu điều chế mã xung (Pulse-Code Modulation – PCM) sau khi giải mã và lấy mẫu lại về 16 kHz đơn kênh.
- **T3** so dấu vân tay âm học.

Ở T3, dấu vân tay của mỗi khung 1 s gồm 20 hệ số cepstral thang mel (Mel-Frequency Cepstral Coefficients – MFCC) (bỏ hệ số $C_0$) cùng giá trị tuyệt đối của delta, được chuẩn hóa z-score theo thống kê toàn kho. Hai tệp được so bằng độ tương đồng cosine trung bình trên đoạn chồng lấp dài nhất (ADR-0007).

Ngưỡng của T3 được hiệu chuẩn bằng dữ liệu. Tập dương gồm 24 cặp giống hệt byte, tập âm gồm 5.000 cặp ngẫu nhiên khác nhãn. Với dấu vân tay viết đúng nguyên văn đặc tả ban đầu, 52,6% cặp âm vượt ngưỡng xem xét. Sau khi bỏ $C_0$ và chuẩn hóa theo kho, giá trị nhỏ nhất của cặp dương là 1,0000, giá trị lớn nhất của cặp âm là 0,9205, và không cặp âm nào đạt 0,95. Từ đó, ngưỡng được đặt như sau: cặp có đoạn chồng lấp từ 3 s trở lên được coi là `duplicate` khi độ tương đồng ≥ 0,95 và đưa vào hàng đợi xem xét khi nằm trong [0,85; 0,95). Một quan sát dẫn tới thêm điều kiện về độ dài: các cặp xem xét giả có đoạn chồng lấp trung vị đúng 1 s, sinh ra do so sánh bội trên khoảng 16,6 triệu cặp. Vì vậy, cặp chồng lấp ngắn hơn 3 s không bao giờ được tự động coi là trùng (ADR-0009).

@@CAP:tbl:leakage|Kết quả cổng khử trùng lặp D3 và cổng kiểm tra rò rỉ D4@@

@@INCLUDE:docs/thesis/tables/02_leakage_d3_d4.md@@

Kết quả ở ⟪tbl:leakage⟫ xác nhận rủi ro rò rỉ là có thật. Có ba nhóm trùng xuyên bộ dữ liệu, trong đó hai cặp đạt độ tương đồng 1,000000 trên đoạn chồng lấp dài 35 s và 13 s: `Sirens-0046` (DataSEC) với `S-0233` (DataSED), và `Sirens-0067` với `S-0211`. Cặp thứ ba là `Train-0012` với `S-0213`, độ tương đồng 0,9548 trên 31 s. Ngoài ra, 35 cặp xuyên bộ dữ liệu thuộc vùng xem xét được duyệt tay bằng cách nghe trực tiếp: 10 cặp kết luận trùng, 1 cặp không chắc (được xử lý thận trọng như trùng) và 24 cặp khác nhau. Sau D3, 11 đoạn DataSEC trùng với bản ghi DataSED thuộc tập dev hoặc test bị loại khỏi dữ liệu tiền huấn luyện. Con số này bằng 0,2179% của DataSEC, nằm trong dải "nhỏ" (dưới 1%) mà kế hoạch dữ liệu quy định là loại bỏ, ghi nhận và vẫn giữ hiệu lực của RQ1. Bên trong DataSEC còn 119 đoạn bị loại vì là bản sao trong cùng nhóm trùng, nên tổng số đoạn không vào tập chia là 130.

### Chia tập theo nhóm rò rỉ (D4)

Đơn vị chia tập là **nhóm rò rỉ** (`leakage_group`), không phải tệp hay cửa sổ. Một nhóm gồm các tệp giống hệt byte, các nhóm trùng của D3 và các cặp tương tự cao bị buộc nằm cùng tập. DataSED được chia 60/20/20 theo recording bằng phân tầng đa nhãn lặp (iterative multilabel stratification) trên 21 nhãn có mặt, seed 20260922 (ADR-0008). DataSEC được chia 70/15/15 theo lớp gộp. Ngưỡng gom cặp tương tự vào cùng nhóm được đặt ở 0,93, trên mức nhiễu đã đo (0,9205). Nếu dùng 0,85, hiện tượng nối chuỗi tạo ra một khối 315 tệp có mật độ cạnh chỉ 0,024, trộn tiếng nói với tiếng nổ, và làm tỷ lệ chia lệch 5 điểm phần trăm (ADR-0012).

@@CAP:tbl:split|Hai bộ dữ liệu và tập chia đã đóng băng@@

@@INCLUDE:docs/thesis/tables/01_data_split.md@@

Kết quả chia tập được tóm tắt trong ⟪tbl:split⟫. Cổng D4 kiểm năm điều kiện trước khi đóng băng: không nhóm nào nằm ở hai tập, không SHA-256 nào nằm ở hai tập, không cặp trùng nào xuyên tập, mọi lớp có mẫu ở mỗi tập, và các đoạn đã loại thực sự vắng mặt. Cả hai bộ dữ liệu đạt 5/5. Cổng này được chứng minh **không đạt rỗng**: khi gỡ danh sách loại trừ ra, kiểm tra thứ năm thất bại và chỉ đúng tệp `Sirens-0046.wav`. Phép thử ngược này cần thiết vì trong quá trình làm, hai lỗi lệch không gian tên định danh (`recording_id` so với `file_id`) từng làm mọi phép giao thành rỗng, và một phép giao rỗng thì luôn báo "sạch". Hai tập chia được đóng băng bằng SHA-256; nếu tệp chia bị sửa sau khi đóng băng, cổng D4 từ chối chạy.

## Độ phủ nhãn và độ nhất quán chú giải

### Độ phủ nhãn gốc đa âm

Khi đọc kỹ tệp nén, đề tài phát hiện bản nhãn đa âm chỉ phủ 703/717 bản ghi. Mười bốn bản ghi `S-0704` đến `S-0717`, đúng là tập bản ghi mang nhãn `wind_turbine`, không có dòng nhãn đa âm nào nhưng vẫn nằm trong tập chia benchmark: 8 bản ghi ở train, 3 ở dev và 3 ở test. Nếu chấm điểm trên các bản ghi này, mọi dự đoán trên đó bị tính là báo động nhầm, dù thực chất chúng chỉ thiếu nhãn. Đề tài không chia lại tập (vì tập chia đã đóng băng) mà bổ sung một tập đánh giá `annotated`, chỉ gồm bản ghi có nhãn đa âm: dev còn 134 và test còn 139 bản ghi (ADR-0034). Từ vòng chọn hệ thống cuối, mọi kiểm chứng chéo và đánh giá test đều dùng tập này. Các kết quả cũ trên tập `all` (142 bản ghi test) được giữ nguyên và ghi rõ tập đánh giá khi trích.

### Độ nhất quán giữa hai lần chú giải

DataSED chứa 8 cặp bản ghi giống hệt byte nhưng được chú giải độc lập hai lần. Đây là một phép đo độ nhất quán chú giải có sẵn, không tốn thêm công gán nhãn. Trên 8 cặp này, 67/94 biên sự kiện lệch nhau không quá collar 0,2 s, độ lệch biên lớn nhất là 12,72 s, và 2/8 cặp bất đồng về lớp hoặc số sự kiện. Khi coi một lần chú giải là "dự đoán" của lần kia, event-F1 giữa người với người với collar 0,2 s là 0,5785. Hệ quả cho việc đọc kết quả là collar 0,2 s chặt hơn độ chính xác của chính nhãn. Một cải thiện nhỏ hơn mức bất đồng này không phân biệt được với nhiễu nhãn. Tuy vậy, cỡ mẫu chỉ 8 cặp, nên đây là tín hiệu cảnh báo chứ không phải một nghiên cứu về độ nhất quán chú giải.

## Rủi ro dữ liệu còn lại

Bốn rủi ro được ghi nhận và chưa thể loại bỏ hoàn toàn:

- **Nguồn âm thanh chung với AudioSet.** Một phần âm thanh gốc của hai bộ dữ liệu lấy từ AudioSet [@fredianelli2025environmental], trong khi các bộ mã hóa của đề tài được tiền huấn luyện trên AudioSet. Mức trùng không định lượng được.
- **Tập dev và test nhỏ.** Dev có 137 và test có 142 bản ghi, nên khoảng tin cậy rộng.
- **Bốn nút lớp con DataSEC có rất ít mẫu test.** Kết quả trên các nút này chỉ báo bằng số tuyệt đối.
- **Đồng xuất hiện không hoàn toàn tự nhiên.** Một số bản ghi DataSED có âm thanh được thêm bằng tay [@fredianelli2025environmental], nên quan hệ đồng xuất hiện giữa các lớp không hoàn toàn phản ánh môi trường thật.
