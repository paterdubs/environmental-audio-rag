# TIẾN ĐỘ, KẾT LUẬN GIỮA KỲ VÀ KẾ HOẠCH TIẾP THEO

## Đối chiếu tiến độ với kế hoạch

Đề tài bắt đầu ngày 22/09/2026 với kế hoạch tám tuần, hạn nộp 09/11/2026 và một tuần dự phòng tới 16/11/2026. Kế hoạch gốc xếp các hạng mục theo thứ tự phụ thuộc: cổng dữ liệu, mô hình phân loại, SED ba nhánh, metric SED, sinh mô tả, truy hồi, ứng dụng, và cuối cùng là viết báo cáo. ⟪tbl:schedule⟫ đối chiếu kế hoạch với thực tế tại mốc chốt báo cáo (03/10/2026).

@@CAP:tbl:schedule|Đối chiếu kế hoạch và tiến độ thực tế tại mốc 03/10/2026@@

| Hạng mục | Kế hoạch | Thực tế | Trạng thái |
|---|---|---|---|
| W1 – Cổng dữ liệu D0–D4, tài liệu | 22–28/09 | Hoàn tất 23/09; tập chia đóng băng | Đã kiểm chứng |
| W2 – Mô hình phân loại DataSEC, PANNs | 29/09–05/10 | Hoàn tất 23/09 | Đã kiểm chứng |
| W3 – SED ba nhánh, hậu xử lý | 06–12/10 | Hoàn tất 24/09; RQ1 nhiều seed | Đã kiểm chứng |
| W4 – Event-F1, PSDS, phân tích lỗi | 13–19/10 | Hoàn tất 26/09 | Đã kiểm chứng |
| Cải tiến SED (v2, Track 2, vòng chọn S13) | Thêm 26/09; khóa mô hình 18/10 | v2 chốt 26/09; S13 khóa f2 ngày 29/09 | Đã kiểm chứng |
| W5 – Mô tả có căn cứ, metric ảo giác | 20–26/10 | Hoàn tất 25–26/09; chạy lại trên f2 ngày 02/10 | Đã kiểm chứng |
| W6 – Kho sự kiện, RAG, benchmark truy hồi | 27/10–02/11 | Hoàn tất 26/09; bộ phân tích câu hỏi 28/09; chạy lại trên f2 ngày 02/10 | Đã kiểm chứng |
| W7 – API, giao diện, demo, đóng băng artifact | 03–09/11 | Hoàn tất 02/10 | Đã kiểm chứng |
| Viết báo cáo khóa luận (L3) | 19/10–09/11 | Báo cáo giữa kỳ này | Đang thực hiện |
| Slide bảo vệ (L4) | 03–09/11 | Chưa bắt đầu | Chưa thực hiện |

@@NOTE:Nguồn: docs/PLAN.md (bảng trạng thái tổng, khối Lộ trình tới hạn nộp); CLAUDE.md §10.@@

Phần kỹ thuật vượt xa tiến độ dự kiến, vì các hạng mục không phụ thuộc nhau được làm song song và các thí nghiệm dài được chạy theo hàng đợi ngoài giờ. Việc đi trước lịch không làm thay đổi kỷ luật đánh giá. Mốc khóa mô hình dự kiến 18/10 được thực hiện sớm vào 29/09, khi mọi ứng viên ghi trước đã có đủ kết quả trên dev (ADR-0031 §9); luật chọn vẫn được ghi trước và lựa chọn vẫn được commit trước khi mở test. Ngoài ra, có ba hạng mục phát sinh ngoài kế hoạch gốc, đều do đo đạc chỉ ra:

- giai đoạn cải tiến SED, sau khi đo được giới hạn trên của kiến trúc v1;
- tập đánh giá `annotated`, sau khi phát hiện 14 bản ghi thiếu nhãn đa âm;
- bộ phân tích câu hỏi thành bộ lọc, để giao diện nhận câu hỏi tự nhiên.

