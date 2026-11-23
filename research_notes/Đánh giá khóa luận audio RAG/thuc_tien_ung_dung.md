# Tính thực tiễn của hệ thống SED + truy hồi sự kiện âm thanh môi trường: ứng dụng thật, yêu cầu triển khai, bối cảnh Việt Nam

> Ghi chú nghiên cứu ngày 23/11/2026 (hạn nộp 28/11/2026; giai đoạn P đóng băng 18/11 theo ADR-0043). Phạm vi tuân ADR-0001: chỉ mô tả **nguồn âm quan sát được**, không tuyên bố phát hiện tội phạm, ý định, khẩn cấp hay sự cố an ninh.
> **Nhãn độ tin cậy nguồn:** **[gốc]** = đã đọc trực tiếp văn bản hoặc paper gốc; **[abstract]** = chỉ đọc abstract; **[thứ cấp]** = trang tư vấn luật hoặc báo; **[snippet]** = chỉ thấy qua tóm tắt kết quả tìm kiếm, trang gốc bị chặn (403/paywall). Dữ kiện trong repo được dẫn bằng đường dẫn tương đối từ thư mục này (`../../` là gốc repo).

---

## 1. Quản lý tiếng ồn môi trường: nhận dạng nguồn âm giải quyết vấn đề gì cho trạm quan trắc và cơ quan quản lý? (END, DYNAMAP, SONYC, CENSE, Barcelona/Paris, bối cảnh Ý)

### Takeaway
Máy đo và trạm quan trắc truyền thống cho biết **mức ồn** nhưng không cho biết **nguồn**. Mọi dự án lớn đều phải thêm một lớp nhận dạng nguồn: DYNAMAP loại "sự kiện ồn bất thường" khỏi bản đồ ồn giao thông; SONYC phục vụ cơ quan thực thi; CENSE đo thời gian hiện diện của từng nguồn. Chuỗi SED → timeline → event store → truy vấn của khóa luận nằm đúng ở lớp này. Khác biệt quan trọng: các dự án đó luôn đi kèm phép đo mức âm đã hiệu chuẩn, còn khóa luận thì không có.

