# Data workspace

| Thư mục | Nội dung | Commit |
|---|---|---:|
| `raw/` | Archive giải nén, bất biến | Không |
| `interim/` | Audio/labels chuẩn hóa, tái tạo được | Không |
| `features/` | Feature tensors | Không |
| `manifests/` | Provenance, inventory, exclusions, duplicate groups | Có |
| `annotations/` | Mapping và canonical annotation nhỏ | Có |
| `reference/` | LICENSE/README/taxonomy metadata được phép lưu | Có |
| `splits/` | Frozen split IDs và hashes | Có |

Không đặt raw audio vào Git, kể cả sample nhỏ, trước khi kiểm license.

## Dọn dung lượng

Dọn ổ D (26/09, người dùng duyệt nhóm 1 + 3): xoá 21 `last.pt` (checkpoint kèm optimizer,
chỉ để train tiếp), `best.pt` của D2 `classifier_datasec_20260923T125149Z` (trùng từng bit D1,
SHA-256 `5ab56f3e…` ghi ở AGENT_SYNC), và 2 ZIP gốc trong `data/raw/*/archives/` (tải lại bằng
`scripts.data_sources download`, đối chiếu MD5 ở `docs/measurements/archive_audit_20260922.md`).
Giữ: WAV giải nén (717 + 5,048), feature, mọi `best.pt` còn lại, dự đoán `.npz`, evaluation, caption.
Giải phóng 26.4 GB (D trống 10.6 → 37.0 GB).
