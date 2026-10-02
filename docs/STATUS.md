# STATUS.md — Trạng thái có bằng chứng

**Cập nhật:** 2026-10-02 — S8 phục vụ f2 và W7 7.4 đã kiểm chứng. S13 hoàn tất sớm theo cho phép của người dùng. Commit `c3f0033` khóa
f2 bằng CV dev annotated trước test; test annotated của 11 ứng viên đã báo, không chọn lại dù f1
có micro test cao hơn. RQ1-v2 3 B-v2 vs 3 C-v2 hoàn tất và âm tính về event-F1. Sổ test đã cập
nhật. Demo Compose phục vụ f2 theo ADR-0039; status báo `official=true`.
**Taxonomy:** `0.1` / `67ca8a8c…` · **Test:** 734 pass, 0 skip, 19 warnings; ruff sạch
(Windows, 29/09)

> Đây là nguồn chân lý về **phần đã chạy được**. Kiến trúc dự kiến nằm trong
> [SYSTEM.md](SYSTEM.md). Mọi dòng trong file này trỏ tới một artifact kiểm
> chứng được — số liệu chi tiết ở [measurements/](measurements/).

---

## 0. Tóm tắt

- **W1–W5 xong.** W6 có kết quả RQ3 (ADR-0027, duyệt 26/09). W7 chạy được đầu-cuối (ADR-0029,
  duyệt 26/09); từ 27/09 cả inference cũng chạy trong Docker (ADR-0033 §6) — demo trực tiếp bằng
  một lệnh `docker compose --profile app up -d`. Từ 28/09 profile demo dùng v2 qua env
  (ADR-0035), nhưng mặc định code và hệ thống chính thức vẫn v1 tới S8.
- **L2 parser câu hỏi xong 28/09 (ADR-0036), chỉ validation.** Qwen3.5-9B + JSON Schema sinh từ
  21 lớp/predicate: 240/240 output hợp schema; exact template 171/200 (0.855), paraphrase khóa
  trước 37/40 (0.925). RQ3 hybrid parsed 0.491 EN / 0.490 VI, Δ gold +0.012 / −0.002; Δ dương
  không phải cải thiện parser. API tự parse khi thiếu filter và trả lỗi rõ khi llama.cpp tắt.
- **Giai đoạn cải thiện SED (26/09, ADR-0030, duyệt 26/09).** Chẩn đoán trên dev: trần event-F1
  của kiến trúc v1 là 0.63 (pool thời gian /64); trần người 0.58; v1 chỉ onset 0.23, chỉ
  offset 0.50, segment F1 0.65 → lỗi nằm ở biên. Biên lệch **đối xứng, tản rộng** — giả thuyết
  "posterior bão hoà" bị đo bác bỏ ([boundary_errors_20260926.md](measurements/boundary_errors_20260926.md)).
  cSEBB thua θ global ở v1 (CV 0.058 so với 0.154) và ở mọi run v2.
- **SED v2 chốt 26/09 tối** (ADR-0030 §9). Cấu hình: pool /8, BiGRU 2×256, 30 epoch,
  augmentation, trần `pos_weight` 10.
  - Lựa chọn trên dev commit trước test (`ec71b20`): ensemble 3 seed, CV 0.2129 ± 0.0622.
  - Test một lần: event-F1 **micro 0.1476** [0.1088, 0.1866], **macro 0.1369**. Mốc v1 là
    0.0941 / 0.0917. Bootstrap ghép cặp v2 − v1 +0.0536 [+0.0261, +0.0853].
  - **PSDS không tăng** (PSDS-1 0.3447 so với 0.3489).
  - Ablation: độ phân giải thời gian là thành phần quyết định (−0.084 CV dev khi bỏ).
  - S9 (RQ1-v2) chạy từ 23:17.
