# ADR-0008 — Tỉ lệ split DataSED là 60/20/20

**Status:** Accepted
**Date:** 2026-09-23

## Context

Phát hiện khi chuẩn bị freeze split ở cổng D4: tài liệu và code nói hai con số
khác nhau, và chưa ADR nào ghi nhận sự khác biệt đó.

| Nguồn | Tỉ lệ | Bằng chứng |
|---|---|---|
| [DATA_PLAN §8.1](../DATA_PLAN.md) bảng nguyên tắc | 70/15/15 | văn bản |
| `scripts/create_splits.py` | **60/20/20** | `SplitConfig(train=0.6, validation=0.2, test=0.2)` |
| Split candidate đã sinh | **60/20/20** | 435/142/140 trên 717 recording |
| [ADR-0003](ADR-0003-threshold-va-post-processing.md) §Đánh đổi | **60/20/20** | "Với dev **142** recording, per-class θ có thể overfit dev" |

Số học: 717 × 0.70 = 502, không phải 435. 717 × 0.60 = 430 ≈ 435. Con số 142 mà
ADR-0003 dùng để lập luận về overfit chỉ tồn tại ở 60/20/20; với 70/15/15 thì dev
là 108 recording.

Nói cách khác: **toàn bộ dự án đã vận hành trên 60/20/20.** Chỉ một bảng trong
DATA_PLAN ghi 70/15/15, và không có ADR nào đứng sau nó.

[DATA_PLAN §8.4](../DATA_PLAN.md) quy định "tỉ lệ chỉ được đổi bằng ADR, và chỉ
trước khi xem test metrics". Cả hai điều kiện đang thoả: chưa có test metric nào
được sinh cho DataSED SED, và đây là ADR.

## Decision

**Giữ 60/20/20. Sửa DATA_PLAN §8.1 cho khớp với thực tế.**

Ba lý do, theo thứ tự trọng số:

### 1. ADR-0003 cần dev lớn

ADR-0003 quét **21 threshold per-class độc lập** trên dev. Đó là 21 bậc tự do fit
trên một tập duy nhất. ADR-0003 đã nêu rủi ro overfit dev với 142 recording; hạ
dev xuống 108 làm rủi ro đó tệ hơn khoảng 24% về cỡ mẫu mà không đổi số bậc tự do.

### 2. W4 cần test lớn

[PLAN W4](../PLAN.md) task 4.3 yêu cầu bootstrap CI **theo recording**, 1000 lần,
cho mọi số chính, trên 21 class. Với test 108 recording, nhiều class sẽ có quá ít
recording chứa sự kiện để CI có nghĩa. 140 recording không giải quyết hết vấn đề
nhưng tốt hơn rõ rệt, và chi phí là 67 recording rời khỏi train.

### 3. Đổi sang 70/15/15 tốn nhiều hơn được

Đổi nghĩa là: sinh lại split, sửa lại lập luận của ADR-0003, và mọi số đo đã có
(kể cả baseline `sed_polyphonic_20260922T115340Z`) mất tính so sánh. Đổi lại được
67 recording cho train — chưa tới 10% train, trên một dataset mà baseline hiện đã
đạt frame macro-F1 0.359 chứ không phải đang đói dữ liệu ở mức cấu trúc.

### 4. Điều **không** đổi

- Đơn vị split vẫn là **recording group**, không phải event, không phải window.
- Seed vẫn `20260922`.
- Iterative multilabel stratification theo event presence, 21 nhãn nhị phân.
- Split vẫn phải sinh lại **sau** cổng D3, vì duplicate group có thể buộc
  recording đổi split.
- DataSEC vẫn dùng 70/15/15 như [DATA_PLAN §8.3](../DATA_PLAN.md) — đó là dataset
  khác, kích thước khác (5,048 clip), và ADR-0006 đã lập luận riêng cho nó.

## Consequences

### Tích cực

- Code, split candidate, ADR-0003 và tài liệu nói cùng một con số. Không còn một
  mâu thuẫn im lặng nằm giữa spec và cài đặt.
- Dev 142 giữ được lập luận overfit của ADR-0003 nguyên vẹn.
- Không phải sinh lại baseline hay viết lại ADR nào.

### Đánh đổi

- **Train nhỏ hơn 67 recording** so với 70/15/15. Trên 717 recording thì đó là
  9.3% train. Với nhánh A (scratch) — nhánh đói dữ liệu nhất — đây là mất mát
  thật, và phải nêu nếu nhánh A kém bất thường.
- DataSEC 70/15/15 còn DataSED 60/20/20 là **hai quy tắc trong một dự án**. Phải
  giải thích trong báo cáo, không được để người đọc tự phát hiện.
- Tỉ lệ này khác mặc định 70/15/15 quen thuộc của văn liệu, nên khi so với số
  công bố của người khác phải nói rõ.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| **Sửa code về 70/15/15** | Phá lập luận định lượng của ADR-0003 (dev 142), buộc sinh lại split và mất tính so sánh của baseline đã đo. Đổi lại chỉ được 9.3% train |
| **Giữ mâu thuẫn, coi là chi tiết** | [DATA_PLAN §8.4](../DATA_PLAN.md) cấm đổi tỉ lệ ngoài ADR. Một spec nói 70/15/15 trong khi code chạy 60/20/20 là đúng thứ làm kết quả không tái lập được |
| **70/15/15 cho train, nhưng gộp dev vào test khi báo cáo** | Phá tính độc lập của đánh giá: θ đã chọn trên dev thì dev không còn là tập chưa thấy |
| **Split theo tỉ lệ khác nữa, ví dụ 60/15/25** | Không có lập luận nào đỡ; và mọi thay đổi đều tốn chi phí sinh lại như nhau |

## Evidence cần kiểm lại

- [ ] Sau khi sinh lại split hậu-D3, phân bố 21 class ở dev và test có đủ mẫu để
      bootstrap CI theo recording không — nếu không, nêu trong Hạn chế thay vì
      đổi tỉ lệ sau khi đã thấy dữ liệu.
- [ ] Nhánh A (scratch) có kém bất thường do train nhỏ hơn không.
- [ ] Số recording thực tế sau khi loại duplicate group có còn giữ xấp xỉ
      60/20/20 không.
