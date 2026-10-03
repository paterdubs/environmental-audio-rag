# GIỚI THIỆU

## Bối cảnh và lý do chọn đề tài

Giám sát tiếng ồn môi trường ngoài trời từ lâu dựa vào các chỉ số mức áp suất âm tổng hợp. Những chỉ số này cho biết một khu vực ồn đến đâu nhưng không cho biết âm thanh đến từ nguồn nào, xuất hiện lúc nào và kéo dài bao lâu. Hai đêm có cùng mức ồn trung bình có thể do giao thông hoặc do công trường gây ra, và mỗi trường hợp đòi hỏi biện pháp xử lý khác nhau. Vì vậy, bài toán đặt ra không chỉ là phân loại một đoạn âm thanh mà là phát hiện sự kiện âm thanh (Sound Event Detection – SED): xác định lớp nguồn âm cùng thời điểm bắt đầu (onset) và kết thúc (offset) của từng sự kiện trong bản ghi liên tục [@mesaros2021tutorial].

Bản ghi môi trường thực tế có ba đặc điểm làm bài toán khó hơn phân loại đoạn âm thanh đã cắt sẵn. Thứ nhất, môi trường tự nhiên mang tính đa âm (polyphonic): nhiều nguồn có thể hoạt động đồng thời, nên một khung thời gian có thể mang nhiều nhãn [@mesaros2021tutorial]. Thứ hai, nhãn mạnh (strong label) gắn onset và offset cho từng sự kiện tốn công hơn nhiều so với nhãn yếu (weak label) chỉ cho biết một lớp có mặt trong bản ghi, nên tập dữ liệu có nhãn mạnh thường nhỏ [@mesaros2021tutorial]. Thứ ba, khi kết quả phát hiện được diễn đạt thành mô tả ngôn ngữ tự nhiên để người dùng đọc, mô hình sinh văn bản có xu hướng tạo ra nội dung không trung thành với nguồn đầu vào. Hiện tượng này được gọi là ảo giác (hallucination) trong sinh ngôn ngữ tự nhiên [@ji2023hallucination].

Đề tài sử dụng hai bộ dữ liệu công bố năm 2025 của cùng nhóm tác giả: DataSEC cho phân loại sự kiện âm thanh môi trường (Sound Event Classification – SEC) và DataSED cho phát hiện sự kiện theo thời gian [@fredianelli2025environmental]. Hai bộ dữ liệu có chung hệ lớp, cùng miền tiếng ồn ngoài trời và có thể bổ trợ nhau: DataSEC gồm các đoạn âm thanh rời, còn DataSED gồm các bản ghi dài có chú giải thời gian. Sự gần gũi này tạo cơ hội học chuyển giao, nhưng cũng tạo nguy cơ hai bộ dữ liệu dùng chung bản ghi gốc. Nếu điều đó xảy ra mà không được kiểm soát, đánh giá chuyển giao sẽ trở thành huấn luyện trên chính dữ liệu kiểm tra.

Từ đó, đề tài hướng tới một hệ thống khép kín. Hệ thống nhận bản ghi môi trường và phát hiện sự kiện có định vị thời gian. Sau đó nó sinh mô tả chỉ dựa trên các sự kiện đã phát hiện, lưu sự kiện dưới dạng có cấu trúc và cho phép truy vấn lịch sử bằng câu hỏi tự nhiên. Ở bước truy vấn, hệ thống dùng kỹ thuật sinh tăng cường truy hồi (Retrieval-Augmented Generation – RAG). RAG kết hợp mô hình sinh với một bộ nhớ ngoài được truy hồi khi cần [@lewis2020rag]. Mọi câu trả lời đều phải trích dẫn được bản ghi và khoảng thời gian làm bằng chứng.

## Phát biểu bài toán

Cho một bản ghi âm môi trường liên tục $x(t)$, hệ thống cần tạo ra ba đầu ra liên kết với nhau. Đầu ra thứ nhất là dòng thời gian sự kiện (event timeline):

$$E = \{(c_i,\ t^{on}_i,\ t^{off}_i,\ s_i)\}_{i=1}^{N}$$

