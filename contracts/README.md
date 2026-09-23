# Contracts

JSON Schema Draft 2020-12 trung lập framework cho ranh giới hệ thống.

Các contract hiện có:

- `recording.schema.json`
- `event.schema.json`
- `timeline.schema.json`
- `inference_response.schema.json`
- `retrieval_result.schema.json`
- `run_manifest.schema.json`

Mọi service và data export phải được kiểm bằng cùng schema version. Chạy
`python -m pytest tests/test_contracts.py` để xác minh schema và các run manifest
đã commit. Dependency phát triển: `jsonschema`.
