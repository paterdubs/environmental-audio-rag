# KẾT QUẢ VÀ THẢO LUẬN

Chương này báo cáo kết quả, kể cả kết quả âm tính và kết quả kém đi. Mọi bảng do script sinh từ tệp kết quả đã khóa. Cách đọc số:

- **F1 theo sự kiện** tính bằng thư viện `sed_eval` [@mesaros2016metrics], dung sai 0,2 s; micro hay macro được ghi rõ.
- **Tập kiểm tra** gồm 139 bản ghi có nhãn, trừ khi ghi khác.
- **KTC 95%** là khoảng tin cậy 95% bootstrap ghép cặp theo bản ghi (mục 2.2.8).
- Trong bảng, **số in đậm** là giá trị tốt nhất của cột và **hàng nền xám** là cấu hình đang dùng; in đậm không có nghĩa là khác biệt có ý nghĩa thống kê.

⟪tbl:keyresults⟫ gom kết quả chính, mỗi câu hỏi nghiên cứu một dòng. Các mục sau trình bày chi tiết.

@@CAP:tbl:keyresults|Kết quả chính theo câu hỏi nghiên cứu@@

@@COLWIDTHS:18,18,40,24@@

@@INCLUDE:report/final_tables/f00_key_results.md@@

## Mô hình phân loại DataSEC

Mô hình phân loại đạt macro-F1 0,8466 trên 22 lớp cấp trên của tập kiểm tra DataSEC, tỷ lệ phân loại đúng 0,9135 (676 trên 740 đoạn) (⟪tbl:classifier⟫; F1 từng lớp ở ⟪tbl:classperclass⟫, Phụ lục B). Ở cấp lớp con, macro-F1 trên 28 lớp chỉ là 0,6266 vì bị kéo xuống bởi các lớp con có rất ít mẫu; chỉ tính 5 lớp con có ít nhất 10 mẫu kiểm tra thì được 0,8453. Tỷ lệ nhất quán là 0,9526: 95% số lần, lớp con được đoán thuộc đúng lớp cấp trên được đoán. Hai lớp yếu nhất là `vehicle_idling` (F1 0,6154) và `vehicle_pass_by` (0,6538), hai loại âm thanh gần giống nhau. Hiệu chuẩn nhiệt độ (mục 2.2.4) cho kết quả âm tính: ECE trên tập kiểm tra **tăng** từ 0,0332 lên 0,0564; nhóm báo đúng như vậy.

@@CAP:tbl:classifier|Kết quả mô hình phân loại DataSEC trên tập kiểm tra@@

@@INCLUDE:report/tables/m01_classifier.md@@

⟪tbl:clshistory⟫ đặt kết quả này cạnh các kết quả đã công bố trên các phiên bản dữ liệu khác nhau. Hai trong số đó dùng mô hình tiền huấn luyện đối sánh âm thanh–văn bản (Contrastive Language-Audio Pretraining – CLAP) cộng một lớp tuyến tính. Mục đích là cho thấy bối cảnh, không phải xếp hạng, vì ba điều kiện khác nhau: phiên bản dữ liệu, tập đo, và cách chia. Đề tài chia theo nhóm trùng sau khi kiểm rò rỉ; dự án trên bản 4 tự ghi rằng không chia được theo nguồn. Với cùng kiến trúc CNN14, tỷ lệ phân loại đúng trên bản 4 cao hơn đề tài khoảng 0,044; nhóm chưa kiểm phần chênh này đến từ đâu.

@@CAP:tbl:clshistory|Kết quả phân loại đã công bố theo phiên bản dữ liệu (không so trực tiếp được)@@

@@COLWIDTHS:20,22,22,14,11,11@@

| Nguồn | Dữ liệu | Tập đo, cách chia | Mô hình | Tỷ lệ đúng | Macro-F1 |
|---|---|---|---|---:|---:|
| Artuso và cs., 2025 [@artuso2025clap] | Tiền thân của DataSEC, 21 lớp | Tập kiểm định | CLAP + lớp tuyến tính | 0,9183 | — |
| Khóa luận | DataSEC bản 3, 5.048 tệp, 22 lớp | Tập kiểm tra 740 đoạn; chia theo nhóm trùng | PANNs CNN14 | 0,9135 | 0,8466 |
| Dự án GitHub, 11/2026 [@goyumsamuditha2026datasec] | DataSEC bản 4, 4.292 tệp, 22 lớp | Tập kiểm tra 654 đoạn; không chia theo nguồn | PANNs CNN14 | 0,9572 | 0,9203 |
| | | | CLAP + lớp tuyến tính | 0,9709 | 0,9534 |

@@NOTE:Nguồn: Artuso và cs. (2025), đọc trực tiếp; README của dự án GitHub, đọc trực tiếp ngày 23/11/2026; số của khóa luận từ per_class_metrics_datasec_20260923. Dự án GitHub không qua bình duyệt.@@

## Câu hỏi nghiên cứu 1: huấn luyện thêm trên DataSEC có giúp không?

Vì huấn luyện SED không cho kết quả giống hệt nhau giữa các lần chạy, câu trả lời dựa trên nhiều lần chạy (⟪tbl:rq1⟫). Với SED v1 (3 lần chạy nhánh B, 4 lần chạy nhánh C, chấm trên 142 bản ghi), F1 theo sự kiện micro trung bình của B là 0,0610 và của C là 0,0539; hiệu C − B là −0,0071 [−0,0164; +0,0021]. Với SED v2 (3 lần chạy mỗi nhánh), hiệu là −0,0029 [−0,0254; +0,0199]. Cả hai khoảng tin cậy đều chứa 0. Dao động giữa các lần huấn luyện lớn ngang hoặc lớn hơn hiệu giữa hai nhánh (⟪fig:rq1seeds⟫): ở SED v1, kết quả của nhánh C trải từ 0,0472 đến 0,0660 qua 4 lần huấn luyện, phủ trọn khoảng của nhánh B (0,0557 đến 0,0651).

