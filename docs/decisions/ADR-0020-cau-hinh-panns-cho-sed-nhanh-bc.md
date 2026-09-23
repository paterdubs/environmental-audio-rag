# ADR-0020 — Cấu hình PANNs cho `train_sed.py`, nhánh B/C (W3)

**Status:** Accepted
**Date:** 2026-09-23

## Context

D1–D6 (tuần 2/8, DataSEC classifier) sắp xong. Việc tiếp theo trên đường găng
([PLAN.md](../PLAN.md) W3) là ba nhánh SED trên DataSED — nhánh **A** (scratch,
đã có số: frame macro-F1 0.359448) và nhánh **B**/**C** (PANNs CNN14, ADR-0002).

Rà `scripts/train_sed.py` và `ml/datasets/features.py` trước khi giao Codex thì
thấy **bốn** chỗ chưa đủ đặc tả — đúng mẫu hình đã lặp lại nhiều lần trong tuần
này (C1, D4, D1): code hiện tại *chạy được* cho nhánh A, nhưng không có đường
nào cắm PANNs vào mà không tự đoán:

1. `SoundEventDetector(classes=len(class_ids))` trong `main()` **không truyền
   `encoder=`** — luôn dùng `AudioEncoder()` mặc định. Không có cách chọn
   `PannsCNN14Encoder` qua CLI.
2. Script đọc cứng `datased_logmel_v1.csv` (16 kHz, 50 fps). PANNs cần
   `logmel_panns_v1` (32 kHz, **100 fps** — đo thật ở B3, không phải 50 fps
   suy diễn từ nhánh A).
3. `SedFeatureDataset(frame_rate=50.0, window_frames=500, hop_frames=250)` —
   ba tham số này gắn với 50 fps. Đổi feature set mà không đổi cả ba sẽ làm
   target onset/offset tính sai theo giây, hoặc window ngắn hơn C2 đã đo VRAM.
4. Nhánh B (AudioSet→DataSED trực tiếp, không qua DataSEC) và nhánh C
   (AudioSet→DataSEC→DataSED, dùng checkpoint D1) cần **hai nguồn trọng số
   encoder khác nhau và khả năng cần hai chuẩn hoá input khác nhau** — chưa có
   quyết định nào phân biệt hai đường nạp này.

Không quyết định trước, Codex sẽ hoặc tự đoán (rủi ro lặp lại lỗi
`safe_batch_size` sai 12 lần, hoặc lỗi shape như C1 từng gặp), hoặc dừng lại
hỏi — cả hai đều tốn một vòng round-trip có thể tránh được.

## Decision

### 1. `--encoder {audio,panns}`, mặc định `audio` (giữ nhánh A không đổi)

```
--encoder audio   → SoundEventDetector(classes)               # nhánh A, hiện trạng
--encoder panns   → SoundEventDetector(classes, encoder=PannsCNN14Encoder(...))
```

Khi `--encoder panns`, bắt buộc phải có đúng một trong hai cờ nạp trọng số
(script raise lỗi rõ nếu thiếu cả hai hoặc có cả hai):

```
--audioset-checkpoint <path>       # nhánh B
--datasec-checkpoint <path>        # nhánh C — checkpoint D1 (best.pt)
```

### 2. Feature set đi theo encoder, không phải cờ riêng

`--encoder panns` tự động dùng `logmel_panns_v1` (`data/features/datased/logmel_panns_v1`,
manifest `datased_logmel_panns_v1.csv`) và `frame_rate=100.0`; `--encoder audio`
giữ `logmel_v1`/50.0 như hiện tại. Không thêm `--feature-set` riêng — hai thứ
luôn đi cùng nhau trong repo này (ADR-0002 §Đánh đổi), tách rời chỉ tạo ra tổ
hợp không hợp lệ (vd `audio` encoder + feature 32 kHz).

### 3. Cùng độ dài cửa sổ theo **giây**, không phải theo frame, giữa các nhánh

C2 đã đo VRAM CNN14 an toàn ở cửa sổ 10 s (batch 24). ADR-0002 §5 đòi "cùng
training budget" giữa ba nhánh — nghĩa là cùng độ dài cửa sổ/hop **theo giây**,
không phải cùng số frame.

**Sửa lỗi 2026-09-24:** bản đầu ADR này ghi nhầm hop hiện tại của nhánh A là
250 frame (5 s). Đọc lại `SedTrainingConfig` thật: `hop_frames` mặc định là
**500**, bằng `window_frames` — tức nhánh A hiện chạy cửa sổ **10 s / hop 10 s
(không overlap)**, không phải 5 s. Bảng dưới sửa theo số thật:

| Encoder | frame_rate | window_frames (10 s) | hop_frames (10 s, không overlap) |
|---|---:|---:|---:|
| `audio` (nhánh A) | 50 | 500 (hiện trạng) | 500 (hiện trạng) |
| `panns` (nhánh B/C) | 100 | **1000** | **1000** |

Batch size cho `--encoder panns` mặc định **24** (số đo thật C2 ở 10 s), không
phải batch 8 hiện tại của nhánh A.

### 4. Chuẩn hoá input — khác nhau có chủ đích giữa B và C

**Nhánh C không cần `--normalization` riêng.** `load_classifier_encoder` nạp
`state_dict()` đầy đủ của `encoder.*`, và `input_mean`/`input_std` là
`register_buffer` nên **nằm trong chính state_dict đó** — nạp checkpoint D1 tự
động mang theo chuẩn hoá DataSEC-train đã tính ở F1. Đây là điều đúng: trọng số
`conv_block1…6` của checkpoint D1 đã được tối ưu cho phân bố input **đã chuẩn
hoá theo DataSEC**, nên giữ nguyên chuẩn hoá đó khi fine-tune tiếp là nhất
quán — tự tính lại thống kê DataSED và ghi đè sẽ đẩy input ra khỏi vùng hoạt
động mà các khối tích chập "quen". **Không truyền `normalization_path` khi dùng
`--datasec-checkpoint`** — nếu truyền, giá trị đó bị `load_classifier_encoder`
ghi đè ngay sau đó nên vô nghĩa, chỉ gây hiểu lầm khi đọc log.

**Nhánh B cần chuẩn hoá riêng, tính từ train DataSED.** `--audioset-checkpoint`
chỉ mang `conv_block1…6` gốc AudioSet, không mang thống kê corpus nào của dự án
này. Dùng chuẩn hoá DataSEC ở đây là tuỳ tiện (nhánh B chưa từng thấy DataSEC).
Cần một task mới sinh `data/manifests/datased_logmel_panns_v1_train_normalization.npz`
từ **train split DataSED** (giống hệt cách F1 làm cho DataSEC, cùng script nếu
tổng quát hoá được tham số dataset) — B2 đã trích `logmel_panns_v1` cho cả 717
file DataSED nên không còn phụ thuộc gì. Gọi tên task này **F2**.

### 5. Manifest ghi đủ để phân biệt ba nhánh khi đọc lại

Thêm vào `manifest.config`: `encoder_type` (`audio`/`panns`), `feature_set`,
`frame_rate`, `window_frames`, `hop_frames`, `weight_source`
(`"scratch"`/`"audioset"`/`"datasec:<run_id>"`), `checkpoint_sha256`. Không sửa
`contracts/run_manifest.schema.json` — theo đúng tiền lệ D1 (`config` là
mapping tự do).

### 6. Lưu prediction NPZ (PLAN.md task 3.4) — vá cùng lúc, không phải việc riêng

Rà tiếp một bước sau train thì thấy `ml/evaluation/predictions.py` đã có contract
`PredictionArtifact`/`save_predictions` đầy đủ (schema `prediction-artifact-v1`,
test pass từ tuần trước — nhật ký "W3: prediction, post-processing"), và
`create_run_directory` đã tạo sẵn thư mục con `predictions/` cho **mọi** run —
nhưng **chưa ai từng ghi gì vào đó**. Xác nhận: cả hai run `sed_polyphonic_*`
(nhánh A) đã train xong tuần trước có `predictions/` rỗng.

Nguyên nhân gốc: `SedFeatureDataset.__getitem__` trả về `(features, target,
valid)` — **không có `recording_id`/`start_frame`** dù `SedWindow` (dataclass
nội bộ) có đủ hai trường này. `run_epoch` (`ml/training/sed.py`) vì vậy chỉ
tính được metric tổng hợp, không thể ghép logits về đúng recording/thời điểm.
Đây là chặn cho **cả ba nhánh**, không riêng B/C — nên vá một lần, không phải
việc lặp lại mỗi nhánh.

**Quyết định:** không đổi chữ ký `__getitem__` (sẽ vỡ `collate_fn` mặc định vì
`recording_id` là `str`, khó ghép batch cùng tensor). Thay vào đó, thêm hàm mới
`collect_predictions(model, loader, device, frame_rate) -> PredictionArtifact`
trong `ml/training/sed.py`, đọc trực tiếp `loader.dataset.windows` theo **đúng
thứ tự index** (chỉ hợp lệ khi `shuffle=False` — đúng thực trạng của
`validation`/`test` loader trong `train_sed.py`, không hợp lệ cho `train`
loader, không cần thiết cho `train`). `frame_offsets_s = start_frame /
frame_rate`.

**⚠️ Namespace khác nhau giữa hai tầng — phải ánh xạ tường minh, không đổi tên
cột split CSV.** Cột `split` trong `data/splits/datased_polyphonic.csv` và dict
`loaders` của `train_sed.py` dùng `"validation"`; nhưng
`PredictionArtifact.split` (`ml/evaluation/predictions.py`) và toàn bộ
`ml/postprocessing/calibration.py` (`sweep_*`, `build_postproc_artifact`,
`calibrated_on`) chỉ chấp nhận **literal `"dev"`** — `validate_predictions`
raise `ValueError` với bất kỳ giá trị nào khác `{"dev", "test"}`. Đây là đúng
mẫu lỗi lệch namespace đã gặp nhiều lần trong dự án (`clip_id`/`file_id`,
`recording_id`) — khác ở chỗ lần này có guard raise sẵn nên sẽ lộ ngay, không
âm thầm sai như các lần trước. Khi gọi `save_predictions`, truyền
`split="dev"` cho loader `"validation"` và `split="test"` cho loader `"test"`
— **không** đổi tên cột `split` trong CSV/`train_sed.py` để khớp theo chiều
ngược lại, vì "validation" đã lan ra nhiều chỗ khác (`build_loaders`,
`report_split.py`, mọi manifest DataSEC/DataSED). Ghi
`predictions/dev.npz` và `predictions/test.npz` (đúng tên PLAN.md §2.3 dùng).

**Guard bắt buộc:** raise rõ nếu `isinstance(loader.sampler, ...)` không phải
sequential hoặc `shuffle=True` được truyền nhầm cho loader dùng để dump
prediction — sai thứ tự sẽ ghép logits sai recording một cách im lặng, đúng
lớp lỗi mà `check_leakage`/registry đã nhiều lần bắt được trong dự án này.

## Consequences

### Tích cực
- Ba nhánh dùng chung một script, khác nhau đúng ba cờ (`--encoder`,
  `--audioset-checkpoint` hoặc `--datasec-checkpoint`) — không phân nhánh code
  trùng lặp.
- Chuẩn hoá đúng theo từng nguồn trọng số, tránh lặp lại lớp lỗi "chuẩn hoá sai
  ngữ cảnh" đã thấy ở fingerprint (ADR-0007) và bn0 (ADR-0018).
- `C − B` vẫn so sánh được công bằng: cùng 10 s window thật, cùng batch, chỉ
  khác nguồn trọng số ban đầu — đúng yêu cầu ADR-0002 §5.

### Đánh đổi
- Thêm một task mới (F2) trước khi nhánh B chạy được — không tránh được, vì
  chuẩn hoá DataSED-train là dữ kiện chưa từng đo.
- Batch 24 ở 10 s cho CNN14 (81M tham số) có thể chậm hơn nhánh A (CNN nhỏ,
  batch 8) trên cùng số epoch — chấp nhận, đã đổi lấy transfer learning thật.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| Nhánh C tự tính lại chuẩn hoá DataSED-train | Đẩy input ra khỏi phân bố các khối tích chập đã pretrain quen — giống lỗi "chuẩn hoá không nhất quán" ADR-0007 từng sửa, chỉ khác chỗ xảy ra |
| Giữ window 500 frame cho cả `panns` (đổi nghĩa thành 5 s) | Vi phạm "cùng training budget" ADR-0002 §5 — nhánh B/C thấy ngữ cảnh ngắn hơn nhánh A một cách âm thầm |
| Thêm `--feature-set` độc lập với `--encoder` | Cho phép tổ hợp không hợp lệ (audio encoder + 32kHz feature) mà không ai kiểm tra tới khi crash giữa chừng |

## Evidence cần kiểm lại

- [ ] `--encoder panns --audioset-checkpoint ...` (nhánh B) chạy 1 epoch không
      lỗi shape, VRAM trong ngưỡng C2 đã đo.
- [ ] `--encoder panns --datasec-checkpoint ml/runs/classifier_datasec_20260923T121808Z/checkpoints/best.pt`
      (nhánh C) — xác nhận bằng log rằng `input_mean`/`input_std` sau khi nạp
      khác `zeros`/`ones` mặc định (tức chuẩn hoá DataSEC đã thực sự đi kèm).
- [ ] So sánh thời gian train thực tế nhánh A vs B/C — cập nhật ước lượng giờ
      của PLAN.md W3 nếu lệch nhiều.
