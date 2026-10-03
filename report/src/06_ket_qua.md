# KẾT QUẢ HIỆN CÓ VÀ THẢO LUẬN

Chương này báo cáo các kết quả đã có tại mốc giữa kỳ (03/10/2026). Mọi bảng định lượng được sinh bằng script từ artifact đã khóa và ghi tệp nguồn ngay dưới bảng. Khi đọc các con số, cần lưu ý bốn quy ước.

- **Event-F1** luôn là F1 theo sự kiện với onset collar 0,2 s và dung sai offset $\max(0{,}2\text{ s};\ 0{,}2 L_{ref})$, tính bằng `sed_eval`. Macro và micro được ghi rõ ở từng chỗ.
- **Tập đánh giá** là `all` (142 bản ghi test) hoặc `annotated` (139 bản ghi test có nhãn đa âm, Mục 3.4.1).
- **Khoảng tin cậy** 95% được bootstrap theo bản ghi (Mục 4.7.3).
- Số trên **dev** dùng để chọn cấu hình. Số trên **test** chỉ dùng để đo cấu hình đã chọn và không bao giờ được dùng để chọn lại.

## Mô hình phân loại DataSEC

Mô hình phân loại phân cấp đạt macro-F1 0,8466 trên 22 lớp gộp của tập test DataSEC (⟪tbl:classifier⟫). Ở cấp lớp con, macro-F1 trên cả 28 nút là 0,6266, nhưng con số này bị kéo bởi các nút có rất ít mẫu test. Chỉ tính 5 nút có ít nhất 10 mẫu test, macro-F1 là 0,8453. Theo quy ước đánh giá, các nút ít mẫu chỉ được báo bằng số tuyệt đối (Phụ lục C); chẳng hạn `vacuum_cleaner` đúng 0/4 và `air_compressor` đúng 0/5. Tỷ lệ nhất quán cha–con là 0,9526: trong 95% trường hợp, lớp con được dự đoán thuộc đúng gia đình của lớp gộp được dự đoán. Các lớp gộp yếu nhất là `vehicle_idling` (F1 0,6154) và `vehicle_pass_by` (0,6538), là hai lớp có nội dung âm học gần nhau.

@@CAP:tbl:classifier|Kết quả mô hình phân loại DataSEC trên tập test@@

@@INCLUDE:report/tables/m01_classifier.md@@

Hiệu chuẩn xác suất cho kết quả âm tính. Nhiệt độ $T = 1{,}5681$ chọn trên dev làm sai số hiệu chuẩn kỳ vọng (Expected Calibration Error – ECE) trên test **tăng** từ 0,0332 lên 0,0564. Kết quả được báo đúng như vậy, không chỉnh $T$ theo test. Mô hình phân loại tái lập trùng từng bit khi huấn luyện lại cùng seed; ngược lại, mô hình SED không có tính chất này (Mục 6.7).

## RQ1 — Tiền huấn luyện thêm trên DataSEC

### RQ1 với công thức v1

Câu trả lời cho RQ1 dựa trên nhiều run, vì huấn luyện SED không tất định (ADR-0021). Với công thức v1 và tập test `all`, phân tích chính dùng 7 run có cây làm việc sạch: 3 run nhánh B và 4 run nhánh C (⟪tbl:rq1⟫). Event-F1 micro trung bình của B là 0,0610 và của C là 0,0539. Hiệu C − B bootstrap ghép cặp theo bản ghi là −0,0071 [−0,0164; +0,0021], Welch p = 0,2336. PSDS cũng không phân biệt được: PSDS-1 0,2902 so với 0,2892 (p = 0,913), PSDS-2 0,6498 so với 0,6591 (p = 0,181). Phân tích độ nhạy với cả 10 run (5/5) cho cùng kết luận, không metric nào có p < 0,05. Ngược lại, tiền huấn luyện nói chung giúp rõ: trên các run chính thức, nhánh A học từ đầu chỉ đạt event-F1 0,0360 và PSDS-2 0,4514, so với 0,0621 và 0,6456 của nhánh B.

@@CAP:tbl:rq1|Kết quả RQ1 (công thức v1, test all) và RQ1-v2 (công thức v2, test annotated)@@

@@INCLUDE:docs/thesis/tables/03_rq1.md@@

