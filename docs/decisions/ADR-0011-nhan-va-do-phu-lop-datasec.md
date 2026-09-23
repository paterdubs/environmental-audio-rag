# ADR-0011 — Nguồn nhãn và tập lớp của cổng D4 khi áp cho DataSEC

**Status:** Accepted
**Date:** 2026-09-23

## Context

[ADR-0010](ADR-0010-dinh-danh-datasec-va-cong-freeze.md) gỡ hai chặn định danh.
Còn hai chặn nữa, cả hai đều nằm trong kiểm 4 của cổng D4 ("mọi class có mặt ở
mọi split"), và cả hai đều **không** làm chương trình vỡ — chúng làm nó trả lời sai.

### Chặn A — DataSEC không có file annotation

`load_labels` đọc `data/annotations/<dataset>_<mode>_events.csv`. Thư mục đó chỉ
có `datased_polyphonic_events.csv` và `datased_monophonic_events.csv`. Nhãn
DataSEC nằm ở **cây thư mục**: `DATASEC/<Coarse>/[<Subclass>/]<tên>.wav`.

Logic suy nhãn từ đường dẫn đã tồn tại — `_path_labels` trong
`ml/datasets/datasec.py`. Nhưng module đó `import torch` ở cấp module, và nhật ký
23/09 ghi lại rằng chính môi trường này đã một lần không khởi tạo được torch
(`0x8007000e`). Một cổng dữ liệu phụ thuộc vào thứ có thể không nạp được là một
cổng có thể bị bỏ qua đúng lúc cần nó nhất.

### Chặn B — kiểm phủ đọc cứng 21 lớp

`expected = taxonomy.polyphonic_class_ids` → **21**. Con số đó đúng cho DataSED:
`wind_turbine` nằm ngoài nhãn polyphonic ([ADR-0001](ADR-0001-scope-and-datasets.md)),
nên đòi nó sẽ làm trượt một split đúng. Nhưng DataSEC là dataset **phân loại** với
**22** lớp coarse, và mọi lớp đều có clip. Dùng 21 ở đây sẽ báo thiếu
`wind_turbine` ở cả ba split, mãi mãi.

Câu hỏi thật hơn: có nên đòi cả **28 subclass** có mặt ở mọi split không? Đòi mà
dữ liệu không cho phép thì cổng sẽ ép người ta hoặc nới ràng buộc rò rỉ, hoặc bỏ
split — cả hai đều tệ hơn việc không đòi.

### Đo trước khi chốt

Trên 5,048 clip DataSEC, sau khi loại 130 dòng `datasec:` của `exclusions.csv`:

| | |
|---|---:|
| Clip còn lại | **4,918** |
| Số `leakage_group` | 4,457 |
| Cụm lớn nhất | **315 file (6.4%)** — không phải 326, vì loại trừ đã lấy đi một phần |
| Lớp coarse có mặt | **22 / 22** |
| Subclass có mặt | **28 / 28** |
| Lớp coarse kẹt trong < 3 `leakage_group` | **0 / 22** |
| Subclass kẹt trong < 3 `leakage_group` | **0 / 28** |

Lớp coarse nhỏ nhất `cat_fights_and_moans` 48 file trải trên 44 nhóm; subclass nhỏ
nhất `magpies` 19 file trải trên 16 nhóm. Không lớp nào **bị buộc** phải vắng mặt
ở một split.

## Decision

### 1. Nguồn nhãn được khai báo, không đoán theo dataset

`DatasetKeys.label_source`: `events_csv` cho DataSED, `directory` cho DataSEC.
`load_labels` rẽ theo khai báo đó.

### 2. Logic suy nhãn tách sang `ml/dataops/datasec_labels.py`, không phụ thuộc torch

`ml/dataops/` là vùng torch-free và phải giữ nguyên như vậy. `ml/datasets/datasec.py`
giờ import lại từ đó nên không có hai bản logic. Thêm một test chạy cổng trong
tiến trình con và khẳng định `torch` **không** nằm trong `sys.modules`.

### 3. Tập lớp của kiểm phủ khai báo theo dataset

| Dataset | Tập lớp | Số |
|---|---|---:|
| DataSED | `polyphonic_class_ids` | 21 |
| DataSEC | 22 coarse **+** 28 subclass | **50** |

Đòi cả hai mức cho DataSEC là **khả thi theo số đo**, không phải theo kỳ vọng: mọi
lớp ở cả hai mức đều trải trên ≥ 16 `leakage_group`. Một subclass biến mất khỏi một
split sẽ là khiếm khuyết thật của bộ chia, không phải hệ quả bắt buộc của dữ liệu —
nên cổng được phép chặn.

### 4. "Có mặt" và "đủ mẫu để đo" là hai chuyện khác nhau

Cổng chỉ bảo đảm lớp **không biến mất**. Nó không nói gì về độ tin cậy thống kê.
`magpies` 19 file với 60/20/20 cho test khoảng 4 mẫu — vẫn phải báo **số tuyệt
đối** theo [ADR-0006 §4](ADR-0006-danh-gia-subclass.md), và không được tuyên bố
cải thiện per-subclass ở mức đó.

### 5. `choices=("datased",)` chỉ được nới theo từng script, khi pipeline của nó chạy thật

`create_splits`, `check_leakage`, `freeze_split` đều còn khoá ở `datased`. Nới cả
ba cùng lúc sẽ tạo ra lệnh chạy được nửa vời — và một lệnh chạy được nửa vời là
cách dễ nhất để ai đó tin rằng cổng đã chạy.

## Consequences

### Tích cực

- Cổng D4 của DataSEC đọc được nhãn thật, và kiểm đúng 50 nhãn thay vì 21.
- Cổng dữ liệu không còn phụ thuộc torch, có test giữ tính chất đó.
- Câu hỏi khả thi của A1 đã có nửa câu trả lời: cụm lớn nhất **315 / 4,918 = 6.4%**
  nằm gọn trong bất kỳ split nào ở cả 60/20/20 lẫn 70/15/15.

### Đánh đổi

- Kiểm phủ của DataSEC nghiêm hơn của DataSED (50 nhãn so với 21). Nếu bộ chia
  không đặt nổi một subclass 19 file vào cả ba split, cổng sẽ trượt — và đó là
  điều mong muốn, nhưng sẽ tốn một vòng chỉnh.
- Suy nhãn từ đường dẫn tin vào cây thư mục của archive. Nếu cây đổi, nhãn đổi im
  lặng. Đã chặn bằng test đối chiếu inventory thật với đúng 50 nhãn của taxonomy.

## Alternatives considered

- **Sinh `datasec_events.csv` từ cây thư mục.** Tạo một artifact trung gian có thể
  lệch với cây thư mục mà không ai biết, chỉ để chiều một chữ ký hàm.
- **Chỉ đòi 22 coarse, bỏ subclass.** An toàn hơn nhưng bỏ mất một khiếm khuyết
  thật; số đo cho thấy đòi cả 28 là khả thi, nên không có lý do bỏ.
- **Đòi subclass nhưng cho phép vắng ở test.** Chính là cách im lặng đánh mất
  RQ4 — subclass vắng ở test thì không đo được gì về subclass.
- **Import `build_datasec_manifest` từ `ml/datasets/datasec.py`.** Ngắn nhất, nhưng
  kéo torch vào cổng dữ liệu.

## Evidence cần kiểm lại

- Sau khi split DataSEC sinh thật: `magpies`, `crickets`, `olive_shaker`,
  `lawn_mower` có đúng mặt ở cả ba split không, và số tuyệt đối ở test là bao nhiêu.
- 130 clip bị loại có tập trung vào vài lớp không — nếu có thì phân bố lớp của
  corpus pretraining lệch đi và phải nêu ở Hạn chế.
