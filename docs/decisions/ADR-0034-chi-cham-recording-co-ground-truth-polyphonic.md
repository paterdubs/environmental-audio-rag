# ADR-0034 — Chỉ chấm trên recording có ground truth polyphonic (từ vòng chọn S13)

**Status:** Accepted — người dùng duyệt 28/09 ("các việc cần tôi quyết thì cứ làm theo như bạn đề
xuất"), phương án (B) của PLAN nợ #25.
**Date:** 2026-09-28

## Context

Khi đối chiếu bài báo DataSED với archive (nợ #21), `polyphonic_coverage_20260927.md` cho thấy file
gốc `Polyphonic_sound_detection.csv` chỉ phủ 703/717 recording. 14 recording S-0704…S-0717 — đúng
tập có nhãn monophonic `wind_turbine` — không có dòng polyphonic nào, nhưng split benchmark
`data-v1.0` gồm cả 717. Pipeline vì thế coi chúng là **không có sự kiện**:
- khi chấm dev/test, dự đoán ở đó thành FP, sự kiện thật (102 nhãn monophonic thuộc 21 lớp) không
  thành FN;
- khi train, 8 recording là mẫu âm dù có âm thanh.

Phân bố: train 8 (0.989 h), dev 3 (0.392 h), test 3 (0.280 h: S-0711, S-0716, S-0717). Trên dev,
bỏ 3 recording nâng event-F1 micro của (c)/(d)/(f1) khoảng +0.002; thứ hạng không đổi.

Ba phương án (PLAN nợ #25): (A) giữ nguyên, ghi Hạn chế; (B) từ S13 chỉ chấm trên recording có GT;
(C) sinh lại split và train lại mọi thứ.

## Decision

### 1. Tập chấm "annotated" cho mọi đánh giá từ S13

`data/manifests/datased_polyphonic_unannotated.csv` (sinh bởi
`scripts.report_polyphonic_coverage --manifest-only` từ file gốc của archive) liệt kê 14
recording. `ml/evaluation/coverage.py` bỏ chúng khi `eval_set="annotated"`.

`select_postproc_cv`, `select_sebb_cv`, `evaluate_run` nhận `--eval-set {all,annotated}`:
- `annotated`: dev 137 → **134** recording, test 142 → **139**;
- file ra có hậu tố `_annotated`, không ghi đè kết quả cũ;
- mặc định vẫn `all`, để mọi số đã báo tái lập được.

### 2. Sửa luật ADR-0031 §4 ở đúng một điểm

Điểm của mỗi ứng viên ở vòng chọn S13 là CV dev trên tập **annotated** (cùng 5 fold theo
`leakage_group`, cùng hai họ hậu xử lý, lấy họ tốt hơn). Test một lần sau khi chọn cũng chấm trên
tập annotated. Mọi phần khác của luật giữ nguyên. Sửa này ghi **trước** khi có CV annotated của bất
kỳ ứng viên nào.

### 3. Không train lại, không đổi split

`data-v1.0` giữ nguyên, run đã train giữ nguyên. 8 recording train thiếu GT vẫn là mẫu âm trong mọi
model — ghi vào Hạn chế. Cỡ ảnh hưởng: 0.989 h trên tổng khoảng 11 h train.

### 4. Số đã báo giữ nguyên, có ghi chú

RQ1, SED v2 (test micro 0.1476) và mọi số trước 28/09 là trên tập `all`, giữ nguyên và ghi rõ như
vậy. Với các hệ thống đã mở test ((a), (c)), bản chấm annotated trên test chỉ tính **sau** khi lựa
chọn S13 đã commit, cùng lúc với các ứng viên khác — không để số test mới dẫn hướng vòng chọn.

### 5. Kết quả CV annotated (28/09, chưa phải lựa chọn S13)

Hàng đợi đã sinh đủ **18/18** file lựa chọn cho 9 ứng viên (hai họ θ và cSEBB); mọi file đều có
`eval_set="annotated"` và `git.dirty=false`. Báo cáo sinh tự động:
[`s13_ranking_annotated_20260928.md`](../measurements/s13_ranking_annotated_20260928.md).

| Hạng annotated | Ứng viên | Model | Họ thắng | CV annotated mean ± sd | CV all | Δ |
|---:|---|---:|---|---:|---:|---:|
| 1 | f2 | 3 | cSEBB | 0.2383 ± 0.0562 | 0.2224 | +0.0159 |
| 2 | f4 | 6 | θ | 0.2354 ± 0.0585 | 0.2248 | +0.0105 |
| 3 | f1 | 3 | θ | 0.2286 ± 0.0601 | 0.2114 | +0.0171 |
| 4 | d | 3 | θ | 0.2285 ± 0.0570 | 0.2230 | +0.0054 |
| 5 | e | 6 | θ | 0.2237 ± 0.0665 | 0.2050 | +0.0186 |
| 6 | c | 3 | θ | 0.2212 ± 0.0498 | 0.2129 | +0.0083 |
| 7 | f3 | 6 | θ | 0.2070 ± 0.0560 | 0.1813 | +0.0257 |
| 8 | b | 1 | θ | 0.2031 ± 0.0565 | 0.1900 | +0.0131 |
| 9 | a | 4 | θ | 0.1620 ± 0.0226 | 0.1538 | +0.0082 |

Thứ tự đổi từ `f4/d/f2/c/f1/e/b/f3/a` trên `all` thành
`f2/f4/f1/d/e/c/f3/b/a` trên `annotated`; cả 9 điểm đều tăng. Chênh hạng 1–2 là **0.0029**, nhỏ
hơn sd giữa fold của f2 (**0.0562**), nên **không được gọi f2 là tốt hơn f4**. Bảng này chỉ chuẩn
bị dữ liệu cho S13 ngày 18/10; chưa chọn hệ thống và chưa mở test.

## Consequences

### Tích cực

- Vòng chọn và con số test cuối không còn phạt dự đoán đúng trên recording không có nhãn.
- Không tốn GPU; chỉ chạy lại CV trên dev.

### Đánh đổi

- Train vẫn mang lỗi mẫu âm (§3).
- Hai hệ số chấm cùng tồn tại (`all` cho số lịch sử, `annotated` từ S13) — mọi bảng phải ghi rõ
  tập chấm.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| (A) Giữ nguyên, chỉ ghi Hạn chế | Biết lỗi đo mà vẫn dùng cho vòng chọn cuối và con số headline |
| (C) Sinh lại split, train lại toàn bộ | Hàng chục giờ GPU cho ảnh hưởng đo được +0.002; đổi `data-v1.0` làm mất khả năng so với mọi số đã báo |
| Dùng nhãn monophonic làm GT polyphonic cho 14 recording | Monophonic chỉ gán nguồn nổi trội, không phải mọi nguồn — sẽ tạo FN giả |
