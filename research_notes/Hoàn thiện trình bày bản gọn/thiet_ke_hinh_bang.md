# Thiết kế sơ đồ khối, bảng và hình matplotlib cho khóa luận in Word (A4, TNR 13, vùng chữ 15,5 cm)

Ghi chú nghiên cứu, 28/11/2026. Phạm vi: (1) màu hộp sơ đồ khối đậm dần theo mức quan trọng, (2) bảng có ô
tiêu đề trắng, (3) kiểu hình matplotlib và chọn dạng biểu đồ cho kết quả SED/RAG. Không sửa tệp nào của repo;
mọi số tương phản/độ sáng dưới đây tính trong phiên này bằng công thức WCAG 2.x (nguồn W3C ở mục 2) qua script
nháp `C:\Users\patph\AppData\Local\Temp\claude\85ae35366b529c68\b4942c2f-c1bf-4b4b-81ce-f0801cbaaca1\scratchpad\viz\contrast.py`.
L* là độ sáng CIELAB tính từ độ chói tương đối WCAG — xấp xỉ mức xám khi in đen trắng.

Hiện trạng repo đã đọc (để khuyến nghị khớp mã):
- `scripts/report_docx/diagram.py`: `FILLS` = plain `F5F6F8`, model `FBEFE8`, store `EAF1FB`, offline `ECF8F1`;
  viền hộp `a:ln w="9525"` (0,75 pt) màu `MUTED 57606A`; đường/mũi tên `width_pt=1.0` màu MUTED, đầu tam giác
  `med`; chữ hộp 9,5 pt, dòng đầu INK `1F2328` đậm, các dòng sau MUTED; nhãn rời 8 pt. 1 pt = 12 700 EMU
  (mã dùng `round(width_pt * 12700)`).
- `scripts/report_docx/ooxml.py` dòng 217–254: bảng kẻ lưới đủ sáu cạnh `sz="4"` màu `000000`; ô tiêu đề
  nền `E7E6E6`, chữ đậm, căn giữa; hàng "đang dùng" nền `D9D9D9`; `w:tblHeader` lặp tiêu đề; `cantSplit`.
- `report/quy_cach_bao_cao.md` dòng 84–86: quy ước đã ghi — số in đậm = tốt nhất trong cột/nhóm, hàng nền xám
  nhạt `D9D9D9` = cấu hình đang dùng; in đậm không hàm ý khác biệt có ý nghĩa thống kê.
- Mẫu khoa `report/Mau bao cao KLTN_DS.docx`: 3 bảng mẫu dùng style `TableGrid` (đủ sáu cạnh `sz="4"`), ô nền
  `FFFFFF` (218 lần `w:fill="FFFFFF"`) — tức bảng mẫu của khoa **có ô tiêu đề trắng** và **kẻ lưới đủ**.
- `scripts/build_research_figures.py`, `scripts/build_final_figures.py`: rcParams `font.family="DejaVu Sans"`,
  `font.size=8.5`; nhãn trục/chú giải 6,5–7,5 pt; `figsize` rộng 4,6–7,4 in; `savefig(dpi=300,
  bbox_inches="tight")`; bảng màu `BLUE 2a78d6, ORANGE eb6834, GREEN 2f9e44, GRAY 8c959f` (+ tím `8250df`).
  Trong `report/gon_src/*.md` hình chèn với `{width=10cm…15cm}` (6 hình 15 cm, 3 hình 14 cm…).
- Môi trường: matplotlib 3.11.2; `C:\Windows\Fonts\times.ttf` (Times New Roman 7.13) có đủ mọi ký tự tiếng Việt
  đã thử và các ký hiệu `≥ ≤ ± → ← × Δ ∆ α θ μ · … ‰ √ ∞ ≈ − –` (kiểm bằng fontTools, 0 ký tự thiếu); có
  `DejaVu Serif`, `STIXGeneral`, `Cambria`; **không** có Noto Serif.

## 1. Giới chuyên môn khuyên gì về mã hóa mức quan trọng/thứ bậc bằng màu, và về thang tuần tự một sắc độ?

### Takeaway
Thứ bậc (mức quan trọng) là dữ liệu có thứ tự, nên mã hóa bằng **độ sáng của một sắc độ** (nhạt → đậm), còn
**sắc độ** (hue) chỉ để phân **loại**; phần nền phải dịu để phần nhấn nổi lên (Wilke: accent color). Bốn màu nền
hiện tại của sơ đồ có L* 94,9–96,9 và tương phản với giấy trắng chỉ 1,08–1,14:1, nên khi in đen trắng bốn loại hộp
trông như nhau và không có bậc quan trọng nào.

