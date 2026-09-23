# ADR-0018 — Nạp một phần checkpoint PANNs AudioSet: chỉ conv_block, không faithful full CNN14

**Status:** Accepted
**Date:** 2026-09-23

## Context

Codex (Task F1) xác minh được nguồn checkpoint thật (Zenodo 3576403,
`Cnn14_mAP=0.431.pth`, MD5 `595633ac2d1cac7ef04ebf70e2fee4e4`, 1.4 GB) và phát
hiện một vấn đề sâu hơn việc tải mạng: **kiến trúc không khớp cấu trúc**.

Checkpoint gốc (từ source code chính thức) có các khối:

```
spectrogram_extractor, logmel_extractor, bn0,
conv_block1 … conv_block6, fc1, fc_audioset
```

`PannsCNN14Encoder` trong repo này **chỉ có** `blocks.0 … blocks.5`
(`ml/models/panns.py`). Khác biệt không phải chi tiết đặt tên — là khác biệt
thiết kế có chủ đích từ đầu, chỉ chưa ai đối chiếu tới khi có checkpoint thật:

| | PANNs gốc | Repo này |
|---|---|---|
| Input | waveform thô | log-mel đã trích sẵn (`ml/configs/features.yaml`) |
| `spectrogram_extractor` + `logmel_extractor` | có, bên trong model | không — nằm ngoài, ở tầng feature pipeline |
| `bn0` | batchnorm học được trên 64 mel band, áp ngay sau logmel | không có |
| `conv_block1…6` | có | có, tên khác (`blocks.0…5`) |
| `fc1` (2048→2048) + `fc_audioset` (2048→527) | có, đầu ra AudioSet gốc | không — thay bằng head của repo (`coarse_head`, `subclass_head`, …) |

Load `strict=True` cả checkpoint là không thể — không phải lỗi cấu hình, là hai
kiến trúc khác nhau ở phạm vi rộng hơn một khối.

## Decision

### 1. Giữ nguyên `PannsCNN14Encoder` tách khỏi tiền xử lý âm thanh

Không viết lại thành faithful full CNN14 (waveform→spectrogram→logmel→bn0→...).
Lý do quyết định, không chỉ tiện: mọi pipeline dữ liệu của dự án (feature cache
`.npy`, `ClassificationFeatureDataset`, `logmel_panns_v1` đã lên kế hoạch trích
ở B2) đều giả định log-mel được trích **trước**, ngoài model. Đổi sang mô hình
nhận waveform thô sẽ viết lại toàn bộ tầng dữ liệu ở tuần 2/8 — chi phí không
tương xứng lợi ích khi mục tiêu là transfer representation, không phải tái tạo
đúng byte pipeline gốc.

**Hệ quả phải ghi rõ trong báo cáo cuối:** đây không phải "PANNs CNN14" đúng
nguyên bản — là **các khối tích chập của CNN14** (`conv_block1…6`), nạp trọng
số AudioSet, ghép vào một tiền xử lý log-mel khác với `bn0` gốc. Gọi tên chính
xác trong luận văn: *"CNN14 convolutional blocks, AudioSet-pretrained, adapted
to externally-computed log-mel input"* — không viết tắt thành "PANNs CNN14"
trần trụi ở phần phương pháp.

### 2. Chỉ transplant `conv_block1…6`, bỏ qua phần còn lại có chủ đích

Ánh xạ khoá, dựa trên cấu trúc `_PannsConvBlock.layers` hiện tại
(`Conv2d, BatchNorm2d, ReLU, Conv2d, BatchNorm2d, ReLU`):

```
conv_block{N}.conv1.{weight}       -> blocks.{N-1}.layers.0.{weight}
conv_block{N}.bn1.{weight,bias,running_mean,running_var,num_batches_tracked}
                                    -> blocks.{N-1}.layers.1.{...}
conv_block{N}.conv2.{weight}       -> blocks.{N-1}.layers.3.{weight}
conv_block{N}.bn2.{...}            -> blocks.{N-1}.layers.4.{...}
```
với `N = 1..6`. `spectrogram_extractor`, `logmel_extractor`, `bn0`, `fc1`,
`fc_audioset` bị bỏ, có chủ đích — không phải thiếu sót.

**`strict` áp trên tập con đã ánh xạ, không phải cả checkpoint:** sau khi remap,
gọi `self.blocks.load_state_dict(remapped, strict=True)`. Nếu một tensor sau
remap lệch shape với `blocks` hiện tại (ví dụ do conv có `bias=False` ở repo
này nhưng checkpoint có bias) → raise rõ tên tensor, không nuốt lỗi bằng
`strict=False` toàn cục.

