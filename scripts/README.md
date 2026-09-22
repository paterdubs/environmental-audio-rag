# Scripts

CLI chạy từ repository root bằng `python -m scripts.<name>`. Danh sách dự kiến:

```text
fetch_source_metadata
download_datasets
verify_archives
build_inventory
normalize_annotations
find_duplicates
make_splits
train_classifier
train_sed
evaluate_run
build_retrieval_index
serve_demo
```

Script chỉ parse arguments và gọi module trong `ml/`; không chứa logic lõi khó test.
