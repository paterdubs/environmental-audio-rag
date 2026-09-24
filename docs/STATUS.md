# STATUS.md — Trạng thái có bằng chứng

**Cập nhật:** 2026-09-24, sau khi chốt RQ1 (ADR-0021)
**Taxonomy:** `0.1` / `67ca8a8c…` · **Test:** 376 pass (Windows), 355 pass (Linux CI), ruff sạch

> Đây là nguồn chân lý về **phần đã chạy được**. Kiến trúc dự kiến nằm trong
> [SYSTEM.md](SYSTEM.md). Mọi dòng trong file này trỏ tới một artifact kiểm
> chứng được — số liệu chi tiết ở [measurements/](measurements/).

---

## 0. Tóm tắt

- **W1–W3 xong, W4 gần xong** (thiếu 4.6, 4.7). W5/W6 có nền tảng, chưa có kết quả.
- **RQ1 âm tính:** pretraining thêm trên DataSEC **không** cải thiện SED so với chỉ
  AudioSet (5 run/nhánh, không metric nào p < 0.05). Pretraining nói chung giúp rõ.
- **Event-F1 thấp (~0.05)** chủ yếu do định vị thời gian thô; nới collar 0.2 → 1.0 s
  tăng ~3×.
- **Train SED không tất định cùng seed** → mọi số SED báo mean ± sd nhiều run.

---

## 1. Snapshot

