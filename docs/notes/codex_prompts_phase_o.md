# Chuỗi prompt giao việc cho Codex — giai đoạn O (từ lượt 6)

Soạn 08/10/2026 tối. Người dùng copy từng khối ``` vào Codex **theo đúng thứ tự**. Mỗi lượt có
**điều kiện bắt đầu**; chưa đủ điều kiện thì chưa giao. Lượt 1–5 (XO-1..XO-19) đã xong và đã
merge vào master (`5cb948d`).

| Lượt | Task | Bắt đầu khi | Cần Claude trước? |
|---|---|---|---|
| 6 | XO-20 bảng tầng S tổng · XO-21 chẩn đoán "frame mAP tăng, event-F1 không" · XO-22 lỗi biên theo run · XO-23 hàng đợi OOF có bước chồng lấn | **Ngay** (XO-20/21 tự chờ file CV) | Không |
| 7 | XO-24 báo cáo B0 OOF · XO-25 kiểm hồi quy ensemble 5 fold | CV B0 OOF hop 10 s **và** hop 5 s đã xong (hai file `*_cv_selection_annotated.json` trong cả hai thư mục `ml/runs/sed_oof_B0_*`) | Không |
| 8 | XO-26 công cụ O-F (nhãn mạnh giả cho pool DataSEC) | Claude ghi mục "[MỞ] Claude → Codex — đặc tả O-F" ở AGENT_SYNC §6 | **Có** |
| 9 | XO-27 hỗ trợ O-E (target biên + đánh giá) | Claude ghi mục "[MỞ] Claude → Codex — đặc tả O-E" ở AGENT_SYNC §6 | **Có** |
| 10 | XO-28 chuẩn bị tầng C cho test một lần (sổ test, freeze, runbook) | Claude commit lựa chọn tầng C | **Có** |

Luật cứng chung (đã có trong mọi prompt bên dưới): worktree `..\earag-codex-o`, nhánh
`codex/phase-o`; không GPU; không mở `predictions/test.npz`; không ghi vào tree chính
`..\environmental-audio-rag` (chỉ đọc `ml/runs` ở đó); không `pip install`, không push; mỗi task
chạy `pytest` và `ruff` không qua pipe, cập nhật AGENT_SYNC §3.O/§4/§5 rồi commit; số lệch kỳ
vọng hoặc phản biện ghi §6; không sửa file của Claude (`train_sed.py`, `select_*`, `build_oof.py`,
`frame_mn_finetune.py`, `sed_factory.py`, `features.py`, CLAUDE.md, PLAN, STATUS, PAPER_NOTES,
ADR). XO-11 (phục vụ suy luận chồng lấn) vẫn chặn cho tới khi Claude mở.

---

## Lượt 6 — giao ngay

```
Tiếp giai đoạn O, lượt 6. Luật cứng như các lượt trước: worktree ..\earag-codex-o, nhánh
codex/phase-o, không GPU, không mở predictions/test.npz, không ghi vào tree chính
..\environmental-audio-rag (chỉ đọc ml/runs ở đó), không pip install/push, lệch số → §6,
không sửa file của Claude. XO-11 vẫn chặn.

Bắt đầu: git -C ..\earag-codex-o merge master (master = 5cb948d, đã có lượt 5 của bạn và
recipe oc_gru/oc_tf/oc_tf_kd + DO-4 của Claude). Ghi XO-20..XO-23 vào §3.O.

Bối cảnh (dev, CV 5 fold annotated; luật tầng S = phải vượt seed T2b tốt nhất 0.2330):
- T2b seed 172924Z/180358Z/185137Z; O-B 20261008T062333Z (--train-fixes);
  O-C GRU 20261008T083632Z (frame mAP 0.756, họ thắng 0.2318, không qua);
  DO-4 20261008T131138Z (--train-fixes --window-sampling class_balanced; frame mAP 0.743,
  họ thắng 0.2174, không qua); O-C TF256 KD 20261008T135047Z và TF256 strong
  20261008T145841Z (CV đang chạy). Tất cả là sed_polyphonic_<id> trong ml/runs.
