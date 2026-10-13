# Ngữ cảnh báo cáo biên tầng O — sáu run

Artifact: [boundary_errors_20261009.json](boundary_errors_20261009.json) và [boundary_errors_20261009.md](boundary_errors_20261009.md).

Chạy nguyên script Claude trên CPU, tất cả dùng postproc_cv_annotated.json đã lưu; không chạy selector. Toàn bộ 137 dev gồm 134 annotated và 3 recording không có GT; posterior được tính âm trên 3 recording này. Khác phạm vi 134 annotated của XO-21. Script chỉ áp họ θ; DO-4 là họ θ đồng hành, khác cSEBB thắng CV. Đã kiểm raster 100 Hz đúng với cả sáu prediction.

Ghép mỗi GT với dự đoán cùng lớp có overlap dương lớn nhất, có thể dùng lại dự đoán và không cần đạt collar; **n overlap không phải TP sed_eval**. Không dùng số này thay kết quả CV hoặc chọn model. Command và hash trong context.json. Output gốc từ scratch được copy tự động vào thư mục measurement; giữ bản bốn run ngày 08 và bổ sung bản sáu run ngày 09, không sửa số tay.
