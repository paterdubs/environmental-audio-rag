# Run huấn luyện DataSEC — `classifier_datasec_20260923T121808Z`

> Sinh bởi `scripts.report_classifier_run ml\runs\classifier_datasec_20260923T121808Z`. Không sửa số bằng tay.

- Nạp checkpoint AudioSet — đây là bước giữa của **nhánh C** (ADR-0002).
- Checkpoint: `artifacts/checkpoints/Cnn14_mAP=0.431.pth`
- Checkpoint SHA-256: `7f0ea3a7ad9622f7bdc22439a750e04efdc1641bc4c930ff8727bb92d3141a69`
- Tỷ lệ tham số transplant: `0.9223014234971963`
- Split SHA-256: `e8d3099010ac2937e5bb9c542a29f51fe50712525a7d35d077c0cedec75ec60a`
- Taxonomy SHA-256: `67ca8a8c53278cd438d7d06a4ba09e277f3f9a6df99460bdbec1d3a927729a3a`
- Seed: `20260922`
- Git dirty lúc chạy: `False`
- Số item: train=3434, validation=744, test=740
- Best checkpoint: epoch 12/12 (validation coarse_macro_f1 = 0.8230)

## Test (chạy một lần, sau khi khoá best checkpoint)

| Metric | Giá trị |
|---|---:|
| coarse macro-F1 | 0.8466 |
| subclass macro-F1 (tất cả node) | 0.6266 |
| subclass macro-F1 (n≥10, 5 node) | 0.8453 |
| parent-consistency rate | 0.9526 |
| loss | 1.5497 |
| số item / có subclass | 740 / 203 |

## Diễn giải

`subclass macro-F1 (n≥10)` là số diễn giải được (ADR-0006 §3) — 5 node đạt ngưỡng này trên test: `[13, 14, 18, 20, 26]` (chỉ số trong không gian 28 subclass). Số `(tất cả node)` có nhiễu từ các lớp n_test nhỏ, chỉ báo cáo kèm theo, không thay thế.

`parent-consistency rate` đo tỷ lệ subclass dự đoán rơi đúng gia đình coarse dự đoán — so với baseline random $k_c/28$ đã đặc tả ở [ADR-0006 §7](../decisions/ADR-0006-danh-gia-subclass.md) khi có số đó.