@@CAP:tbl:rq1|Kết quả Câu hỏi nghiên cứu 1 trên tập kiểm tra@@

@@INCLUDE:docs/thesis/tables/03_rq1.md@@

![](report/gon_figures/c12_rq1_seeds.png){width=15.5cm}

@@CAP:fig:rq1seeds|F1 theo sự kiện micro của nhánh B và nhánh C qua nhiều lần huấn luyện (điểm: trung bình; vạch màu: ±1 độ lệch chuẩn; dải xám: từ nhỏ nhất đến lớn nhất)@@

@@NOTE:Nguồn: rq1_multiseed_clean_20260924.json, rq1_v2_multiseed_20260929.json (đọc lại thống kê đã lưu).@@

Ngược lại, tiền huấn luyện nói chung giúp rõ: nhánh A học từ đầu chỉ đạt F1 theo sự kiện 0,0360, so với 0,0621 của nhánh B. Riêng PSDS-2 của SED v2 tăng +0,0279 (p = 0,0193), nhưng đây là một trong nhiều chỉ số được so và chưa hiệu chỉnh cho việc so nhiều lần.

**Kết luận Câu hỏi nghiên cứu 1:** nhóm **không** có bằng chứng rằng huấn luyện thêm trên DataSEC cải thiện F1 theo sự kiện so với chỉ dùng AudioSet. Kết quả âm tính này không loại trừ một lợi ích nhỏ hơn cận trên của khoảng tin cậy (+0,0021 với SED v1, +0,0199 với SED v2).

## Các thế hệ SED

⟪fig:journey⟫ tóm tắt năm thế hệ SED trên cùng tập kiểm tra, kèm điểm mà mỗi thế hệ dùng khi được chọn. Phần dưới giải thích từng bước.

![](report/gon_figures/r04_sed_journey.png){width=15cm}

@@CAP:fig:journey|F1 theo sự kiện của các thế hệ SED trên tập kiểm tra, và điểm dùng để chọn@@

@@NOTE:Nguồn: s13_test_20261018.json, final_numbers_20261110.json, lbr_context_20261123.json, calibration_20261123.json.@@

**SED v1: vì sao F1 theo sự kiện thấp?** Chẩn đoán trên tập phát triển cho thấy hai nguyên nhân. Thứ nhất, CNN14 ra quyết định theo khối 0,64 s, nên kể cả nhận dạng hoàn hảo thì F1 theo sự kiện tối đa chỉ là 0,6294 (⟪fig:ceiling⟫, trái). Thứ hai, phần lớn lỗi nằm ở biên và ở bỏ sót: trong 886 sự kiện tham chiếu, chỉ 112 khớp dung sai, 417 đúng lớp nhưng lệch biên, và 357 bị bỏ sót. Nới dung sai từ 0,2 s lên 1 s làm F1 theo sự kiện của nhánh B tăng khoảng ba lần (0,062 lên 0,185), phù hợp với chẩn đoán này.

![](report/gon_figures/c04_resolution_ceiling.png){width=15.5cm}

@@CAP:fig:ceiling|Trần F1 theo sự kiện khi nhận dạng đúng nhưng ra quyết định theo khối (trái), và phân rã 886 sự kiện tham chiếu của tập phát triển theo kiểu lỗi (phải)@@

@@NOTE:Nguồn: sed_ceilings_20260926.json, sed_ceilings_v2_20260926.json (tập phát triển; trần tính từ nhãn, không cần mô hình).@@

**SED v2.** Sửa độ phân giải thời gian là thay đổi có tác dụng rõ nhất (⟪fig:ablation⟫): quay về nén 64 lần làm F1 theo sự kiện giảm 0,0840, trong khi bỏ tăng cường dữ liệu hay nới trần trọng số mẫu dương không tách được khỏi dao động giữa các phần. Trên tập phát triển, số sự kiện khớp dung sai tăng từ 112 lên 148 (⟪fig:ceiling⟫, phải). Tổ hợp 3 lần huấn luyện của SED v2 đạt F1 theo sự kiện micro 0,1476 trên 142 bản ghi kiểm tra, so với 0,0941 của SED v1; hiệu +0,0536 [+0,0261; +0,0853]. Cũng ở bước này, nhóm thấy ngưỡng riêng cho từng lớp bị quá khớp tập phát triển: từ tập phát triển sang tập kiểm tra, F1 theo sự kiện với ngưỡng riêng giảm 39% đến 48%, còn với ngưỡng chung chỉ giảm 2% đến 15%.

![](report/gon_figures/c05_v2_ablation.png){width=15.5cm}

@@CAP:fig:ablation|Đóng góp của từng thay đổi trong SED v2: F1 theo sự kiện micro kiểm chứng chéo 5 phần trên tập phát triển; dải nền xanh là khoảng của 3 lần huấn luyện SED v2 đủ@@

@@NOTE:Nguồn: sed_v2_ablation_20260926.json (tập phát triển). Tệp tổng hợp ghi cây làm việc chưa sạch; các lần huấn luyện SED v2 trong hình đều chạy trên cây sạch, riêng dòng tham chiếu SED v1 thì không.@@

**Hệ mốc.** Vòng chọn tiếp theo so 11 ứng viên bằng kiểm chứng chéo trên tập phát triển và khóa hệ mốc (F1 theo sự kiện micro kiểm chứng chéo 0,2383 ± 0,0562). Trên tập kiểm tra, hệ mốc đạt micro 0,1643 [0,1103; 0,2242]. Thứ hạng trên tập kiểm tra không trùng thứ hạng trên tập phát triển: một ứng viên chỉ đứng thứ tư trên tập phát triển lại có micro kiểm tra cao nhất (0,1817). Hệ mốc **không** được chọn lại, vì chọn lại theo tập kiểm tra chính là tinh chỉnh trên tập kiểm tra. Bảng xếp hạng đầy đủ ở Phụ lục B (⟪tbl:s13⟫). Ở hệ mốc, cSEBB tốt hơn ngưỡng chung (0,2383 so với 0,2107), trong khi với các thế hệ trước nó thua; kết luận về cSEBB vì vậy phụ thuộc vào mô hình.