### RQ1 với công thức v2

Để kiểm tra kết quả âm tính có phải do kiến trúc v1 quá thô hay không, đề tài lặp lại phép so sánh với công thức v2 (RQ1-v2): 3 run B-v2 so với 3 run C-v2. Phân tích này được ghi trước và chỉ mở test sau khi vòng chọn hệ thống cuối đã commit (ADR-0031 §2). Trên test `annotated`, event-F1 macro của B-v2 và C-v2 là 0,1221 và 0,1147, micro là 0,1324 và 0,1294. Hiệu C − B về micro là −0,0029 [−0,0254; +0,0199], Welch p = 0,6965 (macro p = 0,4220). Riêng PSDS-2 tăng +0,0279 với p = 0,0193, tức kết luận phụ thuộc vào metric.

**Kết luận RQ1:** với cả hai công thức, đề tài **không** có bằng chứng rằng tiền huấn luyện thêm trên DataSEC cải thiện event-F1 so với chỉ tiền huấn luyện trên AudioSet. Kết luận này không có nghĩa là DataSEC "vô ích" nói chung: PSDS-2 của RQ1-v2 tăng có ý nghĩa thống kê đơn lẻ, và chưa có hiệu chỉnh cho phép so sánh bội. Đây là kết quả âm tính hợp lệ, được giữ nguyên trong báo cáo; trọng tâm đóng góp vì vậy chuyển sang C1, C2 và C4 (ADR-0021).

## Tiến triển của mô hình SED

### Chẩn đoán lỗi và giới hạn trên

Sau RQ1, event-F1 tuyệt đối của v1 còn rất thấp, nên đề tài chẩn đoán nguyên nhân trên dev trước khi cải tiến (⟪tbl:ceilings⟫). Phép đo trần độ phân giải cho thấy một mô hình nhận dạng hoàn hảo, nếu ra quyết định theo khối 0,64 s như CNN14 nén /64, chỉ đạt event-F1 0,6294; ở khối 1,28 s, con số này là 0,3032. Trần do nhãn, đo trên 8 cặp bản ghi chú giải hai lần, là 0,5785. Với hệ v1 trên dev, event-F1 chỉ xét onset là 0,2325, chỉ xét offset là 0,4975, và F1 theo đoạn 1 s là 0,6542. Trong 886 sự kiện tham chiếu, 112 khớp collar, 417 có chồng lấp đúng lớp nhưng lệch biên, và 357 bị bỏ sót. Lỗi chủ yếu vì thế nằm ở **biên sự kiện** và ở **bỏ sót**, chứ không nằm ở nhận dạng lớp. Nới onset collar từ 0,2 s lên 1 s làm event-F1 của nhánh B tăng khoảng ba lần (0,062 lên 0,185) cũng phù hợp với chẩn đoán này.

@@CAP:tbl:ceilings|Chẩn đoán trần và phân rã lỗi SED trên tập dev@@

@@INCLUDE:report/tables/m03_sed_ceilings.md@@

Bảng này là số dev in-sample: hậu xử lý được chọn trên chính dev. Hai tệp đo được sinh khi cây làm việc có thay đổi chưa commit (`git.dirty = true`). Vì vậy, bảng chỉ dùng cho chẩn đoán, không dùng như kết quả đánh giá. Một giả thuyết ban đầu cho rằng "posterior bão hòa làm onset trễ"; đề tài đã đo và bác bỏ giả thuyết này. Trung vị posterior của khung âm chỉ là 0,008, và sai số onset phân bố đối xứng (khoảng tứ phân vị −0,39 đến +0,51 s; chỉ 30,2% nằm trong ±0,2 s). Chẩn đoán đúng là biên **tản rộng và đối xứng**.

### SED v2 và các ablation

