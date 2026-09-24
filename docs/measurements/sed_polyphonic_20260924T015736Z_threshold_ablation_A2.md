# Ablation A2 — global θ so với per-class θ — `sed_polyphonic_20260924T015736Z`

> Sinh bởi `scripts.report_threshold_ablation ml\runs\sed_polyphonic_20260924T015736Z`. Không đổi `postproc.json` đã đóng băng (vẫn là per_class, chính thức); đây là báo cáo so sánh độc lập, dùng lại đúng priors/θ đã có.

## Event-based F1 đa lớp đồng thời — dev và test

| Chế độ | Dev F1 | Test F1 | Dev − Test |
|---|---:|---:|---:|
| Global (θ=0.95) | 0.0823 | 0.0788 | +0.0035 |
| Per-class | 0.1017 | 0.0616 | +0.0401 |

**Dấu hiệu overfit dev**: per-class tụt mạnh hơn global từ dev sang test (evaluation_protocol.md §2.4) — 21 bậc tự do fit trên dev. Ghi vào Hạn chế của báo cáo SED, không tự ý đổi lại `postproc.json`.