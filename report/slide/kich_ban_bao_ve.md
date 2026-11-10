# Kịch bản bảo vệ khóa luận

> Sinh tự động bởi `scripts.build_final_slides` từ `report/slide_bao_ve.pptx`; sửa nội dung trong `scripts/build_final_slides.py`, không sửa tay tệp này.

## Slide 1

Mở đầu (30 giây). Chào quý thầy cô, nhóm em là Phát và Tính, trình bày khóa luận "Xây dựng hệ
thống phát hiện, sinh mô tả và truy vấn sự kiện âm thanh môi trường dựa trên RAG". Bài có năm
phần: đề tài và hệ thống; dữ liệu và cách đánh giá; phát hiện sự kiện; mô tả và truy hồi; kết luận.

## Slide 2. Từ bản ghi âm đến câu trả lời có bằng chứng

(1 phút) Hệ thống nhận một bản ghi âm môi trường dài và trả về ba thứ nối tiếp: danh sách sự kiện có
thời gian, một đoạn mô tả chỉ được viết từ danh sách đó, và câu trả lời có bằng chứng cho câu hỏi
về lịch sử. Nhóm đo từng mắt xích riêng. Đề tài không suy ra ý định hay mức nguy hiểm: "phát hiện
kính vỡ lúc 5,4 giây" hợp lệ, "phát hiện đột nhập" thì không.

## Slide 3. Ba câu hỏi nghiên cứu và bốn đóng góp

(1,5 phút) Ba câu hỏi và bốn đóng góp. Điểm cần nói thẳng: sau khi tra văn liệu tháng 11, nhóm thấy
đã có công trình gần với C2, C3, C4 — ECHO và TAC đo ảo giác của mô tả âm thanh, Weck và Serra kiểm
tra trùng trong một bộ dữ liệu, LA-RAG dựng event store SQL kèm RAG. Vì vậy nhóm trình bày là áp
dụng và mở rộng, không phải lần đầu. Phạm vi tra là mức khóa luận, không phải tổng quan hệ thống.

## Slide 4. Hệ thống: bước ghép sự kiện nằm ở dịch vụ suy luận, không ở mô hình

(1 phút) Bản ghi đi qua dịch vụ suy luận thành danh sách sự kiện; danh sách dùng hai hướng: sinh
mô tả và lưu kho để truy hồi. Ranh giới quan trọng: ngưỡng và tham số ghép là kết quả hiệu chuẩn trên
dev, nên đổi điểm vận hành mà không huấn luyện lại. Đây cũng là chỗ LBR gắn vào, ở phần SED.

## Slide 5. Dữ liệu: hai bộ cùng nhóm tác giả, có chung bản ghi gốc

(1,5 phút) Hai bộ dữ liệu cùng sáu tác giả, cùng miền, công bố cách nhau bốn tháng, nên nhóm giả định
chúng có thể chung bản ghi gốc cho tới khi đo được. Kiểm tra bằng dấu vân âm thanh tìm ra ba nhóm
trùng; có hai cặp giống nhau hoàn toàn trên 35 và 13 giây. Sau khi người duyệt tay 35 cặp mơ hồ,
11 đoạn DataSEC (0,22%) bị loại trước khi huấn luyện. Từ đó mọi phép đo chuyển giao nằm trong điều
kiện rò rỉ đã được kiểm soát.

## Slide 6. Cách đánh giá: chọn trước, mở test đúng một lần

(1 phút) Quy tắc cứng: không tinh chỉnh trên test. Mọi lựa chọn làm trên dev hoặc trên dự đoán
ngoài mẫu, luật chọn ghi trước, và test mở đúng một lần cho cấu hình đã khóa. Nhóm công khai cả
những chỗ sai lệch: 10 trong 42 lượt đánh giá SED có cờ dirty do chính script sinh ra tệp báo cáo
chưa commit; mã và cấu hình không đổi.

## Slide 7. RQ1: học thêm trên DataSEC không giúp SED tốt hơn

(1,5 phút) Kết quả âm tính. Với cả hai công thức huấn luyện và nhiều seed, nhánh C không hơn nhánh B
về event-F1: hiệu C − B có khoảng tin cậy chứa 0. Đừng hiểu là DataSEC vô ích: PSDS-2 của công thức
v2 có tăng, nhưng chưa hiệu chỉnh so sánh bội. Nhóm giữ nguyên kết quả âm tính và chuyển trọng tâm
sang mô tả bám sự kiện và hỏi đáp thời gian.

