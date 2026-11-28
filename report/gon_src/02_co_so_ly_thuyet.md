# CƠ SỞ LÝ THUYẾT

Chương này tóm tắt kiến thức nền mà đề tài dùng và định nghĩa mọi chỉ số được dùng để đọc kết quả ở Chương 6. Các nguồn trích trong chương đều được nhóm đọc toàn văn.

## Phát hiện sự kiện âm thanh

Phát hiện sự kiện âm thanh (SED) trả lời câu hỏi "cái gì xảy ra và khi nào". Đầu ra gồm lớp sự kiện cùng thời điểm bắt đầu và kết thúc [@mesaros2021tutorial]. Vì nhiều nguồn có thể vang cùng lúc, SED đa âm là bài toán phân loại **nhiều nhãn cho từng khung thời gian**, không phải gán một nhãn cho cả đoạn.

Có hai kiểu nhãn [@mesaros2021tutorial]. Nhãn mạnh ghi rõ khoảng thời gian của từng sự kiện. Nhãn yếu chỉ cho biết lớp nào có mặt trong bản ghi. Nhãn mạnh tốn công hơn vì người gán phải nghe lại và đặt biên cho từng sự kiện, mà biên của âm thanh môi trường vốn không rõ nét. DataSEC có nhãn theo đoạn, còn DataSED có nhãn mạnh [@fredianelli2025environmental].

Đầu vào thường dùng là phổ log-mel, một "ảnh" thời gian–tần số của tín hiệu. Kiến trúc phổ biến là mạng tích chập hồi quy (Convolutional Recurrent Neural Network – CRNN) [@mesaros2021tutorial]: phần mạng nơ-ron tích chập (Convolutional Neural Network – CNN) trích đặc trưng từ ảnh phổ, phần hồi quy học quan hệ theo thời gian. Trong đề tài, phần hồi quy là mạng hồi quy có cổng hai chiều (Bidirectional Gated Recurrent Unit – BiGRU). Mô hình cho ra xác suất của từng lớp tại từng khung. Chuỗi xác suất này chưa phải là sự kiện; nó phải qua bước ghép thành đoạn (mục 2.3). Vì vậy chất lượng phát hiện phụ thuộc cả mô hình lẫn bước ghép, và cả hai đều phải được chọn trên tập phát triển, không chọn trên tập kiểm tra.

## Các chỉ số đánh giá

Mục này định nghĩa mọi chỉ số mà Chương 6 dùng, theo đúng tham số trong mã đánh giá. Bảng nối từng câu hỏi nghiên cứu với chỉ số và bảng kết quả nằm ở cuối Chương 4 (⟪tbl:evalmap⟫). Quy ước chung: số sự kiện phát hiện đúng (True Positive – TP), báo nhầm (False Positive – FP) và bỏ sót (False Negative – FN) ký hiệu là $TP$, $FP$, $FN$; độ chính xác (*precision*) và độ đầy đủ (*recall*) là

$$P = \frac{TP}{TP+FP}, \qquad R = \frac{TP}{TP+FN}, \qquad F_1 = \frac{2PR}{P+R}$$

⟪eqno:f1⟫

### F1 theo đoạn

Mesaros và cộng sự phân biệt chỉ số theo đoạn với chỉ số theo sự kiện [@mesaros2016metrics]. F1 theo đoạn chia trục thời gian thành các đoạn 1 s; mỗi cặp (đoạn, lớp) là một quyết định có hoặc không, và $TP$, $FP$, $FN$ được đếm trên các cặp đó. Chỉ số này trả lời câu hỏi "trong từng giây, lớp nào có mặt" và không phạt việc lệch biên dưới 1 s. Đề tài tính bằng thư viện `sed_eval`.

### F1 theo sự kiện, micro và macro

F1 theo sự kiện so từng sự kiện dự đoán với sự kiện tham chiếu cùng lớp [@mesaros2016metrics]. Một cặp được coi là khớp khi thời điểm bắt đầu lệch không quá một dung sai (*collar*) $\tau = 0{,}2$ s; với thời điểm kết thúc, dung sai là

$$\Delta_{off} \le \max\left(\tau,\ \rho \cdot L_{ref}\right), \qquad \tau = 0{,}2\ \text{s},\ \rho = 0{,}2$$

