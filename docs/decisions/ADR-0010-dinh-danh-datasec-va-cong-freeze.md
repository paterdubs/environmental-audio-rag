# ADR-0010 — Định danh item của DataSEC, và nghĩa của loại trừ khi đóng băng split

**Status:** Accepted
**Date:** 2026-09-23

## Context

Split DataSEC chưa tồn tại. Khi rà soát đường đi để mở khoá nó, hai chặn lộ ra —
cả hai đều **không** phải lỗi cú pháp mà là câu hỏi chưa ai trả lời.

### Chặn 1 — DataSEC không có `recording_id`, và cổng D4 đòi có

[`scripts/check_leakage.py`](../../scripts/check_leakage.py) phân giải khoá split
qua `data/manifests/<dataset>_recordings.csv` với ba cột
`recording_id` / `file_id` / `content_sha256`. DataSEC **không có file đó**. Nó chỉ
có `datasec_inventory.csv`, mà manifest này:

- không có cột `recording_id`;
- đặt tên cột hash là `sha256`, không phải `content_sha256`.

Khác biệt này không phải sơ suất đặt tên. Nó phản ánh hai cách công bố dữ liệu:

| | DataSED | DataSEC |
|---|---|---|
| Đơn vị công bố | **recording** 60 s, có annotation riêng | **clip** rời, xếp theo cây thư mục |
| Có định danh độc lập với đường dẫn? | có — `S-0001` | không |
| Archive cho biết clip cắt từ bản thu nào? | — | **không** |

Câu hỏi thật là: `recording_id` của DataSEC nên là gì?

### Chặn 2 — cổng freeze đọc một con số của dataset khác

[`scripts/freeze_split.py`](../../scripts/freeze_split.py) ghi vào bản ghi đóng băng
`leaked_pretraining_clips = audit["alarm"]["leaked_files"]` = **11**. Con số đó đếm
**clip DataSEC** trùng dev/test DataSED. Trong bản ghi của split DataSED nó đọc
như thể DataSED rò rỉ 11 file. Dùng lại nguyên si cho DataSEC thì cổng *có vẻ*
nghiêm nhưng đang kiểm nhầm dataset.

Sâu hơn: thử đặt luật "mọi file trong `exclusions.csv` phải vắng mặt khỏi split"
thì **split đã đóng băng của DataSED lập tức trượt**. Đo được:

| | |
|---|---:|
| Dòng `datased:` trong `exclusions.csv` | 13 |
| Trong số đó nằm **trong** split đã đóng băng | **13 / 13** |
| Vi phạm "cùng `leakage_group` với anh em trong nhóm trùng" | **0 / 13** |

Nghĩa là `exclusions.csv` gộp **hai động từ khác nhau** dưới một cái tên.

## Decision

### 1. DataSEC không có `recording_id`. Khoá item của split DataSEC là `file_id`

Không bịa ra một lớp định danh mà archive không cung cấp.

Quan hệ nguồn gốc giữa các clip DataSEC **đã được đo**: cổng D3 sinh
`duplicate_groups.csv` và `split_cohesion_pairs.csv`, và
[`build_leakage_groups`](../../ml/dataops/grouping.py) hợp nhất chúng thành
`leakage_group`. Đó chính là đại diện thực nghiệm cho "cùng một nguồn thu". Thêm
một `recording_id` suy đoán bên cạnh sẽ là:

- một **tuyên bố về nguồn gốc mà không ai đo** — đúng thứ `CLAUDE.md` §5 cấm;
- một **namespace thứ ba** trong repo đã hai lần hỏng vì lệch namespace, lần gần
  nhất suýt bỏ lọt cặp similarity 1.000000 giữa `Sirens-0046` và `S-0233`.

Tiền lệ đã có trong code: [`build_datasec_manifest`](../../ml/datasets/datasec.py)
đặt `clip_id = file_id`.

### 2. Khoá và tên cột được khai báo tập trung, không đọc cứng ở từng script

Thêm [`ml/dataops/registry.py`](../../ml/dataops/registry.py): mỗi dataset khai báo
`item_col`, manifest nguồn, tên cột hash, và corpus mà split của nó đại diện.
`check_leakage` dùng registry thay vì đọc cứng `recording_id` và `content_sha256`.