- Mẫu hình cần mô tả: GRU và DO-4 tăng frame mAP nhưng không tăng event-F1.

XO-20 (ưu tiên 1) — scripts/report_tier_s.py: một bảng tầng S cho mọi run sàng lọc so với
  ba seed T2b. Cột: run, recipe/cờ (đọc manifest), frame mAP tốt nhất (metrics.json),
  θ CV mean±sd, cSEBB CV mean±sd (cấu hình đã chọn), họ thắng (luật S13: hòa giữ θ), so
  seed tốt nhất (Δ, "qua"/"không qua"), số fold cao hơn seed tốt nhất, macro/micro full-dev
  in-sample của họ thắng (dùng lại code report_screening_per_class, ghi rõ in-sample).
  Chỉ đưa run có đủ hai file *_cv_selection_annotated.json; run thiếu liệt kê ở cuối là
  "đang chờ". Ra docs/measurements/tier_s_20261009.{md,json}. Chạy lại được khi có run mới
  (--stamp). Không kết luận ngoài luật đã ghi.

XO-21 (ưu tiên 2) — scripts/report_detection_gap.py: mô tả vì sao frame mAP tăng mà event-F1
  không tăng, cho T2b 172924Z, O-C GRU, DO-4, TF256 KD (và TF strong nếu đã có CV). Chỉ dev
  annotated, chỉ mô tả:
  - theo lớp: frame AP; số event dự đoán/tham chiếu với hậu xử lý họ thắng; tỷ lệ frame có
    p > θ đã chọn so với tỷ lệ frame dương thật;
  - "θ tối ưu theo lớp" in-sample (quét lưới θ có sẵn, từng lớp) so với θ global đã chọn —
    chỉ để đo khoảng cách, ghi rõ không dùng để chọn (A2: θ per-class overfit dev);
  - phân rã lỗi event: insertion/deletion/substitution, onset-only/offset-only F1.
  Ra docs/measurements/detection_gap_20261009.{md,json}. Giả thuyết ghi rõ là giả thuyết.

XO-22 (ưu tiên 3) — chạy scripts.report_boundary_errors (đã có, chỉ dev) cho bốn run trên
  bằng nhiều --run "nhãn=ml/runs/<run>", --out-dir trong worktree của bạn rồi commit
  measurement. Nếu script cần postproc của run, dùng file *_annotated đã có; thiếu thì ghi
  §6, không tự chạy selector.

XO-23 (ưu tiên 4) — mở rộng scripts/run_oof_queue.py (của bạn): tùy chọn
  --rewindow HOP:WEIGHTING (ví dụ 5:triangular:0.3). Khi bật: sau 5 run fold, chạy
  dump_predictions <run> --split dev --hop-seconds HOP --weighting WEIGHTING --label
  <label>_f<k>_h<HOP> cho từng fold, build_oof hai lần (thô và chồng lấn, nhãn
  <label>_h10 và <label>_h<HOP>), rồi hai selector cho từng OOF. Resume theo từng bước;
  test bằng runner giả; --dry-run in đúng thứ tự lệnh. KHÔNG chạy thật.

Mỗi task xong: pytest + ruff (không pipe), cập nhật §3.O/§4/§5, commit. Xong lượt báo commit
hash và các điểm ở §6.
```

---

## Lượt 7 — khi CV B0 OOF xong

Điều kiện: cả `ml/runs/sed_oof_B0_h10_*` và `ml/runs/sed_oof_B0_h5_*` đều có đủ
`postproc_cv_selection_annotated.json` và `sebb_cv_selection_annotated.json`.

```
Tiếp giai đoạn O, lượt 7. Luật cứng như các lượt trước (worktree ..\earag-codex-o, nhánh
codex/phase-o, không GPU, không mở predictions/test.npz, không ghi tree chính, không pip
install/push, lệch số → §6, không sửa file của Claude). Bắt đầu: git merge master.