## Slide 8. Chẩn đoán: lỗi nằm ở biên sự kiện và bỏ sót, không ở nhận dạng lớp

(1,5 phút) Event-F1 của bản đầu rất thấp nên nhóm chẩn đoán trước khi cải tiến. Số đo trên dev: ngay cả
mô hình nhận dạng hoàn hảo nhưng quyết định theo khối 0,64 giây cũng chỉ tối đa 0,63; chỉ xét thời điểm
bắt đầu thì 0,23; trong 886 sự kiện, 357 bị bỏ sót và 417 đúng lớp nhưng lệch biên. Lỗi nằm ở biên và
bỏ sót, không phải nhận dạng. Đây là số dev in-sample dùng để chẩn đoán.

## Slide 9. Chọn bằng dự đoán ngoài mẫu: hệ B0, và vì sao không tin dev

(1,5 phút) Sau vòng chọn đầu, nhóm thấy xếp hạng trên 134 bản ghi dev không đáng tin: ba ứng viên
đều đảo chiều khi chạy dự đoán ngoài mẫu trên 564 bản ghi. Hệ B0 được chọn theo luật ghi trước. Trên
test, B0 hơn f2 không đáng kể về thống kê. Giai đoạn P thử thêm bốn hướng, không hướng nào vượt B0,
và test không được mở trong giai đoạn này.

## Slide 10. LBR: học sửa biên và chấm lại hộp sự kiện

(1,5 phút) Từ chẩn đoán lỗi, nhóm đề xuất LBR: hai mô hình boosting học trên xác suất ngoài mẫu. Bộ
tinh chỉnh dịch biên của hộp, bộ chấm lại ước lượng hộp có đúng không. Học lồng nhau để mô hình không
thấy fold nó chấm. V2 tối ưu khớp biên chặt; V3 tối ưu ít bỏ sót, dùng cho demo. Cấu hình V3 được ghi
trước khi mở test.

## Slide 11. Kết quả SED trên test: LBR V2 tăng event-F1 micro khoảng 1,6 lần

(2 phút) Trên test có nhãn, 139 bản ghi, mở một lần cho cấu hình đã khóa. LBR V2 đạt micro 0,2965 và
macro 0,2356; hiệu so với B0 là +0,116, khoảng tin cậy không chứa 0. Cái giá: độ phủ giảm — recall giao
nhau và segment-F1 của V2 thấp hơn B0. Vì vậy V3 ở điểm recall_first được dùng cho demo: phát hiện được
khoảng 82% sự kiện tham chiếu ở mức chồng lấn với precision 0,78, event-F1 micro 0,2287. Hai điểm vận
hành cho hai mục đích.

## Slide 12. PSDS phụ thuộc lưới ngưỡng; PSDS-2 của LBR thấp hơn B0

(1,5 phút) PSDS lấy từ đường PSD-ROC trên một tập ngưỡng, nên phụ thuộc lưới. Lưới tuyến tính mặc định
cắt phần lớn hộp của LBR; nhóm ghi trước lưới log và đo B0 trên cùng lưới. LBR có PSDS-1 cao hơn
nhưng PSDS-2 thấp hơn B0 rõ rệt, nhất quán với việc đổi độ phủ lấy độ chính xác. Chẩn đoán trên dev cho
hiện tượng v1 sang v2: lưới và độ lệch giữa các lớp giải thích phần lớn, nhưng đây chỉ là gợi ý.

## Slide 13. RQ2: ràng buộc ngữ pháp loại ảo giác ở cả bốn hệ SED

(2 phút) Bốn cách sinh trên cùng danh sách sự kiện của từng hệ SED, mức đầu–cuối, 139 bản ghi. Template
cho 0 ở mọi chỉ số — kiểm chứng bộ đo. Viết tự do hiếm khi bịa nguồn âm nhưng hay thêm bối cảnh
không có trong bằng chứng, 26 đến 40% số mô tả. Ngữ pháp giải mã đưa ảo giác, bối cảnh, gọi tên quá
mức và từ cấm về 0 ở cả bốn hệ. Cần nhớ: danh sách sự kiện là dự đoán của SED, nên 0 ảo giác không
có nghĩa mô tả đúng với âm thanh.

