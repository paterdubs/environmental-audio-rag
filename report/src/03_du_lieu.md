# DỮ LIỆU

Chương này mô tả hai bộ dữ liệu, các lớp âm thanh và quy trình chuẩn bị dữ liệu (D0–D4). Quy trình bảo đảm mọi tệp đều có nguồn gốc, mọi tệp bị loại đều có lý do, và các tập chia được khóa bằng mã băm (hash) trước khi huấn luyện. Mọi con số trong chương do script tính từ tệp kiểm kê và báo cáo đo; nguồn ghi dưới mỗi bảng.

## Hai bộ dữ liệu

DataSEC và DataSED được công bố trên Zenodo theo giấy phép CC-BY-NC-SA-4.0 và mô tả trong một bài báo trên *Scientific Data* [@fredianelli2025environmental]. Giấy phép lấy từ bản ghi Zenodo vì hai tệp nén không có tệp LICENSE. Điều khoản "chia sẻ tương tự" nghĩa là nếu công bố mô hình huấn luyện từ dữ liệu này thì mô hình cũng phải theo cùng giấy phép.

Nhóm không dùng các số thống kê trong bài báo, vì phiên bản DataSEC trong bài (4.292 tệp) cũ hơn bản đã tải, và số tệp, tổng thời lượng của DataSED trong bài khác với tệp nén thực tế. Mọi thống kê dưới đây đo trực tiếp từ tệp nén, đã kiểm kích thước và MD5 trước khi giải nén (DataSEC 6.414.663.316 byte, DataSED 4.510.378.259 byte, cả hai khớp giá trị công bố).

**DataSEC** (Zenodo 17033970, bản 3) gồm 5.048 tệp WAV đơn kênh 44,1 kHz, tổng 23,71 giờ. Nhãn lấy từ cây thư mục, có hai cấp: 22 lớp gộp và 28 lớp con thuộc 10 lớp gộp. Phân bố lớp rất lệch: `voices` (1.900 tệp, 37,6%) và `music` (1.001 tệp, 19,8%) chiếm 57,5%, trong khi lớp nhỏ nhất chỉ có 50 tệp (chênh khoảng 38 lần). Ở cấp lớp con, bốn nút có dưới 25 tệp (`crickets`, `olive_shaker`, `magpies`, `lawn_mower`) nên mỗi nút chỉ có 3–4 mẫu test. Vì vậy nhóm lấy mẫu cân bằng lớp khi huấn luyện và chỉ báo số tuyệt đối cho các nút có dưới 10 mẫu test.

**DataSED** (Zenodo 15346092) gồm 717 bản ghi WAV 44,1 kHz, tổng 18,68 giờ, dài trung bình khoảng 94 s. Bộ này có hai bản nhãn mạnh trên cùng âm thanh: bản đa âm (polyphonic) có 4.034 sự kiện thuộc 21 lớp, phủ 703 bản ghi; bản đơn âm có 4.309 sự kiện thuộc 22 lớp, phủ đủ 717 bản ghi. Sự kiện dài từ 0,41 s đến 296,5 s, trung vị 5,8 s. Nhóm chọn bản đa âm làm benchmark chính vì môi trường thật thường có nhiều nguồn cùng lúc.

## Các lớp âm thanh

Hệ lớp (phiên bản 0.1, SHA-256 `67ca8a8c…`) có 22 lớp với tên tiếng Anh dạng snake_case, ánh xạ một–một từ nhãn gốc; bảng đầy đủ ở Phụ lục A. Ánh xạ đã được kiểm trực tiếp trên tệp nén: 22/22 lớp gộp và 10/10 nhóm lớp con khớp, không có nhãn lạ. Nhãn gốc được giữ nguyên để truy nguồn; gặp nhãn lạ thì quy trình dừng chứ không tự đoán.

Đề tài dùng hai tập lớp khác nhau:

- **22 lớp** cho phân loại DataSEC và cho bản nhãn đơn âm của DataSED.
- **21 lớp đa âm** cho đầu ra SED. Lớp `wind_turbine` không có trong bản nhãn đa âm.

Kết quả trên 21 lớp đa âm và trên 22 lớp đơn âm **không so sánh trực tiếp được**, vì khác tập lớp, khác định nghĩa nhãn và khác mẫu số khi tính macro.

Hai lớp gộp `sirens_and_alarms` và `thunder_fireworks_gunshot` chứa các nguồn âm khác bản chất (còi báo động khác chuông báo; sấm khác pháo hoa và tiếng súng). DataSED chỉ có nhãn ở cấp gộp, nên mô tả về hai lớp này phải giữ đúng mức mơ hồ: viết "một âm thanh xung giống sấm, pháo hoa hoặc tiếng súng", không viết "một tiếng súng". Điều này được kiểm thử trong phần sinh mô tả (Chương 4).

