# PHƯƠNG PHÁP

Chương này trình bày phương pháp theo đường đi của dữ liệu: từ tệp âm thanh đến sự kiện, từ sự kiện đến mô tả, rồi đến kho sự kiện và câu trả lời. Cuối chương là cách đánh giá.

## Luồng xử lý tổng thể

⟪fig:dataflow⟫ là luồng xử lý của hệ thống cuối. Tệp âm thanh được đổi về đơn kênh 16 kHz rồi cắt thành các cửa sổ 10 s, trượt mỗi bước 5 s. Mô hình SED cho xác suất của 21 lớp tại từng khung 10 ms; xác suất ở các cửa sổ chồng nhau được lấy trung bình theo trọng số tam giác. Bước cSEBB tách ma trận xác suất thành các hộp sự kiện, rồi LBR dời biên và chấm lại từng hộp. Kết quả là dòng thời gian sự kiện. Từ dòng thời gian, hệ thống sinh mô tả tiếng Anh và tiếng Việt, ghép thành một tài liệu truy hồi, nhúng tài liệu thành vector bằng BGE-M3 và lưu tất cả vào kho PostgreSQL.

@@DIAGRAM:dataflow@@

@@CAP:fig:dataflow|Luồng xử lý dữ liệu của hệ thống cuối, từ tệp âm thanh tới kho sự kiện@@

@@NOTE:Nguồn: thông số đọc từ cấu hình của hệ đang phục vụ và từ mã kiểm tra tệp tải lên.@@

Một nguyên tắc xuyên suốt: **mọi tham số của bước ghép sự kiện (ngưỡng, cSEBB, LBR) được chọn ngoại tuyến rồi khóa lại**; khi phục vụ, hệ thống chỉ nạp tham số đã khóa. Nhờ vậy có thể đổi điểm vận hành mà không cần huấn luyện lại mô hình.

Đề tài so sánh nhiều thế hệ mô hình SED. Để dễ theo dõi, báo cáo chỉ dùng bốn tên cho các hệ chính (⟪tbl:systems⟫); mã nội bộ tương ứng nằm ở Phụ lục B.

@@CAP:tbl:systems|Bốn hệ SED chính được so sánh trong báo cáo@@

@@COLWIDTHS:22,78@@

| Tên | Là gì |
|---|---|
| Hệ mốc | Tổ hợp 3 mô hình Frame-MobileNet, ghép sự kiện bằng cSEBB; được khóa ở vòng chọn trước, giữ làm mốc so sánh |
| Hệ cơ sở | Tổ hợp 5 mô hình Frame-MobileNet (mỗi phần dữ liệu một mô hình), suy luận cửa sổ chồng nhau, cSEBB; là hệ SED cuối cùng trước LBR |
| LBR chính | Hệ cơ sở cộng LBR, cấu hình cho F1 theo sự kiện cao nhất; là kết quả chính của báo cáo |
| LBR ứng dụng | Hệ cơ sở cộng LBR, cấu hình ưu tiên độ phủ sự kiện (ít bỏ sót); dùng trong ứng dụng minh họa |

## Mô hình phân loại trên DataSEC

Mô hình phân loại có hai vai trò: là bước giữa của nhánh C trong Câu hỏi nghiên cứu 1, và đáp ứng mục tiêu (2) của khóa luận (phân loại 22 lớp trên DataSEC). Mô hình gồm bộ mã hóa CNN14 khởi tạo từ trọng số AudioSet [@kong2020panns] và hai đầu ra: một cho 22 lớp cấp trên, một cho 28 lớp con. Hàm mất mát có thêm một số hạng phạt việc đoán lớp con không thuộc lớp cấp trên đã đoán; hệ số của số hạng này (0,5) được chọn trên tập phát triển theo luật đặt trước. Vì `voices` và `music` chiếm 57,5% dữ liệu, huấn luyện dùng lấy mẫu cân bằng lớp.

## Mô hình phát hiện sự kiện (SED)

**Hàm mất mát.** Mô hình SED dự đoán xác suất cho 21 lớp tại từng khung trên cửa sổ 10 s. Hàm mất mát là entropy chéo nhị phân (*binary cross-entropy*), có trọng số cho khung có sự kiện để bù việc thời gian "có sự kiện" ít hơn nhiều so với thời gian "không có sự kiện".

