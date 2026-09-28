# ADR-0035 — Demo phục vụ SED v2 trước S8

**Status:** Accepted — người dùng duyệt trực tiếp ngày 28/09/2026: demo được dùng v2 ngay,
không tạo số test mới và không đổi hệ thống chính thức.
**Date:** 2026-09-28

## Context

Hệ thống phục vụ chính thức theo ADR-0029 §1 và ADR-0031 §6 là ensemble C v1
`sed_ensemble_C_clean_20260925T045631Z`; nó chỉ được đổi một lần ở S8, sau vòng chọn cuối ngày
18/10. Ensemble B-v2 ba seed `sed_ensemble_v2_20260926T150934Z` đã được chọn và mở test công
khai từ 26/09, nhưng vẫn chỉ là một ứng viên của vòng chọn cuối.

Người dùng cần demo hiện tại thể hiện chất lượng v2, nhưng không cho phép việc trình diễn này trở
thành một lần chọn hệ thống mới, một lần chấm test mới, hay thay đổi số dùng trong luận văn.

## Decision

### 1. Phạm vi chỉ là demo

Profile `app` của Docker Compose phục vụ ensemble B-v2 ba seed. Hệ thống **chính thức** của luận
văn vẫn là ensemble C v1 cho tới S8; ADR này không sửa luật chọn hay lịch ADR-0031.

### 2. Mặc định code vẫn là v1

`Engine` đọc hai biến môi trường:

- `EARAG_SERVED_RUN`: đường dẫn run tương đối repository;
- `EARAG_SERVED_POSTPROC`: tên file hậu xử lý nằm trong run.

Khi bỏ cả hai biến, mặc định vẫn là
`ml/runs/sed_ensemble_C_clean_20260925T045631Z` + `postproc_cv.json`. Đường dẫn tuyệt đối, đường
dẫn thoát khỏi repository và tên hậu xử lý có thành phần thư mục đều bị từ chối.

### 3. Kiến trúc và hậu xử lý v2 lấy từ artifact, không hardcode

`ServedSed` dựng từng thành viên qua `sed_model(config, ...)` từ manifest của chính run. Ba
manifest v2 ghi pool thời gian `[2,2,2,1,1,1]` (/8), BiGRU 2×256 và
`upsample="after_rnn"`; checkpoint thật đã nạp strict thành công.

Theo [`sed_v2_selection_20260926.json`](../measurements/sed_v2_selection_20260926.json), ứng viên
(c) thắng bằng họ θ, cấu hình `global|25`. File lựa chọn của run chỉ tới cấu hình đó và artifact
đóng băng tương ứng là `postproc_cv.json`; demo v2 dùng đúng file này, không hiệu chuẩn lại.

### 4. Trạng thái API phân biệt demo và chính thức

`Engine.info()` và `GET /api/v1/models/status` trả thêm `served_run` và `official`. `official=true`
chỉ khi đúng cặp mặc định v1 + `postproc_cv.json`; cấu hình demo v2 luôn trả `false` dù chạy khỏe.

### 5. Compose chọn v2 và cách quay về v1

Service `inference` trong profile `app` đặt:

```text
EARAG_SERVED_RUN=ml/runs/sed_ensemble_v2_20260926T150934Z
EARAG_SERVED_POSTPROC=postproc_cv.json
```

Volume `./ml/runs:/app/ml/runs:ro` đã bao phủ ensemble và cả ba thư mục thành viên. Muốn quay về
v1 chỉ cần bỏ hai biến môi trường rồi tạo lại service; không sửa hằng mặc định và không build lại
checkpoint.

### 6. Không phân tích lại ngầm dữ liệu đã upload

Recording đã upload bằng v1 giữ nguyên timeline, caption và `model_version` cũ trong event store.
Đổi biến môi trường chỉ áp dụng cho upload mới; hệ thống không chạy lại recording cũ ngầm. Parity
v2 chỉ so đầu ra phục vụ với logit/đầu ra test đã đóng băng, không đọc ground truth để tính metric
và không tạo số test mới.

## Consequences

### Tích cực

- Demo mới dùng chất lượng SED v2 mà vẫn giữ nguyên protocol chọn hệ thống cuối.
- Một image phục vụ được cả v1 và v2; kiến trúc, số thành viên và hậu xử lý truy được về artifact.
- API và giao diện vận hành có thể hiện rõ đây không phải hệ thống chính thức.

### Đánh đổi

- Event store có thể đồng thời chứa recording từ nhiều `model_version`; đây là lịch sử có chủ ý.
- Người vận hành phải nhìn `official`, không được suy hệ thống chính thức từ việc demo đang chạy.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| Đổi hằng `SERVED_ENSEMBLE` sang v2 | Biến ngoại lệ demo thành mặc định và vi phạm ADR-0031 §6 |
| Chờ S8 mới demo v2 | Không đáp ứng duyệt trực tiếp ngày 28/09 |
| Phân tích lại toàn bộ upload cũ | Làm mất provenance/model_version cũ và thay đổi dữ liệu ngầm |
| Hardcode một lớp model v2 riêng | Trùng logic train và dễ lệch kiến trúc manifest |

