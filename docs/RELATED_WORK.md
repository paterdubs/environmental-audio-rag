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

### Còn phải làm

- [x] Tìm paper kèm dataset — **đã kiểm tra record DataSEC (Zenodo 17033970,
      v3), không có publication/venue nào được liệt kê**, không có "related
      identifiers"/"cited by". ⚠️ Đây là kết quả từ tóm tắt `WebFetch` (mô hình
      nhỏ đọc trang), **không phải đọc trực tiếp HTML** — theo đúng bài học đã
      rút ra ở ADR-0015 (tóm tắt WebSearch từng báo sai license), kết quả này
      cần một người **mở trực tiếp trang Zenodo xác nhận lại** trước khi coi là
      chốt. Chưa kiểm DataSED (15346092).
- [ ] ⚠️ **Chênh lệch cần đối chiếu:** tóm tắt trên báo record DataSEC ghi
      "4,292 mẫu, 18h26" — khác với `datasec_archive_audit.json` đã đo trực
      tiếp từ archive (**5,048 file, 23.7082 h**). Nhiều khả năng tóm tắt đọc
      nhầm phiên bản cũ hơn v3, hoặc lẫn với một con số khác trên trang. **Không
      dùng số 4,292/18h26 ở bất kỳ đâu** cho tới khi có người xác nhận trực
      tiếp trên trang Zenodo. Theo nguyên tắc đã ghi ở dòng dưới: archive là sự
      thật, trang mô tả thì không.
- [ ] Đối chiếu số file và số giờ trong paper với archive thật.
      **Archive là sự thật kiểm chứng được; paper thì không.** Chênh lệch phải ghi,
      không ép số theo paper.
- [ ] Xác minh có paper nào đã công bố baseline trên hai dataset này chưa. Nếu có,
      đó là baseline để so sánh trực tiếp → nâng lên V4.
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
| Pretrained audio transformer (AST, PaSST, BEATs) | V1 | Xem [ADR-0002](decisions/ADR-0002-encoder-va-nhanh-transfer.md) về lý do không chọn |
| PANNs / AudioSet pretraining | V1 | Encoder đề xuất |
| Threshold calibration và hậu xử lý | V1 | Xem [ADR-0003](decisions/ADR-0003-threshold-va-post-processing.md) |
| Event-based F1 và collar | V1 | `sed_eval` |
| **PSDS** và ba tiêu chí DTC/GTC/CTTC | V1 | `psds_eval`; tham số ở [evaluation_protocol §3.3](evaluation_protocol.md) |
| DCASE task SED — giao thức và baseline | V1 | Nguồn của quy ước collar 0.2 s |

### Câu hỏi cần văn liệu trả lời

1. Giá trị collar và segment length nào là quy ước chuẩn để kết quả so được?
2. Hai scenario PSDS nào được dùng phổ biến nhất, với tham số nào?
3. Median filter và event tối thiểu thường suy từ đâu — train hay dev?
   (Đề tài chọn train, [ADR-0003](decisions/ADR-0003-threshold-va-post-processing.md);
   cần đối chiếu với thực hành phổ biến.)

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
