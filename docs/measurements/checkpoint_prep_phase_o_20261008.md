# Chuẩn bị checkpoint giai đoạn O — XO-5 (08/10/2026)

Tải release v0.0.1 bằng curl; kiểm kích thước asset qua GitHub API, băm SHA-256 tại máy, đọc `torch.load(map_location="cpu", weights_only=True)`. `CUDA_VISIBLE_DEVICES=""` được đặt trong Python trước import torch. Không inference/train, không viết wrapper.

## File, hash và tham số

Đếm tham số gồm **cả strong head lẫn weak head** lưu trong state dict; loại buffer BatchNorm. Backbone FMN riêng có 2.971.664 tham số, 308 tensor gồm 24.446 phần tử buffer. Tên parameter/buffer đối chiếu với model thật; JSON kèm toàn bộ key/shape/dtype và nguồn. TF tính cả 32 frequency parameter RoPE không trainable; phần còn lại 5.028.254 phần tử. RotaryEmbedding khai báo freqs là nn.Parameter(requires_grad=False) mặc định.

| File | Byte | Tham số | SHA-256 |
|---|---:|---:|---|
| [fmn10+gru-256_strong.pt](https://github.com/theMoro/EfficientSED/releases/download/v0.0.1/fmn10%2Bgru-256_strong.pt) | 26139225 | 6483854 | `1c963930f92d7cd42ff01f4bff940701aa2db8f5c6d64601cf8c0d1d5d5bf007` |
| [fmn10+tf-256_advanced-kd-weak-strong.pt](https://github.com/theMoro/EfficientSED/releases/download/v0.0.1/fmn10%2Btf-256_advanced-kd-weak-strong.pt) | 20304913 | 5028286 | `7d5326a485b742b323b33dd2bcb366606b614b2a5deaa5e452ef34ddedb9797c` |
| [fmn10+tf-256_strong.pt](https://github.com/theMoro/EfficientSED/releases/download/v0.0.1/fmn10%2Btf-256_strong.pt) | 20341877 | 5028286 | `20510a4235433d3d0867a812fbb1f985c4221e54eb338f5a5842f50d9cff2683` |
| [fmn10_strong.pt](https://github.com/theMoro/EfficientSED/releases/download/v0.0.1/fmn10_strong.pt) | 15538778 | 3830798 | `92a5c1dc5aa21620e262420c4cc657d2f699bdfa20a748de506c354a2fe2770a` |
| [ATST-F_strong_1.pt](https://github.com/fschmid56/PretrainedSED/releases/download/v0.0.1/ATST-F_strong_1.pt) | 344480550 | 86106750 | `fbf2577958e3648d55ee8cea7e0e5260c4505fb0c13964e1ec81bc367cee5eda` |

Các asset API không công bố digest: SHA-256 trên là định danh byte tải được, không phải phép đối chiếu với checksum độc lập của tác giả.

## Key/shape theo module và khả năng nạp

| File | Module | Tensor | Tham số | Buffer (numel) |
|---|---|---:|---:|---:|
| fmn10+gru-256_strong.pt | `net.model` | 308 | 2971664 | 24446 |
| fmn10+gru-256_strong.pt | `net.seq_model` | 16 | 3053568 | 0 |
| fmn10+gru-256_strong.pt | `net.strong_head` | 2 | 229311 | 0 |
| fmn10+gru-256_strong.pt | `net.weak_head` | 2 | 229311 | 0 |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.model` | 308 | 2971664 | 24446 |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.seq_model` | 25 | 1826864 | 0 |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.strong_head` | 2 | 114879 | 0 |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.weak_head` | 2 | 114879 | 0 |
| fmn10+tf-256_strong.pt | `net.model` | 308 | 2971664 | 24446 |
| fmn10+tf-256_strong.pt | `net.seq_model` | 25 | 1826864 | 0 |
| fmn10+tf-256_strong.pt | `net.strong_head` | 2 | 114879 | 0 |
| fmn10+tf-256_strong.pt | `net.weak_head` | 2 | 114879 | 0 |
| fmn10_strong.pt | `net.model` | 308 | 2971664 | 24446 |
| fmn10_strong.pt | `net.strong_head` | 2 | 429567 | 0 |
| fmn10_strong.pt | `net.weak_head` | 2 | 429567 | 0 |
| ATST-F_strong_1.pt | `model.atst` | 138 | 85419264 | 0 |
| ATST-F_strong_1.pt | `strong_head.weight` | 1 | 343296 | 0 |
| ATST-F_strong_1.pt | `strong_head.bias` | 1 | 447 | 0 |
| ATST-F_strong_1.pt | `weak_head.weight` | 1 | 343296 | 0 |
| ATST-F_strong_1.pt | `weak_head.bias` | 1 | 447 | 0 |

Bốn FMN đều: lọc `net.model.*`, bỏ tiền tố đó, gọi `ml.models.external.frame_mn.get_model(width_mult=1.0).load_state_dict(..., strict=True)` trên CPU → **missing=[]; unexpected=[]; shape mismatch=[]** so với backbone checkpoint `frame_mn10_strong_1.pt`. Truyền state dict thô không nạp được vì namespace và head/sequence khác; JSON ghi danh sách raw missing/unexpected. Loader `encoder_state_from_checkpoint` hiện tại chỉ nhận `model.frame_mn.` và bỏ head; cần Claude bổ sung đường nạp EfficientSED để giữ sequence model.

Các shape tiêu biểu (đầy đủ ở JSON):

| File | Key | Shape |
|---|---|---|
| fmn10+gru-256_strong.pt | `net.model.features.0.0.weight` | [16, 1, 3, 3] |
| fmn10+gru-256_strong.pt | `net.model.features.16.0.weight` | [960, 160, 1, 1] |
| fmn10+gru-256_strong.pt | `net.seq_model.0.gru.weight_ih_l0` | [768, 960] |
| fmn10+gru-256_strong.pt | `net.seq_model.0.gru.weight_hh_l0` | [768, 256] |
| fmn10+gru-256_strong.pt | `net.seq_model.0.gru.weight_ih_l1` | [768, 512] |
| fmn10+gru-256_strong.pt | `net.strong_head.weight` | [447, 512] |
| fmn10+gru-256_strong.pt | `net.weak_head.weight` | [447, 512] |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.model.features.0.0.weight` | [16, 1, 3, 3] |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.model.features.16.0.weight` | [960, 160, 1, 1] |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.seq_model.0.weight` | [256, 960] |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.seq_model.1.layers.0.0.pos_encoding.freqs` | [16] |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.seq_model.1.layers.0.0.norm.gamma` | [256] |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.seq_model.1.layers.0.0.to_qkv.weight` | [768, 256] |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.seq_model.1.layers.0.0.to_gates.weight` | [8, 256] |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.seq_model.1.layers.0.0.to_gates.bias` | [8] |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.seq_model.1.layers.0.0.to_out.0.weight` | [256, 256] |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.seq_model.1.layers.0.1.net.0.gamma` | [256] |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.seq_model.1.layers.0.1.net.1.weight` | [1024, 256] |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.seq_model.1.layers.0.1.net.1.bias` | [1024] |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.seq_model.1.layers.0.1.net.4.weight` | [256, 1024] |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.seq_model.1.layers.0.1.net.4.bias` | [256] |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.strong_head.weight` | [447, 256] |
| fmn10+tf-256_advanced-kd-weak-strong.pt | `net.weak_head.weight` | [447, 256] |
| fmn10+tf-256_strong.pt | `net.model.features.0.0.weight` | [16, 1, 3, 3] |
| fmn10+tf-256_strong.pt | `net.model.features.16.0.weight` | [960, 160, 1, 1] |
| fmn10+tf-256_strong.pt | `net.seq_model.0.weight` | [256, 960] |
| fmn10+tf-256_strong.pt | `net.seq_model.1.layers.0.0.pos_encoding.freqs` | [16] |
| fmn10+tf-256_strong.pt | `net.seq_model.1.layers.0.0.norm.gamma` | [256] |
| fmn10+tf-256_strong.pt | `net.seq_model.1.layers.0.0.to_qkv.weight` | [768, 256] |
| fmn10+tf-256_strong.pt | `net.seq_model.1.layers.0.0.to_gates.weight` | [8, 256] |
| fmn10+tf-256_strong.pt | `net.seq_model.1.layers.0.0.to_gates.bias` | [8] |
| fmn10+tf-256_strong.pt | `net.seq_model.1.layers.0.0.to_out.0.weight` | [256, 256] |
| fmn10+tf-256_strong.pt | `net.seq_model.1.layers.0.1.net.0.gamma` | [256] |
| fmn10+tf-256_strong.pt | `net.seq_model.1.layers.0.1.net.1.weight` | [1024, 256] |
| fmn10+tf-256_strong.pt | `net.seq_model.1.layers.0.1.net.1.bias` | [1024] |
| fmn10+tf-256_strong.pt | `net.seq_model.1.layers.0.1.net.4.weight` | [256, 1024] |
| fmn10+tf-256_strong.pt | `net.seq_model.1.layers.0.1.net.4.bias` | [256] |
| fmn10+tf-256_strong.pt | `net.strong_head.weight` | [447, 256] |
| fmn10+tf-256_strong.pt | `net.weak_head.weight` | [447, 256] |
| fmn10_strong.pt | `net.model.features.0.0.weight` | [16, 1, 3, 3] |
| fmn10_strong.pt | `net.model.features.16.0.weight` | [960, 160, 1, 1] |
| fmn10_strong.pt | `net.strong_head.weight` | [447, 960] |
| fmn10_strong.pt | `net.weak_head.weight` | [447, 960] |
| ATST-F_strong_1.pt | `model.atst.pos_embed` | [1, 251, 768] |
| ATST-F_strong_1.pt | `model.atst.patch_embed.patch_embed.weight` | [768, 256] |
| ATST-F_strong_1.pt | `model.atst.blocks.0.attn.qkv.weight` | [2304, 768] |
| ATST-F_strong_1.pt | `model.atst.blocks.1.attn.qkv.weight` | [2304, 768] |
| ATST-F_strong_1.pt | `model.atst.blocks.2.attn.qkv.weight` | [2304, 768] |
| ATST-F_strong_1.pt | `model.atst.blocks.3.attn.qkv.weight` | [2304, 768] |
| ATST-F_strong_1.pt | `model.atst.blocks.4.attn.qkv.weight` | [2304, 768] |
| ATST-F_strong_1.pt | `model.atst.blocks.5.attn.qkv.weight` | [2304, 768] |
| ATST-F_strong_1.pt | `model.atst.blocks.6.attn.qkv.weight` | [2304, 768] |
| ATST-F_strong_1.pt | `model.atst.blocks.7.attn.qkv.weight` | [2304, 768] |
| ATST-F_strong_1.pt | `model.atst.blocks.8.attn.qkv.weight` | [2304, 768] |
| ATST-F_strong_1.pt | `model.atst.blocks.9.attn.qkv.weight` | [2304, 768] |
| ATST-F_strong_1.pt | `model.atst.blocks.10.attn.qkv.weight` | [2304, 768] |
| ATST-F_strong_1.pt | `model.atst.blocks.11.attn.qkv.weight` | [2304, 768] |
| ATST-F_strong_1.pt | `strong_head.weight` | [447, 768] |
| ATST-F_strong_1.pt | `weak_head.weight` | [447, 768] |

## Frontend và kiến trúc đọc từ code

[EfficientSED @e3449bfd](https://github.com/theMoro/EfficientSED/tree/e3449bfd1f4922b81d82410ed842653f462bfca8): `FrameMNWrapper` (`models/efficient_cnns/fmn/fmn_wrapper.py`) dựng `get_model(width_mult=1.0)`; `PredictionsWrapper` gắn sequence và hai linear head. Backbone cho embedding 960 chiều; chuỗi được căn về 250 bước/10 s (25 Hz) trước sequence/head. Bốn file lưu strong/weak head **447 lớp**, không phải taxonomy 21 lớp của repo. GRU chọn hidden **256**, 2 lớp hai chiều (đầu ra 512); TF: Linear 960→256 rồi 2 block, 8 heads, RoPE, FFN×4, gated attention; đầu ra 256. Bản advanced KD cùng cấu trúc TF256, khác trọng số. No-sequence dùng Identity.

FMN: 16 kHz, 128 mel, FFT 512, Hann không periodic 400 mẫu, hop 160 (10 ms), centered reflect padding, power→natural log (floor 1e-7), preemphasis 0.97, fast norm `(logmel+4.5)/5`. `fmin=0`; `fmax=None` được **resolve thành 7000 Hz** do `fmax_aug_range=2000`, không phải 8000 Hz. Train jitter fmin 0…9, fmax 6001…8000; eval không jitter. Mel dùng Kaldi; `htk=False,norm=1` là đối số constructor nhưng không quyết định công thức Kaldi. Cấu hình trùng frontend FMN hiện có; strict weight load chỉ chứng minh cấu trúc, không tự chứng minh số inference.

Môi trường chung chưa có torchaudio hoặc rotary_embedding_torch. Upstream prediction_wrapper còn import mamba_ssm vô điều kiện; không cài thêm hay sửa môi trường của Claude. Strict-load backbone dùng vendor nội bộ nên không cần các dependency đó. [RotaryEmbedding source](https://github.com/lucidrains/rotary-embedding-torch/blob/main/rotary_embedding_torch/rotary_embedding_torch.py) xác nhận freqs là parameter đóng băng; dependency upstream không ghim phiên bản.

[PretrainedSED @1aa47e48](https://github.com/fschmid56/PretrainedSED/tree/1aa47e482f7e89904cba2338999345025d8b4e36): `ATSTWrapper` → `FrameASTModel`, embedding 768, 12 transformer blocks ×12 heads, FFN×4, qkv_bias=False; patch 64 mel×4 frame, 1001 mel frame →250 token/10 s. Backbone 85.419.264 tham số; hai head 447×768 cộng bias → tổng 86.106.750. ATST không tương thích backbone FMN.

ATSTMel: 16 kHz, 64 mel, FFT/win 1024, hop160, fmin60/fmax7800 Hz; torchaudio MelSpectrogram mặc định power2, centered reflect padding, Hann periodic, HTK mel, norm=None. AmplitudeToDB(power,top_db80), clamp[-50,80], scaler cố định min=-79.6482/max=50.6842 (ánh xạ tuyến tính, không clamp sau scale). Frontend buffer không nằm trong checkpoint, phải dựng từ code.

## License và nguồn

[EfficientSED LICENSE](https://github.com/theMoro/EfficientSED/blob/e3449bfd1f4922b81d82410ed842653f462bfca8/LICENSE) và [PretrainedSED LICENSE](https://github.com/fschmid56/PretrainedSED/blob/1aa47e482f7e89904cba2338999345025d8b4e36/LICENSE): MIT, ©2024 Florian Schmid. Release không có license riêng cho từng asset. [ATST upstream LICENSE](https://github.com/Audio-WestlakeU/audiossl/blob/main/LICENSE) phân biệt code MIT với checkpoint được liên kết CC BY 4.0; giữ chuỗi attribution ATST khi dùng bản fine-tune. Không suy license checkpoint từ license dataset. Báo license là bằng chứng khai báo, không quyết định pháp lý mới.

## Ước lượng activation ATST (fp16; batch 8×10 s)

Đặt B=8, N=250, D=768, H=12, L=12, mỗi phần tử 2 byte. Một B×N×D: **3,072,000 byte**; một attention matrix B×H×N×N: **12,000,000 byte**. Giả định giữ mỗi block QKV (3D), FFN expansion (4D), bốn tensor D cho residual/norm và hai attention matrix:

`L × (11×B×N×D×2 + 2×B×H×N×N×2)` = **693,504,000 byte ≈ 0.6459 GiB**.

Đây là ước lượng các tensor giữ lại theo giả định, **không phải peak VRAM hay cận trên**. Còn tensor backward, mask, workspace, allocator và phần frontend. T0 GPU do Claude chạy vẫn cần thiết.

## Tái lập và provenance

Lệnh tải: `curl.exe -fL --retry 4 -C - <asset-url> -o <file>.codex-download`; kiểm size rồi rename; không ghi đè file có sẵn.

Kiểm CPU: `torch.load(path,map_location="cpu",weights_only=True)`; lọc backbone như trên; SHA bằng `hashlib.file_digest`. Toàn bộ JSON từ helper `.agent_logs/inspect_checkpoints.py` và `.agent_logs/render_checkpoint_report.py` (helper bỏ qua Git; report và JSON được commit). Revision worktree khi sinh: `08c05d37cfb7f43007904744b457bb5c2b778af6`, dirty=True (đang làm task). SHA source file lấy đúng byte git blob, tránh checkout CRLF.
