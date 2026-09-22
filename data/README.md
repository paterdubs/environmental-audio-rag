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

