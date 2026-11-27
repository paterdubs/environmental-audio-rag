# KẾT QUẢ VÀ THẢO LUẬN

Chương này báo cáo kết quả, kể cả kết quả âm tính và kết quả kém đi. Mọi bảng do script sinh từ tệp kết quả đã khóa. Cách đọc số:

- **Event-F1** tính bằng thư viện `sed_eval` [@mesaros2016metrics], dung sai 0,2 s; micro hay macro được ghi rõ.
- **Tập kiểm tra** gồm 139 bản ghi có nhãn, trừ khi ghi khác.
- **KTC 95%** là khoảng tin cậy bootstrap theo bản ghi (Chương 2).
- Trong bảng, **số in đậm** là giá trị tốt nhất của cột và **hàng nền xám** là cấu hình đang dùng; in đậm không có nghĩa là khác biệt có ý nghĩa thống kê.

⟪tbl:keyresults⟫ gom kết quả chính, mỗi câu hỏi một dòng. Các mục sau trình bày chi tiết.

@@CAP:tbl:keyresults|Kết quả chính theo câu hỏi nghiên cứu@@

@@COLWIDTHS:18,18,40,24@@

@@INCLUDE:report/final_tables/f00_key_results.md@@

## Mô hình phân loại DataSEC

Mô hình phân loại đạt macro-F1 0,8466 trên 22 lớp gộp của tập kiểm tra DataSEC, độ chính xác 0,9135 (676 trên 740 đoạn) (⟪tbl:classifier⟫). Ở cấp lớp con, macro-F1 trên 28 lớp chỉ là 0,6266 vì bị kéo xuống bởi các lớp con có rất ít mẫu; chỉ tính 5 lớp con có ít nhất 10 mẫu kiểm tra thì được 0,8453. Tỷ lệ nhất quán là 0,9526: 95% số lần, lớp con được đoán thuộc đúng lớp gộp được đoán. Hai lớp yếu nhất là `vehicle_idling` (F1 0,6154) và `vehicle_pass_by` (0,6538), hai loại âm thanh gần giống nhau. Hiệu chuẩn xác suất bằng nhiệt độ cho kết quả âm tính: sai số hiệu chuẩn ECE trên tập kiểm tra **tăng** từ 0,0332 lên 0,0564; nhóm báo đúng như vậy.

@@CAP:tbl:classifier|Kết quả mô hình phân loại DataSEC trên tập kiểm tra@@

@@INCLUDE:report/tables/m01_classifier.md@@

⟪tbl:clshistory⟫ đặt kết quả này cạnh các kết quả đã công bố trên các phiên bản dữ liệu khác nhau. Mục đích là cho thấy bối cảnh, không phải xếp hạng, vì ba điều kiện khác nhau: phiên bản dữ liệu, tập đo, và cách chia. Đề tài chia theo nhóm trùng sau khi kiểm rò rỉ; dự án trên bản 4 tự ghi rằng không chia được theo nguồn. Với cùng kiến trúc CNN14, kết quả trên bản 4 cao hơn đề tài khoảng 4,4 điểm phần trăm; nhóm chưa kiểm phần chênh này đến từ đâu.

@@CAP:tbl:clshistory|Kết quả phân loại đã công bố theo phiên bản dữ liệu (không so trực tiếp được)@@

@@COLWIDTHS:22,24,22,16,8,8@@

| Nguồn | Dữ liệu | Tập đo, cách chia | Mô hình | Độ chính xác | Macro-F1 |
|---|---|---|---|---:|---:|
| Artuso và cs., 2025 [@artuso2025clap] | Tiền thân của DataSEC, 21 lớp | Tập kiểm định | CLAP + lớp tuyến tính | 91,83% | — |
| Khóa luận | DataSEC bản 3, 5.048 tệp, 22 lớp | Tập kiểm tra 740 đoạn; chia theo nhóm trùng | PANNs CNN14 | 91,35% | 84,66% |
| Dự án GitHub, 11/2026 [@goyumsamuditha2026datasec] | DataSEC bản 4, 4.292 tệp, 22 lớp | Tập kiểm tra 654 đoạn; không chia theo nguồn | PANNs CNN14 | 95,72% | 92,03% |
| | | | CLAP + lớp tuyến tính | 97,09% | 95,34% |

@@NOTE:Nguồn: Artuso và cs. (2025), đọc trực tiếp; README của dự án GitHub, đọc trực tiếp ngày 23/11/2026; số của khóa luận từ per_class_metrics_datasec_20260923. Dự án GitHub không qua bình duyệt.@@