Bối cảnh: B0 (ADR-0041 §2 = T2b + --train-fixes + suy luận chồng lấn hop 5 s gộp tam giác
sàn 0.3) đã train 5 fold (--cv-fold 0..4, seed 20260922) và ghép OOF trên 564 recording:
ml/runs/sed_oof_B0_h10_<ts> (dự đoán thô) và ml/runs/sed_oof_B0_h5_<ts> (chồng lấn). CV
θ/cSEBB annotated đã chạy xong cho cả hai (prior theo fold, e428e2b).

XO-24 (ưu tiên 1) — scripts/report_b0_oof.py, chỉ mô tả:
  - với mỗi OOF: họ thắng, cấu hình, CV mean±sd, 5 giá trị fold; macro/micro full-OOF của
    họ thắng (refit đã lưu), PSDS không cần;
  - theo fold mô hình (0..4): micro/macro trên recording của fold đó, số recording, số event
    tham chiếu; phân rã theo nguồn recording (thuộc train gốc hay dev gốc) — đây là điểm cần
    xem: OOF trên dev gốc có gần số CV dev của f2 (0.2383) không;
  - so h5 với h10 cùng phép chấm: Δ, số fold cao hơn, bootstrap ghép cặp theo recording
    (dùng lại ml/evaluation/multirun.paired_branch_bootstrap như report_oof, 1000 lần, seed
    20260922). Ghi rõ đây là kiểm tra thành phần chồng lấn của B0, không phải lựa chọn.
  Ra docs/measurements/b0_oof_20261009.{md,json}.

XO-25 (ưu tiên 2) — kiểm toàn vẹn OOF của B0, chỉ đọc:
  - mỗi run fold k (5 run sed_polyphonic_* có config.cv_fold = k, liệt kê trong manifest của
    sed_oof_B0_h10) có predictions/dev.npz chứa đúng recording của fold k trong
    data/splits/datased_trainval_folds.csv (SHA eaa30dc1…); 5 fold rời nhau, hợp lại đủ 564;
  - tập train của fold k, dựng lại bằng scripts.train_sed.apply_cv_fold + train_tables
    (gọi hàm, không sửa), không chứa recording nào của fold k và không chứa recording test;
  - các cặp gán đôi bị gộp (manifest train_fixes.merged_duplicates) không bắc qua fold.
  Ra docs/measurements/b0_oof_integrity_20261009.{md,json}. Lỗi → §6 kèm danh sách recording.
  Lưu ý: không dựng ensemble 5 model fold trên dev gốc — mọi model fold đã thấy 4/5 dev gốc
  khi train, nên số đó vô nghĩa.

Mỗi task xong: pytest + ruff (không pipe), cập nhật §3.O/§4/§5, commit. Báo hash và §6.
```

---

## Lượt 8 — O-F, chờ đặc tả của Claude

Điều kiện: AGENT_SYNC §6 có mục **"[MỞ] Claude → Codex — đặc tả O-F"** (teacher, ngưỡng,
cách cắt clip, định dạng nhãn giả). Claude khóa các lựa chọn đó trước, vì chúng ảnh hưởng
trực tiếp tới RQ1b.

```
Tiếp giai đoạn O, lượt 8. Luật cứng như các lượt trước (worktree ..\earag-codex-o, nhánh
codex/phase-o, không GPU, không mở predictions/test.npz, không ghi tree chính, không pip
install/push, lệch số → §6, không sửa file của Claude). Bắt đầu: git merge master.

Đọc docs/AGENT_SYNC.md §6 mục "[MỞ] Claude → Codex — đặc tả O-F" và làm đúng đặc tả đó.