⟪eqno:collar⟫

với $L_{ref}$ là độ dài sự kiện tham chiếu. Đây là chỉ số chính của phần SED. Khi gộp nhiều lớp có hai cách [@mesaros2016metrics]. *Micro* cộng dồn $TP$, $FP$, $FN$ của mọi lớp rồi mới tính F1, nên các lớp có nhiều sự kiện chi phối kết quả. *Macro* tính F1 riêng từng lớp rồi lấy trung bình, nên mỗi lớp có trọng số như nhau:

$$F_1^{micro} = F_1\Big(\sum_c TP_c,\ \sum_c FP_c,\ \sum_c FN_c\Big), \qquad F_1^{macro} = \frac{1}{|\mathcal{C}|}\sum_{c \in \mathcal{C}} F_{1,c}$$

⟪eqno:micromacro⟫

Lớp không có quyết định dương nào mang giá trị không xác định theo quy ước của `sed_eval` và bị bỏ khỏi trung bình macro. Báo cáo nêu cả hai. Việc chọn hệ thống dùng micro, vì luật chọn đã được ghi trước bằng micro và micro ít dao động hơn trên tập phát triển nhỏ.

### Chỉ số theo giao nhau và PSDS

F1 theo sự kiện đòi biên khớp trong 0,2 s. Với bài toán giám sát, câu hỏi "sự kiện có được phát hiện không" nhiều khi quan trọng hơn. Bilen và cộng sự đề xuất ba tiêu chí dựa trên tỷ lệ chồng lấp thời gian [@bilen2020psds]:

- **Tiêu chí phát hiện (Detection Tolerance Criterion – DTC):** một dự đoán là đúng khi ít nhất $\rho_{DTC}$ thời lượng của nó nằm trên sự kiện tham chiếu cùng lớp.
- **Tiêu chí phủ nhãn (Ground Truth intersection Criterion – GTC):** một sự kiện tham chiếu được coi là đã phát hiện khi các dự đoán cùng lớp phủ ít nhất $\rho_{GTC}$ thời lượng của nó.
- **Tiêu chí nhầm lớp (Cross-Trigger Tolerance Criterion – CTTC):** một dự đoán sai lớp bị tính là nhầm lớp khi nó chồng lên sự kiện tham chiếu của lớp khác ít nhất $\rho_{CTTC}$.

Tại một ngưỡng, đề tài dùng $\rho_{DTC} = \rho_{GTC} = 0{,}1$ và $\rho_{CTTC} = 0{,}3$ để tính hai chỉ số theo giao nhau:

$$\text{Độ phủ sự kiện} = \frac{\#\{\text{sự kiện tham chiếu đạt GTC}\}}{\#\{\text{sự kiện tham chiếu}\}}, \qquad \text{Độ chính xác theo giao nhau} = \frac{TP}{TP + FP}$$

⟪eqno:intersection⟫

trong đó $TP$ là số sự kiện tham chiếu đạt GTC và $FP$ là số dự đoán không đạt DTC. **Độ phủ sự kiện** là khái niệm trung tâm của luận điểm (Chương 1): tỷ lệ sự kiện thật mà SED đã phát hiện, không đòi biên khớp chặt.

Điểm phát hiện âm thanh đa âm (Polyphonic Sound Detection Score – PSDS) không gắn với một ngưỡng mà quét cả **dải** ngưỡng [@bilen2020psds]. Với mỗi ngưỡng, PSDS tính tỷ lệ sự kiện được phát hiện của từng lớp và tỷ lệ báo nhầm hiệu dụng $e$ (số báo nhầm mỗi giờ, cộng phần nhầm lớp có trọng số $\alpha_{CT}$). PSDS là diện tích dưới đường cong đó đến $e_{max}$, chuẩn hóa về $[0, 1]$:

$$\text{PSDS} = \frac{1}{e_{max}} \int_0^{e_{max}} \Big(\mu_{TPR}(e) - \alpha_{ST}\, \sigma_{TPR}(e)\Big)\, de$$

⟪eqno:psds⟫

với $\mu_{TPR}$ và $\sigma_{TPR}$ là trung bình và độ lệch chuẩn giữa các lớp. Đề tài dùng hai kịch bản chuẩn. **PSDS-1** nhấn mạnh định vị đúng thời điểm: $\rho_{DTC} = \rho_{GTC} = 0{,}7$, $\alpha_{CT} = 0$. **PSDS-2** nhấn mạnh tránh nhầm lớp: $\rho_{DTC} = \rho_{GTC} = 0{,}1$, $\rho_{CTTC} = 0{,}3$, $\alpha_{CT} = 0{,}5$. Cả hai dùng $\alpha_{ST} = 1$ và $e_{max} = 100$. Vì PSDS là tích phân trên dải ngưỡng, hai hệ chỉ so được khi tính trên **cùng một lưới ngưỡng**; một hệ có thể tốt ở kịch bản này mà kém ở kịch bản kia.

### Chỉ số phân loại

Mô hình phân loại trên DataSEC được đo bằng tỷ lệ phân loại đúng (*accuracy*) và macro-F1 trên 22 lớp cấp trên và 28 lớp con. **Tỷ lệ nhất quán** là tỷ lệ mẫu có lớp con dự đoán thuộc đúng lớp cấp trên dự đoán. Độ tin cậy của xác suất được đo bằng sai số hiệu chuẩn kỳ vọng (Expected Calibration Error – ECE): chia các dự đoán thành $B = 15$ khoảng theo độ tin cậy, rồi lấy trung bình có trọng số của độ lệch giữa tỷ lệ đúng và độ tin cậy trung bình trong từng khoảng,

$$\text{ECE} = \sum_{b=1}^{B} \frac{|B_b|}{N} \,\big|\operatorname{acc}(B_b) - \operatorname{conf}(B_b)\big|$$

⟪eqno:ece⟫

Hiệu chuẩn nhiệt độ chia logit cho một hằng số $T$ chọn trên tập phát triển; cách này không đổi thứ hạng dự đoán.

### Chỉ số bám sát của mô tả

Mô tả được chấm ở hai mức. Ở mức thứ nhất, "nguồn" là danh sách sự kiện **dự đoán** mà bộ sinh nhận được; ở mức thứ hai, là **nhãn gốc** của bản ghi. Mức thứ nhất đo lỗi của bộ sinh, mức thứ hai đo độ đúng với âm thanh.

Gọi $\mathcal{M}$ là danh sách các lần nhắc nguồn âm trong một mô tả, tìm bằng từ điển cụm từ (một lớp được nhắc ba lần thì tính ba lần), và $\mathcal{C}$ là tập lớp trong danh sách sự kiện. Tỷ lệ ảo giác $H$ và tỷ lệ bỏ sót $O$ của một mô tả là

$$H = 1 - \frac{|\{m \in \mathcal{M} : \text{lớp}(m) \in \mathcal{C}\}|}{|\mathcal{M}|}, \qquad O = 1 - \frac{|\{c \in \mathcal{C} : c \text{ được nhắc}\}|}{|\mathcal{C}|}$$

⟪eqno:halluc⟫

với quy ước $H = 0$ khi mô tả không nhắc nguồn âm nào và $O = 0$ khi danh sách sự kiện rỗng; số báo cáo là trung bình trên các bản ghi. Bỏ sót tính theo **lớp**, không theo sự kiện. Ba chỉ số phụ là cờ theo từng mô tả hoặc từng lần nhắc: **thêm bối cảnh** (mô tả có từ chỉ nguyên nhân hay bối cảnh), **từ cấm** (mô tả có từ thuộc danh sách cấm G3, Chương 4), và **gọi tên quá cụ thể** (tỷ lệ lần nhắc dùng tên cụ thể hơn lớp, ví dụ "xe cứu thương" khi lớp chỉ là `sirens_and_alarms`). **Độ phủ bằng chứng** là tỷ lệ lần nhắc có một sự kiện làm bằng chứng; **độ đúng thứ tự** là tỷ lệ cặp lần nhắc liền nhau đúng thứ tự thời gian.

Hai chỉ số trùng cụm từ của lĩnh vực mô tả ảnh và văn bản chỉ dùng để đo **độ giống câu mẫu**, không đo độ đúng: BLEU-4 (Bilingual Evaluation Understudy) đếm cụm 1 đến 4 từ trùng với câu tham chiếu, CIDEr (Consensus-based Image Description Evaluation) đếm cụm trùng có trọng số theo độ hiếm.

### Chỉ số truy hồi và câu trả lời

Gọi $R_q$ là tập bản ghi liên quan của câu truy vấn $q$, tính từ **nhãn gốc** theo đúng nghĩa của bộ lọc, và $r_i$ là bản ghi xếp thứ $i$. Lợi ích tích lũy chiết khấu chuẩn hóa (normalized Discounted Cumulative Gain – nDCG) ở 10 kết quả đầu là

$$\text{nDCG@}10 = \frac{\sum_{i=1}^{10}\mathbb{1}[r_i \in R_q]/\log_2(i+1)}{\sum_{i=1}^{\min(|R_q|,10)}1/\log_2(i+1)}$$

⟪eqno:ndcg⟫

Chỉ số này thưởng cho kết quả liên quan được xếp cao, và chỉ tính trên các câu truy vấn có ít nhất một bản ghi liên quan. **Độ đúng bộ lọc** là tỷ lệ kết quả trả về thỏa **mọi** điều kiện của câu truy vấn trên sự kiện đã lưu; với chế độ có lọc, giá trị 1,000 là phép kiểm tra cài đặt, không phải thước đo chất lượng. Với câu trả lời, đề tài đo **tỷ lệ khẳng định thiếu bằng chứng** (câu trả lời nhắc nguồn âm không có trong bằng chứng), **số câu có trả lời** (câu trả lời có ít nhất một bằng chứng) và **tỷ lệ trích đúng nhãn gốc** (tỷ lệ bản ghi được trích thật sự liên quan theo nhãn gốc).

### Chỉ số của bộ phân tích câu hỏi

Bộ phân tích câu hỏi biến câu tự nhiên thành bộ lọc. **Tỷ lệ hợp lược đồ** là tỷ lệ đầu ra đọc được theo lược đồ bộ lọc. **Tỷ lệ đúng hoàn toàn** là tỷ lệ câu có bộ lọc sinh ra, sau khi chuẩn hóa thứ tự, trùng khít bộ lọc chuẩn. Độ chính xác và độ đầy đủ theo lớp so tập lớp sinh ra với tập lớp chuẩn. **Độ đúng điều kiện thời gian** chỉ tính trên các câu có điều kiện thời gian.

### Khoảng tin cậy và kiểm định

Để so hai hệ $A$, $B$ trên cùng $n$ bản ghi, đề tài dùng **bootstrap ghép cặp theo bản ghi**: mỗi lần lặp lấy mẫu có hoàn lại $n$ bản ghi, cộng dồn $TP$, $FP$, $FN$ của mỗi hệ trên mẫu đó và tính

$$\Delta^{*} = F_1^{micro}(B^{*}) - F_1^{micro}(A^{*})$$

⟪eqno:bootstrap⟫

Sau 1.000 lần lặp, khoảng tin cậy 95% (KTC 95%) là phân vị 2,5% và 97,5% của các $\Delta^{*}$. Đơn vị lấy mẫu là bản ghi vì các sự kiện trong cùng bản ghi phụ thuộc nhau; với truy hồi, đơn vị là câu truy vấn. Ghép cặp (dùng cùng một mẫu cho cả hai hệ) loại bỏ phần dao động do độ khó riêng của từng bản ghi.

Khi so hai nhóm lần huấn luyện (ví dụ ba lần chạy của nhánh B với ba lần chạy của nhánh C), đề tài dùng thêm kiểm định t Welch trên điểm của từng lần chạy. Khi so thứ hạng của các ứng viên giữa hai tập, đề tài dùng hệ số tương quan hạng Spearman $\rho$. Các khoảng tin cậy không hiệu chỉnh cho việc so nhiều lần. Quy tắc đọc kết quả: báo cáo chỉ nói một hiệu là "có ý nghĩa" khi khoảng tin cậy không chứa 0; chênh lệch có khoảng tin cậy chứa 0, hoặc nhỏ hơn độ dao động giữa các lần huấn luyện, **không** được gọi là cải thiện.

### Độ trễ

Độ trễ của ứng dụng được đo bằng thời gian từ lúc tải tệp lên đến lúc có kết quả, và bằng **hệ số thời gian thực**, tức thời gian xử lý chia cho độ dài âm thanh; hệ số nhỏ hơn 1 nghĩa là xử lý nhanh hơn thời gian thật. Báo cáo nêu trung vị và phân vị 95%; với 10 lần đo, phân vị 95% gần như là giá trị lớn nhất.

## Từ xác suất đến sự kiện

Cách ghép phổ biến là làm mượt chuỗi xác suất bằng lọc trung vị, so với một ngưỡng $\theta_c$, nối các khoảng trống ngắn và bỏ sự kiện quá ngắn. Các giới hạn độ dài được suy từ thống kê nhãn của tập huấn luyện; suy từ chính tập đang chấm là một dạng rò rỉ khó thấy.

Ebbers và cộng sự chỉ ra rằng ngưỡng theo khung gắn chặt biên sự kiện với độ tin cậy: ngưỡng càng cao, thời điểm bắt đầu càng bị đẩy về nơi xác suất *đạt* ngưỡng, chứ không phải nơi xác suất bắt đầu tăng [@ebbers2024sound]. Họ đề xuất hộp bao sự kiện âm thanh (Sound Event Bounding Boxes – SEBB): ngưỡng chỉ quyết định giữ hay bỏ sự kiện, không dời biên. Biến thể cSEBB (change-detection-based SEBB) tìm biên tại điểm xác suất đổi hướng. Trên 13 hệ thống của thử thách phát hiện và phân loại cảnh, sự kiện âm thanh (Detection and Classification of Acoustic Scenes and Events – DCASE) năm 2023, cSEBB tăng trung bình 4,1 điểm PSDS-1 và 3,4 điểm F1 so với lọc trung vị [@ebbers2024sound]. Kết quả đó đo trên dữ liệu khác, nên nhóm xem cSEBB là một lựa chọn cần kiểm tra trên tập phát triển, không mặc định là tốt hơn.

Một hướng khác là sửa biên ngay trong lúc huấn luyện. Schmid và cộng sự thêm vào mô hình các bộ phận học riêng thời điểm bắt đầu và kết thúc; trên AudioSet-Strong, cách này nâng PSDS-1 của một mô hình CRNN từ 41,1 lên 48,0 [@schmid2026boundary]. Cách đó cần huấn luyện lại mô hình. LBR của khóa luận (Chương 4) làm việc khác: học sửa biên **sau** mô hình, trên xác suất đã có, nên không phải huấn luyện lại mô hình gốc.

## Học chuyển giao

**Tiền huấn luyện trên AudioSet.** Kong và cộng sự công bố họ mạng nơ-ron âm thanh tiền huấn luyện (Pretrained Audio Neural Networks – PANNs), huấn luyện trên AudioSet (hơn 5.000 giờ, 527 lớp) rồi chuyển sang sáu tác vụ âm thanh khác [@kong2020panns]. Mạng tích chập 14 lớp CNN14 của họ là điểm xuất phát của nhánh B và C trong Câu hỏi nghiên cứu 1. Với SED, các phép gộp (*pooling*) của mạng làm giảm độ phân giải theo thời gian; Chương 6 cho thấy điều này đặt một giới hạn trên đo được cho F1 theo sự kiện.

**Tiền huấn luyện theo khung.** Schmid và cộng sự tiền huấn luyện mô hình âm thanh trên nhãn **theo khung** của AudioSet Strong, cho đầu ra mỗi 40 ms. Trên bộ dữ liệu DESED (Domestic Environment Sound Event Detection Dataset), chỉ huấn luyện thêm một lớp tuyến tính trên bộ mã hóa đóng băng đã đạt PSDS-1 45,4 đến 49,2, gần với huấn luyện tiếp toàn bộ (47,6 đến 49,2) [@schmid2025effective]. Từ kết quả này, nhóm thử hai bộ mã hóa cùng loại có trọng số công bố trong kho mã của bài: BEATs (Bidirectional Encoder representation from Audio Transformers), một mô hình tự giám sát [@chen2022beats], và Frame-MobileNet, một mạng MobileNet cho đầu ra theo khung do Morocutti và cộng sự đề xuất [@morocutti2025tradeoffs]. Các con số trên đo trên DESED, nên chỉ là lý do để thử, không phải dự báo kết quả.

**Tăng cường dữ liệu.** Mixup huấn luyện trên tổ hợp tuyến tính của hai mẫu và nhãn của chúng [@zhang2018mixup]. FilterAugment nhân trọng số ngẫu nhiên lên các dải tần để mô phỏng môi trường âm học khác nhau; trên SED, nó tăng PSDS 6,50% so với 2,13% của cách che dải tần [@nam2022filteraugment].

**Trùng lặp giữa các bộ dữ liệu.** Chuyển giao chỉ có nghĩa khi dữ liệu kiểm tra không nằm trong dữ liệu tiền huấn luyện. Bài mô tả DataSEC và DataSED cho biết một phần âm thanh lấy từ Freesound và AudioSet [@fredianelli2025environmental]. Vì vậy hai bộ có thể chung bản ghi gốc (nhóm kiểm tra ở Chương 3), và mô hình tiền huấn luyện trên AudioSet có thể đã "nghe" một phần âm thanh gốc. Rủi ro thứ hai này không định lượng được vì danh sách nguồn không được công bố.

## Mô tả bám sát sự kiện và ảo giác

Ji và cộng sự định nghĩa ảo giác trong sinh văn bản là nội dung "vô nghĩa hoặc không trung thành với nguồn được cung cấp" [@ji2023hallucination]. Ở đề tài, "nguồn" là danh sách sự kiện, nên ảo giác được định nghĩa hẹp và kiểm tra được (mục 2.2.5): mô tả nhắc một nguồn âm không có trong danh sách là ảo giác; mô tả đặt sai thứ tự hai sự kiện cũng là lỗi.

Cách định nghĩa này cho phép đo ảo giác **mà không cần câu mô tả mẫu do người viết**. Trong lĩnh vực mô tả âm thanh tự động đã có chỉ số gần: Kuan và cộng sự đề xuất ECHO (Evaluation of Caption Hallucination in audiO), tính tỷ lệ đối tượng được nhắc mà không có trong nhãn thật [@kuan2024echo]; ECHO không xét thời gian hay thứ tự. Kumar và cộng sự đề xuất mô hình mô tả âm thanh kèm mốc thời gian TAC (Timestamped Audio Captioner) và đo ảo giác bằng một mô hình chấm độ khớp âm thanh–văn bản [@kumar2026tac]. Chỉ số của nhóm khác ở chỗ so mô tả với **dòng thời gian sự kiện đã phát hiện**, bằng các luật máy kiểm tra được (độ phủ bằng chứng, khẳng định thiếu bằng chứng, thứ tự, từ cấm, gọi tên quá cụ thể). Vì đã có công trình gần, báo cáo coi đây là áp dụng và mở rộng.

## Truy hồi và RAG

Lewis và cộng sự đề xuất RAG: kết hợp một mô hình sinh với một kho dữ liệu ngoài, truy cập qua bộ truy hồi [@lewis2020rag]. Nhóm áp dụng ý tưởng này với hai thay đổi. Kho ngoài là các sự kiện có cấu trúc (lớp, bắt đầu, kết thúc, độ tin cậy) thay vì văn bản tự do. Câu trả lời bắt buộc kèm bằng chứng (mã bản ghi, khoảng thời gian).

Để câu hỏi tiếng Việt và tiếng Anh dùng chung một kho, nhóm dùng mô hình nhúng đa ngữ BGE-M3 (BAAI General Embedding, Multi-Linguality, Multi-Functionality, Multi-Granularity), hỗ trợ hơn 100 ngôn ngữ [@chen2024m3]. Độ tương đồng vector hợp với câu hỏi mang tính ngữ nghĩa, nhưng không bảo đảm các điều kiện cứng như "sự kiện dài hơn 30 giây" hay "tiếng kính vỡ trước tiếng còi". Các điều kiện đó là phép so sánh số và phép nối theo thời gian, nên được xử lý bằng bộ lọc trong cơ sở dữ liệu. Truy hồi kết hợp lọc theo điều kiện trước, rồi xếp hạng theo vector trong tập đã lọc.

Hệ thống gần nhất với hướng này là LA-RAG (Long Audio Retrieval-Augmented Generation): chuyển âm thanh dài thành bản ghi sự kiện có mốc thời gian lưu trong cơ sở dữ liệu SQL, đổi biểu thức thời gian tuyệt đối (ví dụ "trước buổi trưa") thành cửa sổ thời gian, rồi truy xuất bằng độ tương đồng kèm bộ lọc trước khi để mô hình ngôn ngữ trả lời [@hegde2026larag]. Trong công trình đó, nhóm không thấy điều kiện quan hệ **giữa hai sự kiện** (trước, sau, chồng nhau, nằm trong); đề tài bổ sung bốn điều kiện loại này bằng SQL. Chất lượng truy hồi được đo bằng nDCG@10 (mục 2.2.6).

## Hai kỹ thuật dùng trong hệ thống

**Giải mã có ràng buộc bằng ngữ pháp.** Mô hình ngôn ngữ sinh từng token $y_t$ theo phân phối $p(y_t \mid y_{<t}, x)$. Giải mã có ràng buộc chỉ giữ những token mà sau khi thêm vào, chuỗi vẫn là phần đầu của một câu thuộc ngôn ngữ $L(G)$ của ngữ pháp $G$:

$$p_G(y_t \mid y_{<t}, x) \propto p(y_t \mid y_{<t}, x)\cdot \mathbb{1}\big[\,y_{\le t} \in \operatorname{prefix}(L(G))\,\big]$$

⟪eqno:constrained⟫

Phần mềm llama.cpp cài đặt cơ chế này bằng ngữ pháp dạng GBNF (GGML Backus–Naur Form). Trong đề tài, ngữ pháp được sinh lại cho từng bản ghi từ chính danh sách sự kiện, nên mô hình chỉ có thể nhắc những lớp có trong danh sách, theo đúng thứ tự thời gian. Điều kiện ⟪eq:grounding⟫ vì vậy được bảo đảm ngay từ cấu tạo; đổi lại, câu văn bị bó hẹp và có thể bỏ sót khi danh sách dài.

**Cây tăng cường gradient và học chéo.** Mô hình tăng cường gradient là tổng $F_M(x) = \sum_{m=1}^{M} \nu\, h_m(x)$, trong đó mỗi cây quyết định $h_m$ được học để sửa sai số còn lại của $F_{m-1}$, và $\nu$ là hệ số học. LBR dùng bản cài đặt của thư viện scikit-learn: một mô hình hồi quy dự đoán độ dời biên, một mô hình phân loại chấm lại khả năng hộp sự kiện là đúng. Vì cả hai được học và chấm trên cùng tập dữ liệu, nhóm dùng **học chéo (*cross-fit*)**: chia bản ghi thành $K$ phần; mô hình áp cho phần $k$ chỉ học trên $K-1$ phần còn lại. Nhờ đó nhãn của một phần không đi vào mô hình nào được áp lên chính phần đó.

## Vị trí của đề tài

Các nguồn trên cung cấp nền cho từng phần của hệ thống: dữ liệu có nhãn mạnh [@fredianelli2025environmental], chỉ số SED [@mesaros2016metrics; @bilen2020psds], ghép biên sự kiện [@ebbers2024sound], tiền huấn luyện [@kong2020panns; @schmid2025effective; @morocutti2025tradeoffs], ảo giác [@ji2023hallucination] và RAG [@lewis2020rag]. Bài mô tả DataSED không báo cáo mô hình cơ sở nào [@fredianelli2025environmental], và trong phạm vi tra cứu nhóm không thấy công trình nào báo kết quả SED theo sự kiện trên DataSED.

Về rò rỉ dữ liệu, Weck và Serra dùng dấu vân âm thanh để tìm bản trùng giữa tập huấn luyện và tập đánh giá, và chỉ ra điểm truy hồi bị thổi phồng [@weck2023leakage]. Wijngaard và cộng sự đo mức chồng lấn giữa nhiều bộ dữ liệu âm thanh–ngôn ngữ [@wijngaard2025survey]. Kiểm tra trùng lặp vì vậy là kỹ thuật đã có.

Phần riêng của đề tài là **tích hợp các phần trên thành một hệ thống kiểm chứng được**: chuyển giao có kiểm soát trùng lặp, SED đa âm trên bản ghi môi trường, mô tả bám sát sự kiện kiểm tra được bằng máy, và truy hồi có điều kiện quan hệ giữa các sự kiện, với mọi câu trả lời truy được về bản ghi và khoảng thời gian. Phạm vi tra cứu ở mức khóa luận, không phải tổng quan hệ thống đầy đủ.