Ánh xạ của DataSEC là đồng nhất nhưng **vẫn đi qua manifest**: item lạ phải vỡ ở
đó chứ không lặng lẽ thành một phép giao rỗng ở tầng trên. Registry cũng từ chối
`file_id` sai tiền tố.

### 3. Loại trừ của D3 có hai nghĩa, phụ thuộc corpus mà split đại diện

| `reason_code` | Với **benchmark** (DataSED) | Với **corpus pretraining** (DataSEC) |
|---|---|---|
| `exclude_duplicate` | **giữ lại**, buộc cùng `leakage_group` — xoá thì benchmark teo lại | **vắng mặt** (DATA_PLAN §7.5: giữ một representative) |
| `exclude_cross_dataset_leak` / `_unsure` | không áp dụng | **vắng mặt** — ràng buộc cứng của RQ1 |

`require_exclusion_policy` kiểm đúng luật của corpus tương ứng, và với nhóm được
giữ lại thì kiểm bất biến thay thế: mọi thành viên có mặt của một nhóm trùng phải
cùng một `leakage_group`.

### 4. Cổng từ chối kết luận "sạch" trên một phép giao rỗng

Có loại trừ cho dataset nhưng split phân giải ra tập rỗng → `SystemExit`, không
phải "0 vi phạm". Sau hai lần bị pass rỗng lừa, một cổng không chứng minh được nó
chạm dữ liệu thì không đáng tin.

### 5. Con số báo động được ghi kèm phạm vi

Bản ghi đóng băng thêm
`leaked_clips_scope: "datasec clips overlapping datased dev/test"` để 11 không bị
đọc thành thuộc tính của split đang đóng băng.

## Consequences

### Tích cực

- Split DataSEC mở khoá được mà không cần sinh `datasec_recordings.csv` giả.
- Lỗi lệch namespace lần ba bị chặn ở tầng khai báo, không phải ở từng script.
- Cổng freeze của DataSEC sẽ kiểm đúng 11 clip rò rỉ — chứ không kiểm nhầm 13
  dòng nội bộ của DataSED.
- `check_leakage datased` vẫn **5/5 PASS** và `split_sha256` vẫn
  `d2924a5e45c2b271…` — `data-v1.0` không bị động tới.

### Đánh đổi

- File split của hai dataset có cột khoá **khác tên**. Code nào đọc split phải hỏi
  registry, không được giả định `recording_id`. Đây là cái giá của việc không bịa
  định danh, và registry làm nó nổ sớm thay vì âm thầm.
- `leakage_group` gánh cả vai "cùng nguồn thu" cho DataSEC. Nếu cụm cohesion 326
  file thực ra là dương tính giả, thì ràng buộc split sẽ **chặt hơn cần thiết** —
  thà chặt quá còn hơn rò rỉ, nhưng phải nêu ở Hạn chế.

## Alternatives considered

- **Sinh `datasec_recordings.csv` với `recording_id == file_id`.** Thoả schema mà
  không phải sửa code, nhưng dựng một bảng ánh xạ đồng nhất chỉ để chiều một giả
  định sai, và vẫn để lại namespace thứ ba cho người sau vấp.
- **Suy `recording_id` từ tên file** (`Bells-0001` → `Bells`). Gom 5,048 clip
  thành 22 "bản thu" — một tuyên bố nguồn gốc hoàn toàn bịa.
- **Suy `recording_id` từ `leakage_group`.** Đúng về nội dung nhưng thừa: nó chính
  là `leakage_group` đổi tên, và hai tên cho một thứ là cách sinh ra lệch namespace.
- **Dùng chung một luật loại trừ cho mọi dataset.** Đo được là sai: sẽ làm trượt
  split DataSED đã đóng băng ở `data-v1.0`.

## Evidence cần kiểm lại

- Cụm cohesion 326 file (6.5%) của DataSEC có chia được theo tỉ lệ đã chốt không —
  nếu không, quyết định ở §1 vẫn đúng nhưng tỉ lệ split phải bàn lại bằng ADR riêng.
- 119 dòng `exclude_duplicate` của DataSEC bị loại khỏi corpus pretraining có làm
  lệch phân bố lớp không — nếu tập trung vào vài lớp thì phải nêu ở Hạn chế.
