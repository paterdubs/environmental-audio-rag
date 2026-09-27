# RELATED_WORK.md — Công trình liên quan

> ⚠️ **Đây CHƯA phải literature review hoàn chỉnh.** Nó là khung cho Chương 2 báo
> cáo, kèm bảng trích xuất để điền dần.
>
> **Nguyên tắc cứng: không bịa trích dẫn.** Mọi ô chưa xác minh giữ nguyên
> `⚠️ CẦN XÁC MINH`. Một paper chỉ được viết vào báo cáo khi có đủ: tác giả, năm,
> venue, DOI/URL, và ngày truy cập.
>
> Khái niệm và công thức đề tài dùng: [SYSTEM.md §2](SYSTEM.md). File này theo dõi
> *văn liệu* và *mức xác minh*.

---

## 0. Mức xác minh

| Mức | Nghĩa |
|---|---|
| **V0** | Chưa tìm |
| **V1** | Biết tên/khái niệm nhưng chưa có nguồn chính |
| **V2** | Có DOI/URL, chưa đọc kỹ |
| **V3** | Đã đọc, đã trích xuất vào bảng §8 |
| **V4** | Đã đối chiếu số liệu, dùng được để so sánh trực tiếp |

**Chỉ V3 và V4 được trích dẫn trong báo cáo.**

---

## 1. Hai dataset của đề tài — V2

Đây là hai nguồn duy nhất hiện đã xác minh được metadata.

| | DataSEC | DataSED |
|---|---|---|
| Tiêu đề | DataSEC — Dataset for Sound Event Classification of environmental noise | DataSED — Dataset for Sound Event Detection of environmental noise |
| Tác giả | Fredianelli L., Artuso F., Pompei G., Licitra G., Iannace G., Akbaba A. | (cùng nhóm) |
| Công bố | 2025-09-02 | 2025-05-05 |
| Record DOI | `10.5281/zenodo.17033970` | `10.5281/zenodo.15346092` |
| Concept DOI | `10.5281/zenodo.15340688` | `10.5281/zenodo.15346091` |
| License | `cc-by-nc-sa-4.0` | `cc-by-nc-sa-4.0` |
| Mức | **V2** | **V2** |

Nguồn: `data/reference/zenodo_datasec_17033970.json`,
`data/reference/zenodo_datased_15346092.json`.

### Bài báo mô tả hai dataset — tìm thấy 26/09/2026, **V3 từ 27/09** (đọc trực tiếp toàn văn)

| Trường | Giá trị |
|---|---|
| Trích dẫn | Fredianelli L., Artuso F., Pompei G., Licitra G., Iannace G., Akbaba A. (2025). *Environmental Noise Dataset for Sound Event Classification and Detection.* **Scientific Data**. |
| DOI / định danh | `10.1038/s41597-025-05991-w` · PMCID PMC12572321 · PMID 41162415 |
| URL | https://www.nature.com/articles/s41597-025-05991-w · https://pmc.ncbi.nlm.nih.gov/articles/PMC12572321/ |
| Truy cập | 26/09/2026 qua tóm tắt `WebFetch` (V2); **27/09/2026 tải thẳng HTML cả hai bản (curl), trích văn bản bằng code và đọc toàn bộ** (V3). SHA-256 trang: Nature `abbcd099…`, PMC `6211e1f6…` |

**Đọc trực tiếp 27/09 — những gì bản tóm tắt bỏ sót hoặc chưa chắc** (số đối chiếu với archive
bằng `scripts/report_polyphonic_coverage.py` → [polyphonic_coverage_20260927.md](measurements/polyphonic_coverage_20260927.md)):

- **Xác nhận không có baseline:** bài chỉ có Background, Methods, Data Record, Technical
  Validation, Usage Notes — không model, không metric, không split khuyến nghị.
- **Nguồn âm thanh có một phần từ Freesound và AudioSet**, và mọi file "đã bị cắt, dán, trộn,
  sửa tay" (mục Methods). Với DataSED: "trong một số trường hợp track được sửa tay để bỏ đoạn dài
  không đổi, **hoặc âm thanh được thêm tay** để track sinh động hơn" (Data Record). Hệ quả cho đề
  tài: (a) encoder pretrain trên AudioSet (CNN14, BEATs, frame_mn) có thể đã thấy một phần âm
  thanh gốc — không định lượng được vì bài không công bố danh sách nguồn; (b) không phải mọi đồng
  xuất hiện trong DataSED là tự nhiên. Ghi vào Hạn chế (PAPER_NOTES S31).