| Thành phần | Trạng thái | Bằng chứng |
|---|---|---|
| Archive DataSEC / DataSED | ✅ MD5 khớp, `pass` | [archive_audit_20260922.md](measurements/archive_audit_20260922.md) |
| Taxonomy xác minh từ archive | ✅ 22/22 coarse, 28 subclass, 0 unmapped | cùng trên |
| Dedup T1/T2/T3, nội bộ + xuyên dataset (D3) | ✅ 3 cặp trùng xuyên dataset xác nhận | [dedup_20260923.md](measurements/dedup_20260923.md) |
| Duyệt tay 35 cặp nghi vấn | ✅ 10 duplicate · 1 unsure · 24 distinct | [review_worksheet_20260923.md](measurements/review_worksheet_20260923.md) |
| Rò rỉ xuyên dataset | ✅ 11 clip = 0.2179% → dải `minor` | `data/manifests/exclusions.csv` |
| Split DataSED (D4) | ✅ đóng băng 438/137/142, tag `data-v1.0` | `data/splits/datased_polyphonic.frozen.json` |
| Split DataSEC | ✅ đóng băng 3,434/744/740 | `data/splits/datasec_classification.frozen.json` |
| Đặc trưng `logmel_v1`, `logmel_panns_v1` | ✅ 717 + 5,048 file | `data/manifests/*_logmel_*.csv` |
| Checkpoint AudioSet CNN14 | ✅ SHA-256 xác minh, 92.23% tham số transplant | [panns_checkpoint_20260923.md](measurements/panns_checkpoint_20260923.md) |
| Classifier DataSEC (D1) | ✅ coarse macro-F1 test **0.8467**, tái lập bit-for-bit (D2) | [per_class_metrics_datasec_20260923.md](measurements/per_class_metrics_datasec_20260923.md) |
| SED ba nhánh A/B/C | ✅ 1 + 5 + 5 run | xem §2 |
| Hậu xử lý + event-F1 + PSDS + bootstrap | ✅ chạy thật trên mọi run | `ml/runs/*/evaluation.json`, `*_eval.md` |
| Ablation A2, A3, A5 (hậu xử lý) | ✅ trên cả A/B/C | xem §3 |
| Phân tích theo lớp / độ dài / collar | ✅ | xem §2 |
| 4.6 `confusable_with` từ ma trận nhầm thật | ○ | — |
| 4.7 Ablation A4 `pos_weight` | ○ | — |
| Caption có căn cứ (W5) | ◐ template + metric G1–G3 verify trên 426 recording thật; chưa có nhánh LLM đối chứng | [*_caption_wiring_test.md](measurements/) |
| Event store + RAG (W6) | ◐ PostgreSQL + pgvector chạy (Docker); chưa nạp dữ liệu, chưa embedding | `docker-compose.yml`, `db/migrations/` |
| API / frontend (W7) | ○ | — |
| CI | ✅ xanh trên GitHub Actions (Linux, Python 3.12) — lần đầu đỏ vì kiểm đường dẫn phụ thuộc hệ điều hành, đã sửa (`de4acc1`) | [https://github.com/paterdubs/environmental-audio-rag/actions](https://github.com/paterdubs/environmental-audio-rag/actions) |

---

## 2. Kết quả SED

### 2.1 Run chính thức (tree sạch, 1 run/nhánh)

| Metric (test, 142 recording) | A · scratch | B · AudioSet | C · AudioSet→DataSEC |
|---|---:|---:|---:|
| event-based F1 (collar 0.2 s) | 0.0220 | 0.0569 | 0.0396 |
| PSDS-1 | 0.1820 | 0.2444 | 0.2533 |
| PSDS-2 | 0.4475 | 0.6442 | 0.6384 |

Run: A `sed_polyphonic_20260923T173234Z`, B `…20260924T054531Z`, C `…20260924T061000Z`.

### 2.2 RQ1 trên nhiều run — kết luận chính thức ([ADR-0021](decisions/ADR-0021-rq1-ket-qua-am-tinh.md))

| Metric | Chính: 7 run sạch (B n=3, C n=4) | Độ nhạy: 10 run (n=5/5) |
|---|---|---|
| event-based F1 | B 0.0526±0.0038 · C 0.0494±0.0070 · p=0.479 | p=0.917 |
| PSDS-1 | B 0.2513±0.0077 · C 0.2541±0.0152 · p=0.767 | p=0.268 |
| PSDS-2 | B 0.6443±0.0035 · C 0.6497±0.0113 · p=0.425 | p=0.718 |

Welch t-test hai phía. 3/10 run có `git.dirty=true` (B `015736Z`, `031616Z`; C
`021958Z`) nên phân tích chính loại chúng. Nguồn:
[rq1_multiseed_clean_20260924.md](measurements/rq1_multiseed_clean_20260924.md),
[rq1_multiseed_20260924.md](measurements/rq1_multiseed_20260924.md).

> ⚠️ [seed_variance_vs_rq1_delta.md](measurements/seed_variance_vs_rq1_delta.md) (2 run/nhánh)
> kết luận event-F1 "vượt nhiễu 8.2×" — **đã bị bác bỏ** bởi dữ liệu 5 run.

### 2.3 Chẩn đoán vì sao event-F1 thấp

| Collar onset | 0.2 s (protocol) | 0.5 s | 1.0 s | 2.0 s |
|---|---:|---:|---:|---:|
| B run chính thức | 0.057 | 0.115 | 0.168 | 0.204 |
| C run chính thức | 0.040 | 0.093 | 0.149 | 0.163 |

Chẩn đoán, không phải số chính thức ([collar_sensitivity_20260924.md](measurements/collar_sensitivity_20260924.md)).
Định vị thời gian là nút thắt lớn (CNN14 ~1.28 s/khối, ADR-0014); ở collar 2 s vẫn
~0.2 → còn lỗi nhận dạng lớp (nhầm lớp là loại lỗi nhiều nhất). Recall thấp ở mọi
bin độ dài ([rq1_duration_polyphony_20260924.md](measurements/rq1_duration_polyphony_20260924.md);
chỉ cột recall hợp lệ). Theo lớp: kết quả trộn, không lớp nào đủ tin cậy sau so sánh
bội ([branch_per_class_clean_20260924.md](measurements/branch_per_class_clean_20260924.md)).

### 2.4 Tính tái lập

Train SED **không tất định** cùng seed và cùng code (frame macro-F1 B 0.5850 →
0.5705). Classifier DataSEC tái lập bit-for-bit. Nguyên nhân chưa xác minh.

---

## 3. Ablation hậu xử lý (A/B/C)

| Ablation | Kết quả | Kết luận |
|---|---|---|
| A2 · θ per-class vs global | Per-class dev→test −66% / −39% / −29%; global ổn định | Overfit dev có hệ thống — vào Hạn chế |
| A3 · median filter | Δ +0.0025 / +0.0035 / −0.0015 | Không tác động rõ |
| A5 · percentile duration prior | `g_max` percentile 25 tốt hơn cả 3 nhánh; 75 tệ hơn cả 3 | Ứng viên chọn lại trên **dev**; ADR-0003 chưa đổi |

---

## 4. Dữ liệu

| | DataSEC | DataSED |
|---|---|---|
| Nội dung | 5,048 clip · 23.7082 h · 44.1 kHz mono | 717 recording · 18.6847 h · 44.1 kHz |
| Nhãn | 22 coarse + 28 subclass (cây thư mục) | 4,034 event polyphonic / 21 lớp, có onset/offset |
| Split | 3,434 / 744 / 740 (130 clip bị loại) | 438 / 137 / 142 |
| License | CC-BY-NC-SA-4.0 | CC-BY-NC-SA-4.0 |

Chi tiết theo lớp: [data_inventory.md](data_inventory.md).

---

## 5. Việc còn lại

1. W4: 4.6 (`confusable_with`), 4.7 (A4 `pos_weight`), bootstrap CI cho số trung bình nhiều run.
2. W5: nhánh caption không ràng buộc (cần chọn LLM), nhánh ràng buộc, đánh giá oracle + end-to-end.
3. W6: nạp event vào pgvector, embedding BGE-M3, retrieval + benchmark.
4. W7: API, giao diện.
5. Cân nhắc chọn lại `g_max` percentile trên dev (A5).
