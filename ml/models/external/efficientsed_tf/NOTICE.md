# EfficientSED TF256 — phần sequence tối thiểu, MIT

Nguồn EfficientSED: <https://github.com/theMoro/EfficientSED>, commit
`e3449bfd1f4922b81d82410ed842653f462bfca8`:
`models/sequence_models/roformer/attention.py`, `transformer_block.py`,
`models/sequence_models/helper.py` (chỉ RMSNorm), và cách ghép `seq_model`
trong `models/prediction_wrapper.py`. Attention/block upstream ghi nguồn
[BS-RoFormer](https://github.com/lucidrains/BS-RoFormer), MIT.

Rotary: [rotary-embedding-torch 0.9.1](https://pypi.org/project/rotary-embedding-torch/0.9.1/),
file `rotary_embedding_torch/rotary_embedding_torch.py` trong wheel
`rotary_embedding_torch-0.9.1-py3-none-any.whl`, SHA-256
`489ef53e21ab4c4eb35c0c97b551d724f5eea71c2bca39acb8fee8d88b142a76`.
Ghim bằng bản phát hành và checksum wheel; không suy commit Git của wheel
hoặc phiên bản rotary dùng để train checkpoint (upstream không ghim).

Thay đổi: dùng reshape/permute/unsqueeze/expand thay einops; chỉ giữ
language RoPE mặc định, cache không persistent, `freqs` Parameter frozen;
bỏ API XPos/axial/pixel/learned frequencies, attention bias/zero-KV và
print/global first_RUN không dùng ở TF256. Giữ RMSNorm bằng F.normalize,
SDPA, gating, residual, dropout và namespace state_dict. Không đổi frontend,
không tạo model wrapper hoặc cài dependency. Runtime chỉ cần torch.

`build_tf256()` trả `nn.Sequential` projection960→256 + hai block
(8head×32, FF1024, dropout0.1). Đầu vào `[B,T,960]`, đầu ra `[B,T,256]`.
Strip đúng prefix `net.seq_model.` rồi `load_state_dict(..., strict=True)`.
Factory khởi tạo ngẫu nhiên theo torch mặc định: phải load checkpoint khi dùng
pretrain; không tái tạo init_weights của upstream để train từ đầu.

## Bản quyền và giấy phép được giữ lại

EfficientSED: Copyright (c) 2024 Florian Schmid.
BS-RoFormer: Copyright (c) 2023 Phil Wang.
rotary-embedding-torch 0.9.1: Copyright (c) 2021 Phil Wang.

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
