# CƠ SỞ LÝ THUYẾT VÀ NGHIÊN CỨU LIÊN QUAN

Chương này trình bày các khái niệm và kỹ thuật mà đề tài kế thừa. Văn liệu được trích chỉ gồm những nguồn mà đề tài đã đọc trực tiếp toàn văn và đối chiếu metadata xuất bản. Các chủ đề chưa có nguồn đạt mức này được nêu rõ là khoảng trống của phần tổng quan, không được viết như thể đã có căn cứ.

## Phát hiện sự kiện âm thanh đa âm

### Nhãn yếu, nhãn mạnh và tính đa âm

Phát hiện sự kiện âm thanh là bài toán nhận biết "cái gì xảy ra và khi nào" trong tín hiệu âm thanh [@mesaros2021tutorial]. Khác với phân loại, đầu ra của SED gồm lớp sự kiện cùng thời điểm onset và offset. Môi trường tự nhiên mang tính đa âm, tức nhiều nguồn có thể cùng hoạt động trong một khoảng thời gian, nên một khung thời gian có thể mang nhiều nhãn [@mesaros2021tutorial]. Về mặt học máy, SED đa âm vì vậy là bài toán phân loại đa nhãn theo từng khung thời gian, không phải phân loại đơn nhãn.

Hai kiểu nhãn quyết định cách học và cách đánh giá [@mesaros2021tutorial]. Nhãn mạnh chỉ rõ đoạn thời gian mà sự kiện hoạt động. Nhãn yếu chỉ cho biết sự kiện có mặt trong bản ghi, không cho biết ở đâu. Nhãn mạnh đắt hơn nhiều vì người gán nhãn phải nghe lại và đặt biên cho từng sự kiện; ranh giới của âm thanh môi trường lại thường không sắc nét. Hai bộ dữ liệu của đề tài phản ánh đúng sự phân chia này: DataSEC cung cấp các đoạn âm thanh rời với nhãn ở mức đoạn, còn DataSED cung cấp bản ghi dài có nhãn mạnh ở hai phiên bản, đa âm và đơn âm [@fredianelli2025environmental].

### Biểu diễn log-mel và kiến trúc CRNN

Đầu vào phổ biến của mô hình SED là phổ log-mel: tín hiệu được biến đổi Fourier thời gian ngắn, chiếu lên bộ lọc thang mel rồi lấy logarit, tạo thành ảnh thời gian–tần số. Một kiến trúc đa dụng cho SED là mạng nơ-ron tích chập hồi quy (Convolutional Recurrent Neural Network – CRNN) [@mesaros2021tutorial]. Trong CRNN, các lớp tích chập của mạng nơ-ron tích chập (Convolutional Neural Network – CNN) đóng vai trò trích đặc trưng từ biểu diễn thời gian–tần số, còn các lớp hồi quy học phụ thuộc theo thời gian giữa các khung. Trong đề tài, tầng hồi quy là mạng hồi quy có cổng hai chiều (Bidirectional Gated Recurrent Unit – BiGRU).

Đầu ra của mô hình là ma trận logit $z_{t,c}$ cho khung $t$ và lớp $c$. Với bài toán đa nhãn, mỗi ô được chuyển thành xác suất hậu nghiệm (posterior) độc lập bằng hàm sigmoid:

$$p_{t,c} = \sigma(z_{t,c}) = \frac{1}{1 + e^{-z_{t,c}}}$$

⟪eqno:sigmoid⟫

Chuỗi $p_{t,c}$ theo thời gian chưa phải là sự kiện. Nó phải qua bước hậu xử lý (Mục 2.3) để thành các đoạn $(c, t^{on}, t^{off})$. Vì vậy, chất lượng phát hiện phụ thuộc vào cả mô hình lẫn quy tắc hậu xử lý, và hai phần này phải được chọn trên dữ liệu phát triển, không phải trên dữ liệu kiểm tra.

## Đánh giá phát hiện sự kiện âm thanh

### Metric theo khung, theo đoạn và theo sự kiện

