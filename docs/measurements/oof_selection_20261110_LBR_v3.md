# LBR V3 — cấu hình ứng dụng (ADR-0045 §11, ADR-0046)

> OOF 564 recording annotated, 5 fold, cross-fit lồng nhau như tầng C. V3 được tìm ra **sau** khi xem kết quả tầng C trên chính OOF này (thăm dò 10/11) — không phải ứng viên ghi trước, không thay V2 làm số chính. Không đọc test.

## Thước chính — 21 lớp, điểm F1

| Hệ thống | Macro | Micro | Nsys/Nref | Δ micro [95% CI] |
|---|---:|---:|---:|---|
| B0 | 0.1797 | 0.2342 | 1761/3294 | — |
| P1x3 | 0.1794 | 0.2344 | 1902/3294 | — |
| LBR_v3 | 0.2347 | 0.3058 | 2016/3294 | +0.0716 [+0.0489, +0.0917] vs B0 |
| LBR_v3_on_P1x3 | 0.2407 | 0.3160 | 1877/3294 | +0.0816 [+0.0602, +0.1021] vs P1x3 |

## Thước ứng dụng — 21 lớp

| Hệ thống | Điểm | Micro chính | Collar 1 s | Segment 1 s | Giao nhau P | Giao nhau R | Giao nhau F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| B0 | f1 | 0.2342 | 0.4645 | 0.7007 | 0.9476 | 0.5495 | 0.6956 |
| B0 | recall_first | 0.1811 | 0.3945 | 0.7776 | 0.6275 | 0.7799 | 0.6955 |
| P1x3 | f1 | 0.2344 | 0.4858 | 0.7188 | 0.9347 | 0.5999 | 0.7308 |
| P1x3 | recall_first | 0.1789 | 0.4038 | 0.7773 | 0.6272 | 0.7963 | 0.7017 |
| LBR_v3 | f1 | 0.3058 | 0.5247 | 0.7693 | 0.9591 | 0.6697 | 0.7887 |
| LBR_v3 | recall_first | 0.2302 | 0.4137 | 0.7594 | 0.6744 | 0.8336 | 0.7456 |
| LBR_v3_on_P1x3 | f1 | 0.3160 | 0.5175 | 0.7663 | 0.9772 | 0.6512 | 0.7816 |
| LBR_v3_on_P1x3 | recall_first | 0.2582 | 0.4518 | 0.7738 | 0.7710 | 0.8175 | 0.7936 |

## Thước ứng dụng — 19 lớp Việt Nam

| Hệ thống | Điểm | Micro chính | Collar 1 s | Segment 1 s | Giao nhau P | Giao nhau R | Giao nhau F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| B0 | f1 | 0.2425 | 0.4766 | 0.7103 | 0.9464 | 0.5538 | 0.6987 |
| B0 | recall_first | 0.1869 | 0.4020 | 0.7742 | 0.6257 | 0.7829 | 0.6955 |
| P1x3 | f1 | 0.2405 | 0.4942 | 0.7228 | 0.9357 | 0.6038 | 0.7340 |
| P1x3 | recall_first | 0.1824 | 0.4099 | 0.7690 | 0.6275 | 0.7986 | 0.7028 |
| LBR_v3 | f1 | 0.3155 | 0.5303 | 0.7621 | 0.9592 | 0.6679 | 0.7874 |
| LBR_v3 | recall_first | 0.2362 | 0.4176 | 0.7505 | 0.6736 | 0.8379 | 0.7468 |
| LBR_v3_on_P1x3 | f1 | 0.3251 | 0.5234 | 0.7565 | 0.9759 | 0.6483 | 0.7790 |
| LBR_v3_on_P1x3 | recall_first | 0.2650 | 0.4559 | 0.7659 | 0.7721 | 0.8209 | 0.7958 |

Sàn precision điểm ưu tiên phát hiện: 0.6.
Ngưỡng theo fold: {'0': {'f1': 0.85, 'recall_first': 0.005}, '1': {'f1': 0.85, 'recall_first': 0.005}, '2': {'f1': 0.85, 'recall_first': 0.005}, '3': {'f1': 0.85, 'recall_first': 0.005}, '4': {'f1': 0.85, 'recall_first': 0.005}}.