**Hệ cơ sở.** Do thứ hạng trên tập phát triển không đáng tin, nhóm chuyển sang chọn trên dự đoán ngoài mẫu của 564 bản ghi (Chương 4). Hệ cơ sở đạt F1 theo sự kiện micro ngoài mẫu 0,2342. Trên tập kiểm tra, hệ cơ sở đạt micro 0,1806 [0,1261; 0,2384], so với 0,1643 của hệ mốc; hiệu +0,0164 [−0,0128; +0,0495] chứa 0, nên báo cáo **không** gọi hệ cơ sở tốt hơn hệ mốc.

## LBR và hệ thống cuối

Trên dự đoán ngoài mẫu, LBR chính nâng F1 theo sự kiện micro từ 0,2342 lên 0,3332, hiệu +0,0990 [+0,0761; +0,1200]. ⟪tbl:lbrcontext⟫ đặt kết quả này cạnh các cách đơn giản hơn: ngưỡng riêng từng lớp cho 0,2335 và dịch thời điểm bắt đầu đồng loạt cho 0,2469, đều thấp hơn hẳn LBR. Nếu sửa được biên của mọi hộp khớp trong phạm vi ±1 s thì micro đạt 0,4641; LBR chính đi được khoảng 43% quãng đường từ hệ cơ sở tới mức đó. Khi học trên dự đoán của một mô hình rồi áp lên tổ hợp 3 lần huấn luyện, LBR vẫn tăng +0,1160, nên mức tăng không phụ thuộc vào đúng mô hình dùng để học.

@@CAP:tbl:lbrcontext|LBR so với các cách đơn giản hơn, trên dự đoán ngoài mẫu (564 bản ghi)@@

@@COLWIDTHS:38,12,12,38@@

@@INCLUDE:report/final_tables/f10_lbr_context.md@@

⟪fig:oofcands⟫ đặt LBR cạnh mọi ứng viên khác đã được so với hệ cơ sở trên cùng 564 bản ghi ngoài mẫu. Bảy hướng thay hoặc tổ hợp mô hình, thêm lần huấn luyện và tăng cường dữ liệu cho hiệu từ −0,0290 đến +0,0002, không hướng nào có khoảng tin cậy nằm hẳn bên phải 0. Chỉ các biến thể LBR làm được điều đó. Nói cách khác, sau hệ cơ sở, phần còn cải thiện được nằm ở biên hộp chứ không ở mô hình.

![](report/gon_figures/c02_oof_candidates.png){width=15.5cm}

@@CAP:fig:oofcands|Hiệu F1 theo sự kiện micro so với hệ cơ sở của mọi ứng viên đã so trên dự đoán ngoài mẫu (564 bản ghi), kèm KTC 95%@@

@@NOTE:Nguồn: oof_selection_20261009.json, oof_selection_20261014.json, oof_selection_20261108.json, oof_selection_20261108_P4.json, lbr_selection_annotated.json, lbr_application_annotated.json.@@

Tập kiểm tra được mở một lần cho các cấu hình đã khóa (⟪tbl:sedfinal⟫). LBR chính đạt F1 theo sự kiện macro 0,2356 và micro 0,2965 [0,2293; 0,3603]. Hiệu micro so với hệ cơ sở là +0,1159 [+0,0741; +0,1593]; khoảng tin cậy không chứa 0 và cùng hướng với kết quả ngoài mẫu. **Hệ thống cuối của đề tài là hệ cơ sở cộng LBR; LBR chính là số chính.**

@@CAP:tbl:sedfinal|SED trên tập kiểm tra: từ hệ mốc đến LBR@@

@@COLWIDTHS:22,11,22,20,12,13@@

@@INCLUDE:report/final_tables/f01_sed.md|cols=1,2,3,4,5,7|used=1:^LBR V2@@

LBR có đánh đổi (⟪fig:sedfinal⟫). Theo tiêu chí giao nhau (mục 2.2.3), LBR chính có độ phủ sự kiện 0,5108 so với 0,5351 của hệ cơ sở và độ chính xác theo giao nhau 0,9545 so với 0,9706; F1 theo đoạn giảm từ 0,7260 xuống 0,5965. Tức là LBR chính dự đoán nhiều hộp hơn (373 so với 345) và đặt biên khớp hơn, nhưng **không** phát hiện thêm sự kiện thật. LBR ứng dụng đổi hướng ngược lại: dự đoán 668 sự kiện cho 740 sự kiện tham chiếu, đạt độ phủ sự kiện 0,8203 và độ chính xác theo giao nhau 0,7812, nhưng F1 theo sự kiện micro chỉ 0,2287. Vậy có hai cấu hình cho hai mục đích: LBR chính khi cần biên khớp chặt, LBR ứng dụng khi cần ít bỏ sót. Ứng dụng minh họa dùng LBR ứng dụng.

![](report/gon_figures/f01_sed_final.png){width=15cm}

@@CAP:fig:sedfinal|F1 theo sự kiện micro và chỉ số theo giao nhau của các hệ SED trên tập kiểm tra@@

@@NOTE:Nguồn: final_numbers_20261110.json.@@

⟪fig:perclass⟫ so F1 theo sự kiện theo lớp của hệ cơ sở và LBR chính cho 20 lớp có ít nhất 10 sự kiện tham chiếu. LBR tăng ở 15 lớp, giảm ở 2 lớp (`music` và `propeller_aircrafts`), và 3 lớp đứng yên ở 0. Mức tăng lớn nhất nằm ở các lớp kéo dài có biên đầu bị đoán sớm: `vacuum_cleaner_fan_hairdryer`, `cicadas_and_crickets` và `workshop` tăng 0,24 đến 0,26. Ba lớp đứng ở 0 cho thấy giới hạn của LBR: nếu mô hình gốc không sinh hộp đúng lớp thì không có gì để tinh chỉnh.