## RQ1: huấn luyện thêm trên DataSEC có giúp không?

Vì huấn luyện SED không cho kết quả giống hệt nhau giữa các lần chạy, câu trả lời dựa trên nhiều lần chạy (⟪tbl:rq1⟫). Với SED v1 (3 lần chạy nhánh B, 4 lần chạy nhánh C, chấm trên 142 bản ghi), event-F1 micro trung bình của B là 0,0610 và của C là 0,0539; hiệu C − B là −0,0071 [−0,0164; +0,0021]. Với SED v2 (3 lần chạy mỗi nhánh), hiệu là −0,0029 [−0,0254; +0,0199]. Cả hai khoảng tin cậy đều chứa 0. Dao động giữa các seed lớn ngang hoặc lớn hơn hiệu giữa hai nhánh: ở SED v1, kết quả của nhánh C trải từ 0,0472 đến 0,0660 qua 4 seed, phủ trọn khoảng của nhánh B (0,0557 đến 0,0651).

@@CAP:tbl:rq1|Kết quả RQ1 trên tập kiểm tra@@

@@INCLUDE:docs/thesis/tables/03_rq1.md@@

Ngược lại, tiền huấn luyện nói chung giúp rõ: nhánh A học từ đầu chỉ đạt event-F1 0,0360, so với 0,0621 của nhánh B. Riêng PSDS-2 của SED v2 tăng +0,0279 (p = 0,0193), nhưng đây là một trong nhiều chỉ số được so và chưa hiệu chỉnh cho việc so nhiều lần.

**Kết luận RQ1:** nhóm **không** có bằng chứng rằng huấn luyện thêm trên DataSEC cải thiện event-F1 so với chỉ dùng AudioSet. Kết quả âm tính này không loại trừ một lợi ích nhỏ hơn cận trên của khoảng tin cậy (+0,0021 với SED v1, +0,0199 với SED v2).

## Các thế hệ SED

⟪fig:journey⟫ tóm tắt năm thế hệ SED trên cùng tập kiểm tra, kèm điểm mà mỗi thế hệ dùng khi được chọn. Phần dưới giải thích từng bước.

![](report/gon_figures/r04_sed_journey.png){width=15cm}

@@CAP:fig:journey|Event-F1 của các thế hệ SED trên tập kiểm tra, và điểm dùng để chọn@@

@@NOTE:Nguồn: s13_test_20261018.json, final_numbers_20261110.json, lbr_context_20261123.json, calibration_20261123.json.@@

**SED v1: vì sao event-F1 thấp?** Chẩn đoán trên tập phát triển cho thấy hai nguyên nhân. Thứ nhất, CNN14 ra quyết định theo khối 0,64 s, nên kể cả nhận dạng hoàn hảo thì event-F1 tối đa chỉ là 0,6294. Thứ hai, phần lớn lỗi nằm ở biên và ở bỏ sót: trong 886 sự kiện tham chiếu, chỉ 112 khớp dung sai, 417 đúng lớp nhưng lệch biên, và 357 bị bỏ sót. Nới dung sai từ 0,2 s lên 1 s làm event-F1 của nhánh B tăng khoảng ba lần (0,062 lên 0,185), phù hợp với chẩn đoán này.

**SED v2.** Sửa độ phân giải thời gian là thay đổi có tác dụng rõ nhất: quay về nén 64 lần làm event-F1 giảm 0,0840. Gộp 3 seed của SED v2 đạt event-F1 micro 0,1476 trên 142 bản ghi kiểm tra, so với 0,0941 của SED v1; hiệu +0,0536 [+0,0261; +0,0853]. Cũng ở bước này, nhóm thấy ngưỡng riêng cho từng lớp bị quá khớp tập phát triển: từ tập phát triển sang tập kiểm tra, event-F1 với ngưỡng riêng giảm 39% đến 48%, còn với ngưỡng chung chỉ giảm 2% đến 15%.

