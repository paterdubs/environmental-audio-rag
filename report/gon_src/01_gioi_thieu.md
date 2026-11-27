# GIỚI THIỆU

Chương này nêu vấn đề, bối cảnh áp dụng ở Việt Nam, ba câu hỏi nghiên cứu, các đóng góp và kết quả chính của khóa luận.

## Vì sao chọn đề tài

Giám sát tiếng ồn ngoài trời thường chỉ dựa vào mức ồn trung bình. Con số này cho biết một khu vực ồn đến đâu, nhưng không cho biết tiếng ồn đến từ nguồn nào, xuất hiện lúc nào và kéo dài bao lâu. Hai đêm có cùng mức ồn có thể do xe cộ hoặc do công trường, và mỗi trường hợp cần cách xử lý khác nhau.

Vì vậy nhóm chọn bài toán phát hiện sự kiện âm thanh (Sound Event Detection – SED): trong một bản ghi dài, tìm các nguồn âm, thời điểm bắt đầu (onset) và kết thúc (offset) của từng nguồn [@mesaros2021tutorial]. Bài toán này khó hơn phân loại một đoạn âm thanh đã cắt sẵn vì ba lý do. Thứ nhất, nhiều nguồn có thể vang lên cùng lúc (đa âm) [@mesaros2021tutorial]. Thứ hai, nhãn có thời điểm chính xác tốn công làm nên thường ít [@mesaros2021tutorial]. Thứ ba, khi kết quả được viết thành câu văn, mô hình ngôn ngữ dễ viết ra điều không có trong dữ liệu; hiện tượng này gọi là ảo giác [@ji2023hallucination].

Nhóm dùng hai bộ dữ liệu công bố năm 2025 của cùng một nhóm tác giả: DataSEC gồm các đoạn âm thanh rời để phân loại, DataSED gồm các bản ghi dài có nhãn thời gian [@fredianelli2025environmental]. Hai bộ cùng lĩnh vực nên có thể hỗ trợ nhau (học chuyển giao), nhưng cũng có thể chứa cùng một bản ghi gốc. Nếu không kiểm soát, mô hình sẽ vô tình được học trên chính dữ liệu dùng để kiểm tra.

Từ đó, đề tài xây dựng một hệ thống gồm bốn bước: nhận bản ghi và phát hiện sự kiện; viết mô tả chỉ từ các sự kiện đã phát hiện; lưu sự kiện có cấu trúc; và trả lời câu hỏi về lịch sử bản ghi bằng sinh tăng cường truy hồi (Retrieval-Augmented Generation – RAG). RAG cho mô hình tra cứu một kho dữ liệu bên ngoài trước khi trả lời [@lewis2020rag]. Mỗi câu trả lời phải nêu được bản ghi và khoảng thời gian làm bằng chứng.

## Bài toán đặt ra

Với một bản ghi âm liên tục $x(t)$, hệ thống cho ba đầu ra. Đầu ra thứ nhất là danh sách sự kiện, còn gọi là dòng thời gian:

$$E = \{(c_i,\ t^{on}_i,\ t^{off}_i,\ s_i)\}_{i=1}^{N}$$

⟪eqno:timeline⟫

trong đó $c_i$ là lớp nguồn âm, $t^{on}_i < t^{off}_i$ là thời điểm bắt đầu và kết thúc (giây), $s_i \in [0, 1]$ là độ tin cậy; các sự kiện được phép chồng nhau. Đầu ra thứ hai là một câu mô tả $y$ chỉ được viết từ $E$: mọi nguồn âm được nhắc đến phải có trong $E$.

$$\operatorname{mention}(y) \subseteq \{\, c_i : (c_i, t^{on}_i, t^{off}_i, s_i) \in E \,\}$$

⟪eqno:grounding⟫

Đầu ra thứ ba là câu trả lời cho một câu hỏi tự nhiên về lịch sử bản ghi, kèm bằng chứng dạng (mã bản ghi, khoảng thời gian).

