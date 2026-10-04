# Kịch bản trình bày slide giữa kỳ

> Sinh tự động bởi `scripts.build_midterm_slides` từ `report/slide.pptx`; sửa nội dung trong `scripts/midterm_slides/`, không sửa tay tệp này.

## Slide 1 — Bìa

Mở đầu (30 giây). Chào thầy, nhóm em gồm Phát và Tính, báo cáo giữa kỳ đề tài
"Xây dựng hệ thống phát hiện, sinh mô tả và truy vấn sự kiện âm thanh môi trường dựa trên RAG".
Bài trình bày có 6 phần; nhóm tập trung nhiều nhất vào phương pháp, kịch bản thí nghiệm và kết
quả.

## Slide 2 — Đề tài: nghe bản ghi dài, ghi lại sự kiện, viết mô tả và trả lời câu hỏi

(1 phút) Máy đo tiếng ồn hiện nay chỉ trả về một con số dB. Đề tài muốn máy làm được 4 việc
như cột bên phải: nhận một bản ghi dài, ghi lại sự kiện kèm thời điểm, viết câu mô tả, và trả
lời
câu hỏi về lịch sử có kèm bằng chứng. Ví dụ là bản ghi thật S-0009 trong tập dev.
Ba khó khăn: âm chồng nhau, dữ liệu có mốc thời gian ít, và mô hình ngôn ngữ dễ bịa.

## Slide 3 — Ba câu hỏi nghiên cứu (RQ) và những gì đề tài không làm

(1 phút) Ba câu hỏi nghiên cứu nói bằng lời thường. RQ1 hỏi việc học thêm có giúp không.
RQ2 hỏi câu mô tả có bịa không. RQ3 hỏi nên tìm kiếm theo cách nào.
Mỗi thẻ ghi luôn slide kết quả tương ứng để thầy dễ đối chiếu.
Ngoài phạm vi: không nghe nội dung lời nói, không suy ra tội phạm hay mức nguy hiểm, vì dữ liệu
không có cơ sở cho các kết luận đó.

## Slide 4 — Hệ thống: 5 bước từ file âm thanh tới câu trả lời có bằng chứng

(1 phút) Đi theo hình bên trái từ trên xuống. Bước 2 là mô hình SED; tham số ghép xác suất thành
sự kiện được chọn trên dev và lưu cạnh mô hình, nên đổi độ nhạy không cần huấn luyện lại.
Nhấn mạnh ô xanh: bộ viết mô tả chỉ đọc danh sách sự kiện, đây là cách "khóa" việc bịa nguồn âm.

## Slide 5 — Demo chạy được trên máy cá nhân, không cần Internet

(1 phút) Demo chạy bằng Docker trên máy cá nhân: cơ sở dữ liệu, dịch vụ suy luận và giao diện.
Nếu thầy muốn xem trực tiếp: chạy scripts/demo_up.ps1 rồi mở http://127.0.0.1:8088.
Lịch sử demo chỉ gồm bản ghi tập train để không lộ dữ liệu test.

## Slide 6 — Hai bộ dữ liệu cùng nhóm tác giả, bổ trợ cho nhau

(1 phút) DataSEC giống bộ thẻ học từ vựng: đoạn ngắn, mỗi đoạn một nhãn.
DataSED giống phim có phụ đề chi tiết: bản ghi dài, đánh dấu từng sự kiện bắt đầu và kết thúc
lúc nào.
DataSED là bài thi chính; DataSEC là tài liệu học thêm cho nhánh C của RQ1.

## Slide 7 — Hai bộ có chung bản ghi gốc, nên phải loại trùng trước khi học

(1,5 phút) Hai bộ dữ liệu cùng sáu tác giả nên nhóm giả định có trùng cho tới khi đo được điều
ngược lại.
Quy trình D0–D4 trong hình: kiểm tệp tải → kiểm kê → chuẩn hóa nhãn → tìm trùng → chia tập.
Tìm trùng ba tầng; tầng 3 so "vân tay âm thanh" (MFCC). Ngưỡng được hiệu chuẩn: cặp trùng thật
đạt
1,0000, cặp khác nhau cao nhất 0,9205, nên chọn ngưỡng 0,95.
Câu hỏi có thể gặp: "Loại 11 đoạn có đủ chưa?" → còn một rủi ro không đo được: hai bộ lấy một
phần âm
thanh từ AudioSet, mà mô hình nền cũng học AudioSet; nhóm ghi rõ đây là hạn chế.

