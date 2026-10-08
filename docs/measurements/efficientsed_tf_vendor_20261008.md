# XO-18 — kiểm vendor EfficientSED TF256 trên CPU

Chỉ phần sequence, không kiểm frontend/classifier hoặc chất lượng SED. Không cài package; wheel rotary0.9.1/einops0.8.2 chỉ import qua ZIP trong scratch subprocess để làm oracle. Runtime vendor chỉ torch. CUDA_VISIBLE_DEVICES rỗng.

- Rotary: 36 ca bit-equal ở float32/64/16/bfloat16, 3D/4D, seq_dim−2/−3, cache hit, cache growth và offset.
- fmn10+tf-256_advanced-kd-weak-strong.pt: strict-load 25 key, 1826864 parameter (1826832 trainable); [2,250,960]→[2, 250, 256], finite, eval forward bit-equal upstream, max_abs_diff=0.0.
- fmn10+tf-256_strong.pt: strict-load 25 key, 1826864 parameter (1826832 trainable); [2,250,960]→[2, 250, 256], finite, eval forward bit-equal upstream, max_abs_diff=0.0.

Seed20260922, CPU threads2, torch 2.11.0+cu128. Checksum nguồn/wheel/checkpoint và toàn bộ ca kiểm trong JSON. Không suy bit-equality sang GPU/autocast/training/dropout hoặc frontend. Phiên bản rotary dùng train checkpoint vẫn không biết.