![](report/gon_figures/r07_per_class.png){width=13.5cm}

@@CAP:fig:perclass|F1 theo sự kiện theo lớp của hệ cơ sở và LBR chính trên tập kiểm tra (lớp có ít nhất 10 sự kiện)@@

@@NOTE:Nguồn: tệp đánh giá đã lưu của hệ cơ sở và của LBR (đọc lại, không tính lại).@@

Trên **19 lớp** của bối cảnh đô thị Việt Nam (Chương 1), F1 theo sự kiện micro của hệ cơ sở là 0,1892 và của LBR chính là 0,3120; LBR ứng dụng có độ phủ sự kiện 0,8319 với độ chính xác theo giao nhau 0,7810. Đây chỉ là phép lọc lớp trên DataSED, không phải dữ liệu thu tại Việt Nam.

**PSDS.** PSDS tính trên một dải ngưỡng nên phụ thuộc cách chọn dải (mục 2.2.3). Trên cùng dải ngưỡng log, LBR chính đạt PSDS-1 0,3512 và PSDS-2 0,6116, còn hệ cơ sở đạt 0,3061 và 0,7452. Như vậy LBR tăng PSDS-1, kịch bản đòi biên khớp, nhưng **giảm rõ** PSDS-2, kịch bản chỉ đòi chồng lấp ít; điều này nhất quán với việc LBR làm biên khớp hơn mà không tăng độ phủ sự kiện. Dải ngưỡng quan trọng đến mức nào thể hiện ở ⟪fig:psdsgrid⟫: với dải ngưỡng ban đầu, LBR chính chỉ đạt PSDS-2 0,2960, vì 542 hộp có điểm thấp hơn ngưỡng nhỏ nhất của dải và không bao giờ được tính. Vì vậy mọi so sánh PSDS trong báo cáo dùng chung dải ngưỡng log. Chẩn đoán chi tiết về PSDS ở Phụ lục B (⟪tbl:psdsdiag⟫).

![](report/gon_figures/c06_psds_grid.png){width=15.5cm}

@@CAP:fig:psdsgrid|PSDS-1 và PSDS-2 trên tập kiểm tra theo hai dải ngưỡng: dải ban đầu của từng hệ (gạch chéo) và dải log dùng chung (tô đặc)@@

@@NOTE:Nguồn: final_numbers_20261110.json, lbr_psds_grid_20261110_annotated.json. Dải ban đầu của hệ cơ sở là lưới tuyến tính mặc định của bước đánh giá; của LBR là lưới cũ của bước LBR.@@

## F1 theo sự kiện khoảng 0,30 là cao hay thấp?

Một con số F1 theo sự kiện đứng riêng khó đọc, nên báo cáo đặt nó cạnh hai mốc tham chiếu. Cả hai chỉ để hình dung độ lớn, không phải bảng xếp hạng.

**Mốc thứ nhất: độ đồng thuận giữa hai lần gán nhãn trên chính DataSED** (⟪tbl:calibration⟫). Trên 8 cặp bản ghi được gán nhãn hai lần, F1 theo sự kiện giữa hai lần gán là 0,5785 với dung sai 0,2 s và 0,7425 với F1 theo đoạn 1 s. LBR chính đạt 0,2965, khoảng 51% mức đồng thuận; còn theo đoạn 1 s, hệ cơ sở đạt 0,7260, khoảng 98%. Nói cách khác, nhận dạng *có hay không trong từng giây* đã gần mức đồng thuận, còn **định vị biên chính xác** vẫn là nút thắt. Đây không phải khẳng định "ngang người": mẫu chỉ có 8 cặp và hai bên đo trên các bản ghi khác nhau.

@@CAP:tbl:calibration|F1 theo sự kiện theo bốn cách đo, cạnh độ đồng thuận giữa hai lần gán nhãn@@

@@COLWIDTHS:34,16,16,16,18@@

@@INCLUDE:report/final_tables/f11_calibration.md@@

⟪fig:calibration⟫ vẽ lại ba cột của bảng cạnh mức đồng thuận. Khoảng cách tới đường đứt nét lớn nhất ở F1 theo sự kiện dung sai 0,2 s và gần như biến mất ở F1 theo đoạn 1 s; LBR ứng dụng còn vượt đường này ở F1 theo đoạn, nhưng hai bên đo trên các bản ghi khác nhau nên không đọc thành "hơn người".

![](report/gon_figures/c03_calibration.png){width=15.5cm}

@@CAP:fig:calibration|F1 theo ba cách đo của ba hệ SED trên tập kiểm tra, cạnh mức đồng thuận giữa hai lần gán nhãn (đường đứt nét, 8 cặp bản ghi)@@

@@NOTE:Nguồn: calibration_20261123.json.@@

**Mốc thứ hai: thử thách DCASE** (⟪tbl:dcase⟫). Với DESED, PSDS của các hệ cơ sở DCASE cùng cỡ với PSDS của đề tài. Tuy nhiên DESED là đoạn 10 s, 10 lớp, phần lớn là dữ liệu tổng hợp; DataSED là bản ghi trung bình 94 s, 21 lớp và chỉ có 564 bản ghi có nhãn để huấn luyện. Nhóm không viết "tương đương DESED".

@@CAP:tbl:dcase|Các mốc công bố dùng để hình dung độ khó (không so trực tiếp được)@@

@@COLWIDTHS:30,22,48@@

