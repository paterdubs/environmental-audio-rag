# evaluation_protocol.md — Giao thức đánh giá

## 1. Nguyên tắc

- Metric, threshold và post-processing được định nghĩa trước test run.
- Report macro và per-class; không dùng micro score che class yếu.
- Confidence interval bootstrap theo recording, không theo frame.
- Test chỉ chạy khi config và checkpoint đã đóng băng.
- Mỗi bảng kết quả gắn run ID, split hash và taxonomy hash.

## 2. DataSEC classification

### Primary

- Macro F1 trên 22 coarse class.
- Balanced accuracy.
- Per-class precision, recall, F1.

### Secondary

- Subclass macro F1 trên các node có subclass.
- Hierarchical consistency: subclass prediction phải thuộc coarse parent.
- Expected calibration error và reliability plot.

## 3. DataSED SED

### Primary benchmark

DataSED polyphonic, 21 class.

- PSDS theo hai operating scenarios được đóng băng trong config.
- Event-based macro F1 với onset/offset collars công bố trong report.
- Segment-based macro F1 tại segment length cố định.

### Secondary benchmark

DataSED monophonic, 22 class:

- Cùng metric và post-processing.
- Không so trực tiếp score polyphonic và monophonic như cùng task.

### Error analysis

- Class confusion.
- Insertion, deletion, fragmentation, merging.
- Hiệu năng theo event duration, polyphony và confidence.
- Chênh lệch pretraining DataSEC vs no-pretraining.

## 4. Grounded caption

Caption được đánh giá so với event timeline, không cần reference prose.

| Metric | Ý nghĩa |
|---|---|
| Event precision | Tỷ lệ event được nhắc có trong timeline |
| Event recall | Tỷ lệ event timeline được nhắc trong caption |
| Hallucination rate | Event mention không có bằng chứng |
| Omission rate | Event có bằng chứng nhưng không được nhắc |
| Temporal order accuracy | Thứ tự mention khớp onset |
| Coverage by evidence | Tỷ lệ mention liên kết được event ID |

N-gram metric chỉ là phụ vì không có một câu diễn đạt duy nhất.

## 5. Retrieval/RAG

Tập query gồm bốn nhóm:

1. Single-class retrieval.
2. Multi-class conjunction.
3. Temporal relation: A trước/sau B.
4. Duration/confidence + semantic description.

Metric:

- Recall@1, @5, @10.
- MRR.
- nDCG@10 khi có graded relevance.
- Filter exactness.
- Evidence precision.
- Unsupported-claim rate của answer.

So sánh:

```text
structured only
vector only
hybrid structured + vector
```

## 6. Ablation tối thiểu

- Không DataSEC pretraining vs có DataSEC pretraining.
- Global threshold vs per-class threshold.
- Caption template vs constrained learned captioner, nếu triển khai.
- Vector retrieval vs hybrid retrieval.
- Coarse-only vs hierarchical classifier trên DataSEC.

## 7. Model selection

- Checkpoint chọn bằng dev primary metric.
- Threshold và median filter học từ train/dev, không dùng test labels.
- Nếu nhiều seed, chọn config trước rồi report mean ± std của các seed đã định.
- Không chọn run tốt nhất theo test.

## 8. Báo cáo bắt buộc

- Dataset version và file counts thực tế.
- Split rule và hash.
- Model parameter count, input representation và training budget.
- Metric config đầy đủ.
- Per-class table.
- Failure cases đại diện, gồm false positive và false negative.
- Giới hạn: DataSED coarse labels không xác nhận subclass prediction.

