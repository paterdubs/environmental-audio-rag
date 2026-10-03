# KẾT QUẢ VÀ THẢO LUẬN

Chương này báo cáo các kết quả có được tại mốc giữa kỳ (03/10/2026), kể cả kết quả âm tính và kết quả kém đi. Các bảng do script sinh từ tệp kết quả đã khóa, nguồn ghi ngay dưới bảng. Trong các bảng chính, **số in đậm là giá trị tốt nhất trong cột** (hoặc trong nhóm hàng cùng loại), và **hàng nền xám là cấu hình đang dùng** trong hệ thống cuối; in đậm không có nghĩa là khác biệt có ý nghĩa thống kê. Bốn quy ước khi đọc số:

- **Event-F1** là F1 theo sự kiện với collar 0,2 s (Chương 2), tính bằng thư viện `sed_eval`; macro hay micro được ghi rõ ở từng chỗ.
- **Tập đánh giá** là `all` (142 bản ghi test) hoặc `annotated` (139 bản ghi test có nhãn đa âm, Chương 3).
- **Khoảng tin cậy** 95% được bootstrap theo bản ghi (Chương 4).
- Số trên **dev** dùng để chọn cấu hình; số trên **test** chỉ dùng để đo cấu hình đã chọn và không bao giờ dùng để chọn lại.

## Mô hình phân loại DataSEC

Mô hình phân loại đạt macro-F1 0,8466 trên 22 lớp gộp của tập test DataSEC (⟪tbl:classifier⟫). Ở cấp lớp con, macro-F1 trên cả 28 nút chỉ là 0,6266 vì bị kéo xuống bởi các nút có rất ít mẫu test; chỉ tính 5 nút có ít nhất 10 mẫu test thì được 0,8453. Theo quy ước, nút ít mẫu chỉ báo số tuyệt đối (Phụ lục C), chẳng hạn `vacuum_cleaner` đúng 0/4 và `air_compressor` đúng 0/5. Tỷ lệ nhất quán cha–con là 0,9526: 95% lần, lớp con được đoán thuộc đúng nhóm của lớp gộp được đoán. Hai lớp gộp yếu nhất là `vehicle_idling` (F1 0,6154) và `vehicle_pass_by` (0,6538), có âm thanh gần nhau.

@@CAP:tbl:classifier|Kết quả mô hình phân loại DataSEC trên tập test@@

@@INCLUDE:report/tables/m01_classifier.md@@

Việc hiệu chuẩn xác suất cho kết quả âm tính: nhiệt độ $T = 1{,}5681$ chọn trên dev làm sai số hiệu chuẩn (ECE) trên test **tăng** từ 0,0332 lên 0,0564. Nhóm báo đúng như vậy, không chỉnh $T$ theo test. Mô hình phân loại tái lập trùng từng bit khi huấn luyện lại cùng seed; mô hình SED thì không (xem phần hạn chế).

## RQ1: học thêm từ DataSEC có giúp không?

Vì huấn luyện SED không tất định (ADR-0021), câu trả lời dựa trên nhiều lần chạy. Với công thức v1 và tập test `all`, phân tích chính dùng 7 lần chạy có cây làm việc sạch: 3 của nhánh B và 4 của nhánh C (⟪tbl:rq1⟫). Event-F1 micro trung bình của B là 0,0610 và của C là 0,0539; hiệu C − B (bootstrap ghép cặp theo bản ghi) là −0,0071 [−0,0164; +0,0021], Welch p = 0,2336. PSDS cũng không phân biệt được: PSDS-1 0,2902 so với 0,2892 (p = 0,913), PSDS-2 0,6498 so với 0,6591 (p = 0,181). Phân tích độ nhạy với cả 10 lần chạy cho cùng kết luận (không chỉ số nào có p < 0,05). Ngược lại, tiền huấn luyện nói chung giúp rõ: nhánh A học từ đầu chỉ đạt event-F1 0,0360 và PSDS-2 0,4514, so với 0,0621 và 0,6456 của nhánh B.

@@CAP:tbl:rq1|Kết quả RQ1: công thức v1 (test all) và công thức v2 (test annotated)@@

@@INCLUDE:docs/thesis/tables/03_rq1.md@@