Máy có thể kiểm tra được điều kiện ⟪eq:grounding⟫. Tuy nhiên, điều kiện này chỉ bảo đảm mô tả **khớp với danh sách sự kiện mà hệ thống dự đoán**, không bảo đảm khớp với âm thanh thật: nếu bước phát hiện sai thì mô tả cũng sai theo. Khóa luận luôn đo riêng hai mức đúng này.

## Bối cảnh ứng dụng tại Việt Nam

Tiếng ồn ở Việt Nam được quản lý theo **QCVN 26:2025/BNNMT**, thay cho QCVN 26:2010/BTNMT [@qcvn262025]. Quy chuẩn đặt giới hạn theo ba yếu tố: **loại nguồn** (cơ sở có thiết bị, loa, công trường đang thi công, giao thông đường bộ và đường sắt), **khung giờ** (ban ngày 06:00 đến 18:00, buổi tối 18:00 đến 22:00, ban đêm 22:00 đến 06:00) và **thời gian phát ra tiếng ồn**. Ví dụ, giới hạn đối với công trường ở khu vực A, B, C là 65, 60 và 50 dBA theo khung giờ; ngưỡng của cơ sở sản xuất, kinh doanh được nới thêm 15 dBA khi tiếng ồn kéo dài không quá 1 giờ ban ngày và giảm dần khi kéo dài hơn [@qcvn262025]. "Nguồn nào, lúc nào, kéo dài bao lâu" chính là những gì dòng thời gian sự kiện của hệ thống trả lời.

Quy chuẩn cũng cho thấy giới hạn của đề tài. Việc đo phải dùng **máy đo mức âm loại 1** đã kiểm định [@qcvn262025]. Hệ thống của nhóm xử lý tệp âm thanh thông thường và **không đo mức ồn dBA**, nên chỉ là công cụ **sàng lọc**: giúp chọn bản ghi và khoảng thời gian đáng chú ý để đo hoặc nghe lại, không phải bằng chứng vi phạm. Hệ thống chỉ gọi tên nguồn âm nghe được (ví dụ "có nhạc"), không kết luận loại cơ sở (ví dụ "có karaoke") hay hành vi vi phạm. ⟪tbl:qcvnmap⟫ nêu cách nhóm đề xuất ghép lớp âm thanh với hạng mục nguồn của quy chuẩn.

@@CAP:tbl:qcvnmap|Ánh xạ đề xuất từ lớp âm thanh sang hạng mục nguồn của QCVN 26:2025/BNNMT@@

@@COLWIDTHS:34,40,26@@

| Lớp của hệ thống | Hạng mục nguồn trong quy chuẩn | Vai trò |
|---|---|---|
| `workshop` | Công trường xây dựng, thiết bị máy móc | Nguồn có thể bị quản lý |
| `music` | Loa; cơ sở trong cùng tòa nhà | Nguồn có thể bị quản lý; chỉ nói "có nhạc" |
| `vehicle_pass_by`, `vehicle_idling`, `horn` | Phương tiện giao thông đường bộ | Nguồn có thể bị quản lý |
| `train` | Đường sắt | Nguồn có thể bị quản lý |
| Các lớp sinh vật (`birds`, `dog_barkings_and_howlings`, …) | Không phải nguồn bị quản lý | Tiếng ồn nền, cần loại khi chọn thời điểm đo |

@@NOTE:Nguồn: QCVN 26:2025/BNNMT, đọc trực tiếp bản gốc. Ánh xạ là đề xuất của nhóm, không phải phân loại của quy chuẩn.@@

Nhóm chưa đo hệ thống trên bản ghi thu tại Việt Nam. Hai bộ dữ liệu là dữ liệu công bố sẵn, nên nhóm không khẳng định chúng đại diện cho âm thanh đô thị Việt Nam. Để tiến gần bối cảnh này, Chương 6 báo thêm kết quả trên **19 lớp**, bỏ hai lớp ít gặp ở đô thị Việt Nam (`propeller_aircrafts` và `crows_seagulls_magpies`).

