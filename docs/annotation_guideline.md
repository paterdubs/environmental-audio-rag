# annotation_guideline.md — Quy ước xử lý nhãn

## 1. Mục đích

Dự án dùng annotation công bố, không tổ chức chiến dịch gán nhãn mới. Tài liệu này quy định cách nhập, chuẩn hóa, kiểm lỗi và bảo toàn nhãn nguồn.

## 2. Nguồn chân lý

- Raw annotation từ archive là bất biến.
- Canonical annotation được sinh bằng script từ raw annotation và taxonomy mapping có version.
- Không sửa raw CSV, filename hoặc timestamps bằng tay.

## 3. Event contract

Mỗi event canonical cần:

```text
recording_id
source_dataset
source_label
canonical_class_id
onset_s
offset_s
label_mode
taxonomy_version
```

Ràng buộc:

- `0 <= onset_s < offset_s`.
- `offset_s <= recording_duration + tolerance`.
- Overlap hợp lệ ở polyphonic mode.
- Monophonic và polyphonic annotation không được trộn trong cùng evaluation run.

## 4. Label modes

### Polyphonic

Giữ mọi target event được annotate dù chồng lấp. Đây là benchmark chính.

### Monophonic

Chỉ giữ nguồn chiếm ưu thế theo annotation công bố. Đây là benchmark phụ; không diễn giải là ground truth đầy đủ của soundscape.

## 5. Combined classes

Không nghe rồi tách thủ công:

- `sirens_and_alarms`
- `thunder_fireworks_gunshot`
- Các machinery/transport coarse classes khác

DataSEC subclass label có thể huấn luyện classifier riêng, nhưng prediction không thay thế DataSED ground truth.

## 6. Boundary handling

- Giữ onset/offset source với độ chính xác ban đầu.
- Khi rasterize, dùng một hàm chung cho train và evaluation.
- Event cắt qua window được clip vào window nhưng giữ source event ID.
- Event chạm ranh giới không được nhân đôi khi stitch prediction.

## 7. QA verdict

| Verdict | Ý nghĩa | Hành động |
|---|---|---|
| `pass` | File và annotation hợp contract | Giữ |
| `quarantine` | Cần xem thêm, chưa dùng train/eval | Tách khỏi split |
| `exclude_corrupt` | Audio/CSV không đọc được | Loại, ghi reason |
| `exclude_invalid_time` | Timestamp không thể sửa bằng quy tắc xác định | Loại event/file theo policy |
| `exclude_duplicate` | Bản sao thuộc group khác | Giữ một representative theo rule |

Không có verdict “nhãn nghe không đúng” trong pipeline tự động. Trường hợp nghi ngờ được ghi failure analysis, không sửa test tùy ý.

## 8. Manual audit nhỏ

Nếu cần audit:

- Sample theo class, label mode và duration quantile.
- Người nghe không xem prediction model.
- Chỉ đánh giá chất lượng dataset; không dùng kết quả audit để chọn model.
- Báo tỷ lệ và uncertainty, không suy rộng quá sample.

## 9. Caption reference

Reference caption được sinh xác định từ ground-truth timeline cho sanity check. Nó không phải caption tự nhiên do người gán và không dùng metric n-gram làm kết luận chính.