- **Bản polyphonic và monophonic** là hai phiên bản nhãn của cùng tập audio; bài không nói bản
  polyphonic bỏ recording nào. Archive: `Polyphonic_sound_detection.csv` chỉ phủ **703**
  recording (S-0001…S-0703), bản monophonic phủ 717. 14 recording S-0704…S-0717 — đúng tập có nhãn
  `wind_turbine` — không có ground truth polyphonic nhưng nằm trong split benchmark của đề tài
  (PLAN nợ #25, PAPER_NOTES S30).
- **Số liệu tự mâu thuẫn trong bài:** văn bản ghi 712 file, dài nhất 285.0 s, tổng ~17.02 h,
  4309 nhãn monophonic; Bảng 3 của chính bài cộng ra **4323** nhãn. Archive: 717 file, dài nhất
  818.3 s, 18.68 h — nhưng số nhãn polyphonic (4034) và monophonic (4309) **khớp đúng** văn bản.
  7/22 lớp trong Bảng 3 lệch archive 1–5 nhãn.
- DataSEC trong bài: 4292 file, 18 h 26 phút, DOI `10.5281/zenodo.15340689` — đây là phiên bản
  cũ; đề tài dùng record v3 `17033970` (5,048 file, 23.7082 h). Con số "4,292 / 18h26" từng bị
  nghi là tóm tắt đọc nhầm (mục dưới) là **số thật của bài**, không phải lỗi tóm tắt.
- Gán nhãn: nghe bằng tai nghe trong phòng yên tĩnh, công cụ Python tự viết; bài nói có "nghe lại
  bởi nhiều người vận hành" nhưng **không báo số đo agreement nào** → phép đo 8 cặp trùng của đề
  tài (0.5785 event-F1 người vs người) vẫn là thông tin mới.

Nội dung theo tóm tắt 26/09 (giữ để truy vết; phần mâu thuẫn đã được đoạn trên thay thế):

- **Không có thí nghiệm baseline nào** (không model, không metric) → nếu đúng, số của đề tài
  có thể là baseline SED đầu tiên được báo cáo trên DataSED. Claim này còn cần systematic
  search các bài trích dẫn dataset.
- Thống kê bản monophonic: 712 file, trung bình 87.18 s, tổng ~17.02 h; ví dụ theo lớp: jet
  27.1 s (100 nhãn), propeller 23.9 s (218 nhãn), wind turbine 33.9 s (113 nhãn).
  **Khác** archive đã đo (717 WAV, 18.6847 h) → theo nguyên tắc dưới đây, archive là sự thật.
  Một tóm tắt khác (WebSearch) ghi "hơn 35 giờ, 712 recording, hơn 4000 nhãn" → **không dùng**.
- Gán nhãn: nghe tai nghe trong phòng yên tĩnh, công cụ gán nhãn Python tự viết, kiểm tra
  không chồng event cùng lớp; **không báo inter-annotator agreement** → phép đo 8 cặp trùng của
  đề tài (0.5785 event-F1 người vs người) là thông tin mới.
- Không khuyến nghị split train/test.

### Còn phải làm

- [x] **Tìm paper kèm dataset — tìm thấy 26/09:** *Scientific Data* 2025 (mục trên). Việc
      kiểm Zenodo trước đó (dòng dưới) không thấy vì record không liệt kê publication.
- [x] Tìm paper kèm dataset — **đã kiểm tra record DataSEC (Zenodo 17033970,
      v3), không có publication/venue nào được liệt kê**, không có "related
      identifiers"/"cited by". ⚠️ Đây là kết quả từ tóm tắt `WebFetch` (mô hình
      nhỏ đọc trang), **không phải đọc trực tiếp HTML** — theo đúng bài học đã
      rút ra ở ADR-0015 (tóm tắt WebSearch từng báo sai license), kết quả này
      cần một người **mở trực tiếp trang Zenodo xác nhận lại** trước khi coi là
      chốt. Chưa kiểm DataSED (15346092).
- [x] ~~⚠️ Chênh lệch "4,292 mẫu, 18h26" của DataSEC~~ — **giải quyết 27/09**: đó là số in
      trong chính bài *Scientific Data* (DOI Zenodo `15340689`, phiên bản cũ), không phải tóm
      tắt đọc nhầm. Đề tài dùng record v3 `17033970` (5,048 file, 23.7082 h — đo từ archive).
      Khi trích bài, ghi rõ bài mô tả phiên bản cũ hơn bản đề tài dùng.
- [x] Đối chiếu số file và số giờ trong paper với archive thật — **xong 27/09**
      ([polyphonic_coverage_20260927.md](measurements/polyphonic_coverage_20260927.md)): DataSED
      712 vs 717 file, 17.02 vs 18.68 h; số nhãn khớp; Bảng 3 của bài tự mâu thuẫn (4323 vs
      4309). Archive là sự thật, không ép số theo bài.
- [ ] Xác minh có paper nào đã công bố baseline trên hai dataset này chưa. Nếu có,
      đó là baseline để so sánh trực tiếp → nâng lên V4. **26/09:** bài dataset không có
      baseline (theo tóm tắt); một WebSearch ("DataSED sound event detection results") không
      tìm thấy bài nào khác — **chưa phải systematic search**, còn phải tìm các bài trích dẫn
      DOI `10.1038/s41597-025-05991-w`.
- [x] **DataSEC và DataSED có chia sẻ nguồn ghi âm — đã đo, không phải suy đoán.**
      Cổng D3 tìm được **3 cặp trùng xuyên dataset**, hai cặp similarity
      **1.000000** (không phải trùng ngẫu nhiên): `Sirens-0046.wav` (DataSEC) ↔
      `S-0233.wav` (DataSED, 35 s chồng lấp), `Sirens-0067.wav` ↔ `S-0211.wav`
      (13 s), và `Train-0012.wav` ↔ `S-0213.wav` (sim 0.9548, 31 s). Cả 6 tác
      giả trùng nhau, công bố cách nhau 4 tháng — khớp giả thuyết ban đầu. Xử lý:
      loại 11 clip DataSEC khỏi pretraining (0.2179%, dải `minor`), RQ1 vẫn hợp
      lệ. Nguồn: `docs/measurements/dedup_20260923.md`,
      [ADR-0009](decisions/ADR-0009-nguong-phu-thuoc-overlap.md). **Đây là dữ
      kiện tự đo, không phải trích dẫn văn liệu — không nâng mức V, nhưng viết
      thẳng vào báo cáo được vì có artifact kiểm chứng.**