Mesaros và cộng sự phân biệt hai họ metric cho SED đa âm: metric theo đoạn (segment-based) và metric theo sự kiện (event-based) [@mesaros2016metrics]. Metric theo đoạn chia trục thời gian thành các đoạn cố định, ví dụ 1 s, rồi so sánh tập lớp hoạt động trong từng đoạn. Metric theo sự kiện so sánh từng sự kiện dự đoán với sự kiện tham chiếu cùng lớp. Một cặp được xem là khớp khi onset lệch không quá một ngưỡng dung sai gọi là collar; offset được so bằng collar hoặc bằng một tỷ lệ độ dài sự kiện tham chiếu [@mesaros2016metrics]. Đề tài dùng onset collar $\tau = 0{,}2$ s và dung sai offset

$$\Delta_{off} \le \max\left(\tau,\ \rho \cdot L_{ref}\right), \qquad \tau = 0{,}2\ \text{s},\ \rho = 0{,}2$$

⟪eqno:collar⟫

trong đó $L_{ref}$ là độ dài sự kiện tham chiếu. Gọi $TP$, $FP$, $FN$ là số sự kiện khớp, số sự kiện dự đoán không khớp và số sự kiện tham chiếu bị bỏ lỡ. Precision, recall và F1 theo sự kiện được tính theo công thức thông thường:

$$P = \frac{TP}{TP+FP}, \qquad R = \frac{TP}{TP+FN}, \qquad F_1 = \frac{2PR}{P+R}$$

⟪eqno:f1⟫

Trong báo cáo này, F1 theo khung (frame-F1) chỉ dùng để kiểm tra quá trình huấn luyện có chạy đúng. Nó **không** được đặt cạnh event-F1 như cùng một đại lượng, vì cùng một mô hình có thể cho event-F1 rất khác nhau tùy hậu xử lý.

### Trung bình micro và macro

Khi gộp kết quả của nhiều lớp, có hai cách lấy trung bình [@mesaros2016metrics]. Trung bình theo mẫu (instance-based), còn gọi là micro, cộng dồn $TP$, $FP$, $FN$ của mọi lớp rồi mới tính F1; mỗi quyết định có trọng số bằng nhau nên các lớp nhiều sự kiện lấn át. Trung bình theo lớp (class-based), còn gọi là macro, tính F1 cho từng lớp $c$ rồi lấy trung bình:

$$F_1^{micro} = F_1\Big(\sum_c TP_c,\ \sum_c FP_c,\ \sum_c FN_c\Big), \qquad F_1^{macro} = \frac{1}{|\mathcal{C}|}\sum_{c \in \mathcal{C}} F_{1,c}$$

⟪eqno:micromacro⟫

Hai con số này trả lời hai câu hỏi khác nhau, nên đề tài báo cả hai. Từ ngày 26/09/2026, macro được trình bày trước, micro đi kèm; còn các vòng chọn hệ thống vẫn dùng micro vì luật chọn đã được ghi trước bằng micro và micro ít nhiễu hơn trên tập dev nhỏ (ADR-0031). Lệch protocol trước ngày này, khi các con số chính đều là micro, được công khai ở Mục 6.7.

### Điểm PSDS

Metric dựa trên collar gắn với một điểm vận hành duy nhất (một ngưỡng). Bilen và cộng sự đề xuất điểm phát hiện âm thanh đa âm (Polyphonic Sound Detection Score – PSDS), đánh giá hệ thống trên **dải** điểm vận hành [@bilen2020psds]. PSDS định nghĩa dự đoán đúng và sai bằng tỷ lệ giao thời gian thay cho collar, thông qua ba tiêu chí: tiêu chí dung sai phát hiện (Detection Tolerance Criterion – DTC), tiêu chí giao với nhãn gốc (Ground Truth intersection Criterion – GTC) và tiêu chí kích hoạt chéo (Cross-Trigger Tolerance Criterion – CTTC). Đề tài dùng hai kịch bản được cố định trước khi chạy test (docs/evaluation_protocol.md §3.3). PSDS-1 với DTC = GTC = 0,7 nhấn mạnh định vị thời gian. PSDS-2 với DTC = GTC = 0,1, CTTC = 0,3 và trọng số phạt kích hoạt chéo 0,5 nhấn mạnh việc tránh nhầm lớp. Một hệ thống có thể tốt ở kịch bản này và kém ở kịch bản kia; chênh lệch đó là thông tin cần báo, không phải nhiễu cần bỏ qua.

