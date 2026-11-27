# CƠ SỞ LÝ THUYẾT

Chương này tóm tắt kiến thức nền mà đề tài dùng. Các nguồn trích trong chương đều được nhóm đọc toàn văn.

## Phát hiện sự kiện âm thanh

Phát hiện sự kiện âm thanh (SED) trả lời câu hỏi "cái gì xảy ra và khi nào". Đầu ra gồm lớp sự kiện cùng thời điểm bắt đầu và kết thúc [@mesaros2021tutorial]. Vì nhiều nguồn có thể vang cùng lúc, SED đa âm là bài toán phân loại **nhiều nhãn cho từng khung thời gian**, không phải gán một nhãn cho cả đoạn.

Có hai kiểu nhãn [@mesaros2021tutorial]. Nhãn mạnh ghi rõ khoảng thời gian của từng sự kiện. Nhãn yếu chỉ cho biết lớp nào có mặt trong bản ghi. Nhãn mạnh tốn công hơn vì người gán phải nghe lại và đặt biên cho từng sự kiện, mà biên của âm thanh môi trường vốn không rõ nét. DataSEC có nhãn theo đoạn, còn DataSED có nhãn mạnh [@fredianelli2025environmental].

Đầu vào thường dùng là phổ log-mel, một "ảnh" thời gian–tần số của tín hiệu. Kiến trúc phổ biến là mạng tích chập hồi quy (CRNN) [@mesaros2021tutorial]: phần tích chập (CNN) trích đặc trưng từ ảnh phổ, phần hồi quy (ở đây là BiGRU) học quan hệ theo thời gian. Mô hình cho ra xác suất của từng lớp tại từng khung. Chuỗi xác suất này chưa phải là sự kiện; nó phải qua bước ghép thành đoạn (mục "Từ xác suất đến sự kiện" bên dưới). Vì vậy chất lượng phát hiện phụ thuộc cả mô hình lẫn bước ghép, và cả hai đều phải được chọn trên tập phát triển, không chọn trên tập kiểm tra.

## Chỉ số đánh giá SED

**Event-F1.** Mesaros và cộng sự phân biệt chỉ số theo đoạn (chia trục thời gian thành các đoạn cố định, ví dụ 1 s, rồi so từng đoạn) với chỉ số theo sự kiện (so từng sự kiện dự đoán với sự kiện tham chiếu cùng lớp) [@mesaros2016metrics]. Một cặp được coi là khớp khi thời điểm bắt đầu lệch không quá một dung sai (collar). Đề tài dùng dung sai $\tau = 0{,}2$ s cho thời điểm bắt đầu; với thời điểm kết thúc, dung sai là

$$\Delta_{off} \le \max\left(\tau,\ \rho \cdot L_{ref}\right), \qquad \tau = 0{,}2\ \text{s},\ \rho = 0{,}2$$

⟪eqno:collar⟫

với $L_{ref}$ là độ dài sự kiện tham chiếu. Gọi $TP$, $FP$, $FN$ là số sự kiện phát hiện đúng, báo nhầm và bỏ sót. Precision, recall và F1 (gọi là event-F1) là

$$P = \frac{TP}{TP+FP}, \qquad R = \frac{TP}{TP+FN}, \qquad F_1 = \frac{2PR}{P+R}$$

⟪eqno:f1⟫

**Micro và macro.** Khi gộp nhiều lớp có hai cách [@mesaros2016metrics]. *Micro* cộng dồn $TP$, $FP$, $FN$ của mọi lớp rồi mới tính F1, nên các lớp có nhiều sự kiện chi phối kết quả. *Macro* tính F1 riêng từng lớp rồi lấy trung bình, nên mỗi lớp có trọng số như nhau:

$$F_1^{micro} = F_1\Big(\sum_c TP_c,\ \sum_c FP_c,\ \sum_c FN_c\Big), \qquad F_1^{macro} = \frac{1}{|\mathcal{C}|}\sum_{c \in \mathcal{C}} F_{1,c}$$

⟪eqno:micromacro⟫

Báo cáo nêu cả hai. Việc chọn hệ thống dùng micro, vì luật chọn đã được ghi trước bằng micro và micro ít dao động hơn trên tập phát triển nhỏ.

