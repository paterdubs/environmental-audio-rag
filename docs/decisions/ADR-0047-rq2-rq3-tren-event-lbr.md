# ADR-0047 — Chạy lại caption template (RQ2) và RAG (RQ3) trên event LBR V2 và V3

**Status:** Accepted (người dùng chọn 10/11: chạy lại RQ2/RQ3 trên event LBR, cả V2 và V3, phạm vi
template EN/VI + RAG)
**Date:** 2026-11-10

## Context

Lượt mở test LBR (`98315fd`, ADR-0045 §8) cho V2 micro 0.2965 so với B0 0.1806, Δ +0.1159
[+0.0741, +0.1593]; V3 là cấu hình ứng dụng cho demo (ADR-0045 §11). Mọi số W5/W6 hiện có lại tính
trên event B0 (ADR-0044). Người dùng chọn đo lại để caption và RAG mô tả đúng hệ thống mới, thay vì
ghi hạn chế.

Hai ràng buộc kỹ thuật:

1. W5/W6 dựng timeline qua `e2e_timelines` (`scripts/generate_llm_captions.py`), vốn chỉ nhận
   posterior + θ/cSEBB.
2. Model LBR cuối fit trên đủ 5 fold OOF, tức đã thấy **mọi** recording dev. Áp nó lên dev cho số
   in-sample, đúng lỗi ADR-0044 §1 đã tránh với B0.

## Decision

### 1. Đầu vào

- **Test:** `sed_ensemble_B0_final_test_20261014T085016Z/predictions/test.npz` (artifact đã chấm ở
  O5 và lượt test LBR, không dump lại) + manifest run LBR đóng băng; event sinh bằng đúng
  `lbr_scored_boxes`/`lbr_events` như `evaluate_run`.
- **Validation (dev):** posterior `sed_filtered_B0_oof_dev_20261107T181008Z/predictions/dev.npz`
  (134 recording, như ADR-0044) + **event cross-fit**: `scripts.export_lbr_oof_events` lặp lại
  cross-fit lồng nhau của tầng C (cùng OOF nguồn, fold, biến thể, cấu hình), mỗi recording được chấm
  bằng model không thấy fold của nó, rồi giữ recording split `validation`. Manifest ghi micro F1 trên
  toàn bộ 564 recording OOF; **phải trùng** measurement tầng C (V2 điểm F1 0.333197, V3 ưu tiên
  phát hiện 0.230248), lệch thì dừng.
- **Kiểm trước commit (10/11, bản xem trước tree bẩn, chỉ đọc dev OOF, không đọc test):** micro OOF
  trên 564 recording trùng tầng C chính xác tới chữ số cuối: V2 điểm F1 0.3331973898858075, V3 ưu
  tiên phát hiện 0.23024830699774265; mỗi bản giữ 134 recording validation. Bản chính thức vẫn sinh
  lại trên tree sạch.
- `e2e_timelines` nhận manifest LBR qua `--postproc` kèm `--lbr-point` bắt buộc
  (`ml/postprocessing/lbr_timeline.py`); manifest run đóng băng trên split khác `test` bị từ chối.
  `model_version` của timeline/event là `<run LBR>:<điểm>`.
- Không đổi lexicon EN/VI, query set, BGE-M3, output parser đã khóa (ADR-0036), contract.

### 2. Cấu hình ghi trước

| Nhãn | Run LBR | Điểm vận hành | Vai trò |
|---|---|---|---|
| `lbrv2` | `sed_lbr_B0_20261109T172809Z` | `f1` | số chính của luận văn (cùng hệ SED với số SED chính) |
| `lbrv3` | `sed_lbr_B0v3_20261110T042337Z` | `recall_first` | đúng cấu hình demo phục vụ (DEMO.md) |

Không chấm thêm điểm vận hành nào khác; không chọn giữa V2/V3 từ số W5/W6.

### 3. Phạm vi

- **W6:** với mỗi nhãn, dựng lại corpus `validation` rồi `test` bằng `build_retrieval_index
  --replace`; bốn cấu hình (gold/parsed × retrieval/answers) như ADR-0044.
- **W5:** chỉ template EN và VI (`scripts.score_template_e2e`), mức `e2e`, `--eval-set annotated`;
  test báo thêm `all` làm độ nhạy. Ba nhánh LLM không chạy lại; số LLM vẫn trên f2 (ADR-0040).