**SED v1 và ba nhánh của Câu hỏi nghiên cứu 1.** Nhánh A dùng một mạng CRNN nhỏ học từ đầu. Nhánh B và C dùng CNN14: B khởi tạo từ AudioSet, C khởi tạo từ bộ mã hóa của mô hình phân loại DataSEC. Ba nhánh dùng cùng tập chia, cùng số vòng huấn luyện (*epoch*) và cùng cách cắt cửa sổ. Về sau nhóm phát hiện CNN14 nén trục thời gian 64 lần, nên mỗi quyết định ứng với một khối khoảng 0,64 s; riêng giới hạn này đã chặn F1 theo sự kiện ở 0,6294 kể cả khi nhận dạng hoàn hảo (Chương 6).

**SED v2.** Thế hệ thứ hai sửa các nguyên nhân đã đo được thay vì dò siêu tham số: chỉ nén thời gian 8 lần (80 ms mỗi khung); thêm BiGRU hai lớp; huấn luyện 30 vòng; dùng tăng cường dữ liệu gồm cắt cửa sổ ngẫu nhiên, mixup [@zhang2018mixup] và FilterAugment [@nam2022filteraugment].

**Bộ mã hóa tiền huấn luyện theo khung.** Dựa trên kết quả "đóng băng gần bằng huấn luyện tiếp toàn bộ" [@schmid2025effective], nhóm thử hai bộ mã hóa có độ phân giải 40 ms: BEATs [@chen2022beats] đóng băng, chỉ huấn luyện phần đầu ra; và Frame-MobileNet [@morocutti2025tradeoffs] khoảng 3 triệu tham số, huấn luyện tiếp toàn bộ. Trọng số tiền huấn luyện của cả hai lấy từ kho mã công bố kèm bài của Schmid và cộng sự. Frame-MobileNet nhận sóng âm 16 kHz và tự tính phổ log-mel 128 dải, 100 khung/s bên trong mô hình; các đặc trưng 64 dải mel trích sẵn ở Chương 3 chỉ dùng cho SED v1 và v2. Frame-MobileNet là bộ mã hóa của hệ mốc và hệ cơ sở.

**Tổ hợp mô hình.** Huấn luyện SED không cho kết quả giống hệt nhau giữa các lần chạy, kể cả cùng hạt giống ngẫu nhiên (*seed*). Vì vậy mỗi cấu hình được huấn luyện nhiều lần với các hạt giống khác nhau, và ứng viên là trung bình xác suất của các mô hình (tổ hợp mô hình, *ensemble*).

**Cách chọn hệ thống.** Ban đầu nhóm chọn ứng viên bằng kiểm chứng chéo 5 phần trên tập phát triển (134 bản ghi). Vòng chọn này khóa **hệ mốc**. Sau đó nhóm thấy cách chọn này quá nhiễu: ba ứng viên vượt qua vòng sàng lọc trên tập phát triển đều thua khi đo lại trên dữ liệu lớn hơn. Nhóm vì vậy chuyển sang chọn trên **dự đoán ngoài mẫu** của 564 bản ghi có nhãn thuộc tập huấn luyện và tập phát triển: chia 5 phần, mỗi bản ghi được dự đoán bởi mô hình không được học trên nó, và hai ứng viên được so bằng bootstrap ghép cặp. Hệ được chọn theo cách này là **hệ cơ sở**: 5 mô hình Frame-MobileNet (mỗi phần một mô hình), bỏ khỏi tập huấn luyện các bản ghi thiếu nhãn, suy luận cửa sổ chồng nhau và ghép sự kiện bằng cSEBB. Bốn hướng thử thêm sau đó (thêm lần huấn luyện, chưng cất tri thức, cửa sổ 20 s, tăng cường âm lượng và dải tần) đều không vượt hệ cơ sở.

## Tinh chỉnh biên học được (LBR)

