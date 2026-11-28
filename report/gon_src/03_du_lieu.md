# DỮ LIỆU

Chương này mô tả hai bộ dữ liệu, các lớp âm thanh và quy trình chuẩn bị dữ liệu. Quy trình bảo đảm ba điều: mọi tệp có nguồn gốc, mọi tệp bị loại có lý do, và các tập dữ liệu được khóa bằng mã băm trước khi huấn luyện.

## Hai bộ dữ liệu

DataSEC và DataSED được công bố trên Zenodo theo giấy phép Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0) và được mô tả trong một bài báo trên *Scientific Data* [@fredianelli2025environmental]. Giấy phép này cấm dùng vào mục đích thương mại, nên dự án không phát hành trọng số mô hình.

Nhóm đo mọi thống kê trực tiếp từ tệp tải về, không lấy từ bài báo. Lý do là bản DataSEC nhóm dùng (bản 3) có 5.048 tệp, trong khi bài báo mô tả 4.292 tệp; chênh lệch do lỗi thừa tệp ở lớp Music, được sửa ở bản 4 công bố sau khi dữ liệu của đề tài đã khóa. Trước khi giải nén, nhóm kiểm kích thước và mã băm MD5 (MD5 Message-Digest Algorithm) của hai tệp nén; cả hai khớp giá trị công bố.

**DataSEC** gồm 5.048 tệp WAV đơn kênh 44,1 kHz, tổng 23,71 giờ. Nhãn lấy từ cây thư mục, có hai cấp: 22 lớp cấp trên và 28 lớp con thuộc 10 lớp cấp trên. Phân bố lớp rất lệch: `voices` (1.900 tệp, 37,6%) và `music` (1.001 tệp, 19,8%) chiếm 57,5%, trong khi lớp nhỏ nhất chỉ có 50 tệp. Vì vậy khi huấn luyện, nhóm lấy mẫu cân bằng giữa các lớp.

**DataSED** gồm 717 bản ghi WAV 44,1 kHz, tổng 18,68 giờ, dài trung bình khoảng 94 s. Bản nhãn đa âm có 4.034 sự kiện thuộc 21 lớp; sự kiện dài từ 0,41 s đến 296,5 s, trung vị 5,8 s. Nhóm dùng bản nhãn đa âm làm chuẩn đánh giá chính vì môi trường thật thường có nhiều nguồn cùng lúc.

## Các lớp âm thanh

Hệ lớp có 22 lớp, đặt tên tiếng Anh dạng `snake_case` và ánh xạ một–một từ nhãn gốc; bảng đầy đủ ở Phụ lục A (⟪tbl:taxonomy⟫). Đề tài dùng hai tập lớp:

- **22 lớp** cho phân loại trên DataSEC.
- **21 lớp** cho SED trên DataSED. Lớp `wind_turbine` không có trong bản nhãn đa âm.

Hai lớp gộp `sirens_and_alarms` và `thunder_fireworks_gunshot` chứa các nguồn âm khác nhau (còi báo động khác chuông báo; sấm khác pháo hoa và tiếng súng). DataSED chỉ có nhãn ở cấp gộp, nên mô tả về hai lớp này phải giữ đúng mức mơ hồ: viết "âm thanh giống sấm, pháo hoa hoặc tiếng súng", không viết "một tiếng súng".

⟪fig:dataprofile⟫ cho thấy hai kiểu mất cân bằng. Ở DataSEC, số tệp theo lớp trải từ 50 (`cat_fights_and_moans`) đến 1.900 (`voices`). Ở DataSED, 4.034 sự kiện chia thành 2.408 ở tập huấn luyện, 886 ở tập phát triển và 740 ở tập kiểm tra; lớp nào cũng có mặt ở cả ba tập.

![](report/gon_figures/r01_data_profile.png){width=15cm}

@@CAP:fig:dataprofile|Phân bố lớp: số tệp DataSEC và số sự kiện DataSED theo tập@@

