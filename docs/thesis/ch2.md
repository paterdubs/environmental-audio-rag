# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VÀ CÔNG TRÌNH LIÊN QUAN

## 2.1. Phát hiện sự kiện âm thanh đa nhãn

Sound Event Detection (SED) là bài toán xác định lớp và khoảng thời gian hoạt động của các sự kiện âm thanh trong một bản ghi. Khác với phân loại một nhãn duy nhất cho toàn clip, SED đa nhãn cho phép nhiều lớp cùng hoạt động tại một thời điểm. Với frame thời gian \(t\) và lớp \(c\), mô hình dự đoán xác suất

\[
\hat{y}_{t,c}=\sigma\left(f_{\theta}(x)_{t,c}\right),
\]

trong đó sigmoid được áp dụng độc lập cho từng lớp. Cách biểu diễn này phù hợp với soundscape đa âm vì sự xuất hiện của một lớp không loại trừ lớp khác.

### 2.1.1. Nhãn clip-level và strong label

Nhãn clip-level chỉ cho biết một lớp có xuất hiện trong toàn bộ clip hay không. Loại nhãn này phù hợp cho audio tagging hoặc phân loại, nhưng không đủ để xác định onset và offset. Ngược lại, strong label gắn mỗi sự kiện với lớp, thời điểm bắt đầu và thời điểm kết thúc. DataSEC cung cấp dữ liệu cho phân loại, trong khi DataSED cung cấp annotation theo thời gian cho SED; hai vai trò này phản ánh thiết kế của bộ dữ liệu được công bố [@fredianelli2025environmental].

Strong label là điều kiện cần cho chuỗi xử lý của đề tài. Không có onset và offset, chúng tôi không thể đánh giá biên sự kiện, không thể tạo evidence theo time span và cũng không thể kiểm tra quan hệ trước–sau trong tầng truy vấn. Vì vậy, DataSEC được dùng cho học biểu diễn và phân loại hỗ trợ, còn DataSED là benchmark temporal chính. Quyết định phân vai dữ liệu được khóa tại [ADR-0001](../decisions/ADR-0001-scope-and-datasets.md).

### 2.1.2. Event-based F1, collar và PSDS

Đầu ra frame-level cần được chuyển thành danh sách event trước khi đánh giá. Sau khi nhị phân hóa xác suất, hệ thống có thể làm trơn chuỗi, gộp các đoạn liền kề, loại event quá ngắn và nối các event cùng lớp bị ngắt bởi khoảng trống nhỏ. Vì bước này làm thay đổi số lượng và biên event, chất lượng hậu xử lý không thể được suy ra chỉ từ frame-F1.

Event-based F1 ghép từng event dự đoán với event tham chiếu cùng lớp. Một cặp được xem là khớp khi sai lệch onset nằm trong collar cho phép và sai lệch offset thỏa dung sai tuyệt đối hoặc tương đối theo độ dài event. Collar phản ánh thực tế rằng ranh giới âm học không luôn sắc nét, nhưng đồng thời khiến kết quả phụ thuộc vào giao thức đánh giá. DCASE đã sử dụng đánh giá ở mức segment và event cho SED trên bản ghi thực; do khác dữ liệu và quy tắc collar, các con số giữa benchmark không được so sánh trực tiếp [@dcase2016task3].

PSDS đánh giá hệ thống trên một dải operating point thay vì chỉ tại một ngưỡng đã chọn. Metric này xét mức giao nhau giữa detection và ground truth, đồng thời có thể phạt cross-trigger giữa các lớp. Trong báo cáo, chúng tôi dùng event-based F1 làm chỉ số trực tiếp tại hậu xử lý đã khóa và dùng PSDS như góc nhìn bổ sung về hành vi theo ngưỡng. Lựa chọn metric và collar được giữ cố định theo giao thức đánh giá của dự án; không thay đổi sau khi xem test.

### 2.1.3. Hậu xử lý ngưỡng và cSEBB

Hậu xử lý theo ngưỡng frame liên kết hai quyết định: event có được giữ hay không và biên event nằm ở đâu. Với mỗi lớp, pipeline truyền thống cần ngưỡng xác suất \(\theta\), độ rộng làm trơn, thời lượng tối thiểu và khoảng trống tối đa để gộp event. Trong đề tài, \(\theta\) được chọn trên dev vì phụ thuộc phân bố điểm của mô hình; các duration prior được suy từ train để tránh đưa thống kê của dev hoặc test vào hậu xử lý. Quy tắc này được khóa tại [ADR-0003](../decisions/ADR-0003-threshold-va-post-processing.md).

