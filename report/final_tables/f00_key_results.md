# Kết quả chính theo câu hỏi nghiên cứu

> Sinh tự động bởi `scripts.report_key_results` tại git `0e8680f`.

| Câu hỏi | Tập đo | Kết quả (KTC 95%) | Kết luận |
|---|---|---|---|
| RQ1: thêm DataSEC | Test, công thức v2, 3 + 3 seed | C − B micro −0,0029 [−0,0254; +0,0199] | Không có khác biệt đo được (KTC chứa 0) |
| SED: B0 → LBR V2 | Test annotated, n = 139 | Micro 0,1806 → 0,2965, hiệu +0,1159 [+0,0741; +0,1593]; F1 theo đoạn 0,7260 → 0,5965; PSDS-2 (lưới log) 0,7452 → 0,6116 | LBR tăng event-F1 rõ; đổi lại F1 theo đoạn và PSDS-2 thấp hơn |
| RQ2: so với dự đoán | Test annotated, bốn hệ SED | Viết tự do: ảo giác 0,005 đến 0,022, suy diễn bối cảnh 0,259 đến 0,403; có ràng buộc: 0 và 0 | Ràng buộc loại lỗi của bộ sinh (theo cấu tạo); cái giá là bỏ sót |
| RQ2: so với nhãn gốc | Dev annotated, f2 / B0 / LBR V2 | Template bỏ sót 0,342 đến 0,415 số lớp có thật | Lỗi còn lại do SED, không do bộ sinh |
| RQ3: hybrid so với vector_only | Test, bộ lọc gold, bốn kho | Hiệu nDCG@10 −0,111 đến −0,075 ở ba kho độ phủ thấp, +0,040 ở V3; độ đúng bộ lọc 1,000 so với 0,271 đến 0,493 | Lọc cứng luôn đúng điều kiện nhưng xếp hạng bị chặn bởi độ phủ của SED |
| RQ3: chế độ backfill | Test, bộ lọc gold, bốn kho | Hơn vector_only +0,041 đến +0,097, mọi KTC > 0 | Cải tiến có tác dụng nằm ở độ phủ khi truy hồi |
| Ứng dụng | CPU, 10 bản ghi TRAIN | Tải lên và phân tích trung vị 3,89 s; truy vấn 0,22 s | Phân tích âm thanh chạy cục bộ trên CPU; bộ phân tích câu hỏi cần máy chủ llama.cpp |

**Nguồn:** `docs/measurements/final_numbers_20261110.json`; `docs/measurements/rq3_modes_20261123.json`; `docs/measurements/retrieval_backfill_test_20261124.json`; `docs/measurements/caption_vs_gt_dev_20261124.json`; `docs/measurements/latency_lbrv3_20261123.json`.
