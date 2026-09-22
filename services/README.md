# Services

| Service | Trách nhiệm | Không chứa |
|---|---|---|
| `api` | upload, persistence, query, orchestration | model weights, torch inference |
| `inference` | preprocessing, SED, caption | business persistence |
| `frontend` | timeline, caption, search, evidence | duplicated taxonomy constants |
| `stream` | future chunk streaming/stitching | benchmark training logic |

MVP ưu tiên batch upload. Stream chỉ triển khai sau khi offline evaluation đóng băng.

