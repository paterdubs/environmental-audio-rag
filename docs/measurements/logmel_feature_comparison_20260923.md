# So sánh logmel_v1 và logmel_panns_v1 trên 5 file DataSED chung (B4)

> Sinh bởi `scripts.compare_logmel_features`. Không sửa số bằng tay.

- Tỷ lệ frame kỳ vọng (32000/16000 Hz): `2.0`
- Tỷ lệ khớp kỳ vọng ở cả 5 file: **True**
- Tương quan bao trùm năng lượng thấp nhất trong 5 file: **0.9879**

| file_id | frames v1 | frames panns | tỷ lệ frame | khớp kỳ vọng | tương quan bao trùm |
|---|---:|---:|---:|---|---:|
| `S-0001.wav` | 2966 | 5931 | 1.9997 | True | 0.9881 |
| `S-0002.wav` | 6200 | 12399 | 1.9998 | True | 0.9879 |
| `S-0003.wav` | 4787 | 9574 | 2.0 | True | 0.9883 |
| `S-0004.wav` | 5349 | 10697 | 1.9998 | True | 0.9975 |
| `S-0005.wav` | 11666 | 23332 | 2.0 | True | 0.9983 |

## Diễn giải

Hai bộ đặc trưng dùng fmin/fmax và mel filterbank khác nhau (`logmel_v1`: 20–8000 Hz @ 16 kHz; `logmel_panns_v1`: 50–14000 Hz @ 32 kHz), nên so giá trị theo từng mel-bin không có nghĩa. Hai điều kiểm được:

1. **Tỷ lệ frame khớp đúng tỷ lệ sample rate** (32000/16000 = 2.0) — xác nhận `hop_length` tính theo mẫu (320) áp dụng nhất quán ở cả hai cấu hình, không phải một bên bị lỗi tính hop theo giây.
2. **Tương quan bao trùm năng lượng theo thời gian cao** (sau nội suy về cùng số frame) — xác nhận cả hai đại diện đúng cùng nội dung âm thanh vật lý, không phải lỗi decode/alignment làm lệch thời gian giữa hai bên.

Kết luận: khác biệt quan sát được là đúng kỳ vọng từ khác cấu hình (sample rate, fmin/fmax), **không phải lỗi resample**.