**Hệ mốc.** Vòng chọn tiếp theo so 11 ứng viên bằng kiểm chứng chéo trên tập phát triển và khóa hệ mốc (event-F1 micro kiểm chứng chéo 0,2383 ± 0,0562). Trên tập kiểm tra, hệ mốc đạt micro 0,1643 [0,1103; 0,2242]. Thứ hạng trên tập kiểm tra không trùng thứ hạng trên tập phát triển: một ứng viên chỉ đứng thứ tư trên tập phát triển lại có micro kiểm tra cao nhất (0,1817). Hệ mốc **không** được chọn lại, vì chọn lại theo tập kiểm tra chính là tinh chỉnh trên tập kiểm tra. Bảng xếp hạng đầy đủ ở Phụ lục B. Ở hệ mốc, cSEBB tốt hơn ngưỡng chung (0,2383 so với 0,2107), trong khi với các thế hệ trước nó thua; kết luận về cSEBB vì vậy phụ thuộc vào mô hình.

**Hệ cơ sở.** Do thứ hạng trên tập phát triển không đáng tin, nhóm chuyển sang chọn trên dự đoán ngoài mẫu của 564 bản ghi (Chương 4). Hệ cơ sở đạt event-F1 micro ngoài mẫu 0,2342. Trên tập kiểm tra, hệ cơ sở đạt micro 0,1806 [0,1261; 0,2384], so với 0,1643 của hệ mốc; hiệu +0,0164 [−0,0128; +0,0495] chứa 0, nên báo cáo **không** gọi hệ cơ sở tốt hơn hệ mốc.

## LBR và hệ thống cuối

Trên dự đoán ngoài mẫu, LBR chính nâng event-F1 micro từ 0,2342 lên 0,3332, hiệu +0,0990 [+0,0761; +0,1200]. ⟪tbl:lbrcontext⟫ đặt kết quả này cạnh các cách đơn giản hơn: ngưỡng riêng từng lớp cho 0,2335 và dịch thời điểm bắt đầu đồng loạt cho 0,2469, đều thấp hơn hẳn LBR. Nếu sửa được biên của mọi hộp khớp trong phạm vi ±1 s thì micro đạt 0,4641; LBR chính đi được khoảng 43% quãng đường từ hệ cơ sở tới mức đó. Khi học trên dự đoán của một mô hình rồi áp lên gộp 3 seed, LBR vẫn tăng +0,1160, nên mức tăng không phụ thuộc vào đúng mô hình dùng để học.

@@CAP:tbl:lbrcontext|LBR so với các cách đơn giản hơn, trên dự đoán ngoài mẫu (564 bản ghi)@@

@@COLWIDTHS:38,12,12,38@@

@@INCLUDE:report/final_tables/f10_lbr_context.md@@

Tập kiểm tra được mở một lần cho các cấu hình đã khóa (⟪tbl:sedfinal⟫). LBR chính đạt event-F1 macro 0,2356 và micro 0,2965 [0,2293; 0,3603]. Hiệu micro so với hệ cơ sở là +0,1159 [+0,0741; +0,1593]; khoảng tin cậy không chứa 0 và cùng hướng với kết quả ngoài mẫu. **Hệ thống cuối của đề tài là hệ cơ sở cộng LBR; LBR chính là số chính.**

@@CAP:tbl:sedfinal|SED trên tập kiểm tra: từ hệ mốc đến LBR@@

@@COLWIDTHS:21,9,18,17,10,13,12@@

@@INCLUDE:report/final_tables/f01_sed.md|used=1:^LBR V2@@

LBR có đánh đổi (⟪fig:sedfinal⟫). Theo tiêu chí giao nhau (hộp dự đoán được tính đúng khi chồng lên sự kiện tham chiếu cùng lớp một phần đủ lớn), LBR chính có recall 0,5108 so với 0,5351 của hệ cơ sở, và F1 theo đoạn giảm từ 0,7260 xuống 0,5965. LBR ứng dụng đổi hướng ngược lại: dự đoán 668 sự kiện cho 740 sự kiện tham chiếu, đạt recall theo giao nhau 0,8203 và precision 0,7812, nhưng event-F1 micro chỉ 0,2287. Tức là có hai cấu hình cho hai mục đích: LBR chính khi cần biên khớp chặt, LBR ứng dụng khi cần ít bỏ sót. Demo dùng LBR ứng dụng.

![](report/gon_figures/f01_sed_final.png){width=15cm}

@@CAP:fig:sedfinal|Event-F1 micro và chỉ số theo giao nhau của các hệ SED trên tập kiểm tra@@

@@NOTE:Nguồn: final_numbers_20261110.json.@@