Để kiểm tra kết quả âm tính có phải do kiến trúc v1 quá thô, nhóm lặp lại phép so sánh với công thức v2 (3 lần chạy B-v2 so với 3 lần C-v2). Phân tích này được ghi trước và chỉ mở test sau khi hệ thống cuối đã được khóa (ADR-0031). Trên test `annotated`, event-F1 macro của B-v2 và C-v2 là 0,1221 và 0,1147, micro là 0,1324 và 0,1294. Hiệu C − B về micro là −0,0029 [−0,0254; +0,0199], Welch p = 0,6965 (macro p = 0,4220). Riêng PSDS-2 tăng +0,0279 với p = 0,0193, nên kết luận phụ thuộc vào chỉ số.

**Kết luận RQ1:** với cả hai công thức, nhóm **không** có bằng chứng rằng huấn luyện thêm trên DataSEC cải thiện event-F1 so với chỉ dùng AudioSet. Điều này không có nghĩa DataSEC "vô ích" nói chung: PSDS-2 của công thức v2 tăng có ý nghĩa khi xét riêng, dù chưa hiệu chỉnh cho việc so sánh nhiều chỉ số. Đây là kết quả âm tính hợp lệ và được giữ nguyên; trọng tâm đóng góp vì vậy chuyển sang C1, C2 và C4 (ADR-0021).

## Mô hình SED tiến bộ ra sao?

### Vì sao event-F1 của v1 thấp?

Sau RQ1, event-F1 của v1 còn rất thấp nên nhóm chẩn đoán nguyên nhân trên dev trước khi cải tiến. Một mô hình nhận dạng hoàn hảo nhưng ra quyết định theo khối 0,64 s (như CNN14 nén 64 lần) cũng chỉ đạt tối đa event-F1 0,6294; với khối 1,28 s, tối đa là 0,3032. Giới hạn do nhãn, đo trên 8 cặp bản ghi được gán nhãn hai lần, là 0,5785. Với v1 trên dev, event-F1 nếu chỉ xét thời điểm bắt đầu là 0,2325, chỉ xét thời điểm kết thúc là 0,4975, còn F1 theo đoạn 1 s là 0,6542. Trong 886 sự kiện tham chiếu, 112 khớp collar, 417 đúng lớp và có chồng lấp nhưng lệch biên, và 357 bị bỏ sót. Vậy lỗi chủ yếu nằm ở **biên sự kiện** và **bỏ sót**, không phải nhận dạng lớp. Nới collar thời điểm bắt đầu từ 0,2 s lên 1 s làm event-F1 của nhánh B tăng khoảng ba lần (0,062 lên 0,185), phù hợp với chẩn đoán này.

Các số này là số dev in-sample và hai tệp đo được sinh khi cây làm việc có thay đổi chưa commit (`git.dirty = true`), nên chỉ dùng để chẩn đoán, không phải kết quả đánh giá. Một giả thuyết ban đầu cho rằng "xác suất bão hòa làm thời điểm bắt đầu bị trễ" đã được đo và bác bỏ (trung vị xác suất của khung không có sự kiện chỉ 0,008; sai số thời điểm bắt đầu phân bố đối xứng, chỉ 30,2% nằm trong ±0,2 s). Chẩn đoán đúng là biên **tản rộng và đối xứng**.

### Từ v1 đến v2

Ba lần chạy v2 đạt event-F1 micro theo kiểm chứng chéo trên dev là 0,1900, 0,2096 và 0,2169, so với 0,1538 của ensemble v1. Thử bỏ từng thành phần cho thấy chỉ độ phân giải thời gian có tác động phân biệt được: quay về nén 64 lần làm event-F1 giảm 0,0840, gấp 1,6 lần độ lệch chuẩn giữa các fold. Trần trọng số dương 50 thay cho 10 (−0,0126) và bỏ tăng cường dữ liệu (+0,0068) đều nằm trong nhiễu; mỗi biến thể chỉ có một seed nên "không phân biệt được" không đồng nghĩa "không có tác dụng". Đáng chú ý, average precision theo khung gần như không đổi khi bỏ độ phân giải (0,667 so với 0,688) trong khi event-F1 giảm mạnh: chỉ số theo khung không phản ánh chất lượng định vị.