## Slide 8 — Chia dữ liệu theo nhóm trùng và khóa lại trước khi huấn luyện

(1 phút) Train để học, dev để thử và chọn, test là bài thi thật chỉ làm một lần.
Không chia theo từng tệp mà theo nhóm trùng, để hai bản giống nhau không rơi vào hai phần khác
nhau.
Hai phát hiện phụ: 14 bản ghi thiếu nhãn (xử lý bằng tập annotated), và nhãn của chính con người
chỉ khớp nhau 0,58, nên điểm của máy cần đọc trong bối cảnh này.

## Slide 9 — Luật chơi: học trên train, chọn trên dev, thi test đúng một lần

(1,5 phút) Đây là luật chơi chống "học thuộc đề", áp dụng cho mọi kịch bản phía sau.
Ví dụ đọc điểm: tập test có 740 sự kiện thật, f2 báo 295, trong đó 85 đúng.
Precision 0,29 nghĩa là trong cái máy báo có khoảng 29% đúng; recall
0,11
nghĩa là máy chỉ tìm ra khoảng 11% sự kiện thật. Recall thấp là điểm nghẽn chính của hệ thống.
Các số này tính từ evaluation_cv_annotated.json đã khóa, không chạy lại test.

## Slide 10 — Sáu kịch bản thí nghiệm, mỗi kịch bản trả lời một câu hỏi

(1 phút) Bản đồ để thầy theo dõi: sáu kịch bản, mỗi cái trả lời một câu hỏi, cột cuối ghi slide
kết quả.
KB1 là RQ1; KB2–KB4 là chuỗi cải thiện mô hình phát hiện sự kiện; KB5 là RQ2; KB6 là RQ3.

## Slide 11 — KB1 (RQ1): ba cách khởi đầu, chỉ khác nhau ở bước học thêm

(1 phút) Ba nhánh có cùng điểm cuối: học phát hiện sự kiện trên DataSED. Khác nhau ở điểm khởi
đầu.
Câu hỏi RQ1 là C có hơn B không, vì hai nhánh này chỉ khác đúng một bước học thêm DataSEC.
Huấn luyện mô hình SED cho kết quả hơi khác nhau dù cùng seed, nên phải chạy nhiều lần và dùng
thống kê.
Kết quả ở slide 18.

## Slide 12 — KB2: đo xem mô hình đầu (v1) sai ở đâu, rồi mới sửa

(1 phút) Thay vì dò thử tham số, nhóm đo trước. Mô hình CNN14 bản v1 thu nhỏ trục thời gian 64
lần,
mỗi quyết định ứng với 0,64 giây, trong khi luật chấm chỉ cho lệch 0,2 giây; nên dù đoán đúng
loại 100%
điểm tối đa cũng chỉ 0,63. Phân loại lỗi trên dev cho thấy lỗi chủ yếu là lệch biên và bỏ sót.
v2 sửa đúng các chỗ này. Kết quả ở slide 19.

## Slide 13 — KB3: thử mô hình nền đã quen “nghe theo từng 40 ms”

(1 phút) Mô hình CNN14 được dạy để nói "đoạn này có tiếng gì". Hai mô hình nền T2a, T2b được dạy
sẵn để nói "lúc nào có tiếng gì" theo từng 40 ms, nên hợp với bài đánh dấu thời điểm hơn.
Hình bên trái so kiến trúc v1, v2 và f2. Mỗi cấu hình chạy 3 lần rồi lấy trung bình vì huấn
luyện
không ổn định. Ở bước này chỉ dùng dev; test chỉ mở ở vòng chọn cuối (KB4).

## Slide 14 — KB4: chọn hệ cuối bằng luật viết trước khi có kết quả