Ba seed của SED v2 đạt event-F1 micro theo kiểm chứng chéo trên dev 0,1900, 0,2096 và 0,2169, so với 0,1538 của ensemble v1 (⟪tbl:ablation⟫). Ablation bỏ-từng-phần cho thấy chỉ độ phân giải thời gian có tác động phân biệt được: quay về nén /64 làm event-F1 giảm 0,0840, gấp 1,6 lần độ lệch chuẩn giữa các fold. Ngược lại, trần trọng số dương 50 thay cho 10 (−0,0126) và bỏ tăng cường dữ liệu (+0,0068) đều nằm trong nhiễu. Mỗi biến thể chỉ có một seed, nên "không phân biệt được" không đồng nghĩa với "không có tác dụng". Đáng chú ý là average precision theo khung gần như không đổi khi bỏ độ phân giải (0,667 so với 0,688), trong khi event-F1 giảm mạnh. Điều này cho thấy metric theo khung không phản ánh được chất lượng định vị sự kiện.

@@CAP:tbl:ablation|Ablation SED v2 trên kiểm chứng chéo dev@@

@@INCLUDE:docs/thesis/tables/05_sed_v2_ablation.md@@

Theo luật chọn ghi trước, ensemble 3 seed của v2 (ứng viên c, kiểm chứng chéo 0,2129 ± 0,0622) được commit trước khi mở test. Ensemble này được chọn theo luật, nhưng **không** được gọi là tốt hơn run đơn, vì chênh lệch 0,023 nhỏ hơn độ lệch chuẩn giữa các fold. Trên test `all`, ensemble v2 đạt event-F1 micro 0,1476 [0,1088; 0,1866] và macro 0,1369, so với 0,0941 và 0,0917 của v1. Hiệu ghép cặp v2 − v1 là +0,0536 [+0,0261; +0,0853], khoảng tin cậy không chứa 0. Tuy vậy, **PSDS không tăng**: PSDS-1 0,3447 so với 0,3489, PSDS-2 0,6744 so với 0,6987. Lợi ích của v2 vì thế nằm ở điểm vận hành đã chọn chứ không phải trên toàn dải ngưỡng; nguyên nhân chưa được giải thích và được đưa vào việc còn lại (Mục 7.4).

Các ablation hậu xử lý trên ba nhánh v1 dẫn tới lựa chọn ngưỡng chung. Khi chuyển từ dev sang test, event-F1 với ngưỡng riêng từng lớp giảm 48%, 39% và 41% (A, B, C), trong khi với ngưỡng chung chỉ giảm 15%, 4% và 2%. Điều này cho thấy ngưỡng riêng từng lớp quá khớp dev một cách có hệ thống. Lọc trung vị không có tác động rõ (Δ +0,0063, +0,0026, −0,0014). Phân vị 25 cho $g^{max}$ được chọn lại trên dev bằng kiểm chứng chéo ở cả 5 ứng viên của vòng tối ưu v1.

### Vòng chọn cuối S13 và kết quả test

Vòng chọn cuối gồm 11 ứng viên đã ghi trước (⟪tbl:codes⟫). Các ứng viên được xếp hạng bằng kiểm chứng chéo trên dev `annotated`, và lựa chọn được commit trước khi sinh dự đoán test cho các ứng viên chưa từng chạm test (commit `c3f0033`). Hệ f2 (T2b×3 với cSEBB) đứng đầu với event-F1 micro 0,2383 ± 0,0562. Chênh lệch với f4 chỉ 0,0029, nhỏ hơn độ lệch chuẩn của f2, nên f2 được *chọn* theo luật nhưng không được gọi là *tốt hơn* f4 (⟪tbl:s13⟫).

@@CAP:tbl:s13|Xếp hạng 11 ứng viên trên dev và kết quả test annotated một lần@@

@@INCLUDE:docs/thesis/tables/06_s13_ranking_test.md@@

Trên test `annotated`, f2 đạt event-F1 macro 0,1206 và micro 0,1643 [0,1103; 0,2242], PSDS-1 0,3164 và PSDS-2 0,7253. Thứ hạng trên test **không trùng** thứ hạng trên dev. f1 (BEATs đóng băng) chỉ đứng thứ 4 trên dev nhưng có micro test cao nhất (0,1817); g1 đứng thứ 6 trên dev nhưng có macro test cao nhất (0,1617). Hệ thống cuối **không** được chọn lại, vì chọn lại theo test chính là tinh chỉnh trên test. Hơn nữa, khoảng tin cậy test của các ứng viên dẫn đầu đều chồng lấp nhau (⟪fig:s13⟫). Hiện tượng này là minh chứng trực tiếp cho sai số khi chọn mô hình trên một tập dev nhỏ (134 bản ghi).

