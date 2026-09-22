# STATUS.md — Trạng thái có bằng chứng

**Cập nhật:** 2026-09-22, sau Phase 1 (xác minh archive + git baseline)
**Git:** `3c80110` · **Taxonomy:** `0.1` / `67ca8a8c…`

> Đây là nguồn chân lý duy nhất về **phần đã chạy được**. Kiến trúc dự kiến nằm
> trong [SYSTEM.md](SYSTEM.md). Mọi dòng trong file này phải trỏ tới một artifact
> kiểm chứng được.

---

## 0. Cổng hiện tại

**D3 — audit duplicate.** DataSED exact duplicate (T1) đã xong. Còn thiếu:
duplicate nội bộ DataSEC, T2/T3, và **duplicate xuyên DataSEC–DataSED**.

Không freeze split, không chạy thí nghiệm transfer trước khi D3 xong.

---

## 1. Snapshot

| Thành phần | Trạng thái | Bằng chứng |
|---|---|---|
| Scope | ✅ Đã chốt | [ADR-0001](decisions/ADR-0001-scope-and-datasets.md) |
| Quyết định kiến trúc | ✅ 6 ADR | [decisions/](decisions/) |
| Repository scaffold | ✅ | `c9ccbc6`, 98 file |
| **Git baseline** | ✅ | `c9ccbc6`, `3c80110` — trước đó **chưa có commit nào** |
| DataSED download + verify | ✅ | 4,510,378,259 B, MD5 `44e093f6…` |
| **DataSEC download + verify** | ✅ | 6,414,663,316 B, MD5 `29fa9b8c…`, verify 10.3 s |
| Archive audit (D0) | ✅ cả hai `pass` | [measurements/archive_audit_20260922.md](measurements/archive_audit_20260922.md) |
| **Taxonomy xác minh từ archive** | ✅ | 22/22 coarse, 10/10 nhóm subclass, 0 unmapped |
| DataSED inventory (D1) | ✅ | `datased_inventory_summary.json` |
| DataSED annotation (D2) | ✅ | `datased_preparation_audit.json` |
| DataSEC giải nén + inventory (D1) | ○ | Archive đã verify, chưa giải nén |
| Dedup T1 DataSED | ✅ | 8 nhóm exact duplicate |
| **Dedup T2/T3 + xuyên dataset (D3)** | ○ | **Cổng đang chặn** |
| Split DataSED | ◐ candidate | 435/142/140, chưa freeze |
| Log-mel v1 | ✅ | 717/717 file |
| SED baseline polyphonic | ◐ dò đường | frame macro-F1 test 0.359448 |
| Event-based F1 / PSDS | ○ | Chưa có post-processing hiệu chuẩn |
| DataSEC classifier | ○ | |
| Transfer DataSEC → DataSED | ○ | Phụ thuộc D3 |
| Grounded caption | ○ | Chỉ có contract [SYSTEM §6](SYSTEM.md) |
| RAG / retrieval | ○ | Chỉ có thiết kế [SYSTEM §7](SYSTEM.md) |
| API / inference / frontend | ○ | Chỉ có thư mục scaffold |
| CI | ○ | |
| Test suite | ✅ | 18 test pass, ruff sạch |

---

## 2. Artifact archive audit

Sinh bằng `python -m scripts.audit_archive` và `scripts.report_archive_audit`.

| Trường | DataSEC | DataSED |
|---|---:|---:|
| Record DOI | `10.5281/zenodo.17033970` | `10.5281/zenodo.15346092` |
| License | `cc-by-nc-sa-4.0` | `cc-by-nc-sa-4.0` |
| Archive bytes | 6,414,663,316 | 4,510,378,259 |
| MD5 khớp | ✅ | ✅ |
| ZIP entries | 5,099 | 722 |
| Audio files | 5,048 | 717 |
| Giải nén (GiB) | 7.01 | 5.55 |
| Bảng annotation | 0 | 2 |
| **LICENSE/README trong archive** | **0** | **0** |
| Coarse label trong layout | 22 | 0 (nhãn ở CSV) |
| Subclass label trong layout | 28 | 0 |
| Nhãn ngoài taxonomy | 0 | 0 |
| Verdict | `pass` | `pass` |

---

## 3. Artifact DataSED

- Inventory: 717 WAV, **18.6847 giờ**, 44,100 Hz (717/717), mono 716 / stereo 1.
- Annotation: **4,034** polyphonic event / 21 class / 703 recording;
  **4,309** monophonic event / 22 class / 717 recording.
- **14 recording không có polyphonic target event** — giữ làm recording âm tính.
- Exact duplicate (T1): **8 nhóm**, mỗi nhóm 2 recording.
- Log-mel v1: 717/717 file, 16 kHz, 64 mel, hop 320 (50 fps), float16.
- Candidate split SHA-256: `656c1851de7c22a5eb6b2c2dc2b20397ad1bce98b136c591b7fe68b88cd130b1`.

Parser giữ nguyên `raw_class_label`, gồm nhãn nguồn `Cat fight and moans` (số ít,
khác DataSEC dùng số nhiều), rồi ánh xạ sang taxonomy `0.1`.

---

## 4. Artifact DataSEC

Từ archive audit — **chưa giải nén**, nên chưa có duration, sample rate hay hash
từng file.

- 5,048 WAV, 22 coarse class, 28 subclass.
- Nhãn mã hóa bằng **cây thư mục**, không có bảng annotation.
- Phân bố **lệch 38:1**: `voices` 1,900 (37.6%), `music` 1,001 (19.8%),
  nhỏ nhất `cat_fights_and_moans` 50 (1.0%).
