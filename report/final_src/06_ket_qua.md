# KẾT QUẢ VÀ THẢO LUẬN

Chương này báo cáo các kết quả có được tại mốc đóng băng (11/2026), kể cả kết quả âm tính và kết quả kém đi. Các bảng do script sinh từ tệp kết quả đã khóa, nguồn ghi ngay dưới bảng. Trong các bảng chính, **số in đậm là giá trị tốt nhất trong cột** (hoặc trong nhóm hàng cùng loại), và **hàng nền xám là cấu hình đang dùng** trong hệ thống cuối; in đậm không có nghĩa là khác biệt có ý nghĩa thống kê. Bốn quy ước khi đọc số:

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

Theo luật chọn ghi trước, ensemble 3 seed của v2 (kiểm chứng chéo 0,2129 ± 0,0622) được commit trước khi mở test. Nó được chọn theo luật nhưng **không** được gọi là tốt hơn một lần chạy đơn, vì chênh 0,023 nhỏ hơn độ lệch chuẩn giữa các fold. Trên test `all`, ensemble v2 đạt event-F1 micro 0,1476 [0,1088; 0,1866] và macro 0,1369, so với 0,0941 và 0,0917 của v1; hiệu ghép cặp v2 − v1 là +0,0536 [+0,0261; +0,0853], khoảng tin cậy không chứa 0. Tuy vậy **PSDS không tăng**: PSDS-1 0,3447 so với 0,3489, PSDS-2 0,6744 so với 0,6987. Lợi ích của v2 nằm ở điểm vận hành đã chọn chứ không phải trên toàn dải ngưỡng; nguyên nhân được chẩn đoán trên tập dev ở phần "PSDS và lưới ngưỡng" bên dưới.

Về ghép sự kiện trên ba nhánh v1: từ dev sang test, event-F1 với ngưỡng riêng từng lớp giảm 48%, 39%, 41% (A, B, C), còn với ngưỡng chung chỉ giảm 15%, 4%, 2%, nên ngưỡng riêng từng lớp quá khớp dev một cách có hệ thống. Lọc trung vị không có tác động rõ (Δ +0,0063, +0,0026, −0,0014; đổi dấu giữa các nhánh).

### Vòng chọn S13 và hệ f2 (mốc so sánh)

Vòng chọn S13 gồm 11 ứng viên đã ghi trước (Chương 4); sau vòng này, giai đoạn O (phần tiếp theo) thay cách chọn. Các ứng viên được xếp hạng bằng kiểm chứng chéo trên dev `annotated`, và lựa chọn được commit trước khi sinh dự đoán test cho các ứng viên chưa từng chạm test (commit `c3f0033`). Hệ f2 (T2b×3 với cSEBB) đứng đầu với event-F1 micro 0,2383 ± 0,0562. Chênh lệch với f4 chỉ 0,0029, nhỏ hơn độ lệch chuẩn của f2, nên f2 được *chọn* theo luật nhưng không được gọi là *tốt hơn* f4 (⟪tbl:s13⟫).

@@CAP:tbl:s13|Xếp hạng 11 ứng viên trên dev và kết quả test annotated (một lần)@@

@@INCLUDE:docs/thesis/tables/06_s13_ranking_test.md|cols=1,2,4,5,6,7,8,9|best=5+,7+,8+|used=2:^f2$@@

Trên test `annotated`, f2 đạt event-F1 macro 0,1206 và micro 0,1643 [0,1103; 0,2242], PSDS-1 0,3164 và PSDS-2 0,7253. Thứ hạng test **không trùng** thứ hạng dev: f1 (BEATs đóng băng) chỉ đứng thứ 4 trên dev nhưng có micro test cao nhất (0,1817); g1 đứng thứ 6 trên dev nhưng có macro test cao nhất (0,1617). Hệ cuối **không** được chọn lại, vì chọn lại theo test chính là tinh chỉnh trên test. Hơn nữa, khoảng tin cậy test của các ứng viên đứng đầu đều chồng lấp. Đây là minh chứng trực tiếp cho sai số khi chọn mô hình trên tập dev nhỏ (134 bản ghi).

