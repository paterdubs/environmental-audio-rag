# ADR-0009 — Ngưỡng T3 phụ thuộc độ dài chồng lấp, và tách hai loại review

**Status:** Accepted
**Date:** 2026-09-23

## Context

Lần chạy `detect` đầu tiên với ngưỡng đã hiệu chuẩn ([ADR-0007](ADR-0007-fingerprint-va-luat-dedup.md))
cho ra **44,915 cặp ở dải `review`**. [DATA_PLAN §7.3](../DATA_PLAN.md) quy định
mỗi cặp `review` phải có quyết định của người. 44,915 quyết định thủ công không
phải một quy trình — đó là một cổng không chạy được.

### Vì sao nhiều đến thế: bài toán so sánh bội

Hiệu chuẩn đo tỷ lệ dương tính giả **trên mỗi cặp**: 11/5,000 = 0.22% ở ngưỡng
0.85. Cổng D3 lại so **16.6 triệu cặp**. 0.22% × 16.6 triệu ≈ 36,000 dương tính
giả — đúng bậc với 44,915 quan sát được. Ngưỡng không sai; việc áp một ngưỡng
per-pair lên một số lượng cặp lớn như vậy mới là chỗ sai.

### Cột `overlap` tách hai quần thể

Đo trên 45,191 cặp T3 thật:

| Dải similarity | Số cặp | Median overlap |
|---|---:|---:|
| [0.85, 0.88) | 31,731 | **1.0 s** |
| [0.88, 0.90) | 8,991 | **1.0 s** |
| [0.90, 0.93) | 3,767 | **1.0 s** |
| [0.93, 0.95) | 391 | **1.0 s** |
| [0.95, 0.99) | 212 | 14.5 s |
| [0.99, 1.00] | 99 | **42.5 s** |

Mọi dải dưới 0.95 có median overlap **đúng bằng sàn 1 giây**. 43,149 trong
45,191 cặp (95.5%) có overlap dưới 3 giây. Diễn giải: hai bản ghi tiếng ồn môi
trường bất kỳ đều tồn tại **một** cửa sổ 1 giây trông giống nhau. Đó là nhiễu,
không phải bằng chứng cùng nguồn.

Ngược lại, ba cặp xuyên dataset đạt `duplicate` có overlap 35 s, 13 s và 31 s.

Sàn 1 giây là do [ADR-0007 §6](ADR-0007-fingerprint-va-luat-dedup.md) đưa vào để
1,464 clip DataSEC ngắn hơn 3 s không nằm ngoài tầm phát hiện. Ý định đúng, nhưng
nó thiếu một luật bù: đoạn ngắn hơn thì cần bằng chứng mạnh hơn.

## Decision

### 1. Ngưỡng similarity phụ thuộc độ dài chồng lấp

```text
overlap >= min_overlap_s (3.0 s):
    similarity >= duplicate_min (0.95)  → duplicate
    similarity >= review_min    (0.85)  → review
    còn lại                             → distinct

required_overlap <= overlap < min_overlap_s:
    similarity >= short_duplicate_min (0.99) → duplicate
    còn lại                                  → distinct       ← KHÔNG có dải review
```

Đoạn ngắn **không có dải review**: bằng chứng trên 1–3 giây quá mỏng để đáng một
quyết định của người, và số lượng cặp như vậy khiến hàng đợi review vô dụng.

### 2. Tách review nội bộ khỏi review xuyên dataset

| Loại | Số cặp | Xử lý |
|---|---:|---|
| **Xuyên dataset** | **35** | Người quyết định. `review_queue_cross_dataset.csv` |
| Nội bộ một dataset | 1,731 | Ràng buộc **"cùng split"**. `split_cohesion_pairs.csv` |

Chỉ nhóm xuyên dataset ảnh hưởng RQ1: một clip pretraining trùng với recording ở
dev hoặc test của benchmark thì Δ transfer không còn diễn giải được. 35 cặp là
khối lượng làm tay được trong một buổi.

### 3. Review nội bộ trở thành ràng buộc cohesion, không phải quyết định xoá

Điều [DATA_PLAN §7.3](../DATA_PLAN.md) cấm là **tự động quyết định loại trừ**.
Giữ hai recording nghi ngờ trong cùng một split không phải loại trừ: nó không xoá
dữ liệu nào, và chỉ có thể làm **giảm** rò rỉ chứ không bao giờ che giấu. Vì vậy
áp tự động là hợp lệ, và nó gỡ được nút cổ chai 1,731 quyết định.