## Mục tiêu và câu hỏi nghiên cứu

Mục tiêu chung là dựng một quy trình tái lập được, đi từ dữ liệu công bố đến câu trả lời có bằng chứng. Cụ thể gồm bảy việc:

- \(1) chuẩn bị dữ liệu có nguồn gốc rõ và tập chia cố định;
- \(2) huấn luyện mô hình phân loại 22 lớp trên DataSEC;
- \(3) huấn luyện mô hình SED 21 lớp trên DataSED và tinh chỉnh biên sự kiện;
- \(4) đo hiệu quả của việc chuyển giao từ DataSEC sang DataSED;
- \(5) sinh mô tả có căn cứ và đo ảo giác;
- \(6) truy hồi kết hợp lọc điều kiện và tìm theo ngữ nghĩa;
- \(7) làm ứng dụng web minh họa từ đầu đến cuối.

Ba câu hỏi nghiên cứu (Research Question – RQ) được tóm tắt ở ⟪tbl:rq⟫.

@@CAP:tbl:rq|Ba câu hỏi nghiên cứu@@

| Mã | Câu hỏi | Cách trả lời |
|---|---|---|
| RQ1 | Huấn luyện thêm trên DataSEC có giúp SED tốt hơn so với chỉ dùng mô hình tiền huấn luyện AudioSet không? | So nhánh C (AudioSet rồi DataSEC) với nhánh B (chỉ AudioSet), nhiều lần chạy, có khoảng tin cậy |
| RQ2 | Buộc mô tả bám sát danh sách sự kiện thì giảm ảo giác bao nhiêu so với viết tự do? | So tỷ lệ ảo giác và bỏ sót giữa các cách sinh, trên cùng một kết quả SED |
| RQ3 | Truy hồi kết hợp (lọc điều kiện rồi xếp hạng theo ngữ nghĩa) so với chỉ lọc hoặc chỉ ngữ nghĩa thì thế nào? | So chỉ số xếp hạng nDCG@10 và độ đúng bộ lọc; mức liên quan tính từ nhãn gốc |

Với RQ1, nhóm so ba nhánh: nhánh A học từ đầu, nhánh B dùng trọng số tiền huấn luyện trên AudioSet [@kong2020panns], nhánh C dùng AudioSet rồi huấn luyện tiếp trên DataSEC. Phép so đúng là **C với B**; so C với A sẽ trộn tác dụng của tiền huấn luyện nói chung với tác dụng riêng của DataSEC.

## Phạm vi

Đề tài xử lý âm thanh môi trường ngoài trời theo lô, không theo thời gian thực. Phạm vi gồm SED 21 lớp trên DataSED, phân loại 22 lớp trên DataSEC, mô tả bằng tiếng Anh (để đánh giá) và tiếng Việt (cho giao diện), cùng truy vấn theo lớp, thời gian, thời lượng, độ tin cậy và quan hệ trước–sau.

Một số hướng bị loại có chủ ý vì dữ liệu không đủ cơ sở: nhận dạng lời nói hay người nói; suy ra tội phạm, ý định, tai nạn, tình huống khẩn cấp; chấm điểm mức nguy hiểm. Mô tả chỉ nói về *nguồn âm nghe được*, không nói về *tình huống*: "phát hiện tiếng kính vỡ lúc 5,4 s" là hợp lệ, còn "phát hiện đột nhập" thì không.

## Đóng góp

⟪tbl:contrib⟫ nêu sáu đóng góp, bằng chứng và mức khẳng định. Sau khi tra cứu văn liệu (Chương 2), nhóm thấy đã có công trình gần với C2, C3 và C4, nên báo cáo gọi chúng là **áp dụng và mở rộng** kỹ thuật đã có.

@@CAP:tbl:contrib|Sáu đóng góp, bằng chứng và giới hạn@@

@@COLWIDTHS:7,27,36,30@@