So với các thế hệ trước trên cùng tập test `annotated` (⟪tbl:progress⟫), f2 có micro cao hơn v1 (0,1643 so với 0,0945). So với v2, f2 có micro cao hơn (0,1643 so với 0,1500) nhưng **macro thấp hơn** (0,1206 so với 0,1389) và PSDS-1 thấp hơn (0,3164 so với 0,3458), với khoảng tin cậy micro chồng lấp. Vì vậy báo cáo **không** khẳng định f2 tốt hơn v2: f2 là hệ được khóa theo quy trình S13, không phải hệ được chứng minh là tốt nhất. Hệ này được giữ làm mốc so sánh cho hệ cuối.

@@CAP:tbl:progress|Tiến triển SED v1 → v2 → f2 trên test annotated@@

@@COLWIDTHS:23,10,11,11,19,13,13@@

@@INCLUDE:docs/thesis/tables/04_sed_progress.md|cols=1,2,3,4,5,6,7|best=3+,4+,6+,7+|used=1:S13@@

Phân tích theo lớp (Phụ lục C) cho thấy f2 còn rất yếu: 7/21 lớp có event-F1 bằng 0 trên test, trong đó có `vehicle_pass_by` (70 sự kiện tham chiếu), `birds` và `dog_barkings_and_howlings`. Các lớp tốt nhất là `cicadas_and_crickets` (0,4138), `music` (0,3750) và `workshop` (0,3636); lớp `cat_fights_and_moans` chỉ có 9 sự kiện tham chiếu nên báo là khớp 1/9. Hệ f2 chỉ dự đoán 295 sự kiện cho 740 sự kiện tham chiếu, và 349 lỗi là bỏ sót: hệ bị giới hạn chủ yếu bởi **recall**.

**Về cSEBB.** Ở v1, v2 và T2a, cSEBB đều thua ngưỡng chung trên kiểm chứng chéo dev (ví dụ ở v1: 0,0582 so với 0,1538). Hệ f2 là trường hợp đầu tiên cSEBB thắng: 0,2383 ± 0,0562 so với 0,2107 ± 0,0343 của ngưỡng chung, chênh lệch nằm trong biên dao động giữa các fold. Giả thuyết hợp lý là cSEBB phát huy khi xác suất có độ phân giải thật (T2b, 40 ms, không có tầng làm mượt thời gian), còn với mô hình có tầng hồi quy hoặc gộp thô thì thua. Kết luận về cSEBB vì vậy phải phát biểu có điều kiện, không thể nói chung là "tốt hơn" hay "kém hơn".

### Giai đoạn O: chọn bằng dự đoán ngoài mẫu và hệ B0

Sau S13, nhóm đổi cách chọn (Chương 4). Trên 564 bản ghi có nhãn của train và dev, cả ba ứng viên qua vòng sàng lọc trên dev đều đảo chiều khi đo ngoài mẫu (PAPER_NOTES S56), nghĩa là xếp hạng bằng kiểm chứng chéo trên 134 bản ghi dev không đáng tin. Hệ **B0** đạt event-F1 micro ngoài mẫu 0,2342 (macro 0,1797) và được mở test một lần: macro 0,1366, micro 0,1806 [0,1261; 0,2384], so với 0,1206 và 0,1643 của f2. Hiệu B0 − f2 về micro là +0,0164 [−0,0128; +0,0495]; khoảng tin cậy chứa 0 nên báo cáo **không** gọi B0 tốt hơn f2 có ý nghĩa. B0 được giữ vì là hệ chọn được theo luật ghi trước trên tiêu chí ngoài mẫu.