Phân tích lỗi trên dự đoán ngoài mẫu của hệ cơ sở (⟪fig:fnbreakdown⟫) cho thấy hệ chỉ khớp đúng 592 trong 3.294 sự kiện tham chiếu. Trong 2.702 sự kiện bị bỏ sót, 1.477 không có hộp dự đoán cùng lớp nào chồng lên. Nhưng 789 trong số đó (53%) có xác suất lớn nhất từ 0,9 trở lên: mô hình đã "nghe thấy", chỉ là hộp bị loại ở bước ghép. Thêm 872 sự kiện có hộp cùng lớp nhưng lệch biên, phần lớn ở biên đầu (656). Biên đầu thường bị đoán sớm (⟪fig:onsetbias⟫): với các lớp kéo dài như `train` và `jet_aircrafts`, độ lệch trung vị khoảng −1,5 s. Như vậy nút thắt nằm ở biên hộp sau bước ghép, không phải ở khả năng nhận dạng.

![](report/gon_figures/r05_fn_breakdown.png){width=15cm}

@@CAP:fig:fnbreakdown|Phân loại 2.702 sự kiện bị hệ cơ sở bỏ sót trên dự đoán ngoài mẫu, và xác suất lớn nhất của mô hình trong các sự kiện không có hộp cùng lớp@@

@@NOTE:Nguồn: lbr_diagnosis_20261109.json (564 bản ghi của tập huấn luyện và tập phát triển; không dùng tập kiểm tra).@@

Độ lệch này có hướng và khác nhau theo lớp: lớp ngắn như `glass_breaking` hay `horn` nằm trong dung sai, còn lớp kéo dài bị đoán sớm rõ rệt. Một độ lệch có hệ thống như vậy có thể học để sửa mà không cần huấn luyện lại mô hình SED, và đó là ý tưởng của LBR.

![](report/gon_figures/c11_onset_bias.png){width=15.5cm}

@@CAP:fig:onsetbias|Trung vị độ lệch thời điểm bắt đầu theo lớp của hệ cơ sở trên dự đoán ngoài mẫu; cột đỏ là lớp lệch ra ngoài dung sai 0,2 s@@

@@NOTE:Nguồn: lbr_diagnosis_20261109.json; tính trên các sự kiện khớp 1–1 cùng lớp.@@

LBR là bước hậu xử lý gồm hai mô hình cây tăng cường gradient, học trên dự đoán ngoài mẫu (⟪fig:lbr⟫). **Bộ tinh chỉnh** dự đoán độ dời của thời điểm bắt đầu và kết thúc cho từng hộp. **Bộ chấm lại** nhận đặc trưng của hộp cùng độ dời vừa dự đoán, rồi ước lượng xác suất hộp đó đúng. Hộp được giữ nếu điểm vượt ngưỡng. Cả hai được học bằng học chéo lồng nhau, nên không mô hình nào được áp lên phần dữ liệu nó đã học.

@@DIAGRAM:lbr@@

@@CAP:fig:lbr|Hai bộ học của LBR và cách học chéo lồng nhau@@

@@NOTE:Nguồn: mã bước LBR trong ml/postprocessing.@@

LBR có hai cấu hình, khác nhau ở cách chọn ngưỡng. **LBR chính** chọn ngưỡng cho F1 theo sự kiện cao nhất; đây là kết quả chính của báo cáo. **LBR ứng dụng** chọn ngưỡng cho độ phủ sự kiện cao nhất với độ chính xác theo giao nhau không dưới 0,6 (mục 2.2.3), tức ưu tiên không bỏ sót sự kiện; cấu hình này dùng cho ứng dụng minh họa và được khóa trước khi đo trên tập kiểm tra. Với bài toán giám sát, câu hỏi "sự kiện có được phát hiện không" nhiều khi quan trọng hơn việc khớp biên chặt, nên Chương 6 báo cả hai chỉ số theo giao nhau.

## Từ xác suất đến sự kiện trong hệ thống

**Ngưỡng.** Làm mượt xác suất bằng lọc trung vị, so với ngưỡng $\theta$, nối khoảng trống ngắn và bỏ sự kiện quá ngắn. Hai giới hạn độ dài suy từ tập **huấn luyện**. Ngưỡng riêng cho từng lớp bị quá khớp tập phát triển (Chương 6), nên nhóm dùng một ngưỡng chung, chọn bằng kiểm chứng chéo.

**cSEBB.** Nhóm tự cài đặt cSEBB theo bài báo [@ebbers2024sound]. Ý chính: so xác suất trung bình ngay trước và ngay sau mỗi thời điểm; chỗ tăng mạnh nhất mở sự kiện, chỗ giảm mạnh nhất đóng sự kiện; ngưỡng chỉ quyết định giữ hay bỏ sự kiện, không dời biên.