## Quy trình chuẩn bị dữ liệu

Quy trình gồm các cổng kiểm tra nối tiếp; cổng sau chỉ chạy khi cổng trước đạt (⟪fig:pipeline⟫).

![](report/figures/m04_data_pipeline.png){width=13cm}

@@CAP:fig:pipeline|Quy trình chuẩn bị dữ liệu D0–D4 và các tệp đã khóa@@

@@NOTE:Nguồn: scripts/build_midterm_figures.py, đọc data/manifests/{datasec,datased}_inventory_summary.json, datased_preparation_audit.json, duplicate_audit.json và hai tệp split đóng băng.@@

**D0–D2: kiểm tệp nén, kiểm kê, chuẩn hóa nhãn.** Cổng D0 kiểm kích thước và MD5 **trước** khi giải nén và đối chiếu cây nhãn với hệ lớp; việc bỏ qua kiểm tra được ghi thành kết luận riêng để không bao giờ bị đọc nhầm là "đạt". Cổng D1 ghi tần số lấy mẫu, số kênh, thời lượng, SHA-256 của từng tệp và trích sẵn đặc trưng log-mel (`logmel_v1`: 16 kHz, 64 mel, 50 khung/s, cho mô hình học từ đầu; `logmel_panns_v1`: 32 kHz, 64 mel, 100 khung/s, cho mô hình họ PANNs). Cổng D2 chuyển nhãn DataSED thành bảng sự kiện; nhãn gốc không bao giờ bị sửa, nghi ngờ nhãn nào thì ghi phân tích lỗi thay vì chỉnh dữ liệu.

**D3: tìm bản trùng.** D3 là cổng quan trọng nhất cho RQ1. Hai bộ dữ liệu có cùng sáu tác giả, cùng miền và công bố cách nhau bốn tháng, nên nhóm giả định hai bộ *có thể* chung bản ghi gốc cho tới khi đo được điều ngược lại. Bản trùng được tìm ở ba tầng, cả trong từng bộ lẫn giữa hai bộ: **T1** so mã băm byte của tệp; **T2** so mã băm tín hiệu sau khi giải mã và lấy mẫu lại về 16 kHz đơn kênh; **T3** so dấu vân tay âm học (20 hệ số MFCC mỗi khung 1 s, chuẩn hóa theo toàn kho, so bằng độ tương đồng cosine trên đoạn chồng lấp dài nhất, ADR-0007).

Ngưỡng của T3 được hiệu chuẩn bằng dữ liệu, gồm 24 cặp giống hệt byte (dương) và 5.000 cặp ngẫu nhiên khác nhãn (âm). Dấu vân tay theo đặc tả ban đầu cho 52,6% cặp âm vượt ngưỡng xem xét, tức không dùng được. Sau khi bỏ hệ số $C_0$ và chuẩn hóa theo kho, cặp dương thấp nhất đạt 1,0000, cặp âm cao nhất đạt 0,9205 và không cặp âm nào đạt 0,95. Từ đó nhóm đặt: cặp chồng lấp từ 3 s trở lên là `duplicate` khi độ tương đồng ≥ 0,95, và vào hàng đợi xem xét khi nằm trong [0,85; 0,95). Cặp chồng lấp dưới 3 s không bao giờ được tự động coi là trùng, vì các cặp "xem xét" giả có đoạn chồng lấp trung vị đúng 1 s — hệ quả của việc so sánh khoảng 16,6 triệu cặp (ADR-0009).

@@CAP:tbl:leakage|Kết quả khử trùng lặp D3 và kiểm tra trùng giữa các tập D4@@

@@INCLUDE:docs/thesis/tables/02_leakage_d3_d4.md@@

⟪tbl:leakage⟫ xác nhận rủi ro là có thật. Có ba nhóm trùng giữa hai bộ dữ liệu, trong đó hai cặp có độ tương đồng 1,000000 trên đoạn chồng lấp 35 s và 13 s: `Sirens-0046` (DataSEC) với `S-0233` (DataSED), và `Sirens-0067` với `S-0211`. Cặp thứ ba là `Train-0012` với `S-0213` (0,9548 trên 31 s). Thêm 35 cặp giữa hai bộ nằm ở vùng xem xét được duyệt tay bằng cách nghe: 10 cặp trùng, 1 cặp không chắc (xử lý thận trọng như trùng) và 24 cặp khác nhau. Sau D3, 11 đoạn DataSEC trùng với bản ghi DataSED thuộc dev hoặc test bị loại khỏi dữ liệu tiền huấn luyện. Con số này là 0,2179% DataSEC, nằm trong dải "nhỏ" (dưới 1%) mà kế hoạch dữ liệu quy định là loại bỏ, ghi nhận và vẫn giữ hiệu lực của RQ1. Trong nội bộ DataSEC còn 119 đoạn bị loại vì là bản sao, nên tổng số đoạn không vào tập chia là 130.

