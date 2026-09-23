# ADR-0012 — Ràng buộc cohesion đòi bằng chứng trên mức dương tính giả đã đo

**Status:** Accepted
**Date:** 2026-09-23

## Context

Split DataSEC đầu tiên chạy được với tỉ lệ đã chốt 70/15/15
([DATA_PLAN §8.3](../DATA_PLAN.md), [ADR-0008](ADR-0008-ti-le-split-datased.md))
cho ra **65.2 / 20.4 / 14.5**. Lệch 5 điểm phần trăm không phải sai số làm tròn.

Nguyên nhân: một `leakage_group` **315 file** rơi trọn vào validation.

### Cụm 315 không phải một cụm

| Tính chất | Giá trị | Nếu là cụm trùng thật |
|---|---:|---|
| Số đỉnh | 315 | — |
| Cạnh cohesion bên trong | 1,171 | 49,455 |
| **Mật độ** | **0.024** | ≈ 1.0 |
| Đỉnh chỉ có **một** cạnh | 70 | ≈ 0 |
| Số lớp coarse khác nhau | **4** | 1 |

Thành phần này gồm `voices` 259, `music` 42, `thunder_fireworks_gunshot` 13,
`propeller_aircrafts` 1. Một cụm chứa cả tiếng người lẫn tiếng nổ không phải "cùng
một bản thu nguồn" — đó là **chaining của single-linkage**.

Đây đúng là lỗi [ADR-0009 §2](ADR-0009-nguong-phu-thuoc-overlap.md) đã phát hiện và
sửa cho cạnh `duplicate` (thành phần 2,310 file nối bằng ngưỡng yếu nhất 0.850).
Lần đó `build_groups` được sửa để **chỉ** union cạnh `duplicate`. Nhưng cohesion
vẫn union toàn bộ cạnh `review`, nên cùng một cơ chế hỏng vẫn còn nguyên ở tầng
bên cạnh — chỉ là chưa ai nhìn vào vì DataSED cụm lớn nhất chỉ có 4.

### Vì sao chaining lại mạnh đến vậy ở `voices`

Bỏ 58 cạnh xuyên lớp (3.4%) chỉ làm cụm co từ 315 xuống 254. Chaining nằm **bên
trong** `voices` — lớp chiếm 37.6% DataSEC. Clip tiếng nói chia sẻ cấu trúc phổ
băng rộng, nên ở dải review chúng nối yếu với nhau hàng loạt. Đây chính là quần
thể dương tính giả mà ADR-0009 đã định lượng: FPR 0.22% mỗi cặp × 16.6 triệu cặp.

### Ngưỡng ở đâu thì khối tan

Quét trên 1,712 cặp review nội bộ DataSEC:

| sim ≥ | overlap ≥ | Cạnh giữ lại | Cụm lớn nhất |
|---:|---:|---:|---:|
| 0.85 | 3 s | 1,367 | **315** |
| 0.88 | 3 s | 306 | 75 |
| 0.90 | 3 s | 136 | 14 |
| 0.92 | 3 s | 76 | 6 |
| 0.94 | 3 s | 34 | 4 |
| 0.85 | 10 s | 104 | 13 |

Không có điểm gãy nhân tạo nào cần bịa ra: **hiệu chuẩn đã cho sẵn con số**.
[ADR-0007](ADR-0007-fingerprint-va-luat-dedup.md) đo trên 5,000 cặp ngẫu nhiên
khác nhãn và được `negative_max = 0.9205`.

## Decision

### 1. Cohesion đòi `similarity ≥ 0.93`

`COHESION_MIN_SIMILARITY = 0.93` — giá trị sạch đầu tiên **trên** mức dương tính
giả cao nhất đã đo (0.9205). Dưới mức đó, một cặp không mang bằng chứng phân biệt
được với nhiễu, nhưng vẫn phải trả giá bằng chất lượng split.

Ngưỡng `review` **không** đổi: 0.85 vẫn là mức để một cặp được *nhìn*. Thay đổi ở
đây là mức để một cặp trở thành *ràng buộc*. Xem, và bị ràng buộc, là hai việc có
giá khác nhau.

### 2. "Chỉ có thể làm giảm rò rỉ" không có nghĩa là miễn phí

Lập luận cũ trong `split_cohesion_pairs` là: giữ hai recording nghi ngờ cùng split
thì không bao giờ che giấu rò rỉ, nên xử lý tự động được mà không vi phạm
DATA_PLAN §7.3. Lập luận đó vẫn đúng về **an toàn** và sai về **chi phí**. Ràng
buộc được lấy hợp bắc cầu, nên cạnh yếu không chỉ tốn đúng cặp của nó — nó kéo
theo cả thành phần liên thông.