| Bối cảnh | Chỉ số | Mốc công bố |
|---|---|---|
| DCASE 2016 nhiệm vụ 3, ghi âm đời thực [@dcase2016task3] | F1 theo sự kiện, chỉ xét thời điểm bắt đầu | 0,015 đến 0,081 trên 16 hệ; hệ cơ sở 0,063 |
| DCASE 2022 nhiệm vụ 4, DESED [@dcase2022task4] | PSDS-1 / PSDS-2 | Hệ cơ sở 0,315 / 0,543 |
| DCASE 2023 nhiệm vụ 4A, DESED [@dcase2023task4a] | PSDS-1 / PSDS-2 | Hệ cơ sở 0,327 / 0,538; hệ cơ sở có BEATs 0,510 / 0,798 |
| DCASE 2023 nhiệm vụ 4B, MAESTRO Real [@dcase2023task4b] | F1 micro / macro | Hệ cơ sở 0,7413 / 0,3528 |
| Khóa luận (tập kiểm tra, 21 lớp) | F1 theo sự kiện micro / macro; PSDS-1 / PSDS-2 | 0,2965 / 0,2356 (LBR chính); 0,3061 đến 0,3512 / 0,6116 đến 0,7452 |

@@NOTE:Nguồn: trang kết quả DCASE 2016, 2022 và 2023, đọc trực tiếp ngày 23/11/2026; số của khóa luận từ final_numbers_20261110.json.@@

## Câu hỏi nghiên cứu 2: mô tả có bám sát sự kiện không?

Bốn cách sinh được so trên cùng danh sách sự kiện của từng hệ SED, trên 139 bản ghi kiểm tra (⟪tbl:rq2final⟫, ⟪fig:rq2errors⟫). Có ba kết quả.

@@CAP:tbl:rq2final|Bỏ sót và ảo giác theo cách sinh và hệ SED (tập kiểm tra, so với danh sách sự kiện dự đoán)@@

@@COLWIDTHS:28,18,18,18,18@@

@@INCLUDE:report/final_tables/f04_rq2.md@@

![](report/gon_figures/c13_rq2_errors.png){width=15.5cm}

@@CAP:fig:rq2errors|Tỷ lệ bỏ sót, ảo giác nguồn âm và mô tả có suy diễn bối cảnh theo cách sinh và hệ SED (tập kiểm tra); tam giác đánh dấu giá trị bằng 0@@

@@NOTE:Nguồn: rq2_llm_systems_20261110_test_annotated.json. Màu đậm dần theo mức ràng buộc của cách sinh.@@

**Thứ nhất, cách theo mẫu cho 0 ở mọi chỉ số**, cả tiếng Anh lẫn tiếng Việt, trên cả bốn hệ SED. Đây là bằng chứng bộ đo không báo lỗi giả trên mô tả đúng.

**Thứ hai, viết tự do hiếm khi bịa nguồn âm, nhưng hay thêm điều không có trong bằng chứng.** Tỷ lệ ảo giác nguồn âm của cách tự do chỉ từ 0,005 đến 0,022. Lỗi chính nằm ở chỗ thêm bối cảnh (0,259 đến 0,403 số mô tả) và gọi tên quá cụ thể (0,126 đến 0,140). Hai cách có ràng buộc đưa ảo giác, bối cảnh, gọi tên quá cụ thể và từ cấm về 0 ở cả bốn hệ SED.

**Thứ ba, cái giá của ràng buộc là bỏ sót, và nó tăng khi danh sách sự kiện dày.** Cách ràng buộc bỏ sót 0,012 (hệ mốc), 0,013 (hệ cơ sở), 0,007 (LBR chính) nhưng 0,081 với LBR ứng dụng; hiệu so với hệ mốc là +0,069 [+0,041; +0,097]. Danh sách của LBR ứng dụng dày (668 sự kiện trên 139 bản ghi), trong khi cách ràng buộc chỉ nhắc một phần sự kiện. Cách ràng buộc + phủ giữ bỏ sót bằng 0 ở mọi hệ, và không có chỉ số nào kém hơn cách tự do.

Cần đọc Câu hỏi nghiên cứu 2 đúng mức. Kết quả "0 vi phạm" của hai cách có ràng buộc là hệ quả của cấu tạo ngữ pháp, nên thông tin thật nằm ở cái giá (bỏ sót) và ở mức lệch của cách viết tự do. Câu của cách ràng buộc cũng gần như câu theo mẫu: so với câu theo mẫu, nó đạt BLEU-4 0,358 và CIDEr 3,60, còn cách tự do chỉ 0,015 và 0,116. Vì cách theo mẫu đạt 0 ở mọi chỉ số và không tốn tính toán, giao diện dùng mô tả theo mẫu.

**Mô tả so với nhãn gốc.** "Không ảo giác so với danh sách dự đoán" chưa có nghĩa là mô tả đúng với âm thanh. Để tách hai loại lỗi, nhóm chấm lại chính các mô tả đã sinh trên tập phát triển, lần này so với nhãn gốc (⟪tbl:captiontiers⟫). Phép đo này không gọi lại mô hình ngôn ngữ và không dùng tập kiểm tra.

@@CAP:tbl:captiontiers|Ảo giác và bỏ sót: so với danh sách dự đoán / so với nhãn gốc (tập phát triển)@@

@@COLWIDTHS:18,32,25,25@@

@@INCLUDE:report/final_tables/f04b_caption_tiers.md@@

Kết quả cho thấy ba điều (⟪fig:captiongt⟫). **Một,** so với nhãn gốc, mọi cách sinh đều bỏ sót khoảng 34% đến 42% số lớp có thật ở hệ mốc, hệ cơ sở và LBR chính, kể cả hai cách vốn bằng 0 khi so với dự đoán. **Hai,** chênh lệch giữa các cách sinh nhỏ hơn nhiều so với chênh lệch giữa các hệ SED: trong cùng một hệ, ảo giác so với nhãn gốc của bốn cách sinh lệch nhau nhiều nhất 0,056, còn cùng một cách sinh lệch 0,16 đến 0,20 khi đổi từ LBR chính sang LBR ứng dụng. **Ba,** vì vậy độ đúng của mô tả với âm thanh chủ yếu do SED quyết định; phần của bộ sinh là không tự thêm nguồn âm ngoài danh sách.

![](report/gon_figures/c07_caption_vs_gt.png){width=15.5cm}