### Mức tham chiếu từ ghi âm thực

Event-F1 trên bản ghi môi trường thực thường thấp. Ở nhiệm vụ 3 của chuỗi thử thách DCASE (Detection and Classification of Acoustic Scenes and Events) năm 2016 (phát hiện sự kiện trong âm thanh đời thực), metric chính là tỷ lệ lỗi theo đoạn 1 s; bảng kết quả event-based với collar 250 ms chỉ xét onset cho thấy baseline và các hệ thống dẫn đầu đạt event-F1 từ 4,7% đến 6,3% [@dcase2016task3]. Con số này dùng để **định cỡ** mức khó của bài toán. Nó không thể so trực tiếp với kết quả của đề tài, vì khác dữ liệu, khác số lớp và khác quy tắc collar.

## Hậu xử lý posterior thành sự kiện

### Ngưỡng và ưu tiên thời lượng

Cách hậu xử lý phổ biến là lọc trung vị (median filter) chuỗi posterior, so với ngưỡng $\theta_c$, gộp các khoảng trống ngắn hơn $g^{max}_c$ và bỏ sự kiện ngắn hơn $d^{min}_c$. Các tham số độ dài là ưu tiên thời lượng (duration prior) suy từ thống kê nhãn. Đề tài suy chúng từ tập huấn luyện, còn ngưỡng thì quét trên tập dev (ADR-0003). Nếu suy duration prior từ chính tập đang chấm, hậu xử lý đã "biết trước" phân bố cần đo; đây là một dạng rò rỉ khó nhận ra vì kết quả trông vẫn hợp lệ.

### Hộp bao sự kiện cSEBB

Ebbers và cộng sự chỉ ra rằng ngưỡng theo khung buộc chặt biên sự kiện với độ tin cậy: ngưỡng càng cao thì onset bị đẩy về nơi posterior *đạt* ngưỡng, chứ không phải nơi nó bắt đầu tăng [@ebbers2024sound]. Họ đề xuất hộp bao sự kiện (Sound Event Bounding Boxes – SEBB): mỗi sự kiện là một bộ (lớp, onset, offset, độ tin cậy), và ngưỡng chỉ quyết định giữ hay bỏ hộp, không dời biên. Biến thể cSEBB xác định biên bằng phát hiện điểm thay đổi: bộ lọc bậc độ dài $\tau$ tạo chuỗi chênh lệch giữa trung bình nửa sau và nửa trước, các cực trị của chuỗi này mở và đóng sự kiện, và khoảng trống được gộp theo một ngưỡng tuyệt đối hoặc tương đối. Trên 13 hệ thống của DCASE 2023, cSEBB cải thiện trung bình 4,1 điểm PSDS1 và 3,4 điểm F1 so với lọc trung vị [@ebbers2024sound]. Kết quả đó được đo trên dữ liệu và mô hình khác, nên đề tài coi cSEBB là một họ hậu xử lý cạnh tranh, phải được chọn bằng kiểm chứng chéo trên dev chứ không mặc định tốt hơn.

## Học chuyển giao cho âm thanh môi trường

### Tiền huấn luyện trên AudioSet

Kong và cộng sự công bố họ mạng PANNs (Pretrained Audio Neural Networks) huấn luyện trên AudioSet, một tập hơn 5.000 giờ với 527 lớp, rồi chuyển giao sang sáu tác vụ nhận dạng âm thanh khác [@kong2020panns]. Mạng CNN14 trong họ này gồm các khối tích chập, mỗi khối kết thúc bằng average pooling 2×2, và đạt mAP 0,431 trên tác vụ gán nhãn AudioSet [@kong2020panns]. Trọng số tiền huấn luyện của CNN14 là điểm xuất phát của nhánh B và C trong RQ1. Một chi tiết quan trọng cho SED là pooling theo trục thời gian làm giảm độ phân giải thời gian của đầu ra; Mục 4.3 cho thấy chi tiết này đặt ra một giới hạn trên đo được cho event-F1.

### Tiền huấn luyện theo khung và tự giám sát

