# PLAN.md — Roadmap

Mỗi milestone chỉ hoàn tất khi đạt exit criteria và cập nhật `STATUS.md`.

## M0 — Foundation

- [x] Chốt scope DataSEC + DataSED.
- [x] Dựng repository scaffold.
- [x] Viết kiến trúc, taxonomy, data plan và evaluation protocol bản đầu.
- [ ] Kiểm toàn bộ link nội bộ.
- [ ] Khởi tạo Git và baseline CI.

**Exit:** cấu trúc độc lập, tài liệu nhất quán, không chứa code/data từ dự án cũ.

## M1 — Data acquisition và audit

- [ ] Tải LICENSE, README, metadata trước audio.
- [ ] Freeze record/version DOI và SHA-256.
- [ ] Tải archive vào `data/raw/`.
- [ ] Xác thực số file, duration, sample rate, channel và label schema.
- [ ] Tạo acoustic/content fingerprints.
- [ ] Báo cáo duplicate nội bộ và xuyên dataset.
- [ ] Canonicalize label nhưng giữ raw label.

**Exit:** manifest tái lập được; mọi file hợp lệ hoặc có exclusion reason.

## M2 — Split và data loaders

- [ ] Freeze DataSEC train/dev/test theo content group.
- [ ] Freeze DataSED train/dev/test theo recording group và iterative multilabel stratification.
- [ ] Implement classification dataset.
- [ ] Implement strong-label SED dataset.
- [ ] Test frame alignment và padding/masking.

**Exit:** loader deterministic; không duplicate group xuyên split.

## M3 — Baselines

- [ ] DataSEC classifier baseline.
- [ ] DataSED SED baseline không pretraining DataSEC.
- [ ] SED baseline có pretraining DataSEC.
- [ ] Threshold sweep chỉ trên dev.
- [ ] Per-class error analysis.

**Exit:** có bảng baseline tái lập cùng run manifests.

## M4 — Proposed hierarchical SED

- [ ] Chọn encoder qua ablation có giới hạn.
- [ ] Thiết kế transfer DataSEC → DataSED.
- [ ] Thử coarse SED + subclass refinement.
- [ ] Đánh giá calibration và domain mismatch.

**Exit:** mô hình đề xuất hơn baseline trên metric chính hoặc chỉ ra trade-off có bằng chứng.

## M5 — Grounded caption

- [ ] Timeline canonicalization.
- [ ] Caption template baseline.
- [ ] Constrained caption model nếu còn ngân sách.
- [ ] Event hallucination, omission và temporal-order evaluation.

**Exit:** caption không thêm event ngoài timeline theo contract; có metric dev/test.

## M6 — RAG và ứng dụng

- [ ] Event store cùng metadata filters.
- [ ] Embedding index cho caption/event summary.
- [ ] Hybrid retrieval và evidence-bound answer.
- [ ] API, inference service và frontend.
- [ ] Retrieval benchmark.

**Exit:** demo upload → timeline → caption → truy vấn; câu trả lời dẫn recording/time span.

## M7 — Final evaluation

- [ ] Chạy test một lần bằng config đóng băng.
- [ ] Ablation DataSEC pretraining, grounding và hybrid retrieval.
- [ ] Báo cáo failure cases và giới hạn miền dữ liệu.
- [ ] Đóng băng artifact, commit và hướng dẫn tái lập.

