# ADR-0007 — Fingerprint T3 và luật dedup cho file ngắn

**Status:** Accepted
**Date:** 2026-09-23

## Context

[DATA_PLAN §7.2–§7.3](../DATA_PLAN.md) đặc tả ba tầng phát hiện trùng lặp. Khi
triển khai, chín điều trong đặc tả **đo được là không chạy như mô tả**. ADR này
ghi lại các lệch, vì chúng ảnh hưởng trực tiếp tới cổng D3 — cổng quyết định RQ1
có diễn giải được hay không.

Mọi số dưới đây sinh từ `tests/test_fingerprint.py` và từ inventory đã commit,
không phải ước lượng.

### Dữ kiện đo được

| # | Quan sát | Số đo | Nguồn |
|---:|---|---|---|
| 1 | DataSEC **không** phải 16 kHz như DATA_PLAN §7.2 ghi | 5,048/5,048 file ở **44.1 kHz**, mono | `datasec_inventory_summary.json` |
| 2 | `C0` của MFCC phụ thuộc gain, chi phối cosine | Hai đoạn **giống hệt** chỉ đạt cosine **0.15** | `_frame_vector` trước khi sửa |
| 3 | Trung bình có dấu của delta triệt tiêu | norm 0.25 so với 13.9 của nửa MFCC | cùng trên |
| 4 | Dải sát Nyquist nhạy với resampler | `fmax=8000` → 0.577; `fmax=7000` → **1.000** | `test_fingerprint_survives_resample_roundtrip` |
| 5 | T2 không bắt được đổi bit-depth | **49.5%** mẫu lệch đúng 1 LSB giữa PCM_16 và PCM_24 | `test_documents_t2_cannot_catch_bit_depth_change` |
| 6 | Luật chồng lấp 3 s loại bỏ phần lớn clip ngắn | **1,464 clip DataSEC (29.0%)** ngắn hơn 3 s | `datasec_inventory.csv` |
| 7 | Negative phổ phẳng đạt điểm cao giả | Hai nguồn nhiễu trắng vô quan hệ: **0.88** > ngưỡng review 0.85 | `test_documents_flat_spectrum_negatives_score_high` |
| 8 | Cosine chưa chuẩn hoá **không tách được** positive khỏi negative | **52.6%** cặp ngẫu nhiên khác nhãn vượt 0.85; negative max **0.983** > positive min | lần hiệu chuẩn đầu |
| 9 | Frame tĩnh lặng cho vector 0, bị tính là bất tương đồng | Một cặp DataSED **byte-identical** chỉ đạt **0.95 = 57/60** vì 3 frame lặng | `S-0606` / `S-0622` |

Điểm 5 đáng nói riêng. DATA_PLAN §7.2 biện minh sự tồn tại của T2 **chính bằng**
ví dụ 16-bit/24-bit. Đo cho thấy đó là ví dụ T2 không làm được: lệch là hệ thống
ở tầng libsndfile, tỷ lệ thuận theo bit nên không ngưỡng bit nào vá được.

## Decision

### 1. T3 bỏ hệ số MFCC thứ 0, lấy `n_mfcc = 21` rồi cắt

Giữ đúng 20 hệ số như đặc tả, nhưng là hệ số 1–20 thay vì 0–19. `C0` là
log-năng lượng, phụ thuộc gain, và peak-normalize không cứu được vì trích đoạn
với file gốc có peak khác nhau.

### 2. Nửa delta gộp bằng trung bình **trị tuyệt đối**

Giữ 40 chiều như đặc tả, nhưng 20 chiều delta mang thông tin biến thiên thay vì
gần như bằng 0.

### 3. Chuẩn hoá L2 **từng nửa** trước khi ghép, rồi chuẩn hoá vector đầy đủ

Không làm thì nửa có thang lớn hơn quyết định toàn bộ cosine.

### 4. `fmax = 7000` thay vì Nyquist 8000

Mọi so khớp xuyên dataset đều đi qua ít nhất một lần resample. Dải sát Nyquist
là dải bộ lọc của resampler can thiệp, nên loại nó khỏi fingerprint.

### 5. T2 giữ nguyên định nghĩa, nhưng tuyên bố đúng năng lực

T2 = SHA-256 trên PCM đã decode, resample 16 kHz mono, lượng tử hoá int16 (thang
2¹⁵, đúng thang libsndfile đọc PCM_16). Nó bắt **khác container, khác metadata,
khác layout kênh**. Nó **không** bắt đổi bit-depth. Phần đó do T3 lo — cặp
24-bit/16-bit cho cosine 1.000.

### 6. Luật chồng lấp cho file ngắn

```text
required_overlap = max( min(3.0, thời lượng file ngắn hơn), 1.0 )

Nếu required_overlap < 3.0:
    verdict tối đa là `review` — không bao giờ tự động `duplicate`
```

File ngắn hơn 1.0 s **không** được T3 kết luận, và danh sách `file_id` của chúng
phải nằm trong `duplicate_audit.json` (`unreachable_by_tier3`) để báo cáo nêu
đúng độ phủ của cổng D3, thay vì im lặng.

### 7. Không dùng pre-filter — so khớp đầy đủ mọi cặp

Sau khi vector hoá vòng lặp lag bằng `bincount` (899 µs → 50 µs mỗi cặp cỡ trung
vị), toàn bộ 16.6 triệu cặp chạy trong khoảng 15 phút. Một heuristic gate chỉ
thêm rủi ro bỏ sót mà không đổi được bậc thời gian.

### 8. Loại frame tĩnh lặng khỏi trung bình cosine

Frame có norm 0 không mang thông tin. Tính nó vào trung bình là phạt oan file có
khoảng lặng, tới mức một cặp byte-identical không đạt nổi 1.000. Trung bình phải
lấy trên **số cặp frame hợp lệ**, không trên độ dài hình học của đường chéo.