### Cited Findings
**Động lực chính sách ở châu Âu**
- Khoảng 112 triệu người (>20% dân số châu Âu) chịu ồn dài hạn từ đường bộ, đường sắt, hàng không vượt ngưỡng của END. Đường bộ phủ rộng nhất (~92 triệu người ≥ 55 dB Lden), đường sắt 18 triệu, hàng không 2,6 triệu. Số liệu lấy từ vòng báo cáo END 2022 — [EEA, *Environmental noise in Europe 2025*](https://www.eea.europa.eu/en/analysis/publications/environmental-noise-in-europe-2025) [snippet trang EEA].
- Cùng báo cáo: năm 2021, phơi nhiễm ồn giao thông liên quan khoảng 66.000 ca tử vong sớm, 50.000 ca bệnh tim mạch mới và 22.000 ca tiểu đường type 2. Ồn giao thông nằm trong top 3 mối đe dọa sức khỏe môi trường — [EEA 2025](https://www.eea.europa.eu/en/analysis/publications/environmental-noise-in-europe-2025) [snippet].
  - **Mâu thuẫn:** một snippet khác của trang xuất bản EEA ghi 73.000 ca/năm.
  - Trang của Ủy ban châu Âu vẫn ghi "12,000 premature deaths", tức số liệu cũ — [EC, Noise](https://environment.ec.europa.eu/topics/noise_en) [gốc].
  - Khi trích, nên dùng 66.000 kèm năm 2021.
- Theo EC, Directive 2002/49/EC là "The main EU law to identify and reduce noise pollution levels where necessary". Zero Pollution Action Plan đặt mục tiêu giảm 30% tỷ lệ người bị ồn giao thông làm phiền kinh niên vào năm 2030 — [EC Noise](https://environment.ec.europa.eu/topics/noise_en) [gốc].
- WHO 2018 khuyến nghị **theo loại nguồn** — [FHI (Viện Y tế công cộng Na Uy) tóm tắt WHO](https://www.fhi.no/ml/miljo/stoy/nye-retningslinjer-for-stoy-fra-verdens-helseorganisasjon/), [QMUL 2018](https://www.qmul.ac.uk/news/latest-news/2018/smd/reduce-traffic-noise-to-prevent-heart-disease.html) [thứ cấp]:
  - đường bộ < 53 dB Lden và < 45 dB Lnight;
  - hàng không < 45 dB Lden và < 40 dB Lnight;
  - tuabin gió 45 dB Lden.

**LIFE DYNAMAP (Milan và Rome): phát hiện "anomalous noise events" (ANE) để làm bản đồ ồn động**
- Benocci et al. 2020 — [Sensors 20(2):412, DOI 10.3390/s20020412](https://doi.org/10.3390/s20020412), đọc toàn văn qua [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7014368/fullTextXML) [gốc]:
  - Milan có 24 trạm cố định (Quận 9, ~2000 đoạn đường); Rome có 19 cảm biến dọc đường A90.
  - Cảm biến loại "customized low-cost", "ARM-based".
  - So với máy đo Class 1 tại 12 điểm: R² = 0,99, sai lệch trung bình 1,0 ± 0,9 dB.
  - Bản đồ động đạt sai số < 3 dB (ngưỡng của Good Practice Guide) cho phần lớn nhóm đường.
  - ANE "may alter the noise levels represented by DYNAMAP", nên phải loại để dữ liệu chỉ còn nguồn giao thông.
- ANED hai lớp (road traffic noise vs ANE), dùng MFCC + GMM. So với baseline one-class GMM, F1 cải thiện tương đối 18,7% (ngoại ô) và 31,8% (đô thị) ở cửa sổ 1 s. Tác giả tự nhận "still has room for improvement" — [Socoró, Alías, Alsina-Pagès, Sensors 17(10):2323, 2017](https://doi.org/10.3390/s17102323) [abstract].
- Bộ dữ liệu ngoại ô Rome: 156 h 20 phút audio gán nhãn từ WASN 19 node; ANE chia 16 tiểu loại; còi hú, tàu hỏa và sấm chiếm ưu thế — [Alsina-Pagès et al., Sensors 19(11):2480, 2019](https://doi.org/10.3390/s19112480) [abstract]. Snippet trang PMC ghi tỷ lệ ≈ 98,3% road traffic noise, 0,7% ANE, 1,0% "dummy" — [PMC6603744](https://pmc.ncbi.nlm.nih.gov/articles/PMC6603744) [snippet, chưa đối chiếu toàn văn].
- Tổng 304 h 20 phút dữ liệu gán nhãn từ hai WASN. ANE đặc biệt phổ biến ở đô thị; nhiều ANE tác động thấp hoặc trung bình gộp lại có thể nghiêm trọng như một ANE tác động cao — [Alías et al., Sensors 20(3):609, 2020](https://doi.org/10.3390/s20030609) [abstract].

**SONYC (New York)**
- Mục tiêu: cảm biến "low-cost, low-power… produce calibrated acoustic measurements and recognize individual sound sources in real time"; dữ liệu dùng để "drive the strategic application of noise code enforcement by city agencies" — [Bello et al., arXiv:1805.00889, CACM 2019](https://arxiv.org/abs/1805.00889) [abstract].
- Vận hành thực tế — [Mydlarz et al., "The Life of a New York City Noise Sensor Network", Sensors 19(6):1415, 2019](https://ar5iv.labs.arxiv.org/html/1903.03195) [gốc]:
  - phần cứng: Raspberry Pi 2B, micro MEMS dải 32–120 dBA, hiệu chuẩn "compliant with IEC 61672-1 Type-2", khoảng 80 USD tiền linh kiện mỗi node;
  - quy mô: 55 node, node đầu tiên lắp từ 05/2016;
  - độ ổn định: data yield trung bình 73,2% (dao động 23,0–94,8%), Wi-Fi yếu là nguyên nhân downtime chính;
  - **không phân loại trên thiết bị** vì "presents a challenge" về tính toán.

**CENSE (Lorient, Pháp; ANR 2017–2021)**
- Mạng cảm biến chi phí thấp mật độ cao, đồng hóa dữ liệu giữa mô phỏng và đo — [CENSE general overview (HAL)](https://hal.archives-ouvertes.fr/hal-03432916), [ANR-16-CE22-0012](https://anr.fr/Project-ANR-16-CE22-0012) [snippet]:
  - nhận dạng tự động traffic, voices, birds bằng deep learning để ước lượng **thời gian hiện diện** của từng nguồn; tỷ lệ hiện diện bám nhịp sinh hoạt hằng ngày của thành phố;
  - 78 gateway node (pha 1) + 65 node (pha 2);
  - khảo sát khoảng 2.000 hộ, đối chiếu với 123 cảm biến.

**Barcelona và Paris**
- Barcelona — [Euronoise 2015](https://www.conforg.fr/euronoise2015/proceedings/data/articles/000195.pdf), [Ajuntament de Barcelona – Sentilo](https://ajuntament.barcelona.cat/digital/en/digital-transformation/urban-technology/sentilo) [snippet]:
  - cảm biến ồn chạy trên nền tảng mã nguồn mở Sentilo;
  - năm 2015 có 11 cảm biến âm, cộng mạng chính 25 máy Class I;
  - một tin không ghi ngày nhắc tới 133 đơn vị.
- Paris, radar âm thanh Bruitparif "Méduse" — [Paris.fr](https://www.paris.fr/pages/paris-experimente-ses-premiers-radars-sonores-20411), [Bruitparif 05/2025](https://www.bruitparif.fr/pages/En-tete/400%20Nos%20publications/700%20Rapports%20d'%C3%A9tude/2025-05-14%20-%20Bilan%20sur%20un%20an%20d'exploitation%20d'un%20radar%20sonore%20p%C3%A9dagogique%20Bd%20Malesherbes%20Paris17.pdf) [snippet]:
  - thử nghiệm ở rue d'Avron từ 01 đến 10/2022, không phạt;
  - biển cảnh báo khi xe vượt 85 dB ban ngày hoặc 80 dB ban đêm;
  - cuối 2025 LNE mới bắt đầu thử nghiệm homologation (hai ứng viên MicrodB và Bruitparif) — đây là điều kiện bắt buộc trước khi dùng số đo để phạt;
  - chưa thấy xác nhận năm 2026 về việc đã bắt đầu phạt.

**Bối cảnh tác giả dataset (Ý)**
- DataSEC + DataSED: >35 giờ audio thật, không tổng hợp, "collected from sound level meter measurements and online repositories". DataSED có 712 recording thực tế với >4000 nhãn — [IRIS Unicampania, 2025](https://iris.unicampania.it/handle/11591/579845) [gốc, metadata].
- DataSED polyphonic có 21 lớp, bỏ Wind turbine — [Zenodo 15346092](https://zenodo.org/records/15346092).
- Bài mô tả dataset: Fredianelli, Artuso, Pompei, Licitra, Iannace, Akbaba (2025), *Scientific Data*, đã xác minh mức V3 — [`docs/RELATED_WORK.md`](../../docs/RELATED_WORK.md).
- Nhóm Fredianelli/Licitra nghiên cứu ồn cảng Livorno [snippet]:
  - đo liên tục hơn 3 tháng ở kênh công nghiệp — [Sustainability 12(5):1740, 2020](https://mdpi.com/2071-1050/12/5/1740);
  - các dự án Interreg Marittimo REPORT, MON ACUMEN, DECIBEL, RUMBLE cho ra hướng dẫn đặc trưng nguồn để lập bản đồ ồn cảng và đặc tả mạng quan trắc tích hợp; phân loại nguồn hỗ trợ chọn vị trí trạm — [Environments 8:12, 2021](https://arpi.unipi.it/retrieve/e0d6c931-c05c-fcf8-e053-d805fe0aa794/environments-08-00012.pdf).

**Tiền lệ phân loại nguồn**
- Thiết bị ghi mức ồn không người trực "can only determine overall noise levels without regard to source" — [Wright & Flindell, IOA](https://www.ioa.org.uk/system/files/publications/P%20WRIGHT%20IH%20FLINDELL%20AUTOMATIC%20NOISE%20SOURCE%20IDENTIFICATION.pdf) [snippet, ~1991–92].
- Phân loại chạy ngay trong cảm biến không dây; pilot ở bãi nghiền đá chạy 50 ngày, nhận đúng >90% nguồn — [Luận văn TUT, 2017](https://urn.fi/URN:NBN:fi:tty-201710041981) [snippet, trang gốc trả 403].

### Inferences
- Các dự án thật đều tách hai tầng: (1) mức âm đã hiệu chuẩn và (2) nhận dạng nguồn. Khóa luận chỉ làm tầng (2), cộng thêm phần truy hồi và bằng chứng. Vì vậy nên định vị là **"lớp nhận dạng và truy hồi nguồn bổ trợ cho trạm đo"**, không phải trạm đo.
- DYNAMAP là ví dụ chuẩn của "SED phục vụ quản lý". Các ANE phổ biến (còi hú, tàu, sấm, còi xe, tiếng người) đều có lớp tương ứng trong 22 lớp của khóa luận, mịn hơn bài toán hai lớp RTN/ANE.
- CENSE đo "thời gian hiện diện nguồn" — chính là thống kê thời lượng lấy được từ onset/offset trong event timeline.
- SONYC năm 2019 chưa phân loại được trên Raspberry Pi 2B; năm 2025 CNN nhẹ đã chạy được trên Pi 4B (xem §5). Kiến trúc "SED tại biên, chỉ gửi metadata" vì thế khả thi hơn trước.
- Bài học Paris: ngay cả thiết bị chuyên dụng cũng phải homologation mới được dùng để phạt. Khóa luận không nên tuyên bố giá trị chứng cứ pháp lý.
- Dataset do chuyên gia đo ồn thu một phần bằng máy đo mức âm, nên lập luận "dữ liệu từ thực hành quan trắc" có cơ sở. Tuy nhiên một phần lấy từ kho online, không phải 100% ghi âm hiện trường.

### Gaps
- Chưa đọc được EUR-Lex (trang tóm tắt trả về rỗng). Chi tiết END (chu kỳ 5 năm, ngưỡng cho agglomeration, đường, đường sắt, sân bay; chỉ số Lden/Lnight ở Annex I) cần trích từ [EUR-Lex 32002L0049](https://eur-lex.europa.eu/eli/dir/2002/49/oj) trước khi đưa vào báo cáo.
- Không có F1 tuyệt đối của ANED trên dữ liệu thật; PMC/MDPI chặn truy cập.
- Chưa xác minh khuyến nghị WHO cho đường sắt và leisure noise; chưa có chi phí trên mỗi cảm biến của DYNAMAP, CENSE, Barcelona.

---

## 2. Thiết bị quan trắc thương mại có nhận dạng/phân loại nguồn: tính năng gì, so với khóa luận thế nào?

### Takeaway
Ngành đã đi từ "ghi âm khi vượt ngưỡng, người nghe gắn nhãn" (Cirrus, B&K, thập niên 2010) sang "AI phân loại nguồn trên clip được kích hoạt" (Svantek SvanNET AI 26 lớp năm 2024, SiteHive, Wood noiseAI, Norsonic/SINTEF 2026). Taxonomy 22 lớp của khóa luận **cùng độ chi tiết** với SvanNET AI.

Khóa luận khác các sản phẩm này ở bốn điểm:
- làm SED đa âm có onset/offset trên recording liên tục;
- có truy vấn ngôn ngữ tự nhiên EN/VI kèm bằng chứng;
- có caption bị ràng buộc vào bằng chứng;
- có benchmark công khai — điều không vendor nào công bố.

Đổi lại, khóa luận không đo mức âm, không cảnh báo thời gian thực và không gắn với phần cứng đã hiệu chuẩn.

### Cited Findings
- **Svantek SvanNET AI** (datasheet 07/2024) — [AcSoft UK, SvanNET AI datasheet](https://acsoft.co.uk/wp-content/uploads/2024/07/SvanNET-AI-UK-Datasheet.pdf) [gốc, text trích bằng pdftotext]:
  - là module cho SvanNET Automatic Monitoring Services (dịch vụ online), xử lý "event-triggered audio recordings (WAV files)";
  - 26 lớp: Airplane, Animals, Applause, Birds, Blast, Boat, Cat, Construction, Dog, Drone, Emergency vehicle, Helicopter, Industrial noise, Motorcycle, Music, Other, Rain, Speech, Storm, Train horn, Train, Vehicle alarm, Vehicle horn, Vehicle, Wind (bản trích liệt kê "Airplane" hai lần);
  - báo cáo tự động kèm confidence; quảng cáo "Eliminates the need for manual review of audio recordings, significantly reducing the time required for environmental noise assessments";
  - tương thích SV 307A, SV 200A, SV 258PRO, SV 27x; ứng dụng: smart city, construction monitoring, compliance & reporting.
- Trang sản phẩm Svantek năm 2026 — [Svantek SvanNET AI](https://svantek.com/products/svannet-ai/) [gốc]:
  - số lớp không nhất quán (26/27/28);
  - yêu cầu WAV ≥ 16 kHz;
  - đếm xe, tàu, máy bay theo ngày/tuần;
  - "New Model… Available from November 2026";
  - **không công bố số accuracy**.
- **Cirrus Research** [gốc/snippet]:
  - Optimus có module "sound source recognition" (trình bày ở Internoise 2010) để "trigger recordings when a specific noise has been recognised". Ví dụ người ngoài vũ trường và chim hót "cannot be distinguished using the LAeq,1s graph" — [Cirrus](https://cirrusresearch.com/innovation-in-sound-source-recognition).
  - Invictus: noise event detection, ghi âm trong lúc đo, cảnh báo SMS/email, đầu vào thời tiết và video — [Cirrus Invictus](https://www.cirrusresearch.co.uk/products/environmental-noise-monitors/invictus-noise-monitors) [snippet].
  - Acoustic Fingerprint: kích hoạt ghi âm khi LAeq vượt ngưỡng trong một khoảng thời gian, hoặc khi có tone trong dải — [Cirrus](https://cirrusresearch.co.uk/products/sound-level-meters/optimus-sound-level-meters/acoustic-fingerprint) [snippet].
- **B&K Type 3639 NMT**: ghi broadband và 1/3-octave, GPS, sound recording, thời tiết — [National Academies, 2010, App. E](https://www.nationalacademies.org/read/12928/chapter/19) [snippet].
- **SiteHive Audio Classifier** (cho công trường): gán nguồn kèm % confidence cho từng clip, ước lượng phần đóng góp của công trường vào tổng ồn — [SiteHive](https://help.sitehive.co/articles/124490-audio-classifier) [snippet].
- Các sản phẩm và case study khác [snippet]:
  - Wood noiseAI: AI phân loại tập dữ liệu âm lớn, đã dùng cho dự án xây dựng — [Wood](https://www.woodplc.com/solutions/expertise/noise-ai);
  - UK CCS: thiết bị đo ồn + bụi tích hợp AI, gắn nguồn cho sự kiện vượt ngưỡng — [CCS](https://ccsbestpractice.org.uk/?p=92671);
  - INCE 2025: case study AI/ML ở công trường hạ tầng tại Rhode Island — [INCE](https://ince.publisher.ingentaconnect.com/contentone/ince/incecp/2025/00000271/00000001/art00016);
  - SINTEF/Norsonic 2026: máy đo AI tách máy xúc khỏi mòng biển và giao thông — [SINTEF 2026](https://www.sintef.no/en/latest-news/2026/a-microphone-that-can-sort-sounds-and-measure-noise-could-be-coming-to-a-construction-site-near-you/), [ScienceNorway](https://partner.sciencenorway.no/artificial-intelligence-sintef-sound/why-is-it-difficult-for-ai-to-distinguish-between-the-sound-of-excavators-and-seagulls/2636082).
- **Singapore NEA** — [NEA](https://www.nea.gov.sg/our-services/pollution-control/noise-pollution/construction-noise-control/noise-measurements---noise-management-plan), [MSE written reply](https://www.mse.gov.sg/latest-news/written-reply-to-parliamentary-question-on-noise-monitoring-protocols-of-construction-sites/) [snippet]:
  - công trường cách khu nhạy cảm (nhà ở, bệnh viện, trường học) ≤ 150 m phải lắp hệ quan trắc ồn; NEA chỉ định số máy và vị trí;
  - dự án > 3 triệu SGD hoặc có phá dỡ/đóng cọc phải quan trắc thời gian thực, NEA và nhà thầu cùng xem được;
  - thực thi dùng máy Class 1; NEA khuyến nghị dùng cảnh báo dự báo;
  - ngưỡng 70 và 75 dBA không thống nhất giữa các nguồn.

### Inferences
So sánh chức năng (dựa trên các nguồn trên và repo):

| Chức năng | SvanNET AI | Cirrus/B&K (truyền thống) | Khóa luận |
|---|---|---|---|
| Đo mức âm Class 1 | có (thiết bị đi kèm) | có | **không** |
| Kích hoạt ghi âm theo ngưỡng | có | có | không; xử lý toàn bộ recording |
| Phân loại nguồn | clip-level, 26 lớp + confidence | người nghe / luật đơn giản | **SED đa âm 21 lớp có onset/offset**; phân loại 22 lớp + 28 subclass |
| Nguồn chồng lấp | không rõ | — | có |
| Tìm kiếm qua nhiều recording bằng câu hỏi tự nhiên | không thấy | không | có (EN/VI, hybrid RAG, có evidence) |
| Caption bị ràng buộc vào bằng chứng | không | không | có (G1–G3) |
| Cảnh báo thời gian thực | có | có (SMS/email) | không; chỉ batch offline ([`docs/SYSTEM.md`](../../docs/SYSTEM.md) §1.6) |
| Accuracy công khai, tái lập được | không | không | có (benchmark DataSED) |

- Đối chiếu lớp: khoảng 15 hạng mục của SvanNET trùng với lớp của khóa luận (máy bay/trực thăng, chim, mèo, chó, construction/industrial ↔ `workshop`, emergency vehicle/vehicle alarm ↔ `sirens_and_alarms`, vehicle horn ↔ `horn`, vehicle/motorcycle ↔ `vehicle_*`, train, music, speech ↔ `voices`, storm/blast ↔ `thunder_fireworks_gunshot`). Chỉ khóa luận có: `bells`, `chicken_coop`, `cicadas…`, `glass_breaking`, `lawn_mower…`, `vacuum_cleaner…`, `wind_turbine`. Chỉ SvanNET có: rain, wind, boat, drone, applause. Câu nói được: **"taxonomy của khóa luận nói cùng 'ngôn ngữ nguồn' với sản phẩm thương mại 2024–2026."**
- Tuyên bố "eliminates manual review" là quảng cáo, chưa được kiểm chứng. Lỗi đo được của khóa luận (horn↔sirens; xem [`docs/taxonomy.md`](../../docs/taxonomy.md) §8.1) cho thấy vẫn cần người xác minh. Thiết kế evidence (recording + time span) giúp người kiểm nhanh, không thay người.

### Gaps
- Chưa xác minh tính năng nhận dạng nguồn của 01dB/ACOEM, Sonitus, HBK (2024–2026). Audio Analytic chưa tra (thuộc mảng thiết bị gia dụng).
- Không tìm thấy giá thiết bị thương mại, cũng như đánh giá accuracy độc lập nào cho các classifier thương mại.

---

## 3. Bối cảnh Việt Nam: QCVN 26:2025/BNNMT, Luật BVMT 2020, NĐ 45/2022, NĐ 282/2025, khiếu nại tiếng ồn — công cụ hỗ trợ ai, làm gì?

### Takeaway
**Đã xác minh từ văn bản gốc: QCVN 26:2010/BTNMT đã bị thay bằng QCVN 26:2025/BNNMT** (ban hành theo Thông tư 01/2025/TT-BNNMT ngày 15/5/2025, hiệu lực 14/11/2025). Cơ sở đang hoạt động được áp bản 2010 đến hết 31/12/2026 (nguồn thứ cấp).

Quy chuẩn mới đặt ngưỡng theo ba biến:
- **loại nguồn**: cơ sở có thiết bị, loa, công trường, đường bộ, đường sắt;
- **ba khung giờ**: 06–18h, 18–22h, 22–06h;
- **thời lượng phát ra tiếng ồn**: nới ngưỡng ở Bảng 2 và Bảng 4.

"Nguồn nào – lúc nào – bao lâu" chính là thứ timeline SED trả lời. Nhưng đánh giá tuân thủ **bắt buộc** dùng máy đo mức âm loại 1 (TCVN 12527-1:2018), theo TCVN 7878-1/-2:2018, do tổ chức đủ năng lực quan trắc thực hiện. Vì vậy SED chỉ là công cụ **sàng lọc và khoanh vùng**, không phải bằng chứng vi phạm.

Thực tế ở TP.HCM:
- khoảng 21.000 phản ánh tiếng ồn qua đường dây 1022 từ đầu 2024 đến 07/2025;
- phường thiếu máy đo;
- người vi phạm hạ âm lượng khi cán bộ đến.

NĐ 282/2025 chấp nhận bằng chứng ghi âm/ghi hình nếu thể hiện rõ thời gian, địa điểm và mức độ ảnh hưởng.

### Cited Findings
**QCVN 26:2025/BNNMT (đọc toàn văn)** — [PDF tại CDN thuvienphapluat](https://cdn.thuvienphapluat.vn/uploads/tintuc/2025/05/22/QCVN%2026_2025_BNNMT.pdf); bản trên cổng Bộ: [mae.gov.vn](https://www.mae.gov.vn/noidung/Lists/VBQPPL/Attachments/567/QCVN%2026_2025_BNNMT.pdf) [gốc]

*Thông tin chung*
- Lời nói đầu ghi: "QCVN 26:2025/BNNMT thay thế QCVN 26:2010/BTNMT", ban hành theo Thông tư 01/2025/TT-BNNMT ngày 15/5/2025.
- Phạm vi: tiếng ồn từ cơ sở sản xuất, kinh doanh, dịch vụ, công trình xây dựng đang thi công, phương tiện giao thông và hoạt động dân sinh. Không áp dụng cho tiếng ồn lao động.
- §1.3.5 phân loại tiếng ồn: liên tục (ổn định/dao động), xung (< 1 s), ngắt quãng (mỗi lần ≥ 1 s).
- §2.1 khu vực bị ảnh hưởng:
  - **A**: giáo dục, y tế, chăm sóc người cao tuổi, bảo tàng, thư viện, tôn giáo, trụ sở, văn phòng;
  - **B**: nhà ở, khách sạn và cơ sở lưu trú;
  - **C**: chăn nuôi, trồng trọt, thủy sản;
  - **D**: thể thao, công viên, văn hóa, giải trí, thương mại, nhà hàng;
  - **E**: nhà ga, bến xe, bãi đỗ, khu sản xuất tập trung, công nghiệp.

*Giới hạn (dBA; Ngày 06h–trước 18h / Tối 18h–trước 22h / Đêm 22h–trước 06h)*
- **Bảng 1** (cơ sở có thiết bị theo Phụ lục), đọc theo thứ tự hàng trong PDF: A 50/45/40; B 55/50/45; C 60/55/50; D 65/60/55; E 70/65/60.
- **Bảng 2** — nới ngưỡng theo thời lượng phát ra tiếng ồn:

  | Thời lượng phát (một trong các trường hợp) | Nới ngưỡng |
  |---|---|
  | ≤ 1 h ngày · ≤ 0,5 h tối · ≤ 0,25 h đêm | +15 dBA |
  | 1–2 h ngày · 0,5–1 h tối · 0,25–0,5 h đêm | +10 dBA |
  | 2–4 h ngày · 1–2 h tối · 0,5–1 h đêm | +5 dBA |
  | 4–6 h ngày · 2–3 h tối · 1–1,5 h đêm | +3 dBA |
  | dài hơn | giữ ngưỡng Bảng 1 |

- **Bảng 3** (nguồn khác):
  - **công trường đang thi công**: khu A–C 65/60/50; khu D–E 70/65/50;
  - **loa, ồn từ trong nhà phát ra ngoài**: A–C 55/50/45; D–E 65/60/55;
  - **cơ sở "trong cùng tòa nhà"** (gym/fitness, võ đường, vũ trường, dạy nhạc, bar, nhà hàng, siêu thị, **karaoke**): A–C 50/45/40.
- **Bảng 4** (công trường ban ngày):
  - phát ≤ 3 h: +10 dBA; 3–6 h: +5 dBA;
  - thêm +3 dBA ban ngày khi dùng máy đóng/nhổ cọc, máy đục lỗ, máy xúc;
  - trừ 5 dBA vào ngày nghỉ ở khu A và B.
- **Ghi chú (\*)**: ngưỡng cho loa không áp dụng với loa, còi xe chuyên dụng của cơ quan, đơn vị dùng theo quy định pháp luật, và loa của chương trình biểu diễn được cấp phép.
- **Bảng 5** (giao thông; ngày 06–22h / đêm 22–06h): đường bộ A–C 68/58, D–E 73/63; đường sắt A–C 70/60, D–E 75/65. Không có bảng riêng cho tiếng ồn hàng không.

*Phương pháp đo và quản lý*
- §2.5 mức ồn nền: đo ≥ 5 phút **khi nguồn cần đo không phát** (lấy Leq). Nếu không tách được nguồn thì lấy L90. Hiệu chỉnh −3/−2/−1 dBA khi chênh lệch 3 / 4–5 / 6–9 dBA.
- §3.1: vị trí đo "phải tránh tối đa các nguồn ồn khác không liên quan"; nếu không tránh được thì "phải lựa chọn thời gian đo hợp lý để loại bỏ tối đa tác động từ các nguồn ồn khác".
- §3.2: "phải sử dụng thiết bị đo mức âm loại 1 theo quy định tại TCVN 12527-1:2018", thiết bị đã kiểm định và hiệu chuẩn.
- §3.3: không đo khi mưa, gió < 5,5 m/s.
- §3.4: đo ≥ 15 phút; với ồn xung, đo ≥ 15 phút và có ≥ 50 giá trị.
- §3.5: theo TCVN 7878-1:2018 (ISO 1996-1:2016) và TCVN 7878-2:2018 (ISO 1996-2:2017).
- §4.1: quan trắc phục vụ quản lý nhà nước phải do tổ chức đủ điều kiện năng lực quan trắc thực hiện. §4.2: nếu ồn nền đã vượt ngưỡng thì không đánh giá nguồn. §4.4: kết quả đánh giá là cơ sở để cơ quan quản lý xử lý.
- Phụ lục: danh mục thiết bị gây ồn, ví dụ máy nén khí ≥ 7,5 kW, cưa máy ≥ 15 kW, quạt thông gió ≥ 7,5 kW, từ 2 máy mài ≥ 3,75 kW, máy phát điện ≥ 120 kW.

*Hiệu lực, chuyển tiếp và các mâu thuẫn cần biết*
- Hiệu lực 14/11/2025. Cơ sở đang hoạt động hoặc dự án đã duyệt được áp QCVN 26:2010 đến 31/12/2026; từ 01/01/2027 phải đáp ứng bản 2025 — [LuatVietnam 2025](https://luatvietnam.vn/tin-van-ban-moi/3-quy-chuan-ky-thuat-quoc-gia-ve-chat-luong-moi-truong-xung-quanh-ap-dung-tu-14-11-2025-186-102239-article.html) [thứ cấp; điều khoản này nằm trong thông tư, chưa đọc gốc].
- Bản 2010 cũ chỉ có hai khung giờ (6–21h, 21–6h); khu thông thường 70/55 dBA — [VnExpress International, 10/7/2025](https://e.vnexpress.net/news/news/karaoke-cacophony-in-hcmc-sees-neighbors-quarreling-authorities-deluged-with-complaints-4911577.html).
- **Lưu ý mâu thuẫn:** bản tóm tắt QCVN 26:2025 trên [hethongphapluat](https://hethongphapluat.com/national-technical-regulation-qcvn-26-2025-bnnmt-for-noise.html) ghi "ngày 6–21h / đêm 21–6h", trái với văn bản gốc. Không dùng nguồn này.

**Luật Bảo vệ môi trường 2020 (72/2020/QH14), Điều 89** — [Luật Hoàng Anh](https://luathoanganh.vn/moi-truong/quan-ly-va-kiem-soat-tieng-on-do-rung-anh-sang-buc-xa-mui-kho-chiu-la-gi-lha10300.html) [thứ cấp]; văn bản gốc tại [vbpl.moj.gov.vn](https://vbpl.moj.gov.vn/TW/Lists/vbpq/Attachments/146609/17112020.luat%2072.doc) (chưa mở). Hiệu lực 01/01/2022.
- Tổ chức, cá nhân gây tiếng ồn, độ rung phải kiểm soát, xử lý để bảo đảm quy chuẩn.
- Trong khu dân cư phải giảm thiểu, không tác động xấu đến cộng đồng.
- Đơn vị quản lý tuyến đường mật độ phương tiện cao phải có biện pháp giảm thiểu.

**NĐ 45/2022/NĐ-CP, Điều 22** (xử phạt dựa trên số dBA vượt quy chuẩn) [thứ cấp, chưa đối chiếu gốc]
- Vượt < 2 dBA: cảnh cáo — [HoaTieu](https://hoatieu.vn/phap-luat/muc-phat-vi-pham-quy-dinh-bao-dam-su-yen-tinh-chung-213258).
- Vượt 2 đến < 5 dBA: phạt 1–5 triệu đồng — [LuatMinhKhue](https://luatminhkhue.vn/tong-hop-muc-phat-vi-pham-tieng-on-theo-nghi-dinh-45-2022-nd-cp.aspx).
- Tổ chức bị phạt gấp đôi cá nhân (Điều 6). Thẩm quyền: Chủ tịch UBND các cấp và thanh tra chuyên ngành (Điều 68) — [ACC](https://accgroup.vn/nguyen-tac-xu-phat-vi-pham-hanh-chinh-am-thanh).
- Khung tổng 1–160 triệu đồng; cơ sở kinh doanh có thể bị đình chỉ 3–12 tháng — [Báo Pháp luật](https://baophapluat.vn/quan-ca-phe-mo-nhac-gay-tieng-on-bi-xu-ly-ra-sao-post466936.html).

**NĐ 282/2025/NĐ-CP** (trật tự công cộng; thay NĐ 144/2021; hiệu lực 15/12/2025) — [Tuổi Trẻ News, 23/12/2025](https://news.tuoitre.vn/how-decree-282-applies-and-what-evidence-needed-to-curb-karaoke-noise-in-vietnam-103251223143952307.htm) [báo]:
- karaoke và loa có thể bị phạt **ở bất kỳ giờ nào**;
- theo luật sư, Điều 9 quy định cảnh cáo hoặc phạt 500.000–1.000.000 đồng;
- **bằng chứng được chấp nhận**: ghi âm/ghi hình, biên bản xác minh, lời khai của hộ lân cận — kể cả khi nhạc đã tắt lúc cán bộ đến; nhưng "Such evidence must clearly show the time, location, and degree of impact";
- không được dựa vào cảm nhận chủ quan;
- phường ở Cà Mau "has no specialized sound-measuring equipment"; cán bộ Mỹ Tho cho rằng phải chứng minh vượt chuẩn và "measurement and assessment are not easy".

Nguồn khác về NĐ 282/2025 và chỗ mâu thuẫn:
- Tụ tập hát karaoke gây ồn bị phạt đến 2 triệu đồng và tịch thu tang vật — [Tuổi Trẻ, 30/12/2025](https://tuoitre.vn/tp-hcm-giam-han-tieng-on-karaoke-nguoi-dan-hoan-nghenh-duoc-nhung-ngay-yen-tinh-20251228172409015.htm).
- VOV tóm tắt là "không cần máy đo, 24/24 giờ" — [VOV](https://vov.vn/tu-khoa/tieng-on) [snippet].
- **Mâu thuẫn** về mức phạt và về việc có cần đo hay không: phải đọc bản gốc trước khi trích.
- NĐ 45/2022 (theo dBA) và NĐ 282/2025 (trật tự công cộng) chạy song song — [LuatMinhKhue 2026](https://luatminhkhue.vn/hat-karaoke-loa-keo-keo-gay-on-ao-trong-khu-dan-cu-dip-tet.aspx) [snippet].

**Khiếu nại và thực thi**
- TP.HCM — [VnExpress International, 10/7/2025](https://e.vnexpress.net/news/news/karaoke-cacophony-in-hcmc-sees-neighbors-quarreling-authorities-deluged-with-complaints-4911577.html):
  - đường dây 1022 nhận "nearly 21,000 noise-related complaints" từ đầu 2024, chủ yếu về karaoke và nhạc lớn;
  - Chủ tịch phường 13 Bình Thạnh: "To impose fines, we need meters or to hire professionals, but the ward lacks the funds, and the process takes time";
  - người vi phạm thường tắt hoặc hạ nhạc khi cán bộ đến.
- Hà Nội — [VnExpress, 25/10/2022](https://vnexpress.net/cu-dan-do-thi-kho-vi-o-nhiem-tieng-on-4525562.html):
  - Viện Sức khỏe nghề nghiệp và Môi trường đo tại 12 trục đường/nút giao: ban ngày 77,8–78,1 dBA, ban đêm 65,3–75,7 dBA (vượt 10–20 dBA);
  - nguồn ồn: giao thông, karaoke/loa, làng nghề (máy giã cốm Mễ Trì), xưởng hàn/cơ khí, khoan, công trình xây dựng;
  - xử lý "rất khó thực hiện" vì việc đo phải do đơn vị độc lập được chứng nhận, và ồn nền thường đã vượt chuẩn.
- Hà Nội công bố quan trắc tự động cho không khí, mưa và ngập, nhưng không có tiếng ồn — [MOIT](https://moit.gov.vn/bao-ve-moi-truong/ha-noi-cung-cap-truc-tuyen-thong-tin-quan-trac-moi-truong-tu2.html) [snippet].
- Ngoài Nội Bài, chưa sân bay nào ở Việt Nam có hệ quan trắc ồn tự động — [JST VANJ 2024](https://jst.vanj.jp/wp-content/uploads/2024/11/Quan-trac-va-du-bao-tieng-on-hang-khong-%E2%80%93-bao-ve-moi-truong-song-quanh-san-bay.pdf) [snippet].

### Inferences
**Ánh xạ 22 lớp sang QCVN 26:2025** (suy luận dựa trên văn bản gốc):

| Lớp khóa luận | Hạng mục QCVN 26:2025 | Vai trò trong đánh giá |
|---|---|---|
| `workshop` (jackhammer, drill, saw, grinder, air_compressor) | Bảng 3 công trường (+ Bảng 4, +3 dBA cho máy đục/đóng cọc); Phụ lục thiết bị (máy nén khí, cưa máy, máy mài) cho Bảng 1 | nguồn bị quản lý |
| `music` (+ `voices` chồng lấp) | Bảng 3 "Loa" và cơ sở "cùng tòa nhà" (karaoke, bar, vũ trường, gym); NĐ 282/2025 | nguồn bị quản lý |
| `vehicle_pass_by`, `vehicle_idling`, `horn` | Bảng 5 đường bộ | nguồn bị quản lý |
| `train` | Bảng 5 đường sắt | nguồn bị quản lý |
| `sirens_and_alarms` | ghi chú (\*): loại trừ loa/còi xe chuyên dụng | nguồn có thể bị **loại khỏi** đánh giá |
| `jet_aircrafts`, `propeller_aircrafts` | không có bảng riêng | nhiễu khi đo nguồn khác |
| `lawn_mower…`, `vacuum_cleaner…` | "hoạt động dân sinh khác"; quạt thông gió ≥ 7,5 kW thuộc Phụ lục | nguồn bị quản lý (mức thấp) |
| lớp sinh vật (`dog…`, `birds`, `cicadas…`…) | không phải nguồn bị quản lý | nhiễu cần loại khi chọn thời gian đo (§3.1) và đo ồn nền (§2.5) |
| `thunder_fireworks_gunshot`, `glass_breaking` | điều kiện thời tiết (§3.3), ồn xung (§3.4) | cờ "khoảng đo bị nhiễm"; **không bao giờ** suy ra "súng" (ADR-0001) |

**Ba nhóm người dùng hợp lý ở Việt Nam** (không cần tuyên bố pháp lý):
1. **Cán bộ môi trường cấp phường/xã và đơn vị quan trắc được thuê.** Dùng timeline để quyết định *khi nào, ở đâu* mang máy loại 1 đến đo; tìm khoảng ≥ 5 phút nguồn không phát để đo ồn nền (§2.5); loại khoảng bị nhiễm (§3.1); và biết nguồn đã phát bao lâu trong từng khung giờ để chọn đúng dòng nới ngưỡng ở Bảng 2/Bảng 4.
2. **Ban quản lý chung cư hoặc tòa nhà hỗn hợp** (karaoke, gym, bar ở tầng dưới thuộc hạng mục "cùng tòa nhà" của QCVN 26:2025). Có nhật ký `music`/`workshop` theo giờ để đối thoại với hộ kinh doanh. Nhật ký này đáp ứng phần "thời gian, địa điểm" mà NĐ 282/2025 yêu cầu, **không** đáp ứng phần "mức độ ảnh hưởng".
3. **Nhà nghiên cứu** soundscape, giao thông, công trường: cần tìm kiếm qua hàng tuần ghi âm.

Khi người vi phạm hạ âm lượng lúc cán bộ đến, một nhật ký liên tục có dấu thời gian là thông tin mà cán bộ đến sau không có được. Tuy vậy, giá trị chứng cứ còn phụ thuộc chuỗi lưu giữ, thiết bị thu, và luôn thiếu dBA.

### Gaps
- Chưa đọc bản gốc NĐ 45/2022 Điều 22 và NĐ 282/2025 Điều 9; mức phạt hiện chỉ có từ nguồn thứ cấp, cần đối chiếu trên vbpl.moj.gov.vn.
- Chưa đọc gốc điều khoản chuyển tiếp trong Thông tư 01/2025/TT-BNNMT.
- Không có thống kê riêng về khiếu nại thi công ban đêm, không có số liệu năm 2026.
- Không tìm thấy mạng quan trắc ồn tự động công khai ở Hà Nội hoặc TP.HCM.

---

## 4. Quyền riêng tư và ràng buộc pháp lý của giám sát âm thanh

### Takeaway
- Ở châu Âu, giọng nói là dữ liệu cá nhân theo GDPR: CNIL đã cảnh cáo dự án "capteurs sonores" của Saint-Étienne năm 2019 và thành phố bỏ dự án.
- Ở Việt Nam, từ 01/01/2026 áp dụng Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 cùng NĐ 356/2025/NĐ-CP (thay NĐ 13/2023); chế tài nằm trong NĐ 330/2026 (hiệu lực 19/8/2026).
- Các mạng giám sát thật đã áp dụng privacy-by-design; SONYC là ví dụ rõ nhất.
- Thiết kế của khóa luận gồm: chỉ phát hiện *sự hiện diện* của `voices`, không ASR, không nhận dạng người nói, caption không chứa lời thoại, không suy luận tội phạm, lưu sự kiện có cấu trúc. Đây là một lợi thế để trình bày, nhưng chỉ đầy đủ khi có thêm chính sách lưu giữ "chỉ metadata".

### Cited Findings
- **CNIL và Saint-Étienne** — [Seban Avocats, 21/11/2019](https://www.seban-associes.avocat.fr/lavertissement-de-la-cnil-a-lencontre-du-projet-de-captation-de-bruit-suspect-par-la-ville-de-saint-etienne/?id=98615), [Banque des Territoires](https://www.banquedesterritoires.fr/saint-etienne-renonce-linstallation-de-capteurs-de-sons) [thứ cấp]:
  - thư cảnh cáo ngày 25/10/2019 gửi dự án thu và phân tích "bruits suspects";
  - CNIL viết "la voix d'une personne constitue une donnée à caractère personnel au sens de l'article 4-1) du RGPD" và dự án "ne saurait se fonder sur la base légale de l'intérêt légitime";
  - thành phố bỏ thử nghiệm.
- Năm 2021, La Quadrature du Net khiếu nại dự án cảm biến âm gắn camera ở Orléans — [Banque des Territoires](https://www.banquedesterritoires.fr/les-capteurs-sonores-dorleans-dans-le-viseur-de-la-quadrature-du-net) [snippet].
- **Privacy-by-design của SONYC** — [Mydlarz et al., 2019](https://ar5iv.labs.arxiv.org/html/1903.03195) [gốc]:
  - ghi đoạn audio 10 s, khoảng 3 lần/phút, khoảng cách ngẫu nhiên "to break up continuity of the audio samples for privacy reasons";
  - nén FLAC, mã hóa AES (khóa AES được mã hóa bằng RSA);
  - chuyên gia âm học độc lập đánh giá các đoạn có tiếng nói là "unintelligible as conversation";
  - IRB của NYU miễn xét duyệt thêm; có biển thông báo kèm FAQ.
- **Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15** thông qua 26/6/2025, hiệu lực 01/01/2026, gồm 5 chương 39 điều — [Cổng TTĐT Hà Tĩnh](https://hatinh.gov.vn/vi/bai-viet/luat-bao-ve-du-lieu-ca-nhan-chinh-thuc-co-hieu-luc-thi-hanh-tu-ngay-112026), [thuvienphapluat](https://thuvienphapluat.vn/van-ban/Cong-nghe-thong-tin/Luat-Bao-ve-du-lieu-ca-nhan-2025-91-2025-QH15-625628.aspx).
- **NĐ 356/2025/NĐ-CP** (31/12/2025) hướng dẫn luật và thay NĐ 13/2023 từ 01/01/2026: mở rộng danh mục dữ liệu cơ bản và nhạy cảm (Điều 3, 4), đổi cơ chế đánh giá tác động, quy định nhân sự bảo vệ dữ liệu — [PwC Vietnam, 28/01/2026](https://www.pwc.com/vn/vn/publications/legal-news-brief/20260128-new-rules-personal-data-protection.html), [LuatVietnam](https://luatvietnam.vn/legal-updates/new-features-of-decree-356-2025-compared-with-decree-13-2023-on-personal-data-protection-892-106712-article.html) [thứ cấp].
- Dữ liệu cơ bản gồm cả hình ảnh và một mục bao quát "thông tin khác giúp xác định một người"; dữ liệu sinh trắc học thuộc nhóm nhạy cảm — [thuvienphapluat Q&A](https://thuvienphapluat.vn/hoi-dap-phap-luat/danh-muc-du-lieu-ca-nhan-co-ban-tu-ngay-01012026-gom-co-nhung-du-lieu-nao-138076189.html) [snippet].
- **NĐ 330/2026/NĐ-CP** xử phạt vi phạm về an ninh mạng và bảo vệ dữ liệu cá nhân, hiệu lực 19/8/2026 — [LuatVietnam](https://luatvietnam.vn/tin-van-ban-moi/da-co-luat-bao-ve-du-lieu-ca-nhan-2025-so-91-2025-qh15-186-102925-article.html) [snippet].
- **Thiết kế trong repo:**
  - `voices`: "Không nhận dạng lời, không nhận dạng người nói… Caption không bao giờ được chứa lời thoại" — [`docs/taxonomy.md`](../../docs/taxonomy.md) §D1;
  - ngoài phạm vi: ASR, suy luận tội phạm/ý định/khẩn cấp, risk score, hệ cảnh báo — [`docs/SYSTEM.md`](../../docs/SYSTEM.md) §1.6; [ADR-0001](../../docs/decisions/ADR-0001-scope-and-datasets.md);
  - API **lưu WAV upload** vào `data/uploads` (25 file lúc kiểm) và chỉ xóa file khi lỗi hoặc không có dòng recording tương ứng — `services/api/app/recordings.py`, `services/api/app/main.py`.

### Inferences
- **Lập luận cho buổi bảo vệ:**
  1. Dự án bị CNIL chặn là dự án tìm "tiếng động đáng ngờ" — đúng hướng mà ADR-0001 đã loại bỏ.
  2. Đầu ra của khóa luận là bảng sự kiện (lớp, onset, offset, confidence), không phải audio hay lời nói.
  3. Giống SONYC và BirdNET-Pi, hệ thống có thể xử lý tại chỗ rồi chỉ giữ metadata.
- **Giới hạn của lập luận:**
  - Metadata gắn với một địa chỉ (ví dụ "có nhạc ở căn hộ X mỗi tối") vẫn có thể "giúp xác định một người", tức vẫn có thể là dữ liệu cá nhân. Nên nói là **giảm thiểu**, không phải **miễn trừ**; cần ý kiến luật sư.
  - Hiện hệ thống vẫn lưu audio upload, nên privacy-by-design mới là **thiết kế có thể làm**, chưa phải đặc tính đã có. Muốn nói là đặc tính thì cần chế độ lưu giữ ở §7, mục O2.

### Gaps
- Chưa xác nhận NĐ 356/2025 xếp "giọng nói/ghi âm" vào dữ liệu cơ bản hay sinh trắc học.
- Không tìm thấy hướng dẫn riêng của EDPB về cảm biến âm thanh.
- Chưa đọc văn bản gốc NĐ 330/2026; con số "phạt tối đa 3 tỷ đồng" chưa xác minh.

---

## 5. Yêu cầu triển khai: RTF, edge hardware, chi phí, dung lượng, độ trễ; kiểm chứng tối thiểu nào thuyết phục hội đồng?

### Takeaway
- Mạng giám sát thật dùng node khoảng 80 USD (Raspberry Pi), chấp nhận uptime khoảng 73%, và đến năm 2019 vẫn chưa phân loại trên thiết bị.
- Năm 2025, CNN nhẹ cỡ EfficientAT mn10 chạy < 0,25 s cho mỗi cửa sổ 10 s trên Raspberry Pi 4B; CNN14 mất khoảng 3,5 s (khi có GUI) và nóng tới khoảng 85 °C.
- Khóa luận đã đo trên CPU (container): recording 60,8 s xử lý trong 2,01 s (RTF ≈ 0,033, đã gồm upload); truy vấn hybrid 0,25 s.
- Hội đồng sẽ tin hơn nếu có thêm: RTF trên audio ≥ 1 h, ngân sách lưu trữ metadata so với audio, một smoke test trên ghi âm Việt Nam, và phản hồi của 1–2 người làm nghề.

### Cited Findings
- SONYC: Raspberry Pi 2B, khoảng 80 USD linh kiện mỗi node, IEC 61672-1 Type-2, 55 node, yield 73,2%, Wi-Fi là nguyên nhân downtime chính; phân vùng 12 GB giữ được khoảng 3 ngày offline; khi đầy 95% thì xóa audio trước dữ liệu mức âm; chưa phân loại trên node — [Mydlarz et al., 2019](https://ar5iv.labs.arxiv.org/html/1903.03195) [gốc].
- DYNAMAP: ANED chạy trên "ARM-based acoustic sensors", khả thi "both in terms of computational cost and classification performance"; cảm biến lệch 1,0 ± 0,9 dB so với Class 1 — [Benocci et al., 2020](https://doi.org/10.3390/s20020412) [gốc].
- Benchmark trên Raspberry Pi 4B — [Grau-Haro et al., arXiv:2509.14049, 2025](https://arxiv.org/html/2509.14049v2) [gốc]:
  - Pi 4B 4 GB, mỗi model chạy 24 h, cửa sổ 10 s trượt mỗi 5 s, xuất ONNX;
  - EfficientAT mn05/mn10: < 0,25 s cho mỗi đoạn 10 s (headless);
  - CNN6/9/13: khoảng ≤ 1 s;
  - CNN14: khoảng 3,5 s với GUI (headless nhanh hơn khoảng 2 s), nhiệt độ khoảng 85 °C;
  - tác giả khuyến nghị MobileNet và CNN6/CNN10 cho suy luận liên tục.
- PANNs trên Raspberry Pi bị hạ xung do nhiệt sau vài phút, làm tăng độ trễ — [arXiv:2306.09106](https://arxiv.org/html/2306.09106v2) [snippet].
- BirdNET-Pi: Raspberry Pi 4B/5 + micro thành trạm nghe 24/7, phân loại tại chỗ, tự trích clip phát hiện, có biểu đồ xu hướng — [Cornell Lab BirdNET-Pi](https://birdnet.cornell.edu/birdnet-pi/), [Raspberry Pi News](https://www.raspberrypi.com/news/classify-birds-acoustically-with-birdnet-pi/) [snippet].
- **Số đo của khóa luận** (repo):
  - f2, CPU container: upload + phân tích S-0016 mất 2,012 s; truy vấn hybrid (BGE-M3) 0,250 s — [`docs/thesis/tables/12_runtime.md`](../../docs/thesis/tables/12_runtime.md), [`demo_f2_e2e_20261002.json`](../../docs/measurements/demo_f2_e2e_20261002.json);
  - S-0016 dài 60,83 s (44,1 kHz, mono, PCM16) — [`data/manifests/datased_inventory.csv`](../../data/manifests/datased_inventory.csv);
  - f2 là ensemble 3 × `frame_mn10` (CNN khoảng 3M tham số) — [`docs/PAPER_NOTES.md`](../../docs/PAPER_NOTES.md) S32;
  - hệ thống phục vụ hiện tại là B0 (hop 5 s, 5 model fold; E2E S-0131 mất 1,55 s, nhưng **request đầu mất 49,8 s do nạp model**), demo chạy trên LBR V3 — [`CLAUDE.md`](../../CLAUDE.md) §3.
- **Quy mô DataSED:**
  - 717 WAV, tổng 18,68 h, trung bình 93,8 s, dài nhất 818 s — tính từ `datased_inventory.csv`;
  - bài báo ghi 712 recording — [IRIS](https://iris.unicampania.it/handle/11591/579845).
- **Giới hạn hiện tại của hệ thống:**
  - chỉ batch offline, streaming ngoài phạm vi ([`docs/SYSTEM.md`](../../docs/SYSTEM.md) §1.6); `services/stream/app` đang trống;
  - bảng recordings có cột `captured_at TIMESTAMPTZ` ([`db/migrations/001_event_store.sql`](../../db/migrations/001_event_store.sql)), nhưng filter truy vấn chỉ gồm `classes_all`, `temporal` (before/after/overlaps/within giữa hai lớp) và `duration` (`class_id`, `min_s`) — [`contracts/query_set.schema.json`](../../contracts/query_set.schema.json). **Chưa lọc được theo giờ thật**, nên câu ví dụ "sau 22:00" mới chạy được phần "kéo dài > 30 s".

### Inferences
- **Thông lượng:** RTF ≈ 2,012 / 60,83 ≈ 0,033, tức nhanh khoảng 30 lần thời gian thực. Nếu tuyến tính, một ngày audio mất khoảng 48 phút CPU — **chưa đo**, cần kiểm trên audio dài. Thời gian nạp model 49,8 s chỉ trả một lần cho mỗi tiến trình.
- **Edge:** một model mn10 < 0,25 s cho 10 s trên Pi 4B, nên ensemble 3–5 thành viên ước khoảng < 0,75–1,25 s cho 10 s (RTF < 0,13), chưa tính hậu xử lý và LBR. Khả thi trên giấy, phải đo. Nếu dùng CNN14 hoặc BEATs (~90M tham số) thì rủi ro trên Pi.
- **Dung lượng:**
  - audio 44,1 kHz / 16-bit / mono = 88,2 kB/s, khoảng 7,6 GB/ngày/cảm biến;
  - ở 16 kHz, khoảng 2,8 GB/ngày;
  - metadata sự kiện (vài trăm dòng × ~200 B) < 1 MB/ngày;
  - chênh hơn 3 bậc độ lớn. Đây vừa là lý do kỹ thuật, vừa là lý do privacy cho mô hình "xử lý tại biên, chỉ gửi metadata".
- **Độ trễ:** người làm nghề cần hai kiểu — cảnh báo thời gian thực (như NEA Singapore) và báo cáo ngày/tuần (như Svantek). Khóa luận thuộc kiểu thứ hai (hậu kiểm, báo cáo); nên nói thẳng điều này.

### Gaps
- Không có số Jetson; không có RTF SED end-to-end trên Pi 5.
- SONYC không nêu dung lượng mỗi ngày.
- Không có yêu cầu độ trễ nào do cơ quan Việt Nam đặt ra.
- Chưa có RTF của B0 (chưa có thời lượng S-0131 trong ghi chú này).

---

## 6. Miền ứng dụng khác trong phạm vi ADR-0001; miền nào thuyết phục nhất với hội đồng Việt Nam?

### Takeaway
Cùng một pipeline phục vụ được năm miền:
1. nhật ký tuân thủ ồn công trường;
2. nghiên cứu soundscape đô thị;
3. nghiên cứu ồn giao thông, cảng, sân bay;
4. tìm kiếm trong ghi âm dài kiểu bioacoustics;
5. quản lý tòa nhà hỗn hợp.

Với hội đồng Việt Nam, miền (1) và (5) thuyết phục nhất vì gắn thẳng vào các bảng của QCVN 26:2025 và vào những phàn nàn quen thuộc (thi công đêm, karaoke).

### Cited Findings
- **Công trường:** NEA Singapore (≤ 150 m, thời gian thực, Class 1); Svantek "Construction Compliance and Reporting"; SiteHive; SINTEF/Norsonic; QCVN 26:2025 Bảng 3/4 — các nguồn đã dẫn ở §2, §3.
- **Soundscape:** CENSE đo tỷ lệ hiện diện của traffic, voices, birds theo nhịp ngày — [HAL](https://hal.archives-ouvertes.fr/hal-03432916) [snippet].
- **Giao thông, cảng, sân bay:** DYNAMAP; Svantek đếm phương tiện theo ngày/tuần; ồn cảng Livorno; Nội Bài — các nguồn §1, §3.
- **Bioacoustics:** BirdNET-Pi chạy 24/7, tự trích clip — [Cornell](https://birdnet.cornell.edu/birdnet-pi/).
- **Tòa nhà:** hạng mục "cùng tòa nhà" của QCVN 26:2025 (gym, vũ trường, dạy nhạc, bar, nhà hàng, siêu thị, karaoke), ngưỡng A–C 50/45/40 dBA — [QCVN 26:2025](https://cdn.thuvienphapluat.vn/uploads/tintuc/2025/05/22/QCVN%2026_2025_BNNMT.pdf).

### Inferences
Xếp hạng cho hội đồng Việt Nam:
1. **Thi công, đặc biệt ban đêm.** Lớp `workshop` có 5 subclass (jackhammer, drill, saw, grinder, air compressor) khớp thiết bị nêu trong Phụ lục và ghi chú +3 dBA của QCVN. Câu "workshop sau 22:00 kéo dài > 30 s" là câu hỏi thật của cán bộ và ban quản lý dự án. Có tiền lệ quốc tế (NEA) và sản phẩm thương mại.
2. **Karaoke, loa, nhạc trong khu dân cư và tòa nhà.** Đây là nhóm phàn nàn lớn nhất ở TP.HCM. Giới hạn: `music` không phân biệt karaoke với radio hay loa quán, và hay chồng với `voices`. Chỉ nói "có nhạc", không kết luận "có karaoke".
3. **Nghiên cứu soundscape và giao thông** ở trường đại học, viện nghiên cứu: ít rủi ro pháp lý, chấp nhận sai số. Lưu ý `horn` là lớp yếu (frame-F1 baseline 0,134842; nhầm horn→sirens nhiều nhất — [`docs/taxonomy.md`](../../docs/taxonomy.md) §B3, §8.1), mà còi xe lại là nguồn quan trọng nhất của giao thông Việt Nam.
4. **Bioacoustics:** chỉ là "bài toán cùng dạng", taxonomy sinh vật của khóa luận quá thô để làm ứng dụng chính.
5. **Cảng, sân bay:** đúng chuyên môn của nhóm tác giả dataset nhưng ít liên quan tới người dùng tiềm năng ở Việt Nam.

Không đề xuất: an ninh, "phát hiện súng", "phát hiện đột nhập" qua kính vỡ, giám sát trường học (ADR-0001).

### Gaps
- Chưa tìm được nghiên cứu soundscape nào ở Việt Nam có dùng SED.
- Chưa xác minh Arbimon hay các nền tảng passive acoustic monitoring khác.

---

## 7. Tổng hợp: narrative tính thực tiễn, 2–4 bổ sung (T0/T1/T2), giới hạn trung thực

### Takeaway
Narrative trung thực: **"Khóa luận không thay máy đo ồn. Nó trả lời câu hỏi mà máy đo không trả lời được — nguồn nào, lúc nào, kéo dài bao lâu — trên hàng giờ ghi âm, và cho phép tìm lại bằng chứng bằng câu hỏi tự nhiên. Đây đúng là lớp mà DYNAMAP, SONYC, CENSE và các thiết bị thương mại 2024–2026 đang bổ sung, và đúng ba biến mà QCVN 26:2025 dùng để chọn ngưỡng."**

Bốn bổ sung nhỏ (hai T0, hai T1) trả lời trực tiếp hai lời phê bình dễ gặp nhất: "không thực tế" và "dữ liệu Ý thì áp dụng Việt Nam thế nào". Vì code đã đóng băng từ 18/11, cả hai việc T0 chỉ gồm tài liệu, đo đạc hoặc script ngoài core.

### Cited Findings
Các bằng chứng chịu lực chính (chi tiết và đường dẫn ở §1–§6):
- QCVN 26:2025/BNNMT thay QCVN 26:2010/BTNMT; ngưỡng theo nguồn × khung giờ × thời lượng; đánh giá bắt buộc dùng máy loại 1 do tổ chức đủ năng lực đo — [QCVN 26:2025](https://cdn.thuvienphapluat.vn/uploads/tintuc/2025/05/22/QCVN%2026_2025_BNNMT.pdf) [gốc].
- Khoảng 21.000 phản ánh qua 1022, phường thiếu máy đo — [VnExpress Intl 2025](https://e.vnexpress.net/news/news/karaoke-cacophony-in-hcmc-sees-neighbors-quarreling-authorities-deluged-with-complaints-4911577.html); bằng chứng phải thể hiện thời gian, địa điểm, mức độ ảnh hưởng — [Tuổi Trẻ News 2025](https://news.tuoitre.vn/how-decree-282-applies-and-what-evidence-needed-to-curb-karaoke-noise-in-vietnam-103251223143952307.htm).
- Svantek 26 lớp, phân loại trên clip kích hoạt, không công bố accuracy — [datasheet 2024](https://acsoft.co.uk/wp-content/uploads/2024/07/SvanNET-AI-UK-Datasheet.pdf).
- SONYC dùng node khoảng 80 USD, mã hóa và snippet ngẫu nhiên vì privacy — [Mydlarz 2019](https://ar5iv.labs.arxiv.org/html/1903.03195).
- mn10 < 0,25 s/10 s trên Pi 4B — [arXiv:2509.14049](https://arxiv.org/html/2509.14049v2).
- CNIL coi giọng nói là dữ liệu cá nhân — [Seban 2019](https://www.seban-associes.avocat.fr/lavertissement-de-la-cnil-a-lencontre-du-projet-de-captation-de-bruit-suspect-par-la-ville-de-saint-etienne/?id=98615).

### Inferences

**(a) Đoạn narrative mẫu cho báo cáo và buổi bảo vệ**

> *Bài toán thực tế.* Máy đo mức âm cho biết mức LAeq nhưng không cho biết nguồn. Trong khi đó, QCVN 26:2025/BNNMT (hiệu lực 14/11/2025) đặt ngưỡng khác nhau cho công trường, loa, giao thông đường bộ và đường sắt; theo ba khung giờ 06–18h, 18–22h, 22–06h; và nới ngưỡng tùy thời lượng phát ra tiếng ồn. Cán bộ và kỹ thuật viên quan trắc vì vậy phải biết *nguồn nào, lúc nào, bao lâu* trước khi quyết định đo ở đâu, đo khi nào và áp bảng nào. Ở TP.HCM, khoảng 21.000 phản ánh tiếng ồn từ đầu 2024 trong khi phường thiếu máy đo, và người vi phạm thường giảm âm lượng khi cán bộ đến.
>
> *Đóng góp.* Hệ thống biến hàng giờ ghi âm thành timeline sự kiện có onset/offset, lưu thành dữ liệu có cấu trúc, và trả lời câu hỏi tiếng Việt hoặc tiếng Anh kèm bằng chứng (recording + khoảng thời gian). Đây là lớp nhận dạng nguồn mà các dự án DYNAMAP, SONYC, CENSE và thiết bị thương mại (Svantek SvanNET AI, 2024) đang bổ sung lên trạm đo. Khác biệt là hệ thống có SED đa âm, có truy vấn tự nhiên, và có benchmark công khai, tái lập được.
>
> *Phạm vi trung thực.* Hệ thống không đo dBA và không thay máy đo loại 1. Đầu ra không phải bằng chứng vi phạm theo NĐ 45/2022. Hệ thống chỉ mô tả nguồn âm quan sát được, không suy luận hành vi hay ý định (ADR-0001). Đầu ra không chứa nội dung lời nói, và có thể triển khai theo hướng chỉ lưu metadata.

**(b) Bốn bổ sung đề xuất** (số giờ là ước lượng của người nghiên cứu)

| ID | Tier | Việc | Effort | Trả lời phê bình | Đầu ra / cách kiểm |
|---|---|---|---|---|---|
| B1 | **T0** | Bảng ánh xạ 22 lớp → hạng mục QCVN 26:2025 (bảng ở §3) và một **script ngoài core** tính thời lượng phát theo lớp × khung giờ QCVN (06–18 / 18–22 / 22–06) từ event store, dùng `captured_at` nhập tay cho vài recording demo; chỉ ra dòng nới ngưỡng tương ứng ở Bảng 2/4. Ghi rõ trên báo cáo "không phải kết quả đo mức ồn". | 5–7 h (doc 2 h + script 3–4 h + viết 1 h) | "Dữ liệu Ý thì áp dụng VN thế nào", "không thực tế" | 1 bảng + 1 trang báo cáo; câu "workshop sau 22:00" được minh họa bằng dữ liệu đã gắn giờ, ghi rõ là giờ giả định |
| B2 | **T0** | Benchmark audio dài trên CPU: RTF, RAM đỉnh, số sự kiện/giờ, byte/ngày (metadata so với WAV) cho input ≥ 1 h (nối các recording DataSED và **ghi rõ là nối**, hoặc một bản ghi thật dài); tách riêng thời gian nạp model. | 2,5–3 h | "Không thực tế": quy mô, chi phí, dung lượng | 1 file measurement; câu trả lời có số cho "một ngày audio tốn bao nhiêu" |
| B3 | T0 nếu kịp, nếu không thì **T1** | Smoke test hiện trường ở Việt Nam: 3 cảnh × 5–10 phút ghi bằng điện thoại (công trường; đường có xe máy và còi; hẻm có nhạc); người nghe kiểm 40–60 sự kiện top-k; báo cáo định tính và tỷ lệ đúng nguồn. Quy tắc riêng tư: tránh hội thoại ở gần, xóa WAV sau khi kiểm, chỉ giữ bảng sự kiện. | 5–6 h | "Dữ liệu Ý thì áp dụng VN thế nào" (đo domain shift thật, dù mẫu nhỏ) | Bảng kết quả + ví dụ lỗi; nhiều khả năng lộ điểm yếu của `horn` và `vehicle_*` với giao thông xe máy — báo cáo nguyên văn |
| B4 | **T1** | Kiểm chứng với người làm nghề: phỏng vấn 1–2 người (cán bộ môi trường phường/xã, kỹ thuật viên quan trắc, hoặc ban quản lý tòa nhà) 30 phút theo kịch bản 3 use case ở §3; thêm usability test nhỏ (5 người × 5 tác vụ, SUS). | 5–6 h | "Không thực tế / ai dùng"; hạn chế #6 trong [`docs/SYSTEM.md`](../../docs/SYSTEM.md) §11.3 | Bảng phản hồi + điểm SUS, đặt trong phần hạn chế hoặc đánh giá |

Tùy chọn (chỉ làm khi được phép phá đóng băng code):
- **O1 (T1, 6–8 h):** filter giờ thật trên `captured_at` + onset, kèm chip khung giờ QCVN trên giao diện. Trả lời câu hỏi "ví dụ 'sau 22:00' có chạy thật không?".
- **O2 (T1, 4–6 h):** chế độ "metadata-only" (không giữ WAV sau suy luận, hoặc tắt tiếng các đoạn chồng `voices` trong clip bằng chứng), kèm checklist một trang theo Luật 91/2025 và NĐ 356/2025. Trả lời câu hỏi về quyền riêng tư.

**T2 (hướng phát triển):**
- tích hợp máy đo loại 1 (LAeq,1s) để quy phần mức âm cho từng nguồn, như DYNAMAP hay Svantek;
- chạy trên Raspberry Pi 5 kèm streaming (`services/stream` hiện trống);
- fine-tune trên dữ liệu Việt Nam có nhãn (xe máy, còi, loa kéo, đóng cọc), tách `music` thành loa/karaoke;
- triển khai nhiều cảm biến, xây quy trình chuỗi lưu giữ bằng chứng;
- giải quyết license: dữ liệu CC-BY-NC-SA-4.0 nên một sản phẩm thương mại phải huấn luyện lại trên dữ liệu có quyền.

**(c) Giới hạn trung thực (nên đưa vào báo cáo)**
1. **SED không phải máy đo mức âm đã hiệu chuẩn.** QCVN 26:2025 bắt buộc máy loại 1 (TCVN 12527-1:2018), phương pháp TCVN 7878, hiệu chỉnh ồn nền, điều kiện thời tiết, và tổ chức đủ năng lực đo (§3.2–§4.1). Hệ thống không chứng minh được vượt chuẩn.
2. **Không phải chứng cứ pháp lý.** NĐ 282/2025 đòi bằng chứng thể hiện cả "mức độ ảnh hưởng"; thiết bị chuyên dụng ở Paris còn phải homologation mới được dùng để phạt.
3. **Domain shift.** Dữ liệu từ Ý, một phần lấy từ kho online; recording trung bình chỉ 94 s; soundscape Việt Nam (xe máy, còi, loa kéo) chưa được đo.
4. **Lớp yếu đúng chỗ quan trọng.** `horn` có frame-F1 baseline 0,1348 và hay bị nhầm sang `sirens_and_alarms`; hai lớp gộp `sirens_and_alarms` và `thunder_fireworks_gunshot` không tách được ([`docs/taxonomy.md`](../../docs/taxonomy.md) §7).
5. **Không có lớp karaoke.** `music` và `voices` chỉ nói "có nhạc, có người".
6. **Chưa lọc được theo giờ thật.** Cột `captured_at` có nhưng chưa dùng trong truy vấn; DataSED cũng không có giờ ghi.
7. **Thời gian xử lý mới đo một lần** trên CPU laptop, đã gồm upload; chưa có số đo trên audio dài hay trên thiết bị biên.
8. **Chưa đánh giá người dùng** (SYSTEM.md §11.3 #6).
9. **Privacy mới ở mức thiết kế.** Hệ thống vẫn lưu WAV upload; metadata gắn với địa chỉ vẫn có thể là dữ liệu cá nhân.
10. **License NC-SA** giới hạn việc thương mại hóa model huấn luyện trên DataSEC/DataSED ([`docs/DATA_PLAN.md`](../../docs/DATA_PLAN.md) §3).

**Hỏi–đáp nhanh cho buổi bảo vệ**

| Câu hỏi của hội đồng | Gợi ý trả lời |
|---|---|
| "Có thay được máy đo không?" | Không. Hệ thống là lớp sàng lọc và khoanh vùng: chọn thời điểm, vị trí đo, đo ồn nền, loại nhiễu (QCVN §2.5, §3.1). |
| "Dữ liệu Ý thì dùng ở Việt Nam thế nào?" | Taxonomy trùng hạng mục nguồn của QCVN và của sản phẩm thương mại; pipeline độc lập với dữ liệu (taxonomy là config); domain shift được thừa nhận và có smoke test B3. |
| "Có nghe lén người dân không?" | Không có ASR, caption không chứa lời thoại, không suy luận hành vi; dự án bị CNIL chặn là loại "tiếng động đáng ngờ" mà ADR-0001 đã loại bỏ; có thể chạy chế độ chỉ metadata (O2, T2). |
| "Chạy thật được không?" | RTF khoảng 0,033 trên CPU; CNN cỡ mn10 chạy được trên Pi 4B theo benchmark năm 2025; SONYC từng dùng node khoảng 80 USD. |

### Gaps
- Toàn bộ B1–B4 và O1–O2 mới là đề xuất, chưa có kết quả.
- Mọi tuyên bố về giá trị chứng cứ hay xử lý dữ liệu cá nhân cần luật sư xác nhận.
- Mức phạt của NĐ 45/2022 và NĐ 282/2025 phải đối chiếu bản gốc trước khi đưa vào báo cáo.