## Mức độ đạt mục tiêu tại giữa kỳ

Đối chiếu với bảy mục tiêu cụ thể ở ⟪tbl:objectives⟫:

- **Đã đạt và có bằng chứng: O1, O2, O4, O5, O6 và O7.**
  - Quy trình dữ liệu có đủ nguồn gốc, các cổng kiểm tra đạt, tập chia đóng băng bằng hash (O1).
  - Mô hình phân loại DataSEC đạt macro-F1 0,8466 trên lớp gộp (O2).
  - Phép đo chuyển giao đã thực hiện với nhiều seed và cho kết quả âm tính (O4).
  - Bộ sinh mô tả có ràng buộc kiểm thử tự động cùng bộ metric ảo giác có khoảng tin cậy (O5).
  - Truy hồi lai có vị từ thời gian và ba cấu hình so sánh được (O6).
  - Ứng dụng web chạy đầu–cuối, kèm kịch bản demo đã chạy thật (O7).
- **Đạt về quy trình nhưng chất lượng còn thấp: O3.** Mô hình SED được đánh giá đúng chuẩn bằng event-based F1 và PSDS, nhưng hệ được khóa chỉ đạt event-F1 macro 0,1206 và micro 0,1643 trên test annotated. Con số này thấp so với trần độ phân giải và trần người đã đo.

Về câu hỏi nghiên cứu, cả ba đều đã có câu trả lời có bằng chứng:

- **RQ1:** âm tính về event-F1 với cả hai công thức huấn luyện.
- **RQ2:** ràng buộc ngữ pháp đưa ảo giác, suy diễn bối cảnh, gọi tên quá cụ thể và từ cấm về 0. Cái giá là bỏ sót, và biến thể cover khử được cái giá này.
- **RQ3:** bộ lọc cứng bảo đảm tính đúng ràng buộc tuyệt đối, nhưng xếp hạng bị chặn bởi chất lượng SED; khi đổi sang kho f2, hiệu năng các chế độ có lọc suy giảm.

Mức độ khẳng định đóng góp được giữ thận trọng như ở ⟪tbl:contrib⟫: các đóng góp C1–C4 đã có bằng chứng thực nghiệm trong phạm vi đề tài, nhưng tính mới so với văn liệu chưa được khẳng định.

## Hạn chế

Các hạn chế chính, theo thứ tự ảnh hưởng tới kết luận:

- **Chất lượng SED thấp.** Lỗi chủ yếu nằm ở bỏ sót và biên sự kiện, và nó giới hạn mọi tầng phía sau. "Không ảo giác" của mô tả chỉ có nghĩa trong phạm vi dòng thời gian dự đoán.
- **Tập đánh giá nhỏ và mô hình không tất định.** Khoảng tin cậy rộng, phần lớn chênh lệch giữa các ứng viên mạnh không phân biệt được, và các ablation chỉ có một seed. Nguyên nhân không tất định của huấn luyện SED chưa được xác định.
- **Bộ đo mô tả dựa trên từ điển.** Bộ đo chỉ được đối chiếu với một người đọc trên 60 mô tả.
- **Văn liệu chưa được tổng quan có hệ thống.** Đề tài mới đọc trực tiếp 14 nguồn; chưa tổng quan các mảng mô tả âm thanh tự động, truy hồi âm thanh và kiểm soát rò rỉ trong học chuyển giao. Vì vậy, chưa có cơ sở khẳng định tính mới.
- **Sai lệch truy nguồn ở hai vòng chạy test.** Các trường hợp `dirty` được công khai, không ảnh hưởng nội dung mã hay cấu hình, nhưng vẫn là một khiếm khuyết quy trình.
- **Hệ thống chưa sẵn sàng triển khai thật.** Chưa có xác thực, chưa xử lý luồng, và bản demo chạy CPU không trùng khít hoàn toàn với hệ đã đo.

