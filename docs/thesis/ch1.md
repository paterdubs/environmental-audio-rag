# CHƯƠNG 1. GIỚI THIỆU

## 1.1. Bối cảnh và lý do chọn đề tài

Giám sát âm thanh môi trường không chỉ cần xác định một bản ghi có chứa loại âm thanh nào, mà còn cần biết sự kiện xuất hiện khi nào, kéo dài bao lâu và có chồng lấp với sự kiện khác hay không. So với bài toán phân loại một đoạn âm thanh đã được tách tương đối rõ, bản ghi môi trường liên tục đặt ra khó khăn lớn hơn do nhiều nguồn âm đồng thời, nền âm thay đổi và ranh giới sự kiện không luôn rõ ràng. DataSEC và DataSED được công bố cho hai bối cảnh bổ trợ nhau: phân loại sự kiện âm thanh môi trường và phát hiện sự kiện theo thời gian [@fredianelli2025environmental].

Một hệ thống chỉ trả về nhãn và khoảng thời gian vẫn chưa đủ thuận tiện cho người sử dụng. Kết quả cần được diễn đạt bằng ngôn ngữ tự nhiên và có thể được truy vấn lại trên nhiều bản ghi. Tuy nhiên, bước sinh ngôn ngữ làm xuất hiện một rủi ro mới: câu mô tả có thể bổ sung nguồn âm, nguyên nhân hoặc bối cảnh không được timeline sự kiện hỗ trợ. Ví dụ, tín hiệu có thể chỉ cho phép kết luận rằng có âm thanh thuộc lớp còi hú và báo động, nhưng không đủ căn cứ để khẳng định loại phương tiện, tình trạng khẩn cấp hay mục đích của âm thanh đó.

Từ nhu cầu trên, chúng tôi thực hiện đề tài **“Xây dựng hệ thống phát hiện, sinh mô tả và truy vấn sự kiện âm thanh môi trường dựa trên RAG”**. Hệ thống kết nối bốn khâu: phát hiện sự kiện âm thanh, biểu diễn kết quả thành timeline có provenance, sinh mô tả bám theo timeline và truy vấn có bằng chứng bằng RAG. Phạm vi này được khóa tại [ADR-0001](../decisions/ADR-0001-scope-and-datasets.md): miền ứng dụng là giám sát âm thanh môi trường, không phải an ninh, phát hiện tội phạm hay suy luận tình trạng khẩn cấp.

## 1.2. Phát biểu bài toán

Với một bản ghi âm môi trường liên tục \(x(t)\), chúng tôi cần xây dựng một pipeline tạo ra ba lớp kết quả có quan hệ truy vết:

1. Một **event timeline** \(E\), trong đó mỗi sự kiện gồm lớp âm thanh \(c_i\), thời điểm bắt đầu \(t_i^{on}\), thời điểm kết thúc \(t_i^{off}\) và độ tin cậy \(s_i\). Timeline cho phép nhiều sự kiện chồng lấp.
2. Một **caption có căn cứ** \(y\), được sinh từ timeline thay vì suy luận trực tiếp một cách tự do từ ngữ cảnh. Mọi nguồn âm được nhắc trong caption phải ánh xạ được tới ít nhất một sự kiện trong \(E\).
3. Một **câu trả lời truy vấn** cho câu hỏi ngôn ngữ tự nhiên \(q\), đi kèm bằng chứng gồm mã bản ghi và khoảng thời gian tương ứng.

Ràng buộc cốt lõi của tầng caption được biểu diễn như sau:

\[
\operatorname{mentions}(y) \subseteq \operatorname{classes}(E).
\]

Ràng buộc này chuyển tính đúng đắn của mô tả từ một yêu cầu định tính thành một hợp đồng có thể kiểm tra tự động. Chúng tôi áp dụng cùng nguyên tắc cho tầng truy vấn: câu trả lời chỉ được tổng hợp từ các tài liệu sự kiện đã truy hồi và phải giữ liên kết tới bằng chứng. Lựa chọn xây caption từ timeline và đo riêng hallucination được ghi tại [ADR-0022](../decisions/ADR-0022-llm-va-lexicon-cho-rq2.md); lựa chọn dùng event làm đơn vị dữ liệu truy hồi được ghi tại [ADR-0027](../decisions/ADR-0027-dau-vao-retrieval-va-query-set.md).

## 1.3. Mục tiêu nghiên cứu