⟪eqno:timeline⟫

trong đó $c_i$ là lớp thuộc hệ lớp có phiên bản, $t^{on}_i < t^{off}_i$ là onset và offset tính bằng giây, $s_i \in [0, 1]$ là độ tin cậy, và các sự kiện được phép chồng lấp nhau. Đầu ra thứ hai là một mô tả (caption) $y$ được sinh **chỉ** từ $E$, sao cho mọi nguồn âm được nhắc trong $y$ đều truy ngược được về ít nhất một sự kiện trong $E$:

$$\operatorname{mention}(y) \subseteq \{\, c_i : (c_i, t^{on}_i, t^{off}_i, s_i) \in E \,\}$$

⟪eqno:grounding⟫

Đầu ra thứ ba là câu trả lời cho câu hỏi ngôn ngữ tự nhiên $q$ về lịch sử các bản ghi, kèm tập bằng chứng dạng (mã bản ghi, khoảng thời gian).

Ràng buộc ⟪eq:grounding⟫ phân biệt đề tài với bài toán sinh mô tả âm thanh tự do. Ràng buộc này kiểm tra được bằng máy chứ không chỉ là mục tiêu chất lượng. Cũng cần nói rõ giới hạn của nó: ràng buộc chỉ bảo đảm mô tả trung thành với **dòng thời gian dự đoán**. Nó không bảo đảm mô tả đúng với âm thanh thật, vì mọi sai sót của bước phát hiện sự kiện vẫn truyền sang mô tả. Hai mức đúng đắn này được tách riêng khi đánh giá (Mục 4.7 và Mục 6.4).

## Mục tiêu nghiên cứu

Mục tiêu tổng quát của đề tài là xây dựng một quy trình tái lập được, đi từ bộ dữ liệu công bố tới câu trả lời có bằng chứng. Quy trình này phải đo được ba đại lượng mà các hệ thống mô tả âm thanh thường không đo: mức đóng góp của học chuyển giao, mức ảo giác của mô tả, và mức đóng góp của bộ lọc có cấu trúc trong truy hồi. Mục tiêu cụ thể được tóm tắt trong ⟪tbl:objectives⟫.

@@CAP:tbl:objectives|Mục tiêu cụ thể và tiêu chí nghiệm thu@@

| Mã | Mục tiêu | Tiêu chí nghiệm thu |
|---|---|---|
| O1 | Quy trình dữ liệu tái lập từ nguồn công bố đến tập chia đóng băng | Mọi tệp có nguồn gốc; tập chia có SHA-256; các cổng kiểm tra dữ liệu đạt |
| O2 | Mô hình phân loại DataSEC 22 lớp | Macro-F1 và bảng theo lớp, có hiệu chuẩn |
| O3 | Mô hình SED đa âm trên DataSED 21 lớp | Event-based F1 và PSDS, không chỉ F1 theo khung |
| O4 | Đo chuyển giao DataSEC → DataSED | Các nhánh cùng ngân sách huấn luyện, cùng tập chia |
| O5 | Bộ sinh mô tả có căn cứ và bộ metric ảo giác | Tỷ lệ ảo giác đo được; ràng buộc có kiểm thử tự động |
| O6 | Truy hồi lai có vị từ thời gian | Ba cấu hình truy hồi so sánh được |
| O7 | Ứng dụng web minh họa đầu–cuối | Tải lên → dòng thời gian → mô tả → truy vấn có bằng chứng |

@@NOTE:Nguồn: đặc tả hệ thống của đề tài (docs/SYSTEM.md §1.4).@@

## Câu hỏi nghiên cứu

Đề tài đặt ba câu hỏi nghiên cứu (Research Question – RQ) chính, mỗi câu gắn với một thước đo và một điều kiện tiên quyết để câu trả lời có giá trị (⟪tbl:rq⟫). Một câu hỏi phụ về bộ phân loại phân cấp (tách lớp con bên trong các lớp gộp) chỉ được trả lời trên DataSEC, vì DataSED không có nhãn lớp con. Kết quả của câu hỏi phụ này được báo cáo như một kết quả của mô hình phân loại (Mục 6.1).