### 9. Chuẩn hoá z-score theo thống kê corpus trước khi so cosine

Đây là thay đổi quan trọng nhất trong ADR này. Không có nó, cosine bị chi phối
bởi hình dạng phổ **trung bình** mà mọi bản ghi tiếng ồn môi trường đều chia sẻ,
nên T3 không phân biệt được "cùng nguồn" với "cùng loại khung cảnh".

Thống kê ước lượng trên frame hợp lệ của **cả hai** dataset và cache lại. Dùng
toàn corpus là hợp lệ ở đây: dedup chạy **trước** khi có split, và bước này không
dùng nhãn nào. `standardizer_sha256` đi vào mọi artifact, vì một ngưỡng đã hiệu
chuẩn chỉ có nghĩa với đúng bộ thống kê đã dùng lúc hiệu chuẩn.

| | Trước chuẩn hoá | Sau chuẩn hoá |
|---|---:|---:|
| positive min (24 cặp T1) | 0.950 | **1.000** |
| negative max (5,000 cặp) | 0.983 | **0.920** |
| negative p99.9 | 0.978 | **0.869** |
| negative ≥ 0.85 | 2,630 (52.6%) | **11 (0.22%)** |
| negative ≥ 0.95 | — | **0** |
| tách được? | **không** | **có** |

### 10. Hiệu chuẩn ngưỡng phải báo cả negative

`scripts.find_duplicates calibrate` ghi phân bố của positive (cặp T1 byte-identical)
**và** negative (cặp ngẫu nhiên khác nhãn), kèm số negative vượt 0.85 và 0.95.
Positive byte-identical luôn cho 1.000 nên **tự nó không chứng minh được gì** về
ngưỡng 0.95; chỉ phân bố negative mới nói ngưỡng có tách được hai lớp hay không.

## Consequences

### Tích cực

- Cặp cùng nội dung khác encode giờ cho cosine 1.000 thay vì 0.15 — nếu không
  sửa, cổng D3 sẽ báo "không có trùng lặp xuyên dataset" và kết luận đó **sai**.
- Độ phủ T3 tăng từ 71.0% lên 90.8% clip DataSEC (chỉ còn 464 clip < 1 s ngoài tầm).
- Thời gian chạy cho phép chạy lại toàn bộ khi ngưỡng đổi, nên hiệu chuẩn là
  việc làm được chứ không phải việc phải tin.

### Đánh đổi

- Luật file ngắn đẩy thêm việc sang người quyết định. Chưa biết số nhóm `review`
  là bao nhiêu cho tới khi chạy xong.
- Bỏ `C0` nghĩa là fingerprint mù với mức áp suất âm tuyệt đối. Hai bản ghi cùng
  nội dung nhưng khác mức sẽ được coi là trùng — với mục đích dedup thì đúng.
- `fmax = 7000` bỏ dải 7–8 kHz. Các lớp có năng lượng chủ yếu ở dải này (ví dụ
  một số tiếng côn trùng) bị mất một phần đặc trưng phân biệt.
- Ngưỡng 0.95/0.85 của DATA_PLAN §7.3 **đã được xác nhận bằng đo** — nhưng chỉ
  sau khi có chuẩn hoá z-score. Với fingerprint như đặc tả chữ nghĩa, cùng ngưỡng
  đó cho 52.6% dương tính giả. Nói cách khác: ngưỡng không sai, phương pháp đo
  khoảng cách mới là chỗ sai.
- Thống kê chuẩn hoá phụ thuộc corpus. Thêm dataset thứ ba thì phải hiệu chuẩn
  lại ngưỡng, không được mang số cũ sang.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| **Giữ nguyên `C0`, tin vào peak-normalize** | Đo được: cosine của hai đoạn giống hệt rơi xuống 0.15. Cổng D3 sẽ mù |
| **Hạ số bit của T2 để hấp thụ lệch 1 LSB** | Lệch tỷ lệ thuận theo bit: 15-bit còn 7,520/32,000 mẫu lệch, 12-bit còn 800. Không có điểm dừng đúng |
| **Giữ luật 3 s tuyệt đối** | Bỏ 1,464 clip (29%) khỏi tầm phát hiện mà không nói ra — lỗ thủng của cổng, không phải thận trọng |
| **Tự động `duplicate` cho cặp ngắn đạt 0.95** | Cosine trên 1–3 s nhiễu hơn hẳn; và negative phổ phẳng đã đạt 0.88 trên đoạn dài |
| **Pre-filter theo nhãn coarse** | Giả định nhãn đúng và đầy đủ. Một bản ghi tái sử dụng có thể được gán nhãn khác ở hai dataset, đúng lúc ta cần bắt nhất |
| **Pre-filter theo cosine của vector trung bình** | Phải chứng minh recall của gate trên positive thật, mà positive thật lại chính là thứ đang đi tìm |

## Evidence cần kiểm lại

- [x] Phân bố negative thật trên DataSEC/DataSED có tách khỏi 0.95 không —
      **có**: negative max 0.9205, 0/5,000 vượt 0.95
      (`data/interim/dedup/threshold_calibration.json`).
- [ ] Số nhóm `review` sinh ra có nằm trong khả năng xử lý thủ công không.
- [ ] 464 clip < 1 s có tập trung vào lớp nào không; nếu tập trung vào một lớp
      thì độ phủ D3 lệch theo lớp và phải nêu trong Hạn chế.
- [ ] `fmax = 7000` có làm giảm khả năng phân biệt lớp tần số cao không.
- [ ] Sửa DATA_PLAN §7.2: DataSEC là 44.1 kHz, không phải 16 kHz.
