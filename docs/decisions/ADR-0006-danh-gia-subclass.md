# ADR-0006 — Đánh giá subclass trên continuous audio

**Status:** Accepted
**Date:** 2026-09-22

## Context

RQ4 hỏi: *classifier phân cấp có tách được subclass trong các coarse class gộp
không?* Hai lớp gộp đáng quan tâm nhất:

| Coarse class | Subclass DataSEC | Vì sao quan trọng |
|---|---|---|
| `sirens_and_alarms` | `Sirens` (68), `Alarms` (37) | Còi xe khác báo động tại chỗ về ý nghĩa |
| `thunder_fireworks_gunshot` | `Thunder` (26), `Fireworks` (68), `Gunshot` (141) | Ba nguồn hoàn toàn khác bản chất |

**Vấn đề cốt lõi: DataSED không có subclass ground truth.** Annotation chỉ ở mức
coarse. Model *có thể* dự đoán subclass trên continuous audio, nhưng không có gì
để đối chiếu.

**Vấn đề thứ hai, đo được ở Phase 1:** bốn subclass có dưới 25 file.

| Subclass | Files | test (70/15/15) | Một mẫu sai = |
|---|---:|---:|---:|
| `Crickets` | 20 | 3 | 33 điểm % |
| `Olive shaker` | 20 | 3 | 33 điểm % |
| `Magpies` | 21 | 4 | 25 điểm % |
| `Lawn mower` | 21 | 4 | 25 điểm % |

Cám dỗ ở đây rất cụ thể: báo "subclass accuracy trên DataSED = 0.74" nghe như một
kết quả. Nó không phải — không có mẫu số đúng để tính.

## Decision

### 1. Metric subclass chỉ báo trên DataSEC test

Chỉ ở đây mới có ground truth. Macro-F1 subclass, per-class, hierarchical
consistency.

### 2. Trên DataSED báo ba thứ, và không cái nào là accuracy

| Báo cáo | Nghĩa | Không được gọi là |
|---|---|---|
| **Parent-consistency rate** | Tỷ lệ subclass prediction thuộc đúng coarse class mà SED phát hiện | accuracy |
| **Phân bố subclass prediction** | Histogram, so với tiên nghiệm DataSEC | độ chính xác |
| **Phân tích định tính** | Một số case có nghe kiểm chứng, nêu rõ cỡ mẫu | kết quả định lượng |

Parent-consistency đo được **một điều thật**: model có tự mâu thuẫn không. Nếu
SED nói `sirens_and_alarms` mà subclass head nói `gunshot`, đó là lỗi cấu trúc
phát hiện được không cần ground truth.

### 3. Báo hai con số macro-F1 subclass, không thay thế nhau

```text
subclass macro-F1 (tất cả node)         ← có nhiễu từ 4 class n_test < 10
subclass macro-F1 (node có n_test >= 10) ← số diễn giải được
```

### 4. Class có `n_test < 10` báo bằng số tuyệt đối

```text
✅ Crickets: đúng 2/3 · Olive shaker: đúng 1/3 · Magpies: đúng 3/4
❌ Crickets: F1 = 0.67 · Olive shaker: F1 = 0.33 · Magpies: F1 = 1.00
```

### 5. Caption phải nêu rõ subclass không kiểm chứng được

Khi caption nhắc subclass trên DataSED, mệnh đề "nhưng DataSED không có subclass
ground truth cho khoảng này" là **bắt buộc**, không phải tùy chọn. Có test kiểm
([taxonomy.md §7](../taxonomy.md)).

### 6. Cột `verifiable` trong `event_subclass_predictions`

Boolean, `FALSE` khi dataset không có subclass ground truth. Frontend phải hiển
thị cảnh báo, và metric không được tính precision/recall trên dòng đó.

## Consequences

### Tích cực

- Không có cách nào vô tình báo một con số không có cơ sở — ràng buộc nằm ở tầng
  schema (`verifiable`) và tầng caption (test), không chỉ ở quy ước.
- Parent-consistency là metric thật, đo được, không cần ground truth.
- Báo hai con số macro-F1 giữ được cả tính đầy đủ và tính diễn giải được.
- RQ4 vẫn trả lời được, chỉ là trả lời **một nửa** — và nói rõ nửa nào.

### Đánh đổi

- **RQ4 chỉ trả lời được trên DataSEC.** Câu hỏi thú vị hơn — subclass có chuyển
  được sang soundscape liên tục không — vẫn mở. Phải ghi vào Hạn chế.
- Hai con số macro-F1 làm bảng kết quả dài hơn và cần chú thích.
- Bốn subclass low-support gần như không đóng góp gì cho kết luận, dù vẫn phải
  train và báo cáo.
- `Thunder` chỉ có 26 file trong khi `Gunshot` có 141 — ngay trong node gộp quan
  trọng nhất đã có lệch 5.4:1, nên subclass head ở node này cũng sẽ lệch.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| **Gán nhãn subclass cho một tập con DataSED** | Đúng về khoa học nhưng vượt ngân sách 8 tuần, và mâu thuẫn với quyết định không tổ chức gán nhãn ([ADR-0001](ADR-0001-scope-and-datasets.md)). Ghi vào Hướng phát triển |