@@CAP:fig:captiongt|Ảo giác và bỏ sót của mô tả khi so với danh sách dự đoán (điểm rỗng) và khi so với nhãn gốc (điểm đặc), theo hệ SED và cách sinh (tập phát triển)@@

@@NOTE:Nguồn: caption_vs_gt_dev_20261124.json (134 bản ghi; chấm lại mô tả đã sinh, không gọi lại mô hình ngôn ngữ).@@

**Mô tả theo lớp.** Với LBR ứng dụng, mô tả theo mẫu dài trung bình 400 ký tự trên tập phát triển; mô tả theo lớp còn trung bình 119 ký tự, và vẫn không có ảo giác hay bỏ sót so với danh sách sự kiện. Nhãn "độ tin cậy thấp" mang thông tin: ở LBR ứng dụng, mệnh đề có nhãn này chỉ đúng với nhãn gốc 17/98 lần, còn mệnh đề không có nhãn đúng 202/228 lần. Ngưỡng của nhãn được chọn trên chính tập phát triển này, nên đây là phép đo trong mẫu.

**Giới hạn của bộ đo.** Bộ đo tìm nguồn âm bằng từ điển cụm từ. Trên 60 mô tả được một người đọc đối chiếu, từ điển đạt độ chính xác 0,896 và độ đầy đủ 0,936 so với người đọc. Nhóm cũng cố tình chèn nguồn âm sai vào mô tả để đo độ nhạy, theo ý tưởng của BRACE [@guo2025brace]: khi nguồn âm sai thuộc 21 lớp, bộ đo bắt được gần như mọi ca (1859/1860); khi nguồn âm nằm ngoài hệ lớp, chỉ 62% bị bắt (⟪fig:checker⟫). Lỗi dồn vào vài cụm cụ thể: "a hammer striking", "a clock ticking" và "a phone vibrating" không bị bắt lần nào, còn năm cụm còn lại bị bắt gần như mọi lần. Vì vậy tỷ lệ ảo giác của cách viết tự do là **cận dưới**: nguồn âm lạ có thể lọt qua bộ đo.

![](report/gon_figures/c08_checker_sensitivity.png){width=15.5cm}

@@CAP:fig:checker|Độ nhạy của bộ đo ảo giác: tỷ lệ lỗi cố tình chèn vào mô tả bị bắt được, theo kiểu lỗi (trái) và theo cụm nguồn âm ngoài hệ lớp (phải)@@

@@NOTE:Nguồn: checker_sensitivity_dev_20261124.json (tập phát triển, gộp các cách sinh).@@

## Câu hỏi nghiên cứu 3: truy hồi và câu trả lời có bằng chứng

⟪tbl:rq3final⟫ báo kết quả truy hồi trên tập kiểm tra với bộ lọc chuẩn (lấy đúng từ bộ câu truy vấn), cho bốn kho sự kiện dựng từ dự đoán của bốn hệ SED.

@@CAP:tbl:rq3final|Câu hỏi nghiên cứu 3 trên tập kiểm tra: nDCG@10 và chất lượng câu trả lời@@

@@COLWIDTHS:14,16,16,16,11,14,13@@

@@INCLUDE:report/final_tables/f05_rq3.md@@

Với hệ mốc, hệ cơ sở và LBR chính, nDCG@10 của chế độ kết hợp là 0,415, 0,383 và 0,404, khoảng tin cậy chồng nhau nhiều. Điều này đáng chú ý: LBR chính tăng F1 theo sự kiện micro khoảng 1,6 lần so với hệ cơ sở, nhưng truy hồi gần như không đổi. Truy hồi phụ thuộc vào việc *sự kiện nào* được phát hiện, không phải vào độ khớp của biên. Riêng kho của LBR ứng dụng cao hơn hẳn (0,670) và trả lời được 95/97 câu truy vấn, so với 58 đến 65 của ba kho kia. Đây là **hiệu ứng độ phủ sự kiện**: LBR ứng dụng phát hiện nhiều sự kiện thật hơn (độ phủ sự kiện 0,8203 so với 0,5108 đến 0,5351), nên bộ lọc ít loại nhầm bản ghi liên quan. Cái giá là tỷ lệ trích dẫn đúng thấp hơn (0,712 so với 0,915 của hệ cơ sở).

**Kết hợp có tốt hơn từng thành phần không?** Đây là nội dung gốc của Câu hỏi nghiên cứu 3, và câu trả lời trên dữ liệu này là **không, xét theo nDCG@10** (⟪tbl:rq3paired⟫). Với ba kho có độ phủ sự kiện thấp, chế độ kết hợp thấp hơn chế độ chỉ ngữ nghĩa: −0,111, −0,075 và −0,087, khoảng tin cậy không chứa 0. Riêng kho của LBR ứng dụng, chiều này đảo lại (+0,040). Chế độ kết hợp gần như trùng chế độ chỉ lọc (mọi hiệu không quá 0,013). Hiệu âm không do vài câu truy vấn ngoại lai (⟪fig:rq3queries⟫): ở kho hệ mốc, trong 97 câu truy vấn có bản ghi liên quan, chế độ kết hợp thua ở 49 câu, hòa 33 câu và thắng 15 câu; kho LBR ứng dụng đảo lại, thua 18 và thắng 44.

@@CAP:tbl:rq3paired|Hiệu nDCG@10 ghép cặp giữa các chế độ và độ đúng bộ lọc (tập kiểm tra)@@

@@COLWIDTHS:16,24,22,19,19@@

@@INCLUDE:report/final_tables/f05b_rq3_paired.md@@

![](report/gon_figures/c14_rq3_queries.png){width=15.5cm}

@@CAP:fig:rq3queries|Hiệu nDCG@10 kết hợp − chỉ ngữ nghĩa theo từng câu truy vấn (điểm xám) và trung bình kèm KTC 95% ghép cặp; dòng trên cùng: số câu thua / hòa / thắng@@

@@NOTE:Nguồn: per_query trong bốn tệp kết quả truy hồi trên tập kiểm tra (danh sách ở rq3_modes_20261123.json); tiếng Anh, bộ lọc chuẩn.@@

