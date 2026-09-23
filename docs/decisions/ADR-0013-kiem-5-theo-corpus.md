# ADR-0013 — Kiểm 5 của cổng D4 tách theo corpus, không dùng chung cho DataSEC

**Status:** Accepted
**Date:** 2026-09-23

## Context

A5 nối `scripts.check_leakage` cho `datasec`. Bốn kiểm đầu tổng quát hoá thẳng
qua registry ([ADR-0010](ADR-0010-dinh-danh-datasec-va-cong-freeze.md)). Kiểm 5
thì không.

`check_cross_dataset_exclusions_applied` trả lời câu hỏi: *"clip pretraining
trùng dev/test của benchmark đã bị loại chưa?"* Câu hỏi đó có **hai đối tượng**
gắn cứng — assignment thuộc về benchmark (`HELD_OUT_SPLITS` là dev/test của nó),
`pretraining_prefix` xác định ai là kẻ bị nghi ngờ.

Gọi thẳng hàm này với `dataset="datasec"` thì `assignment` giờ là split của chính
DataSEC, và `pretraining_prefix="datasec:"` mặc định sẽ so DataSEC với **chính
nó**. Hai lỗi xảy ra đồng thời:

1. **Sai khái niệm.** DataSEC không có "dev/test của benchmark" — nó là corpus
   pretraining. Không có gì để kiểm 5 gốc bảo vệ.
2. **Có thể pass rỗng.** 130 clip lẽ ra bị loại đã được `create_splits`/A3 lọc
   sạch trước khi chia ([ADR-0010 §3](ADR-0010-dinh-danh-datasec-va-cong-freeze.md)),
   nên chúng **không** nằm trong `assignment` của DataSEC. Kiểm 5 gốc, nếu gọi
   nguyên si, sẽ chỉ thấy các nhóm cross-dataset chạm held-out DataSEC (khái niệm
   không có), và **luôn pass mà không kiểm được gì** — đúng dạng lỗi đã bắt được
   hai lần trước đó trong repo này.

## Decision

Thêm `check_pretraining_exclusions_absent(assignment, excluded)` — một kiểm 5
khác, dùng cho corpus `pretraining`. Câu hỏi của nó đơn giản và không cần khái
niệm "held-out của benchmark": *"clip đã bị D3 loại có mặt trong assignment
không?"* Đây chính là bất biến `require_exclusion_policy`
([`scripts/freeze_split.py`](../../scripts/freeze_split.py)) đã kiểm khi freeze
([ADR-0010 §3](ADR-0010-dinh-danh-datasec-va-cong-freeze.md)) — giờ nó xuất hiện
trong báo cáo D4 **trước** khi freeze, không chỉ vỡ ra ở bước cuối.

`scripts/check_leakage.py::build_checks` rẽ nhánh bằng `keys_for(dataset).corpus`:

| corpus | Kiểm 5 |
|---|---|
| `benchmark` (DataSED) | `check_cross_dataset_exclusions_applied` — không đổi |
| `pretraining` (DataSEC) | `check_pretraining_exclusions_absent` |

Và `load_exclusions_for_dataset` đọc `exclusions.csv` đúng luật của corpus
(`excluded_must_be_absent` của registry) thay vì luật chung — 130 dòng
`datasec:` (119 nội bộ + 10 leak + 1 unsure) đều phải vắng mặt; 13 dòng
`datased:` không có gì bắt buộc vắng mặt.

**Chống pass rỗng:** nếu `exclusions.csv` không có dòng nào của `dataset` được
truyền vào khi corpus là `pretraining`, `build_checks` từ chối chạy thay vì báo
0 vi phạm.

## Evidence — phá thử

Chèn lại một clip đã bị loại (`Helicopters-0050.wav`, lý do
`exclude_cross_dataset_leak`) vào `datasec_classification.csv`, chạy lại cổng:

```
[FAIL] 5. Clip đã bị D3 loại không lọt vào split pretraining (1 vi phạm)
    datasec:DATASEC/Propeller aircrafts/Helicopters/Helicopters-0050.wav
```

FAIL đúng file, đúng lý do. Khôi phục split bằng `create_splits datasec` lại cho
5/5 PASS với đúng số ban đầu (3,434/744/740, cụm lớn nhất 4). D4 của DataSED
không bị ảnh hưởng (5/5 PASS, `split_sha256` không đổi).

## Consequences

### Tích cực

- Cổng D4 chạy được cho cả hai dataset mà không có kiểm nào pass rỗng.
- Chống lại được vấn đề Chặn #2/#3 kiểu cũ tái diễn ở kiểm 5: một cổng tưởng
  tổng quát nhưng thực chất kiểm nhầm khái niệm.

### Đánh đổi

- `run_all` vẫn đòi đúng 5 `CheckResult`, nhưng "kiểm số 5" giờ có hai định nghĩa
  khác nhau tuỳ dataset. Đọc báo cáo D4 của DataSEC mà không biết ADR này sẽ hiểu
  nhầm ý nghĩa của dòng số 5.

## Alternatives considered

- **Tổng quát hoá `check_cross_dataset_exclusions_applied` bằng tham số.** Cố
  nhét hai khái niệm khác nhau vào một hàm sẽ làm cả hai nhánh khó đọc hơn là
  tách hẳn.
- **Bỏ kiểm 5 cho DataSEC, chỉ chạy 4 kiểm.** Vi phạm thẳng yêu cầu "đúng 5 kiểm"
  của DATA_PLAN §8.4 và `run_all`.