---

## 2. Sound Event Detection

### Nội dung cần tổng hợp

| Chủ đề | Mức | Ghi chú |
|---|---|---|
| Strong vs weak label, và vì sao strong label cần cho grounding | V1 | Khái niệm đã dùng ở [SYSTEM §2.1](SYSTEM.md) |
| CRNN cho SED | V1 | Kiến trúc baseline của đề tài thuộc họ này |
| Pretrained audio transformer (AST, PaSST, BEATs) | V1 → V2 (26/09); Schmid và cộng sự 2025 **V3** (26/09 tối) | Xem [ADR-0002](decisions/ADR-0002-encoder-va-nhanh-transfer.md) về lý do không chọn ban đầu; bản pretrain **theo frame** trên AudioSet Strong: Schmid và cộng sự 2025, §2.1 (2) — dùng cho Track 2 (ADR-0032) |
| PANNs / AudioSet pretraining | V1 → **V2**; chi tiết kiến trúc **V3** (26/09) | Encoder đề xuất; pool CNN14 đối chiếu với code gốc, §2.1 |
| Threshold calibration và hậu xử lý | V1 → **V3** (cSEBB, 26/09) | Xem [ADR-0003](decisions/ADR-0003-threshold-va-post-processing.md); cSEBB §2.1 |
| Event-based F1 và collar | V1 → **V2** | `sed_eval`; Mesaros và cộng sự 2016 (từ danh mục tham khảo) §2.1 |
| **PSDS** và ba tiêu chí DTC/GTC/CTTC | V1 → **V2** | `psds_eval`; tham số ở [evaluation_protocol §3.3](evaluation_protocol.md); Bilen 2020, Ferroni 2021, Ebbers 2022 §2.1 |
| DCASE task SED — giao thức và baseline | V1 → V2 → **V3** (27/09) | DCASE 2016 T3 (ghi âm thật) §2.1 — mốc định cỡ event-F1 |
| Data augmentation cho SED (mixup, FilterAugment) | **V2** (26/09) | Dùng trong SED v2 (ADR-0030), §2.1 |
| Soundscape tổng hợp từ event cô lập (DESED) | **V2** (26/09) | Ý tưởng transfer thay pretraining ([PAPER_NOTES §5](PAPER_NOTES.md)) |

### Câu hỏi cần văn liệu trả lời

1. Giá trị collar và segment length nào là quy ước chuẩn để kết quả so được?
2. Hai scenario PSDS nào được dùng phổ biến nhất, với tham số nào?
3. Median filter và event tối thiểu thường suy từ đâu — train hay dev?
   (Đề tài chọn train, [ADR-0003](decisions/ADR-0003-threshold-va-post-processing.md);
   cần đối chiếu với thực hành phổ biến.)

**Trả lời một phần câu 1 (26/09):** DCASE 2016 Task 3 (ghi âm thật) lấy **segment-based ER
1 s** làm metric chính; event-based dùng collar **250 ms, onset-only**. Protocol của đề tài
(onset 200 ms **và** offset max(200 ms, 20%)) chặt hơn → số event-F1 không so thẳng được, chỉ
dùng để định cỡ.

### 2.1 Nguồn đã tra cho giai đoạn cải thiện SED (26/09/2026, [ADR-0030](decisions/ADR-0030-cai-thien-sed-v2.md))

Mỗi mục ghi: trích dẫn → cách tiếp cận → số đã đối chiếu → dùng ở đâu → còn phải làm.
"Tóm tắt WebFetch" nghĩa là một model nhỏ đọc trang rồi tóm tắt. Số từ đó là **V2** cho tới
khi người đọc trực tiếp bảng gốc (bài học ADR-0015).

**(1) Ebbers, Germain, Wichern, Le Roux (2024). *Sound Event Bounding Boxes.* Proc.
Interspeech 2024, tr. 562–566. DOI `10.21437/Interspeech.2024-2075`.** — **V3**

- Tiếp cận: đọc **trực tiếp 5 trang PDF** (ảnh trang), 26/09.
- Ý chính:
  - Ngưỡng theo frame buộc chặt biên event với độ tin cậy.
  - SEBB = (lớp, onset, offset, độ tin cậy); ngưỡng chỉ quyết định giữ hay bỏ hộp, không dời
    biên.
  - cSEBB tìm onset/offset bằng cực trị của delta sau bộ lọc bậc τ, gộp khoảng trống bằng
    ngưỡng γ (abs hoặc rel).
  - Lưới trong bài: τ ∈ {0.32, 0.48, 0.64} s; γ ∈ {0.15, 0.2, 0.3 abs; 1.5, 2, 3 rel};
    tune theo lớp trên tập validation.
