# K5 — event performance by duration and onset polyphony

> Reference events are binned; estimates are retained for the same recordings.
> Recall and F1 are event-based metrics; test predictions are read once.

## duration

| Bin | B n | B recall | B F1 | C n | C recall | C F1 |
|---|---:|---:|---:|---:|---:|---:|
| <1s | 33 | 0.030303 | 0.011834 | 33 | 0.000000 | 0.000000 |
| 1-3s | 184 | 0.065217 | 0.036364 | 184 | 0.059783 | 0.030942 |
| 3-10s | 257 | 0.042802 | 0.026316 | 257 | 0.035019 | 0.020455 |
| >10s | 266 | 0.082707 | 0.044000 | 266 | 0.052632 | 0.025735 |

## polyphony

| Bin | B n | B recall | B F1 | C n | C recall | C F1 |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 581 | 0.067126 | 0.055714 | 581 | 0.051635 | 0.039947 |
| 2 | 150 | 0.040000 | 0.020654 | 150 | 0.020000 | 0.009885 |
| >=3 | 9 | 0.111111 | 0.033333 | 9 | 0.111111 | 0.025974 |