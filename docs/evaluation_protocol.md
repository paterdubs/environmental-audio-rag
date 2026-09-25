# evaluation_protocol.md — Giao thức đánh giá

> **Đọc file này trước khi báo cáo bất kỳ con số nào.**
>
> Bộ metric: [SYSTEM.md](SYSTEM.md) §8. File này nói *cách chạy để số có nghĩa*,
> và quan trọng hơn: **số đó KHÔNG được nói gì**.

---

## 0. Năm quy tắc nền

| # | Quy tắc |
|---:|---|
| **Q1** | Metric, threshold và post-processing được định nghĩa **trước** test run |
| **Q2** | Báo macro **và** per-class. Không dùng micro score che class yếu |
| **Q3** | Confidence interval bootstrap theo **recording**, không theo frame |
| **Q4** | Test chỉ chạy khi config và checkpoint đã đóng băng |
| **Q5** | Mỗi bảng kết quả gắn run ID, split hash và taxonomy hash |

**Q3 đáng giải thích.** Frame không độc lập: 671,570 frame của test set đến từ
140 recording. Bootstrap theo frame sẽ cho khoảng tin cậy hẹp giả tạo — nó giả
định 671,570 mẫu độc lập trong khi thực tế chỉ có 140. Đơn vị lấy mẫu là recording.

---

## 1. Ba tập, ba câu hỏi khác nhau — đừng trộn

| Tập | Trả lời câu hỏi | Được dùng để |
|---|---|---|
| **train** | — | Tối ưu tham số model; suy duration prior cho post-processing |
| **dev** | "Cấu hình nào tốt hơn?" | Chọn θ, early stopping, chọn checkpoint, chọn config |
| **test** | "Cấu hình đã chọn tốt đến đâu?" | **Chạy một lần, config đóng băng** |

### Ba điều tuyệt đối không

- ❌ Dùng DataSED test để chọn threshold, duration prior hoặc checkpoint.
- ❌ Dùng DataSEC test để chọn encoder cho báo cáo cuối.
- ❌ Chọn run tốt nhất theo test.

### Một vi phạm tinh vi, dễ mắc

Chạy test 3 lần với 3 checkpoint rồi báo cái tốt nhất **là tuning trên test**, dù
mỗi lần chạy đều "đúng quy trình". Số lần chạy test phải bằng số cấu hình đã đóng
băng từ trước, và mọi lần chạy đều phải báo cáo — kể cả lần xấu.

---

## 2. Chọn θ — quy tắc quan trọng nhất và dễ vi phạm nhất

### 2.1 Bốn tham số post-processing và nguồn học

| Tham số | Học từ | **Không** được học từ | Lý do |
|---|---|---|---|
| $\theta_c$ — threshold per class | **dev** | test | Tối ưu event-based F1 trên dev |
| $w_c$ — median filter | **train** | dev, test | Là duration prior |
| $d^{min}_c$ — event tối thiểu | **train** | dev, test | Là duration prior |
| $g^{max}_c$ — gap gộp | **train** | dev, test | Là duration prior |

### 2.2 Vì sao duration prior phải suy từ TRAIN, không từ dev

Đây là điểm dễ sai nhất và hậu quả im lặng.

$w_c$, $d^{min}_c$, $g^{max}_c$ được suy từ **phân bố thời lượng event**. Nếu suy
chúng từ dev rồi đánh giá trên dev, thì hậu xử lý đã "biết trước" phân bố của
chính tập đang chấm. Kết quả dev cao lên, nhưng cao vì rò rỉ, không vì model tốt.

Hậu quả thực tế: chọn cấu hình sai, vì cấu hình nào khớp dev nhất được chọn chứ
không phải cấu hình tổng quát nhất. Rồi test tụt so với dev nhiều hơn dự kiến, và
người làm tưởng là overfit model trong khi thật ra là rò rỉ post-processing.

**Quy tắc:** mọi tham số suy từ *thống kê nhãn* lấy từ train. Chỉ θ — thứ phụ
thuộc vào *phân bố điểm của model* — mới quét trên dev.

### 2.3 Quy trình quét θ

```text
1. Train model, chọn checkpoint theo dev primary metric
2. Sinh logit thô trên dev  →  ml/runs/<run>/predictions/dev.npz
3. Suy w_c, d_min_c, g_max_c từ thống kê thời lượng của TRAIN
4. Quét θ_c trên lưới [0.05, 0.95] bước 0.05, tối ưu event-based F1 per class
5. Ghi postproc.json  →  ĐÓNG BĂNG
6. Sinh logit thô trên test, áp postproc.json y nguyên, chạy MỘT lần
```