Schmid và cộng sự xây dựng quy trình tiền huấn luyện cho transformer âm thanh trên nhãn **theo khung** của AudioSet Strong, sinh đầu ra ở bước 40 ms [@schmid2025effective]. Trên DESED, khi đóng băng bộ mã hóa và chỉ huấn luyện lớp tuyến tính, PSDS1 đạt 45,4–49,2 tùy kiến trúc, gần với chế độ tinh chỉnh toàn bộ (47,6–49,2) [@schmid2025effective]. Phát hiện "đóng băng gần bằng tinh chỉnh" là lý do đề tài thử bộ mã hóa đóng băng trước, vì cách này rẻ trên bộ xử lý đồ họa (Graphics Processing Unit – GPU) 8 GB. Một trong các bộ mã hóa đó là BEATs, mô hình tự giám sát (self-supervised learning – SSL) học bằng cách luân phiên tối ưu tokenizer âm học và mô hình dự đoán nhãn rời rạc [@chen2022beats]. Tuy vậy, các con số trên được đo trên DESED, không phải trên DataSED, nên chúng chỉ là động cơ để thử chứ không phải dự báo kết quả.

### Tăng cường dữ liệu

Hai kỹ thuật tăng cường được dùng trong công thức huấn luyện SED v2. Mixup huấn luyện mạng trên tổ hợp lồi của cặp mẫu và nhãn tương ứng [@zhang2018mixup]. FilterAugment nhân trọng số ngẫu nhiên lên các dải tần của phổ log-mel để mô phỏng ảnh hưởng của môi trường âm học. Trên SED, kỹ thuật này tăng PSDS 6,50% so với 2,13% của frequency masking [@nam2022filteraugment].

### Rò rỉ dữ liệu giữa các bộ dữ liệu

Học chuyển giao giữa hai bộ dữ liệu chỉ có nghĩa khi tập kiểm tra của bộ đích không xuất hiện trong dữ liệu tiền huấn luyện. Bài mô tả DataSEC và DataSED cho biết một phần âm thanh được lấy từ Freesound và AudioSet, rồi được cắt, ghép, trộn hoặc sửa tay; với DataSED, một số bản ghi còn được thêm âm thanh bằng tay [@fredianelli2025environmental]. Điều này gây hai rủi ro. Thứ nhất, hai bộ dữ liệu của cùng nhóm tác giả có thể chứa chung bản ghi gốc; đề tài kiểm tra trực tiếp rủi ro này ở Chương 3. Thứ hai, bộ mã hóa tiền huấn luyện trên AudioSet có thể đã thấy một phần âm thanh gốc; rủi ro này **không định lượng được** vì bài báo không công bố danh sách nguồn, nên chỉ được ghi nhận như một giới hạn.

## Sinh mô tả có căn cứ và hiện tượng ảo giác

Ji và cộng sự định nghĩa ảo giác trong sinh ngôn ngữ tự nhiên là nội dung "vô nghĩa hoặc không trung thành với nội dung nguồn được cung cấp" [@ji2023hallucination]. Họ phân biệt ảo giác nội tại (intrinsic), tức đầu ra mâu thuẫn với nguồn, và ảo giác ngoại tại (extrinsic), tức đầu ra không kiểm chứng được từ nguồn [@ji2023hallucination]. Trong đề tài, "nguồn" của bộ sinh mô tả được định nghĩa hẹp và kiểm tra được: đó là dòng thời gian sự kiện. Một mô tả nhắc đến nguồn âm không có trong dòng thời gian là ảo giác ngoại tại; một mô tả đặt sai thứ tự hai sự kiện là ảo giác nội tại.

Cách định nghĩa này cho phép đo ảo giác **không cần câu mô tả tham chiếu do người viết**. Các metric so khớp n-gram truyền thống so mô tả với câu tham chiếu; một mô tả bịa vẫn có thể trùng nhiều n-gram nên các metric đó không phát hiện được ảo giác. Đề tài chưa đọc trực tiếp văn liệu về mô tả âm thanh tự động (Automated Audio Captioning – AAC) và các metric chuyên biệt của lĩnh vực này. Vì vậy, báo cáo **không** khẳng định rằng bộ metric của đề tài là mới so với văn liệu AAC; việc tổng quan phần này thuộc kế hoạch giai đoạn sau (Mục 7.4).