**PSDS.** Event-F1 gắn với một ngưỡng duy nhất. PSDS (Polyphonic Sound Detection Score) đánh giá trên cả **dải** ngưỡng và dùng tỷ lệ chồng lấp thời gian thay cho dung sai [@bilen2020psds]. Nhóm dùng hai kịch bản chuẩn: PSDS-1 nhấn mạnh định vị đúng thời điểm, PSDS-2 nhấn mạnh tránh nhầm lớp. Một hệ thống có thể tốt ở kịch bản này mà kém ở kịch bản kia.

**Mức khó của bài toán.** Ở thử thách DCASE (Detection and Classification of Acoustic Scenes and Events) 2016, nhiệm vụ 3 với ghi âm đời thực, 16 hệ nộp đạt event-F1 chỉ xét thời điểm bắt đầu từ 1,5% đến 8,1% [@dcase2016task3]. Con số này chỉ để hình dung độ khó; nó không so trực tiếp được với kết quả của đề tài vì khác dữ liệu, số lớp và cách chấm.

## Từ xác suất đến sự kiện

Cách ghép phổ biến là làm mượt chuỗi xác suất bằng lọc trung vị, so với một ngưỡng $\theta_c$, nối các khoảng trống ngắn và bỏ sự kiện quá ngắn. Các giới hạn độ dài được suy từ thống kê nhãn của tập huấn luyện; suy từ chính tập đang chấm là một dạng rò rỉ khó thấy.

Ebbers và cộng sự chỉ ra rằng ngưỡng theo khung gắn chặt biên sự kiện với độ tin cậy: ngưỡng càng cao, thời điểm bắt đầu càng bị đẩy về nơi xác suất *đạt* ngưỡng, chứ không phải nơi xác suất bắt đầu tăng [@ebbers2024sound]. Họ đề xuất hộp bao sự kiện (SEBB): ngưỡng chỉ quyết định giữ hay bỏ sự kiện, không dời biên. Biến thể cSEBB tìm biên tại điểm xác suất đổi hướng. Trên 13 hệ thống của DCASE 2023, cSEBB tăng trung bình 4,1 điểm PSDS1 và 3,4 điểm F1 so với lọc trung vị [@ebbers2024sound]. Kết quả đó đo trên dữ liệu khác, nên nhóm xem cSEBB là một lựa chọn cần kiểm tra trên tập phát triển, không mặc định là tốt hơn.

Một hướng khác là sửa biên ngay trong lúc huấn luyện. Schmid và cộng sự thêm vào mô hình các bộ phận học riêng thời điểm bắt đầu và kết thúc; trên AudioSet-Strong, cách này nâng PSDS1 của một mô hình CRNN từ 41,1 lên 48,0 [@schmid2026boundary]. Cách đó cần huấn luyện lại mô hình. LBR của khóa luận (Chương 4) làm việc khác: học sửa biên **sau** mô hình, trên xác suất đã có, nên không phải huấn luyện lại mô hình gốc.

## Học chuyển giao

**Tiền huấn luyện trên AudioSet.** Kong và cộng sự công bố họ mạng PANNs, huấn luyện trên AudioSet (hơn 5.000 giờ, 527 lớp) rồi chuyển sang sáu tác vụ âm thanh khác [@kong2020panns]. Mạng CNN14 của họ là điểm xuất phát của nhánh B và C trong RQ1. Với SED, các lớp gộp (pooling) của mạng làm giảm độ phân giải theo thời gian; Chương 6 cho thấy điều này đặt một giới hạn trên đo được cho event-F1.

**Tiền huấn luyện theo khung.** Schmid và cộng sự tiền huấn luyện mô hình âm thanh trên nhãn **theo khung** của AudioSet Strong, cho đầu ra mỗi 40 ms. Trên bộ dữ liệu DESED, chỉ huấn luyện thêm một lớp tuyến tính trên bộ mã hóa đóng băng đã đạt PSDS1 45,4 đến 49,2, gần với tinh chỉnh toàn bộ (47,6 đến 49,2) [@schmid2025effective]. Từ kết quả này, nhóm thử hai bộ mã hóa loại đó: BEATs, một mô hình tự giám sát [@chen2022beats], và Frame-MobileNet [@schmid2025effective]. Các con số trên đo trên DESED, nên chỉ là lý do để thử, không phải dự báo kết quả.

**Tăng cường dữ liệu.** Mixup huấn luyện trên tổ hợp tuyến tính của hai mẫu và nhãn của chúng [@zhang2018mixup]. FilterAugment nhân trọng số ngẫu nhiên lên các dải tần để mô phỏng môi trường âm học khác nhau; trên SED, nó tăng PSDS 6,50% so với 2,13% của cách che dải tần [@nam2022filteraugment].

