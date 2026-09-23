# AGENT_SYNC.md — bảng điều phối hai agent

> **File này là kênh liên lạc duy nhất giữa Claude Code và Codex.**
> Đọc **toàn bộ** file trước khi chạm vào bất kỳ file nào khác.
> Cập nhật **ngay sau** mỗi task, không gom lại cuối phiên.

---

## 0. Vai trò

| | Claude Code | Codex |
|---|---|---|
| Vai | **Agent chính** | **Agent thực thi** |
| Quyết định kiến trúc, viết ADR | ✅ | ❌ (đề xuất, không tự quyết) |
| Chia task, đặt nghiệm thu | ✅ | ❌ |
| Viết code theo đặc tả đã chốt | ✅ | ✅ (phần lớn) |
| Chạy thí nghiệm dài, trích feature | ✅ | ✅ |
| Suy luận, phân tích, gỡ lỗi, nêu vấn đề | ✅ **bắt buộc** | ✅ **bắt buộc** |
| Sửa `CLAUDE.md`, `PLAN.md`, `docs/decisions/` | ✅ | ❌ |

**Codex không phải máy gõ code.** Codex phải phản biện khi đặc tả sai, và
**dừng lại báo** thay vì làm theo một yêu cầu mà mình đo được là hỏng. Một task
bị Codex bác bỏ có lý do kèm số đo là một task **thành công**.

---

## 1. Quy tắc chống giẫm chân

### 1.1 Sở hữu file

Chỉ agent sở hữu mới được **sửa** file trong vùng của mình. Agent kia được **đọc**
thoải mái.

| Vùng | Chủ |
|---|---|
| `CLAUDE.md`, `docs/PLAN.md`, `docs/decisions/**` | Claude |
| `docs/AGENT_SYNC.md` §3 (task board) | Claude |
| `docs/AGENT_SYNC.md` §4 (nhật ký) | **cả hai, append-only** |
| `docs/AGENT_SYNC.md` §5 (dữ kiện) | **cả hai, append-only** |
| `docs/AGENT_SYNC.md` §6 (chặn/hỏi) | **cả hai** |
| Mọi vùng khác | ghi ở cột `Chủ` của task board §3 |

**Muốn sửa file ngoài vùng của mình → ghi vào §6, không tự sửa.**

### 1.2 Không bao giờ

- ❌ `git commit`, `git tag`, `git push` khi chưa được người dùng cho phép.
- ❌ Sửa file mà agent kia đang giữ (`🔒` ở §3).
- ❌ Chạy lại `scripts.create_splits datased` — split đã đóng băng
  ([data-v1.0](../data/splits/datased_polyphonic.frozen.json)). Cổng sẽ từ chối.
- ❌ Chạm test set để tuning bất cứ thứ gì.
- ❌ Ghi "xong" khi chưa có command chạy được **và** artifact kiểm chứng.

### 1.3 Nhịp

1. Đọc §3 → chọn task `TODO` thuộc về mình → đổi thành `🔒 <tên> <giờ>`.
2. Làm. Gặp vấn đề → §6 ngay, không chờ hết task.
3. Xong → đổi `✅`, thêm dòng §4, thêm dữ kiện §5 nếu có số mới.
4. Chạy `pytest -q` + `ruff check .` trước khi đánh `✅`.

---

## 2. Trạng thái nền (cập nhật 23/09/2026)

Cổng dữ liệu **đã đóng**, tag `data-v1.0`.

| | |
|---|---|
| Split DataSED | **đóng băng** 438/137/142, sha256 `d2924a5e45c2b271…` |
| DataSEC | 5,048 file · 23.7082 h · **44.1 kHz** mono · **chưa có split** |
| DataSED | 717 file · 18.6847 h · 44.1 kHz |
| Rò rỉ xuyên dataset | 11 clip = 0.2179% → dải `minor`, RQ1 hợp lệ |
| Exclusions | 143 dòng (132 luật nội bộ + 11 người quyết định) |
| Test | 218 pass, ruff sạch |
| Taxonomy sha256 | `67ca8a8c53278cd438d7d06a4ba09e277f3f9a6df99460bdbec1d3a927729a3a` |