@@CAP:tbl:rq|Câu hỏi nghiên cứu, thước đo và điều kiện hợp lệ@@

| Mã | Câu hỏi | Thước đo trả lời | Điều kiện để câu trả lời có giá trị |
|---|---|---|---|
| RQ1 | Tiền huấn luyện thêm trên DataSEC có cải thiện SED trên DataSED so với chỉ tiền huấn luyện trên AudioSet không? | Hiệu C − B của event-based F1 và PSDS, nhiều seed, khoảng tin cậy | Cổng chống rò rỉ xuyên dataset đã đạt |
| RQ2 | Ràng buộc mô tả vào dòng thời gian giảm ảo giác bao nhiêu so với sinh tự do? | Hiệu tỷ lệ ảo giác và tỷ lệ bỏ sót | Các nhánh dùng cùng một dự đoán SED đã đóng băng |
| RQ3 | Truy hồi lai (lọc cứng + xếp hạng vector) so với chỉ lọc có cấu trúc hoặc chỉ vector ra sao? | nDCG@10, Recall@k, MRR, độ đúng bộ lọc | Bộ truy vấn và cách xác định độ liên quan cố định trước khi xem kết quả |

@@NOTE:Nguồn: docs/SYSTEM.md §1.3; ADR-0002; ADR-0021.@@

### RQ1 — Chuyển giao từ DataSEC sang DataSED

RQ1 so sánh ba nhánh khởi tạo bộ mã hóa: A học từ đầu, B khởi tạo từ trọng số tiền huấn luyện trên AudioSet [@kong2020panns], và C khởi tạo từ AudioSet rồi huấn luyện tiếp trên DataSEC. Phép so sánh trả lời RQ1 là **C − B** chứ không phải C − A. Hiệu C − A trộn lẫn hai tác động là tiền huấn luyện nói chung và dữ liệu DataSEC nói riêng, trong khi câu hỏi chỉ quan tâm đến phần đóng góp thêm của DataSEC (ADR-0002).

### RQ2 — Mức căn cứ và ảo giác của mô tả

RQ2 so sánh mô tả sinh tự do bởi mô hình ngôn ngữ lớn (Large Language Model – LLM) với mô tả sinh có ràng buộc giải mã, cùng một mô hình và cùng lời nhắc (prompt). Mô tả theo mẫu (template) đóng vai trò mốc sàn, có căn cứ hoàn toàn theo thiết kế. Đánh giá được thực hiện ở hai mức. Mức *oracle* dùng dòng thời gian từ nhãn gốc, trả lời câu hỏi bản thân bộ sinh mô tả có căn cứ hay không. Mức *đầu–cuối* (end-to-end) dùng dòng thời gian do SED dự đoán, trả lời câu hỏi hệ thống thật có căn cứ hay không.

### RQ3 — Truy hồi có cấu trúc, vector và lai

RQ3 đánh giá vai trò của bộ lọc cứng theo lớp, theo thời lượng và theo quan hệ thời gian (trước, sau, chồng lấp, nằm trong) so với xếp hạng theo độ tương đồng ngữ nghĩa. Độ liên quan của mỗi truy vấn được tính bằng máy từ nhãn gốc, không phụ thuộc vào đầu ra của hệ thống đang được đánh giá.

## Phạm vi và giới hạn

Phạm vi của đề tài gồm âm thanh môi trường ngoài trời, xử lý theo lô (offline), SED đa âm trên 21 lớp của DataSED, phân loại 22 lớp gộp cùng 28 lớp con của DataSEC, mô tả tiếng Anh dùng để đánh giá và tiếng Việt dùng cho giao diện, và truy vấn theo lớp, thời gian, thời lượng, độ tin cậy cùng quan hệ trước–sau.