![](report/figures/m03_s13_dev_vs_test.png){width=14.5cm}

@@CAP:fig:s13|Event-F1 micro của 11 ứng viên: kiểm chứng chéo trên dev và test annotated (95% CI)@@

@@NOTE:Nguồn: docs/measurements/s13_selection_20261018.json; docs/measurements/s13_test_20261018.json; sinh bằng scripts/build_midterm_figures.py.@@

So với các thế hệ trước trên cùng tập test `annotated` (⟪tbl:progress⟫, ⟪fig:progress⟫), f2 có micro cao hơn v1 (0,1643 so với 0,0945). Tuy vậy, so với v2, f2 có micro cao hơn (0,1643 so với 0,1500) nhưng **macro thấp hơn** (0,1206 so với 0,1389) và PSDS-1 thấp hơn (0,3164 so với 0,3458), với khoảng tin cậy micro chồng lấp. Vì vậy, báo cáo **không** khẳng định f2 tốt hơn v2. Hệ f2 là hệ được khóa theo quy trình, không phải hệ được chứng minh là tốt nhất.

@@CAP:tbl:progress|Tiến triển SED v1 → v2 → f2 trên test annotated@@

@@INCLUDE:docs/thesis/tables/04_sed_progress.md@@

![](docs/thesis/figures/04_event_f1_progress.png){width=12cm}

@@CAP:fig:progress|Event-F1 micro của v1, v2 và f2 trên test annotated (95% CI)@@

@@NOTE:Nguồn: docs/measurements/s13_test_20261018.json; sinh bằng scripts/build_thesis_figures.py.@@

Phân tích theo lớp của f2 (Phụ lục C) cho thấy hệ thống còn rất yếu. 7/21 lớp có event-F1 bằng 0 trên test, trong đó có `vehicle_pass_by` với 70 sự kiện tham chiếu, `birds` và `dog_barkings_and_howlings`. Các lớp tốt nhất là `cicadas_and_crickets` (0,4138), `music` (0,3750) và `workshop` (0,3636); lớp `cat_fights_and_moans` chỉ có 9 sự kiện tham chiếu nên được báo là khớp 1/9. Hệ f2 chỉ dự đoán 295 sự kiện cho 740 sự kiện tham chiếu, và 349 lỗi là bỏ sót: hệ thống bị giới hạn chủ yếu bởi **recall**.

### Hậu xử lý cSEBB

Ở v1, v2 và T2a, cSEBB đều thua ngưỡng chung trên kiểm chứng chéo dev; ví dụ ở v1 là 0,0582 so với 0,1538. Hệ f2 là trường hợp đầu tiên cSEBB thắng: 0,2383 ± 0,0562 so với 0,2107 ± 0,0343 của ngưỡng chung (⟪tbl:csebb⟫). Mức chênh này nằm trong biên độ dao động giữa các fold. Giả thuyết hợp lý là cSEBB, vốn dò điểm thay đổi trên posterior theo khung, phát huy khi posterior có độ phân giải thật (T2b, 40 ms, không có tầng làm mượt thời gian). Trên các mô hình có tầng hồi quy hoặc gộp thô, cSEBB thua. Kết luận về cSEBB vì vậy phải được phát biểu có điều kiện, không thể khái quát thành "cSEBB tốt hơn" hay "cSEBB kém hơn".

@@CAP:tbl:csebb|Hai họ hậu xử lý của hệ f2@@

@@INCLUDE:docs/thesis/tables/07_csebb.md@@

## RQ2 — Mô tả có căn cứ

⟪tbl:rq2levels⟫ báo các metric căn cứ trên test của hệ f2 theo bốn chế độ và hai mức đánh giá. Ba kết quả nổi bật như sau.

@@CAP:tbl:rq2levels|Mức căn cứ của mô tả trên test theo chế độ sinh và mức đánh giá (hệ f2)@@

@@INCLUDE:report/tables/m04_rq2_levels.md@@

