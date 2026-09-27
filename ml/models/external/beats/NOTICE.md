# Mã ngoài: BEATs (qua PretrainedSED)

Chép tối thiểu theo [ADR-0032](../../../../docs/decisions/ADR-0032-track2-encoder-pretrain-theo-frame.md) §4,
để dùng checkpoint `BEATs_strong_1.pt` làm encoder đóng băng (T2a).

## Nguồn

| | |
|---|---|
| Repo | https://github.com/fschmid56/PretrainedSED |
| Commit | `1aa47e482f7e89904cba2338999345025d8b4e36` (HEAD `main`, lấy bằng `git ls-remote` ngày 27/09/2026) |
| Gốc của mã BEATs | https://github.com/microsoft/unilm/tree/master/beats (PretrainedSED chép lại, đổi `weight_norm` sang `torch.nn.utils.parametrizations`) |
| License | PretrainedSED: MIT, © 2024 Florian Schmid (`LICENSE`). BEATs: MIT, © Microsoft Corporation (`LICENSE-unilm`, lấy từ repo `microsoft/unilm`) |

SHA-256 của file **gốc** tải từ `raw.githubusercontent.com/fschmid56/PretrainedSED/<commit>/`:

| File gốc | Ở đây | SHA-256 gốc |
|---|---|---|
| `models/beats/BEATs.py` | `BEATs.py` | `c7dba46d9f83a09b0096337816795a2239cbab5f9e979c558c57f15953667765` |
| `models/beats/backbone.py` | `backbone.py` | `5df93ef883d2fea0f9a3763caa93690b706905094d6ec727f86f68a827b87c5d` |
| `models/beats/modules.py` | `modules.py` | `c4b4170b1c4286717b606788f617a0a768af076cdeaaa9b1d35bf70d6c3859fe` |
| `LICENSE` | `LICENSE` | `399acc6d903cfd65a6cd5baba6a99af3ee534d79161b07854c1a6ffeab3dc88b` |

Không chép: `BEATs_wrapper.py`, `prediction_wrapper.py` (đọc để viết lại phần cần dùng ở
`ml/models/beats_frozen.py`), `Tokenizers.py`, `quantizer.py` (chỉ dùng lúc pretrain BEATs).

## Chỗ đã sửa

Mỗi chỗ có chú thích `MODIFIED` ngay tại dòng sửa. Ngoài ba chỗ này, file giữ nguyên từng byte.

1. `BEATs.py`: bỏ `import torchaudio.compliance.kaldi`; `preprocess` gọi
   `ml.features.kaldi_fbank.kaldi_fbank` với đúng tham số cũ. torchaudio không phải phụ thuộc của
   repo; bản viết lại được đối chiếu số với torchaudio 2.11.0 (`tests/test_kaldi_fbank.py`).
2. `BEATs.py`, `backbone.py`: import tương đối trong gói, thay cho bố cục `models.beats` của repo
   nguồn.
3. `backbone.py`, `TransformerEncoder.extract_features`: chỉ rút `np.random.random()` (layerdrop)
   khi `self.training`. Bản gốc rút ở **mọi** lượt forward, kể cả eval (khi đó giá trị bị bỏ qua).
   Với encoder đóng băng chạy trong vòng lặp dữ liệu, việc đó âm thầm dịch chuỗi random crop của
   `SedFeatureDataset` (cùng dùng RNG NumPy toàn cục). Ở chế độ train, hành vi không đổi.

`ruff` bỏ qua thư mục này (`pyproject.toml`, `extend-exclude`) để không phải định dạng lại mã
ngoài — định dạng lại sẽ làm mất khả năng so từng dòng với nguồn.
