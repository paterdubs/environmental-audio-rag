# STATUS.md — Trạng thái có bằng chứng

**Cập nhật:** 2026-09-25 tối — tối ưu SED không train lại xong (ADR-0024); trước đó sửa lỗi ghép cửa sổ (`7ada7d7`), tính lại 11 run
**Taxonomy:** `0.1` / `67ca8a8c…` · **Test:** 486 pass (Windows), ruff sạch; CI Linux chạy lại khi push

> Đây là nguồn chân lý về **phần đã chạy được**. Kiến trúc dự kiến nằm trong
> [SYSTEM.md](SYSTEM.md). Mọi dòng trong file này trỏ tới một artifact kiểm
> chứng được — số liệu chi tiết ở [measurements/](measurements/).

---

## 0. Tóm tắt

- **W1–W3 xong, W4 gần xong** (thiếu 4.6, 4.7; 4.9 tối ưu SED xong). **W5 xong**
  (RQ2 trên test + diễn đạt lớp gộp §7). W6 có nền tảng, chưa có kết quả.
- **Mọi số SED đã tính lại** sau khi sửa lỗi ghép cửa sổ dự đoán (`7ada7d7`, `3208dbb`).
- **RQ1 âm tính (không đổi sau khi tính lại):** pretraining thêm trên DataSEC **không**
  cải thiện SED so với chỉ AudioSet (5 run/nhánh, không metric nào p < 0.05).
  Pretraining nói chung giúp rõ.
- **Event-F1 thấp (~0.06)** chủ yếu do định vị thời gian thô; nới collar 0.2 → 1.0 s
  tăng ~3×.
- **Caption (RQ2):** khi chỉ nhận timeline, LLM gần như không bịa nguồn âm; lỗi của
  sinh tự do nằm ở suy diễn bối cảnh, gọi tên quá cụ thể, từ cấm G3 (ADR-0022 §5).