## Slide 14. RQ2: cái giá là bỏ sót khi danh sách dày — và các giới hạn của bộ đo

(1,5 phút) Ràng buộc có giá. Với V3, danh sách có 668 sự kiện, constrained chỉ nhắc một dãy con nên
bỏ sót 8,1% lớp, so với 1,2% ở f2; hiệu +0,069 khoảng tin cậy không chứa 0. Nhánh cover giải quyết
bằng cấu tạo. Giới hạn: bộ đo dựa trên từ điển, đối chiếu một người đọc trên 60 mô tả; và một lần
llama.cpp hết bộ nhớ GPU khi sinh V3 trên dev, nhóm khởi động lại và chạy tiếp — đã ghi trong ADR.

## Slide 15. RQ3: lọc cứng đúng tuyệt đối; xếp hạng bị chặn bởi SED dự đoán gì

(2 phút) Bốn kho sự kiện, cùng bộ 100 truy vấn, 97 câu có kết quả liên quan. Lọc cứng luôn đúng điều kiện.
f2, B0 và V2 không phân biệt được, dù V2 tăng event-F1 micro khoảng 1,6 lần: truy hồi bị chặn bởi việc SED
dự đoán những sự kiện nào. V3 cao hẳn vì độ phủ: trả lời được 95 trên 97 câu, nhưng tỷ lệ trích dẫn
đúng giảm từ 0,915 xuống 0,712. Vì vậy mức tăng nDCG không phải xếp hạng tốt hơn. Không câu trả lời nào
chứa khẳng định thiếu bằng chứng.

## Slide 16. Demo chạy trên máy cá nhân với LBR V3, không cần Internet

(1 phút) Demo chạy bằng Docker: cơ sở dữ liệu, dịch vụ suy luận, giao diện; mặc định phục vụ LBR V3.
Nếu cần chạy trực tiếp: scripts/demo_up.ps1 rồi mở http://127.0.0.1:8088. Lịch sử demo chỉ gồm bản ghi
tập train. Nếu live lỗi: dùng ảnh fallback hoặc bộ lọc thủ công.

## Slide 17. Hạn chế: những gì khóa luận không khẳng định

(1 phút) Nhóm nêu thẳng các hạn chế: tập test nhỏ; huấn luyện không tất định; PSDS phụ thuộc lưới;
bộ đo mô tả dựa từ điển; một số lượt đánh giá có cờ dirty; tra văn liệu mức khóa luận nên không
dùng chữ lần đầu; và ứng dụng chưa có xác thực.

## Slide 18. Kết luận và hướng phát triển

(1,5 phút) Tóm lại: nhóm có một quy trình tái lập đi từ dữ liệu đến câu trả lời có bằng chứng. Điểm
tiến bộ lớn nhất của SED là LBR; mô tả có ràng buộc loại ảo giác nguồn âm theo cấu tạo; truy hồi bị chặn
bởi những sự kiện SED dự đoán. Kết quả âm tính của RQ1 được giữ nguyên. Hướng tiếp theo ở bên phải.
Xin cảm ơn quý thầy cô, nhóm sẵn sàng trả lời câu hỏi.

## Slide 19

Chuyển sang hỏi đáp. Phụ lục: kết quả theo lớp, sổ ghi test, bộ phân tích câu hỏi.

## Slide 20. Event-F1 theo lớp của B0 và LBR V2 (test annotated)

Lớp dưới 10 mẫu chỉ báo số khớp tuyệt đối. 3 lớp V2 F1 bằng 0: birds, vehicle_idling, vehicle_pass_by.

## Slide 21. Sổ ghi mọi lần chạm test

Sổ sinh tự động từ các tệp kết quả đã khóa (test_ledger_20261111).

## Slide 22. Bộ phân tích câu hỏi: hợp lược đồ 240/240, lỗi ở điều kiện thời gian

Độ đúng ngữ nghĩa hoàn toàn 0,855 (template) và 0,925 (diễn đạt lại); lỗi chủ yếu đảo vai trò a/b, nhầm within/overlaps.