Bước 2 và 6 tách logit ra khỏi metric là có chủ ý: nó cho phép quét lại θ mà
không chạy lại inference. Không có nó, mỗi lần thử một θ khác tốn cả một lượt
forward toàn bộ tập.

### 2.4 Global θ hay per-class θ

Báo cáo **cả hai** (ablation A2). Per-class kỳ vọng tốt hơn vì 21 class có tiên
nghiệm rất khác nhau, nhưng nó cũng có 21 bậc tự do được fit trên dev — nên phải
kiểm chênh lệch dev→test của cả hai. Nếu per-class tốt hơn hẳn trên dev mà tụt
mạnh hơn trên test, đó là dấu hiệu overfit dev.

---

## 3. Metric SED — cấu hình cụ thể

### 3.1 Ba loại metric, ba mục đích

| Metric | Mục đích | Dùng làm primary? |
|---|---|:---:|
| Frame-based F1 | Xác nhận pipeline train chạy đúng | ❌ |
| Segment-based F1 | So sánh thô, ít nhạy với biên | ❌ |
| **Event-based F1** | Chất lượng phát hiện và biên | ✅ |
| **PSDS** | Hiệu năng trên toàn dải operating point | ✅ |

### 3.2 Cấu hình event-based F1

Dùng `sed_eval`, **không tự viết lại**.

| Tham số | Giá trị | Lý do |
|---|---|---|
| `t_collar` (onset) | 0.200 s | Chuẩn quen thuộc của DCASE, so sánh được |
| `percentage_of_length` (offset) | 0.200 | Offset dung sai 20% độ dài event |
| Offset collar hiệu dụng | $\max(0.2\text{ s},\ 0.2 \cdot L_{ref})$ | Sai 1 s trên event 2 s khác hẳn trên event 60 s |
| Averaging | **macro** | Q2 |

> ⚠️ **Collar 0.2 s chặt hơn độ chính xác của chính nhãn** — đo được 23/09/2026,
> [`annotation_consistency_20260923.md`](measurements/annotation_consistency_20260923.md).
>
> DataSED chứa 8 cặp recording **byte-identical** được chú giải độc lập hai lần.
> Trên cùng một audio:
>
> | | |
> |---|---:|
> | Biên nằm trong collar 0.2 s | **67 / 94** |
> | Lệch biên lớn nhất | **12.72 s** (`S-0289` / `S-0500`) |
> | Cặp bất đồng về lớp hoặc số event | **2 / 8** |
>
> Ba hệ quả bắt buộc khi báo cáo:
>
> 1. Sai số của model nhỏ hơn mức bất đồng này **không phân biệt được với nhiễu
>    nhãn**. Không tuyên bố cải thiện ở mức đó.
> 2. Phần Hạn chế phải nêu con số này kèm cỡ mẫu (8 cặp), để người đọc tự định cỡ.
> 3. Hai cặp bất đồng lớp là **bằng chứng trực tiếp** về cặp dễ nhầm, lấy từ
>    ground truth chứ không từ ma trận nhầm của model:
>    `lawn_mower_brush_cutter_olive_shaker` ↔ `propeller_aircrafts`, và
>    `vacuum_cleaner_fan_hairdryer` ↔ `lawn_mower_brush_cutter_olive_shaker`.

### 3.3 Cấu hình PSDS — hai scenario đóng băng

Dùng `psds_eval`. Hai scenario phải khai trong config **trước** test.

| | PSDS-1 | PSDS-2 |
|---|---|---|
| Mục tiêu | Định vị thời gian tốt | Tránh nhầm lớp |
| `dtc_threshold` | 0.7 | 0.1 |
| `gtc_threshold` | 0.7 | 0.1 |
| `cttc_threshold` | — | 0.3 |
| `alpha_ct` | 0 | 0.5 |
| `alpha_st` | 1 | 1 |
| `max_efpr` | 100 | 100 |

PSDS-1 khắt khe về biên; PSDS-2 nới biên nhưng phạt cross-trigger. Báo cả hai vì
một model có thể tốt ở cái này và tệ ở cái kia — và chênh lệch đó là thông tin.

### 3.4 Chỉ dùng 21 class cho polyphonic