- **Train SED không tất định cùng seed** → mọi số SED báo mean ± sd nhiều run.
- **Tối ưu SED không train lại (ADR-0024):** hậu xử lý chọn bằng CV trên dev (θ global
  0.95, `g_max` p25) nâng event-F1 test ở 5/5 ứng viên (+0.030 … +0.043); hệ thống chọn
  theo luật ghi trước = ensemble C: event-F1 **0.0941**, PSDS-1 0.3489, PSDS-2 0.6987.

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
| Tối ưu SED: ensemble + hậu xử lý chọn trên dev (4.9) | ✅ 5 ứng viên, chọn trên dev, test một lần | xem §2.5, [ADR-0024](decisions/ADR-0024-toi-uu-sed-ensemble-va-chon-hau-xu-ly-tren-dev.md) |
| Phân tích theo lớp / độ dài / collar | ✅ | xem §2 |
| 4.6 `confusable_with` từ ma trận nhầm thật | ○ | — |
| 4.7 Ablation A4 `pos_weight` | ○ | — |
| Caption có căn cứ (W5) | ✅ RQ2: template / constrained / unconstrained × oracle / e2e chấm trên test; ràng buộc đưa bối cảnh/G3/gọi tên quá mức về 0, đổi lại omission e2e 6% → 28% | [caption_grounding_*_test.md](measurements/), ADR-0022/0023 |
| Caption tiếng Việt (giao diện) | ✅ template VI, 0 vi phạm G1–G3 trên timeline thật; cụm từ chờ duyệt | [caption_vi_template_*.md](measurements/), ADR-0025 |
| Event store + RAG (W6) | ◐ PostgreSQL + pgvector chạy (Docker); chưa nạp dữ liệu, chưa embedding | `docker-compose.yml`, `db/migrations/` |
| API / frontend (W7) | ○ | — |
| CI | ✅ xanh trên GitHub Actions (Linux, Python 3.12) — lần đầu đỏ vì kiểm đường dẫn phụ thuộc hệ điều hành, đã sửa (`de4acc1`) | [https://github.com/paterdubs/environmental-audio-rag/actions](https://github.com/paterdubs/environmental-audio-rag/actions) |

---

## 2. Kết quả SED

### 2.1 Run chính thức (tree sạch, 1 run/nhánh)

| Metric (test, 142 recording) | A · scratch | B · AudioSet | C · AudioSet→DataSEC |
|---|---:|---:|---:|
| event-based F1 (collar 0.2 s) | 0.0360 | 0.0621 | 0.0472 |
| PSDS-1 | 0.2059 | 0.2818 | 0.2873 |
| PSDS-2 | 0.4514 | 0.6456 | 0.6462 |

Run: A `sed_polyphonic_20260923T173234Z`, B `…20260924T054531Z`, C `…20260924T061000Z`.

### 2.2 RQ1 trên nhiều run — kết luận chính thức ([ADR-0021](decisions/ADR-0021-rq1-ket-qua-am-tinh.md))

| Metric | Chính: 7 run sạch (B n=3, C n=4) | Độ nhạy: 10 run (n=5/5) |
|---|---|---|
| event-based F1 | B 0.0610±0.0048 · C 0.0539±0.0088 · p=0.234 | p=0.124 |
| PSDS-1 | B 0.2902±0.0093 · C 0.2892±0.0139 · p=0.913 | p=0.313 |
| PSDS-2 | B 0.6498±0.0037 · C 0.6591±0.0107 · p=0.181 | p=0.772 |

Welch t-test hai phía. 3/10 run có `git.dirty=true` (B `015736Z`, `031616Z`; C
`021958Z`) nên phân tích chính loại chúng. Nguồn:
[rq1_multiseed_clean_20260924.md](measurements/rq1_multiseed_clean_20260924.md),
[rq1_multiseed_20260924.md](measurements/rq1_multiseed_20260924.md).

> ⚠️ [seed_variance_vs_rq1_delta.md](measurements/seed_variance_vs_rq1_delta.md) (2 run/nhánh)
> kết luận event-F1 "vượt nhiễu 8.2×" — **đã bị bác bỏ** bởi dữ liệu 5 run.

### 2.3 Chẩn đoán vì sao event-F1 thấp

| Collar onset | 0.2 s (protocol) | 0.5 s | 1.0 s | 2.0 s |
|---|---:|---:|---:|---:|
| B run chính thức | 0.062 | 0.132 | 0.185 | 0.222 |
| C run chính thức | 0.047 | 0.112 | 0.181 | 0.202 |

Chẩn đoán, không phải số chính thức ([collar_sensitivity_20260924.md](measurements/collar_sensitivity_20260924.md)).
Định vị thời gian là nút thắt lớn (CNN14 ~1.28 s/khối, ADR-0014); ở collar 2 s vẫn
~0.2 → còn lỗi nhận dạng lớp (nhầm lớp là loại lỗi nhiều nhất). Recall thấp ở mọi
bin độ dài ([rq1_duration_polyphony_20260924.md](measurements/rq1_duration_polyphony_20260924.md);
chỉ cột recall hợp lệ). Theo lớp: kết quả trộn, không lớp nào đủ tin cậy sau so sánh
bội ([branch_per_class_clean_20260924.md](measurements/branch_per_class_clean_20260924.md)).

### 2.4 Tính tái lập

Train SED **không tất định** cùng seed và cùng code (frame macro-F1 B 0.5850 →
0.5705). Classifier DataSEC tái lập bit-for-bit. Nguyên nhân chưa xác minh.

### 2.5 Tối ưu không train lại ([ADR-0024](decisions/ADR-0024-toi-uu-sed-ensemble-va-chon-hau-xu-ly-tren-dev.md))

Ensemble (trung bình xác suất các run sạch) + chọn kiểu θ / percentile `g_max` bằng CV
5 fold trên **dev**; hệ thống chọn theo luật ghi và commit **trước** test (`0387225`).
Cả 5 ứng viên chọn θ global 0.95 + `g_max` p25. Test, event-F1 mặc định → CV:

| Ứng viên | CV dev | event-F1 test [95% CI] | PSDS-1 | PSDS-2 |
|---|---:|---|---:|---:|
| **ensemble C (chọn)** | 0.1538 | 0.0636 → **0.0941** [0.0624, 0.1277] | 0.3489 | 0.6987 |
| ensemble B | 0.1334 | 0.0553 → 0.0969 | 0.3174 | 0.6800 |
| ensemble BC | 0.1236 | 0.0696 → 0.1001 | 0.3402 | 0.7074 |
| run đơn B `054531Z` | 0.1259 | 0.0621 → 0.1048 | 0.2934 | 0.6312 |
| run đơn C `061000Z` | 0.1198 | 0.0472 → 0.0801 | 0.3150 | 0.6324 |

PSDS ở cột phải là với hậu xử lý CV. Hậu xử lý chọn trên dev tăng event-F1, precision,
recall và PSDS-1 ở 5/5; PSDS-2 giảm nhẹ 5/5. Hệ thống được chọn không cao nhất trên test
nhưng CI mọi ứng viên chồng lấn — không chọn lại. Deletion thành lỗi chính (dự đoán
408/740 event). Nguồn: [sed_optimization_20260925.md](measurements/sed_optimization_20260925.md).

---

## 3. Ablation hậu xử lý (A/B/C)

| Ablation | Kết quả | Kết luận |
|---|---|---|
| A2 · θ per-class vs global | Per-class dev→test −48% / −39% / −41%; global −15% / −4% / −2%. Trên **test**, global cao hơn per-class ở cả 3 nhánh (vd. B 0.079 vs 0.062) | Overfit dev có hệ thống — vào Hạn chế; không đổi θ theo test |
| A3 · median filter | Δ +0.0063 / +0.0026 / −0.0014 | Không tác động rõ |
| A5 · percentile duration prior | `g_max` percentile 25 tốt hơn cả 3 nhánh (+0.005/+0.015/+0.005); 75 tệ hơn cả 3 | Đã chọn lại trên **dev** (ADR-0024): cả 5 ứng viên chọn p25; ADR-0003 giữ cho số RQ1 |

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
2. ~~W5: kiểm caption lớp gộp theo taxonomy.md §7~~ — xong 25/09 (ADR-0023 §5); W6 là việc chính tiếp theo.
3. W6: nạp event vào pgvector, embedding BGE-M3, retrieval + benchmark.
4. W7: API, giao diện.
5. ~~Cân nhắc chọn lại `g_max` percentile trên dev (A5)~~ — xong 25/09 (ADR-0024).
