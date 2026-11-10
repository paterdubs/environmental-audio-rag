# CƠ SỞ LÝ THUYẾT

Chương này tóm tắt những kiến thức nền mà đề tài dùng. Nhóm chỉ trích các nguồn đã đọc trực tiếp toàn văn. Những chủ đề chưa có nguồn như vậy được ghi rõ là chưa tổng quan, không viết như thể đã có căn cứ.

## Phát hiện sự kiện âm thanh

Phát hiện sự kiện âm thanh (SED) trả lời câu hỏi "cái gì xảy ra và khi nào" trong tín hiệu âm thanh. Đầu ra gồm lớp sự kiện cùng thời điểm bắt đầu và kết thúc [@mesaros2021tutorial]. Vì nhiều nguồn có thể vang cùng lúc, SED đa âm là bài toán phân loại **đa nhãn theo từng khung thời gian**, không phải phân loại một nhãn cho cả đoạn.

Có hai kiểu nhãn [@mesaros2021tutorial]. Nhãn mạnh ghi rõ đoạn thời gian của từng sự kiện. Nhãn yếu chỉ cho biết lớp nào có mặt trong bản ghi. Nhãn mạnh tốn công hơn vì người gán nhãn phải nghe lại và đặt biên cho từng sự kiện, mà biên của âm thanh môi trường vốn không rõ nét. Hai bộ dữ liệu của đề tài phản ánh sự khác biệt này: DataSEC có các đoạn rời với nhãn mức đoạn, còn DataSED có bản ghi dài với nhãn mạnh [@fredianelli2025environmental].

Đầu vào thường dùng là phổ log-mel, một "ảnh" thời gian–tần số của tín hiệu. Kiến trúc phổ biến là mạng tích chập hồi quy (CRNN) [@mesaros2021tutorial]: phần tích chập (CNN) trích đặc trưng từ ảnh phổ, phần hồi quy (ở đây là BiGRU, mạng hồi quy hai chiều) học quan hệ theo thời gian. Mô hình cho ra xác suất của từng lớp tại từng khung. Chuỗi xác suất này chưa phải là sự kiện: nó phải qua bước ghép thành các đoạn (mục "Từ xác suất thành sự kiện" bên dưới). Vì thế chất lượng phát hiện phụ thuộc cả mô hình lẫn bước ghép, và hai phần này đều phải được chọn trên tập dev, không phải trên tập test.

## Cách đánh giá

**Metric theo sự kiện.** Mesaros và cộng sự phân biệt metric theo đoạn (chia trục thời gian thành các đoạn cố định như 1 s rồi so từng đoạn) với metric theo sự kiện (so từng sự kiện dự đoán với sự kiện tham chiếu cùng lớp) [@mesaros2016metrics]. Một cặp được coi là khớp khi thời điểm bắt đầu lệch không quá một dung sai (collar). Đề tài dùng collar $\tau = 0{,}2$ s cho thời điểm bắt đầu và, cho thời điểm kết thúc, dung sai

$$\Delta_{off} \le \max\left(\tau,\ \rho \cdot L_{ref}\right), \qquad \tau = 0{,}2\ \text{s},\ \rho = 0{,}2$$

⟪eqno:collar⟫

với $L_{ref}$ là độ dài sự kiện tham chiếu. Gọi $TP$, $FP$, $FN$ là số sự kiện đoán đúng, đoán sai và bị bỏ lỡ. Precision, recall và F1 (gọi tắt là event-F1) được tính như sau:

$$P = \frac{TP}{TP+FP}, \qquad R = \frac{TP}{TP+FN}, \qquad F_1 = \frac{2PR}{P+R}$$

⟪eqno:f1⟫

F1 theo khung chỉ dùng để kiểm tra huấn luyện chạy đúng. Nhóm không đặt nó cạnh event-F1 như cùng một đại lượng.

**Micro và macro.** Khi gộp nhiều lớp có hai cách [@mesaros2016metrics]. *Micro* cộng dồn $TP$, $FP$, $FN$ của mọi lớp rồi mới tính F1, nên các lớp có nhiều sự kiện chi phối kết quả. *Macro* tính F1 riêng từng lớp rồi lấy trung bình, nên mỗi lớp có trọng số như nhau:

$$F_1^{micro} = F_1\Big(\sum_c TP_c,\ \sum_c FP_c,\ \sum_c FN_c\Big), \qquad F_1^{macro} = \frac{1}{|\mathcal{C}|}\sum_{c \in \mathcal{C}} F_{1,c}$$

⟪eqno:micromacro⟫

Hai con số trả lời hai câu hỏi khác nhau nên nhóm báo cả hai. Từ 26/09/2026 macro được ghi trước, nhưng các vòng chọn hệ thống vẫn dựa vào micro vì luật chọn đã ghi trước bằng micro và micro ít nhiễu hơn trên tập dev nhỏ (ADR-0031). Trước ngày này, số chính của dự án là micro; việc lệch này được nêu công khai ở Chương 6.

**PSDS.** Event-F1 gắn với một ngưỡng duy nhất. Điểm PSDS (Polyphonic Sound Detection Score) đánh giá trên cả **dải** ngưỡng, dùng tỷ lệ giao thời gian thay cho collar [@bilen2020psds]. Nhóm dùng hai kịch bản cố định trước khi chạy test: PSDS-1 nhấn mạnh việc định vị đúng thời điểm, PSDS-2 nhấn mạnh việc tránh nhầm lớp (docs/evaluation_protocol.md §3.3). Một hệ thống có thể tốt ở kịch bản này mà kém ở kịch bản kia; chênh lệch đó là thông tin cần báo.

**Mức khó.** Ở thử thách DCASE 2016 (nhiệm vụ 3, ghi âm đời thực), các hệ thống đạt event-F1 chỉ 4,7–6,3% [@dcase2016task3]. Con số này chỉ để **định cỡ** độ khó, không so trực tiếp được với kết quả của đề tài vì khác dữ liệu, số lớp và quy tắc collar.

## Từ xác suất thành sự kiện

Cách ghép phổ biến là làm mượt chuỗi xác suất bằng lọc trung vị, so với một ngưỡng $\theta_c$, gộp các khoảng trống ngắn và bỏ sự kiện quá ngắn. Các giới hạn độ dài suy từ thống kê nhãn; nhóm chỉ suy chúng từ tập huấn luyện và quét ngưỡng trên dev (ADR-0003), vì suy từ chính tập đang chấm là một dạng rò rỉ khó thấy.

Ebbers và cộng sự chỉ ra rằng ngưỡng theo khung gắn chặt biên sự kiện với độ tin cậy: ngưỡng càng cao, thời điểm bắt đầu càng bị đẩy về nơi xác suất *đạt* ngưỡng, chứ không phải nơi nó bắt đầu tăng [@ebbers2024sound]. Họ đề xuất hộp bao sự kiện (SEBB), trong đó ngưỡng chỉ quyết định giữ hay bỏ sự kiện, không dời biên. Biến thể cSEBB xác định biên bằng cách tìm điểm xác suất đổi hướng. Trên 13 hệ thống của DCASE 2023, cSEBB tăng trung bình 4,1 điểm PSDS1 và 3,4 điểm F1 so với lọc trung vị [@ebbers2024sound]. Kết quả đó đo trên dữ liệu và mô hình khác, nên nhóm xem cSEBB là một lựa chọn phải được kiểm tra bằng kiểm chứng chéo trên dev, không mặc định là tốt hơn.

## Học chuyển giao

**Tiền huấn luyện trên AudioSet.** Kong và cộng sự công bố họ mạng PANNs, huấn luyện trên AudioSet (hơn 5.000 giờ, 527 lớp) rồi chuyển sang sáu tác vụ âm thanh khác [@kong2020panns]. Mạng CNN14 của họ là điểm xuất phát của nhánh B và C trong RQ1. Một chi tiết quan trọng với SED là các lớp gộp (pooling) làm giảm độ phân giải theo thời gian của đầu ra; Chương 4 cho thấy điều này đặt giới hạn trên đo được cho event-F1.

**Tiền huấn luyện theo khung.** Schmid và cộng sự tiền huấn luyện transformer âm thanh trên nhãn **theo khung** của AudioSet Strong (đầu ra mỗi 40 ms); trên DESED, đóng băng bộ mã hóa và chỉ huấn luyện một lớp tuyến tính đã đạt PSDS1 45,4–49,2, gần với tinh chỉnh toàn bộ (47,6–49,2) [@schmid2025effective]. Vì vậy nhóm thử bộ mã hóa đóng băng trước, do rẻ trên GPU 8 GB; một trong số đó là BEATs, mô hình tự giám sát [@chen2022beats]. Các con số trên đo trên DESED, không phải DataSED, nên chỉ là lý do để thử chứ không phải dự báo kết quả.