`wind_turbine` không thuộc polyphonic label set. Class list **phải** lấy từ
`taxonomy.polyphonic_class_ids`, không phải `taxonomy.class_ids`.

**Không so trực tiếp score polyphonic (21 class) với monophonic (22 class)** như
cùng một task. Chúng khác cả label set lẫn định nghĩa nhãn.

---

## 4. Class có ít mẫu — cách báo cáo

### 4.1 Vấn đề đo được

Bốn subclass DataSEC có dưới 25 file, nên dev/test chỉ 3–4 mẫu:

| Subclass | Files | test | Một mẫu sai = |
|---|---:|---:|---:|
| `Crickets` | 20 | 3 | 33 điểm % |
| `Olive shaker` | 20 | 3 | 33 điểm % |
| `Magpies` | 21 | 4 | 25 điểm % |
| `Lawn mower` | 21 | 4 | 25 điểm % |

### 4.2 Quy tắc báo cáo

| Điều kiện | Báo thế nào |
|---|---|
| $n_{test} \ge 30$ | F1 bình thường, kèm CI bootstrap |
| $10 \le n_{test} < 30$ | F1 kèm CI, **đánh dấu mẫu nhỏ** |
| $n_{test} < 10$ | **Số tuyệt đối, KHÔNG báo tỷ lệ** |

```text
✅ ĐÚNG: Crickets: đúng 2/3 · Olive shaker: đúng 1/3 · Magpies: đúng 3/4
❌ SAI : Crickets: F1 = 0.67 · Olive shaker: F1 = 0.33 · Magpies: F1 = 1.00
```

**Vì sao "F1 = 1.00" là sai dù đúng số học:** nó gợi ý một mức tin cậy mà 3 mẫu
không thể cung cấp. Người đọc bảng sẽ so nó với F1 = 0.85 của một class có 300
mẫu, và kết luận ngược hoàn toàn với thực tế.

### 4.3 Ảnh hưởng lên macro-F1

Macro-F1 cho mỗi class trọng số bằng nhau, nên 4 subclass low-support có ảnh
hưởng không cân xứng lên macro-F1 subclass. **Báo hai con số:**

```text
subclass macro-F1 (tất cả node)        = X.XXX   ← có nhiễu từ 4 class n<10
subclass macro-F1 (node có n_test>=10) = Y.YYY   ← số diễn giải được
```

Không thay thế con số này bằng con số kia. Báo cả hai và nói rõ chênh lệch đến
từ đâu.

---

## 5. "Chưa đo" không phải là 0

| Tình huống | Ghi |
|---|---|
| Chưa chạy thí nghiệm | `○` hoặc "chưa đo" |
| Đã chạy, kết quả bằng 0 | `0.000` kèm run ID |
| Đã chạy, thất bại | "fail" kèm lý do và log |
| Có số nhưng chưa xác minh | `⚠️ CẦN XÁC MINH` |

Ô trống trong bảng kết quả là **lỗi trình bày**, không phải kết quả. Mỗi ô phải
là một trong bốn trạng thái trên.

---

## 6. Khi nào hai run so được với nhau

Hai run chỉ so được khi **toàn bộ** các mục sau giống nhau:

| # | Phải giống | Kiểm bằng |
|---:|---|---|
| 1 | Split | `split_sha256` |
| 2 | Taxonomy và class order | `taxonomy_sha256` |
| 3 | Label mode (polyphonic / monophonic) | config |
| 4 | Feature version | `data_manifest_sha256` |
| 5 | Metric và tham số metric | config |
| 6 | Training budget (epoch × batch) | config |

Khác bất kỳ mục nào → **không so được**, và không được đặt cạnh nhau trong cùng
một bảng mà không ghi chú.

### 6.1 Hai thứ TUYỆT ĐỐI không so

**1. Frame-based F1 với event-based F1.** Khác đơn vị đo. Một model frame-F1
0.359 có thể có event-F1 0.10 hoặc 0.45 tùy hậu xử lý. Đặt chúng cùng một cột là
gây hiểu nhầm nghiêm trọng.

**2. Score polyphonic (21 class) với monophonic (22 class).** Khác label set,
khác định nghĩa nhãn, khác số lớp trong mẫu số macro.

### 6.2 Trường hợp baseline hiện tại

Run `sed_polyphonic_20260922T115340Z`, frame macro-F1 test **0.359448**:

| Điều kiện | Trạng thái |
|---|---|
| Split đã freeze | ❌ candidate, chưa qua D3/D4 |
| θ đã hiệu chuẩn | ❌ cố định 0.5 |
| Event-based metric | ❌ chỉ có frame |
| `git.revision` truy vết được | ❌ `"HEAD"`, `dirty: true` |
| Đã hội tụ | ❌ 8 epoch, chưa có bằng chứng |

→ **Đây là số dò đường, không phải kết quả báo cáo.** Mọi lần trích dẫn phải kèm
bốn giới hạn trên. Nó không so được với bất kỳ paper nào.

---

## 7. Điều kiện để một lần train được tính là hợp lệ

| # | Điều kiện | Kiểm |
|---:|---|---|
| 1 | `complete = true` trong manifest | Run bị ngắt không được ghi `complete` |
| 2 | `git.revision` là commit thật, `dirty = false` | Không tái lập được nếu dirty |
| 3 | `split_sha256` khớp split đã freeze | |
| 4 | `taxonomy_sha256` khớp taxonomy đang dùng | |
| 5 | Seed đã set cho torch, numpy, python | |
| 6 | Manifest có đủ trường bắt buộc | [SYSTEM.md](SYSTEM.md) §9.2 |
| 7 | Cổng D4 đã pass | Trước benchmark chính |

Artifact thiếu manifest hoặc thiếu bất kỳ mục nào ở trên **không hợp lệ cho báo
cáo**, kể cả khi số đẹp.

---

## 8. Đánh giá caption

### 8.1 Hai mức, phải báo cả hai

| Mức | Timeline đầu vào | Trả lời |
|---|---|---|
| **Oracle** | Ground truth DataSED | Captioner tự nó có grounded không |
| **End-to-end** | SED prediction đã đóng băng | Hệ thống thật có grounded không |

Chênh lệch giữa hai mức = lỗi do SED, không phải lỗi captioner. **Chỉ báo
end-to-end sẽ quy tội sai cho captioner.**

### 8.2 Điều kiện để RQ2 có nghĩa

Ba nhánh caption (template / constrained / unconstrained) phải chạy trên **cùng
một bộ SED prediction đóng băng** (E5). Nếu đổi SED giữa các nhánh thì Δ
hallucination trộn hai nguyên nhân và không nói gì về grounding.

### 8.3 N-gram metric chỉ là phụ

BLEU/METEOR/CIDEr so với reference caption sinh xác định từ timeline. Vì reference
đó không phải caption người viết, điểm n-gram **không** nói lên chất lượng ngôn
ngữ, và **không** phát hiện được hallucination (một caption bịa vẫn có thể trùng
n-gram cao). Báo để tham khảo, không dùng kết luận.

---

## 9. Đánh giá retrieval

### 9.1 Query set xây trước khi xem kết quả

100 query, bốn nhóm (30/25/25/20 — [SYSTEM.md](SYSTEM.md) §8.5). Relevance
judgment phải xác định được **bằng máy từ ground truth**, không phán đoán thủ công:

```text
Query "bản ghi có tiếng kính vỡ"
  → relevant = mọi recording có ≥1 event ground-truth class glass_breaking
```

Như vậy relevance không phụ thuộc vào output của hệ thống đang đánh giá.

### 9.2 Filter exactness — metric bắt vi phạm kiến trúc

$$\text{filter exactness} = \frac{\text{số kết quả thỏa MỌI hard filter}}{\text{tổng số kết quả trả về}}$$

`hybrid` và `structured_only` phải đạt **1.000**. Thấp hơn 1.000 là **lỗi hệ
thống**, không phải hiệu năng kém — nghĩa là semantic ranker đã ghi đè hard filter,
vi phạm [SYSTEM.md](SYSTEM.md) §7.2.

`vector_only` sẽ thấp hơn 1.000 theo thiết kế. Đó chính là thứ cần đo để chứng
minh giá trị của structured filter (RQ3).

### 9.3 Unsupported-claim rate

Tỷ lệ câu trả lời chứa claim không có `evidence[]` chống lưng. Mục tiêu **0.000**
— vì đây là ràng buộc A1, không phải mục tiêu hiệu năng.

---

## 10. Quy ước trình bày số

| Hạng mục | Quy ước |
|---|---|
| F1, precision, recall, PSDS | 3 chữ số thập phân: `0.359` |
| Số trong artifact JSON | Giữ đầy đủ: `0.35944821333661925` |
| Phần trăm | 1 chữ số: `37.6%` |
| Đếm | Có phân cách nghìn: `5,048` |
| Thời gian | Giây, 1–2 chữ số: `12.4–13.1 s` |
| Δ giữa hai nhánh | Kèm dấu: `+0.042` |
| CI | `0.359 [0.331, 0.388]` |
| Hash trong bảng | 8 ký tự đầu: `656c1851…` |