(1,5 phút) Đây là phần quan trọng để chống gian lận: luật chọn và danh sách 11 ứng viên được ghi
vào tài liệu (ADR-0031) trước khi có số; lựa chọn f2 được commit lên git trước khi tạo dự đoán
test.
Sau đó chấm test đúng một lần cho tất cả và báo hết, kể cả khi ứng viên khác có điểm test cao
hơn.
Mỗi ứng viên cũng chọn luôn cách ghép xác suất thành sự kiện; ngưỡng riêng từng loại bị loại vì
quá khớp dev (bằng chứng ở ablation A2 trên cả ba nhánh).

## Slide 15 — KB5 (RQ2): cùng một danh sách sự kiện, bốn cách viết mô tả

(1,5 phút) Cùng một danh sách sự kiện máy đoán cho S-0009, bốn cách viết cho ra bốn câu.
Câu viết tự do nghe tự nhiên nhưng tự thêm "in the forest" — đó là kiểu lỗi chính của mô hình
ngôn ngữ.
Cách constrained dùng một "ngữ pháp" sinh riêng cho từng bản ghi: mô hình chỉ được chọn từ tên
nguồn âm
và số giây có trong danh sách. Nó chỉ còn quyền chọn nhắc sự kiện nào và dừng ở đâu, nên có thể
bỏ sót;
bản cover chặn lỗi bỏ sót. Ba luật G1–G3 có kiểm thử tự động. Kết quả ở slide
22.

## Slide 16 — KB6 (RQ3): ba cách tìm, đo trên 100 câu hỏi mẫu

(1 phút) Ví dụ bên trái lấy từ lượt chạy demo thật: câu hỏi tiếng Việt được mô hình ngôn ngữ đổi
thành bộ lọc có điều kiện "trước", rồi hệ thống tìm và trả lời kèm thời điểm.
Ba cách tìm khác nhau ở chỗ có lọc cứng hay không. nDCG@10 thưởng cho việc đặt đáp án đúng ở vị
trí cao
trong 10 kết quả đầu. Kết quả ở slide 24.

## Slide 17 — Bộ phân loại DataSEC làm tốt bài dễ: macro-F1 0,85 trên 22 loại âm

(1 phút) Bộ phân loại học trên DataSEC đạt macro-F1 0,85 trên 22 loại âm. Đây là bài dễ hơn vì
chỉ
đoán loại cho đoạn ngắn đã cắt sẵn. Có một kết quả âm tính: hiệu chỉnh nhiệt độ làm sai số độ
tin cậy
tăng chứ không giảm, nhóm báo nguyên như vậy. Bảng theo từng loại ở Phụ lục.

## Slide 18 — RQ1: học thêm trên DataSEC không giúp tìm sự kiện tốt hơn

(1,5 phút) Kết quả âm tính. Với cả hai công thức, nhánh C có điểm hơi thấp hơn B, nhưng khoảng
tin cậy
của hiệu C − B chứa số 0 và p lớn hơn nhiều so với 0,05, nên không có khác biệt.
Bảng không in đậm vì không có giá trị nào "tốt nhất" có ý nghĩa. Nhóm giữ nguyên kết quả âm tính
này,
và vì vậy trọng tâm đóng góp chuyển sang C1, C2, C4 (mô tả bám sự kiện, cách đo, hỏi đáp thời
gian).
Nếu thầy hỏi "DataSEC có vô ích không": chỉ kết luận về event-F1; PSDS-2 ở v2 có tăng.

## Slide 19 — Vì sao v1 thấp, và v2 cải thiện được bao nhiêu

(1,5 phút) Bảng trái là chẩn đoán trên dev. Kiến trúc v1 quyết định theo khối 0,64 s nên điểm
tối đa
chỉ 0,63; người với người chỉ khớp 0,58. Phân rã lỗi: phần lớn là lệch biên và bỏ sót.
Bảng ablation: bỏ độ chi tiết thời gian làm tụt 0,084, lớn nhất; hai thay đổi còn lại nằm trong
nhiễu.
Trên test v2 hơn v1 rõ (+0,054, khoảng tin cậy không chứa 0) — đây là cải thiện có ý nghĩa duy
nhất.
Nhưng PSDS không tăng, nghĩa là v2 tốt hơn ở đúng điểm vận hành đã chọn; giải thích việc này là
việc
trong kế hoạch tiếp theo. Lưu ý: số bảng trái là số dev in-sample, chỉ dùng để chẩn đoán.