### 3. Sinh lại cohesion bằng một lệnh riêng, không bằng `regroup`

`regroup` gọi `_finalise`, mà hàm đó **ghi đè `exclusions.csv`** bằng luật nội bộ:
chạy nó sẽ xoá sạch 11 quyết định của người và đặt lại
`cross_dataset_exclusions_pending_split`. Ngưỡng cohesion không liên quan gì tới
những thứ đó. Thêm `scripts.find_duplicates cohesion` chỉ ghi đúng một file.

### 4. `data-v1.0` **không** sinh lại

Luật mới chỉ **bỏ** cạnh, nên phân hoạch mới là *mịn hơn* phân hoạch cũ. Split
thoả "cùng nhóm ⇒ cùng split" theo nhóm cũ thì tự động thoả theo nhóm mới. Đã kiểm
trên split đã đóng băng: **0 vi phạm** với cả hai luật, `split_sha256` giữ nguyên
`d2924a5e45c2b271…`. Split DataSED vì vậy chỉ *chặt hơn cần thiết*, không mất an
toàn — và chặt hơn cần thiết không phải lý do để phá một artifact đã đóng băng.

## Consequences

### Tích cực

| | Trước | Sau |
|---|---:|---:|
| Cặp cohesion | 1,731 | **109** |
| Cụm DataSEC lớn nhất | 315 | **4** |
| Số `leakage_group` DataSEC | 4,457 | 4,873 |
| Tỉ lệ split DataSEC | 65.2/20.4/14.5 | **69.8/15.1/15.1** |

Và độ phủ lớp đạt đủ: **50/50 nhãn** (22 coarse + 28 subclass) có mặt ở cả ba
split. Bốn subclass hỗ trợ thấp ra đúng như ADR-0006 §4 dự báo —
`magpies` 13/3/3, `crickets` 14/3/3, `olive_shaker` 14/3/3, `lawn_mower` 15/3/3.

### Đánh đổi

- 1,622 cặp không còn là ràng buộc. Nếu trong số đó có cặp cùng nguồn thật, hai
  clip của nó **có thể** rơi vào hai split khác nhau. Đây là đánh đổi có ý thức:
  bằng chứng của chúng nằm dưới mức nhiễu đã đo, còn chi phí thì đo được rõ ràng.
- Ngưỡng 0.93 kế thừa toàn bộ giả định của lần hiệu chuẩn ADR-0007. Hiệu chuẩn lại
  bằng bộ thống kê khác thì phải xem lại con số này.
- DataSED đã đóng băng dưới luật cũ, DataSEC sinh dưới luật mới. Hai artifact sinh
  bởi hai phiên bản luật — chấp nhận được **chỉ vì** luật mới mịn hơn, và phải nêu
  rõ khi mô tả quy trình.

## Alternatives considered

- **Giữ nguyên, chấp nhận lệch 5 điểm.** Không chỉ lệch tỉ lệ: validation bị nhét
  một khối 315 clip do `voices` chi phối, làm lệch cả phân bố lớp của split đó.
- **Chỉ bỏ cạnh xuyên lớp.** Đo được là không đủ: 315 → 254. Và nó sai về nguyên
  tắc — hai clip khác lớp **vẫn có thể** cùng một bản thu nguồn.
- **Dùng `overlap ≥ 10 s` thay cho ngưỡng similarity.** Cho kết quả tương đương
  (cụm lớn nhất 13), nhưng 10 s là con số chọn tay; 0.9205 là con số đã đo.
- **Chặn kích thước cụm.** Xử lý triệu chứng, và "cụm bao nhiêu là to" lại là một
  hằng số bịa nữa.
- **Sinh lại và đóng băng lại DataSED thành `data-v1.1`.** Không có lợi ích an toàn
  nào — đã chứng minh split cũ thoả luật mới.

## Evidence cần kiểm lại

- Sau khi có E1: lấy mẫu vài cặp trong 1,622 cặp bị bỏ và nghe, xem có cặp cùng
  nguồn thật nào không. Nếu có, ghi vào Hạn chế.
- `voices` chiếm 37.6% và là nguồn chaining chính. Nếu lớp khác cũng vậy ở dataset
  khác, ngưỡng cohesion nên suy từ phân bố similarity **trong từng lớp**.
