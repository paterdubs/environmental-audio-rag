# TIẾN ĐỘ VÀ KẾ HOẠCH TIẾP THEO

## Tiến độ so với kế hoạch

Đề tài bắt đầu ngày 22/09/2026 với kế hoạch tám tuần, hạn nộp 09/11/2026 và một tuần dự phòng tới 16/11/2026. Kế hoạch gốc xếp công việc theo thứ tự phụ thuộc: kiểm tra dữ liệu, mô hình phân loại, SED, chỉ số đánh giá, sinh mô tả, truy hồi, ứng dụng, cuối cùng là viết báo cáo. ⟪tbl:schedule⟫ đối chiếu kế hoạch với thực tế tại mốc 03/10/2026.

@@CAP:tbl:schedule|Kế hoạch và tiến độ thực tế tại mốc 03/10/2026@@

| Hạng mục | Kế hoạch | Thực tế | Trạng thái |
|---|---|---|---|
| Dữ liệu D0–D4, tập chia đóng băng | 22–28/09 | Xong 23/09 | Đã kiểm chứng |
| Mô hình phân loại DataSEC | 29/09–05/10 | Xong 23/09 | Đã kiểm chứng |
| SED ba nhánh, chỉ số, phân tích lỗi (W3–W4) | 06–19/10 | Xong 24–26/09; RQ1 nhiều seed | Đã kiểm chứng |
| Cải tiến SED (v2, Track 2, chọn hệ cuối) | Thêm 26/09; khóa mô hình 18/10 | v2 chốt 26/09; khóa f2 ngày 29/09 | Đã kiểm chứng |
| Mô tả bám sát sự kiện (RQ2) | 20–26/10 | Xong 25–26/09; chạy lại trên f2 ngày 02/10 | Đã kiểm chứng |
| Kho sự kiện, RAG, truy hồi (RQ3) | 27/10–02/11 | Xong 26/09; bộ phân tích câu hỏi 28/09; chạy lại trên f2 ngày 02/10 | Đã kiểm chứng |
| API, giao diện, demo, đóng băng tệp kết quả | 03–09/11 | Xong 02/10 | Đã kiểm chứng |
| Viết báo cáo khóa luận | 19/10–09/11 | Báo cáo giữa kỳ này | Đang thực hiện |
| Slide bảo vệ | 03–09/11 | Chưa bắt đầu | Chưa thực hiện |

@@NOTE:Nguồn: docs/PLAN.md (bảng trạng thái tổng, khối Lộ trình tới hạn nộp); CLAUDE.md §10.@@

Phần kỹ thuật đi trước lịch vì các hạng mục không phụ thuộc nhau được làm song song và các thí nghiệm dài chạy theo hàng đợi ngoài giờ. Việc đi trước lịch không làm đổi kỷ luật đánh giá: mốc khóa mô hình dự kiến 18/10 được thực hiện sớm vào 29/09 khi mọi ứng viên ghi trước đã có đủ kết quả trên dev (ADR-0031), luật chọn vẫn ghi trước và lựa chọn vẫn commit trước khi mở test. Có ba hạng mục phát sinh ngoài kế hoạch gốc, đều do số đo chỉ ra: giai đoạn cải tiến SED (sau khi đo được giới hạn trên của v1), tập đánh giá `annotated` (sau khi phát hiện 14 bản ghi thiếu nhãn đa âm), và bộ phân tích câu hỏi thành bộ lọc (để giao diện nhận câu hỏi tự nhiên).

## Mức độ đạt mục tiêu

Đối chiếu với bảy việc nêu ở Chương 1:

- **Đã đạt và có bằng chứng: các việc (1), (2), (4), (5), (6), (7).** Quy trình dữ liệu có đủ nguồn gốc, các cổng kiểm tra đạt và tập chia khóa bằng mã băm; mô hình phân loại đạt macro-F1 0,8466; phép đo chuyển giao đã làm với nhiều seed (kết quả âm tính); bộ sinh mô tả có ràng buộc kiểm thử tự động cùng chỉ số ảo giác có khoảng tin cậy; truy hồi kết hợp có điều kiện thời gian và ba cấu hình so sánh được; ứng dụng web chạy đầu–cuối với kịch bản demo đã chạy thật.
- **Đạt về quy trình nhưng chất lượng còn thấp: việc (3), mô hình SED.** SED được đánh giá đúng chuẩn (event-F1 và PSDS), nhưng hệ khóa chỉ đạt event-F1 macro 0,1206 và micro 0,1643 trên test `annotated`, thấp so với giới hạn độ phân giải và giới hạn người đã đo.

Về ba câu hỏi nghiên cứu, cả ba đã có câu trả lời có bằng chứng:

- **RQ1:** âm tính về event-F1 với cả hai công thức huấn luyện.
- **RQ2:** ràng buộc ngữ pháp đưa ảo giác, suy diễn bối cảnh, gọi tên quá cụ thể và từ cấm về 0; cái giá là bỏ sót, và biến thể cover khử được cái giá này.
- **RQ3:** bộ lọc cứng bảo đảm đúng ràng buộc tuyệt đối nhưng xếp hạng bị chặn bởi chất lượng SED; khi đổi sang kho f2, các chế độ có lọc kém đi.

Mức khẳng định đóng góp giữ thận trọng như ở Chương 1: C1–C4 có bằng chứng thực nghiệm trong phạm vi đề tài, nhưng tính mới so với văn liệu chưa được khẳng định.

## Hạn chế

Các hạn chế về chất lượng SED, tập đánh giá nhỏ, tính không tất định, bộ đo dựa trên từ điển và sai lệch truy nguồn đã nêu ở Chương 6. Ngoài ra có hai hạn chế về phạm vi: nhóm mới đọc trực tiếp 14 nguồn, chưa tổng quan các mảng mô tả âm thanh tự động, truy hồi âm thanh và kiểm soát trùng lặp khi học chuyển giao, nên chưa có cơ sở khẳng định tính mới; và hệ thống chưa sẵn sàng triển khai thật (chưa có xác thực, chưa xử lý luồng, bản demo chạy CPU không trùng khít hoàn toàn với hệ đã đo).

## Kế hoạch giai đoạn tiếp theo

Từ sau báo cáo giữa kỳ đến hạn nộp 09/11/2026, nhóm ưu tiên hoàn thiện báo cáo cuối và bổ sung các phân tích làm rõ kết quả hiện có. Nhóm **không** mở rộng phạm vi và **không** chạy thêm đánh giá trên test cho hệ đã khóa (⟪tbl:nextplan⟫).

@@CAP:tbl:nextplan|Kế hoạch giai đoạn tiếp theo@@

| Thời gian | Công việc | Kết quả nghiệm thu |
|---|---|---|
| 04–12/10 | Nhận nhận xét giữa kỳ của giảng viên hướng dẫn; điều chỉnh đề cương báo cáo cuối | Danh sách chỉnh sửa có xác nhận |
| 04–18/10 | Khảo sát văn liệu có hệ thống (mô tả âm thanh tự động và ảo giác, truy hồi âm thanh, kiểm soát trùng lặp giữa các bộ dữ liệu, baseline trên DataSED) | Ba nhận định về tính mới được xác nhận hoặc rút lại |
| 06–18/10 | Giải thích vì sao PSDS không tăng khi event-F1 tăng, **chỉ trên dev**; phân tích tương quan lỗi giữa các họ mô hình trong ensemble | Báo cáo đo sinh bằng script |
| 06–18/10 | Mở rộng kiểm tra bộ đo mô tả: thêm người đọc, mẫu lớn hơn nếu kịp | Độ đồng thuận từ điển–người có khoảng tin cậy hẹp hơn |
| 19/10–02/11 | Viết báo cáo cuối kỳ hoàn chỉnh; duyệt cụm từ tiếng Việt của giao diện | Bản thảo đầy đủ gửi giảng viên |
| 03–09/11 | Hoàn thiện định dạng, slide bảo vệ, tập dượt demo | Bản nộp và slide |
| 10–16/11 | Dự phòng, chỉ dùng khi được gia hạn | — |

@@NOTE:Nguồn: docs/PLAN.md (L3–L6, nợ kỹ thuật #5, #6, #11); docs/PAPER_NOTES.md §6.@@

Các hướng dài hạn — tổng hợp âm thanh nền từ đoạn DataSEC để tạo nhãn mạnh cho lớp hiếm, huấn luyện chung nhãn mạnh và nhãn yếu, xử lý luồng thời gian thực, dữ liệu đa kênh — được ghi nhận nhưng **không** thuộc phạm vi khóa luận.

## Kết luận giữa kỳ

Tại thời điểm giữa kỳ, nhóm đã xây xong một hệ thống đầu–cuối tái lập được: từ dữ liệu công bố, qua phát hiện sự kiện và sinh mô tả bám sát sự kiện, đến truy vấn có trích dẫn. Mỗi tầng đều có phép đo, và mọi phép đo theo quy tắc chọn trên dev, kiểm tra một lần. Điều quan trọng nhất không phải một con số cao, mà là hệ thống *biết và đo được* giới hạn của mình:

- hai bộ dữ liệu có chung bản ghi gốc, và mức trùng đã được định lượng;
- huấn luyện thêm trên DataSEC không cải thiện SED;
- lỗi SED nằm ở biên sự kiện và ở bỏ sót;
- ràng buộc giải mã loại bỏ suy diễn với cái giá đo được;
- truy hồi bị chặn bởi recall của SED.

Giai đoạn tiếp theo tập trung làm rõ các kết quả này bằng phân tích trên dev và tổng quan văn liệu có hệ thống, rồi hoàn thiện báo cáo cuối đúng hạn.