Thứ nhất, khi chỉ nhận dòng thời gian, LLM sinh tự do **hiếm khi bịa nguồn âm**. Tỷ lệ ảo giác nguồn âm của chế độ unconstrained chỉ 0,0065 ở mức oracle và 0,0112 ở mức đầu–cuối. Lỗi thật của sinh tự do nằm ở chỗ khác: 28,9% (oracle) và 40,1% (đầu–cuối) mô tả thêm bối cảnh không có trong bằng chứng, khoảng 14% gọi tên quá cụ thể so với lớp gộp, và 0,7% chứa từ cấm. Ràng buộc ngữ pháp (constrained và constrained-cover) đưa cả bốn loại lỗi này về 0. Hiệu constrained − unconstrained ở mức đầu–cuối là −0,011 [−0,022; −0,002] với ảo giác và −0,401 [−0,479; −0,324] với bối cảnh.

Thứ hai, ràng buộc có giá: chế độ constrained **bỏ sót** nhiều hơn. Ở mức oracle, tỷ lệ bỏ sót là 0,0925 so với 0,0184 của unconstrained (hiệu +0,074 [+0,044; +0,107]). Ở mức đầu–cuối, hiệu là +0,007 [−0,002; +0,019], khoảng tin cậy chứa 0. Chế độ constrained-cover giải quyết đánh đổi này theo cấu tạo: bỏ sót bằng 0 ở cả hai mức, và không thua unconstrained ở metric nào. Ngược lại, mô tả của chế độ này gần với mô tả template về văn phong.

Thứ ba, khi đổi hệ SED từ v1 sang f2 (⟪tbl:rq2⟫), hướng kết luận của RQ2 giữ nguyên. Bỏ sót đầu–cuối của constrained giảm từ 0,036 xuống 0,012. Ảo giác của unconstrained đổi từ 0,005 thành 0,011 với khoảng tin cậy chồng lấp, nên không phải một thay đổi phân biệt được. Mô tả template tiếng Việt trên test f2 không có vi phạm G1–G3 nào ở cả hai tập đánh giá.

@@CAP:tbl:rq2|RQ2 ở mức đầu–cuối trên test: hệ v1 (ensemble C) và hệ f2@@

@@INCLUDE:docs/thesis/tables/08_rq2_caption.md@@

Hai giới hạn quan trọng khi đọc kết quả RQ2:

- **Bộ đo dựa trên từ điển.** Trên một mẫu 60 mô tả test do **một** người đọc mù đối chiếu (thực hiện với hệ cũ), việc trích lần nhắc bằng từ điển đạt precision 0,896 và recall 0,936 so với người đọc. Từ điển dễ dãi hơn người ở một số chỗ: một kiểu bịa "tiếng búa gõ" bị che sau từ chỉ địa điểm "xưởng" mà từ điển không bắt được. Ở chỗ khác, nó gắn cờ nhầm: 7/8 lần nhắc bị gắn cờ "bịa" trên test hóa ra là lỗi của từ điển. Mẫu nhỏ và chỉ có một người đọc, nên đây là kiểm tra sơ bộ, chưa phải đánh giá độ tin cậy.
- **"Không ảo giác" ở mức đầu–cuối không có nghĩa là mô tả đúng với âm thanh.** Đây là giới hạn quan trọng nhất. Mô tả trung thành với dòng thời gian *dự đoán*, mà hệ f2 có event-F1 micro chỉ 0,1643 và bỏ sót 349/740 sự kiện tham chiếu. Vì vậy, phần lớn mô tả đầu–cuối có căn cứ theo hợp đồng nhưng vẫn thiếu hoặc sai so với âm thanh thật. Hợp đồng căn cứ bảo đảm mọi sai sót đều truy được về một sự kiện cụ thể của SED; nó không loại bỏ được sai sót đó.

## RQ3 — Truy hồi và câu trả lời có bằng chứng

⟪tbl:rq3⟫ báo kết quả truy hồi trên test cho hai kho sự kiện: kho dựng từ dự đoán của run B (mốc ban đầu) và kho dựng từ dự đoán của hệ f2 (hệ hiện hành), với bộ lọc chuẩn (gold) lấy từ bộ truy vấn và bộ lọc do bộ phân tích câu hỏi sinh ra (parsed).

@@CAP:tbl:rq3|RQ3 trên test: nDCG@10, Recall@k và độ đúng bộ lọc theo kho sự kiện, bộ lọc, chế độ và ngôn ngữ@@