Giai đoạn P thử thêm bốn hướng tăng khả năng phát hiện: thêm seed, chưng cất tri thức, cửa sổ 20 s và tăng cường gain/EQ. Không hướng nào vượt B0 ở vòng ngoài mẫu: thêm hai seed cho hiệu micro +0,0002 [−0,0142; +0,0141]; tăng cường gain/EQ qua sàng lọc trên dev (0,2402) nhưng hiệu ngoài mẫu là −0,0082 [−0,0258; +0,0088], lần thứ tư một ứng viên đảo chiều giữa hai tầng chọn. Test không được mở trong giai đoạn này.

### LBR và hệ thống cuối

Phân tích lỗi của B0 (Chương 4) dẫn tới LBR. Trên dự đoán ngoài mẫu, V2 nâng event-F1 micro từ 0,2342 lên 0,3332, hiệu +0,0990 [+0,0761; +0,1200]. Test annotated chỉ được mở một lần cho các cấu hình đã khóa (⟪tbl:sedfinal⟫). V2 đạt macro 0,2356 và micro 0,2965 [0,2293; 0,3603]; hiệu micro so với B0 là +0,1159 [+0,0741; +0,1593], khoảng tin cậy không chứa 0. V3 ở điểm vận hành f1 cho micro 0,2731, hiệu +0,0925 [+0,0549; +0,1331]. **Hệ cuối của đề tài là B0 cộng LBR; V2 là số chính.**

@@CAP:tbl:sedfinal|SED trên test annotated: từ f2 đến LBR@@

@@COLWIDTHS:19,9,18,17,10,14,13@@

@@INCLUDE:report/final_tables/f01_sed.md|used=1:^LBR V2@@

⟪fig:sedfinal⟫ minh họa cùng số liệu: event-F1 micro tăng từ f2 và B0 lên LBR, trong khi thước giao nhau cho thấy hai điểm vận hành của LBR đánh đổi nhau.

![](report/final_figures/f01_sed_final.png){width=15cm}

@@CAP:fig:sedfinal|Event-F1 micro và thước giao nhau của các hệ SED trên test annotated@@

@@NOTE:Nguồn: docs/measurements/final_numbers_20261110.json; sinh bằng scripts/build_final_figures.py.@@

Có hai cách đọc ⟪tbl:sedfinal⟫ mà số liệu không cho phép bỏ qua. Thứ nhất, PSDS chỉ so được trong cùng một lưới ngưỡng (phần sau). Thứ hai, LBR đánh đổi độ phủ lấy độ chính xác của biên. ⟪tbl:sedapp⟫ báo thêm thước ứng dụng theo tiêu chí giao nhau của PSDS-2 (hộp dự đoán được tính đúng khi phần giao với sự kiện tham chiếu cùng lớp chiếm ít nhất 10% cả hai; ADR-0046) và F1 theo đoạn 1 s. V2 có recall giao nhau 0,5108, thấp hơn 0,5351 của B0 ở điểm vận hành đã khóa của B0, và F1 theo đoạn 0,5965 so với 0,7260; precision giao nhau 0,9545. V3 ở điểm `recall_first` (recall giao nhau tối đa với precision không dưới 0,6) dự đoán 668 sự kiện cho 740 sự kiện tham chiếu, đạt recall giao nhau 0,8203 và precision 0,7812, còn event-F1 micro 0,2287. Theo lớp (Phụ lục C), trong 20 lớp có từ 10 sự kiện tham chiếu trở lên, B0 có 6 lớp với event-F1 bằng 0 và LBR V2 có 3 lớp (`birds`, `vehicle_idling`, `vehicle_pass_by`; riêng `vehicle_pass_by` có 70 sự kiện tham chiếu); lớp tốt nhất của V2 là `workshop` (0,6992) và `cicadas_and_crickets` (0,5588). Tức là có hai điểm vận hành cho hai mục đích: V2 khi cần biên khớp chặt, V3 khi cần ít bỏ sót sự kiện. Demo dùng V3.