**Tăng cường dữ liệu.** Mixup huấn luyện trên tổ hợp lồi của hai mẫu và nhãn của chúng [@zhang2018mixup]. FilterAugment nhân trọng số ngẫu nhiên lên các dải tần để mô phỏng ảnh hưởng của môi trường âm học; trên SED, nó tăng PSDS 6,50% so với 2,13% của che dải tần [@nam2022filteraugment].

**Trùng lặp giữa các bộ dữ liệu.** Chuyển giao chỉ có nghĩa khi dữ liệu kiểm tra không nằm trong dữ liệu tiền huấn luyện. Bài mô tả DataSEC và DataSED cho biết một phần âm thanh lấy từ Freesound và AudioSet, được cắt, ghép, trộn hoặc sửa tay [@fredianelli2025environmental], nên hai bộ có thể chung bản ghi gốc (nhóm kiểm tra ở Chương 3) và mô hình tiền huấn luyện trên AudioSet có thể đã "nghe" một phần âm thanh gốc — rủi ro **không định lượng được** vì danh sách nguồn không được công bố.

## Mô tả có bám sát sự kiện và ảo giác

Ji và cộng sự định nghĩa ảo giác trong sinh văn bản là nội dung "vô nghĩa hoặc không trung thành với nguồn được cung cấp", gồm ảo giác nội tại (mâu thuẫn với nguồn) và ngoại tại (không kiểm chứng được từ nguồn) [@ji2023hallucination]. Ở đề tài, "nguồn" được định nghĩa hẹp và kiểm tra được: là danh sách sự kiện. Mô tả nhắc đến nguồn âm không có trong danh sách là ảo giác ngoại tại; mô tả đặt sai thứ tự hai sự kiện là ảo giác nội tại.

Cách định nghĩa này cho phép đo ảo giác **mà không cần câu mô tả mẫu do người viết**. Các chỉ số đếm n-gram truyền thống so mô tả với câu mẫu, nên một mô tả bịa vẫn có thể trùng nhiều n-gram mà không bị phát hiện. Trong lĩnh vực mô tả âm thanh tự động (Automated Audio Captioning – AAC) đã có các chỉ số gần. Kuan và cộng sự đề xuất ECHO, mô phỏng chỉ số CHAIR của mô tả ảnh: trích danh từ từ mô tả rồi tính tỷ lệ đối tượng không có trong nhãn thật, ở mức đối tượng và mức câu [@kuan2024echo]. ECHO không xét thời gian hay thứ tự. Kumar và cộng sự mô tả âm thanh kèm mốc thời gian và đo tỷ lệ ảo giác là phần trăm sự kiện dự đoán có điểm FLAM (một mô hình chấm độ khớp âm thanh–văn bản) dưới ngưỡng 0,25 đặt trước khi đánh giá; họ nêu rõ đánh giá theo tham chiếu coi một âm có thật nhưng chưa được chú giải là dương tính giả [@kumar2026tac]. Chỉ số của nhóm khác ở chỗ so mô tả với **dòng thời gian sự kiện đã phát hiện** bằng ràng buộc máy kiểm tra được (độ phủ, khẳng định thiếu bằng chứng, thứ tự, từ cấm, gọi tên quá mức), và có đường cưỡng chế ở bước sinh. Vì đã có công trình gần, báo cáo coi đây là **áp dụng và mở rộng**, không khẳng định chưa ai đo.

## Truy hồi và RAG

Lewis và cộng sự đề xuất RAG: kết hợp một mô hình sinh với một kho dữ liệu ngoài, được truy cập qua bộ truy hồi [@lewis2020rag]. Họ cũng nêu việc cung cấp nguồn gốc cho câu trả lời là vấn đề mở. Nhóm áp dụng tinh thần này với hai thay đổi: kho ngoài không phải văn bản tự do mà là các sự kiện có cấu trúc (lớp, bắt đầu, kết thúc, độ tin cậy), và câu trả lời bắt buộc kèm bằng chứng (mã bản ghi, khoảng thời gian); câu trả lời thiếu bằng chứng bị coi là không hợp lệ.