⟪fig:perclass⟫ so event-F1 theo lớp của hệ cơ sở và LBR chính cho 20 lớp có ít nhất 10 sự kiện tham chiếu. LBR tăng ở 15 lớp, giảm ở 2 lớp (`music` và `propeller_aircrafts`), và 3 lớp đứng yên ở 0. Mức tăng lớn nhất nằm ở các lớp kéo dài có biên đầu bị đoán sớm: `vacuum_cleaner_fan_hairdryer`, `cicadas_and_crickets` và `workshop` tăng 0,24 đến 0,26. Ba lớp đứng ở 0 cho thấy giới hạn của LBR: nếu mô hình gốc không sinh hộp đúng lớp thì không có gì để tinh chỉnh.

![](report/gon_figures/r07_per_class.png){width=13.5cm}

@@CAP:fig:perclass|Event-F1 theo lớp của hệ cơ sở và LBR chính trên tập kiểm tra (lớp có ít nhất 10 sự kiện)@@

@@NOTE:Nguồn: tệp đánh giá đã lưu của hệ cơ sở và của LBR (đọc lại, không tính lại).@@

Trên **19 lớp** của bối cảnh đô thị Việt Nam (Chương 1), event-F1 micro của hệ cơ sở là 0,1892 và của LBR chính là 0,3120; LBR ứng dụng có recall theo giao nhau 0,8319 với precision 0,7810. Đây chỉ là phép lọc lớp trên DataSED, không phải dữ liệu thu tại Việt Nam.

**PSDS.** PSDS tính trên một dải ngưỡng nên phụ thuộc cách chọn dải. Trên cùng dải ngưỡng log, LBR chính đạt PSDS-1 0,3512 và PSDS-2 0,6116, còn hệ cơ sở đạt 0,3061 và 0,7452. Như vậy LBR tăng PSDS-1 nhưng **giảm rõ** PSDS-2, nhất quán với việc LBR đổi độ phủ lấy độ chính xác của biên. Chẩn đoán chi tiết về PSDS ở Phụ lục B.

## Event-F1 khoảng 0,30 là cao hay thấp?

Một con số event-F1 đứng riêng khó đọc, nên báo cáo đặt nó cạnh hai mốc tham chiếu. Cả hai chỉ để hình dung độ lớn, không phải bảng xếp hạng.

**Mốc thứ nhất: độ đồng thuận giữa hai lần gán nhãn trên chính DataSED** (⟪tbl:calibration⟫). Trên 8 cặp bản ghi được gán nhãn hai lần, event-F1 giữa hai lần gán là 0,5785 với dung sai 0,2 s và 0,7425 với F1 theo đoạn 1 s. LBR chính đạt 0,2965, khoảng 51% mức đồng thuận; còn theo đoạn 1 s, hệ cơ sở đạt 0,7260, khoảng 98%. Nói cách khác, nhận dạng *có hay không trong từng giây* đã gần mức đồng thuận, còn **định vị biên chính xác** vẫn là nút thắt. Đây không phải khẳng định "ngang người": mẫu chỉ có 8 cặp và hai bên đo trên các bản ghi khác nhau.

@@CAP:tbl:calibration|Event-F1 theo bốn cách đo, cạnh độ đồng thuận giữa hai lần gán nhãn@@

@@COLWIDTHS:34,16,16,16,18@@

@@INCLUDE:report/final_tables/f11_calibration.md@@

**Mốc thứ hai: thử thách DCASE** (⟪tbl:dcase⟫). Với DESED, PSDS của các hệ cơ sở DCASE cùng cỡ với PSDS của đề tài. Tuy nhiên DESED là đoạn 10 s, 10 lớp, phần lớn là dữ liệu tổng hợp; DataSED là bản ghi trung bình 94 s, 21 lớp và chỉ có 564 bản ghi có nhãn để huấn luyện. Nhóm không viết "tương đương DESED".

@@CAP:tbl:dcase|Các mốc công bố dùng để hình dung độ khó (không so trực tiếp được)@@

@@COLWIDTHS:30,22,48@@