@@NOTE:Nguồn: data_profile_20261008_lf.json.@@

Độ dài sự kiện cũng chênh lệch mạnh giữa các lớp (⟪fig:duration⟫): 90% số sự kiện dài từ 1,0 đến 43,5 s, và trung vị theo lớp đi từ 1,5 s (`horn`) đến 38,0 s (`propeller_aircrafts`). Điều này ảnh hưởng tới việc đánh giá. Với lớp kéo dài hàng chục giây, sai 0,2 s ở biên chỉ là phần rất nhỏ của sự kiện nhưng vẫn bị F1 theo sự kiện tính là sai hoàn toàn.

![](report/gon_figures/r02_event_duration.png){width=14cm}

@@CAP:fig:duration|Độ dài sự kiện đa âm theo lớp trên tập huấn luyện (thang log)@@

@@NOTE:Nguồn: data_profile_20261008_lf.json; đường đứt nét là dung sai 0,2 s của F1 theo sự kiện.@@

## Quy trình chuẩn bị dữ liệu

Quy trình gồm năm cổng kiểm tra nối tiếp, ký hiệu D0 đến D4; cổng sau chỉ chạy khi cổng trước đạt (⟪fig:pipeline⟫).

@@DIAGRAM:pipeline@@

@@CAP:fig:pipeline|Quy trình chuẩn bị dữ liệu D0–D4@@

@@NOTE:Nguồn: tệp kiểm kê, báo cáo kiểm trùng và hai tập chia đã khóa (đọc khi dựng báo cáo).@@

**D0–D2: kiểm tệp nén, kiểm kê, chuẩn hóa nhãn.** D0 kiểm kích thước và MD5 **trước** khi giải nén, và đối chiếu cây nhãn với hệ lớp. D1 ghi tần số lấy mẫu, số kênh, thời lượng và mã băm SHA-256 (Secure Hash Algorithm, 256 bit) của từng tệp, rồi trích sẵn phổ log-mel cho các mô hình cần đặc trưng tính trước (64 dải mel). D2 chuyển nhãn DataSED thành bảng sự kiện. Nhãn gốc không bao giờ bị sửa; nếu nghi ngờ nhãn, nhóm ghi lại để phân tích thay vì chỉnh dữ liệu.

**D3: tìm bản trùng.** Đây là cổng quan trọng nhất cho Câu hỏi nghiên cứu 1. Hai bộ dữ liệu có cùng tác giả và cùng lĩnh vực, nên nhóm giả định chúng *có thể* chung bản ghi gốc cho tới khi đo được điều ngược lại. Bản trùng được tìm ở ba tầng, cả trong từng bộ lẫn giữa hai bộ:

- **Tầng 1** so mã băm của tệp.
- **Tầng 2** so mã băm của tín hiệu sau khi đưa về cùng định dạng (16 kHz, đơn kênh).
- **Tầng 3** so "dấu vân tay" âm học: chuỗi hệ số cepstral thang mel (Mel-Frequency Cepstral Coefficients – MFCC) theo từng giây, so bằng độ tương đồng cosine trên đoạn chồng nhau dài nhất.

Ngưỡng của tầng 3 được chọn bằng dữ liệu: 24 cặp giống hệt nhau (cặp dương) và 5.000 cặp ngẫu nhiên khác lớp (cặp âm). Cặp dương thấp nhất đạt 1,0000, cặp âm cao nhất đạt 0,9205, và không cặp âm nào đạt 0,95. Từ đó, một cặp chồng nhau từ 3 s trở lên được coi là trùng khi độ tương đồng ≥ 0,95, và được đưa vào danh sách nghe lại khi nằm trong khoảng 0,85 đến 0,95. Kết quả của D3 và D4 tóm tắt ở ⟪tbl:leakage⟫.

@@CAP:tbl:leakage|Kết quả tìm bản trùng (D3) và kiểm tra tập chia (D4)@@