**Suy luận cửa sổ chồng nhau.** Cửa sổ 10 s không chồng nhau làm các sự kiện ở mép cửa sổ bị cắt. Hệ cơ sở trượt cửa sổ mỗi 5 s và lấy trung bình xác suất theo trọng số tam giác, để khung gần mép có trọng số thấp hơn khung ở giữa.

## Sinh mô tả bám sát sự kiện

**Ba ràng buộc.** Bộ sinh mô tả chỉ nhận danh sách sự kiện, không nhận âm thanh hay thông tin bối cảnh. Mỗi mô tả phải thỏa ba ràng buộc, đều có kiểm thử tự động:

- **G1:** mọi nguồn âm được nhắc đều thuộc danh sách sự kiện.
- **G2:** mỗi lần nhắc đều gắn với một sự kiện làm bằng chứng.
- **G3:** không có từ về nguyên nhân, ý định, bối cảnh hay mức nguy hiểm, như *emergency*, *crime*, *intruder*.

Danh sách rỗng được mô tả là "không phát hiện sự kiện thuộc các lớp mục tiêu", không phải "bản ghi im lặng".

**Bốn cách sinh.** Câu hỏi nghiên cứu 2 so bốn cách sinh trên **cùng một** danh sách sự kiện, lặp lại cho cả bốn hệ SED:

- **Theo mẫu:** câu cố định điền từ danh sách sự kiện; bám sát theo thiết kế, dùng để kiểm tra bộ đo.
- **Tự do:** mô hình ngôn ngữ Qwen3.5-9B chạy trên máy bằng llama.cpp, viết không ràng buộc.
- **Ràng buộc:** cùng mô hình và lời nhắc, nhưng bị giới hạn bằng ngữ pháp (Chương 2). Ngữ pháp chỉ cho phép một câu liệt kê một phần các sự kiện theo thứ tự thời gian, với tên nguồn âm lấy từ từ điển và thời điểm lấy đúng từ sự kiện. Mô hình chỉ còn chọn nhắc sự kiện nào và dừng ở đâu.
- **Ràng buộc + phủ:** như trên, nhưng bắt buộc nhắc sự kiện đầu tiên của mỗi lớp, nên không bỏ sót lớp.

Cần đọc Câu hỏi nghiên cứu 2 đúng mức. Với ngữ pháp như trên, việc hai cách có ràng buộc không có ảo giác là **hệ quả của cấu tạo**. Thông tin thật của câu hỏi này nằm ở *cái giá* của ràng buộc (bỏ sót) và ở *mức lệch* của cách viết tự do. Ngoài ra, câu của cách ràng buộc gần như câu theo mẫu. Vì vậy **ứng dụng dùng mô tả theo mẫu, không dùng mô hình ngôn ngữ để viết mô tả**: mô tả theo mẫu không có lỗi đo được và không tốn tính toán. Trong hệ thống chạy thật, mô hình ngôn ngữ chỉ dùng để phân tích câu hỏi.

**Mô tả theo lớp.** Mô tả theo mẫu viết một mệnh đề cho mỗi sự kiện, nên với danh sách dày của LBR ứng dụng câu rất dài. Ứng dụng dùng một biến thể: mỗi lớp một dòng, lớp lặp lại được đếm số lần, ví dụ "Phát hiện: tiếng chim, 2 lần, 0,0–20,0 giây.". Nếu sự kiện chắc chắn nhất của lớp vẫn có điểm dưới một ngưỡng, dòng đó đổi nhãn thành "Có thể có (độ tin cậy thấp)". Biến thể này vẫn thỏa G1–G3. Mô tả tiếng Việt dùng từ điển tiếng Việt riêng và giữ nguyên dấu khi so khớp, vì bỏ dấu có thể khiến bộ kiểm G3 khớp nhầm (ví dụ "tới phạm vi" thành "tội phạm").

