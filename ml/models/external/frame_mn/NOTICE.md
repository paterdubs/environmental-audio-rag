# Mã ngoài: Frame-MobileNet (qua PretrainedSED)

Chép tối thiểu theo [ADR-0032](../../../../docs/decisions/ADR-0032-track2-encoder-pretrain-theo-frame.md) §3–§4,
để fine-tune toàn bộ checkpoint `frame_mn10_strong_1.pt` (T2b).

## Nguồn

| | |
|---|---|
| Repo | https://github.com/fschmid56/PretrainedSED |
| Commit | `1aa47e482f7e89904cba2338999345025d8b4e36` (cùng commit đã ghim cho BEATs, xem `../beats/NOTICE.md`) |
| Gốc của Frame-MobileNet | MobileNetV3 chỉnh cho audio của EfficientAT (https://github.com/fschmid56/EfficientAT), dựa trên `torchvision.models.mobilenetv3` |
| License | PretrainedSED: MIT, © 2024 Florian Schmid (`LICENSE`). EfficientAT: MIT, © 2022 Florian Schmid (`LICENSE-EfficientAT`, lấy qua GitHub API `repos/fschmid56/EfficientAT/license`) |

SHA-256 của file **gốc** tải từ `raw.githubusercontent.com/fschmid56/PretrainedSED/<commit>/` ngày 27/09/2026:

| File gốc | Ở đây | SHA-256 gốc |
|---|---|---|
| `models/frame_mn/model.py` | `model.py` | `6c316eab1744c3a6d45537532bd4dfc91718f7132f1de42e79a922c8c5b48077` |
| `models/frame_mn/block_types.py` | `block_types.py` | `1dfa5636aadb209eeaa7e412d5fc422bfefe230b4b30f49a14fe11776eab825c` |
| `models/frame_mn/utils.py` | `utils.py` | `b952d15279cf2fb21658e6916ce23e00e3338187564b4ad9c635a10dd261aac5` |
| `models/frame_passt/preprocess.py` | `preprocess.py` | `1ac324f812566924ab52879077186dcaffdc8a4062ee186153be48e99b658db0` |
| `LICENSE` | `LICENSE` | `399acc6d903cfd65a6cd5baba6a99af3ee534d79161b07854c1a6ffeab3dc88b` |

Không chép: `models/frame_mn/Frame_MN_wrapper.py` (SHA-256 `c9f9be29…40d77`) và
`models/prediction_wrapper.py` — đọc để viết lại phần cần dùng ở `ml/models/frame_mn_finetune.py`
(cùng tham số frontend, cùng phép căn chuỗi về 250 bước, head tuyến tính trên từng bước).

`conv_norm.py` **không** phải mã ngoài: viết mới cho repo này, thay `torchvision.ops.misc.ConvNormActivation`
(torchvision không là phụ thuộc). Giữ đúng thứ tự Conv2d → norm → activation để tên khoá
state-dict khớp; checkpoint nạp `strict=True` là bằng chứng.

## Chỗ đã sửa

Mỗi chỗ có chú thích `MODIFIED` ngay tại dòng sửa. Ngoài các chỗ này, file giữ nguyên từng byte.

1. `model.py`, `block_types.py`: `ConvNormActivation` lấy từ `conv_norm.py` thay vì torchvision.
2. `model.py`, `block_types.py`: import tương đối trong gói, thay cho bố cục `models.frame_mn`.
3. `preprocess.py`: bỏ `import torchaudio`. Ma trận mel lấy từ
   `ml.features.kaldi_fbank.kaldi_mel_banks` — bản torch của `torchaudio.compliance.kaldi.get_mel_banks`
   (đã ghim với torchaudio 2.11.0 cho BEATs), gọi với `vtln_warp_factor=1.0` nghĩa là không warp;
   hàm đó đã tự thêm cột Nyquist bằng 0 như bản gốc làm bằng `pad`.
4. `preprocess.py`: `FrequencyMasking`/`TimeMasking` của torchaudio thay bằng lỗi rõ ràng nếu
   `freqm`/`timem` khác 0. `Frame_MN_wrapper` gốc dùng `freqm=0, timem=0`, nên nhánh đó không bao giờ
   chạy với frame_mn.

`ruff` bỏ qua thư mục này (`pyproject.toml`, `extend-exclude`) để không phải định dạng lại mã
ngoài.