@@INCLUDE:docs/thesis/tables/02_leakage_d3_d4.md@@

Kết quả xác nhận rủi ro là có thật. Có ba nhóm trùng giữa hai bộ dữ liệu; hai cặp có độ tương đồng 1,000000 trên đoạn chồng nhau dài 35 s và 13 s (`Sirens-0046` của DataSEC với `S-0233` của DataSED, và `Sirens-0067` với `S-0211`). Thêm 35 cặp giữa hai bộ được nhóm nghe và duyệt tay: 10 cặp trùng, 1 cặp không chắc (xử lý thận trọng như trùng) và 24 cặp khác nhau. Kết quả là 11 đoạn DataSEC trùng với bản ghi DataSED ở tập phát triển hoặc kiểm tra bị loại khỏi dữ liệu tiền huấn luyện, tức 0,2179% DataSEC. Cộng với 119 đoạn trùng ngay trong DataSEC, tổng số đoạn bị loại là 130.

**D4: chia tập.** Đơn vị chia là **nhóm trùng**, không phải từng tệp: các tệp giống nhau luôn nằm cùng một tập. DataSED chia 60/20/20 theo bản ghi, DataSEC chia 70/15/15 theo lớp, với hạt giống ngẫu nhiên cố định (⟪tbl:split⟫).

@@CAP:tbl:split|Hai bộ dữ liệu và tập chia đã khóa@@

@@INCLUDE:docs/thesis/tables/01_data_split.md@@

Cổng D4 kiểm năm điều kiện trước khi khóa: không nhóm trùng nào nằm ở hai tập, không mã băm nào nằm ở hai tập, không cặp trùng nào nằm ở hai tập, lớp nào cũng có mẫu ở mỗi tập, và các đoạn đã loại thật sự vắng mặt. Cả hai bộ dữ liệu đạt 5/5. Nhóm cũng thử ngược để chắc cổng không "đạt" một cách rỗng: khi bỏ danh sách loại trừ, điều kiện thứ năm thất bại và chỉ đúng tệp `Sirens-0046.wav`. Sau đó hai tập chia được khóa bằng SHA-256; nếu tệp chia bị sửa, cổng từ chối chạy.

## Nhãn thiếu và độ nhất quán của nhãn

**Bản ghi thiếu nhãn.** Bản nhãn đa âm chỉ phủ 703/717 bản ghi. Mười bốn bản ghi `S-0704` đến `S-0717` (đều thuộc lớp `wind_turbine`) không có nhãn đa âm nhưng vẫn nằm trong tập chia: 8 ở tập huấn luyện, 3 ở tập phát triển, 3 ở tập kiểm tra. Nếu chấm trên các bản ghi này, mọi dự đoán sẽ bị tính là báo nhầm. Vì tập chia đã khóa, nhóm không chia lại mà chỉ chấm trên các bản ghi có nhãn: tập phát triển còn 134 và tập kiểm tra còn 139 bản ghi. Một số kết quả cũ của thế hệ SED đầu tiên chấm trên cả 142 bản ghi kiểm tra; báo cáo ghi rõ khi trích.

**Hai lần gán nhãn cho cùng một bản ghi.** DataSED có 8 cặp bản ghi giống hệt nhau nhưng được gán nhãn hai lần, nên đo được độ nhất quán của chính nhãn. Trên 8 cặp này, 67/94 biên sự kiện lệch không quá 0,2 s, và 2/8 cặp bất đồng về lớp hoặc số sự kiện. Coi một lần gán là "dự đoán" của lần kia, F1 theo sự kiện giữa hai lần gán là 0,5785. Gần một phần ba số biên (27/94) lệch quá dung sai 0,2 s, tức dung sai này chặt hơn độ nhất quán của nhãn. Báo cáo gọi 0,5785 là **mức đồng thuận quan sát trên 8 cặp**, không coi đó là trần tuyệt đối của mô hình.