@@CAP:tbl:sedapp|Thước ứng dụng trên test annotated@@

@@INCLUDE:report/final_tables/f02_intersection.md@@

### PSDS và lưới ngưỡng

PSDS-1 và PSDS-2 là hai chỉ số theo dải ngưỡng nên phụ thuộc tập điểm vận hành. Lưới tuyến tính mặc định cắt phần lớn hộp của LBR (V2: 0,2146 / 0,2960), vì điểm của bộ chấm lại phân bố rất lệch. Với lưới log ghi trước, V2 đạt 0,3512 / 0,6116 và V3 đạt 0,3369 / 0,6167; B0 đo lại trên cùng lưới log đạt 0,3061 / 0,7452. Như vậy LBR có PSDS-1 cao hơn B0 nhưng PSDS-2 **thấp hơn rõ**, nhất quán với việc LBR đổi độ phủ lấy độ chính xác. Với hệ f2, 19 trên 48 điểm của lưới log bị bỏ vì vượt trần 50.000 sự kiện ghi trước (bộ nhớ của thư viện); nên PSDS lưới log của f2 không được báo.

Hiện tượng "event-F1 tăng nhưng PSDS không tăng" đã xuất hiện ở bước v1 sang v2. Nhóm chẩn đoán trên dev (134 bản ghi có nhãn) theo bốn giả thuyết ghi trước (ADR-0048): H1 do lưới ngưỡng, H2 do lợi ích chỉ nằm quanh điểm vận hành, H3 do phạt độ lệch giữa các lớp của PSDS (tham số `alpha_st`), H4 do tiêu chí giao nhau chặt. ⟪tbl:psdsdiag⟫ cho thấy hiện tượng được tái hiện trên dev: event-F1 micro tăng +0,0534 nhưng PSDS-2 giảm −0,0078. Đổi sang lưới log đưa hiệu PSDS-2 thành +0,0095 (H1 đủ điều kiện); đặt `alpha_st = 0` đưa hiệu về −0,0010 (H3 đủ điều kiện); H2 không được ủng hộ và H4 không áp dụng. Đây là phép đo in-sample trên dev, hiệu rất nhỏ và không có khoảng tin cậy, nên chỉ là gợi ý về nguyên nhân (lưới và độ lệch giữa các lớp), không phải kết luận.

@@CAP:tbl:psdsdiag|Chẩn đoán PSDS v1 sang v2 trên dev@@

@@INCLUDE:report/final_tables/f06_psds.md@@

## RQ2: mô tả có bám sát sự kiện không?

Phép so bốn cách sinh được lặp cho từng hệ SED trên test annotated (⟪tbl:rq2final⟫, mức đầu–cuối, n = 139). Mọi mô tả đều dùng danh sách sự kiện của hệ SED tương ứng; mọi tệp mô tả đều chạy hết, không có mô tả nào bị cắt. Có bốn kết quả.

@@CAP:tbl:rq2final|Bỏ sót và ảo giác theo cách sinh và hệ SED (test annotated, đầu–cuối)@@

@@COLWIDTHS:28,18,18,18,18@@

@@INCLUDE:report/final_tables/f04_rq2.md@@

**Thứ nhất,** cách template cho 0 ở mọi chỉ số, cả tiếng Anh lẫn tiếng Việt và cả bốn hệ SED; đây là kiểm chứng rằng bộ đo không báo lỗi giả trên mô tả tất định.

**Thứ hai,** viết tự do hiếm khi bịa nguồn âm nhưng hay thêm thứ không có trong bằng chứng. Tỷ lệ ảo giác của unconstrained là 0,011 (f2), 0,005 (B0), 0,016 (V2) và 0,022 (V3). Lỗi thật nằm ở bối cảnh (0,259 đến 0,403 số mô tả thêm bối cảnh không có trong bằng chứng) và gọi tên quá cụ thể (0,126 đến 0,140). Ràng buộc ngữ pháp (constrained và constrained-cover) đưa ảo giác, bối cảnh, gọi tên quá mức và từ cấm về 0 ở cả bốn hệ SED.