| Bối cảnh | Chỉ số | Mốc công bố |
|---|---|---|
| DCASE 2016 nhiệm vụ 3, ghi âm đời thực [@dcase2016task3] | Event-F1, chỉ xét thời điểm bắt đầu | 1,5% đến 8,1% trên 16 hệ; hệ cơ sở 6,3% |
| DCASE 2022 nhiệm vụ 4, DESED [@dcase2022task4] | PSDS-1 / PSDS-2 | Hệ cơ sở 0,315 / 0,543 |
| DCASE 2023 nhiệm vụ 4A, DESED [@dcase2023task4a] | PSDS-1 / PSDS-2 | Hệ cơ sở 0,327 / 0,538; hệ cơ sở có BEATs 0,510 / 0,798 |
| DCASE 2023 nhiệm vụ 4B, MAESTRO Real [@dcase2023task4b] | F1 micro / macro | Hệ cơ sở 74,13 / 35,28 |
| Khóa luận (tập kiểm tra, 21 lớp) | Event-F1 micro / macro; PSDS-1 / PSDS-2 | 0,2965 / 0,2356 (LBR chính); 0,3061 đến 0,3512 / 0,6116 đến 0,7452 |

@@NOTE:Nguồn: trang kết quả DCASE 2016, 2022 và 2023, đọc trực tiếp ngày 23/11/2026; số của khóa luận từ final_numbers_20261110.json.@@

## RQ2: mô tả có bám sát sự kiện không?

Bốn cách sinh được so trên cùng danh sách sự kiện của từng hệ SED, trên 139 bản ghi kiểm tra (⟪tbl:rq2final⟫). Có ba kết quả.

@@CAP:tbl:rq2final|Bỏ sót và ảo giác theo cách sinh và hệ SED (tập kiểm tra, so với danh sách sự kiện dự đoán)@@

@@COLWIDTHS:28,18,18,18,18@@

@@INCLUDE:report/final_tables/f04_rq2.md@@

**Thứ nhất, cách theo mẫu cho 0 ở mọi chỉ số**, cả tiếng Anh lẫn tiếng Việt, trên cả bốn hệ SED. Đây là bằng chứng bộ đo không báo lỗi giả trên mô tả đúng.

**Thứ hai, viết tự do hiếm khi bịa nguồn âm, nhưng hay thêm điều không có trong bằng chứng.** Tỷ lệ ảo giác nguồn âm của cách tự do chỉ từ 0,005 đến 0,022. Lỗi chính nằm ở chỗ thêm bối cảnh (0,259 đến 0,403 số mô tả) và gọi tên quá cụ thể (0,126 đến 0,140). Hai cách có ràng buộc đưa ảo giác, bối cảnh, gọi tên quá cụ thể và từ cấm về 0 ở cả bốn hệ SED.

**Thứ ba, cái giá của ràng buộc là bỏ sót, và nó tăng khi danh sách sự kiện dày.** Cách ràng buộc bỏ sót 0,012 (hệ mốc), 0,013 (hệ cơ sở), 0,007 (LBR chính) nhưng 0,081 với LBR ứng dụng; hiệu so với hệ mốc là +0,069 [+0,041; +0,097]. Danh sách của LBR ứng dụng dày (668 sự kiện trên 139 bản ghi), trong khi cách ràng buộc chỉ nhắc một phần sự kiện. Cách ràng buộc + phủ giữ bỏ sót bằng 0 ở mọi hệ, và không có chỉ số nào kém hơn cách tự do.

Cần đọc RQ2 đúng mức. Kết quả "0 vi phạm" của hai cách có ràng buộc là hệ quả của cấu tạo ngữ pháp, nên thông tin thật nằm ở cái giá (bỏ sót) và ở mức lệch của cách viết tự do. Câu của cách ràng buộc cũng gần như câu theo mẫu: so với câu theo mẫu, nó đạt BLEU-4 0,358 và CIDEr 3,60, còn cách tự do chỉ 0,015 và 0,116. Vì cách theo mẫu đạt 0 ở mọi chỉ số và không tốn tính toán, giao diện dùng mô tả theo mẫu.

**Mô tả so với nhãn gốc.** "Không ảo giác so với danh sách dự đoán" chưa có nghĩa là mô tả đúng với âm thanh. Để tách hai loại lỗi, nhóm chấm lại chính các mô tả đã sinh trên tập phát triển, lần này so với nhãn gốc (⟪tbl:captiontiers⟫). Phép đo này không gọi lại mô hình ngôn ngữ và không dùng tập kiểm tra.

@@CAP:tbl:captiontiers|Ảo giác và bỏ sót: so với danh sách dự đoán / so với nhãn gốc (tập phát triển)@@

@@COLWIDTHS:18,32,25,25@@

@@INCLUDE:report/final_tables/f04b_caption_tiers.md@@

