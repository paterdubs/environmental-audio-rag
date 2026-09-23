# ADR-0019 — Viết lại pipeline huấn luyện D1: `scripts/train_classifier.py` chưa từng chạy được

**Status:** Accepted
**Date:** 2026-09-23

## Context

Rà trước khi Codex chạm D1 (đúng vai "suy luận, lên kế hoạch" ở
[AGENT_SYNC.md §0](../AGENT_SYNC.md)): `scripts/train_classifier.py` **chưa
từng chạy thành công một lần nào** kể từ commit đầu tiên (`c9ccbc6`, scaffold).

Bằng chứng — hai file nó đọc **chưa từng tồn tại** trong lịch sử git:

```
data/manifests/datasec_clips.csv   — 0 commit nào tạo ra file này
data/splits/datasec.csv            — 0 commit nào tạo ra file này
```

`ml/runs/` chỉ có hai run SED (`sed_polyphonic_202609221151{37,40}Z`), không có
run classifier nào — khớp với việc script chưa bao giờ chạy được, không ai
phát hiện vì DataSEC training chưa ai thử tới tuần này.

Ngoài đường dẫn sai, còn bốn lớp không tương thích khác, đủ sâu để không thể vá:

| | Script hiện tại | Cần cho D1 |
|---|---|---|
| Model | `AudioClassifier` (`AudioEncoder`, 1 head 22-way) | `HierarchicalAudioClassifier` (`PannsCNN14Encoder`, 2 head) |
| Dataset | `ClassificationFeatureDataset`, trả `(x, label)` | `DataSECFeatureDataset`, trả `(x, coarse, subclass)` |
| Split | `data/splits/datasec.csv`, khoá `clip_id` | `data/splits/datasec_classification.csv` (đã đóng băng), khoá `file_id` (ADR-0010) |
| Feature | `datasec_logmel_v1` (16 kHz) | `datasec_logmel_panns_v1` (32 kHz, B2 đã trích) |
| Vòng lặp train | `run_epoch`/`train_classifier` — `cross_entropy` một head | cần `hierarchical_loss` ba thành phần (ADR-0016) |

`AudioClassifier`/`AudioEncoder` **không ứng với nhánh nào** trong ba nhánh
A/B/C của [ADR-0002](ADR-0002-encoder-va-nhanh-transfer.md): nhánh A train
thẳng trên DataSED (random init), không có bước "DataSEC classifier" nào cả.
Chỉ nhánh C cần D1, và nhánh C dùng CNN14. Giữ đường `AudioClassifier` trong
script này là giữ code chết, không ai gọi tới.

## Decision

### 1. Viết lại hoàn toàn `scripts/train_classifier.py`, không giữ đường cũ

Không thêm cờ `--encoder {baseline,cnn14}` để giữ tương thích ngược — không có
gì để tương thích ngược với, vì đường cũ chưa từng chạy được. Script mới chỉ
làm một việc: huấn luyện `HierarchicalAudioClassifier(PannsCNN14Encoder(), ...)`
trên DataSEC, đúng bước giữa của nhánh C.

### 2. Nạp dữ liệu qua registry, không lặp lại lỗi namespace

```python
from ml.dataops.registry import keys_for
keys = keys_for("datasec")   # item_col = "file_id"
splits = pd.read_csv(ROOT / "data" / "splits" / "datasec_classification.csv")
features = pd.read_csv(ROOT / "data" / "manifests" / "datasec_logmel_panns_v1.csv")
# join theo file_id, KHÔNG phải clip_id
```

Dùng thẳng `DataSECLabelSpace.from_taxonomy`, `DataSECFeatureDataset`,
`make_class_balanced_sampler` đã có trong `ml/datasets/datasec.py` — không viết
lại logic label/sampler.

### 3. Chuẩn hoá thay `bn0` — **đã có sẵn**, dùng thẳng, không viết thêm lớp bọc

Bản nháp đầu của ADR này đề xuất một `NormalizedPannsEncoder` bọc ngoài. Khi
viết thì F1 đã xong trước và Codex chọn cách gọn hơn: buffer `input_mean` /
`input_std` **ngay trong** `PannsCNN14Encoder`
(`ml/models/panns.py::set_input_normalization`, `normalization_path` ở
constructor). Cách này tốt hơn đề xuất ban đầu — không thêm một lớp `nn.Module`
trung gian, chuẩn hoá áp dụng ngay trong `forward()` của chính encoder, buffer
tự vào `state_dict()` với tiền tố rõ ràng (`input_mean`, `input_std`), và test
đã có (`test_encoder_loads_train_only_per_mel_normalization`, 6/6 pass).
**Rút đề xuất `NormalizedPannsEncoder` — không viết thêm.**

