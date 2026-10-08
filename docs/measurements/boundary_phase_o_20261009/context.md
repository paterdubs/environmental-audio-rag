# Ngữ cảnh chạy báo cáo biên tầng O

Artifact gốc: [boundary_errors_20261008.json](boundary_errors_20261008.json), [boundary_errors_20261008.md](boundary_errors_20261008.md).

Chạy script có sẵn, không sửa code Claude; chỉ dev, CPU. Cả4run dùng `postproc_cv_annotated.json`. Script xét toàn137dev, gồm134annotated và3khôngGT (posterior được tính âm trên những recording này), raster100Hz đúng prediction. Khác phạm vi134recording của XO-17/19/20/21. Script luôn áp họ θ; DO-4 có họ thắng CV là cSEBB, nên **đây là chẩn đoán họ θ đồng hành**, không thay kết quả họ thắng XO-21.

Sai số biên ghép từng reference với dự đoán cùng lớp overlap dương lớn nhất; cho phép dùng lại dự đoán cho nhiều reference, không cần đạt collar. **n overlap không phải TP sed_eval** và không cùng phép ghép của XO-17. Chỉ in-sample; không suy nguyên nhân hoặc đổi luật chọn.

TF256 KD `135047Z` được thêm sau khi postproc annotated xuất hiện trong lượt làm; không tự chạy selector. Hash nguồn và câu lệnh đầy đủ ở context.json; helper cpu.py đặt CUDA_VISIBLE_DEVICES rỗng trước import. Measurement ngày chạy UTC ở tên gốc, thư mục nhãn20261009 theo lượt giao.
