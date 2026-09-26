# Ablation A4 — trần `pos_weight` (nhánh B, seed 20260922, một run mỗi trần)

> Sinh bởi `scripts.report_pos_weight_ablation`, giao thức ADR-0028 (ghi trước khi có số). So sánh bằng event-F1 **dev** với postproc riêng của từng run; test chạy một lần, chỉ để báo. "Tốt hơn" chỉ khi vượt trần 50 trên dev quá 0.0096 (2 × SD seed). Event-F1 dev là số in-sample (θ quét trên chính dev) nên lạc quan như nhau ở mọi trần — dùng để so giữa các trần, không để so với test.

| Trần | Lớp chạm trần | pos_weight lớn nhất | Frame macro-F1 dev | Event-F1 dev | Δ dev vs 50 | Event-F1 test | PSDS-1 test | PSDS-2 test | Kết luận |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 10 | 20 | 10.0 | 0.6013 | 0.1233 | +0.0418 | 0.0725 | 0.3010 | 0.6292 | tốt hơn |
| 30 | 10 | 30.0 | 0.5684 | 0.0944 | +0.0130 | 0.0548 | 0.2722 | 0.6656 | tốt hơn |
| 50 | 6 | 50.0 | 0.5475 | 0.0814 | +0.0000 | 0.0621 | 0.2818 | 0.6456 | mốc |
| không clip | 0 | 203.7 | 0.5453 | 0.0946 | +0.0132 | 0.0614 | 0.2687 | 0.6643 | tốt hơn |

Runs: `sed_polyphonic_20260925T205837Z`, `sed_polyphonic_20260925T211704Z`, `sed_polyphonic_20260924T054531Z`, `sed_polyphonic_20260925T213732Z`
