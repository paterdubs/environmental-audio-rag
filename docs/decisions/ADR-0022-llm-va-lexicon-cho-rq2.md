# ADR-0022 — LLM cho nhánh caption RQ2 và lexicon đo grounding cho caption tự do

**Status:** Accepted
**Date:** 2026-09-24

## Context

RQ2 so caption **constrained** với **unconstrained** trên cùng SED prediction đóng
băng (SYSTEM.md §6.5, evaluation_protocol §8.2). Captioner chỉ nhận event timeline,
không nhận audio (§6.1). Còn thiếu ba thứ:

1. **Chọn LLM.** Văn liệu gần nhất đưa timeline/tag sự kiện dạng text vào LLM:
   SAR-LM (Taheri et al., arXiv 2511.06483 — tag PANNs có timestamp → Qwen2.5-Omni-7B /
   Qwen3-30B-A3B / Gemini 2.5 Pro; ghi nhận model 7B "frequently hallucinated" từ
   đặc trưng ký hiệu), TAC (Kumar et al., ICML 2026 — Qwen3-Next-80B-A3B, Gemini 3 Pro),
   AudioSetCaps (NeurIPS 2024 — Mistral-7B), Sound-VECaps (Llama 3), AudioTime và
   WavCaps (GPT-3.5/4, ChatGPT).
2. **Lexicon đo mention quá hẹp cho văn bản tự do.** Lexicon v1 chỉ khớp tên nhãn
   (`propeller aircrafts`, `sirens and alarms`…). Trên 3 caption smoke-test thật của
   Qwen3.5-9B, v1 bắt được 1/3/2 mention trong khi caption nhắc 3/4/7 nguồn âm —
   bỏ sót "propeller aircraft", "sirens", "crows, seagulls", "vehicle traffic",
   "musical notes". Chấm bằng v1 sẽ thổi phồng omission và **che** hallucination của
   nhánh unconstrained, tức đo sai đúng thứ RQ2 hỏi.
3. **Timeline e2e sai độ dài** — lỗi ghép cửa sổ (commit `7ada7d7`), phát hiện khi
   smoke-test: LLM chép "130-second recording" cho audio 125.4 s.

## Decision

### 1. Một LLM cục bộ cho CẢ HAI nhánh: Qwen3.5-9B, GGUF Q4_K_M, llama.cpp

| | |
|---|---|
| Model | `Qwen/Qwen3.5-9B` (Apache 2.0, 02/2026), bản lượng tử `bartowski/Qwen_Qwen3.5-9B-GGUF` Q4_K_M |
| SHA-256 | `d784ce9eda1a5a7b51e8f705a9e6310844bf4f173654d115823c775fdea56d43` (khớp Hugging Face LFS) |
| Runtime | llama.cpp **b11158** (Windows CUDA 12.4), `-ngl 99 -c 4096 -np 1 --jinja` |
| Sinh | temperature 0 (greedy), seed 20260922, max_tokens 256, **thinking tắt** |
| Prompt | `caption-prompt-v1`, timeline chỉ gồm `class_id/onset_s/offset_s` (bỏ score để oracle và e2e cùng định dạng) |

Cấu hình ở `ml/configs/caption_llm.yaml`; `scripts.generate_llm_captions` kiểm
server đang chạy đúng file và băm lại file model trước mỗi lần sinh.

**Vì sao cùng một model:** Δ RQ2 phải chỉ đo tác dụng của ràng buộc. Hai nhánh khác
nhau **duy nhất** ở grammar lúc decode (grammar-constrained decoding, Geng et al.,
EMNLP 2023). Grammar cần can thiệp logit → loại API đóng (chỉ ép được JSON schema).

**Đo trên máy (RTX 3070 Laptop 8 GB):** VRAM đỉnh 5,712 MiB; ~55 token/s; GBNF
chạy đúng; chạy lại cùng input cho output **giống hệt từng byte** (`-np 1`).

### 2. Nhánh unconstrained ghi lại vi phạm, không chặn