**Đọc bắt buộc trước khi code:** [CLAUDE.md](../CLAUDE.md) §4–§6,
[PLAN.md](PLAN.md) W2, [ADR-0002](decisions/ADR-0002-encoder-va-nhanh-transfer.md),
[ADR-0006](decisions/ADR-0006-danh-gia-subclass.md),
[ADR-0007](decisions/ADR-0007-fingerprint-va-luat-dedup.md),
[ADR-0009](decisions/ADR-0009-nguong-phu-thuoc-overlap.md).

---

## 3. Bảng task

Trạng thái: `TODO` · `🔒 <agent> <giờ>` đang làm · `✅` xong · `⛔` bị chặn (xem §6)

| ID | Task | Chủ | Vùng file | Phụ thuộc | Trạng thái |
|---|---|---|---|---|---|
| — | *(Claude điền đầu phiên)* | | | | |

---

## 4. Nhật ký — append-only

Định dạng một dòng, mới nhất **ở trên cùng**:

```
[HH:MM] <agent> <task-id> — <đã làm gì> · <artifact hoặc command kiểm chứng>
```

<!-- APPEND Ở NGAY DƯỚI DÒNG NÀY -->

---

## 5. Dữ kiện đã đo — append-only

Chỉ ghi số **đã có artifact**. Không ghi ước lượng, không ghi cảm giác.
Đây là nơi agent kia lấy thông tin mà không phải đo lại.

| Dữ kiện | Giá trị | Nguồn | Ai đo |
|---|---|---|---|
| DataSEC sample rate | 44.1 kHz, 5,048/5,048 | `datasec_inventory_summary.json` | Claude |
| DataSEC cụm cohesion lớn nhất | **326 file (6.5%)** | `split_cohesion_pairs.csv` | Claude |
| DataSED cụm cohesion lớn nhất | 4 file (0.6%) | cùng trên | Claude |
| Clip DataSEC < 3 s | 1,464 (29.0%) | `datasec_inventory.csv` | Claude |
| Clip DataSEC < 1 s | 464 (9.2%) | cùng trên | Claude |
| Imbalance DataSEC | 38:1; `voices`+`music` = 57.5% | `datasec_archive_audit.json` | Claude |
| Collar 0.2 s vs nhãn | chỉ **67/94** biên đạt | `annotation_consistency_20260923.md` | Claude |
| Cặp lớp bất đồng trong ground truth | `lawn_mower…`↔`propeller_aircrafts`; `vacuum…`↔`lawn_mower…` | cùng trên | Claude |

---

## 6. Chặn, hỏi, phản biện

Ghi ở đây khi: bị chặn · cần sửa file ngoài vùng · **không đồng ý với một task**.
Agent kia phải trả lời trước khi task liên quan đi tiếp.

```
### [MỞ] <agent> — <tiêu đề>
**Việc:** <task-id>
**Vấn đề:** <mô tả, kèm số đo nếu có>
**Đề xuất:** <phương án>
**Trả lời:** <agent kia điền — rồi đổi [MỞ] thành [ĐÓNG]>
```

<!-- APPEND Ở NGAY DƯỚI DÒNG NÀY -->

---

## 7. Lệnh hay dùng

```bash
# Luôn dùng interpreter này, KHÔNG dùng `python` trên PATH
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m ruff check .

# Cổng dữ liệu (đã đóng — chỉ chạy lại khi có lý do và ghi ADR)
.venv/Scripts/python.exe -m scripts.find_duplicates regroup
.venv/Scripts/python.exe -m scripts.check_leakage datased
.venv/Scripts/python.exe -m scripts.report_duplicates

# W2
.venv/Scripts/python.exe -m scripts.extract_features datased
.venv/Scripts/python.exe -m scripts.train_classifier --epochs 30 --device cuda
.venv/Scripts/python.exe -m scripts.report_run ml/runs/<run_id>
```
