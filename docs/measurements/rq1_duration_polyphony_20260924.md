# K5 — event performance by duration and onset polyphony

> Reference events are binned; estimates are retained for the same recordings.
> Recall and F1 are event-based metrics; test predictions are read once.

## duration

| Bin | B n | B recall | B F1 | C n | C recall | C F1 |
|---|---:|---:|---:|---:|---:|---:|
| <1s | 33 | 0.030303 | 0.011834 | 33 | 0.000000 | 0.000000 |
| 1-3s | 184 | 0.092391 | 0.052550 | 184 | 0.070652 | 0.041868 |
| 3-10s | 257 | 0.042802 | 0.026667 | 257 | 0.042802 | 0.028169 |
| >10s | 266 | 0.078947 | 0.041625 | 266 | 0.048872 | 0.027168 |

## polyphony

| Bin | B n | B recall | B F1 | C n | C recall | C F1 |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 581 | 0.074010 | 0.061429 | 581 | 0.053356 | 0.045756 |
| 2 | 150 | 0.040000 | 0.020761 | 150 | 0.033333 | 0.018553 |
| >=3 | 9 | 0.111111 | 0.033333 | 9 | 0.111111 | 0.031746 |