## Slide 20 — Chọn hệ cuối: f2 đứng đầu trên dev, nhưng test xếp hạng khác

(1,5 phút) Hình trái: chấm cam là điểm trên dev (trung bình 5 phần), chấm xanh là điểm test với
khoảng tin cậy.
Theo luật ghi trước, f2 đứng đầu dev nên được chọn, nhưng f2 chỉ hơn f4 0,003 — nhỏ hơn độ dao
động.
Trên test thứ hạng khác: f1 và g1 cao hơn. Nhóm không đổi sang f1, vì chọn theo điểm test là
gian lận,
và khoảng tin cậy các ứng viên đầu đều chồng nhau. Đây là minh chứng cho sai số khi chọn trên
dev nhỏ.
Bảng đầy đủ 11 ứng viên ở Phụ lục 1.

## Slide 21 — v1 → v2 → f2: tiến bộ rõ so với v1, nhưng f2 chưa chắc hơn v2

(1 phút) So ba thế hệ trên cùng tập test annotated. f2 hơn v1 rõ ở micro. So với v2 thì không
kết luận
được: f2 cao hơn ở micro và PSDS-2 nhưng thấp hơn ở macro và PSDS-1.
Điểm yếu lớn nhất của f2 là bỏ sót: báo 295 sự kiện trong khi có 740 sự kiện thật; 7 loại âm
điểm 0.
Bảng theo từng loại âm ở Phụ lục 4.

## Slide 22 — RQ2: ép theo luật đưa “bịa” và “thêm bối cảnh” về 0, đổi lại dễ bỏ sót

(1,5 phút) Đọc theo cột: mỗi cột là một loại lỗi, càng thấp càng tốt; số in đậm là thấp nhất
trong mỗi mức chấm.
Phát hiện bất ngờ: viết tự do ít khi bịa ra nguồn âm, nhưng hay "thêm mắm muối": 40% câu
đầu–cuối thêm bối
cảnh, khoảng 14% gọi tên quá cụ thể (nói "xe cứu thương" khi nhãn chỉ là "còi").
Ép theo ngữ pháp đưa các lỗi này về 0; cái giá là bỏ sót ở mức oracle. Bản cover khử được cái
giá này.
Hiệu bối cảnh constrained − unconstrained ở đầu–cuối là −0,401 [−0,479; −0,324].

## Slide 23 — RQ2: “không bịa” chưa có nghĩa là “đúng với âm thanh”

(1 phút) Đây là giới hạn quan trọng nhất của RQ2. Hình trên: nhãn gốc; hình dưới: hệ f2 dự đoán.
Câu mô tả đúng với danh sách dự đoán, nhưng so với âm thanh thật thì sai vị trí máy bay và bỏ
sót 4 sự kiện.
Nhóm tách rõ hai mức: oracle đo riêng bộ viết mô tả; đầu–cuối đo cả hệ thống.

## Slide 24 — RQ3: lọc cứng luôn đúng điều kiện, nhưng xếp hạng phụ thuộc SED

(1,5 phút) Đọc theo từng kho: số in đậm là tốt nhất trong mỗi kho. Hàng xám là cấu hình demo
dùng.
Cách có lọc luôn đúng điều kiện 100%. Cách chỉ theo nghĩa có nDCG cao trên kho f2 nhưng 73% kết
quả sai điều kiện,
ví dụ hỏi "dài hơn 30 giây" vẫn trả bản ghi ngắn.
Khi đổi sang kho f2, điểm của hai cách có lọc giảm — nhóm báo nguyên kết quả kém đi. Giả thuyết:
f2 bỏ sót
nhiều sự kiện nên kho thiếu, bộ lọc loại mất bản ghi đúng. Muốn cải thiện phải nâng recall của
SED.

