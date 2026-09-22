# ADR-0003 — Threshold và post-processing

**Status:** Accepted
**Date:** 2026-09-22

## Context

Baseline hiện tại dùng threshold cố định **0.5** cho cả 21 class và không có hậu
xử lý nào. Ba lý do khiến cấu hình này chắc chắn không tối ưu:

1. **`pos_weight` tới 50.** Manifest của `sed_polyphonic_20260922T115340Z` cho
   thấy 6 class đạt trần `pos_weight = 50` (`bells`, `cat_fights_and_moans`,
   `chicken_coop`, `crows_seagulls_magpies`, `glass_breaking`, `horn`). Loss có
   trọng số lệch mạnh làm phân bố điểm đầu ra lệch theo, nên 0.5 không còn là
   điểm cân bằng precision/recall.
2. **21 class có tiên nghiệm rất khác nhau.** `cicadas_and_crickets` là nền liên
   tục kéo dài; `glass_breaking` là xung dưới 1 giây. Một threshold chung không
   thể phù hợp cả hai.
3. **Không có hậu xử lý nghĩa là không gộp đoạn, không lọc event vụn.** Frame-F1
   không phạt sự vụn; event-based F1 thì phạt nặng.

Bốn tham số hậu xử lý cần quyết định nguồn học:

```text
θ_c      threshold per class
w_c      median filter width
d_min_c  độ dài event tối thiểu
g_max_c  khoảng cách tối đa để gộp hai event cùng lớp
```

**Câu hỏi khó:** học chúng từ đâu? Trực giác nói "dev, vì dev là để chọn tham số".
Nhưng ba trong bốn tham số là **duration prior** — chúng suy từ thống kê thời
lượng nhãn, không phải từ điểm của model.

## Decision

### 1. Nguồn học tách theo bản chất tham số

| Tham số | Học từ | Không được học từ |
|---|---|---|
| `θ_c` | **dev** | test |
| `w_c` | **train** | dev, test |
| `d_min_c` | **train** | dev, test |
| `g_max_c` | **train** | dev, test |

**Lý do tách:** `θ_c` phụ thuộc phân bố *điểm của model*, nên phải đo trên tập
model chưa train lên — đó là dev. Ba tham số còn lại phụ thuộc phân bố *thời
lượng nhãn*, là thuộc tính của dữ liệu chứ không của model, nên suy từ train là
đủ và tránh được rò rỉ.

Nếu suy duration prior từ dev rồi đánh giá trên dev, hậu xử lý đã biết trước phân
bố của chính tập đang chấm. Dev score tăng vì rò rỉ, dẫn tới chọn sai cấu hình,
và test tụt nhiều hơn dự kiến — triệu chứng dễ bị chẩn đoán nhầm thành overfit model.

### 2. Per-class θ, quét trên lưới cố định

```text
θ ∈ [0.05, 0.95], bước 0.05, tối ưu event-based F1 của từng class trên dev
```

Báo cáo **cả** global θ và per-class θ (ablation A2), kèm chênh lệch dev→test của
cả hai để phát hiện overfit dev.

### 3. Suy duration prior từ train

| Tham số | Quy tắc |
|---|---|
| `d_min_c` | Percentile 5 của thời lượng event class `c` trong train |
| `g_max_c` | Percentile 50 của khoảng cách giữa hai event liên tiếp cùng class trong train |
| `w_c` | Làm tròn lẻ của `d_min_c × frame_rate / 2`, tối thiểu 1 |

### 4. Đóng băng vào `postproc.json` trước khi chạy test

```json
{
  "taxonomy_sha256": "67ca8a8c…",
  "calibrated_on": "dev",
  "duration_prior_from": "train",
  "per_class": {
    "glass_breaking": {"theta": 0.35, "median_w": 3, "d_min_s": 0.30, "g_max_s": 0.20}
  }
}
```

### 5. Lưu logit thô

Mỗi run ghi `predictions/{dev,test}.npz`. Không có nó, mỗi lần thử một θ khác
phải chạy lại toàn bộ inference.

## Consequences

### Tích cực

- Tách nguồn học theo bản chất tham số loại được một dạng rò rỉ khó thấy.
- Per-class θ kỳ vọng cải thiện đáng kể event-based F1 so với 0.5 cố định.
- Lưu logit thô làm việc quét ngưỡng rẻ đi hàng chục lần, cho phép ablation thật.
- `postproc.json` làm kết quả test tái lập được.

### Đánh đổi

- **21 bậc tự do fit trên dev.** Với dev 142 recording, per-class θ có thể overfit
  dev. Giảm thiểu: báo chênh lệch dev→test của cả global và per-class; nếu
  per-class tụt mạnh hơn thì nêu trong Hạn chế.
- Thêm một artifact (`postproc.json`) phải quản lý và version.
- Logit thô cho test set chiếm dung lượng: 1,344 window × 500 frame × 21 class ×
  4 byte ≈ 56 MB mỗi run. Nằm trong `ml/runs/**` nên không commit.
- Percentile 5 và 50 là lựa chọn khởi đầu, chưa có cơ sở thực nghiệm trên dữ liệu
  này. Phải hiệu chuẩn.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| **Giữ θ = 0.5 cố định** | Chắc chắn không tối ưu với `pos_weight` tới 50; và không so được với văn liệu |
| **Global θ duy nhất** | Đơn giản, ít overfit hơn, nhưng không xử lý được chênh lệch tiên nghiệm giữa `cicadas_and_crickets` và `glass_breaking`. Vẫn báo cáo làm ablation |
| **Học tất cả bốn tham số trên dev** | Rò rỉ duration prior — xem Decision §1 |
| **Học θ trên train** | Model đã fit train nên phân bố điểm trên train quá lạc quan; θ chọn ra sẽ quá cao |
| **Tối ưu θ trực tiếp trên PSDS** | PSDS tích phân trên toàn dải operating point nên theo thiết kế không phụ thuộc một θ; tối ưu θ theo PSDS là mâu thuẫn khái niệm |

## Evidence cần kiểm lại

- [ ] Percentile 5 / 50 có hợp lý trên phân bố thời lượng thật của DataSED không.
- [ ] Per-class θ có overfit dev không — đo chênh lệch dev→test.
- [ ] Trần `pos_weight = 50` có phải giá trị tốt không (ablation A4).
- [ ] Median filter có cải thiện event-F1 không, hay chỉ làm mất event ngắn
      như `glass_breaking` (ablation A3).