Mục tiêu tổng quát của đề tài là xây dựng một hệ thống local, tái lập được, đi từ dữ liệu âm thanh đến câu trả lời có bằng chứng, đồng thời đánh giá riêng chất lượng phát hiện, mức bám căn cứ của caption và hiệu quả truy hồi.

Các mục tiêu cụ thể gồm:

- xây dựng quy trình dữ liệu có provenance, khử trùng lặp xuyên dataset và split theo nhóm nguồn để hạn chế leakage;
- xây dựng và so sánh các hệ thống SED trên bản ghi đa âm, bao gồm các phương án transfer learning và encoder tiền huấn luyện theo frame;
- xây dựng caption tiếng Anh và tiếng Việt từ event timeline, với hợp đồng grounding có thể kiểm tra bằng máy;
- xây dựng event store và tầng RAG hỗ trợ lọc có cấu trúc, tìm kiếm vector, truy hồi lai và quan hệ thời gian;
- triển khai giao diện local cho quy trình upload, xem timeline, đọc caption, đặt câu hỏi và mở đúng đoạn âm thanh làm bằng chứng;
- lưu cấu hình, revision, hash dữ liệu và artifact đánh giá để các kết quả có thể được đối chiếu và tái lập.

Các mục tiêu trên không bao gồm nhận dạng nội dung lời nói, định danh người nói, suy luận ý định, chấm điểm rủi ro hay phát cảnh báo khẩn cấp. Giới hạn này là hệ quả trực tiếp của [ADR-0001](../decisions/ADR-0001-scope-and-datasets.md): nhãn của dữ liệu mô tả nguồn âm, không cung cấp ground truth cho các kết luận về tình huống.

## 1.4. Câu hỏi nghiên cứu

### 1.4.1. RQ1 — Transfer learning DataSEC → DataSED

**RQ1:** Việc tiền huấn luyện bổ sung trên DataSEC cải thiện SED trên DataSED đến mức nào so với khởi tạo từ AudioSet mà không qua DataSEC?

Chúng tôi so sánh các nhánh có cùng dữ liệu đích, ngân sách huấn luyện và giao thức hậu xử lý. Câu hỏi chỉ có ý nghĩa khi các nguồn trùng giữa DataSEC và DataSED đã được phát hiện và cô lập khỏi đường transfer; vì vậy audit leakage là điều kiện tiên quyết, không phải bước làm sạch phụ. Thiết kế ba nhánh được khóa tại [ADR-0002](../decisions/ADR-0002-encoder-va-nhanh-transfer.md), luật xử lý overlap tại [ADR-0009](../decisions/ADR-0009-nguong-phu-thuoc-overlap.md), còn cách diễn giải kết quả âm tính được khóa tại [ADR-0021](../decisions/ADR-0021-rq1-ket-qua-am-tinh.md).

### 1.4.2. RQ2 — Grounding và hallucination của caption

**RQ2:** Caption bị ràng buộc bởi event timeline thay đổi hallucination và omission như thế nào so với caption sinh tự do?

Chúng tôi giữ nguyên timeline đầu vào giữa các nhánh để sự khác biệt phản ánh cơ chế sinh caption thay vì thay đổi từ SED. Ngoài các chỉ số ngôn ngữ bề mặt, phép đánh giá tập trung vào việc caption có nhắc nguồn âm ngoài timeline, bỏ sót sự kiện, làm sai thứ tự thời gian hoặc dùng từ bị cấm hay không. Nhánh sinh tự do và lexicon đánh giá được quy định tại [ADR-0022](../decisions/ADR-0022-llm-va-lexicon-cho-rq2.md); nhánh constrained và cơ chế evidence được quy định tại [ADR-0023](../decisions/ADR-0023-nhanh-caption-constrained.md); biến thể ưu tiên độ phủ được bổ sung tại [ADR-0026](../decisions/ADR-0026-constrained-cover.md).

### 1.4.3. RQ3 — Structured, vector và hybrid retrieval

**RQ3:** Truy hồi lai giữa bộ lọc có cấu trúc và embedding vector hoạt động như thế nào so với từng thành phần riêng lẻ khi truy vấn event timeline?

Ba cấu hình được so sánh trên cùng corpus và query set được xây dựng trước khi xem kết quả. Bộ lọc có cấu trúc khai thác lớp, thời lượng, độ tin cậy và quan hệ trước–sau; nhánh vector hỗ trợ tương đồng ngữ nghĩa và truy vấn song ngữ; nhánh hybrid kết hợp hai tín hiệu. Đầu vào corpus và query set được khóa tại [ADR-0027](../decisions/ADR-0027-dau-vao-retrieval-va-query-set.md), còn parser chuyển câu hỏi tự nhiên thành bộ lọc được khóa tại [ADR-0036](../decisions/ADR-0036-parser-cau-hoi-thanh-bo-loc-retrieval.md).