- Số:
  - Trên 13 hệ thống DCASE 2023 T4a (CV 5 fold trên tập eval công khai), cSEBB hơn median
    filter trung bình **4.1 điểm PSDS1** và **3.4 điểm F1** (collar onset 200 ms, offset
    max(200 ms, 20%) — trùng protocol của đề tài).
  - Trong thiết lập CV 5 fold trên eval: hệ thắng giải .644 → .703 PSDS1, F1 .688 → .734.
  - Khi tune đúng cách trên output validation (điểm thô từ Xiao, Li, Barahona, baseline;
    Kim gửi điểm đã hậu xử lý): SOTA mới .686 PSDS1 (Kim) và .706 F1 (Xiao). Abstract ghi
    ".644 → .686 PSDS1".
- Mã tham chiếu: `github.com/merlresearch/sebbs`, license **AGPL-3.0**. Đề tài **tự viết lại**
  theo mô tả trong bài (`ml/postprocessing/sebb.py`), không chép mã.
- Dùng ở: [PAPER_NOTES](PAPER_NOTES.md) S14 (âm tính trên posterior v1), lưới chọn v2.

**(2) Schmid F., Morocutti T., Foscarin F., Schlüter J., Primus P., Widmer G. (2025).
*Effective Pre-Training of Audio Transformers for Sound Event Detection.* ICASSP 2025
(IEEE Xplore 10888942); arXiv:2409.09546 (v1 14/09/2024, v2 28/11/2024).** — **V3** (26/09,
cổng T0 của ADR-0031 §3)

- Tiếp cận: **đọc trực tiếp** PDF arXiv v2 (5 trang), README, file LICENSE và code model của repo
  (`models/frame_mn/*`, `inference.py`, `models/prediction_wrapper.py`). Trước đó chỉ có tóm
  tắt WebFetch của bản HTML v1 (V2).
- Ý chính: pretrain transformer trên nhãn **theo frame** AudioSet Strong (bước 3, sau SSL/ImageNet
  và AudioSet Weak). Teacher: sampler cân bằng (trọng số ∝ nghịch tần suất theo tổng thời gian
  nhãn), frequency warping, FilterAugment, Freq-MixStyle, mixup; BiGRU 2 lớp (hidden 1024–2048)
  trên transformer; 30 epoch. Ensemble 15 teacher (3 mỗi kiến trúc, PSDS1 47.1) → knowledge
  distillation theo frame cho student **không** có sequence model, 120 epoch, chỉ mixup.
- Kiến trúc đầu ra: embedding S×D (S = 250, 496, 250, 62, 497; D = 768, 768, 768, 3840, 768 cho
  ATST-F, BEATs, fPaSST, M2D, ASiT) đưa về 250 frame / 10 s (**40 ms**) bằng adaptive avg pool
  (S > 250) hoặc nội suy tuyến tính (S < 250), rồi lớp tuyến tính.
- Cài đặt train AudioSet Strong: Adam, cosine + 5,000 bước warmup, lưới lr {7e-5, 1e-4, 3e-4,
  6e-4, 1e-3, 3e-3}, batch 256, median filter 0.48 s chung mọi lớp, 3 seed; kiểm định ASO
  α = 0.05 (Bonferroni).
- Số (đối chiếu bảng gốc v2):
  - Bảng I, PSDS1 AudioSet Strong (không variance penalty), ATST-F / BEATs / fPaSST / M2D / ASiT:
    đủ pipeline 45.8 / 46.5 / 45.4 / 46.3 / 46.2; hệ thống của Li và cộng sự (tính lại bằng PSDS1
    mới) 40.9 / 36.5 / 38.7 / 36.9 / 37.0. Dòng "checkpoint cũ 34.7 / 29.0 / 29.2" trong bản ghi V2
    trước đây **không có trong v2** (lấy từ HTML v1) → bỏ.
  - Bảng II, DESED (PSDS1 có variance penalty), đủ pipeline: **fine-tune** 48.2 / 49.2 / 48.2 /
    48.7 / 47.6; **frozen** (đóng băng transformer, chỉ train lớp tuyến tính) 47.7 / 48.1 / 45.4 /
    49.2 / 48.1. Frozen gần bằng fine-tune.
  - Fine-tune DESED dùng layer-wise lr decay **0.5** (bài báo); ví dụ DC16-T2 trong README dùng
    0.95. Lr chọn bằng lưới riêng mỗi thí nghiệm; DESED và DC16-T2 mỗi thí nghiệm 4 seed.
  - MAESTRO (ngoài miền): không cải thiện rõ → lợi ích chỉ có khi âm thanh và nhãn gần ontology
    AudioSet (lớp DataSED thuộc trường hợp này).
- README (thêm, không có trong bài): bỏ 2 lớp transformer cuối làm DESED tăng (ATST-F 50.4 →
  51.1, BEATs 48.6 → 51.1, cấu hình baseline DCASE 2023). `frame_mn06` (1.62M) và `frame_mn10`
  (3.83M tham số) ghi "NEW", **không có số nào trong bài** → chất lượng chưa được xác minh.
- Repo: `github.com/fschmid56/PretrainedSED`, **MIT** (đọc LICENSE). Release v0.0.1:
  `frame_mn10_strong_1.pt` khoảng 15.5 MB; `BEATs_strong_1.pt` khoảng 364 MB;
  `ATST-F_strong_1.pt` khoảng 344 MB; đều 447 lớp.
