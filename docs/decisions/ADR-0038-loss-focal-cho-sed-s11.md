# ADR-0038 — Loss focal cho SED S11

**Status:** Accepted — 2026-09-28 (được người dùng xác nhận dùng số ADR-0038)  
**Date:** 2026-09-28

## Context

Sau CV dev annotated của S13, ứng viên T2b `frame_mn` đang dẫn trong nhóm đã chạy. ADR-0031 §5 cho phép thử loss focal hoặc asymmetric để thay trần `pos_weight=10`, nhưng mọi lựa chọn phải đăng ký trước, chỉ dùng dev và không mở test. ADR-0037 đã được dùng cho quyết định frontend nên quyết định này dùng số tiếp theo ADR-0038.

## Decision

1. Thử **binary focal loss** (không cộng `pos_weight`) trên họ T2b `--encoder frame_mn --recipe t2b`. Các augmentation, kiến trúc, cửa sổ, batch, seed và lịch học giữ nguyên recipe T2b.
2. Pilot có một seed `20260922`, 3 epoch, learning rate `3e-4`, `--warmup-epochs 0 --no-cosine-decay`, chỉ ghi macro-AP frame trên dev. Lưới đăng ký trước: `gamma ∈ {0.5, 1.0, 2.0}`; tối đa ba cấu hình. Chọn gamma có macro-AP epoch cuối cao nhất; hoà thì chọn gamma nhỏ hơn.
3. Sau pilot, chạy đủ ba seed `{20260922, 2, 3}` với gamma đã chọn. Ứng viên ghi trước: (g1) ensemble ba seed T2b focal. Nếu đủ artifact và không lỗi quy trình, (g2) ensemble (g1) cộng ensemble T2b hiện đang dẫn `sed_ensemble_t2b_20260927T200914Z`; đây là phép thử bổ sung cùng họ, không phải lựa chọn ngầm.
4. Điểm chọn S13 của g1/g2 là điểm tốt hơn giữa họ global và cSEBB theo cùng CV annotated 5 fold; hoà và luật độ lệch chuẩn áp dụng y hệt ADR-0031 §4/ADR-0034. Báo per-class dev, đặc biệt các lớp hiếm, nhưng không dùng số đó để đổi lưới sau khi pilot đã chạy.
5. Mọi run phải có manifest ghi `loss`, gamma và git sạch. Hàng đợi chỉ tạo `dev.npz`, dùng `dump_predictions --verify-dev`, `build_ensemble --splits dev` và CV annotated; không `--evaluate-test`, không đọc `predictions/test.npz`.

## Alternatives considered

| Phương án | Lý do không chọn |
|---|---|
| ASL trong S11 | Thêm ba tham số (gamma+, gamma−, clip) trong khi thời gian chỉ cho một pilot nhỏ; giữ làm hướng sau nếu focal không đủ bằng chứng |
| Focal trên C-v2 | T2b là họ đang dẫn annotated và có recipe/đầu vào đã kiểm chứng; thử trên họ khác sẽ tăng số run ngoài ngân sách |
| Giữ `pos_weight` rồi nhân focal | Không đo được tác động của việc thay cơ chế cân bằng; trái mục tiêu S11 |

## Consequences

Nếu focal không cải thiện, kết quả âm tính được giữ nguyên và g1/g2 bị loại khỏi vòng S13. Nếu cải thiện, chỉ CV dev annotated được dùng để đưa ứng viên vào danh sách; hệ thống phục vụ và số test không đổi. Thêm một loss torch trong `ml/training/sed.py`, nhưng mặc định `bce` phải tái lập đường cũ.

## Verification

Unit test kiểm giá trị focal trên tensor nhỏ, gradient hữu hạn và `gamma=0` trùng BCE (với `pos_weight=1`). Script report pilot kiểm manifest cùng recipe/seed/epoch và gamma thuộc đúng lưới trước khi ghi measurement. Gate ruff/pytest chạy trước commit code và trước mỗi commit artifact/docs.