Để câu hỏi tiếng Việt và tiếng Anh dùng chung một kho, nhóm dùng mô hình embedding đa ngữ BGE-M3, hỗ trợ hơn 100 ngôn ngữ và đầu vào dài tới 8192 token [@chen2024m3]. Độ tương đồng vector hợp với câu hỏi mang tính ngữ nghĩa, nhưng không bảo đảm các ràng buộc cứng như "sự kiện dài hơn 30 giây" hay "tiếng kính vỡ trước tiếng còi". Những ràng buộc đó là phép so sánh số và phép nối theo thời gian nên được xử lý bằng bộ lọc trong cơ sở dữ liệu. Truy hồi kết hợp (lai) lọc cứng trước, rồi mới xếp hạng vector trong tập đã lọc, để độ tương đồng ngữ nghĩa không bao giờ ghi đè bộ lọc.

Hệ thống gần nhất với hướng này là LA-RAG: chuyển âm thanh dài thành bản ghi sự kiện có mốc thời gian lưu trong cơ sở dữ liệu SQL, phân loại ý định câu hỏi, đổi biểu thức thời gian tuyệt đối (ví dụ "trước buổi trưa") thành cửa sổ thời gian rồi truy xuất theo độ tương đồng embedding kèm bộ lọc có cấu trúc trước khi để mô hình ngôn ngữ trả lời [@hegde2026larag]. Trong phần phương pháp của công trình đó, nhóm không thấy toán tử quan hệ **giữa hai sự kiện** (trước, chồng lấn, trong lúc); đề tài bổ sung bốn điều kiện loại này bằng SQL.

Chất lượng truy hồi được đo bằng các chỉ số xếp hạng chuẩn: Recall@k (tỷ lệ kết quả liên quan nằm trong $k$ kết quả đầu), MRR và nDCG@10 (chỉ số thưởng cho kết quả liên quan được xếp cao); công thức ở Chương 4.

## Vị trí của đề tài

Các nguồn đã đọc cung cấp nền cho từng mắt xích: dữ liệu môi trường có nhãn mạnh [@fredianelli2025environmental], chỉ số SED và PSDS [@mesaros2016metrics; @bilen2020psds], ghép biên sự kiện [@ebbers2024sound], tiền huấn luyện theo đoạn và theo khung [@kong2020panns; @schmid2025effective], ảo giác [@ji2023hallucination] và RAG [@lewis2020rag]. Bài mô tả DataSED không báo cáo mô hình hay chỉ số cơ sở nào [@fredianelli2025environmental]. Trong phạm vi tra cứu (Chương 1), nhóm không thấy công trình nào khác báo số SED theo sự kiện trên DataSED, nhưng "không thấy" không đồng nghĩa với "không tồn tại", nên báo cáo không khẳng định kết quả của mình là baseline đầu tiên.

Về rò rỉ dữ liệu, Weck và Serra dùng dấu vân âm thanh để tìm các bản trùng giữa tập huấn luyện và tập đánh giá của SoundDesc và chỉ ra điểm truy hồi bị thổi phồng [@weck2023leakage]; Wijngaard và cộng sự đo mức chồng lấn giữa nhiều bộ dữ liệu âm thanh–ngôn ngữ bằng độ tương đồng embedding [@wijngaard2025survey]. Kiểm tra trùng trong một bộ dữ liệu và đo chồng lấn giữa các bộ đều đã có.

Phần còn lại của đề tài là **tích hợp có nguồn gốc và kiểm chứng được**: chuyển giao có kiểm soát trùng lặp trên cặp DataSEC–DataSED, SED đa âm trên bản ghi môi trường, mô tả bám sát sự kiện kiểm tra được bằng máy, và truy hồi trên dòng thời gian có điều kiện quan hệ giữa sự kiện, với mọi câu trả lời truy được về bản ghi, khoảng thời gian, phiên bản mô hình và mã băm tập chia. Kết quả âm tính được báo nguyên văn. Phạm vi tra cứu (ba truy vấn mở rộng và đọc sáu bài) không phải tổng quan hệ thống đầy đủ.