@@INCLUDE:docs/thesis/tables/09_rq3_retrieval.md@@

Trên kho run B, chế độ structured_only đạt nDCG@10 cao nhất (0,5231), hybrid đứng thứ hai (0,4808 tiếng Anh, 0,4716 tiếng Việt), và vector_only thấp nhất (0,4179 và 0,3403). Hiệu hybrid − structured là −0,042 [−0,085; −0,004]: với tài liệu dạng template, xếp hạng vector trong tập đã lọc không giúp ích mà còn làm giảm nhẹ chất lượng. Độ đúng bộ lọc của structured_only và hybrid đạt 1,000 như yêu cầu kiến trúc. Vector_only chỉ đạt 0,5866 (tiếng Anh), tức khoảng 41% kết quả vi phạm ít nhất một ràng buộc cứng mà người hỏi đặt ra.

Khi đổi sang kho f2, kết quả **suy giảm** ở hai chế độ có lọc: nDCG@10 của structured_only giảm từ 0,5231 xuống 0,4161, của hybrid tiếng Anh từ 0,4808 xuống 0,4147. Vector_only lại tăng, từ 0,4179 lên 0,5261. Bộ xây tài liệu và cách tính độ liên quan không đổi; thứ thay đổi là tập sự kiện dự đoán. Giả thuyết là hệ f2 dự đoán ít sự kiện hơn hẳn số tham chiếu, nên bộ lọc cứng trên sự kiện dự đoán loại mất nhiều bản ghi thực sự liên quan; vector_only không bị ràng buộc đó (độ đúng bộ lọc chỉ 0,274) nên vẫn xếp được các bản ghi này lên. Giả thuyết **chưa được kiểm chứng**, và kết quả suy giảm được báo nguyên văn, không diễn giải theo hướng có lợi. Kết quả này cũng cho thấy chất lượng truy hồi trên dòng thời gian bị chặn bởi recall của SED.

Hai điều kiện đánh giá cần nêu rõ. Thứ nhất, kết quả với bộ lọc gold giả định câu hỏi luôn được phân tích đúng, nên chỉ là cận trên về độ đúng bộ lọc. Với bộ lọc do bộ phân tích sinh ra trên kho f2, nDCG@10 thay đổi trong khoảng −0,006 đến 0,000 so với gold. Thứ hai, ở cả tám cấu hình trả lời (gold/parsed × structured/hybrid × Anh/Việt), tỷ lệ khẳng định thiếu bằng chứng là 0,000, và 97/97 câu trả lời đúng hợp đồng, có bằng chứng thật và trích dẫn thỏa bộ lọc. Như vậy, đúng như mục tiêu của ràng buộc A1–A4, câu trả lời không vượt ra ngoài những gì kho sự kiện chứa. Đổi lại, khi kho sự kiện thiếu, câu trả lời cũng thiếu.

## Bộ phân tích câu hỏi và độ khớp khi phục vụ

Bộ phân tích câu hỏi sinh đầu ra hợp lược đồ ở 240/240 câu (⟪tbl:parser⟫). Độ đúng ngữ nghĩa hoàn toàn đạt 0,855 trên 200 câu template và 0,925 trên 40 câu diễn đạt lại được khóa trước khi chạy. Lỗi chủ yếu nằm ở vị từ thời gian: độ chính xác vị từ trên tập template chỉ 0,767, với các lỗi như đảo vai trò $a/b$, nhầm "within" thành "overlaps", hoặc bỏ ràng buộc thời lượng. Trên tập validation, hybrid với bộ lọc parsed thay đổi +0,012 (Anh) và −0,002 (Việt) so với gold. Mức tăng dương này không phải bằng chứng bộ phân tích cải thiện truy hồi: một bộ lọc sai có thể tình cờ làm thứ hạng tốt lên.

@@CAP:tbl:parser|Đánh giá bộ phân tích câu hỏi thành bộ lọc@@

@@INCLUDE:docs/thesis/tables/10_parser_l2.md@@