Sound Event Bounding Boxes tách biên sự kiện khỏi quyết định giữ hoặc bỏ event. Trong cách tiếp cận cSEBB, onset và offset được suy từ biến thiên của posterior sau làm trơn, sau đó một độ tin cậy được gán cho toàn event; threshold chỉ quyết định chọn bounding box chứ không dời biên. Ebbers và cộng sự báo cáo lợi ích của cSEBB trên nhiều hệ SED thuộc DCASE, nhưng phương pháp vẫn cần được thẩm định trên posterior và dữ liệu cụ thể [@ebbers2024sound]. Vì vậy, chúng tôi xem cSEBB là một họ hậu xử lý cạnh tranh với ngưỡng global, lựa chọn bằng cross-validation trên dev thay vì mặc định coi nó tốt hơn. Thiết kế và lưới lựa chọn được ghi tại [ADR-0030](../decisions/ADR-0030-cai-thien-sed-v2.md).

## 2.2. Transfer learning cho âm thanh môi trường

### 2.2.1. AudioSet và encoder tiền huấn luyện

Transfer learning dùng encoder đã học biểu diễn âm thanh trên một corpus nguồn, sau đó thích nghi encoder hoặc head cho dữ liệu đích. Trong đề tài, nhánh scratch cung cấp mốc không tiền huấn luyện; nhánh AudioSet đo lợi ích của pretraining tổng quát; nhánh AudioSet→DataSEC→DataSED đo phần đóng góp bổ sung của DataSEC. Chỉ đối chiếu nhánh cuối với nhánh AudioSet mới cô lập được tác động của DataSEC. Thiết kế đối chứng này được khóa tại [ADR-0002](../decisions/ADR-0002-encoder-va-nhanh-transfer.md).

Encoder tiền huấn luyện cho tagging không nhất thiết có độ phân giải thời gian phù hợp với SED. Nếu pooling theo thời gian quá mạnh, việc nội suy đầu ra chỉ phục hồi kích thước tensor, không phục hồi thông tin về biên đã mất. Đây là lý do chúng tôi tách vấn đề “nhận ra lớp” khỏi vấn đề “định vị event” và ghi rõ giới hạn độ phân giải của baseline tại [ADR-0014](../decisions/ADR-0014-doi-chieu-do-phan-giai-thoi-gian-cnn14.md).

### 2.2.2. Pretraining theo frame

Pretraining theo frame cung cấp giám sát thời gian ngay từ corpus nguồn, phù hợp hơn với mục tiêu định vị onset và offset. Schmid và cộng sự khảo sát các encoder âm thanh tiền huấn luyện với nhãn theo frame và cho thấy cả chế độ đóng băng lẫn fine-tune đều có thể được dùng cho SED [@schmid2025effective]. Kết quả này tạo cơ sở để đề tài mở một track encoder theo frame, nhưng không đủ để giả định một checkpoint cụ thể sẽ thắng trên DataSED.

Chúng tôi vì thế triển khai hai hướng có vai trò khác nhau: encoder transformer đóng băng kết hợp head tuần tự và Frame-MobileNet được fine-tune toàn bộ. Thứ tự thử nghiệm, cổng khả thi, checkpoint và các ứng viên ensemble được ghi trước tại [ADR-0032](../decisions/ADR-0032-track2-encoder-pretrain-theo-frame.md). Việc ghi trước ngăn quá trình lựa chọn kiến trúc bị dẫn hướng bởi kết quả test.

### 2.2.3. Domain shift và nguy cơ leakage

DataSEC gồm các clip phục vụ phân loại, còn DataSED gồm soundscape liên tục có nhiều nguồn chồng lấp. Giữa hai miền có khác biệt về nền âm, thời lượng, mật độ event và phân bố lớp. Vì vậy, tiền huấn luyện trên DataSEC có thể giúp học đặc trưng lớp nhưng cũng có thể không chuyển thành khả năng định vị thời gian trên DataSED.

Một nguy cơ nghiêm trọng hơn domain shift là duplicate leakage. Hai dataset cùng miền và cùng nhóm công bố có thể chia sẻ nguồn âm; khi một đoạn thuộc recording đích đã xuất hiện trong corpus tiền huấn luyện, chênh lệch transfer không còn phản ánh khả năng khái quát hóa. Chúng tôi xử lý rủi ro này bằng fingerprint nhiều tầng, duyệt thủ công các cặp nghi vấn và gom nguồn liên quan vào leakage group trước khi split. Ngưỡng overlap và luật loại clip pretraining được khóa tại [ADR-0007](../decisions/ADR-0007-fingerprint-va-luat-dedup.md) và [ADR-0009](../decisions/ADR-0009-nguong-phu-thuoc-overlap.md).

## 2.3. Sinh mô tả có ràng buộc bằng chứng

Trong đề tài, Automated Audio Captioning được thu hẹp thành bài toán sinh mô tả từ event timeline đã đóng băng. Đầu vào của captioner chỉ gồm lớp, onset và offset; mô hình ngôn ngữ không nhận waveform. Thiết kế này giúp tách lỗi phát hiện khỏi lỗi diễn đạt và cho phép truy ngược từng mention về event nguồn.

