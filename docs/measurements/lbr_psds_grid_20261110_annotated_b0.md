# PSDS của LBR với lưới ghi trước (ADR-0047) — test, annotated, n=139

| Run | Lưới | PSDS-1 | PSDS-2 | Điểm | Event ở ngưỡng thấp nhất | Box không bao giờ vào |
|---|---|---:|---:|---:|---:|---:|
| B0 (cSEBB) | tuyến tính (evaluate_run) | 0.3131 | 0.7310 | 19/19 | 2134 | 2535 |
| B0 (cSEBB) | log 1e-5..0.99 (mới) | 0.3061 | 0.7452 | 48/48 | 4668 | 1 |

B0 (cSEBB): lưới tuyến tính tái tạo đúng `evaluation_phase_o_annotated.json` (ADR-0048 §3).

git: `36b1b10761dfbebdab82ddcaeebe5208d39f842a` dirty=False