- Đây là lần mở test **thứ ba** cho W5/W6 (sau S8 và S8-lite). So với B0 (ADR-0044 §4) chỉ mô tả;
  không đổi hệ thống phục vụ hay lựa chọn SED từ các số này.

### 4. Thứ tự

1. Code + test + ADR này commit; mọi bước dưới chạy trên tree sạch.
2. `export_lbr_oof_events` cho hai nhãn; kiểm micro OOF trùng tầng C.
3. Với `lbrv2` rồi `lbrv3`: W6 validation (4 cấu hình) → W5 template dev. Chỉ khi wiring đạt
   (contract, unsupported-claim, evidence thật) mới sang bước 4.
4. W6 test (4 cấu hình) → W5 template test, `lbrv2` trước, `lbrv3` sau, để DB demo kết thúc ở V3.
5. Sổ test, freeze artifact, STATUS, PAPER_NOTES.

## Alternatives considered

| Phương án | Lý do không chọn |
|---|---|
| Áp model LBR cuối lên dev | Model đã thấy dev; số validation lạc quan giả |
| Chỉ V2 hoặc chỉ V3 | Người dùng chọn cả hai: V2 khớp số SED chính, V3 khớp demo |
| Chạy lại ba nhánh LLM | ~1–1.5 ngày GPU; RQ2 về ràng buộc LLM đã có kết luận trên f2 |
| Giữ W5/W6 trên B0, ghi hạn chế | Người dùng chọn đo lại |

## Consequences

DB demo kết thúc với corpus V3 (validation cross-fit, test đóng băng). Corpus B0 tái dựng được từ
ADR-0044. Số validation của LBR không so được trực tiếp với B0 vì event dev đến từ cross-fit, khác
cách sinh; so sánh với B0 chỉ dùng test.

## Bổ sung 10/11 — kẹp biên event LBR ở nơi tiêu thụ

Lượt validation `lbrv3` dừng ở `canonicalize_timeline` ("invalid event bounds"). Nguyên nhân: box
sau tinh chỉnh có `offset` vượt độ dài recording; `apply_deltas` chỉ kẹp `onset ≥ 0`. Đo trên event
cross-fit đã export: V3 ưu tiên phát hiện có **14/945** event vượt cuối recording (ví dụ S-0030:
offset 141.675 s, recording 141.64 s; S-0236: 36.243 s so với 36.01 s), V2 điểm F1 có 0/400 trên dev.
Hệ quả thực tế: bật `EARAG_SERVED_LBR` thì một lần upload tương tự sẽ lỗi trong `Pipeline.timeline`.

Quyết định: `clip_events_to_duration` (`ml/postprocessing/lbr_apply.py`) kẹp event vào
`[0, duration]` và bỏ event không còn độ dài; dùng ở `lbr_postproc_events` (timeline caption/RAG,
cả run đóng băng lẫn event cross-fit) và `ServedSed.events`. **Không đổi `lbr_events`/`apply_deltas`**
nên mọi số event-F1, PSDS, thước ứng dụng đã đo (tầng C, lượt test `98315fd`) giữ nguyên; event-F1
vẫn tính trên box chưa kẹp, còn caption/RAG và demo dùng event đã kẹp. Phần lệch tối đa vài phần
mười giây ở cuối recording. Export cross-fit không sinh lại (SHA-256 đã khóa); kẹp áp lúc đọc.
`lbrv2` validation đã chạy trước bản sửa (0 event vượt trên dev nên kết quả không đổi); sinh lại cùng
`lbrv3` trên tree sạch sau commit bản sửa để mọi bản ghi cùng một revision.

## Bổ sung 10/11 — ghi trước lưới PSDS của LBR, đo lại một lần trên test (người dùng duyệt)

**Vấn đề.** PSDS-1/2 của V2 ở lượt test `98315fd` (0.2146 / 0.2960) thấp hơn B0 (0.3131 / 0.7310;
bản đầu ghi nhầm 0.3489 / 0.6987 của ensemble C v1, sửa theo ADR-0048 §4)
trong khi event-F1 cao hơn nhiều. Chẩn đoán chỉ trên dev OOF (564 recording, không đọc test):
điểm rescorer rất lệch (phân vị 50% = 3.7e-4, 75% = 0.021, 90% = 0.76) còn `T_GRID` bắt đầu ở 0.005,
nên ~55% box không bao giờ vào đường PSD-ROC. Đường cong bị cắt ở phía eFPR cao. Trên dev, lưới phủ
mọi phân vị cho PSDS-1 0.3676 (B0 0.3512) và PSDS-2 0.6535 (B0 0.7504).