**Thứ ba,** cái giá của constrained là bỏ sót, và nó phụ thuộc độ dày của danh sách sự kiện. Bỏ sót là 0,012 (f2), 0,013 (B0), 0,007 (V2) nhưng 0,081 với V3; hiệu V3 − f2 là +0,069 [+0,041; +0,097]. Danh sách của V3 dày (668 sự kiện trên 139 bản ghi), trong khi constrained chỉ nhắc một dãy con các sự kiện nên bỏ sót lớp nhiều hơn khi danh sách dài; cách giải thích này khớp với số liệu nhưng chưa được kiểm bằng thí nghiệm kiểm soát. Unconstrained cũng bỏ sót nhiều hơn ở V3 (0,023 so với 0,005, hiệu +0,018 [+0,004; +0,034]). Cách constrained-cover giữ bỏ sót bằng 0 ở mọi hệ, theo cấu tạo của ngữ pháp, và không có chỉ số nào tệ hơn unconstrained.

**Thứ tư,** ở mức oracle (danh sách là nhãn gốc, dùng lại 139 mô tả đã sinh ở lượt trước, trùng khít 139/139), constrained bỏ sót 0,094 so với 0,019 của unconstrained; template và constrained-cover bằng 0. Hướng kết luận ở mức đầu–cuối vì vậy giữ nguyên khi đổi hệ SED.

Hai giới hạn khi đọc kết quả RQ2:

- **Bộ đo dựa trên từ điển.** Trên mẫu 60 mô tả test do **một** người đọc mù đối chiếu (với hệ trước đó), việc trích nguồn âm bằng từ điển đạt precision 0,896 và recall 0,936 so với người đọc. Từ điển dễ dãi hơn người ở một số chỗ: một kiểu bịa "tiếng búa gõ" bị che sau từ chỉ địa điểm "xưởng" mà từ điển không bắt được, và ở chỗ khác nó gắn cờ nhầm. Mẫu nhỏ và chỉ một người đọc, nên đây là kiểm tra sơ bộ.
- **"Không ảo giác" ở mức đầu–cuối không có nghĩa là mô tả đúng với âm thanh.** Mô tả trung thành với danh sách sự kiện *dự đoán*, mà hệ tốt nhất có event-F1 micro chỉ 0,2965 và bỏ sót phần lớn sự kiện tham chiếu (V2 dự đoán 373 trên 740). Ràng buộc bảo đảm mọi sai sót truy được về một sự kiện cụ thể của SED; nó không loại bỏ được sai sót đó.

Về độ tin cậy của lượt chạy: trong lúc sinh mô tả cho V3 trên dev, máy chủ llama.cpp gặp lỗi hết bộ nhớ GPU một lần; nhóm khởi động lại máy chủ và chạy tiếp, các tệp đã xong được giữ nguyên. Chuỗi yêu cầu sau khi khởi động lại khác chuỗi ban đầu, và vì llama.cpp chỉ tất định theo chuỗi yêu cầu, mô tả của các tệp chạy sau điểm này không chắc tái tạo được từng ký tự nếu chạy lại từ đầu. Sự việc được ghi ở ADR-0048.

## RQ3: truy hồi và câu trả lời có bằng chứng

⟪tbl:rq3final⟫ báo kết quả truy hồi trên test với bộ lọc chuẩn (gold) lấy từ bộ truy vấn, cho bốn kho sự kiện dựng từ dự đoán của f2, B0, LBR V2 và LBR V3 (V3 ở điểm `recall_first`). Cùng bộ 100 truy vấn dùng cho mọi kho, trong đó 97 câu có ít nhất một bản ghi liên quan.