⟪fig:timeline⟫ đặt cạnh nhau sự kiện từ nhãn gốc và sự kiện do hệ mốc dự đoán trên một bản ghi của tập phát triển. Mô tả sinh từ dự đoán là: *"The sound of jet aircrafts can be heard from 0.3 to 10.0 seconds, followed by the sound of birds from 10.0 to 29.2 seconds and the sound of birds from 90.0 to 108.8 seconds."* Mọi nguồn âm và mốc thời gian trong câu đều có sự kiện dự đoán tương ứng, nên câu hợp lệ theo G1–G3. Nhưng so với nhãn gốc, câu đặt tiếng máy bay phản lực sai chỗ và bỏ qua bốn sự kiện. Đây là khoảng cách giữa "bám sát dự đoán" và "đúng với âm thanh".

![](report/figures/m05_dev_timeline.png){width=13cm}

@@CAP:fig:timeline|Sự kiện theo nhãn gốc và theo dự đoán của hệ mốc trên bản ghi S-0009 (tập phát triển)@@

@@NOTE:Nguồn: tệp mô tả của hệ mốc trên tập phát triển.@@

## Truy hồi và trả lời có bằng chứng

**Kho sự kiện.** Nhóm dùng PostgreSQL 16 với phần mở rộng pgvector, để bộ lọc, điều kiện thời gian và xếp hạng vector nằm trong **một** câu truy vấn SQL. Mỗi bản ghi có một tài liệu truy hồi ghép mô tả tiếng Anh, tiếng Việt và một bản tóm tắt sự kiện (lớp, thời điểm, số sự kiện). Tài liệu được nhúng bằng BGE-M3 thành vector 1024 chiều [@chen2024m3]. Mỗi hệ SED có một kho riêng, dùng chung bộ 100 câu truy vấn, nên so được giữa các hệ.

**Bốn chế độ truy hồi.**

- **Chỉ lọc:** chỉ trả bản ghi thỏa mọi điều kiện của câu truy vấn.
- **Chỉ ngữ nghĩa:** chỉ xếp hạng theo độ tương đồng vector, không lọc.
- **Kết hợp:** lọc trước, rồi xếp hạng theo vector trong tập đã lọc.
- **Bổ sung:** giữ nguyên danh sách của chế độ kết hợp, rồi lấp các chỗ còn trống (cho đủ 10 kết quả) bằng kết quả của chế độ chỉ ngữ nghĩa. Kết quả lấp thêm được gắn nhãn "gần khớp, không thỏa bộ lọc" và không được dùng làm bằng chứng.

Chế độ bổ sung xuất phát từ phân tích lỗi của ba chế độ đầu trên tập kiểm tra (Chương 6). Vì vậy định nghĩa của nó được ghi lại trước, kiểm trên tập phát triển, rồi mới đo trên tập kiểm tra đúng một lần.

Bộ lọc gồm tập lớp phải có mặt, ràng buộc thời lượng và một điều kiện thời gian giữa hai lớp $a$, $b$ trong cùng bản ghi (⟪tbl:predicates⟫). Mỗi điều kiện được viết một lần bằng SQL (để truy hồi) và một lần bằng Python (để tính mức liên quan từ nhãn gốc); một kiểm thử bảo đảm hai cách viết cho cùng kết quả.

@@CAP:tbl:predicates|Bốn điều kiện thời gian giữa sự kiện a và b@@

| Điều kiện | Ý nghĩa | Ví dụ câu hỏi |
|---|---|---|
| before | a kết thúc trước khi b bắt đầu | Tiếng kính vỡ trước tiếng còi |
| after | a bắt đầu sau khi b kết thúc | Tiếng còi sau tiếng kính vỡ |
| overlaps | a và b chồng nhau | Tiếng nói chồng với tiếng máy |
| within | a nằm trọn trong b | Tiếng chim trong lúc có tiếng công trường |

@@NOTE:Nguồn: mã điều kiện thời gian của bộ truy hồi.@@

**Bộ phân tích câu hỏi.** Câu hỏi tiếng Việt hoặc tiếng Anh được chuyển thành bộ lọc dạng JSON (JavaScript Object Notation) bằng mô hình ngôn ngữ chạy trên máy, bị ràng buộc bởi một lược đồ sinh từ 21 lớp và bốn điều kiện. Lược đồ bảo đảm *hình thức* (không thể tạo ra lớp hay điều kiện không tồn tại), nhưng không bảo đảm *nghĩa* (vẫn có thể đảo vai trò a và b). Vì vậy độ đúng của bộ phân tích được đo riêng (Chương 6), và trên giao diện bộ lọc hiện thành thẻ để người dùng sửa trước khi truy vấn.