**Ghi trước.**

1. Lưới PSDS mới của cả hai run LBR: `numpy.geomspace(1e-5, 0.99, 48)` (cố định, chọn theo hình dạng
   phân phối điểm trên dev, **không tinh chỉnh** theo bất kỳ số PSDS nào; không thử lưới khác).
2. Model, ngưỡng đóng băng, điểm vận hành, cách dựng event: giữ nguyên. Chỉ đổi tập operating point
   đưa vào `psds_score`. Event-F1, thước ứng dụng không đổi.
3. Đo một lần trên test annotated (`sed_ensemble_B0_final_test_20261014T085016Z/predictions/test.npz`)
   cho `sed_lbr_B0_20261109T172809Z` và `sed_lbr_B0v3_20261110T042337Z`, bằng
   `scripts.report_lbr_psds_grid`. Báo **cả số cũ (T_GRID) lẫn số mới**, kèm số điểm và số event ở
   điểm thấp nhất. Số cũ không bị thay thế.
4. Không chọn lại hệ thống, điểm vận hành hay lưới từ số test. Nếu PSDS-2 vẫn thấp hơn B0, báo
   nguyên văn (trên dev, một phần do tinh chỉnh biên: chỉ-tinh-chỉnh 0.6602 so với B0 0.7504).

## Bổ sung 10/11 — kết quả

Lượt mở test thứ ba cho W5/W6 đã chạy theo §4 trên tree sạch; chỉ mô tả, không đổi hệ thống phục vụ.

**W5, template (test annotated n=139, EN và VI):** hallucination, omission, forbidden term và
over-specific đều 0.0000 ở B0, V2 `f1`, V3 `recall_first`. Template sinh tất định từ timeline nên 0
lỗi chứng minh đường ống và lexicon, không chứng minh khả năng tổng quát.

**W6, nDCG@10 test, gold filter, EN [CI 95%]:**

| Cấu hình | B0 (ADR-0044) | LBR V2 `f1` | LBR V3 `recall_first` |
|---|---:|---:|---:|
| structured_only | 0.392 [0.315, 0.469] | 0.411 [0.337, 0.486] | 0.683 [0.624, 0.740] |
| vector_only | 0.458 [0.391, 0.522] | 0.491 [0.432, 0.553] | 0.630 [0.579, 0.679] |
| hybrid | 0.383 [0.307, 0.461] | 0.404 [0.332, 0.478] | 0.670 [0.610, 0.729] |

Với `parsed` filter các số thấp hơn gold không quá 0.02 ở mọi cấu hình. Câu trả lời ràng buộc
evidence: unsupported-claim 0.000, contract và evidence thật 97/97 ở cả ba; "có trả lời" hybrid/en
58/97 (B0), 62/97 (V2), 95/97 (V3); "trích đúng GT" 0.915, 0.899, 0.712.

**Cách đọc.** V2 so với B0: CI chồng lấn, không gọi là tốt hơn. V3 nhảy mạnh vì đưa 668/740 event vào
corpus; relevance lấy từ ground truth nên nhiều event hơn làm nDCG@10 và độ phủ tăng, còn "trích đúng
GT" giảm — đọc kèm precision giao nhau 0.7812, không đọc như retrieval tốt hơn. Validation của LBR
dùng event cross-fit nên không so trực tiếp với B0.

**Số PSDS đo lại (lưới ghi trước).** Xem
[lbr_psds_grid_20261110_annotated.md](../measurements/lbr_psds_grid_20261110_annotated.md):
V2 PSDS-1 0.2146 → 0.3512, PSDS-2 0.2960 → 0.6116 (B0 0.3131 / 0.7310 trên lưới tuyến tính, khác
lưới; cùng lưới ở ADR-0048 §3); V3 0.3354 → 0.3369 và
0.6158 → 0.6167. Mô hình, điểm vận hành và event-F1 không đổi. PSDS-2 của V2 vẫn thấp hơn B0.