@@CAP:tbl:rq3final|RQ3 trên test với bộ lọc gold: nDCG@10 và chất lượng câu trả lời@@

@@COLWIDTHS:12,17,17,17,11,13,13@@

@@INCLUDE:report/final_tables/f05_rq3.md@@

Với f2, B0 và V2, khoảng tin cậy chồng lấn mạnh: nDCG@10 của hybrid tiếng Anh là 0,415, 0,383 và 0,404; nhóm không phân biệt được ba hệ này. Điều này đáng lưu ý vì V2 tăng event-F1 micro khoảng 1,6 lần so với B0 (hiệu +0,1159) mà truy hồi gần như không đổi: truy hồi bị chặn bởi việc sự kiện nào được dự đoán chứ không phải bởi độ chính xác biên. Riêng LBR V3 cao hơn hẳn: hybrid 0,670 [0,610; 0,729], structured 0,683, và trả lời được 95/97 truy vấn so với 58 đến 65 của ba hệ kia. Đây là **hiệu ứng độ phủ**: V3 dự đoán nhiều sự kiện hơn nên bộ lọc cứng ít loại nhầm bản ghi thật sự liên quan. Cái giá thể hiện ở tỷ lệ trích dẫn trùng với bản ghi liên quan theo nhãn gốc: 0,712 với V3 so với 0,915 (B0), tức nhiều kết quả được trích hơn nhưng nhiều trong số đó không thật sự liên quan. Vì vậy mức tăng nDCG của V3 không phải bằng chứng xếp hạng tốt hơn.

Độ đúng bộ lọc của structured_only và hybrid là 1,000 như kiến trúc yêu cầu. Ở mọi cấu hình trả lời, tỷ lệ khẳng định thiếu bằng chứng là 0,000: câu trả lời không vượt ra ngoài những gì kho chứa; đổi lại, kho thiếu thì câu trả lời cũng thiếu. Bộ lọc gold giả định câu hỏi luôn được phân tích đúng nên chỉ là cận trên: với bộ lọc do bộ phân tích câu hỏi sinh ra (parsed), nDCG@10 của hybrid tiếng Anh là 0,409 (f2), 0,377 (B0), 0,398 (V2) và 0,655 (V3), thấp hơn gold từ 0,006 đến 0,015.

## Bộ phân tích câu hỏi và độ khớp khi phục vụ

Bộ phân tích câu hỏi cho đầu ra hợp lược đồ ở 240/240 câu (⟪tbl:parser⟫). Độ đúng ngữ nghĩa hoàn toàn đạt 0,855 trên 200 câu template và 0,925 trên 40 câu diễn đạt lại được khóa trước khi chạy. Lỗi chủ yếu nằm ở điều kiện thời gian: độ chính xác trên tập template chỉ 0,767, với các lỗi như đảo vai trò a/b, nhầm "within" thành "overlaps" hoặc bỏ ràng buộc thời lượng. Trên tập validation, hybrid với bộ lọc parsed thay đổi +0,012 (Anh) và −0,002 (Việt) so với gold; mức tăng dương này không phải bằng chứng bộ phân tích cải thiện truy hồi, vì bộ lọc sai cũng có thể tình cờ làm thứ hạng tốt lên.

@@CAP:tbl:parser|Đánh giá bộ phân tích câu hỏi thành bộ lọc@@

@@INCLUDE:docs/thesis/tables/10_parser_l2.md|cols=1,2,3,4,5,6,7@@

Hệ thống phục vụ cũng được kiểm xem có tái tạo đúng đầu ra đã đóng băng không, bằng cách so sự kiện (không chấm điểm lại trên test). Với B0, 351/352 sự kiện trùng khít trên GPU. Với LBR V3 `recall_first`, 573/692 sự kiện trùng khít, 665 lệch không quá một khung và 691 nằm trong collar 0,2 s; sai khác xác suất lớn nhất là 0,0020 và bộ tinh chỉnh khuếch đại nó thành dịch biên một khung. Khi chạy trong container CPU, phép tính số thực khác nên mức trùng còn thấp hơn; chênh lệch được định lượng ở các tệp đo của từng hệ.