**Câu trả lời có bằng chứng** được sinh theo mẫu cố định từ các bản ghi đã truy hồi. Mỗi câu nhắc lại một sự kiện bằng chứng (lớp, khoảng thời gian). Không có kết quả thì trả danh sách rỗng kèm bộ lọc đã áp, không suy đoán. Một bộ kiểm độc lập đếm số khẳng định không có bằng chứng tương ứng.

## Cách đánh giá

**Chọn trên tập phát triển, đo trên tập kiểm tra một lần.** Tập huấn luyện dùng để học mô hình. Tập phát triển (và dự đoán ngoài mẫu) dùng để chọn ngưỡng, bản lưu trọng số (*checkpoint*) và cấu hình. Tập kiểm tra chỉ dùng để đo cấu hình đã khóa, và **mỗi cấu hình chỉ được đo trên tập kiểm tra một lần**. Lựa chọn được lưu vào git trước khi sinh dự đoán cho tập kiểm tra, mọi lần dùng tập kiểm tra được ghi vào một sổ, và không cấu hình nào được chọn lại sau khi xem kết quả kiểm tra.

**Bộ câu truy vấn.** Bộ 100 câu truy vấn gồm bốn nhóm (21 câu một lớp, 27 câu nhiều lớp, 30 câu quan hệ thời gian, 22 câu thời lượng), được chọn theo nhãn của tập huấn luyện trước khi xem kết quả. Mỗi câu có bộ lọc chuẩn viết tay và câu hỏi tương ứng bằng tiếng Anh và tiếng Việt. Trên tập kiểm tra có 97/100 câu có ít nhất một bản ghi liên quan.

**Chỉ số.** Mọi chỉ số đã được định nghĩa ở mục 2.2. ⟪tbl:evalmap⟫ nối mỗi câu hỏi nghiên cứu và mục tiêu với chỉ số chính và bảng kết quả tương ứng ở Chương 6.

@@CAP:tbl:evalmap|Câu hỏi nghiên cứu, mục tiêu, chỉ số chính và nơi báo kết quả@@

@@COLWIDTHS:30,44,26@@

| Câu hỏi hoặc mục tiêu | Chỉ số chính (mục định nghĩa) | Kết quả |
|---|---|---|
| Mục tiêu (2): phân loại trên DataSEC | Macro-F1, tỷ lệ phân loại đúng, tỷ lệ nhất quán, ECE (2.2.4) | ⟪tbl:classifier⟫ |
| Câu hỏi nghiên cứu 1: chuyển giao từ DataSEC | F1 theo sự kiện micro; khoảng tin cậy bootstrap; kiểm định t Welch (2.2.2, 2.2.8) | ⟪tbl:rq1⟫ |
| Mục tiêu (3): SED và LBR | F1 theo sự kiện micro và macro; F1 theo đoạn; độ phủ sự kiện; PSDS-1 và PSDS-2 (2.2.1 đến 2.2.3) | ⟪tbl:sedfinal⟫, ⟪tbl:calibration⟫ |
| Câu hỏi nghiên cứu 2: mô tả bám sát sự kiện | Ảo giác, bỏ sót, thêm bối cảnh, gọi tên quá cụ thể, từ cấm (2.2.5) | ⟪tbl:rq2final⟫, ⟪tbl:captiontiers⟫ |
| Câu hỏi nghiên cứu 3: truy hồi | nDCG@10, độ đúng bộ lọc, khẳng định thiếu bằng chứng (2.2.6) | ⟪tbl:rq3final⟫, ⟪tbl:rq3paired⟫ |
| Bộ phân tích câu hỏi | Hợp lược đồ, đúng hoàn toàn, đúng điều kiện thời gian (2.2.7) | ⟪tbl:parser⟫ |
| Mục tiêu (7): ứng dụng | Độ trễ, hệ số thời gian thực (2.2.9) | ⟪tbl:latency⟫ |

@@NOTE:Nguồn: định nghĩa chỉ số ở mục 2.2; bảng kết quả ở Chương 5 và Chương 6.@@