XO-26 — công cụ nhãn mạnh giả cho pool DataSEC (data/manifests/datasec_o_f_pool.csv, 2.846
  clip): script sinh lệnh/đọc kết quả theo đặc tả, kiểm hash WAV với pool, validator cho file
  nhãn giả (cột, khoảng thời gian trong độ dài clip, lớp thuộc 21 lớp polyphonic, nhãn lớp
  của clip phải khớp nhãn thư mục DataSEC). Phần suy luận teacher cần GPU: chỉ viết +
  test trên 2–3 clip bằng CPU, KHÔNG chạy toàn pool — Claude chạy.
  Báo cáo mô tả pool sau khi có nhãn giả do Claude sinh ra (nếu đã có): số event/clip,
  thời lượng, độ phủ theo lớp. Không tạo hoặc sửa nhãn bằng tay.

Mỗi task xong: pytest + ruff (không pipe), cập nhật §3.O/§4/§5, commit. Báo hash và §6.
```

---

## Lượt 9 — O-E, chờ đặc tả của Claude

Điều kiện: AGENT_SYNC §6 có mục **"[MỞ] Claude → Codex — đặc tả O-E"** (Claude đã khóa các
điểm mở của XO-10: init, đơn vị IoU, k theo lớp, cách ghép cửa sổ).

```
Tiếp giai đoạn O, lượt 9. Luật cứng như các lượt trước (worktree ..\earag-codex-o, nhánh
codex/phase-o, không GPU, không mở predictions/test.npz, không ghi tree chính, không pip
install/push, lệch số → §6, không sửa file của Claude). Bắt đầu: git merge master.

Đọc docs/AGENT_SYNC.md §6 mục "[MỞ] Claude → Codex — đặc tả O-E". Phần model/loss do Claude
viết; bạn làm phần phụ trợ đã ghi trong mục đó (dự kiến: sinh target onset/offset từ
annotation theo lưới nhãn, kiểm bất biến target trên dữ liệu thật, báo cáo phân bố khoảng
cách tới biên theo lớp, và metric biên mô tả trên dev cho run O-E so với T2b).

XO-27 — làm đúng các mục được giao trong đặc tả; mọi số trên dev; không chạy train.

Mỗi task xong: pytest + ruff (không pipe), cập nhật §3.O/§4/§5, commit. Báo hash và §6.
```

---

## Lượt 10 — chuẩn bị test một lần, chờ Claude commit lựa chọn tầng C

Điều kiện: Claude đã commit lựa chọn tầng C (measurement `oof_selection_*` + cập nhật ADR-0041)
**trước** khi sinh bất kỳ logit test nào.

```
Tiếp giai đoạn O, lượt 10. Luật cứng như các lượt trước (worktree ..\earag-codex-o, nhánh
codex/phase-o, không GPU, không mở predictions/test.npz, không ghi tree chính, không pip
install/push, lệch số → §6, không sửa file của Claude). Bắt đầu: git merge master.

Claude đã commit lựa chọn tầng C (đọc docs/measurements/oof_selection_*.md và ADR-0041).
Test chạy đúng một lần cho: hệ thống cuối, B0, tối đa 2 ablation ghi trước (ADR-0041 §2).

XO-28 (chuẩn bị, KHÔNG mở test):
  - Runbook docs/notes/test_once_phase_o.md: danh sách lệnh chính xác (dump test cho từng
    model fold, ensemble 5 fold, evaluate_run --eval-set annotated với postproc đã khóa),
    thứ tự, artifact đầu ra, và kiểm trước khi chạy (tree sạch, commit lựa chọn có trước,
    hash postproc/split/taxonomy khớp). Claude chạy runbook, bạn không chạy.
  - Mở rộng report_test_ledger/freeze_artifacts nếu runbook sinh loại run mới (ensemble
    fold); test bằng manifest giả. Không đọc file test thật.
  - Script so sánh sau test (chỉ đọc evaluation đã lưu): hệ thống cuối vs B0 vs f2 bằng
    bootstrap ghép cặp trên 139 recording annotated; chạy thử bằng fixture.

Mỗi task xong: pytest + ruff (không pipe), cập nhật §3.O/§4/§5, commit. Báo hash và §6.
```
