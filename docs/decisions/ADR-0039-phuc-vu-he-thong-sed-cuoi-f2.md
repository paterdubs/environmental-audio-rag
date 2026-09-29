# ADR-0039 — Phục vụ hệ thống SED cuối f2

**Status:** Accepted
**Date:** 2026-09-29

## Context

ADR-0031 §4 và §9 đã khóa f2 (T2b × 3, cSEBB `tau0.64_rel2`) bằng CV dev
`annotated` trước khi mở test. Hệ thống đang phục vụ vẫn là PANNs/v1, còn profile Compose
tạm trỏ v2 theo ADR-0035. f2 nhận waveform PCM 16 kHz trong khi service cũ chỉ dựng PANNs
trên log-mel; cSEBB cũng không dùng post-processing ngưỡng/duration-prior cũ.

## Decision

1. Hệ thống mặc định/chính thức là `sed_ensemble_t2b_20260927T200914Z` với
   `sebb_cv_selection_annotated.json`; `/models/status` phải trả `official=true` khi không có
   override.
2. Inference hỗ trợ member `frame_mn`: resample mono 16 kHz bằng cùng `librosa.load`, lượng tử
   PCM16 như cache lúc train, cắt cửa sổ theo lưới log-mel 100 fps và zero-pad như
   `SedWaveformDataset`.
3. Event của f2 dùng đúng cSEBB đã chọn trên dev, không chuyển sang threshold/duration prior.
   `check_inference_parity` đối chiếu waveform cache và `predictions/test.npz` f2 S13; CPU
   container và CUDA host là phép đo tái tạo, không phải đánh giá lại hay tuning.
4. Compose không còn override demo v2. Override `EARAG_SERVED_*` giữ lại chỉ để chẩn đoán cục bộ
   và luôn khiến `official=false`.

## Alternatives considered

| Phương án | Lý do không chọn |
|---|---|
| Chỉ đổi hằng sang f2 | Service cũ từ chối `frame_mn` và không hiểu cSEBB. |
| Phục vụ f4 vì dùng threshold cũ | Trái luật chọn CV đã khóa; không được chọn lại sau test. |
| Giữ override Compose v2 | Demo sẽ công bố hệ thống không phải hệ thống chính thức. |

## Consequences

Service cần thêm đường waveform 16 kHz và tải ba checkpoint Frame-MobileNet. Artifact S13 f2
test chỉ là reference parity; run ensemble dev vẫn là nguồn cấu hình/three-member phục vụ.
Các số W5/W6 cũ giữ nguyên, còn S8 sinh bộ số mới duy nhất trên f2.

## Verification

Kiểm thử unit bao phủ mặc định official và override. Gate toàn repo, parity CUDA host, parity CPU
trong container, W5/W6 và registry artifact được ghi sau khi chạy trên tree sạch; các file
measurement liên kết từ STATUS, CLAUDE và PLAN.