| Mã | Đóng góp | Bằng chứng | Giới hạn |
|---|---|---|---|
| C1 | Bộ sinh mô tả bám sát sự kiện, máy kiểm tra được | Trên tập kiểm tra, bộ sinh có ràng buộc không có ảo giác nguồn âm ở cả bốn hệ SED | Kết quả này có được nhờ cấu tạo của ngữ pháp; giao diện dùng mô tả theo mẫu |
| C2 | Bộ chỉ số đo mức bám sát của mô tả | Đo ảo giác, bỏ sót, thứ tự, từ cấm, có khoảng tin cậy | Đã có chỉ số gần (ECHO, TAC); mẫu đối chiếu với người đọc nhỏ |
| C3 | Đo chuyển giao có kiểm soát trùng lặp giữa hai bộ dữ liệu | Tìm ra ba nhóm trùng, loại 11 đoạn; RQ1 cho kết quả âm tính | Kiểm tra trùng giữa các bộ dữ liệu đã có; đây là áp dụng cho cặp DataSEC–DataSED |
| C4 | RAG trên dòng thời gian sự kiện, có điều kiện quan hệ giữa hai sự kiện | Bốn điều kiện thời gian viết bằng SQL; chế độ bổ sung cao hơn cả hai chế độ gốc ở bốn kho | Đã có hệ lưu sự kiện kết hợp RAG (LA-RAG); truy hồi kết hợp vẫn thấp hơn chỉ ngữ nghĩa ở nhóm câu hỏi quan hệ thời gian |
| C5 | Tinh chỉnh biên học được (LBR) sau bước phát hiện | Event-F1 micro trên tập kiểm tra 0,1806 lên 0,2965, hiệu +0,1159 [+0,0741; +0,1593] | Đổi lại PSDS-2 và F1 theo đoạn thấp hơn; chưa kiểm trên bộ dữ liệu khác |
| C6 | Giao thức đánh giá chống chọn theo tập kiểm tra | Chọn trên dự đoán ngoài mẫu; sổ ghi 42 lượt đánh giá SED trên tập kiểm tra; khóa dữ liệu bằng mã băm | Là quy trình của dự án, không phải phương pháp mới |

## Kết quả chính

Với RQ1, huấn luyện thêm trên DataSEC không tạo khác biệt đo được: khoảng tin cậy 95% của hiệu chứa 0. Với SED, bước LBR nâng event-F1 micro trên tập kiểm tra từ 0,1806 lên 0,2965. Với RQ2, bộ sinh có ràng buộc không có ảo giác nguồn âm so với danh sách sự kiện, nhưng khi so với nhãn gốc thì lỗi do SED vẫn còn. Với RQ3, truy hồi kết hợp thấp hơn truy hồi chỉ theo ngữ nghĩa ở ba trên bốn kho, còn chế độ bổ sung cao hơn cả hai ở cả bốn kho. Ứng dụng web chạy trên CPU, trung vị 3,89 giây cho mỗi bản ghi.

Các kết quả ghép thành một kết luận chung: **trong hệ thống này, độ đúng của mô tả và câu trả lời phụ thuộc chủ yếu vào bước phát hiện sự kiện. Bộ sinh có ràng buộc không tự thêm nguồn âm ngoài danh sách sự kiện, và bộ lọc cứng chỉ trả bản ghi có sự kiện đã lưu thỏa điều kiện. Vì vậy cải tiến có tác dụng nằm ở SED và ở độ phủ sự kiện khi truy hồi.** Hai bộ phận khác vẫn có lỗi riêng và được đo ở Chương 6: bộ phân tích câu hỏi và bộ đo ảo giác.

## Bố cục báo cáo

Chương 2 trình bày kiến thức nền. Chương 3 mô tả dữ liệu và cách kiểm soát trùng lặp. Chương 4 trình bày phương pháp. Chương 5 mô tả hệ thống đã xây dựng. Chương 6 báo cáo kết quả, kể cả kết quả âm tính. Chương 7 nêu kết luận, hạn chế và hướng phát triển. Chi tiết quy trình tái lập và nhật ký thí nghiệm nằm ở Phụ lục B.