`UnconstrainedLLMCaptioner` không gọi `assert_safe`, `evidence = []` (G2 coverage = 0
theo cấu tạo). Vi phạm G1–G3 của sinh tự do là đại lượng RQ2 đo.

### 3. Lexicon v2 (`ml/configs/caption_lexicon.yaml`) và giao thức đóng băng

Mỗi cụm từ ánh xạ tới một **tập** lớp ứng viên, bốn loại: `class` (diễn đạt lại),
`specific` (gọi tên thành viên của lớp gộp — có căn cứ lớp nhưng vượt mức mơ hồ
của bằng chứng, SYSTEM §6.4 → báo riêng `over_specific_rate`), `family` (mơ hồ giữa
nhiều lớp: "aircraft", "vehicle", "singing"), `out_of_taxonomy` ("wind", "rain" —
luôn là hallucination). Thêm `context_terms` (bối cảnh/không khí suy diễn: "urban",
"peaceful") → `context_term_rate`, tách khỏi lexicon cấm G3 hiện có.

**Mơ hồ luôn xử theo hướng có lợi cho caption:** mention `family` có căn cứ nếu
**bất kỳ** lớp nào trong nhóm có trong timeline, và được tính phủ recall. Vì nhánh
constrained dùng đúng tên lớp, sự dễ dãi này chỉ có lợi cho unconstrained → **Δ RQ2
báo ra là cận dưới**.

Liệt kê thành viên của một lớp gộp ("crows, seagulls, and magpies") là **một**
mention (gộp khi giữa hai mention cùng lớp chỉ có dấu câu/and/or); nhắc lại ở câu
khác vẫn là hai mention. Temporal order chỉ tính trên mention có căn cứ.

**Giao thức chống tuning trên test:**

1. Sinh caption unconstrained trên **dev** (oracle + e2e).
2. `scripts.score_captions --audit` liệt kê từ ngoài mọi mention; người rà và mở
   rộng lexicon **chỉ từ caption dev**.
3. Đóng băng: ghi SHA-256 lexicon vào §4 của ADR này, commit.
4. Chỉ khi đó mới sinh và chấm test — cả hai script **từ chối** `--split test` nếu
   không truyền đúng SHA-256 lexicon hiện tại.

### 4. Lexicon đóng băng

| | |
|---|---|
| Version | `caption-lexicon-v2` — 318 cụm |
| SHA-256 | `6f5634bb7837817c94dd16fe0c0b07a6eae15996fe93064c325599d3321edc73` |
| Căn cứ | 274 caption dev (137 recording × oracle/e2e), run B `sed_polyphonic_20260924T054531Z` sau đánh giá lại |
| Bằng chứng | `docs/measurements/caption_grounding_sed_polyphonic_20260924T054531Z_dev.md` (kèm audit) |

Thay đổi do audit dev (ghi đủ để phản biện được):

- Thêm: `coop`, `lawn equipment/maintenance/care`, `idle(s)`, `tool(s)`, `hammering`,
  `thunderclaps`; nhóm mơ hồ `machinery/machine/mechanical noise`, `engine/motor`,
  `chirping/chirp`, `ringing`, `boom`.