Kết quả cho thấy ba điều. **Một,** so với nhãn gốc, mọi cách sinh đều bỏ sót khoảng 34% đến 42% số lớp có thật ở hệ mốc, hệ cơ sở và LBR chính, kể cả hai cách vốn bằng 0 khi so với dự đoán. **Hai,** chênh lệch giữa các cách sinh nhỏ hơn nhiều so với chênh lệch giữa các hệ SED: trong cùng một hệ, ảo giác so với nhãn gốc của bốn cách sinh lệch nhau nhiều nhất 0,056, còn cùng một cách sinh lệch 0,16 đến 0,20 khi đổi từ LBR chính sang LBR ứng dụng. **Ba,** vì vậy độ đúng của mô tả với âm thanh chủ yếu do SED quyết định; phần của bộ sinh là không tự thêm nguồn âm ngoài danh sách.

**Mô tả gộp theo lớp.** Với LBR ứng dụng, mô tả theo mẫu dài trung bình 400 ký tự trên tập phát triển; mô tả gộp theo lớp còn trung bình 119 ký tự, và vẫn không có ảo giác hay bỏ sót so với danh sách sự kiện. Nhãn "độ tin cậy thấp" mang thông tin: ở LBR ứng dụng, mệnh đề có nhãn này chỉ đúng với nhãn gốc 17/98 lần, còn mệnh đề không có nhãn đúng 202/228 lần. Ngưỡng của nhãn được chọn trên chính tập phát triển này, nên đây là phép đo trong mẫu.

**Giới hạn của bộ đo.** Bộ đo tìm nguồn âm bằng từ điển cụm từ. Trên 60 mô tả được một người đọc đối chiếu, từ điển đạt precision 0,896 và recall 0,936 so với người đọc. Nhóm cũng cố tình chèn nguồn âm sai vào mô tả để đo độ nhạy, theo ý tưởng của BRACE [@guo2025brace]: khi nguồn âm sai thuộc 21 lớp, bộ đo bắt được gần như mọi ca (1859/1860); khi nguồn âm nằm ngoài hệ lớp, chỉ 62% bị bắt (ví dụ "a hammer striking" không bị bắt). Vì vậy tỷ lệ ảo giác của cách viết tự do là **cận dưới**: nguồn âm lạ có thể lọt qua bộ đo.

## RQ3: truy hồi và câu trả lời có bằng chứng

⟪tbl:rq3final⟫ báo kết quả truy hồi trên tập kiểm tra với bộ lọc chuẩn (lấy đúng từ bộ câu hỏi), cho bốn kho sự kiện dựng từ dự đoán của bốn hệ SED.

@@CAP:tbl:rq3final|RQ3 trên tập kiểm tra: nDCG@10 và chất lượng câu trả lời@@

@@COLWIDTHS:14,16,16,16,11,14,13@@

@@INCLUDE:report/final_tables/f05_rq3.md@@

Với hệ mốc, hệ cơ sở và LBR chính, nDCG@10 của chế độ kết hợp là 0,415, 0,383 và 0,404, khoảng tin cậy chồng nhau nhiều. Điều này đáng chú ý: LBR chính tăng event-F1 micro khoảng 1,6 lần so với hệ cơ sở, nhưng truy hồi gần như không đổi. Truy hồi phụ thuộc vào việc *sự kiện nào* được dự đoán, không phải vào độ chính xác của biên. Riêng kho của LBR ứng dụng cao hơn hẳn (0,670) và trả lời được 95/97 câu hỏi, so với 58 đến 65 của ba kho kia. Đây là **hiệu ứng độ phủ**: LBR ứng dụng dự đoán nhiều sự kiện hơn, nên bộ lọc ít loại nhầm bản ghi liên quan. Cái giá là tỷ lệ trích dẫn đúng thấp hơn (0,712 so với 0,915 của hệ cơ sở).

**Kết hợp có tốt hơn từng thành phần không?** Đây là câu hỏi gốc của RQ3, và câu trả lời trên dữ liệu này là **không, xét theo nDCG@10** (⟪tbl:rq3paired⟫). Với ba kho có độ phủ thấp, chế độ kết hợp thấp hơn chế độ chỉ ngữ nghĩa: −0,111, −0,075 và −0,087, khoảng tin cậy không chứa 0. Riêng kho của LBR ứng dụng, chiều này đảo lại (+0,040). Chế độ kết hợp gần như trùng chế độ chỉ lọc (mọi hiệu không quá 0,013).

@@CAP:tbl:rq3paired|Hiệu nDCG@10 ghép cặp giữa các chế độ và độ đúng bộ lọc (tập kiểm tra)@@