- Frontend `frame_mn` (đọc `Frame_MN_wrapper.py`): 128 mel, n_fft 512, win 400, hop 160 (16 kHz,
  10 ms), fmin 0; có augmentation biên filterbank lúc train. Code `frame_mn` dựa trên MobileNetV3
  của EfficientAT.
- **Chuỗi license** (GitHub API `/license` + đọc LICENSE, 26/09):
  - `fschmid56/EfficientAT` MIT; `microsoft/unilm` (BEATs) MIT; `kkoutini/PaSST` và
    `facebookresearch/deit` Apache-2.0.
  - `Audio-WestlakeU/audiossl` (ATST-F): code MIT, **checkpoint CC BY 4.0** (phải ghi công).
  - `nttcslab/m2d`: license riêng dạng PDF (chưa đọc) → **không dùng M2D**.
  - ASiT: chưa kiểm.
- Dùng ở: ADR-0030 §7; ADR-0031 §3 (Track 2, duyệt 26/09); ADR-0032 (thiết kế Track 2).

**(3) Kong Q., Cao Y., Iqbal T., Wang Y., Wang W., Plumbley M. D. (2020). *PANNs: Large-Scale
Pretrained Audio Neural Networks for Audio Pattern Recognition.* IEEE/ACM TASLP (2020);
arXiv:1912.10211 (v5 23/08/2020).** — **V2**; chi tiết kiến trúc **V3**

- Tiếp cận: metadata trên arXiv (arXiv **không ghi** vol/pages → ⚠️ CẦN XÁC MINH trên IEEE);
  venue TASLP 2020 thấy qua bản postprint của Surrey. **Đọc trực tiếp code**
  `qiuqiangkong/audioset_tagging_cnn/pytorch/models.py` (26/09).
- Dữ kiện đối chiếu từ code: `Cnn14.forward` có `conv_block1…5` với `pool_size=(2, 2)` và
  `conv_block6` với `pool_size=(1, 1)`, pool `avg`, dropout 0.2 sau mỗi khối → trục thời
  gian nén **/32**. Encoder trong repo nén /64 (pool cả khối 6) và không có dropout giữa các
  khối.
- Dùng ở: PAPER_NOTES S13, ADR-0030 §1.

**(4) DCASE 2016 Task 3 — *Sound event detection in real life audio*: trang task và trang kết
quả** (dcase.community/challenge2016/…). Truy cập 26/09 (tóm tắt, V2); **27/09 tải thẳng HTML
hai trang và đọc văn bản trích bằng code — V3**, mọi số dưới đây khớp. SHA-256 trang: task
`40b64dd2…`, kết quả `6d4a78cf…`.