Ba điều cần đọc cùng nhau. **Một,** chế độ chỉ ngữ nghĩa không tôn trọng điều kiện: chỉ khoảng 27% kết quả của nó thỏa bộ lọc, so với 1,000 của chế độ kết hợp. nDCG cao hơn của nó không có nghĩa là nó đáp ứng câu truy vấn có điều kiện tốt hơn. **Hai,** chênh lệch tập trung ở câu truy vấn nhiều lớp và câu truy vấn quan hệ thời gian (⟪tbl:rq3groups⟫); ví dụ ở kho hệ mốc, nhóm quan hệ thời gian đạt 0,126 với chế độ kết hợp so với 0,426 với chế độ chỉ ngữ nghĩa. **Ba,** nguyên nhân hợp lý nhất là bộ lọc chạy trên sự kiện *dự đoán*: chỉ bản ghi mà SED đã dự đoán đủ mọi lớp và quan hệ trong câu truy vấn mới qua được bộ lọc. Đếm trực tiếp trên kho của hệ cơ sở: trong 705 cặp (câu truy vấn, bản ghi liên quan), 349 cặp bị loại vì sự kiện dự đoán không thỏa bộ lọc (⟪fig:rq3failures⟫). Ở kho LBR ứng dụng, số cặp bị loại giảm còn 127, đúng như dự đoán từ độ phủ sự kiện cao hơn. Bộ phân tích câu hỏi chỉ làm đổi kết quả ở 4 đến 12 trên 97 câu truy vấn, nhỏ hơn nhiều so với phần do SED.

![](report/gon_figures/c09_retrieval_failures.png){width=15.5cm}

@@CAP:fig:rq3failures|Số phận của 705 cặp (câu truy vấn, bản ghi liên quan) ở chế độ kết hợp, theo kho sự kiện (tập kiểm tra, bộ lọc chuẩn)@@

@@NOTE:Nguồn: retrieval_failures_test_20261124.json. Phân tích làm sau khi đã thấy kết quả trên tập kiểm tra, chỉ đọc lại danh sách đã lưu.@@

@@CAP:tbl:rq3groups|nDCG@10 kết hợp / chỉ ngữ nghĩa theo nhóm câu truy vấn (tập kiểm tra)@@

@@COLWIDTHS:16,21,21,21,21@@

@@INCLUDE:report/final_tables/f05c_rq3_groups.md@@

### Chế độ bổ sung

Phân tích trên cho thấy chế độ kết hợp thua không phải vì xếp sai, mà vì trả quá ít kết quả: ở kho hệ mốc, 32/97 câu truy vấn có danh sách kết hợp rỗng. Cần nói rõ đây là quan sát trên tập kiểm tra. Từ đó nhóm thử chế độ bổ sung (Chương 4): giữ nguyên danh sách kết hợp, rồi lấp chỗ trống bằng kết quả chỉ ngữ nghĩa (⟪fig:rq3backfill⟫). Chế độ này không có tham số để chỉnh; định nghĩa được ghi trước, kiểm trên tập phát triển, rồi đo trên tập kiểm tra một lần. Văn liệu về truy hồi lai cũng cho thấy cách trộn hai nguồn xếp hạng tốt nhất phụ thuộc dữ liệu [@bruch2023fusion].

![](report/gon_figures/r13_rq3_backfill.png){width=14cm}

@@CAP:fig:rq3backfill|nDCG@10 của ba chế độ trên tập kiểm tra; số trên cột cam là tỷ lệ kết quả của chế độ bổ sung thỏa bộ lọc@@

@@NOTE:Nguồn: retrieval_backfill_test_20261124.json (bộ lọc chuẩn, tiếng Anh).@@

Hình này cho thấy chế độ bổ sung cao hơn cả hai chế độ gốc ở cả bốn kho, và mọi khoảng tin cậy ghép cặp đều không chứa 0 (⟪fig:backfillpaired⟫). So với chỉ ngữ nghĩa, mức tăng là +0,041 đến +0,097; so với kết hợp là +0,057 đến +0,160. So với chỉ ngữ nghĩa, ở ba kho độ phủ sự kiện thấp phần lớn câu truy vấn hòa, nên mức tăng đến từ một số ít câu; ở mọi so sánh, số câu thua không quá 5 trên 97. Câu truy vấn tiếng Việt và bộ lọc do bộ phân tích sinh ra cho cùng chiều. Cái giá là chỉ 29% đến 31% kết quả thỏa bộ lọc ở ba kho độ phủ sự kiện thấp (57% ở kho LBR ứng dụng); phần còn lại là gợi ý gần nghĩa. Vì vậy ứng dụng tách bạch hai phần: câu trả lời chỉ khẳng định trên phần thỏa bộ lọc, phần gần nghĩa chỉ hiện như gợi ý.

![](report/gon_figures/c10_backfill_paired.png){width=15.5cm}

@@CAP:fig:backfillpaired|Hiệu nDCG@10 ghép cặp của chế độ bổ sung so với hai chế độ gốc, kèm KTC 95% và số câu truy vấn thắng / hòa / thua (tập kiểm tra)@@

@@NOTE:Nguồn: retrieval_backfill_test_20261124.json (bộ lọc chuẩn, tiếng Anh; 97 câu truy vấn có bản ghi liên quan).@@

**Câu trả lời.** Ở mọi cấu hình, tỷ lệ khẳng định thiếu bằng chứng là 0,000: câu trả lời không vượt ra ngoài những gì kho chứa; đổi lại, kho thiếu thì câu trả lời cũng thiếu. Độ đúng bộ lọc 1,000 chỉ cho biết kết quả nhất quán với bộ lọc và với sự kiện *dự đoán* trong kho, không cho biết kết quả đúng với ý người hỏi hay với âm thanh.

### Bộ phân tích câu hỏi