**Báo cáo tỷ lệ tham số thật đã transplant** (không phải giả định): số tensor
+ tổng tham số của `conv_block1…6` so với tổng checkpoint. Đây là bằng chứng
"transfer bao nhiêu phần trăm trọng số", cần cho phần Giới hạn của báo cáo.

### 3. Thiếu `bn0` — thay bằng chuẩn hoá thống kê corpus, không bỏ trống

`bn0` của PANNs là batchnorm học được trên phân bố log-mel của AudioSet, áp
ngay trước `conv_block1`. Thiếu nó nghĩa là input đưa vào các khối đã pretrain
có thể lệch phân bố mà chúng "quen". Không để trống — z-score hoá `logmel_panns_v1`
theo **thống kê của chính tập train DataSEC** (mean/std mỗi mel band, giống
tinh thần chuẩn hoá corpus đã dùng cho fingerprint T3, ADR-0007) trước khi đưa
vào `conv_block1`. Đây là một xấp xỉ, không phải `bn0` thật — ghi rõ là Hạn chế,
không phải giải pháp tương đương.

### 4. Nếu vẫn không tải xong sau khi resume: kích hoạt fallback ADR-0015 §3

`curl -C -` để resume từ 24,649,728 B đã có, không tải lại từ đầu. Thử tối đa
hai lần nữa. Không thành công → đổi tên nhánh B thành "CNN14-scratch", loại
khỏi `C − B` chính, ghi Hạn chế — đúng như ADR-0015 §3 đã định trước.

## Nghiệm thu

Codex triển khai `remap_audioset_state_dict` + `load_audioset_pretrained` (tên
gợi ý, không bắt buộc) trong `ml/models/panns.py`, cùng test:

- Từ dict giả lập đúng tên khoá gốc → `blocks.load_state_dict(strict=True)`
  không raise.
- Shape lệch cố ý ở một tensor → raise nêu đúng tên tensor.
- Tỷ lệ tham số transplant tính đúng (so bằng `sum(p.numel() ...)`).
- Sau khi có checkpoint thật: chạy lại, ghi tỷ lệ thật vào
  `docs/measurements/panns_checkpoint_20260923.md` (nối tiếp F1, không file mới).

## Consequences

### Tích cực
- Không phải viết lại tầng dữ liệu — giữ được toàn bộ pipeline `logmel_panns_v1`
  và `HierarchicalAudioClassifier`/`SoundEventDetector` đã có.
- Vẫn nạp được phần trọng số có khả năng mang thông tin transfer nhiều nhất
  (các khối tích chập, không phải hai lớp fully-connected cuối vốn gắn chặt với
  527 lớp AudioSet).

### Đánh đổi
- **Không phải PANNs CNN14 nguyên bản.** Phải nêu rõ trong mọi chỗ nhắc tới
  kiến trúc trong luận văn — nói "PANNs CNN14" trần trụi là phóng đại.
- Thiếu `bn0` là một biến số chưa kiểm soát được — chuẩn hoá thay thế là suy
  đoán có cơ sở, không phải đã chứng minh tương đương.

## Alternatives considered

- **Viết lại thành faithful full CNN14** (Option 1 Codex đề xuất). Đúng nguyên
  bản nhất nhưng đổi toàn bộ interface input của mọi model trong repo từ
  log-mel sang waveform — chi phí quá lớn so với 8 tuần còn lại, và không có
  gì đảm bảo tự triển khai `spectrogram_extractor`/`logmel_extractor` khớp
  chính xác phiên bản gốc (rủi ro lỗi mới lớn hơn lợi ích trung thực kiến trúc).
- **Bỏ hẳn nhánh B/C, chỉ báo nhánh A.** Mất khả năng trả lời RQ1 hoàn toàn —
  tệ hơn một encoder xấp xỉ có ghi rõ giới hạn.

## Evidence cần kiểm lại

- [ ] Tỷ lệ tham số transplant thật (số tensor / tổng, % tổng tham số).
- [ ] `conv_block` gốc có `bias=False` trên Conv2d không — xác nhận bằng shape
      thật khi load, không suy đoán.
- [ ] Ảnh hưởng của việc thiếu `bn0`: so sánh embedding trước/sau chuẩn hoá thay
      thế trên vài clip DataSEC, xem phân bố activation có "hợp lý" (không bão
      hoà hoàn toàn ở 0 hoặc giá trị cực trị) hay không — dấu hiệu gián tiếp.