Thứ tự dựng model trong script D1:
```python
encoder = PannsCNN14Encoder(normalization_path=stats_path)   # bn0 đã gắn ở đây
report = encoder.load_audioset_pretrained(checkpoint_path)   # trọng số AudioSet
model = HierarchicalAudioClassifier(encoder, num_coarse=22, num_subclass=28)
```
Gọi `load_audioset_pretrained` **sau** khi tạo encoder với `normalization_path`
— thứ tự không quan trọng ở đây vì `load_audioset_pretrained` chỉ nạp
`self.blocks`, không đụng buffer chuẩn hoá.

### 4. Vòng lặp huấn luyện mới trong `ml/training/classification.py`

Thêm (không sửa hàm cũ — hàm cũ dành cho model một head, nếu còn nơi nào gọi):

```python
def run_hierarchical_epoch(
    model: HierarchicalAudioClassifier, loader: DataLoader, *,
    device, coarse_weight: Tensor, family_mask: Tensor,
    optimizer, scaler, loss_weights: HierarchicalLossWeights,
) -> dict:
    """Tiêu thụ batch 3 phần tử (x, coarse, subclass). Trả về dict có
    coarse_macro_f1, subclass_macro_f1_all, subclass_macro_f1_supported (n>=10,
    ADR-0006 §3), parent_consistency_rate, và ba giá trị loss thành phần."""

def train_hierarchical_classifier(...) -> tuple[list[dict], Path]:
    """Giống train_classifier nhưng chọn best checkpoint theo
    validation coarse_macro_f1 — coarse là mục tiêu chính, subclass là chỉ báo
    (ADR-0006 §1: "Metric subclass chỉ báo trên DataSEC test")."""
```

`coarse_weight` dùng `inverse_frequency_weights` đã có. `family_mask` dùng
`build_family_mask` đã có (`ml/models/hierarchical.py`).

### 5. Run manifest: `primary_metric = "coarse_macro_f1"`

```python
manifest["config"]["checkpoint_sha256"] = report_hash    # không sửa schema (ADR trước)
manifest["primary_metric"] = "coarse_macro_f1"
```
`metrics.json` ghi cả `coarse_macro_f1`, hai `subclass_macro_f1_*`, và
`parent_consistency_rate` trên **cả dev lẫn test** — D3/D4/D5 đọc lại từ đây,
không train riêng cho từng báo cáo.

## Nghiệm thu

```bash
.venv/Scripts/python.exe -m scripts.train_classifier --epochs 12 --device cuda
```
chạy hết không lỗi, sinh `ml/runs/classifier_datasec_<...>/metrics.json` có đủ
4 chỉ số trên. `pytest -q` phải có test cho `run_hierarchical_epoch` với dữ
liệu giả lập nhỏ (không cần GPU thật) — dựng batch tay, kiểm shape/loss giảm
qua vài bước gradient.

## Consequences

### Tích cực
- D1 giờ có đường chạy thật, không phải đoán từ một script chết từ đầu dự án.
- Chuẩn hoá thay `bn0` tái dùng được ở bước fine-tune SED sau, không phải viết
  lại lần hai.

### Đánh đổi
- Xoá hẳn đường `AudioClassifier`/`ClassificationFeatureDataset` khỏi script
  này. Nếu về sau cần một baseline DataSEC classifier "thuần" (không CNN14) để
  so sánh, phải viết script riêng — chấp nhận được vì ADR-0002 không định nghĩa
  nhánh nào cần nó.

## Alternatives considered

- **Vá script cũ bằng cách đổi tên file/cột.** Không đủ — vẫn còn sai model,
  sai dataset, sai vòng lặp train. Vá bốn lớp riêng biệt tốn công ngang viết lại
  và dễ bỏ sót một lớp.
- **Chuẩn hoá bn0 ở tầng dataset** (z-score ngay trong `DataSECFeatureDataset`).
  Loại vì encoder được tái sử dụng cho SED fine-tune sau — chuẩn hoá phải đi
  theo encoder, không đi theo dataset của riêng D1.

## Evidence cần kiểm lại

- [ ] Chọn best checkpoint theo `coarse_macro_f1` có bỏ sót trường hợp subclass
      tốt nhưng coarse trung bình không — nếu D4 cho thấy lệch nhau nhiều, có
      thể cần tiêu chí chọn kép.