Bộ phân tích cho đầu ra đúng lược đồ ở 240/240 câu (⟪tbl:parser⟫). Độ đúng hoàn toàn là 0,855 trên 200 câu theo mẫu và 0,925 trên 40 câu diễn đạt lại. Lỗi chủ yếu nằm ở điều kiện thời gian: độ đúng chỉ 0,767, với các lỗi như đảo vai trò a và b, nhầm "within" thành "overlaps" hoặc bỏ ràng buộc thời lượng. Với bộ lọc do bộ phân tích sinh ra, nDCG@10 của chế độ kết hợp thấp hơn bộ lọc chuẩn từ 0,006 đến 0,015 trên tập kiểm tra. Đây là nguồn lỗi nằm ngoài SED, và là lý do giao diện cho người dùng sửa thẻ bộ lọc.

@@CAP:tbl:parser|Đánh giá bộ phân tích câu hỏi@@

@@COLWIDTHS:20,8,14,14,15,14,15@@

@@INCLUDE:docs/thesis/tables/10_parser_l2.md|cols=1,2,3,4,5,6,7@@

## Mức tin cậy của các so sánh

⟪fig:maindiffs⟫ gom các hiệu chính của phần SED, mỗi hiệu kèm khoảng tin cậy, tập đo và cỡ mẫu. Hai hiệu của Câu hỏi nghiên cứu 1 và hiệu giữa hệ cơ sở với hệ mốc có khoảng tin cậy chứa 0; hiệu SED v2 so với SED v1 và hai hiệu của LBR chính thì không.

![](report/gon_figures/c01_main_differences.png){width=15.5cm}

@@CAP:fig:maindiffs|Các hiệu F1 theo sự kiện micro chính của báo cáo, kèm KTC 95% bootstrap ghép cặp (điểm rỗng: dự đoán ngoài mẫu; điểm đặc: tập kiểm tra)@@

@@NOTE:Nguồn: final_numbers_20261110.json, rq1_multirun_bootstrap_sedv2_vs_v1_20260926.json (đổi dấu thành SED v2 − SED v1), lbr_context_20261123.json.@@

Tập kiểm tra không được dùng "một lần" theo nghĩa đen: sổ ghi có **42 lượt đánh giá SED trên tập kiểm tra**, cùng các lượt đo mô tả và truy hồi. Điều nhóm bảo đảm hẹp hơn: mỗi cấu hình đã khóa chỉ được đo trên tập kiểm tra **một lần**, lựa chọn được lưu trước khi sinh dự đoán kiểm tra, và không cấu hình nào được chọn lại sau khi xem kết quả. Ba điểm cần nói thẳng:

- **Thứ hạng trên tập phát triển dự báo kém thứ hạng trên tập kiểm tra.** Ở vòng chọn hệ mốc, tương quan hạng Spearman giữa hai tập là ρ = 0,62. Đây là lý do nhóm chuyển sang chọn trên dự đoán ngoài mẫu. Với LBR chính, hiệu ngoài mẫu (+0,0990) và hiệu trên tập kiểm tra (+0,1159) cùng hướng; sự nhất quán này là bằng chứng chống quá khớp mạnh hơn bất kỳ lượt đo đơn lẻ nào.
- **Có những chỗ tập kiểm tra gợi ý hướng thử.** Thiết kế của LBR được thăm dò trên chính dữ liệu ngoài mẫu dùng để chọn; ý tưởng chế độ bổ sung đến từ phân tích lỗi trên tập kiểm tra. Ở cả hai trường hợp, cấu hình được khóa trước rồi mới đo trên tập kiểm tra một lần, nhưng hướng thử vẫn do kết quả trước đó gợi ý.
- **Khoảng tin cậy không hiệu chỉnh cho việc so nhiều lần.** So sánh chính của phần SED (LBR chính so với hệ cơ sở) được định trước, có khoảng tin cậy không chứa 0 và cùng hướng với kết quả ngoài mẫu. Các so sánh phụ không nên đọc như kết luận.

## Thảo luận

Các kết quả quy về luận điểm đã nêu ở Chương 1: **độ đúng của mô tả và câu trả lời phụ thuộc chủ yếu vào bước phát hiện sự kiện, và cụ thể là vào độ phủ sự kiện.** Bộ sinh có ràng buộc không tự thêm nguồn âm ngoài danh sách sự kiện (Câu hỏi nghiên cứu 2), và bộ lọc cứng chỉ trả bản ghi thỏa điều kiện trên sự kiện đã lưu (Câu hỏi nghiên cứu 3). Khi so với âm thanh thật, lỗi còn lại chủ yếu đến từ SED. Hai bộ phận khác có lỗi riêng đã được đo: bộ phân tích câu hỏi (đúng hoàn toàn 0,855) và bộ đo ảo giác (chỉ bắt 62% nguồn âm ngoài hệ lớp).

Luận điểm này giải thích một kết quả thoạt nhìn trái chiều. LBR chính cải thiện rõ F1 theo sự kiện, chỉ số chính đã định trước, nhưng không cải thiện truy hồi (0,383 với hệ cơ sở so với 0,404 với LBR chính, khoảng tin cậy chồng nhau) và làm mô tả theo mẫu bỏ sót nhiều hơn khi so với nhãn gốc (0,342 lên 0,415, tập phát triển). Lý do là LBR chính làm biên khớp hơn mà không tăng độ phủ sự kiện (0,5351 xuống 0,5108). Ngược lại, khi độ phủ sự kiện tăng, cả hai bước sau đều tốt lên: kho của LBR ứng dụng (độ phủ 0,8203) có nDCG@10 kết hợp 0,670 và mô tả bỏ sót 0,107 so với nhãn gốc; chế độ bổ sung, vốn tăng độ phủ ở bước truy hồi, cao hơn cả hai chế độ gốc ở cả bốn kho. Hướng cải tiến có tác dụng vì vậy là tăng độ phủ sự kiện, ở SED hoặc ở bước truy hồi, chứ không chỉ tăng F1 theo sự kiện. Các hạn chế được tổng hợp ở Chương 7.