Theo luật chọn ghi trước, ensemble 3 seed của v2 (kiểm chứng chéo 0,2129 ± 0,0622) được commit trước khi mở test. Nó được chọn theo luật nhưng **không** được gọi là tốt hơn một lần chạy đơn, vì chênh 0,023 nhỏ hơn độ lệch chuẩn giữa các fold. Trên test `all`, ensemble v2 đạt event-F1 micro 0,1476 [0,1088; 0,1866] và macro 0,1369, so với 0,0941 và 0,0917 của v1; hiệu ghép cặp v2 − v1 là +0,0536 [+0,0261; +0,0853], khoảng tin cậy không chứa 0. Tuy vậy **PSDS không tăng**: PSDS-1 0,3447 so với 0,3489, PSDS-2 0,6744 so với 0,6987. Lợi ích của v2 nằm ở điểm vận hành đã chọn chứ không phải trên toàn dải ngưỡng; nguyên nhân chưa giải thích được và là việc còn lại (Chương 7).

Về ghép sự kiện trên ba nhánh v1: từ dev sang test, event-F1 với ngưỡng riêng từng lớp giảm 48%, 39%, 41% (A, B, C), còn với ngưỡng chung chỉ giảm 15%, 4%, 2%, nên ngưỡng riêng từng lớp quá khớp dev một cách có hệ thống. Lọc trung vị không có tác động rõ (Δ +0,0063, +0,0026, −0,0014; đổi dấu giữa các nhánh).

### Chọn hệ thống cuối và kết quả test

Vòng chọn cuối gồm 11 ứng viên đã ghi trước (Chương 4). Các ứng viên được xếp hạng bằng kiểm chứng chéo trên dev `annotated`, và lựa chọn được commit trước khi sinh dự đoán test cho các ứng viên chưa từng chạm test (commit `c3f0033`). Hệ f2 (T2b×3 với cSEBB) đứng đầu với event-F1 micro 0,2383 ± 0,0562. Chênh lệch với f4 chỉ 0,0029, nhỏ hơn độ lệch chuẩn của f2, nên f2 được *chọn* theo luật nhưng không được gọi là *tốt hơn* f4 (⟪tbl:s13⟫).

@@CAP:tbl:s13|Xếp hạng 11 ứng viên trên dev và kết quả test annotated (một lần)@@

@@INCLUDE:docs/thesis/tables/06_s13_ranking_test.md|cols=1,2,4,5,6,7,8,9|best=5+,7+,8+|used=2:^f2$@@

Trên test `annotated`, f2 đạt event-F1 macro 0,1206 và micro 0,1643 [0,1103; 0,2242], PSDS-1 0,3164 và PSDS-2 0,7253. Thứ hạng test **không trùng** thứ hạng dev: f1 (BEATs đóng băng) chỉ đứng thứ 4 trên dev nhưng có micro test cao nhất (0,1817); g1 đứng thứ 6 trên dev nhưng có macro test cao nhất (0,1617). Hệ cuối **không** được chọn lại, vì chọn lại theo test chính là tinh chỉnh trên test. Hơn nữa, khoảng tin cậy test của các ứng viên đứng đầu đều chồng lấp. Đây là minh chứng trực tiếp cho sai số khi chọn mô hình trên tập dev nhỏ (134 bản ghi).

So với các thế hệ trước trên cùng tập test `annotated` (⟪tbl:progress⟫), f2 có micro cao hơn v1 (0,1643 so với 0,0945). So với v2, f2 có micro cao hơn (0,1643 so với 0,1500) nhưng **macro thấp hơn** (0,1206 so với 0,1389) và PSDS-1 thấp hơn (0,3164 so với 0,3458), với khoảng tin cậy micro chồng lấp. Vì vậy báo cáo **không** khẳng định f2 tốt hơn v2: f2 là hệ được khóa theo quy trình, không phải hệ được chứng minh là tốt nhất.

@@CAP:tbl:progress|Tiến triển SED v1 → v2 → f2 trên test annotated@@

@@COLWIDTHS:23,10,11,11,19,13,13@@

@@INCLUDE:docs/thesis/tables/04_sed_progress.md|cols=1,2,3,4,5,6,7|best=3+,4+,6+,7+|used=1:S13@@

Phân tích theo lớp (Phụ lục C) cho thấy f2 còn rất yếu: 7/21 lớp có event-F1 bằng 0 trên test, trong đó có `vehicle_pass_by` (70 sự kiện tham chiếu), `birds` và `dog_barkings_and_howlings`. Các lớp tốt nhất là `cicadas_and_crickets` (0,4138), `music` (0,3750) và `workshop` (0,3636); lớp `cat_fights_and_moans` chỉ có 9 sự kiện tham chiếu nên báo là khớp 1/9. Hệ f2 chỉ dự đoán 295 sự kiện cho 740 sự kiện tham chiếu, và 349 lỗi là bỏ sót: hệ bị giới hạn chủ yếu bởi **recall**.