- **`voices` + `music` = 57.5%** toàn dataset.
- Bốn subclass dưới 25 file: `Crickets` 20, `Olive shaker` 20, `Magpies` 21,
  `Lawn mower` 21.

Bảng đầy đủ: [SYSTEM §3.4](SYSTEM.md) · [measurements/archive_audit_20260922.md](measurements/archive_audit_20260922.md).

---

## 5. Baseline SED — và bốn lý do nó chưa phải kết quả

Run `sed_polyphonic_20260922T115340Z`, 8 epoch, batch 8, lr 1e-3, window 10 s,
threshold cố định 0.5, seed 20260922:

| Metric | Giá trị |
|---|---:|
| Best validation frame macro-F1 | 0.357305 |
| **Test frame macro-F1** | **0.359448** |
| Test frame macro average precision | 0.466312 |
| Frame đánh giá | 671,570 |

| # | Vì sao chưa phải kết quả báo cáo |
|---:|---|
| 1 | **Frame-level**, không phải event-based — không so được với bất kỳ paper nào |
| 2 | Threshold **0.5 cố định**, chưa hiệu chuẩn per-class, trong khi `pos_weight` tới 50 |
| 3 | Chạy trên split **candidate**, chưa qua D3/D4 |
| 4 | `git.revision: "HEAD"`, `dirty: true` — **không tái lập chính xác được** |

Per-class: [measurements/sed_polyphonic_20260922T115340Z.md](measurements/sed_polyphonic_20260922T115340Z.md).
Thấp nhất: `crows_seagulls_magpies` 0.134646, `horn` 0.134842.
Cao nhất: `cicadas_and_crickets` 0.676579.

---

## 6. Ba phát hiện của Phase 1 làm đổi thiết kế

### 6.1 Imbalance 38:1 → cần class-balanced sampling

`voices` + `music` chiếm 57.5% DataSEC, và đây là hai lớp ít liên quan nhất tới
đánh giá tiếng ồn môi trường. Pretraining với sampling đồng nhất sẽ cho một
encoder chuyên phân biệt nói với nhạc, làm RQ1 đo sai thứ.

→ [ADR-0002](decisions/ADR-0002-encoder-va-nhanh-transfer.md) yêu cầu
class-balanced sampling; ablation A6 định lượng ảnh hưởng.

### 6.2 Bốn subclass có test 3–4 mẫu → metric vô nghĩa

Một mẫu sai làm F1 nhảy 25–33 điểm phần trăm.

→ [ADR-0006](decisions/ADR-0006-danh-gia-subclass.md) và
[evaluation_protocol §4](evaluation_protocol.md): báo số tuyệt đối, không báo tỷ lệ.

### 6.3 Không archive nào chứa LICENSE/README

License `cc-by-nc-sa-4.0` chỉ lấy được từ Zenodo record metadata. Thành phần
**SA** nghĩa là checkpoint nếu công bố phải cùng license, không được MIT/Apache.

→ Đã sửa [DATA_PLAN §2–§3](DATA_PLAN.md) vốn giả định sai rằng archive có LICENSE.

---

## 7. Rủi ro R1 nâng lên mức CAO

Hai dataset do **cùng 6 tác giả** công bố (Fredianelli, Artuso, Pompei, Licitra,
Iannace, Akbaba), cùng miền đo ngoài trời, cách nhau 4 tháng.

Nếu một phần DataSEC được cắt từ chính recording của DataSED, thì "pretrain rồi
fine-tune" trở thành "train trên test set", và Δ transfer của RQ1 là leakage chứ
không phải transfer.

Cổng D3 vì vậy không phải thủ tục hình thức. Ngưỡng báo động và cách xử lý:
[DATA_PLAN §7.6](DATA_PLAN.md).

---

## 8. Blocker còn lại — theo thứ tự

1. **`scripts.find_duplicates`** — T1/T2/T3, nội bộ và xuyên dataset. Chặn D3.
2. **`scripts.check_leakage`** — 5 kiểm của [DATA_PLAN §8.4](DATA_PLAN.md). Chặn D4.
3. Giải nén + inventory DataSEC (D1).
4. Freeze split sau D3, ghi SHA-256 mới (D4).
5. Train DataSEC classifier (E1) và ba nhánh SED (E2/E3).
6. Post-processing hiệu chuẩn, event-based F1, PSDS (E4).

---

## 9. Tài liệu

| File | Dòng | Trạng thái |
|---|---:|---|
| [SYSTEM.md](SYSTEM.md) | 1,584 | ✅ viết lại 22/09 |
| [DATA_PLAN.md](DATA_PLAN.md) | 578 | ✅ viết lại 22/09 |
| [taxonomy.md](taxonomy.md) | 554 | ✅ viết lại 22/09 |
| [PLAN.md](PLAN.md) | ~300 | ✅ viết lại 22/09 |
| [evaluation_protocol.md](evaluation_protocol.md) | 389 | ✅ viết lại 22/09 |
| [CLAUDE.md](../CLAUDE.md) | ~330 | ✅ mới 22/09 |
| [decisions/](decisions/) | 6 ADR | ✅ ADR-0002…0006 mới 22/09 |
| [TRAINING_OPS_PLAN.md](TRAINING_OPS_PLAN.md) | 69 | ○ chờ viết lại |
| [annotation_guideline.md](annotation_guideline.md) | 86 | ○ chờ viết lại |
| [RELATED_WORK.md](RELATED_WORK.md) | 61 | ○ chờ viết lại |
| [data_inventory.md](data_inventory.md) | 29 | ○ chờ sinh lại từ manifest |
| `contracts/*.schema.json` | 0/6 | ○ chưa tồn tại |