## Kế hoạch giai đoạn tiếp theo

Giai đoạn còn lại (từ sau báo cáo giữa kỳ tới hạn nộp 09/11/2026) ưu tiên hoàn thiện báo cáo cuối và bổ sung những phân tích làm rõ kết quả đã có. Đề tài **không** mở rộng phạm vi và **không** chạy thêm đánh giá trên test cho hệ đã khóa (⟪tbl:nextplan⟫).

@@CAP:tbl:nextplan|Kế hoạch giai đoạn tiếp theo@@

| Thời gian | Công việc | Kết quả nghiệm thu |
|---|---|---|
| 04–12/10 | Tiếp nhận nhận xét giữa kỳ của giảng viên hướng dẫn; điều chỉnh đề cương báo cáo cuối | Danh sách chỉnh sửa có xác nhận |
| 04–18/10 | Khảo sát văn liệu có hệ thống (mô tả âm thanh tự động và ảo giác, truy hồi âm thanh, kiểm soát rò rỉ xuyên dataset, baseline trên DataSED); đọc trực tiếp và ghi mức xác minh | Ba nhận định về tính mới được xác nhận hoặc rút lại |
| 06–18/10 | Giải thích vì sao PSDS không tăng khi event-F1 tăng (PSDS theo lớp, đường ROC, điểm vận hành) **chỉ trên dev**; phân tích tương quan lỗi giữa các họ mô hình trong ensemble | Báo cáo đo sinh bằng script |
| 06–18/10 | Mở rộng kiểm tra bộ đo mô tả: thêm người đọc và mẫu lớn hơn, nếu kịp | Độ đồng thuận lexicon–người có khoảng tin cậy hẹp hơn |
| 19/10–02/11 | Viết báo cáo khóa luận cuối kỳ hoàn chỉnh trên khung của báo cáo này; duyệt cụm từ tiếng Việt của giao diện | Bản thảo đầy đủ gửi giảng viên hướng dẫn |
| 03–09/11 | Hoàn thiện định dạng, slide bảo vệ, tập dượt demo | Bản nộp và slide |
| 10–16/11 | Dự phòng, chỉ dùng khi được gia hạn | — |

@@NOTE:Nguồn: docs/PLAN.md (L3–L6, nợ kỹ thuật #5, #6, #11); docs/PAPER_NOTES.md §6.@@

Các hướng phát triển dài hạn, như tổng hợp soundscape từ đoạn DataSEC để tạo nhãn mạnh cho lớp hiếm, huấn luyện chung nhãn mạnh và nhãn yếu, xử lý luồng thời gian thực, hay mở rộng sang dữ liệu đa kênh, được ghi nhận nhưng **không** nằm trong phạm vi khóa luận.

## Kết luận giữa kỳ

Tại thời điểm giữa kỳ, đề tài đã xây dựng xong một hệ thống đầu–cuối tái lập được: từ bộ dữ liệu công bố, qua phát hiện sự kiện, sinh mô tả có căn cứ, tới truy vấn có trích dẫn. Mỗi tầng đều có phép đo đi kèm, và mọi phép đo được thực hiện theo giao thức chọn trên dev, kiểm tra một lần. Kết quả quan trọng nhất không nằm ở một con số cao, mà ở chỗ hệ thống *biết và đo được* giới hạn của mình:

- hai bộ dữ liệu có chung bản ghi gốc, và mức rò rỉ đã được định lượng;
- tiền huấn luyện thêm trên DataSEC không cải thiện SED;
- lỗi SED nằm ở biên sự kiện và ở bỏ sót;
- ràng buộc giải mã loại bỏ suy diễn với cái giá đo được;
- truy hồi bị chặn bởi recall của SED.

Giai đoạn tiếp theo tập trung làm rõ các kết quả này bằng phân tích trên dev và tổng quan văn liệu có hệ thống, rồi hoàn thiện báo cáo cuối kỳ đúng hạn.