Chúng tôi phân biệt các lỗi factual sau: hallucination khi caption nhắc nguồn âm ngoài timeline; omission khi một event không được nhắc; sai thứ tự khi thứ tự mention không phù hợp onset; gọi tên quá cụ thể khi bằng chứng chỉ hỗ trợ một lớp gộp; và suy diễn bối cảnh không có trong timeline. Các metric n-gram vẫn được báo như chỉ số phụ, nhưng không thay thế kiểm tra grounding vì tương đồng câu chữ không bảo đảm tính đúng của nguồn âm.

Ba chế độ sinh tạo thành phổ kiểm soát. `unconstrained` cho mô hình sinh tự do để đo lỗi; `constrained` giới hạn cấu trúc đầu ra và gắn evidence; `constrained_cover` bổ sung cơ chế bảo đảm độ phủ event. Cùng một mô hình và cùng timeline được dùng để sự khác biệt phản ánh ràng buộc decode. Lựa chọn LLM và lexicon được khóa tại [ADR-0022](../decisions/ADR-0022-llm-va-lexicon-cho-rq2.md), hợp đồng nhánh constrained tại [ADR-0023](../decisions/ADR-0023-nhanh-caption-constrained.md), biến thể cover tại [ADR-0026](../decisions/ADR-0026-constrained-cover.md), và cách diễn đạt tiếng Việt tại [ADR-0025](../decisions/ADR-0025-caption-tieng-viet.md).

## 2.4. Retrieval-Augmented Generation trên event timeline

RAG kết hợp truy hồi tài liệu với sinh câu trả lời. Trong hệ thống này, tài liệu không phải đoạn văn tự do đơn thuần mà là biểu diễn của một recording gồm event timeline, caption song ngữ và các trường provenance. Cách tổ chức đó cho phép câu trả lời trỏ tới mã bản ghi và time span thay vì chỉ trả lại văn bản có độ tương đồng cao.

Truy hồi thuần vector phù hợp với diễn đạt ngôn ngữ khác nhau, nhưng không bảo đảm các điều kiện cứng như lớp bắt buộc, thời lượng tối thiểu, độ tin cậy hoặc quan hệ trước–sau. Ngược lại, truy hồi có cấu trúc áp dụng chính xác predicate nhưng ít linh hoạt trước paraphrase. Kiến trúc hybrid của đề tài áp bộ lọc cứng trước, sau đó dùng embedding để xếp hạng trong tập đã thỏa điều kiện; điểm vector không được phép đưa một bản ghi vi phạm filter trở lại kết quả.

Corpus, document, embedding và query set được khóa tại [ADR-0027](../decisions/ADR-0027-dau-vao-retrieval-va-query-set.md). Để người dùng không phải nhập JSON filter, parser L2 chuyển câu hỏi tiếng Anh hoặc tiếng Việt thành schema bộ lọc; nếu parser không sẵn sàng, giao diện quay về bộ lọc thủ công thay vì âm thầm bỏ điều kiện. Quyết định này được ghi tại [ADR-0036](../decisions/ADR-0036-parser-cau-hoi-thanh-bo-loc-retrieval.md).

## 2.5. Tổng hợp khoảng trống nghiên cứu

Các nguồn đã xác minh cung cấp nền tảng cho dữ liệu môi trường, đánh giá SED trên ghi âm thực, hậu xử lý biên event và pretraining theo frame [@fredianelli2025environmental; @dcase2016task3; @ebbers2024sound; @schmid2025effective]. Trên nền đó, đề tài tập trung vào khoảng nối giữa các thành phần: transfer có audit leakage, SED đa âm, caption có hợp đồng grounding và RAG trên event timeline có predicate thời gian.

Chúng tôi không khẳng định chưa có công trình nào từng giải quyết từng thành phần hoặc toàn bộ chuỗi. Việc rà soát có hệ thống cho AAC hallucination và audio retrieval chưa đạt mức xác minh cần thiết để bảo vệ một tuyên bố như vậy. Do đó, khoảng trống được phát biểu ở mức có thể kiểm chứng: xây dựng và đánh giá chuỗi liền mạch trên DataSEC–DataSED, trong đó câu trả lời cuối truy được về recording, time span, model version, split và taxonomy đã khóa.

## Cần người dùng kiểm

- [ ] Xác nhận thuật ngữ tiếng Việt “nhãn theo frame” và “nhãn mạnh” có cần giữ kèm thuật ngữ tiếng Anh *strong label* ở mọi lần xuất hiện hay chỉ ở lần đầu.
- [ ] Xác nhận cách dùng từ “hallucination” trong thân báo cáo hay thay bằng “thông tin không có căn cứ”, đồng thời giữ thuật ngữ tiếng Anh trong ngoặc.
- [ ] Xác nhận khoa chấp nhận kiểu trích dẫn Pandoc `[@khóa]` trước khi chuyển sang DOCX; nếu không, bước dàn trang sẽ đổi sang kiểu trích dẫn theo mẫu khoa.