- Trang task: metric chính là **ER theo đoạn 1 s** ("Error rate will be evaluated in one-second
  segments over the entire test set"); `sed_eval` khớp baseline với `time_resolution=1`,
  `t_collar=0.250`. Hai cảnh: home 11 lớp, residential area 7 lớp. Dữ liệu TUT Sound Events 2016:
  ghi binaural (micro trong tai), mỗi địa điểm 3–5 phút, 44.1 kHz / 24 bit. Chia dev/eval nới
  khỏi 70-30 (home 40–80%, residential 60–80% instance mỗi lớp vào dev); dev có 4 fold, metric
  tính sau khi gộp cả 4 fold.
- Trang kết quả: cột "Event-based (overall / onset-only evaluation dataset)".
  - Baseline (Heittola 2016): segment ER 0.8773 / F1 34.3%; event ER 1.7303 / F1 6.3%.
  - Adavanne_task3_1: 0.8051 / 47.8%; event 5.1248 / 4.8%.
  - Adavanne_task3_2: 0.8887 / 37.9%; event 7.5286 / 4.7%.
  - Vu_task3_1: 0.9124 / 41.9%; event 2.0949 / 6.3%.
- Dùng ở: bảng bối cảnh (PAPER_NOTES §7) — event-F1 thấp là đặc thù ghi âm thật. **Khác
  dataset, khác collar → không so trực tiếp.**

**(5) Nam H., Kim S.-H., Park Y.-H. (2022). *FilterAugment: An Acoustic Environmental Data
Augmentation Method.* ICASSP 2022; arXiv:2110.03282.** — **V2**

- Tiếp cận: abstract trên arXiv.
- Số trong abstract: PSDS tăng **6.50%** so với 2.13% của frequency masking; EER speaker
  verification 1.22% so với 1.26%; góp phần hạng 3 DCASE 2021 T4.
- Code tham chiếu: `github.com/frednam93/FilterAugSED`.
- Dùng ở: `ml/training/augment.py`. Đề tài dùng dạng **cộng dB theo dải** cho đặc trưng
  log-mel dB đã chuẩn hoá; có loại step và linear như bản ICASSP 2022.

**(6) Zhang H., Cisse M., Dauphin Y. N., Lopez-Paz D. (2018). *mixup: Beyond Empirical Risk
Minimization.* ICLR 2018; arXiv:1710.09412.** — **V2** (metadata đối chiếu trên arXiv).
Dùng ở `ml/training/augment.py` (mixup nhãn mềm trên log-mel, cách PANNs áp dụng).

**(7) Turpault N., Serizel R., Shah A. P., Salamon J. (2019). *Sound Event Detection in
Domestic Environments with Weakly Labeled Data and Soundscape Synthesis.* DCASE Workshop 2019,
New York.** — **V2** (metadata qua kết quả tìm kiếm). Nguồn của DESED (soundscape tổng hợp
bằng Scaper). Dùng ở: ý tưởng soundscape tổng hợp từ DataSEC (PAPER_NOTES §5).

**(8) Chỉ thấy trong danh mục tham khảo của (1)** — **V2**, chưa mở bài gốc:

- Mesaros A., Heittola T., Virtanen T. (2016). *Metrics for polyphonic sound event
  detection.* Applied Sciences 6(6):162 (DOI ⚠️ CẦN XÁC MINH; trang MDPI chặn truy cập tự
  động 26/09).
- Bilen Ç. và cộng sự (2020). *A framework for the robust evaluation of sound event detection.*
  ICASSP 2020 — PSDS.
- Ferroni G. và cộng sự (2021). *Improving sound event detection metrics: insights from DCASE
  2020.* ICASSP 2021.
- Ebbers J., Haeb-Umbach R., Serizel R. (2022). *Threshold independent evaluation of sound
  event detection scores.* ICASSP 2022 (`sed_scores_eval`).
- Nam H., Kim S.-H., Park Y.-H. (2022). *Frequency dynamic convolution: frequency-adaptive
  pattern recognition for sound event detection.* Interspeech 2022.
- Shao N., Li X., Li X. (2023). *Fine-tune the pretrained ATST model for sound event
  detection.* arXiv:2309.08153.

**(9) Tổng quan DCASE 2024 Task 4** (Cornell và cộng sự, arXiv:2406.08056) — **V1**: chỉ thấy
qua tóm tắt tìm kiếm (ATST-Frame 40 ms, BEATs, FDY conv, hệ nhiều nhánh). Chưa đọc.

---

## 3. Transfer learning và domain shift

| Chủ đề | Mức |
|---|---|
| Transfer từ clip cô lập sang soundscape liên tục | V1 |
| Fine-tuning vs frozen encoder vs multi-task | V1 |
| **Duplicate leakage khi cùng nguồn xuất hiện ở nhiều dataset** | V1 |
| Hierarchical coarse/subclass prediction | V1 |
| Class imbalance trong pretraining corpus | V1 |

### Khoảng trống đề tài nhắm tới — C3

Cần tìm xem có công trình nào **audit duplicate xuyên dataset trước khi báo Δ
transfer** hay không. Giả thuyết: phần lớn không làm.

> ⚠️ CẦN XÁC MINH — claim này chỉ được viết vào báo cáo sau systematic search.
> Nếu tìm thấy công trình đã làm, C3 phải diễn đạt lại thành "áp dụng vào cặp
> DataSEC–DataSED" chứ không phải "lần đầu".

---

## 4. Automated Audio Captioning và hallucination

| Chủ đề | Mức |
|---|---|
| AAC dạng free-form; dataset Clotho, AudioCaps | V1 |
| Metric n-gram: BLEU, METEOR, CIDEr, SPICE, SPIDEr | V1 |
| Metric ngữ nghĩa: FENSE và tương tự | V1 |
| **Hallucination trong AAC** | V1 |
| Event-conditioned / constrained generation | V1 |
| Đánh giá factual grounding thay vì tương đồng bề mặt | V1 |

### Khoảng trống đề tài nhắm tới — C1 và C2

Cần tìm xem đã có bộ metric nào đo **factual grounding của caption âm thanh so
với event timeline** (không cần reference prose) hay chưa.

Nếu đã có: C2 chuyển thành "áp dụng và mở rộng", và phải so sánh bộ metric của đề
tài với bộ đã có.

---

## 5. Audio retrieval và RAG

| Chủ đề | Mức |
|---|---|
| Text-to-audio retrieval | V1 |
| Retrieval trên metadata và event timeline | V1 |
| Hybrid structured + vector search | V1 |
| Embedding đa ngữ cho retrieval | V1 |
| Evidence-bound generation, unsupported claims | V1 |
| **Truy vấn quan hệ thời gian trên dữ liệu sự kiện** | V1 |

### Khoảng trống đề tài nhắm tới — C4

Cần tìm công trình về retrieval âm thanh có **temporal predicate** (A trước B)
chứ không chỉ tương đồng ngữ nghĩa. Quan hệ khoảng Allen là khái niệm có sẵn
trong CSDL thời gian; câu hỏi là đã ai áp vào event timeline âm thanh chưa.

---

## 6. Chuỗi đóng góp

```text
isolated classification transfer  (RQ1, C3 — có kiểm soát leakage)
  → polyphonic temporal detection (RQ1)
    → evidence-grounded caption   (RQ2, C1 + C2)
      → event-aware RAG retrieval (RQ3, C4)
```

Từng mắt đã có nghiên cứu riêng. Điểm đề tài đóng góp là **chuỗi liền mạch có
provenance xuyên suốt**: mọi câu trả lời cuối truy được về recording ID, time
span, model version, split hash và taxonomy hash.

> ⚠️ CẦN XÁC MINH — claim "chưa có công trình nào làm cả chuỗi này trên
> DataSEC/DataSED" chỉ được viết sau systematic search và bảng §8 điền đủ.

---

## 7. Kế hoạch systematic search

| Bước | Việc | Hạn |
|---:|---|---|
| 1 | Tìm paper kèm DataSEC/DataSED, nâng lên V3 | W1–W2 |
| 2 | Tìm baseline đã công bố trên hai dataset này | W2 |
| 3 | Search SED: DCASE proceedings, IEEE/ACM TASLP | W4 |
| 4 | Search AAC hallucination | W5 |
| 5 | Search audio retrieval + temporal predicate | W6 |
| 6 | Điền bảng §8, đối chiếu ba claim khoảng trống | W8 |

Từ khóa gợi ý: `polyphonic sound event detection`, `environmental noise dataset`,
`audio captioning hallucination`, `grounded audio captioning`,
`text-to-audio retrieval`, `cross-dataset duplicate leakage`,
`PSDS polyphonic sound detection score`, `hierarchical sound event classification`.

---

## 8. Bảng trích xuất tài liệu

Điền khi đạt V3. Một dòng cho mỗi paper.

| Paper | Năm | Task | Dataset | Labels | Model | Metric chính | Số báo | Dùng ở mục nào | Giới hạn | Mức |
|---|---|---|---|---|---|---|---|---|---|---|
| DataSEC (Zenodo) | 2025 | SEC | DataSEC | Clip-level, 2 cấp | — | — | — | §3 dữ liệu | Chưa xác minh có paper | V2 |
| DataSED (Zenodo) | 2025 | SED | DataSED | Strong | — | — | — | §3 dữ liệu | Chưa xác minh có paper | V2 |
| Fredianelli et al., *Scientific Data* | 2025 | Mô tả dataset SEC + SED | DataSEC, DataSED | Clip-level; strong mono/poly | — | — | Không có baseline (theo tóm tắt) | §1, §3 dữ liệu | Chưa đọc toàn văn; số giờ/file khác archive | V2 |
| Ebbers et al., Interspeech | 2024 | Hậu xử lý SED (cSEBB) | DCASE 2023 T4a (DESED) | Strong | 13 hệ DCASE 2023 + cSEBB | PSDS1, collar-F1 | +4.1 PSDS1 / +3.4 F1 trung bình so với median filter | ADR-0030, PAPER_NOTES S14 | Tune theo lớp trên validation | **V3** |
| Schmid et al., ICASSP | 2025 | Pretrain SED theo frame | AudioSet Strong; DESED | Strong (frame) | ATST-F, BEATs, fPaSST, M2D, ASiT | PSDS1 | AS-Strong 45.4–46.5; DESED fine-tune 47.6–49.2, frozen 45.4–49.2 | ADR-0030 §7, ADR-0031 §3, ADR-0032 | Đọc trực tiếp PDF v2 + code + LICENSE (26/09 tối) | **V3** |
| Kong et al., TASLP | 2020 | Tagging / pretraining | AudioSet | Weak | CNN14 | mAP | — | Encoder nhánh B/C | vol/pages chưa xác minh | V2 (kiến trúc V3) |
| DCASE 2016 T3 (kết quả) | 2016 | SED ghi âm thật | Dữ liệu DCASE 2016 T3 (home, residential area) | Strong | Baseline + hệ tham gia | Segment ER/F1 1 s; event onset-only 250 ms | Event-F1 4.7–6.3% (top 3 + baseline) | Bảng bối cảnh | Khác dataset, khác collar | V2 |
| Nam et al., FilterAugment, ICASSP | 2022 | Augmentation SED | DESED | Strong + weak | CRNN | PSDS | +6.50% so với +2.13% (frequency masking) | `augment.py` | Chỉ đọc abstract | V2 |
| ⚠️ CẦN XÁC MINH | | SED | | | | | | §2.1 | | V0 |
| ⚠️ CẦN XÁC MINH | | PSDS | | | | | | §2.2 | | V0 |
| ⚠️ CẦN XÁC MINH | | Transfer | | | | | | §2.3 | | V0 |
| ⚠️ CẦN XÁC MINH | | AAC hallucination | | | | | | §2.4 | | V0 |
| ⚠️ CẦN XÁC MINH | | Audio retrieval | | | | | | §2.5 | | V0 |

---

## 9. Ba claim phải chứng minh hoặc rút lại

| # | Claim | Trạng thái | Nếu sai thì |
|---:|---|---|---|
| 1 | Chưa có bộ metric đo factual grounding của caption âm thanh so với timeline | ⚠️ CẦN XÁC MINH | C2 đổi thành "áp dụng và mở rộng", phải so với bộ đã có |
| 2 | Nghiên cứu transfer thường không audit duplicate xuyên dataset | ⚠️ CẦN XÁC MINH | C3 đổi thành "áp dụng vào cặp DataSEC–DataSED" |
| 3 | Retrieval âm thanh thường không hỗ trợ temporal predicate | ⚠️ CẦN XÁC MINH | C4 đổi thành đóng góp kỹ thuật, không phải đóng góp khái niệm |

**Rút lại một claim không làm khóa luận yếu đi.** Giữ một claim sai thì có.

---

## 10. Nhật ký tra cứu

Ghi mọi lượt tra để phần văn liệu của báo cáo/paper tái lập được: ai tra, bằng gì, thấy gì.
Tra bằng `WebSearch`/`WebFetch` là **tóm tắt**, không phải đọc trực tiếp — chỉ nâng tới V2.

| Ngày | Công cụ | Truy vấn / URL | Kết quả chính | Mục |
|---|---|---|---|---|
| 26/09 | WebSearch | `DataSED dataset sound event detection environmental monitoring polyphonic annotations baseline` | Bài *Scientific Data* 2025 (Nature, PMC) | §1 |
| 26/09 | WebFetch | pmc.ncbi.nlm.nih.gov/articles/PMC12572321 | Tác giả, không baseline, thống kê monophonic | §1 |
| 26/09 | WebSearch | `Fredianelli "DataSED" sound event detection results CRNN F1 2026` | Không thấy bài báo baseline nào khác | §1 |
| 26/09 | WebSearch + WebFetch | arxiv.org/html/2409.09546v1, arxiv.org/abs/2409.09546, github.com/fschmid56/PretrainedSED (+ README, `inference.py`, `prediction_wrapper.py`, `Frame_MN_wrapper.py`) | PretrainedSED: số PSDS, checkpoint, frontend 16 kHz / 128 mel | §2.1 (2) |
| 26/09 | WebSearch + đọc PDF | isca-archive.org/interspeech_2024/ebbers24_interspeech.pdf (5 trang), github.com/merlresearch/sebbs (`csebbs.py`, `change_detection.pyx` qua tóm tắt) | cSEBB: thuật toán, lưới, +4.1/+3.4 điểm; license AGPL | §2.1 (1) |
| 26/09 | WebSearch | `DCASE 2024 task 4 sound event detection top systems …` | BEATs, ATST-Frame 40 ms, FDY conv | §2.1 (9) |
| 26/09 | WebFetch | dcase.community/challenge2016/task-sound-event-detection-in-real-life-audio(-results) | Metric chính segment ER 1 s; event collar 250 ms onset-only; bảng kết quả | §2.1 (4) |
| 26/09 | WebSearch + WebFetch | arxiv.org/abs/2110.03282 | FilterAugment: tác giả, ICASSP 2022, +6.50% vs +2.13% | §2.1 (5) |
| 26/09 | WebFetch | raw.githubusercontent.com/qiuqiangkong/audioset_tagging_cnn/master/pytorch/models.py | CNN14: pool (2,2) khối 1–5, (1,1) khối 6, dropout 0.2 | §2.1 (3) |
| 26/09 | WebFetch | arxiv.org/abs/1912.10211, arxiv.org/abs/1710.09412 | Metadata PANNs, mixup | §2.1 (3), (6) |
| 26/09 | WebSearch | `Turpault Serizel Shah Salamon "Sound event detection in domestic environments …"` | DESED, DCASE Workshop 2019 | §2.1 (7) |
| 26/09 | WebFetch | mdpi.com/2076-3417/6/6/162 | **403** — chưa xác minh DOI Mesaros 2016 | §2.1 (8) |
| 26/09 (tối) | curl + **đọc trực tiếp** | arxiv.org/pdf/2409.09546v2 (PDF 5 trang); raw README, LICENSE, `models/frame_mn/{Frame_MN_wrapper,model}.py`, `inference.py`, `models/prediction_wrapper.py`; API release v0.0.1 | PretrainedSED lên **V3**: Bảng I/II khớp; frozen gần bằng fine-tune; lr decay 0.5 (DESED); `frame_mn` không có trong bài; dòng "checkpoint cũ" của V2 sai phiên bản | §2.1 (2) |
| 27/09 (đêm) | curl + **đọc trực tiếp** (HTML → văn bản bằng code) | nature.com/articles/s41597-025-05991-w, pmc.ncbi.nlm.nih.gov/articles/PMC12572321 | Bài DataSED lên **V3**: không baseline (xác nhận); nguồn một phần từ Freesound + AudioSet, file bị cắt/trộn/thêm âm thanh tay; Bảng 3 tự mâu thuẫn; DataSEC trong bài là phiên bản cũ (4292 file) | §1 |
| 27/09 (đêm) | curl + **đọc trực tiếp** | dcase.community/challenge2016/task-sound-event-detection-in-real-life-audio(-results) | DCASE 2016 T3 lên **V3**: mọi số V2 khớp; thêm chi tiết dữ liệu (binaural, 3–5 phút, 4 fold) | §2.1 (4) |
| 27/09 (đêm) | curl | github.com/fschmid56/PretrainedSED `models/frame_mn/*`, `models/frame_passt/preprocess.py` @1aa47e48; release asset `frame_mn10_strong_1.pt` | Code frame_mn đọc trực tiếp cho T2b: 40 ms thật (stride thời gian ×4), 960 kênh; checkpoint 15,537,114 B | §2.1 (2), ADR-0032 §10 |
| 26/09 (tối) | GitHub API `/repos/*/license` + đọc LICENSE | microsoft/unilm, Audio-WestlakeU/audiossl, nttcslab/m2d, fschmid56/EfficientAT, kkoutini/PaSST, facebookresearch/deit | MIT / code MIT + checkpoint CC BY 4.0 / PDF riêng / MIT / Apache-2.0 / Apache-2.0 | §2.1 (2) |
