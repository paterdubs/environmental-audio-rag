# STATUS.md — Trạng thái có bằng chứng

**Cập nhật:** 2026-09-22

## Snapshot

| Thành phần | Trạng thái | Bằng chứng |
|---|---|---|
| Scope | Đã chốt | `docs/decisions/ADR-0001-scope-and-datasets.md` |
| Repository scaffold | Đã tạo | Cấu trúc, package, CLI và test suite |
| DataSED download | Hoàn tất | Archive 4.51 GB; MD5 `44e093f675fc44cfb8a11b68456b72d7` |
| DataSED audit | Hoàn tất D0–D2 | 717 WAV, 18.6847 giờ, 8 nhóm exact duplicate |
| DataSEC download | Đang chạy, có resume | Archive đích 6,414,663,316 byte; MD5 đích `29fa9b8cc84cfa69aa4e5e674e780383` |
| Frozen splits | DataSED candidate | 435/142/140 recording; chờ audit duplicate xuyên dataset trước freeze D4 |
| Classification baseline | Chưa chạy | Chờ DataSEC hoàn tất |
| SED baseline | Đã chạy | `docs/measurements/sed_polyphonic_20260922T115340Z.md` |
| Grounded caption | Chưa có | Mới có contract dự kiến |
| RAG | Chưa có | Mới có kiến trúc dự kiến |
| API/frontend | Chưa có | Chỉ có folder scaffold |

## Artifact DataSED

- Inventory: `data/manifests/datased_inventory.csv` và `datased_inventory_summary.json`.
- Annotation chuẩn hóa: 4,034 polyphonic event/21 class; 4,309 monophonic event/22 class.
- Polyphonic labels phủ 703/717 recording; 14 recording được giữ như recording không có target event.
- Log-mel v1: 717/717 file, 16 kHz, 64 mel bin, hop 320 sample (50 frame/s), float16 artifact.
- Candidate split SHA-256: `656c1851de7c22a5eb6b2c2dc2b20397ad1bce98b136c591b7fe68b88cd130b1`.
- Test suite: 11 test pass trên Python 3.12/PyTorch 2.11 CUDA 12.8.

## Baseline DataSED

Full run `sed_polyphonic_20260922T115340Z`, 8 epoch, threshold đóng băng 0.5:

- Best validation frame macro-F1: **0.357305**.
- Test frame macro-F1: **0.359448**.
- Test frame macro average precision: **0.466312**.

Đây là metric frame-level để xác nhận baseline. Chưa có event-based F1 hoặc PSDS; không diễn giải các số trên như metric SED cuối cùng.

## Cổng hiện tại

**D3 — duplicate audit.** DataSED exact duplicate đã xong. DataSEC nội bộ và duplicate xuyên DataSEC–DataSED phải hoàn tất trước khi split được freeze và trước transfer experiment.

## Blocker còn lại

- Hoàn tất download/checksum/extract DataSEC và đọc license/README trong archive.
- Audit exact/decoded/near duplicate xuyên hai dataset.
- Freeze lại split sau cross-dataset audit.
- Train DataSEC classifier, sau đó chạy DataSEC → DataSED transfer.
- Thêm post-processing, event-based F1 và PSDS cho benchmark SED đầy đủ.