- **Sửa hai lỗi phân loại của chính bản nháp:** `machinery` và `hammering` từng nằm
  trong `out_of_taxonomy` — sai, đó là âm thanh máy/xưởng ("hammering and tool
  clatter"); để đó sẽ phạt oan nhánh unconstrained.
- Gộp mention khi nối bằng "of/from" và có lớp giao nhau ("the boom of fireworks",
  "the chirping of birds") — trước đó bị đếm hai lần, kéo temporal order về 0 mỗi
  khi timeline chỉ có một event của lớp đó.
- `silence/silent/quiet/stillness`, `outdoor`, `nature/natural`, `roadside` vào
  `context_terms` (§6.6: hệ thống không biết có im lặng hay không).
- **Không thêm** từ tả cách phát âm không nêu nguồn (rhythmic, rumble, roar, hum,
  drone, wail, clatter, buzzing) — không phải mention nguồn âm theo định nghĩa §8.3.

### 5. Kết quả nhánh unconstrained trên test (một lần, lexicon đã đóng băng)

| Mức | Halluc. | Omission | Temporal | Forbidden (G3) | Over-specific | Context |
|---|---:|---:|---:|---:|---:|---:|
| oracle | 0.0126 | 0.0124 | 0.9413 | 0.0070 | 0.1365 | 0.3239 |
| e2e | 0.0038 | 0.0599 | 0.9025 | 0.0141 | 0.1856 | 0.4225 |

Nguồn: `caption_grounding_sed_polyphonic_20260924T054531Z_test.md`. Audit thủ công
(`caption_lexicon_audit_test_20260925.md`): **7/8** mention bị chấm "bịa" là dương
tính giả của lexicon ("horn blast", "insect song", "birds singing"), 1/8 ranh giới
→ hallucination nguồn âm thật **0–1 / ~730 mention**; hai cột Halluc. trên là cận
trên. Lexicon không sửa sau audit.

**Hệ quả cho RQ2:** với timeline làm đầu vào, LLM gần như không bịa nguồn âm — RQ2
không thể thể hiện qua "hallucination nguồn âm" (hiệu ứng sàn). Khác biệt constrained
vs unconstrained phải được đọc trên các chiều sinh tự do thực sự vi phạm: suy diễn
bối cảnh (32–42% caption), gọi tên quá mức bằng chứng (14–19% mention), từ cấm G3
(0.7–1.4%), thứ tự thời gian (0.90–0.94) và omission e2e (6%). Phải viết đúng như
vậy trong Chương kết quả, không trình bày RQ2 như "giảm hallucination".

## Consequences

### Tích cực

- RQ2 cô lập đúng một biến (grammar). Sinh tất định, tái lập từ SHA-256 model +
  build runtime + hash prompt + hash lexicon, đều ghi trong `*.meta.json`.
- Lexicon v2 vẫn cho template hallucination = omission = 0, order = 1 trên cả 21
  lớp (test khoá).

### Đánh đổi / Hạn chế (phải vào báo cáo)

- **Lexicon không đầy đủ theo định nghĩa.** Cách diễn đạt nằm ngoài lexicon là vô
  hình: nguồn âm bịa không có trong danh sách `out_of_taxonomy` sẽ không bị tính.
  Cần một audit thủ công trên mẫu ngẫu nhiên caption test (sau khi chấm) để ước
  lượng tỷ lệ mention bị sót, báo cùng kết quả.
- **Chưa đo bịa về thời gian/số lượng** ("12-minute recording", "in the final ten
  seconds") — lexicon chỉ đo nguồn âm. Ghi vào Hạn chế; ứng viên metric bổ sung.
- Qwen3.5 chưa có technical report arXiv (chỉ blog Qwen, 02/2026) — trích dẫn model
  card. Kết luận RQ2 chỉ nói về model này; kiểm tra chéo với Gemma 4 E4B là tùy chọn
  nếu còn thời gian.
- Timeline e2e phụ thuộc θ quét lại sau `7ada7d7`; caption e2e chỉ sinh sau khi đánh
  giá lại SED.

## Alternatives considered

| Phương án | Vì sao không chọn |
|---|---|
| API (GPT/Gemini) cho unconstrained | Không ép grammar được cho nhánh constrained → hai nhánh khác model; không tái lập được |
| Model khác nhau cho hai nhánh | Δ trộn tác dụng ràng buộc với khác biệt model |
| Giữ lexicon v1 | Đo sai: che hallucination, thổi phồng omission của caption tự do |
| LLM-as-judge chấm mention | Thêm một model không tất định vào phép đo; khó kiểm, trái tinh thần C2 (metric kiểm được bằng máy) |
| Mở rộng lexicon sau khi xem caption test | Tuning phép đo trên test |