## Thảo luận và hạn chế

Tóm lại, nhóm có một hệ thống đầu–cuối chạy được, cùng bằng chứng cho từng câu hỏi nghiên cứu. RQ1 âm tính với nhiều seed và hai công thức. RQ2 cho thấy ràng buộc ngữ pháp loại bỏ các dạng ảo giác và suy diễn đo được ở cả bốn hệ SED, với cái giá là bỏ sót khi danh sách sự kiện dày, mà biến thể cover giải quyết. RQ3 cho thấy bộ lọc cứng bảo đảm đúng ràng buộc tuyệt đối, và chất lượng xếp hạng bị chặn bởi việc SED dự đoán những sự kiện nào. Điểm tiến bộ lớn nhất của SED là LBR (event-F1 micro 0,1806 lên 0,2965), nhưng cái giá là PSDS-2 và độ phủ giảm. Các hạn chế chính:

- **Tập đánh giá nhỏ.** Dev có 137 (134 annotated) và test có 142 (139 annotated) bản ghi, nên khoảng tin cậy rộng. Bootstrap theo bản ghi chỉ phản ánh bất định do mẫu bản ghi, không phản ánh dao động giữa các seed.
- **Huấn luyện SED không tất định.** Cùng mã và cùng seed, F1 macro theo khung của nhánh B vẫn đổi từ 0,5850 sang 0,5705; mọi so sánh SED cần nhiều seed, trong khi các thử nghiệm bỏ-từng-phần của v2 chỉ có một seed.
- **LBR học trên dự đoán ngoài mẫu của chính tập dùng để chọn.** Kiểm tra chuyển giao trên ba seed khác và test mở một lần giảm rủi ro quá khớp, nhưng test chỉ có 139 bản ghi và LBR chưa được kiểm trên một bộ dữ liệu khác.
- **Giới hạn của nhãn.** Giới hạn người đo trên chỉ 8 cặp; collar 0,2 s chặt hơn độ chính xác của nhãn.
- **Micro và macro.** Việc chọn hệ thống vẫn dùng micro dù macro được báo trước; B0 so với f2 và V2 so với V3 có thể đổi thứ tự theo macro hay micro.
- **Sai lệch truy nguồn.** Sổ ghi test (Phụ lục B) cho thấy 10 trong 42 lượt đánh giá SED có cờ `dirty` (cây làm việc có tệp chưa commit do chính script sinh ra); mã và cấu hình không đổi và test không chạy lại, nhưng đây vẫn là hạn chế truy nguồn cần công khai. Các lượt của giai đoạn hoàn thiện đều chạy trên cây sạch.
- **Trùng nguồn với AudioSet** (mức trùng không định lượng được), **chưa có mốc so sánh công bố** trên DataSED và **bản DataSEC dùng chưa phải bản mới nhất** (bản 4 sửa lỗi số tệp của lớp Music).
- **PSDS phụ thuộc lưới ngưỡng**; một phần lưới của f2 bị bỏ vì trần bộ nhớ.
- **Bộ đo mô tả dựa trên từ điển**, chỉ đối chiếu với một người đọc trên 60 mô tả; một số tệp mô tả V3 trên dev sau lần khởi động lại máy chủ không tái tạo từng ký tự.
- **Kết quả RQ3 với bộ lọc gold** chỉ là cận trên về độ đúng bộ lọc; câu hỏi tổng quát kiểu "có những sự kiện gì trong âm thanh này?" chưa được bộ phân tích hỗ trợ.
- **Tra cứu văn liệu ở mức khóa luận**, không phải tổng quan hệ thống đầy đủ (Chương 2).