@@COLWIDTHS:16,24,22,19,19@@

@@INCLUDE:report/final_tables/f05b_rq3_paired.md@@

Ba điều cần đọc cùng nhau. **Một,** chế độ chỉ ngữ nghĩa không tôn trọng điều kiện: chỉ khoảng 27% kết quả của nó thỏa bộ lọc, so với 1,000 của chế độ kết hợp. nDCG cao hơn của nó không có nghĩa là nó đáp ứng câu hỏi có điều kiện tốt hơn. **Hai,** chênh lệch tập trung ở câu hỏi nhiều lớp và câu hỏi quan hệ thời gian (⟪tbl:rq3groups⟫); ví dụ ở kho hệ mốc, nhóm quan hệ thời gian đạt 0,126 với chế độ kết hợp so với 0,426 với chế độ chỉ ngữ nghĩa. **Ba,** nguyên nhân hợp lý nhất là bộ lọc chạy trên sự kiện *dự đoán*: chỉ bản ghi mà SED đã dự đoán đủ mọi lớp và quan hệ trong câu hỏi mới qua được bộ lọc. Đếm trực tiếp trên kho của hệ cơ sở: trong 705 cặp (câu hỏi, bản ghi liên quan), 349 cặp bị loại vì sự kiện dự đoán không thỏa bộ lọc. Bộ phân tích câu hỏi chỉ làm đổi kết quả ở 4 đến 12 trên 97 câu hỏi, nhỏ hơn nhiều so với phần do SED.

@@CAP:tbl:rq3groups|nDCG@10 kết hợp / chỉ ngữ nghĩa theo nhóm câu hỏi (tập kiểm tra)@@

@@COLWIDTHS:16,21,21,21,21@@

@@INCLUDE:report/final_tables/f05c_rq3_groups.md@@

### Chế độ bổ sung

Phân tích trên cho thấy chế độ kết hợp thua không phải vì xếp sai, mà vì trả quá ít kết quả: ở kho hệ mốc, 32/97 câu hỏi có danh sách kết hợp rỗng. Cần nói rõ đây là quan sát trên tập kiểm tra. Từ đó nhóm thử chế độ bổ sung (Chương 4): giữ nguyên danh sách kết hợp, rồi lấp chỗ trống bằng kết quả chỉ ngữ nghĩa. Chế độ này không có tham số để chỉnh; định nghĩa được ghi trước, kiểm trên tập phát triển, rồi đo trên tập kiểm tra một lần. Văn liệu về truy hồi lai cũng cho thấy cách trộn hai nguồn xếp hạng tốt nhất phụ thuộc dữ liệu [@bruch2023fusion].

![](report/gon_figures/r13_rq3_backfill.png){width=14cm}

@@CAP:fig:rq3backfill|nDCG@10 của ba chế độ trên tập kiểm tra; số trên cột cam là tỷ lệ kết quả của chế độ bổ sung thỏa bộ lọc@@

@@NOTE:Nguồn: retrieval_backfill_test_20261124.json (bộ lọc chuẩn, tiếng Anh).@@

⟪fig:rq3backfill⟫ cho thấy chế độ bổ sung cao hơn cả hai chế độ gốc ở cả bốn kho, và mọi khoảng tin cậy ghép cặp đều không chứa 0. So với chỉ ngữ nghĩa, mức tăng là +0,041 đến +0,097; so với kết hợp là +0,057 đến +0,160. Câu hỏi tiếng Việt và bộ lọc do bộ phân tích sinh ra cho cùng chiều. Cái giá là chỉ 29% đến 31% kết quả thỏa bộ lọc ở ba kho độ phủ thấp (57% ở kho LBR ứng dụng); phần còn lại là gợi ý gần nghĩa. Vì vậy ứng dụng tách bạch hai phần: câu trả lời chỉ khẳng định trên phần thỏa bộ lọc, phần gần nghĩa chỉ hiện như gợi ý.

**Câu trả lời.** Ở mọi cấu hình, tỷ lệ khẳng định thiếu bằng chứng là 0,000: câu trả lời không vượt ra ngoài những gì kho chứa; đổi lại, kho thiếu thì câu trả lời cũng thiếu. Độ đúng bộ lọc 1,000 chỉ cho biết kết quả nhất quán với bộ lọc và với sự kiện *dự đoán* trong kho, không cho biết kết quả đúng với ý người hỏi hay với âm thanh.