### 4. Cache giữ số đo, verdict tính lại mỗi lần

`pair_matches.csv` lưu `similarity` và `overlap_s` cho mọi cặp ≥ `evidence_min`
(0.85). `verdict` là **diễn giải**, được tính lại theo ngưỡng hiện hành mỗi lần
`regroup`. Tin vào verdict đã lưu nghĩa là đổi ngưỡng xong vẫn ra kết quả cũ —
đã xảy ra một lần trong lúc phát triển và suýt không bị phát hiện.

Giữ cả dải [0.85, 0.95) trong cache dù không dùng nữa: đó là bằng chứng cho
tuyên bố "dưới 0.95 là nhiễu", và cho phép hiệu chuẩn lại mà không chạy lại 45 phút.

## Consequences

### Tích cực

- Hàng đợi người giảm từ **44,915 → 35**, và 35 cặp đó là đúng những cặp quyết
  định tính hợp lệ của RQ1.
- Ba cặp xuyên dataset ở mức `duplicate` vẫn được giữ nguyên sau khi đổi luật —
  luật mới không làm mất phát hiện nào có thật.
- 1,464 clip DataSEC ngắn vẫn nằm trong tầm phát hiện (ý định của ADR-0007 §6),
  chỉ là phải đạt 0.99.
- Cache số đo cho phép thử một luật khác trong vài giây thay vì 45 phút.

### Đánh đổi

- **`short_duplicate_min = 0.99` chưa được hiệu chuẩn riêng.** Nó được chọn từ
  hình dạng phân bố quan sát được, không từ một tập positive của đoạn ngắn. Nếu
  có cặp trùng thật chỉ chồng lấp 1–2 giây và đạt 0.96, luật này bỏ sót. Ghi vào
  nợ kỹ thuật.
- Đoạn ngắn không có dải review nghĩa là không có vùng đệm: một cặp 0.985 bị xếp
  `distinct` thẳng, không ai xem.
- Ràng buộc cohesion làm split kém cân bằng hơn: 1,731 cặp buộc phải cùng split
  sẽ kéo theo các cụm recording. Ảnh hưởng thật tới phân bố lớp phải đo sau khi
  sinh split.
- Luật hai ngưỡng khó giải thích hơn một ngưỡng duy nhất, và phải nêu trong
  báo cáo thay vì để người đọc giả định 0.95 áp cho mọi cặp.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| **Nâng `review_min` lên 0.93** | Chỉ còn 702 cặp nhưng vẫn 391 cặp có median overlap 1 s — vẫn là nhiễu, chỉ ít hơn. Không chạm vào nguyên nhân |
| **Bỏ sàn 1 s, quay lại luật 3 s tuyệt đối** | 1,464 clip DataSEC (29%) rơi ngoài tầm phát hiện — đúng lỗ thủng mà ADR-0007 §6 vá |
| **Giữ 44,915 cặp, chỉ duyệt tay phần xuyên dataset (1,402)** | 1,402 vẫn quá nhiều, và để lại 43,513 cặp "chưa quyết định" treo vĩnh viễn trong artifact |
| **Hiệu chuẩn ngưỡng theo số dương tính giả kỳ vọng trên toàn bộ 16.6 triệu cặp** | Đúng về nguyên tắc, nhưng cần ước lượng đuôi ở mức 10⁻⁶; mẫu negative 5,000 không đủ và lấy mẫu lớn hơn không giúp vì negative hiếm khi vượt 0.93 |
| **Loại luôn cặp nội bộ ở dải review** | Loại 1,731 cặp bằng luật máy là đúng thứ §7.3 cấm, và xoá dữ liệu dựa trên bằng chứng yếu |

## Evidence cần kiểm lại

- [ ] `short_duplicate_min = 0.99` có bỏ sót cặp trùng thật ngắn không — cần một
      tập positive của đoạn 1–3 s, ví dụ cắt clip từ recording DataSED đã biết.
- [ ] 1,731 ràng buộc cohesion kéo theo cụm recording lớn cỡ nào; nếu có một cụm
      chiếm hơn 10% dataset thì split 60/20/20 không còn khả thi.
- [ ] 35 cặp xuyên dataset ở dải review, sau khi người xem, có bao nhiêu cặp thật.
- [ ] Ba cặp `duplicate` xuyên dataset có rơi vào dev/test sau khi sinh split không.