**D4: chia tập.** Đơn vị chia là **nhóm trùng** (`leakage_group`), không phải từng tệp: các tệp giống nhau hoặc rất giống nhau luôn nằm cùng một tập. DataSED chia 60/20/20 theo bản ghi, phân tầng theo nhãn, seed 20260922 (ADR-0008); DataSEC chia 70/15/15 theo lớp gộp. Ngưỡng gom cặp tương tự được đặt 0,93, trên mức nhiễu đã đo (0,9205); với 0,85, hiện tượng nối chuỗi tạo một khối 315 tệp trộn tiếng nói với tiếng nổ và làm tỷ lệ chia lệch 5 điểm phần trăm (ADR-0012).

@@CAP:tbl:split|Hai bộ dữ liệu và tập chia đã khóa@@

@@INCLUDE:docs/thesis/tables/01_data_split.md@@

Cổng D4 kiểm năm điều kiện trước khi khóa: không nhóm nào nằm ở hai tập, không mã băm nào nằm ở hai tập, không cặp trùng nào xuyên tập, mọi lớp có mẫu ở mỗi tập, và các đoạn đã loại thật sự vắng mặt (⟪tbl:split⟫). Cả hai bộ dữ liệu đạt 5/5. Cổng này được chứng minh **không đạt rỗng**: khi gỡ danh sách loại trừ, kiểm tra thứ năm thất bại và chỉ đúng tệp `Sirens-0046.wav`. Phép thử ngược này cần thiết vì từng có hai lỗi lệch cách đặt tên định danh (`recording_id` và `file_id`) khiến mọi phép giao thành rỗng, mà phép giao rỗng thì luôn báo "sạch". Hai tập chia được khóa bằng SHA-256; nếu sửa tệp chia sau khi khóa, cổng D4 từ chối chạy.

## Nhãn thiếu và độ nhất quán của nhãn

**Bản ghi thiếu nhãn đa âm.** Nhóm phát hiện bản nhãn đa âm chỉ phủ 703/717 bản ghi. Mười bốn bản ghi `S-0704` đến `S-0717` (đều mang nhãn `wind_turbine`) không có dòng nhãn đa âm nhưng vẫn nằm trong tập chia: 8 ở train, 3 ở dev, 3 ở test. Nếu chấm điểm trên chúng, mọi dự đoán bị tính là báo động nhầm dù thực chất chỉ là thiếu nhãn. Nhóm không chia lại tập (đã khóa) mà thêm một tập đánh giá `annotated` chỉ gồm bản ghi có nhãn đa âm: dev còn 134, test còn 139 bản ghi (ADR-0034). Từ vòng chọn hệ thống cuối, mọi kiểm chứng chéo và đánh giá test dùng tập này. Các kết quả cũ trên tập `all` (142 bản ghi test) được giữ và ghi rõ tập đánh giá khi trích.

**Hai lần gán nhãn cho cùng một bản ghi.** DataSED có 8 cặp bản ghi giống hệt byte nhưng được gán nhãn độc lập hai lần, cho một phép đo độ nhất quán có sẵn. Trên 8 cặp này, 67/94 biên sự kiện lệch không quá 0,2 s, độ lệch biên lớn nhất là 12,72 s, và 2/8 cặp bất đồng về lớp hoặc số sự kiện. Coi một lần gán là "dự đoán" của lần kia, event-F1 giữa người với người ở collar 0,2 s là 0,5785. Nghĩa là collar 0,2 s chặt hơn độ chính xác của chính nhãn, và một cải thiện nhỏ hơn mức bất đồng này không phân biệt được với nhiễu nhãn. Do chỉ có 8 cặp, đây là tín hiệu cảnh báo chứ không phải một nghiên cứu về độ nhất quán.

Các rủi ro dữ liệu còn lại — trùng nguồn với AudioSet (không định lượng được), tập dev và test nhỏ, bốn nút lớp con ít mẫu và âm thanh thêm bằng tay [@fredianelli2025environmental] — được nêu ở phần hạn chế của Chương 6.
