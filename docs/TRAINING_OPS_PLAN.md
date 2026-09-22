# TRAINING_OPS_PLAN.md — Vận hành huấn luyện

## 1. Mục tiêu

Mọi experiment chạy được từ config, tạo run directory tự đủ bằng chứng và có thể resume an toàn.

## 2. Run layout dự kiến

```text
ml/runs/<run_id>/
├── manifest.json
├── config.resolved.yaml
├── taxonomy.snapshot.yaml
├── checkpoints/
├── predictions/
├── metrics.json
└── logs/
```

Run artifact bị ignore; report nhỏ được sinh sang `docs/measurements/`.

## 3. Manifest bắt buộc

- Run ID và UTC timestamp.
- Git revision và dirty flag.
- Command line.
- Resolved config.
- Seed.
- Data manifest/split/taxonomy hashes.
- Package and hardware summary.
- Checkpoint selection rule.
- Primary metric và final value.

## 4. Training stages

### T1 — DataSEC classifier

Mục tiêu: baseline 22-class coarse và optional hierarchical head.

### T2 — DataSED SED from scratch/pretrained generic encoder

Mục tiêu: baseline độc lập DataSEC.

### T3 — DataSEC → DataSED transfer

Mục tiêu: đo tác động pretraining trong cùng training budget.

### T4 — Calibration và post-processing

Chỉ dùng dev; config sau chọn được đóng băng trước test.

### T5 — Caption và retrieval

Dùng frozen SED predictions để tránh thay model ngầm giữa các thí nghiệm downstream.

## 5. Resource policy

- Chạy smoke test trên subset trước full run.
- Fail nếu disk estimate vượt quota.
- Không giữ checkpoint mỗi epoch; giữ `last` và checkpoint theo rule định trước.
- Prediction test chỉ tạo sau khi chọn model.
- Không chạy sweep không có hypothesis và budget cap.

## 6. Recovery

- Resume phải kiểm config và data hashes khớp.
- Run bị ngắt không được ghi `complete=true`.
- Artifact thiếu manifest được xem là không hợp lệ cho báo cáo.