### Bộ phân tích câu hỏi

Bộ phân tích cho đầu ra đúng lược đồ ở 240/240 câu (⟪tbl:parser⟫). Độ đúng hoàn toàn là 0,855 trên 200 câu theo mẫu và 0,925 trên 40 câu diễn đạt lại. Lỗi chủ yếu nằm ở điều kiện thời gian: độ đúng chỉ 0,767, với các lỗi như đảo vai trò a và b, nhầm "within" thành "overlaps" hoặc bỏ ràng buộc thời lượng. Với bộ lọc do bộ phân tích sinh ra, nDCG@10 của chế độ kết hợp thấp hơn bộ lọc chuẩn từ 0,006 đến 0,015 trên tập kiểm tra. Đây là nguồn lỗi nằm ngoài SED, và là lý do giao diện cho người dùng sửa thẻ bộ lọc.

@@CAP:tbl:parser|Đánh giá bộ phân tích câu hỏi@@

@@INCLUDE:docs/thesis/tables/10_parser_l2.md|cols=1,2,3,4,5,6,7@@

## Mức tin cậy của các so sánh

Tập kiểm tra không được dùng "một lần" theo nghĩa đen: sổ ghi có **42 lượt đánh giá SED trên tập kiểm tra**, cùng các lượt đo mô tả và truy hồi. Điều nhóm bảo đảm hẹp hơn: mỗi cấu hình đã khóa chỉ được đo trên tập kiểm tra **một lần**, lựa chọn được lưu trước khi sinh dự đoán kiểm tra, và không cấu hình nào được chọn lại sau khi xem kết quả. Ba điểm cần nói thẳng:

- **Thứ hạng trên tập phát triển dự báo kém thứ hạng trên tập kiểm tra.** Ở vòng chọn hệ mốc, tương quan hạng Spearman giữa hai tập là ρ = 0,62. Đây là lý do nhóm chuyển sang chọn trên dự đoán ngoài mẫu. Với LBR chính, hiệu ngoài mẫu (+0,0990) và hiệu trên tập kiểm tra (+0,1159) cùng hướng; sự nhất quán này là bằng chứng chống quá khớp mạnh hơn bất kỳ lượt đo đơn lẻ nào.
- **Có những chỗ tập kiểm tra gợi ý hướng thử.** Thiết kế của LBR được thăm dò trên chính dữ liệu ngoài mẫu dùng để chọn; ý tưởng chế độ bổ sung đến từ phân tích lỗi trên tập kiểm tra. Ở cả hai trường hợp, cấu hình được khóa trước rồi mới đo trên tập kiểm tra một lần, nhưng hướng thử vẫn do kết quả trước đó gợi ý.
- **Khoảng tin cậy không hiệu chỉnh cho việc so nhiều lần.** So sánh chính của phần SED (LBR chính so với hệ cơ sở) được định trước, có khoảng tin cậy không chứa 0 và cùng hướng với kết quả ngoài mẫu. Các so sánh phụ không nên đọc như kết luận.

## Thảo luận

Các kết quả quy về một kết luận: **độ đúng của mô tả và câu trả lời phụ thuộc chủ yếu vào bước phát hiện sự kiện.** Bộ sinh có ràng buộc không tự thêm nguồn âm ngoài danh sách sự kiện (RQ2), và bộ lọc cứng chỉ trả bản ghi thỏa điều kiện trên sự kiện đã lưu (RQ3). Khi so với âm thanh thật, lỗi còn lại chủ yếu đến từ SED. Hai bộ phận khác có lỗi riêng đã được đo: bộ phân tích câu hỏi (đúng hoàn toàn 0,855) và bộ đo ảo giác (chỉ bắt 62% nguồn âm ngoài hệ lớp).

Có một điểm căng cần nói cùng lúc. LBR cải thiện event-F1 rõ, nhưng không cải thiện truy hồi (0,383 với hệ cơ sở so với 0,404 với LBR chính, khoảng tin cậy chồng nhau) và làm F1 theo đoạn giảm từ 0,7260 xuống 0,5965. Truy hồi chỉ tăng khi **độ phủ** sự kiện tăng: ở kho LBR ứng dụng và ở chế độ bổ sung. Hướng cải tiến có tác dụng vì vậy nằm ở hai chỗ: SED tốt hơn, và độ phủ sự kiện khi truy hồi. Các hạn chế được tổng hợp ở Chương 7.