**Không làm tròn trong artifact.** Làm tròn chỉ ở tầng trình bày, do
`scripts/report_*.py` thực hiện. Số gốc giữ nguyên trong JSON để tính lại được.

---

## 11. Giao thức chạy test một lần

```text
TIỀN ĐIỀU KIỆN
  [ ] D4 pass, split đã freeze
  [ ] Checkpoint chọn theo dev, đã đóng băng
  [ ] postproc.json đã đóng băng
  [ ] Danh sách cấu hình sẽ chạy đã viết ra TRƯỚC
  [ ] git clean, revision ghi được

CHẠY
  1. Sinh logit thô trên test → predictions/test.npz
  2. Áp postproc.json y nguyên
  3. Tính event-based F1, PSDS-1, PSDS-2, per-class
  4. Bootstrap CI theo recording, 1000 lần lặp
  5. Sinh docs/measurements/<run_id>.md bằng script

SAU KHI CHẠY
  [ ] Báo cáo MỌI cấu hình đã chạy, kể cả cấu hình xấu
  [ ] Không quay lại sửa θ rồi chạy lại
  [ ] Cập nhật STATUS.md
```

**Nếu phát hiện lỗi thật sau khi chạy test** (bug trong metric, split sai), được
sửa và chạy lại — nhưng **phải ghi vào báo cáo** rằng test đã chạy N lần và vì
sao. Che giấu việc này là gian lận; ghi rõ thì không.

---

## 12. Bộ đánh giá: đã làm gì, còn giới hạn gì

Viết vào báo cáo, không giấu.

Bảng gốc (22/09) liệt kê 8 mục chưa có; **cả 8 đã làm** (cập nhật 25/09):

| # | Mục 22/09 | Trạng thái |
|---:|---|---|
| 1 | Event-based F1 và PSDS | ✅ `sed_eval`/`psds_eval`, mọi run (ADR-0020) |
| 2 | Post-processing hiệu chuẩn | ✅ θ và duration prior chọn trên dev/train; tối ưu bằng CV dev (ADR-0024) |
| 3 | Bootstrap CI | ✅ theo recording cho SED và cho caption (RQ2) |
| 4 | Lưu logit thô | ✅ `predictions/{dev,test}.npz` |
| 5 | Nhiều seed | ✅ 5 run/nhánh, Welch t-test (ADR-0021) |
| 6 | Metric calibration (ECE) | ✅ classifier DataSEC (ADR-0017) |
| 7 | Phân tích lỗi per-class | ✅ SED (`branch_per_class_*`) và caption (`caption_per_class_*`) |
| 8 | Metric caption và retrieval | ✅ caption (C2, W5) · ○ retrieval (W6) |

**Giới hạn còn lại — phải viết vào báo cáo:**

| # | Giới hạn | Hệ quả |
|---:|---|---|
| 1 | Train SED không tất định cùng seed | Mọi số SED báo mean ± sd nhiều run; run đơn không kết luận được |
| 2 | Metric C2 dựa trên lexicon; đối chiếu với người đọc mù trên mẫu 60 caption test, một người — **phiếu chờ người dùng điền** (`scripts.caption_mention_worksheet`) | Chưa có sai số trích đo được; hallucination là cận trên (7/8 mention "bịa" trên test là lỗi lexicon) |
| 3 | Omission tính theo **lớp**, không theo event | Lặp lại cùng lớp mà chỉ nhắc một lần không bị tính bỏ sót |
| 4 | Thứ tự là tỷ lệ cặp đúng (cặp bằng nhau tính đúng), không phải Kendall τ | Báo kèm bản chỉ tính caption ≥2 mention |
| 5 | N-gram so với caption template, không có caption người viết | Chỉ tham khảo, không kết luận (§8.3) |
| 6 | Retrieval chưa có số | RQ3 chưa trả lời (W6) |
| 7 | Caption LLM chỉ tất định theo **chuỗi request** trên server mới khởi động — bộ nhớ đệm prompt của llama.cpp đổi phép tính số thực | Tái lập = sinh lại cả file theo đúng thứ tự; không vá lẻ từng caption (ADR-0023 §7) |