**Trùng lặp giữa các bộ dữ liệu.** Chuyển giao chỉ có nghĩa khi dữ liệu kiểm tra không nằm trong dữ liệu tiền huấn luyện. Bài mô tả DataSEC và DataSED cho biết một phần âm thanh lấy từ Freesound và AudioSet [@fredianelli2025environmental]. Vì vậy hai bộ có thể chung bản ghi gốc (nhóm kiểm tra ở Chương 3), và mô hình tiền huấn luyện trên AudioSet có thể đã "nghe" một phần âm thanh gốc. Rủi ro thứ hai này không định lượng được vì danh sách nguồn không được công bố.

## Mô tả bám sát sự kiện và ảo giác

Ji và cộng sự định nghĩa ảo giác trong sinh văn bản là nội dung "vô nghĩa hoặc không trung thành với nguồn được cung cấp" [@ji2023hallucination]. Ở đề tài, "nguồn" là danh sách sự kiện, nên ảo giác được định nghĩa hẹp và kiểm tra được: mô tả nhắc một nguồn âm không có trong danh sách là ảo giác; mô tả đặt sai thứ tự hai sự kiện cũng là lỗi.

Cách định nghĩa này cho phép đo ảo giác **mà không cần câu mô tả mẫu do người viết**. Trong lĩnh vực mô tả âm thanh tự động (AAC) đã có chỉ số gần: Kuan và cộng sự đề xuất ECHO, tính tỷ lệ đối tượng được nhắc mà không có trong nhãn thật [@kuan2024echo]; ECHO không xét thời gian hay thứ tự. Kumar và cộng sự mô tả âm thanh kèm mốc thời gian và đo ảo giác bằng một mô hình chấm độ khớp âm thanh–văn bản [@kumar2026tac]. Chỉ số của nhóm khác ở chỗ so mô tả với **dòng thời gian sự kiện đã phát hiện**, bằng các luật máy kiểm tra được (độ phủ, khẳng định thiếu bằng chứng, thứ tự, từ cấm, gọi tên quá cụ thể). Vì đã có công trình gần, báo cáo coi đây là áp dụng và mở rộng.

## Truy hồi và RAG

Lewis và cộng sự đề xuất RAG: kết hợp một mô hình sinh với một kho dữ liệu ngoài, truy cập qua bộ truy hồi [@lewis2020rag]. Nhóm áp dụng ý tưởng này với hai thay đổi. Kho ngoài là các sự kiện có cấu trúc (lớp, bắt đầu, kết thúc, độ tin cậy) thay vì văn bản tự do. Câu trả lời bắt buộc kèm bằng chứng (mã bản ghi, khoảng thời gian).

Để câu hỏi tiếng Việt và tiếng Anh dùng chung một kho, nhóm dùng mô hình nhúng đa ngữ BGE-M3, hỗ trợ hơn 100 ngôn ngữ [@chen2024m3]. Độ tương đồng vector hợp với câu hỏi mang tính ngữ nghĩa, nhưng không bảo đảm các điều kiện cứng như "sự kiện dài hơn 30 giây" hay "tiếng kính vỡ trước tiếng còi". Các điều kiện đó là phép so sánh số và phép nối theo thời gian, nên được xử lý bằng bộ lọc trong cơ sở dữ liệu. Truy hồi kết hợp lọc theo điều kiện trước, rồi xếp hạng theo vector trong tập đã lọc.

Hệ thống gần nhất với hướng này là LA-RAG: chuyển âm thanh dài thành bản ghi sự kiện có mốc thời gian lưu trong cơ sở dữ liệu SQL, đổi biểu thức thời gian tuyệt đối (ví dụ "trước buổi trưa") thành cửa sổ thời gian, rồi truy xuất bằng độ tương đồng kèm bộ lọc trước khi để mô hình ngôn ngữ trả lời [@hegde2026larag]. Trong công trình đó, nhóm không thấy điều kiện quan hệ **giữa hai sự kiện** (trước, sau, chồng nhau, nằm trong); đề tài bổ sung bốn điều kiện loại này bằng SQL.

Chất lượng truy hồi được đo bằng nDCG@10, chỉ số thưởng cho kết quả liên quan được xếp cao; công thức ở Chương 4.

## Ba kỹ thuật dùng trong hệ thống

**Giải mã có ràng buộc bằng ngữ pháp.** Mô hình ngôn ngữ sinh từng token $y_t$ theo phân phối $p(y_t \mid y_{<t}, x)$. Giải mã có ràng buộc chỉ giữ những token mà sau khi thêm vào, chuỗi vẫn là phần đầu của một câu thuộc ngôn ngữ $L(G)$ của ngữ pháp $G$:

$$p_G(y_t \mid y_{<t}, x) \propto p(y_t \mid y_{<t}, x)\cdot \mathbb{1}\big[\,y_{\le t} \in \operatorname{prefix}(L(G))\,\big]$$

⟪eqno:constrained⟫

Phần mềm llama.cpp cài đặt cơ chế này bằng ngữ pháp dạng GBNF. Trong đề tài, ngữ pháp được sinh lại cho từng bản ghi từ chính danh sách sự kiện, nên mô hình chỉ có thể nhắc những lớp có trong danh sách, theo đúng thứ tự thời gian. Điều kiện ⟪eq:grounding⟫ vì vậy được bảo đảm ngay từ cấu tạo; đổi lại, câu văn bị bó hẹp và có thể bỏ sót khi danh sách dài.

**Cây tăng cường gradient và học chéo.** Mô hình tăng cường gradient là tổng $F_M(x) = \sum_{m=1}^{M} \nu\, h_m(x)$, trong đó mỗi cây quyết định $h_m$ được học để sửa sai số còn lại của $F_{m-1}$, và $\nu$ là hệ số học. LBR dùng bản cài đặt của thư viện scikit-learn: một mô hình hồi quy dự đoán độ dời biên, một mô hình phân loại chấm lại khả năng hộp sự kiện là đúng. Vì cả hai được học và chấm trên cùng tập dữ liệu, nhóm dùng **học chéo (cross-fit)**: chia bản ghi thành $K$ phần; mô hình áp cho phần $k$ chỉ học trên $K-1$ phần còn lại. Nhờ đó nhãn của một phần không đi vào mô hình nào được áp lên chính phần đó.

**Bootstrap ghép cặp theo bản ghi.** Để so hai hệ $A$, $B$ trên cùng $n$ bản ghi, mỗi lần lặp lấy mẫu có hoàn lại $n$ bản ghi, cộng dồn $TP$, $FP$, $FN$ của mỗi hệ trên mẫu đó và tính

$$\Delta^{*} = F_1^{micro}(B^{*}) - F_1^{micro}(A^{*})$$

⟪eqno:bootstrap⟫

Sau 1.000 lần lặp, khoảng tin cậy 95% (KTC 95%) là phân vị 2,5% và 97,5% của các $\Delta^{*}$. Đơn vị lấy mẫu là bản ghi vì các sự kiện trong cùng bản ghi phụ thuộc nhau. Ghép cặp (dùng cùng một mẫu cho cả hai hệ) loại bỏ phần dao động do độ khó riêng của từng bản ghi. Báo cáo chỉ nói một hiệu là "có ý nghĩa" khi KTC không chứa 0.

## Vị trí của đề tài

Các nguồn trên cung cấp nền cho từng phần của hệ thống: dữ liệu có nhãn mạnh [@fredianelli2025environmental], chỉ số SED [@mesaros2016metrics; @bilen2020psds], ghép biên sự kiện [@ebbers2024sound], tiền huấn luyện [@kong2020panns; @schmid2025effective], ảo giác [@ji2023hallucination] và RAG [@lewis2020rag]. Bài mô tả DataSED không báo cáo mô hình cơ sở nào [@fredianelli2025environmental], và trong phạm vi tra cứu nhóm không thấy công trình nào báo kết quả SED theo sự kiện trên DataSED.

Về rò rỉ dữ liệu, Weck và Serra dùng dấu vân âm thanh để tìm bản trùng giữa tập huấn luyện và tập đánh giá, và chỉ ra điểm truy hồi bị thổi phồng [@weck2023leakage]. Wijngaard và cộng sự đo mức chồng lấn giữa nhiều bộ dữ liệu âm thanh–ngôn ngữ [@wijngaard2025survey]. Kiểm tra trùng lặp vì vậy là kỹ thuật đã có.

Phần riêng của đề tài là **tích hợp các phần trên thành một hệ thống kiểm chứng được**: chuyển giao có kiểm soát trùng lặp, SED đa âm trên bản ghi môi trường, mô tả bám sát sự kiện kiểm tra được bằng máy, và truy hồi có điều kiện quan hệ giữa các sự kiện, với mọi câu trả lời truy được về bản ghi và khoảng thời gian. Phạm vi tra cứu ở mức khóa luận, không phải tổng quan hệ thống đầy đủ.