Đề tài chủ động loại khỏi phạm vi một số hướng có vẻ hấp dẫn nhưng không có cơ sở trong dữ liệu (ADR-0001). Hệ thống không nhận dạng nội dung lời nói hay người nói, vì lớp `voices` chỉ là một nguồn âm và phân tích nội dung vi phạm quyền riêng tư. Hệ thống không suy luận tội phạm, ý định, tai nạn hay tình huống khẩn cấp, và không gán điểm rủi ro hay mức nguy hiểm, vì bằng chứng âm học không đủ để rút ra các kết luận đó. Mọi câu trong mô tả và câu trả lời chỉ được nói về *nguồn âm quan sát được*, không được nói về *tình huống*. Chẳng hạn, "phát hiện tiếng kính vỡ lúc 5,4 s" là hợp lệ, còn "phát hiện đột nhập" là không hợp lệ. Xử lý luồng gần thời gian thực và định vị nguồn âm trong không gian cũng nằm ngoài phạm vi: thư mục dịch vụ luồng mới chỉ là khung rỗng, và hai bộ dữ liệu không có nhãn không gian.

## Đóng góp dự kiến và bằng chứng hiện có

Đề cương ban đầu nêu bốn đóng góp dự kiến. Tại thời điểm giữa kỳ, báo cáo tách rõ phần đã có bằng chứng thực nghiệm với phần vẫn là định hướng (⟪tbl:contrib⟫). Đề tài **chưa** thực hiện khảo sát văn liệu có hệ thống, nên các nhận định về tính mới so với công trình khác chưa được khẳng định. Đây là việc của giai đoạn sau (Mục 7.4).

@@CAP:tbl:contrib|Đóng góp dự kiến và mức bằng chứng tại thời điểm giữa kỳ@@

| Mã | Đóng góp dự kiến | Bằng chứng đã có (Chương 6) | Phần chưa khẳng định |
|---|---|---|---|
| C1 | Bộ sinh mô tả có hợp đồng căn cứ kiểm được bằng máy | Ràng buộc G1–G3 có kiểm thử tự động; ngữ pháp giải mã đưa ảo giác, từ cấm và gọi tên quá cụ thể về 0 trên tập test | Tính mới so với văn liệu mô tả âm thanh |
| C2 | Bộ metric đo mức căn cứ của mô tả không cần câu tham chiếu | Ảo giác, bỏ sót, thứ tự, từ cấm, có khoảng tin cậy; đối chiếu với một người đọc trên 60 mô tả | Mẫu đối chiếu nhỏ, một người đọc |
| C3 | Đo chuyển giao có kiểm soát rò rỉ xuyên dataset | Phát hiện ba nhóm trùng xuyên DataSEC–DataSED; loại 11 đoạn; RQ1 âm tính với nhiều seed | Nhận định "nghiên cứu khác thường không kiểm tra" |
| C4 | RAG trên dòng thời gian sự kiện có vị từ thời gian | Bốn vị từ thời gian bằng SQL; độ đúng bộ lọc 1,000; không có khẳng định thiếu bằng chứng trong câu trả lời | Tính mới so với văn liệu truy hồi âm thanh |

@@NOTE:Nguồn: docs/PAPER_NOTES.md §2; docs/RELATED_WORK.md §9.@@

## Cấu trúc báo cáo

Ngoài chương này, báo cáo gồm sáu chương. Chương 2 trình bày cơ sở lý thuyết về SED và metric đánh giá, học chuyển giao, sinh mô tả có căn cứ và RAG. Chương 3 mô tả hai bộ dữ liệu cùng quy trình chuẩn bị dữ liệu có kiểm soát rò rỉ. Chương 4 trình bày phương pháp: mô hình phân loại, các thế hệ mô hình SED, hậu xử lý, sinh mô tả, truy hồi và giao thức đánh giá. Chương 5 mô tả phần triển khai hệ thống. Chương 6 báo cáo các kết quả đã có, kể cả kết quả âm tính và kết quả suy giảm, cùng các mối đe dọa đến tính hợp lệ. Chương 7 đối chiếu tiến độ với kế hoạch, kết luận mức độ đạt mục tiêu tại giữa kỳ và nêu kế hoạch giai đoạn tiếp theo.