Hệ thống phục vụ được kiểm tra xem có tái tạo đúng đầu ra đã đóng băng hay không, bằng cách so sự kiện, không chấm điểm lại trên test (⟪tbl:parity⟫). Trên GPU, 299/299 sự kiện trùng khít. Trên CPU trong container, phép tính số thực khác nên chỉ 290/299 sự kiện trùng khít và 294/299 nằm trong collar, với sai lệch xác suất lớn nhất 0,0239. Bản demo chạy CPU vì thế không hoàn toàn đồng nhất với hệ đã đo; chênh lệch được định lượng như trên.

@@CAP:tbl:parity|Độ khớp giữa đường nghiên cứu và đường phục vụ của hệ f2@@

@@INCLUDE:docs/thesis/tables/11_serving_parity.md@@

## Thảo luận và các mối đe dọa đến tính hợp lệ

Tổng hợp lại, đề tài đã có một hệ thống đầu–cuối hoạt động, cùng bằng chứng cho từng câu hỏi nghiên cứu. RQ1 âm tính với nhiều seed và hai công thức. RQ2 cho thấy ràng buộc ngữ pháp loại bỏ các dạng ảo giác và suy diễn đo được, với cái giá bỏ sót mà biến thể cover giải quyết được. RQ3 cho thấy bộ lọc cứng bảo đảm tính đúng ràng buộc tuyệt đối, nhưng chất lượng xếp hạng bị chặn bởi chất lượng SED. Điểm yếu nhất của hệ thống hiện tại là chính bước SED: event-F1 thấp và recall thấp truyền xuống mọi tầng phía sau. Các mối đe dọa đến tính hợp lệ được liệt kê dưới đây; mỗi mục đều có bằng chứng trong kho mã.

- **Tập đánh giá nhỏ.** Dev có 137 (134 annotated) và test có 142 (139 annotated) bản ghi, nên khoảng tin cậy rộng. Đơn vị bootstrap là bản ghi, nên khoảng tin cậy chỉ phản ánh bất định do mẫu bản ghi, không phản ánh dao động giữa các seed.
- **Huấn luyện SED không tất định.** Cùng mã và cùng seed, F1 macro theo khung của nhánh B vẫn đổi từ 0,5850 sang 0,5705. Mọi so sánh SED vì thế cần nhiều seed, trong khi các ablation v2 chỉ có một seed mỗi biến thể.
- **Trần do nhãn và collar.** Trần người được đo trên chỉ 8 cặp. Collar 0,2 s chặt hơn độ chính xác của nhãn.
- **Hai thước đo micro và macro.** Trước ngày 26/09, các con số chính đều là micro, lệch với quy tắc của giao thức đánh giá là báo macro. Từ ngày này, macro được báo trước, nhưng thước chọn hệ thống vẫn là micro. Hệ f2 được chọn bằng micro có macro test thấp hơn v2.
- **Sai lệch truy nguồn.** Trong vòng S13, lượt đánh giá test đầu tiên chạy trên cây làm việc sạch. Tuy nhiên, báo cáo chưa commit do chính script sinh ra khiến 15 lượt sau ghi `dirty`. Mẫu hình này lặp lại ở S8, trong đó hai lượt mô tả còn dính một thư mục log tạm. Mã và cấu hình không thay đổi và test không được chạy lại, nhưng đây vẫn là hạn chế truy nguồn cần công khai. Sổ ghi test (⟪tbl:ledger⟫) liệt kê mọi lượt chạm test, trong đó 10/40 lượt đánh giá SED có cờ dirty.
- **Trùng nguồn với AudioSet.** Một phần âm thanh của hai bộ dữ liệu lấy từ AudioSet, trong khi các bộ mã hóa được tiền huấn luyện trên AudioSet. Mức trùng không định lượng được.
- **Chưa có mốc so sánh công bố.** Chưa có baseline công bố trên DataSED để so trực tiếp; số của DCASE 2016 chỉ dùng để định cỡ.
- **Bộ đo mô tả dựa trên từ điển**, chỉ đối chiếu với một người đọc trên 60 mô tả.
- **Kết quả RQ3 với bộ lọc gold** là cận trên về độ đúng bộ lọc.
- **PSDS không tăng** dù event-F1 tăng (v2 so với v1), và nguyên nhân chưa được giải thích.

@@CAP:tbl:ledger|Sổ ghi các lần chạm tập test tính tới mốc báo cáo@@

@@INCLUDE:report/tables/m06_test_ledger.md@@