## Slide 25 — Bộ đổi câu hỏi ra bộ lọc đúng khuôn 100%, hiểu đúng nghĩa 86–93%

(1 phút) Bộ đổi câu hỏi dùng mô hình ngôn ngữ bị ép theo lược đồ JSON nên luôn đúng khuôn
240/240.
Hiểu đúng nghĩa hoàn toàn 85,5% trên câu mẫu và 92,5% trên câu diễn đạt lại; lỗi ở điều kiện
thời gian.
Bảng dưới kiểm tra hệ đang phục vụ: trên GPU trùng khít 100%; trên CPU (demo) lệch nhẹ do phép
tính số thực khác.

## Slide 26 — Tổng kết: hệ thống chạy đầu–cuối; điểm nghẽn là SED còn bỏ sót

(1 phút) Tóm tắt ba câu trả lời. Điểm yếu lớn nhất là bước phát hiện sự kiện: recall thấp kéo
theo
cả câu mô tả lẫn kết quả tìm kiếm. Các hạn chế đều được ghi trong báo cáo, kể cả sự cố cờ dirty.

## Slide 27 — Tiến độ: phần kỹ thuật đi trước lịch, kỷ luật đánh giá giữ nguyên

(45 giây) Phần kỹ thuật đã xong sớm hơn lịch vì các việc độc lập được làm song song và thí
nghiệm dài
chạy theo hàng đợi ngoài giờ. Mốc khóa mô hình dự kiến 18/10 được làm sớm vào 29/09, nhưng luật
chọn
vẫn ghi trước và lựa chọn vẫn commit trước khi mở test. Còn lại: viết báo cáo cuối và slide bảo
vệ.

## Slide 28 — Kế hoạch đến hạn nộp 09/11: làm rõ kết quả, không mở rộng phạm vi

(45 giây) Ưu tiên: nhận góp ý của thầy, tổng quan văn liệu có hệ thống để kiểm tra tính mới,
giải thích vì sao PSDS không tăng (chỉ trên dev), rồi viết báo cáo cuối.
Nhóm xin thầy góp ý về phạm vi và cách trình bày kết quả âm tính.

## Slide 29 — Hỏi đáp

Câu hỏi có thể gặp:
- "Event-F1 0,16 có quá thấp?" → DCASE 2016 (ghi âm đời thực) chỉ 4,7–6,3%, chỉ để định cỡ;
  người với người chỉ khớp 0,58; lỗi chủ yếu là biên và bỏ sót.
- "Sao không chọn f1 khi test cao hơn?" → chọn theo test là học thuộc đề; khoảng tin cậy chồng
nhau.
- "RQ1 âm tính thì DataSEC vô ích?" → chỉ kết luận về event-F1; PSDS-2 ở v2 có tăng (p = 0,019).
- "Sao kết hợp lại kém chỉ lọc?" → tài liệu dạng khuôn, xếp theo nghĩa trong tập đã lọc không
giúp (−0,042).
- "Không bịa có nghĩa là đúng?" → không, chỉ đúng với danh sách máy đoán (slide 23).
- "Có tự gán nhãn thêm không?" → không sửa nhãn gốc; 14 bản ghi thiếu nhãn xử lý bằng tập
annotated.

## Slide 30 — Phụ lục 1 — Đầy đủ 11 ứng viên: kiểm chứng chéo dev và test

## Slide 31 — Phụ lục 2 — RQ3 đầy đủ: bộ lọc chuẩn (gold) và bộ lọc máy đổi (parsed)

## Slide 32 — Phụ lục 3 — RQ2 ở mức đầu–cuối: hệ v1 so với hệ f2 (test)

## Slide 33 — Phụ lục 4 — Event-F1 theo từng loại âm của hệ f2 (test annotated)

## Slide 34 — Phụ lục 5 — Bộ phân loại DataSEC theo 22 loại âm gộp (test)

## Slide 35 — Phụ lục 6 — Ablation v2 (dev) và sổ ghi các lần chạm tập test

## Slide 36 — Phụ lục 7 — Từ điển thuật ngữ