### Cited Findings
- Thang tuần tự dùng "a sequence of colors that clearly indicate" giá trị lớn/nhỏ; "The color scale needs to be
  perceived to vary uniformly across its entire range"; có thể một sắc độ ("from dark blue to light blue") hoặc
  nhiều sắc độ — [Wilke, Color scales](https://clauswilke.com/dataviz/color-basics.html)
- Thang định tính không được gợi thứ tự: "no one color should stand out relative to the others"; dãy màu nhạt dần
  tạo "an apparent order among the items being colored" — [Wilke, Color scales](https://clauswilke.com/dataviz/color-basics.html)
- Màu nhấn (accent): một tập "subdued colors" đi cùng tập "stronger, darker, and/or more saturated colors"; "it is
  critical that the baseline colors do not compete for attention"; cách đơn giản: "remove all color from all
  elements in the figure except the highlighted data categories" — [Wilke, Color scales](https://clauswilke.com/dataviz/color-basics.html)
- Thang định tính chỉ hợp với ít loại: "work best when there are three to five different categories"; quá ~8 thì
  "Use direct labeling instead of colors" — [Wilke, Color pitfalls](https://clauswilke.com/dataviz/color-pitfalls.html)
- Thang cầu vồng "highly non-monotonic", "not an appropriate scale to visualize continuous data values"; tính không
  đơn điệu "becomes particularly apparent if we look at the color scale in grayscale" — [Wilke, Color pitfalls](https://clauswilke.com/dataviz/color-pitfalls.html)
- "Colors are much easier to distinguish when they are applied to large areas than to small ones or thin lines";
  khuyên "test your figures in a cvd simulator" — [Wilke, Color pitfalls](https://clauswilke.com/dataviz/color-pitfalls.html)
- Bảng Okabe–Ito (8 màu): `#E69F00` cam, `#56B4E9` xanh trời, `#009E73` xanh lục lam, `#F0E442` vàng, `#0072B2`
  xanh dương, `#D55E00` đỏ son, `#CC79A7` tím hồng, `#000000` đen — [Wilke, Color pitfalls](https://clauswilke.com/dataviz/color-pitfalls.html)
- Paul Tol: High-contrast `#004488, #DDAA33, #BB5566` "works well for people with monochrome vision and in a
  monochrome printout"; Medium-contrast `#6699CC, #004488, #EECC66, #994455, #997700, #EE99AA` "optimized for
  contrast to work in a monochrome printout"; Bright `#4477AA, #EE6677, #228833, #CCBB44, #66CCEE, #AA3377,
  #BBBBBB` và Vibrant `#EE7733, #0077BB, #33BBEE, #EE3377, #CC3311, #009988, #BBBBBB` an toàn mù màu nhưng không
  ghi là hợp in đơn sắc; tuần tự YlOrBr 9 bậc `#FFFFE5 … #662506` cũng "works in colour-blind vision" và hợp in xám
  — [Paul Tol, Colour schemes](https://sronpersonalpages.nl/~pault/) (tên miền cũ personal.sron.nl không phân giải
  được trong phiên này)
- Tol: các bảng mạnh (bright, high-contrast, vibrant, muted, medium-contrast, dark) "too strong to use for
  backgrounds to mark (black) text, typically in a table"; bảng Pale/Light làm nền cho chữ đen thì "The text
  remains easily readable"; "if the colours were darker, the small print would become difficult to read" —
  [Paul Tol](https://sronpersonalpages.nl/~pault/)
- Skill dataviz (cục bộ): "Sequential = one hue, light->dark"; nếu đổi thứ tự loại làm đổi nghĩa thì đó là thang
  **ordinal** và dùng một sắc độ với bậc sáng đơn điệu, bậc gần nền nhất vẫn ≥ 2:1 với nền; "Color follows the
  entity, never its rank"; "Status colors are reserved" — `C:\Users\patph\AppData\Local\Temp\claude\bundled-skills\2.1.332\1d161357b0d4c7ae5c8db78720ac27a9\dataviz\SKILL.md`, `references/color-formula.md`, `references/palette.md`
- Thang ColorBrewer 9 bậc lấy trực tiếp từ `matplotlib._cm.datad` (matplotlib 3.11.2): Greys `FFFFFF F0F0F0
  D9D9D9 BDBDBD 969696 737373 525252 252525 000000`; Oranges `FFF5EB FEE6CE FDD0A2 FDAE6B FD8D3C F16913 D94801
  A63603 7F2704`; Blues `F7FBFF DEEBF7 C6DBEF 9ECAE1 6BAED6 4292C6 2171B5 08519C 08306B`; Greens `F7FCF5 E5F5E0
  C7E9C0 A1D99B 74C476 41AB5D 238B45 006D2C 00441B`; Purples `FCFBFD EFEDF5 DADAEB BCBDDC 9E9AC8 807DBA 6A51A3
  54278F 3F007D` — dữ liệu cục bộ `.venv/Lib/site-packages/matplotlib/_cm.py` (thang Brewer gốc: [ColorBrewer](https://colorbrewer2.org), không mở trong phiên này)

### Inferences
- **Hai kênh, hai nghĩa.** Độ sáng (L*) = mức quan trọng, còn được khi in xám; sắc độ = loại bước (dữ liệu/mô
  hình/kho/ngoại tuyến), mất khi in xám nên phải mã hóa kép bằng **hình dạng/nét viền** (Wilke, redundant coding,
  mục 2). Không dùng sắc độ để nói "quan trọng".
- **Đặc tả bốn mức × bốn loại** (bậc lấy theo ColorBrewer để mọi loại cùng L* ở cùng mức; số đo trong phiên):

  | Mức | Ý nghĩa | neutral (Greys) | model (Oranges) | store (Blues) | offline (Greens) | L* xấp xỉ | Chữ |
  |---|---|---|---|---|---|---|---|
  | M1 | bối cảnh, đầu vào ngoài, ghi chú | `F0F0F0` | `FEE6CE` | `DEEBF7` | `E5F5E0` | 92–95 | INK `1F2328`, MUTED được (5,3–5,6:1) |
  | M2 | bước thường | `BDBDBD` | `FDAE6B` | `9ECAE1` | `A1D99B` | 77–82 | **chỉ INK** (8,4–9,7:1); MUTED rớt 3,4–3,9:1 |
  | M3 | bước quan trọng | `969696` | `F16913` | `4292C6` | `41AB5D` | 58–63 | **INK đậm** (4,63–5,42:1) |
  | M4 | đóng góp chính (LBR, grounded caption, backfill…) | `525252` | `A63603` | `08519C` | `006D2C` | 35–40 | **trắng đậm** (6,51–7,87:1) |

  Khoảng cách L* giữa các mức ≈ 15 / 18 / 23 — đủ tách trên bản in xám. Bậc 7 của Oranges/Greens (`D94801`,
  `238B45`) là "vùng chết": chữ INK 3,65–3,67:1 và chữ trắng 4,31–4,33:1 đều dưới 4,5:1 → không dùng làm nền chữ.
- **Viền**: M1 0,5 pt (6 350 EMU) màu `BDBDBD`; M2 0,75 pt (9 525 EMU, như hiện nay) màu bậc 7 của cùng thang
  (`737373`/`D94801`/`2171B5`/`238B45`); M3 1,0 pt (12 700 EMU) bậc 8; M4 1,5 pt (19 050 EMU) bậc 9 (`252525`/
  `7F2704`/`08306B`/`00441B`; tương phản viền–nền chỉ 1,44–1,96:1, nên viền M4 là trang trí, không phải ranh giới
  nhận diện — ranh giới đã do nền tối so với giấy, 6,5–7,9:1).
- **Mũi tên**: luồng chính 1,25 pt INK nét liền, đầu tam giác `med`; luồng phụ/ngoại tuyến 0,75 pt MUTED nét đứt
  (`prstDash dash`, mã đã hỗ trợ `Line.dashed`); phản hồi/vòng lặp nét chấm. Màu mũi tên **không** theo loại hộp
  (giữ ink/muted) để mũi tên không cạnh tranh với hộp M4.
- **Mã hóa loại khi in xám** (thay vì chỉ màu): kho dữ liệu = hình trụ (preset DrawingML `can` hoặc
  `flowChartMagneticDisk`), ngoại tuyến = viền nét đứt, mô hình = hình chữ nhật góc bo (`roundRect`), bước thường
  = chữ nhật. Cần thử trong Word 365 vì `diagram.py` hiện chỉ sinh `prstGeom` chữ nhật.
- **Chú giải**: một dải chú giải dưới sơ đồ (dựng bằng chính `Box` cỡ 0,4 × 0,3 cm + nhãn 8 pt) gồm 4 ô xám
  M1→M4 "bối cảnh · bước thường · bước quan trọng · đóng góp chính" và 3 biểu tượng hình "kho dữ liệu (trụ) ·
  ngoại tuyến (nét đứt) · mô hình (góc bo)"; hoặc một câu trong chú thích hình nếu sơ đồ chật. Giữ cùng chú giải
  cho cả 7 sơ đồ.
- **Liều lượng**: tối đa 1–2 hộp M4 mỗi sơ đồ, M3 cho các bước nằm trên đường găng; còn lại M1–M2 — theo nguyên lý
  accent của Wilke (phần nền không được cạnh tranh). Con số "1–2" là đề xuất của tôi, không có nguồn.
- Thực thi trong mã: thay `FILLS: dict[str, str]` bằng `FILLS[(loại, mức)]` + bảng `TEXT_COLOR[mức]` (M1: INK/
  MUTED, M2–M3: INK, M4: `FFFFFF`) — hiện `_paragraph` tô dòng phụ bằng MUTED bất kể nền, sẽ rớt chuẩn ở M2–M4.

### Gaps
- Không tìm được nguồn có thẩm quyền đưa ra số hộp nhấn tối đa trong một sơ đồ; Wilke chỉ minh họa (2 bang, 1 nhóm).
- Không đọc được trực tiếp bài báo Okabe & Ito/trang jfly, Stephen Few "Practical rules for using color in charts"
  và sách Tufte trong phiên này; nhận định về Few/Tufte không được đưa vào.
- Không chạy mô phỏng mù màu cho thang sơ đồ (chỉ chạy cho bảng màu biểu đồ, mục 4); bốn loại cùng mức có L* gần
  nhau là chủ ý, nên khi mất sắc độ phải dựa vào hình dạng/nét viền.

## 2. Giữ nền đậm vẫn đọc được: ngưỡng WCAG, khi nào chuyển chữ trắng, và kiểm in xám

### Takeaway
Chữ trong hộp (8–9,5 pt) là "chữ thường" theo WCAG nên cần ≥ 4,5:1. Với các thang Brewer: chữ đen INK đạt đến
bậc 6 (Greys đến bậc 5), chữ trắng đạt từ bậc 8 (Greys từ bậc 6, Blues từ bậc 7); bậc 7 cam/lục là vùng chết.
Chữ phụ MUTED `57606A` chỉ đạt trên nền rất nhạt (M1), nên từ M2 trở lên mọi dòng chữ phải là INK hoặc trắng.

### Cited Findings
- SC 1.4.3: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1"; chữ lớn
  "at least 3:1"; chữ lớn là "at least 18 point or 14 point bold" — [W3C, Understanding SC 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- Công thức: "L = 0.2126 * R + 0.7152 * G + 0.0722 * B" (sau tuyến tính hóa sRGB, ngưỡng 0.04045, chia 12.92 hoặc
  ((x+0.055)/1.055)^2.4); tỉ lệ "(L1 + 0.05) / (L2 + 0.05)"; ngưỡng không được làm tròn ("4.499:1 would not meet
  the 4.5:1 threshold") — [W3C, Understanding SC 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- "1pt = 1.333px" theo CSS — [W3C, Understanding SC 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- Wilke: nhãn tô màu theo dữ liệu thì dùng "a dark shade of the hue for text and outlines and a light shade for
  fills" để chữ còn đọc được (diễn ý của trang) — [Wilke, Redundant coding](https://clauswilke.com/dataviz/redundant-coding.html)
- Tol: nền mạnh quá đậm cho chữ đen; nền Pale/Light giữ chữ đen dễ đọc — [Paul Tol](https://sronpersonalpages.nl/~pault/)
- Skill dataviz: chữ đặt trong ô màu dùng `#ffffff`, trừ nền vàng/cảnh báo dùng gần đen; "Text wears text tokens,
  never the series color" — `dataviz/references/palette.md`, `dataviz/SKILL.md` (đường dẫn như mục 1)
- Số đo trong phiên (công thức W3C ở trên): nền hiện tại plain `F5F6F8` L* 96,9; model `FBEFE8` 95,2; store
  `EAF1FB` 94,9; offline `ECF8F1` 96,5; tương phản với giấy trắng 1,08–1,14:1. Nền tiêu đề bảng `E7E6E6` L* 91,4;
  hàng dùng `D9D9D9` L* 86,7, INK trên đó 11,19:1. MUTED trên M1 5,27–5,62:1, trên M2 3,40–3,93:1, trên M3
  1,87–2,19:1, trên M4 1,02–1,23:1.

### Inferences
- Quy tắc chuyển chữ: L* nền ≥ ~58 → chữ INK `1F2328` (đậm nếu L* < 70); L* nền ≤ ~40 → chữ trắng đậm; 40 < L*
  < 55 → tránh làm nền chữ. Với thang khác (ví dụ Tol), tính lại bằng công thức W3C chứ không ước bằng mắt.
- Ở cỡ 9,5 pt đậm, ngưỡng vẫn là 4,5:1 (chỉ từ 14 pt đậm mới hạ còn 3:1) — nên không viện dẫn "chữ đậm" để hạ
  chuẩn cho chữ trong hộp.
- **Kiểm in xám** (hai bước, làm cho cả sơ đồ lẫn hình): (a) tính L* mỗi màu nền/màu chuỗi, yêu cầu các mức kề
  nhau cách ≥ ~15 L* (ngưỡng mượn từ "normal-vision floor ΔE ≥ 15" của skill dataviz, vốn đo trên OKLab — đây là
  phép tương tự, không phải chuẩn); (b) xuất PDF từ Word, chuyển trang sang xám (Pillow `ImageOps.grayscale` trên
  ảnh render, hoặc in thử "Grayscale" trong hộp in) và đọc lại bằng mắt: mỗi mức và mỗi chuỗi phải phân biệt được
  mà không cần chú giải màu.
- Mức "đóng góp chính" M4 có tương phản nền–giấy 6,5–7,9:1, còn M1 hiện tại 1,08–1,14:1 → sau khi đổi, sơ đồ có
  dải tương phản rộng, phần nhấn nổi rõ cả khi in máy laser đơn sắc.

### Gaps
- Chưa tìm thấy chuẩn riêng cho tương phản trên giấy in (WCAG là chuẩn màn hình); dùng WCAG làm thước thay thế là
  giả định hợp lý, nhưng máy in laser rẻ thường làm nền trung bình đậm hơn — cần in thử một trang.
- Không fetch được SC 1.4.11 (non-text contrast 3:1) trong phiên này; mục 4 dùng 3:1 cho nét/điểm theo skill
  dataviz ("Contrast vs surface … below 3:1 — relief required").

## 3. Quy ước bảng học thuật (booktabs, APA 7, IEEE) và ô tiêu đề trắng

### Takeaway
APA 7 và booktabs đều dùng ít đường kẻ: kẻ ngang ở đỉnh, dưới hàng tiêu đề, đáy bảng; không kẻ dọc, không kẻ ô;
không nguồn nào yêu cầu tô nền tiêu đề — tiêu đề phân biệt bằng chữ đậm/căn giữa và một đường kẻ. Mẫu khoa cũng
để ô trắng, nhưng kẻ lưới đủ, nên có hai phương án hợp lệ: (A) kiểu booktabs/APA, (B) giữ lưới của mẫu khoa,
chỉ bỏ nền xám tiêu đề.

### Cited Findings
- APA 7: "Tables should only include borders and lines that are needed for clarity"; "Do not use vertical borders,
  and do not use borders around each cell"; kẻ ở "top and bottom of table, beneath column headings, above table
  spanners"; "Spacing and strict alignment is typically enough to clarify relationships between elements"; tiêu
  đề cột căn giữa (checklist "Are column headings centered?") — [Purdue OWL, APA Tables and Figures](https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/apa_tables_and_figures.html)
- APA 7 về hình: "Shading and color should be limited for clarity"; nên "use patterns along with color" cho người
  mù màu hoặc "readers printing in grayscale"; "Gridlines and 3-D effects should be avoided unless they are
  necessary"; chữ trong hình "sans serif, consistently sized, and between 8-14 pt" — [Purdue OWL, APA Tables and Figures](https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/apa_tables_and_figures.html)
- Booktabs (qua Wikibooks): sách/tạp chí chuyên nghiệp "almost _never_ use vertical rules"; đường kép "regarded as
  unnecessary and distracting"; `\toprule`, `\midrule`, `\bottomrule` "ensures that the rule weight and spacing are
  acceptable"; `\cmidrule` cho đường kẻ chỉ dưới một nhóm cột — [Wikibooks, LaTeX/Tables](https://en.wikibooks.org/wiki/LaTeX/Tables)
- Tol: màu mạnh "too strong to use for backgrounds to mark (black) text, typically in a table"; muốn tô ô thì dùng
  bảng Pale (nền chữ đen) — [Paul Tol](https://sronpersonalpages.nl/~pault/)
- Mẫu khoa: 3 bảng mẫu `TableGrid` đủ sáu cạnh `sz="4"`, ô `w:fill="FFFFFF"` — tệp cục bộ `report/Mau bao cao
  KLTN_DS.docx` (giải nén `word/document.xml`, `word/styles.xml` trong phiên). `report/quy_cach_bao_cao.md` không
  quy định kiểu kẻ bảng, chỉ quy định tiêu đề bảng ở trên, căn giữa, cỡ chữ bảng 10–13.
- Quy ước nhấn của repo: in đậm giá trị tốt nhất, hàng `D9D9D9` = cấu hình đang dùng, ghi chú dưới bảng —
  `report/quy_cach_bao_cao.md` dòng 84–86; mã `scripts/report_docx/ooxml.py` dòng 253: `fill = "E7E6E6" if header
  else ("D9D9D9" if used else "")`.

### Inferences
- **Ô tiêu đề trắng**: đổi dòng 253 thành `fill = "D9D9D9" if used and not header else ""` — không đụng số liệu.
  Phù hợp cả APA (không tô) lẫn mẫu khoa (ô trắng).
- **Phương án A — booktabs/APA (khuyên cho bảng kết quả)**, viết thẳng OOXML:
  `tblBorders`: `top` single `sz=12` (1,5 pt), `bottom` single `sz=12`, `left/right/insideV` `nil`, `insideH`
  `nil`; ô hàng tiêu đề thêm `tcBorders/bottom` single `sz=6` (0,75 pt); tiêu đề nhóm cột (spanner) chỉ kẻ
  `bottom sz=4` dưới các ô được gộp, chừa khoảng hở hai đầu nếu được; hàng tổng/hàng tóm tắt kẻ `top sz=4`.
  Bảng dài (> ~12 hàng) có thể thêm `insideH` `sz=2` màu `BFBFBF` (đường mảnh nhạt) thay cho tô sọc.
- **Phương án B — giữ lưới mẫu khoa**: giữ sáu cạnh `sz=4`, bỏ nền tiêu đề, chỉ làm đậm đường dưới tiêu đề
  (`tcBorders/bottom sz=12`). Ít lệch mẫu nhất nếu hội đồng quen bảng lưới; nên hỏi GVHD trước khi chọn A.
- **Tiêu đề**: chữ đậm, căn giữa (đã có), không tô; đơn vị đặt trong tiêu đề cột ("Độ trễ (s)"); `tblHeader` lặp
  tiêu đề khi bảng sang trang (đã có).
- **Thân bảng**: số căn phải (đã có, `_NUMERIC`), cùng số chữ số thập phân trong một cột, dấu phẩy thập phân;
  cột chữ căn trái.
- **Không tô sọc (zebra)**: APA nói khoảng cách/căn lề thường đủ; thêm sọc xám sẽ xung đột với nghĩa "hàng xám =
  cấu hình đang dùng".
- **Đánh dấu cấu hình đang dùng không cần màu**: (i) giữ `D9D9D9` — L* 86,7, chữ INK 11,19:1, in xám vẫn rõ, đã ghi
  quy ước nên ít rủi ro; hoặc (ii) bỏ nền, thêm ký hiệu "†" sau tên cấu hình + ghi chú dưới bảng "† cấu hình hệ
  thống cuối", có thể kèm chữ nghiêng cho cả hàng. Nếu chọn (ii) phải sửa `quy_cach_bao_cao.md` dòng 84–86 và
  bộ đánh dấu `USED_MARK` trong `ooxml.py`.
- **Giá trị tốt nhất**: giữ in đậm (đã quy ước, kèm câu "in đậm không hàm ý khác biệt có ý nghĩa"). Không dùng màu
  chữ cho tốt/xấu.

### Gaps
- Trang APA chính thức (apastyle.apa.org, trang "tables" và "table setup") trả về nội dung rỗng khi fetch (trang
  dựng bằng JS); dùng Purdue OWL làm nguồn thứ cấp.
- Không trích được nguyên văn tài liệu booktabs (PDF CTAN tải được nhưng không có thư viện đọc PDF trong .venv);
  độ dày mặc định `\heavyrulewidth`/`\lightrulewidth` (tôi nhớ là .08em/.05em) **chưa xác minh**.
- Đơn vị `w:sz` của đường kẻ bảng OOXML (1/8 pt theo ECMA-376) không fetch được (officeopenxml.com lỗi SSL); suy
  luận gián tiếp: style `TableGrid` của mẫu dùng `sz="4"` và Word hiển thị nó là ½ pt — cần mở hộp Borders trong
  Word để xác nhận trước khi dùng `sz=12` = 1,5 pt.
- Không tìm được hướng dẫn bảng IEEE chính thức trong phiên này.

## 4. matplotlib: phông TNR có dấu tiếng Việt, mathtext, cỡ chữ theo bề rộng in, đường nét, dpi, bảng màu an toàn

### Takeaway
Thiết kế hình **đúng kích thước in** (15,5 cm hoặc 7,5 cm) với `layout="constrained"` và chèn đúng bề rộng đó, thì
cỡ chữ trong mã = cỡ chữ trên giấy; khi đó dùng 9–11 pt (APA: 8–14 pt). Hiện hình vẽ rộng 6,4–7,4 in rồi thu
xuống 10–15 cm, nên chữ trên giấy chỉ còn khoảng 5,3–7 pt. TNR trên máy có đủ dấu tiếng Việt; dùng `font.serif =
["Times New Roman", "DejaVu Serif"]` (dự phòng từng ký tự từ matplotlib 3.6) và `mathtext.fontset = "stix"`.
Bảng màu hiện tại không an toàn khi in xám (cam/lục/xám L* 57–61) và đang dùng cùng màu cho các thực thể khác nhau
giữa các hình.

### Cited Findings
- Dự phòng phông: "As of Matplotlib 3.6 the Agg, SVG, PDF, and PS backends will "fallback" through multiple fonts in
  a single Text instance"; "Each glyph of the string is rendered using the first font in the list that contains
  that glyph" — [matplotlib, Fonts](https://matplotlib.org/stable/users/explain/text/fonts.html)
- SVG: `svg.fonttype='path'` (mặc định) vẽ chữ thành đường, giống nhau trên mọi máy nhưng "the text will not be
  editable"; `'none'` giữ chữ thật nhưng phụ thuộc phông máy xem — [matplotlib, Fonts](https://matplotlib.org/stable/users/explain/text/fonts.html)
- mathtext có 5 bộ phông `dejavusans`, `dejavuserif`, `cm`, `stix` ("designed to blend well with Times"),
  `stixsans`, và `custom` (dùng `mathtext.rm` …, có `mathtext.fallback`), custom là "experimental feature for
  patient users only" — [matplotlib, Writing mathematical expressions](https://matplotlib.org/stable/users/explain/text/mathtext.html)
- APA: chữ trong hình "sans serif, consistently sized, and between 8-14 pt" — [Purdue OWL, APA](https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/apa_tables_and_figures.html)
- IEEE: ảnh màu/xám "> 300 dpi", hình nét đen trắng (line art) "> 600 dpi"; tăng độ phân giải sau khi tạo không cải
  thiện chất lượng; sách IEEE khuyên vector cho line art — [IEEE Author Center, Resolution and Size](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/resolution-and-size/)
  (qua tóm tắt kết quả tìm kiếm, không mở trang trực tiếp)
- Paul Tol High-contrast `#004488 #DDAA33 #BB5566` hợp in đơn sắc; Vibrant red `#CC3311` — [Paul Tol](https://sronpersonalpages.nl/~pault/)
- Mã hóa kép: "use color to enhance the visual appearance of the figure without relying entirely on color"; đổi
  hình dạng điểm giúp "even the fully desaturated gray-scale version of the figure is legible"; "Whenever possible,
  design your figures so they don't need a legend"; thứ tự chú giải khớp thứ tự dữ liệu — [Wilke, Redundant coding](https://clauswilke.com/dataviz/redundant-coding.html)
- Skill dataviz: "One axis. Never a dual-axis chart"; "a legend is always present for >= 2 series", nhãn trực tiếp
  dùng chọn lọc; hatch/texture chỉ 45°/135° và chỉ cho in/khả năng tiếp cận — `dataviz/SKILL.md`,
  `references/marks-and-anatomy.md`, `references/palette.md`
- Kiểm cục bộ trong phiên: matplotlib 3.11.2; TNR 7.13 không thiếu ký tự Việt/ký hiệu nào đã thử; hình thử với
  `figsize=(15.5/2.54, 6/2.54)`, `layout="constrained"`, `savefig(dpi=300)` (không `bbox_inches`) ra đúng
  1830 × 708 px = 15,49 × 5,99 cm, metadata 300 dpi, 0 cảnh báo phông; chữ Việt, `α`, `Δ ≥ −0,1` hiển thị đúng
  (ảnh thử: `C:\Users\patph\AppData\Local\Temp\claude\85ae35366b529c68\b4942c2f-c1bf-4b4b-81ce-f0801cbaaca1\scratchpad\viz\test_fig.png`).
- Kiểm bảng màu bằng `scripts/validate_palette.js` của skill dataviz (`--mode light --pairs all`):
  - Bảng hiện tại `2A78D6, EB6834, 2F9E44, 8C959F`: CVD **WARN** — cặp lục↔cam ΔE 6,1 (protan), tritan 5,3; xám
    rớt chroma. L*: 50,4 / 59,7 / 57,5 / 61,3 → cam, lục, xám gần như trùng khi in xám. Hình `fig_data_profile` dùng
    đúng cam = dev, lục = test (`SPLIT_COLORS`).
  - Okabe–Ito `0072B2, D55E00, 009E73, E69F00`: PASS mọi kiểm (CVD xấu nhất ΔE 11,0), nhưng L* 46 / 54 / 58 / 71 —
    đỏ son và xanh lục lam chỉ cách 3,5 L*, không phân biệt khi in xám nếu không có kênh phụ.
  - Đề xuất hệ thống `004488, CC3311, 888888, BBBBBB`: CVD PASS (xấu nhất ΔE 13,1 deutan), thị giác thường PASS
    (16,5); FAIL "lightness band" và "chroma floor" (do hai màu xám và một màu rất đậm — chủ ý, xem Inferences);
    WARN `BBBBBB` 1,92:1 với nền trắng. L*: 29,2 / 46,0 / 56,7 / 75,9.
- Trong mã hiện tại, cùng một màu mang nghĩa khác nhau giữa các hình: BLUE = train (`SPLIT_COLORS`), = nhánh B
  (`fig_rq1_seeds`), = B0 + LBR V2 (`fig_per_class`), = micro (`build_final_figures`); GRAY = B0 trong
  `fig_per_class` — `scripts/build_research_figures.py` dòng 34, 309–314, 350; `scripts/build_final_figures.py` dòng 65.

### Inferences
- **Khối rcParams đề xuất** (thay hai khối `plt.rcParams.update` hiện có; không đổi số liệu):

  ```python
  CM = 1 / 2.54
  FULL_W, HALF_W = 15.5 * CM, 7.5 * CM          # bề rộng in; chèn bằng {width=15.5cm} / {width=7.5cm}
  plt.rcParams.update({
      "font.family": "serif",
      "font.serif": ["Times New Roman", "DejaVu Serif"],   # DejaVu chỉ đỡ ký tự TNR thiếu
      "mathtext.fontset": "stix",                            # hợp với Times
      "axes.unicode_minus": True,                            # U+2212, TNR có
      "font.size": 10, "axes.titlesize": 10.5, "axes.labelsize": 10,
      "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9,
      "figure.titlesize": 11,
      "axes.linewidth": 0.8, "axes.edgecolor": "#57606A", "axes.labelcolor": "#1F2328",
      "xtick.color": "#57606A", "ytick.color": "#57606A",
      "xtick.major.width": 0.8, "ytick.major.width": 0.8,
      "xtick.major.size": 3, "ytick.major.size": 3,
      "axes.spines.top": False, "axes.spines.right": False,
      "axes.grid": False, "grid.color": "#D9D9D9", "grid.linewidth": 0.5,  # bật theo một trục khi cần
      "lines.linewidth": 1.5, "lines.markersize": 5, "errorbar.capsize": 0,
      "legend.frameon": False, "hatch.linewidth": 0.6,
      "figure.dpi": 150, "savefig.dpi": 300, "savefig.facecolor": "white",
      "figure.constrained_layout.use": True,
  })
  ```
  Bỏ `bbox_inches="tight"` (nó cắt/nới viền làm bề rộng ảnh lệch khỏi `figsize`, khiến cỡ chữ in không còn đúng);
  dùng `figsize=(FULL_W, h*CM)` và chèn đúng `{width=15.5cm}`.
- **Cỡ chữ theo thân bài 13 pt** (cỡ trên giấy): số trên trục 9 pt (≈ 0,7×), nhãn trục/chú giải 10 pt (≈ 0,77×),
  tiêu đề ô 10,5–11 pt, chú thích nhỏ trong hình không dưới 8 pt (sàn APA). Hình nửa bề rộng (7,5 cm) giữ **cùng**
  cỡ chữ in, nên phải ít nhãn hơn chứ không thu chữ. Ước tính hiện trạng: hình `figsize` 7,2 in (18,3 cm) chèn 15 cm
  → hệ số ≈ 0,82 → chữ 8,5 pt thành ≈ 7 pt, nhãn lớp 6,5 pt thành ≈ 5,3 pt (con số gần đúng vì `bbox_inches` làm
  bề rộng thực khác `figsize`).
- **Serif hay sans**: APA khuyên sans trong hình; đề nghị của người dùng là khớp Times New Roman với thân bài. Cả hai
  đều chấp nhận được trong khóa luận; chọn TNR cho đồng bộ với mẫu khoa (mọi thứ một phông), nhưng phải giữ ≥ 8 pt
  vì serif nhỏ khó đọc hơn khi in.
- **Dấu thập phân**: dùng `matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.2f}".replace(".", ","))` cho trục
  và `$0{,}05$` trong mathtext (đã thử chạy được); tránh `axes.formatter.use_locale` vì tên locale Windows khác Linux.
- **Định dạng xuất**: PNG 300 dpi cho hình có màu/nền (hợp với quy trình Pandoc hiện tại); hình chỉ có nét (sơ đồ,
  đường cong) có thể 600 dpi theo IEEE nếu dung lượng cho phép. SVG chèn được vào Word 365 nhưng quy trình dựng hiện
  chỉ khai báo kiểu nội dung `png` (`scripts/report_docx/package.py` dòng 416–418) — đổi sang SVG là việc riêng,
  không cần cho bản in. matplotlib không xuất EMF trực tiếp.
- **Bảng màu theo thực thể, dùng chung cho mọi hình** (màu + hình điểm + kiểu nét, để in xám vẫn tách):

  | Thực thể | Màu | L* | Tương phản nền trắng | Điểm | Nét |
  |---|---|---|---|---|---|
  | LBR V2 (đề xuất chính) | `#004488` | 29,2 | 9,62 | ● tròn đặc | liền 1,5 pt |
  | LBR V3 (cấu hình ứng dụng) | `#CC3311` | 46,0 | 5,19 | ▲ tam giác | gạch |
  | B0 (hệ cơ sở) | `#888888` | 56,7 | 3,54 | ■ vuông | liền 1,0 pt |
  | f2 (mốc lịch sử) | `#BBBBBB` viền `#555555` | 75,9 | 1,92 (cần viền tối/nhãn trực tiếp) | ○ tròn rỗng | chấm |

  Quy ước xuyên suốt: "đề xuất" luôn xanh đậm `#004488`, "cơ sở/mốc" luôn xám — đúng nguyên lý accent của Wilke.
  Validator dataviz báo FAIL "lightness band/chroma" cho bộ này vì nó kiểm bảng màu **màn hình** coi mọi chuỗi
  ngang hàng; với bản in đen trắng ta cố ý trải độ sáng và cố ý để cơ sở màu xám, còn CVD và thị giác thường đều
  PASS.
- **Thang thứ tự** (ordinal, một sắc độ, bậc gần nền ≥ 2:1 theo skill dataviz):
  - train / dev / test: `#6BAED6` (L* 68,2; 2,43:1) / `#2171B5` (46,3; 5,13:1) / `#08306B` (20,9; 12,76:1).
  - Cách sinh mô tả RQ2 (mức ràng buộc tăng dần): mẫu cố định `#BDBDBD` + hatch `//` (tham chiếu) / LLM tự do
    `#9E9AC8` (65,4) / LLM ràng buộc `#6A51A3` (40,6) / ràng buộc + phủ `#3F007D` (18,1).
  - Chế độ truy hồi RQ3: vector_only `#BBBBBB`, structured_only `#888888`, hybrid `#CC3311`, backfill (cải tiến
    ADR-0049) `#004488` — giữ quy ước "đề xuất = xanh đậm".
- **Hatch cho cột khi in xám**: chỉ `//` và `\\` (45°/135°, theo skill dataviz), `hatch.linewidth` 0,6; chỉ dùng
  khi hai chuỗi cột kề nhau có L* cách < 15.
- **Lưới và trục**: chỉ một trục lưới (trục giá trị), `#D9D9D9` 0,5 pt, nằm dưới dữ liệu (`ax.set_axisbelow(True)`);
  bỏ khung trên/phải; không dùng trục kép.

### Gaps
- Không fetch các trang matplotlib "Figure size in different units" và "Constrained layout guide"; hành vi
  `figsize` theo cm và `layout="constrained"` đã được **kiểm trực tiếp** bằng ảnh thử ở trên thay cho trích dẫn.
- Chỉ thông số `pdf.fonttype=42` (nhúng TrueType) là kiến thức sẵn, không có trong trang Fonts đã đọc; không cần
  cho quy trình PNG hiện tại.
- Trang IEEE chỉ đọc qua tóm tắt tìm kiếm; trang cũ hơn của IEEE ghi 400 dpi cho TIFF màu — mâu thuẫn nhỏ, không
  ảnh hưởng vì khóa luận dùng PNG 300 dpi.

## 5. Dạng biểu đồ hợp cho kết quả SED/RAG (và dạng nên tránh)

### Takeaway
Với số liệu của khóa luận, hiệu quả nhất là: **dot/forest plot khoảng tin cậy của hiệu số ghép cặp** (thay vì đọc
chồng lấn CI), **dumbbell/slope** cho dev→test và B0→V2 theo lớp, **heatmap một sắc độ** cho nhầm lớp/đồng xuất
hiện, **thanh xếp chồng/thác nước** cho phân rã lỗi, **piano-roll** cho dòng thời gian sự kiện (chỉ trên dev/OOF),
**reliability diagram**, **đường PSD-ROC/quét ngưỡng**, **box/violin + điểm** cho sai số onset và độ trễ. Tránh radar,
tròn/vành khuyên, trục kép, 3-D, thang cầu vồng, cột + thanh sai số cho dữ liệu phân phối.

### Cited Findings
- Thanh sai số: "you must specify what quantity and/or confidence level the error bars represent"; người đọc có thể
  hiểu sai thanh sai số là min–max; bỏ mũ thanh (cap) giúp khi nhiều thanh — [Wilke, Visualizing uncertainty](https://clauswilke.com/dataviz/visualizing-uncertainty.html)
- So chồng lấn CI: các quy tắc ngón tay cái "are not reliable and should be avoided"; "The correct way … is to
  calculate confidence intervals for the differences. If those confidence intervals exclude zero, then we know the
  difference is significant" — [Wilke, Visualizing uncertainty](https://clauswilke.com/dataviz/visualizing-uncertainty.html)
- Cột + thanh sai số "represent neither the variation within each category nor the uncertainty of the sample means
  particularly well" — [Wilke, Visualizing uncertainty](https://clauswilke.com/dataviz/visualizing-uncertainty.html)
- Boxplot "divides the data into quartiles"; violin "can be used whenever one would otherwise use a boxplot" nhưng
  phải "verify that you have sufficiently many data points in each group", nếu thưa thì violin "can generate the
  appearance that there is data where none exists" → vẽ điểm (strip/jitter/sina) — [Wilke, Boxplots and violins](https://clauswilke.com/dataviz/boxplots-violins.html)
- Radar: so sánh khó vì bố cục tròn; hình dạng "highly depends on the ordering of categories"; diện tích tăng
  "quadratically"; nhiều chuỗi thì "unreadable"; thay bằng thanh/lollipop xếp hạng, lollipop hai chuỗi, small
  multiples, parallel coordinates — [data-to-viz, The Radar chart and its caveats](https://www.data-to-viz.com/caveat/spider.html)
- Skill dataviz: trước→sau theo từng mục → **dumbbell** (một sắc độ, hai sắc thái); so độ lớn → cột/thanh, lưới →
  **heatmap** một sắc độ; tránh trục kép, tròn 2 lát, vành khuyên cho giá trị gần nhau; >4 chuỗi hội tụ → small
  multiples — `dataviz/references/choosing-a-form.md`, `anti-patterns.md`, `marks-and-anatomy.md`
- APA: tránh "3-D effects" và lưới trừ khi cần — [Purdue OWL, APA](https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/apa_tables_and_figures.html)
- PSDS: điểm PSDS là diện tích dưới đường PSD-ROC dựng từ nhiều điểm vận hành; bài gốc có hình các đường PSD-ROC
  của ba hệ thống — [Bilen et al., arXiv 1910.08440](https://arxiv.org/abs/1910.08440); cách tính độc lập ngưỡng —
  [Ebbers et al., arXiv 2201.13148](https://arxiv.org/abs/2201.13148); `psds_eval` có hàm `plot_psd_roc(psds_score,
  filename=…)` (ví dụ dùng trong [FlexSED evaluation_measures.py](https://huggingface.co/spaces/OpenSound/FlexSED/blob/main/src/utils/evaluation_measures.py)); README
  psds_eval ghi đường PSD-ROC không còn chắc đơn điệu khi `alpha_st ≠ 0` (theo tóm tắt tìm kiếm).
- Nguồn quen thuộc **không mở lại trong phiên này** (cần xác minh trước khi trích trong báo cáo): reliability
  diagram cho định cỡ — Guo et al. 2017, "On Calibration of Modern Neural Networks" ([arXiv 1706.04599](https://arxiv.org/abs/1706.04599));
  kiểu lỗi chèn/xóa/thay thế cho SED đa âm — Mesaros et al. 2016 ([doi:10.3390/app6060162](https://doi.org/10.3390/app6060162));
  công cụ vẽ piano-roll sự kiện `sed_vis` ([TUT-ARG/sed_vis](https://github.com/TUT-ARG/sed_vis)).

### Inferences
Danh mục áp vào artifact đã có (mọi hình đọc measurement đã khóa; không mở `predictions/test.npz`, không tính
lại metric trên test — đúng giao thức trong CLAUDE.md):

| Câu hỏi | Dạng đề xuất | Dữ liệu sẵn có | Ghi chú thiết kế |
|---|---|---|---|
| V2 hơn B0 bao nhiêu, chắc đến đâu (và RQ1 C−B, S13 Δ) | **Forest plot của hiệu số ghép cặp**: một hàng/so sánh, chấm = Δ, đoạn = CI 95% bootstrap, đường dọc ở 0 | `final_numbers_20261110.json`, `rq1_*_multiseed_*.json`, `s13_test_20261018.json` | Theo Wilke, vẽ CI của hiệu số thay vì để người đọc so CI chồng lấn; tô xanh đậm hàng có CI không chứa 0, xám hàng chứa 0; ghi số Δ ngay cạnh |
| Mức micro/macro của các hệ | Dot plot ngang + CI (thay cột) | như trên | Dot plot không cần trục bắt đầu từ 0 như cột |
| Dev(OOF) → test có tụt không | **Slope chart** (≤ ~10 hệ) hoặc scatter dev–test có đường y = x (đã có `fig_dev_vs_test`) | `s13_ranking_annotated_20260928.json`, `s13_test_20261018.json` | Làm nổi hệ được chọn, các hệ khác xám |
| F1 theo lớp B0 → V2 | **Dumbbell** sắp theo Δ (đã có, nên sắp theo Δ thay vì theo tên), ghi n mỗi lớp | `lbr_context_20261123.json` | Chấm xám = B0, chấm xanh đậm = V2; tách lớp tăng/giảm bằng hướng đoạn |
| Lớp nào bị nhầm với lớp nào; lớp nào cùng xuất hiện | **Heatmap** một sắc độ (Blues), ghi số trong ô, thứ tự lớp theo cụm | `confusable_pairs_*` (dev), `data_profile_20261008_lf.json` | Thang tuần tự một sắc độ in xám vẫn đọc được; chữ trong ô đổi trắng ở ô tối theo quy tắc mục 2 |
| Vì sao bỏ sót (phân rã FN) | **Thanh xếp chồng 100 %** hoặc **thác nước** từ tổng sự kiện GT → TP, trừ dần theo loại lỗi | `lbr_diagnosis_20261109.json` (OOF) | Loại lỗi là thứ tự → một sắc độ; ≤ 6 phần, gộp phần đuôi |
| Hệ dự đoán ra sao trên một bản ghi | **Piano-roll**: mỗi lớp một làn, thanh GT mảnh/rỗng phía trên, thanh dự đoán đặc phía dưới, tô TP/FP/FN bằng độ sáng + hatch | Bản ghi dev/OOF (đã có `m05_dev_timeline.png`) | Chỉ dev/train để không chạm test |
| Mô hình có quá tự tin không | **Reliability diagram** (đường chéo tham chiếu, cột độ chính xác theo bin, kèm biểu đồ số mẫu/bin) | `calibration_20261123.json` | Ghi ECE ở góc |
| Đánh đổi độ phủ–báo nhầm theo ngưỡng | **Đường PSD-ROC** chồng cho B0/V2/V3, hoặc **đường quét ngưỡng** F1(θ) có vạch θ đã chọn | Chỉ khi điểm vận hành đã lưu; quét θ trên dev | Phải cùng lưới ngưỡng (bài học ADR-0048); nếu điểm test chưa lưu thì **không** tính lại trên test |
| Onset lệch sớm/muộn theo lớp | **Box + strip** (hoặc sina) theo lớp, dải ±0,2 s tô xám | `lbr_diagnosis_20261109.json` (OOF) | Violin chỉ cho lớp đủ điểm (Wilke) |
| Truy hồi: nDCG theo chế độ × kho | **Small multiples** dot plot + CI, một ô/kho; kèm strip hiệu số theo truy vấn (đã có `fig_rq3_queries`) | `rq3_modes_20261123.json`, `retrieval_backfill_test_20261124.json` | Backfill xanh đậm, các chế độ khác xám/đỏ |
| Độ trễ demo | **ECDF** hoặc box + strip theo bước, trục log nếu đuôi dài | measurement độ trễ (`report_latency`) | Đánh dấu trung vị và p95 bằng chữ |
| Quá trình huấn luyện | Small multiples hoặc đường mảnh từng fold, nhấn epoch chọn | `ml/runs/<served>/…/history.json` | Đã có; chỉ cần đổi cỡ chữ/màu |

- **"Sinh động" mà không lòe loẹt**: mỗi hình một câu chú thích trực tiếp nói điều chính (mũi tên + chữ 9 pt), làm
  nổi một chuỗi đề xuất, phần còn lại xám; ghi số tại điểm cuối thay vì ghi trên mọi điểm.
- **Nên tránh** (kèm lý do có nguồn): radar (data-to-viz), tròn/vành khuyên để so giá trị gần nhau (skill dataviz),
  trục kép (skill dataviz), 3-D và lưới dày (APA), thang cầu vồng cho giá trị liên tục (Wilke), cột + thanh sai số
  khi muốn nói về phân phối (Wilke), đọc ý nghĩa từ việc CI chồng lấn (Wilke).

### Gaps
- Không tìm được bài DCASE dùng làm "chuẩn hình" có thể trích nguyên văn ngoài bài PSDS gốc; các dạng piano-roll và
  reliability diagram dựa trên nguồn quen thuộc chưa mở lại trong phiên này.
- Chương "paired data/slopegraph" của Wilke trả 404 ở URL đã thử; khuyến nghị slope chart dựa trên skill dataviz
  (dumbbell cho trước→sau) và suy luận.
- Chưa kiểm xem các điểm vận hành PSD-ROC trên test đã được lưu trong artifact hay chưa; nếu chưa, hình PSD-ROC
  test sẽ đòi tính lại trên test và vi phạm giao thức — người làm phải kiểm trước.