- **Event-F1 headline trước 26/09 là micro** (lệch Q2, evaluation_protocol §3.2). Từ 26/09 con
  số chính là **macro**, micro kèm; chọn hệ thống vẫn bằng micro (ADR-0031 §1, PLAN nợ #20).
- **S13 đã khóa f2 trước test** (`c3f0033`): 11 ứng viên xếp theo CV annotated
  `f2/f4/g2/f1/d/g1/e/c/f3/b/a`. f2 đạt CV micro 0.2383±0.0562; test annotated macro 0.1206,
  micro 0.1643 [0.1103, 0.2242]. f1 có micro test cao nhất 0.1817 nhưng không chọn lại.
- **RQ1-v2 âm tính về event-F1:** C−B micro trung bình −0.0029, bootstrap theo recording
  [−0.0254, +0.0199]; Welch micro p=0.6965, macro p=0.4220. PSDS-2 tăng +0.0279, p=0.0193,
  nên kết luận phụ thuộc metric.
- **S11 focal (ADR-0038) âm tính với việc thay hệ thống:** pilot chọn γ=2.0; g1 focal T2b×3 đạt
  0.2268±0.0547 (θ) / 0.2265±0.0469 (cSEBB), g2 đạt 0.2319±0.0418 (cSEBB), thấp hơn f2
  0.2383±0.0562. Per-class dev ghi ở [s11_per_class_20260928](measurements/s11_per_class_20260928.md);
  không dùng test.
- **Mọi số SED đã tính lại** sau khi sửa lỗi ghép cửa sổ dự đoán (`7ada7d7`, `3208dbb`).
- **RQ1 âm tính (không đổi sau khi tính lại):** pretraining thêm trên DataSEC **không**
  cải thiện SED so với chỉ AudioSet (5 run/nhánh, không metric nào p < 0.05).
  Pretraining nói chung giúp rõ.
- **Event-F1 thấp (~0.06)** chủ yếu do định vị thời gian thô; nới collar 0.2 → 1.0 s
  tăng ~3×.
- **Caption (RQ2):** khi chỉ nhận timeline, LLM gần như không bịa nguồn âm; lỗi của
  sinh tự do nằm ở suy diễn bối cảnh, gọi tên quá cụ thể, từ cấm G3 (ADR-0022 §5). Có CI
  bootstrap + hiệu số cặp; constrained đổi lại omission e2e +0.224 [+0.178, +0.274]; nhánh
  cover (ADR-0026) buộc phủ lớp → không thua unconstrained ở metric nào (caption gần template).
  Lexicon kiểm bằng người đọc mù 60 caption: precision 0.896, recall 0.936 (ADR-0022 §6).
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
| 4.6 `confusable_with` / 4.7 A4 | ✅ | taxonomy.md §8.1, ADR-0028 |
| Chẩn đoán trần SED (độ phân giải, người, onset/offset) | ✅ dev + ground truth | [sed_ceilings_20260926.md](measurements/sed_ceilings_20260926.md) |
| Hậu xử lý cSEBB (Ebbers 2024) | ✅ cài + CV dev; **âm tính** trên v1 (0.0582 vs 0.1538) | [sebb_cv_…_20260926.md](measurements/sebb_cv_sed_ensemble_C_clean_20260925T045631Z_20260926.md) |
| SED v2 (ADR-0030) | ✅ chốt 26/09 tối: ensemble 3 seed chọn trên dev (`ec71b20`); test micro 0.1476, macro 0.1369, PSDS-1 0.3447, PSDS-2 0.6744; v2 − v1 +0.0536 [+0.0261, +0.0853] | [sed_v2_selection_20260926.md](measurements/sed_v2_selection_20260926.md), [sed_ensemble_v2_20260926T155630Z_eval_cv.md](measurements/sed_ensemble_v2_20260926T155630Z_eval_cv.md), [sed_v2_ablation_20260926.md](measurements/sed_v2_ablation_20260926.md), ADR-0030 §9 |
| RQ1-v2 (S9) / Track 2 (S10) / S11 / S13 | ✅ Hoàn tất. f2 được khóa bằng CV trước test; test macro/micro 0.1206/0.1643. Không chọn lại dù f1 có micro test 0.1817. RQ1-v2 C−B micro −0.0029 [−0.0254, +0.0199], âm tính về event-F1. | [s13_selection_20261018.md](measurements/s13_selection_20261018.md), [s13_test_20261018.md](measurements/s13_test_20261018.md), [rq1_v2_multiseed_20260929.md](measurements/rq1_v2_multiseed_20260929.md), ADR-0031 §9, [PAPER_NOTES S40–S41](PAPER_NOTES.md) |
| Caption có căn cứ (W5) | ✅ RQ2: template / constrained / unconstrained × oracle / e2e chấm trên test; ràng buộc đưa bối cảnh/G3/gọi tên quá mức về 0, đổi lại omission e2e 6% → 28% | [caption_grounding_*_test.md](measurements/), ADR-0022/0023 |
| Caption cover + SED tối ưu (W5 cải thiện) | ✅ cover: omission 0 test; trên ensemble C omission constrained 0.284 → 0.036 | ADR-0026, `caption_grounding_sed_ensemble_C_*` |
| Kiểm lexicon C2 bằng người | ✅ 60 caption, precision 0.896 / recall 0.936, lexicon dễ dãi hơn người | [caption_mention_agreement_20260925.md](measurements/caption_mention_agreement_20260925.md) |
| Caption tiếng Việt (giao diện) | ✅ template VI, 0 vi phạm G1–G3 trên timeline thật; cụm từ duyệt tạm 26/09 | [caption_vi_template_*.md](measurements/), ADR-0025 |
| Event store + RAG (W6) | ◐ dev+test nạp vào PostgreSQL + pgvector, BGE-M3, benchmark RQ3 (test nDCG@10: structured 0.523, hybrid 0.481, vector 0.418; filter exactness 1.000); câu trả lời ràng buộc evidence: unsupported-claim 0.000 | ADR-0027, [retrieval_benchmark_test_20260925.md](measurements/retrieval_benchmark_test_20260925.md) |
| Parser câu hỏi → filter (L2) | ✅ constrained hợp schema 240/240; exact template 0.855, paraphrase 0.925; RQ3 parsed chỉ validation, hybrid Δ gold +0.012 EN / −0.002 VI | ADR-0036, [query_parser_20260928.md](measurements/query_parser_20260928.md), [retrieval_benchmark_validation_parsed_20260928.md](measurements/retrieval_benchmark_validation_parsed_20260928.md) |
| API / inference / frontend (W7) | ◐ 7.1–7.4 xong trên f2; UI natural search/chip/manual fallback, model badge, timeline/evidence playback và phrasing review đã triển khai; Compose healthy, status `official=true`; parity f2 CUDA 299/299 event trùng khít, CPU 294/299 trong collar; E2E TRAIN S-0016 có timeline, caption EN/VI và RAG. 7.5–7.7 còn lại | ADR-0029, ADR-0033 §6, ADR-0039, ADR-0037, [DEMO.md](DEMO.md), [inference_parity_20260929.md](measurements/inference_parity_20260929.md), [inference_parity_cpu_20261002.md](measurements/inference_parity_cpu_20261002.md), [demo_f2_e2e_20261002.md](measurements/demo_f2_e2e_20261002.md) |
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
Định vị thời gian là nút thắt lớn. CNN14 ở 100 fps quyết định theo khối ≈ 0.64 s (1000 frame →
15 khối). ADR-0014 tính 1.28 s cho 50 fps; ghi "~1.28 s" trước đây là sai với nhánh PANNs.
Trần của khối 0.64 s là 0.63 ngay cả với model hoàn hảo
([sed_ceilings_20260926.md](measurements/sed_ceilings_20260926.md)). Ở collar 2 s vẫn
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

1. ~~W4: 4.6, 4.7, bootstrap CI cho số trung bình nhiều run~~ — xong 26/09.
2. ~~W5: kiểm caption lớp gộp theo taxonomy.md §7~~ — xong 25/09 (ADR-0023 §5).
3. ~~W6: nạp event vào pgvector, embedding BGE-M3, retrieval + benchmark~~ — có kết quả
   (ADR-0027, duyệt 26/09).
4. W7: ~~7.4 inference image~~ — xong 27/09 (ADR-0033 §6); 7.5–7.7 làm 19/10–02/11, sau S8
   (ADR-0031 §7).
5. ~~Cân nhắc chọn lại `g_max` percentile trên dev (A5)~~ — xong 25/09 (ADR-0024).
6. ~~SED v2 (ADR-0030): CV + ablation trên dev → commit lựa chọn → test một lần~~ — xong 26/09 tối.
   Chạy lại W5 e2e / W6 (S8) **một lần sau mốc 18/10**, trên hệ thống thắng vòng chọn cuối.
7. Event-F1 macro cho mọi hệ thống đã báo (PLAN nợ #20) — v1 xong (`event_f1_macro_20260926.md`),
   v2 sinh sau hàng đợi.
8. **Lộ trình ADR-0031:** S9–S13 hoàn tất sớm 29/09 theo cho phép của người dùng. f2 là hệ thống
   SED cuối đã khóa; S8 chạy một lần trên f2 để cập nhật caption/RQ3/phục vụ.
   L2 bộ lọc từ câu hỏi đã xong sớm 28/09; sau mốc còn viết báo cáo (L3).