| **Báo subclass accuracy trên DataSED bằng cách coi coarse là proxy** | Không có cơ sở. Coarse đúng không nói gì về subclass đúng |
| **Bỏ hẳn subclass head** | Mất RQ4 và mất một phần đóng góp; DataSEC có hierarchy sẵn nên không tận dụng là lãng phí |
| **Gộp 4 subclass nhỏ vào "other"** | Làm hỏng cấu trúc hierarchy, và "other" không có nghĩa âm học |
| **Chia 50/25/25 riêng cho subclass nhỏ** | Hai quy tắc split trong một dataset, khó tái lập và khó giải thích |

## 7. Đặc tả baseline "random" cho parent-consistency (bổ sung 2026-09-23)

Giải quyết mục đầu của "Evidence cần kiểm lại" ở trên. Codex nêu đúng: "random"
có ít nhất ba nghĩa (uniform trên 28 subclass, prior DataSEC, hay logits của head
chưa train) và không nghĩa nào tái lập được nếu chọn tuỳ ý.

### Chốt: uniform trên toàn bộ 28 subclass, không điều kiện theo coarse

Đây là baseline "không kỹ năng" đúng nghĩa — một head có trọng số ngẫu nhiên và
softmax gần đều sẽ xấp xỉ phân phối này trước khi học được gì. Hai lựa chọn kia
bị loại có lý do:

- **Prior DataSEC** không phải "không kỹ năng" — nó đã mã hoá thông tin thật về
  phân bố lớp (`voices`+`music` = 57.5%, ADR-0002), nên một head chỉ học prior
  cũng vượt qua baseline này. Dùng nó làm baseline sẽ che mất tín hiệu yếu thật.
- **Logits của head chưa train** phụ thuộc phân phối khởi tạo trọng số (Xavier,
  Kaiming, …) — không phải một đại lượng có công thức đóng, và "seed cố định"
  không đủ để tái lập nếu công thức khởi tạo đổi giữa các phiên bản PyTorch.

### Công thức đóng, không cần mô phỏng Monte Carlo

Với mỗi item DataSED có coarse label (ground truth, vì D1 dùng để đo *trước khi*
có prediction thật), nếu coarse đó thuộc 10 nhóm có subclass với $k_c$ lớp con,
xác suất trúng ngẫu nhiên khi vẽ đều trên 28 lớp là:

$$P(\text{parent-consistent} \mid \text{coarse} = c) = \frac{k_c}{28}$$

Baseline là trung bình có trọng số theo tần suất coarse thật trên tập đang đo:

$$\text{baseline} = \frac{1}{N}\sum_{i=1}^{N} \frac{k_{c_i}}{28}$$

chỉ tính trên $N$ item có coarse thuộc 10 nhóm có subclass — 12 coarse còn lại
không có khái niệm "subclass đúng" nên bị loại khỏi mẫu số, giống hệt cách
`ignore_index=-1` loại chúng khỏi loss huấn luyện
([`ml/datasets/datasec.py`](../../ml/datasets/datasec.py)).

Đây là một **giá trị kỳ vọng đóng**, không phải kết quả mô phỏng — không cần
seed, không có phương sai giữa các lần chạy. Generator chỉ cần: với mỗi coarse
$c$, tra `len(taxonomy.classes[c].subclasses) / 28`, rồi lấy trung bình trên tập
item đang đánh giá.

### Phạm vi

- **Dataset:** DataSED — đúng nơi ADR-0006 §2 áp dụng parent-consistency.
- **Coarse dùng để tra $k_c$:** nhãn coarse **thật** (ground truth annotation),
  không phải coarse do SED phát hiện — vì baseline đo "không có kỹ năng ở tầng
  subclass", cô lập khỏi sai số của tầng coarse. Khi có prediction thật (sau D1),
  báo cáo song song hai con số: baseline dùng coarse thật, và baseline dùng
  coarse **do SED phát hiện** — chênh lệch giữa hai con số đo lỗi lan truyền từ
  tầng coarse, một quan sát tự nó có giá trị.
- **Đơn vị đếm:** theo **event** (một khoảng annotation), không theo frame — khớp
  với cách `event_subclass_predictions` được định nghĩa ở §2/§6.

### Nghiệm thu

```
.venv/Scripts/python.exe -m scripts.report_run --random-baseline datased
```
sinh `docs/measurements/parent_consistency_random_baseline_<YYYYMMDD>.md` có:
bảng $k_c$ cho 10 nhóm, số item mỗi coarse trên DataSED, baseline tổng, và ghi rõ
12 coarse không subclass bị loại khỏi mẫu số kèm số lượng bị loại.

## Evidence cần kiểm lại

- [ ] Parent-consistency rate của một model chưa train (random) là bao nhiêu —
      cần baseline để biết số đo có ý nghĩa.
- [ ] Phân bố subclass prediction trên DataSED có lệch theo tiên nghiệm DataSEC
      không (dấu hiệu model chỉ học prior chứ không học âm thanh).
- [ ] Với `n_test = 3`, có nên gộp dev vào test cho riêng các node này không —
      và nếu có thì ảnh hưởng gì tới tính độc lập của đánh giá.