**Về cSEBB.** Ở v1, v2 và T2a, cSEBB đều thua ngưỡng chung trên kiểm chứng chéo dev (ví dụ ở v1: 0,0582 so với 0,1538). Hệ f2 là trường hợp đầu tiên cSEBB thắng: 0,2383 ± 0,0562 so với 0,2107 ± 0,0343 của ngưỡng chung, chênh lệch nằm trong biên dao động giữa các fold. Giả thuyết hợp lý là cSEBB phát huy khi xác suất có độ phân giải thật (T2b, 40 ms, không có tầng làm mượt thời gian), còn với mô hình có tầng hồi quy hoặc gộp thô thì thua. Kết luận về cSEBB vì vậy phải phát biểu có điều kiện, không thể nói chung là "tốt hơn" hay "kém hơn".

## RQ2: mô tả có bám sát sự kiện không?

⟪tbl:rq2levels⟫ báo các chỉ số bám sát sự kiện trên test của hệ f2, theo bốn cách sinh và hai mức đánh giá (oracle dùng nhãn gốc, đầu–cuối dùng sự kiện dự đoán). Ba kết quả nổi bật như sau.

@@CAP:tbl:rq2levels|Mức bám sát sự kiện của mô tả trên test (hệ f2, 142 bản ghi)@@

@@INCLUDE:report/tables/m04_rq2_levels.md|cols=1,2,3,4,5,6,7,8|group=2|best=3-,4-,6-,7-,8-|used=1:^Template@@

**Thứ nhất,** khi chỉ nhận danh sách sự kiện, mô hình ngôn ngữ viết tự do **hiếm khi bịa nguồn âm**: tỷ lệ ảo giác của cách unconstrained chỉ 0,0065 (oracle) và 0,0112 (đầu–cuối). Lỗi thật của viết tự do nằm ở chỗ khác: 28,9% (oracle) và 40,1% (đầu–cuối) mô tả thêm bối cảnh không có trong bằng chứng, khoảng 14% gọi tên quá cụ thể so với lớp gộp, và 0,7% chứa từ cấm. Ràng buộc ngữ pháp (constrained và constrained-cover) đưa cả bốn loại lỗi này về 0. Hiệu constrained − unconstrained ở mức đầu–cuối là −0,011 [−0,022; −0,002] với ảo giác và −0,401 [−0,479; −0,324] với bối cảnh.

**Thứ hai,** ràng buộc có giá: cách constrained **bỏ sót** nhiều hơn. Ở mức oracle, tỷ lệ bỏ sót là 0,0925 so với 0,0184 của unconstrained (hiệu +0,074 [+0,044; +0,107]); ở mức đầu–cuối, hiệu là +0,007 [−0,002; +0,019], khoảng tin cậy chứa 0. Cách constrained-cover giải quyết sự đánh đổi này theo cấu tạo: bỏ sót bằng 0 ở cả hai mức và không thua unconstrained ở chỉ số nào, nhưng văn phong gần với mô tả template.

**Thứ ba,** khi đổi hệ SED từ v1 sang f2, hướng kết luận giữ nguyên. Bỏ sót đầu–cuối của constrained giảm từ 0,036 xuống 0,012. Ảo giác của unconstrained đổi từ 0,005 thành 0,011 với khoảng tin cậy chồng lấp, nên không phải thay đổi phân biệt được. Mô tả template tiếng Việt trên testkhông vi phạm G1–G3 ở cả hai tập đánh giá. Trong demo, mô tả được sinh bằng template (hàng nền xám).

Hai giới hạn khi đọc kết quả RQ2:

- **Bộ đo dựa trên từ điển.** Trên mẫu 60 mô tả test do **một** người đọc mù đối chiếu (với hệ cũ), việc trích nguồn âm bằng từ điển đạt precision 0,896 và recall 0,936 so với người đọc. Từ điển dễ dãi hơn người ở một số chỗ: một kiểu bịa "tiếng búa gõ" bị che sau từ chỉ địa điểm "xưởng" mà từ điển không bắt được; ở chỗ khác nó gắn cờ nhầm (7/8 lần bị gắn cờ "bịa" trên test hóa ra là lỗi từ điển). Mẫu nhỏ và chỉ một người đọc, nên đây là kiểm tra sơ bộ.
- **"Không ảo giác" ở mức đầu–cuối không có nghĩa là mô tả đúng với âm thanh.** Mô tả trung thành với danh sách sự kiện *dự đoán*, mà hệcó event-F1 micro chỉ 0,1643 và bỏ sót 349/740 sự kiện tham chiếu. Vì vậy phần lớn mô tả đầu–cuối bám sát dự đoán nhưng vẫn thiếu hoặc sai so với âm thanh thật. Ràng buộc bảo đảm mọi sai sót truy được về một sự kiện cụ thể của SED; nó không loại bỏ được sai sót đó.

## RQ3: truy hồi và câu trả lời có bằng chứng

⟪tbl:rq3⟫ báo kết quả truy hồi trên test cho hai kho sự kiện: kho dựng từ dự đoán của nhánh B (mốc ban đầu) và kho dựng từ dự đoán của hệ f2 (hệ hiện hành), với bộ lọc chuẩn (gold) lấy từ bộ truy vấn. Hàng nền xám là cấu hình của hệ thống: kho f2, chế độ hybrid.

@@CAP:tbl:rq3|RQ3 trên test với bộ lọc gold: nDCG@10, Recall@10 và độ đúng bộ lọc@@

@@COLWIDTHS:14,21,14,24,12,15@@

@@INCLUDE:docs/thesis/tables/09_rq3_retrieval.md|keep=1:^(Run B\|f2) — gold$|cols=1,2,4,5,8,9|group=1|best=4+,9+|used=1:^f2 — gold$&2:^hybrid@@

Trên kho nhánh B, chế độ structured_only đạt nDCG@10 cao nhất (0,5231), hybrid đứng thứ hai (0,4808 tiếng Anh, 0,4716 tiếng Việt) và vector_only thấp nhất (0,4179 và 0,3403). Hiệu hybrid − structured là −0,042 [−0,085; −0,004]: với tài liệu dạng template, xếp hạng vector trong tập đã lọc không giúp mà còn giảm nhẹ chất lượng. Độ đúng bộ lọc của structured_only và hybrid là 1,000 như kiến trúc yêu cầu; vector_only chỉ đạt 0,5866 (tiếng Anh), tức khoảng 41% kết quả vi phạm ít nhất một ràng buộc cứng của người hỏi.

Khi đổi sang kho f2, kết quả **kém đi** ở hai chế độ có lọc: nDCG@10 của structured_only giảm từ 0,5231 xuống 0,4161, của hybrid (tiếng Anh) từ 0,4808 xuống 0,4147. Ngược lại vector_only tăng từ 0,4179 lên 0,5261. Cách xây tài liệu và cách tính độ liên quan không đổi; thứ thay đổi là tập sự kiện dự đoán. Giả thuyết là f2 dự đoán ít sự kiện hơn hẳn số tham chiếu nên bộ lọc cứng loại mất nhiều bản ghi thực sự liên quan, còn vector_only không bị ràng buộc đó (độ đúng bộ lọc chỉ 0,274) nên vẫn xếp được các bản ghi này lên. Giả thuyết này **chưa được kiểm chứng**; nhóm báo kết quả kém đi nguyên văn, không diễn giải theo hướng có lợi. Điều này cũng cho thấy chất lượng truy hồi bị chặn bởi recall của SED.

Hai điều kiện đánh giá cần nêu. Thứ nhất, bộ lọc gold giả định câu hỏi luôn được phân tích đúng nên chỉ là cận trên; với bộ lọc do bộ phân tích câu hỏi sinh ra (parsed) trên kho f2, nDCG@10 thay đổi từ −0,006 đến 0,000 so với gold. Thứ hai, ở cả tám cấu hình trả lời (gold/parsed × structured/hybrid × Anh/Việt), tỷ lệ khẳng định thiếu bằng chứng là 0,000 và 97/97 câu trả lời đúng hợp đồng, có bằng chứng thật và trích dẫn thỏa bộ lọc. Câu trả lời không vượt ra ngoài những gì kho chứa; đổi lại, kho thiếu thì câu trả lời cũng thiếu.

## Bộ phân tích câu hỏi và độ khớp khi phục vụ