## Sinh tăng cường truy hồi và truy hồi lai

### Kiến trúc RAG

Lewis và cộng sự đề xuất RAG, kết hợp bộ nhớ tham số (một mô hình chuỗi sang chuỗi tiền huấn luyện) với bộ nhớ phi tham số (một chỉ mục vector dày) được truy cập qua bộ truy hồi nơ-ron [@lewis2020rag]. Bài báo cũng nêu việc cung cấp nguồn gốc (provenance) cho câu trả lời là một vấn đề mở [@lewis2020rag]. Đề tài áp dụng tinh thần này cho dữ liệu sự kiện âm thanh nhưng thay đổi hai điểm. Thứ nhất, bộ nhớ ngoài không phải văn bản tự do mà là các sự kiện có cấu trúc, gồm lớp, onset, offset và độ tin cậy. Thứ hai, câu trả lời bắt buộc trích dẫn bằng chứng là (mã bản ghi, khoảng thời gian), và một câu trả lời thiếu bằng chứng bị coi là không hợp lệ.

### Embedding đa ngữ và bộ lọc có cấu trúc

Để câu hỏi tiếng Việt và tiếng Anh cùng truy hồi trên một kho, đề tài dùng mô hình embedding đa ngữ BGE-M3 (M3-Embedding). Mô hình này hỗ trợ hơn 100 ngôn ngữ, ba kiểu truy hồi dày, thưa và đa vector, và đầu vào dài tới 8192 token [@chen2024m3]. Độ tương đồng vector phù hợp với câu hỏi mang tính ngữ nghĩa, nhưng không bảo đảm các ràng buộc cứng như "sự kiện dài hơn 30 giây" hay "tiếng kính vỡ xảy ra trước tiếng còi". Các ràng buộc này là phép so sánh trên thuộc tính số và phép nối theo thời gian, nên được thực hiện bằng bộ lọc có cấu trúc trong cơ sở dữ liệu. Truy hồi lai đặt bộ lọc cứng trước, rồi mới xếp hạng vector *trong* tập đã lọc. Như vậy, độ tương đồng ngữ nghĩa không bao giờ ghi đè được bộ lọc.

Hiệu năng truy hồi được đo bằng các metric xếp hạng chuẩn: Recall@k (tỷ lệ bản ghi liên quan nằm trong $k$ kết quả đầu), hạng nghịch đảo trung bình (Mean Reciprocal Rank – MRR) và lợi ích tích lũy chiết khấu chuẩn hóa tại 10 (normalized Discounted Cumulative Gain – nDCG@10). Công thức cụ thể như đề tài cài đặt được trình bày ở Mục 4.7.

## Tổng hợp và định vị đề tài

Các nguồn đã đọc cung cấp nền tảng cho từng mắt xích: dữ liệu môi trường có nhãn mạnh [@fredianelli2025environmental], metric SED theo sự kiện và PSDS [@mesaros2016metrics; @bilen2020psds], hậu xử lý biên sự kiện [@ebbers2024sound], tiền huấn luyện theo clip và theo khung [@kong2020panns; @schmid2025effective], khái niệm ảo giác [@ji2023hallucination] và RAG [@lewis2020rag]. Bài mô tả DataSED không báo cáo mô hình hay metric baseline nào [@fredianelli2025environmental]. Đề tài chưa thực hiện tìm kiếm có hệ thống các công trình trích dẫn bộ dữ liệu này, nên không khẳng định kết quả của mình là baseline đầu tiên trên DataSED.

Trên nền đó, đề tài tập trung vào phần nối giữa các mắt xích: chuyển giao có kiểm soát rò rỉ xuyên dataset, SED đa âm trên bản ghi môi trường, mô tả có hợp đồng căn cứ kiểm được bằng máy, và truy hồi trên dòng thời gian với vị từ thời gian. Mọi đầu ra cuối cùng truy được về mã bản ghi, khoảng thời gian, phiên bản mô hình, hash của tập chia và hash của hệ lớp.