## 1.5. Phạm vi và giới hạn

Đề tài tập trung vào âm thanh môi trường và xử lý batch/offline. Đầu ra SED là các sự kiện đa âm có nhãn coarse, khoảng thời gian và độ tin cậy. Caption benchmark dùng tiếng Anh; giao diện hỗ trợ thêm tiếng Việt. Tầng truy vấn làm việc trên event timeline và caption đã lưu, hỗ trợ điều kiện theo lớp, thời gian, thời lượng, độ tin cậy và quan hệ thời gian.

Chúng tôi không phân tích nội dung hội thoại hoặc nhận dạng người nói. Hệ thống cũng không định vị nguồn âm trong không gian vì dữ liệu không cung cấp nhãn không gian. Quan trọng hơn, hệ thống không suy luận tội phạm, tai nạn, ý định hay tình trạng khẩn cấp; không xây dựng **risk score**, **severity score** hoặc cơ chế cảnh báo. Một nhãn như `glass_breaking` chỉ cho phép báo cáo sự hiện diện của âm thanh thuộc lớp đó trong một khoảng thời gian, không cho phép suy ra nguyên nhân của sự kiện.

Phạm vi triển khai là demo local có thể kiểm chứng luồng đầu-cuối, không phải hệ thống streaming thời gian thực hay sản phẩm vận hành ngoài hiện trường. Các giới hạn này giúp kết luận của đề tài bám đúng miền dữ liệu và tránh tuyên bố vượt quá bằng chứng.

## 1.6. Đóng góp của đề tài

Trong phạm vi khóa luận, chúng tôi tổng hợp bốn đóng góp chính:

- **C1 — Grounded captioning:** xây dựng cơ chế sinh mô tả từ event timeline với hợp đồng rằng mọi nguồn âm được nhắc phải có sự kiện tương ứng.
- **C2 — Đánh giá factual grounding:** xây dựng phép đo hallucination, omission, thứ tự thời gian và độ phủ evidence mà không phụ thuộc hoàn toàn vào một câu mô tả tham chiếu.
- **C3 — Transfer có kiểm soát leakage:** audit trùng lặp nội bộ và xuyên DataSEC–DataSED trước khi đo ảnh hưởng của tiền huấn luyện từ dữ liệu phân loại sang SED.
- **C4 — RAG trên event timeline:** tổ chức sự kiện thành tài liệu truy hồi có provenance và hỗ trợ predicate thời gian bên cạnh tương đồng ngữ nghĩa.

Chúng tôi không tuyên bố các cơ chế trên là đầu tiên trong toàn bộ văn liệu. Phần tổng quan hiện chỉ sử dụng các nguồn đã được đọc và xác minh; do đó, các đóng góp được trình bày như thiết kế, triển khai và đánh giá trong phạm vi cặp dữ liệu và hệ thống của đề tài.

## 1.7. Cấu trúc báo cáo

Phần còn lại của báo cáo được tổ chức như sau. Chương 2 trình bày cơ sở lý thuyết và các công trình liên quan đã được xác minh. Chương 3 mô tả dữ liệu, taxonomy, quy trình D0–D4 và các biện pháp kiểm soát leakage. Chương 4 trình bày phương pháp, kiến trúc SED, grounded captioning, event store, RAG và nguyên tắc provenance. Chương 5 mô tả giao thức thực nghiệm và kết quả cho các câu hỏi nghiên cứu. Chương 6 trình bày ứng dụng demo local và phương án dự phòng. Chương 7 tổng kết kết quả, giới hạn và hướng phát triển. Các phụ lục lưu taxonomy, cấu hình, artifact freeze, bảng kết quả đầy đủ và lệnh tái lập.

## Cần người dùng kiểm

- [ ] Xác nhận cách gọi “giám sát âm thanh môi trường” phù hợp với thuật ngữ mà khoa và giảng viên hướng dẫn mong muốn.
- [ ] Xác nhận có giữ ký hiệu đóng góp C1–C4 trong bản nộp hay chuyển thành danh sách không đánh mã.
- [ ] Xác nhận khoa chấp nhận ngôi thứ nhất số nhiều “chúng tôi” xuyên suốt báo cáo.