Bộ phân tích câu hỏi cho đầu ra hợp lược đồ ở 240/240 câu (⟪tbl:parser⟫). Độ đúng ngữ nghĩa hoàn toàn đạt 0,855 trên 200 câu template và 0,925 trên 40 câu diễn đạt lại được khóa trước khi chạy. Lỗi chủ yếu nằm ở điều kiện thời gian: độ chính xác trên tập template chỉ 0,767, với các lỗi như đảo vai trò a/b, nhầm "within" thành "overlaps" hoặc bỏ ràng buộc thời lượng. Trên tập validation, hybrid với bộ lọc parsed thay đổi +0,012 (Anh) và −0,002 (Việt) so với gold; mức tăng dương này không phải bằng chứng bộ phân tích cải thiện truy hồi, vì bộ lọc sai cũng có thể tình cờ làm thứ hạng tốt lên.

@@CAP:tbl:parser|Đánh giá bộ phân tích câu hỏi thành bộ lọc@@

@@INCLUDE:docs/thesis/tables/10_parser_l2.md|cols=1,2,3,4,5,6,7@@

Hệ thống phục vụ cũng được kiểm xem có tái tạo đúng đầu ra đã đóng băng không, bằng cách so sự kiện (không chấm điểm lại trên test). Trên GPU, 299/299 sự kiện trùng khít. Trên CPU trong container, phép tính số thực khác nên chỉ 290/299 sự kiện trùng khít và 294/299 nằm trong collar, với sai lệch xác suất lớn nhất 0,0239. Bản demo chạy CPU nên không hoàn toàn đồng nhất với hệ đã đo; chênh lệch được định lượng như trên.

## Thảo luận và hạn chế

Tóm lại, nhóm đã có một hệ thống đầu–cuối chạy được, cùng bằng chứng cho từng câu hỏi nghiên cứu. RQ1 âm tính với nhiều seed và hai công thức. RQ2 cho thấy ràng buộc ngữ pháp loại bỏ các dạng ảo giác và suy diễn đo được, với cái giá là bỏ sót mà biến thể cover giải quyết. RQ3 cho thấy bộ lọc cứng bảo đảm đúng ràng buộc tuyệt đối, nhưng chất lượng xếp hạng bị chặn bởi chất lượng SED. Điểm yếu nhất hiện nay chính là bước SED: event-F1 và recall thấp truyền xuống mọi tầng sau. Các hạn chế chính:

- **Tập đánh giá nhỏ.** Dev có 137 (134 annotated) và test có 142 (139 annotated) bản ghi, nên khoảng tin cậy rộng. Bootstrap theo bản ghi chỉ phản ánh bất định do mẫu bản ghi, không phản ánh dao động giữa các seed.
- **Huấn luyện SED không tất định.** Cùng mã và cùng seed, F1 macro theo khung của nhánh B vẫn đổi từ 0,5850 sang 0,5705; mọi so sánh SED cần nhiều seed, trong khi các thử nghiệm bỏ-từng-phần của v2 chỉ có một seed.
- **Giới hạn của nhãn.** Giới hạn người đo trên chỉ 8 cặp; collar 0,2 s chặt hơn độ chính xác của nhãn.
- **Micro và macro.** Trước ngày 26/09 các số chính đều là micro, lệch với quy tắc báo macro. Từ ngày này macro được báo trước nhưng việc chọn hệ thống vẫn dùng micro, nên f2 có macro test thấp hơn v2.
- **Sai lệch truy nguồn.** Ở vòng chọn cuối, lượt đánh giá test đầu chạy trên cây làm việc sạch, nhưng báo cáo chưa commit do chính script sinh ra làm 15 lượt sau ghi `dirty`; mẫu hình này lặp lại ở S8 với một thư mục log tạm. Mã và cấu hình không đổi và test không chạy lại, nhưng đây vẫn là hạn chế truy nguồn cần công khai. Sổ ghi test (Phụ lục B) cho thấy 10/40 lượt đánh giá SED có cờ `dirty`.
- **Trùng nguồn với AudioSet** (mức trùng không định lượng được) và **chưa có mốc so sánh công bố** trên DataSED; số của DCASE 2016 chỉ để định cỡ.
- **Bộ đo mô tả dựa trên từ điển**, chỉ đối chiếu với một người đọc trên 60 mô tả.
- **Kết quả RQ3 với bộ lọc gold** chỉ là cận trên về độ đúng bộ lọc.
- **PSDS không tăng** dù event-F1 tăng (v2 so với v1), nguyên nhân chưa giải thích được.
