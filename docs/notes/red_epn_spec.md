# RED + EPN — đặc tả để cài O-E

Ngày kiểm: 08/10/2026. Nguồn: Schmid và cs., *Sound Event Detection with
Boundary-Aware Optimization and Inference*,
[arXiv:2601.04178v2](https://arxiv.org/abs/2601.04178v2), 06/06/2026,
[PDF](https://arxiv.org/pdf/2601.04178v2), 5 trang, IEEE SPL 2026.
PDF đã tải ở lượt XO-4; SHA-256:
`d0648f2e4f73f39dcb930ab21ba7b5f79c0e2c82bf209f351a5ee96ed80fa4a6`.
Đọc lại `pdftotext -layout` và hình trang 3 để kiểm phân số của (4), (5), Algorithm 1.
Mức V3. Trang bên dưới là số in trên PDF, bắt đầu từ 1.

Đây là ghi chú triển khai, không phải model đã chạy. Phân biệt **bài báo** với
**suy ra/đề xuất kỹ thuật** ở từng phần. Các lựa chọn chưa được PDF khóa phải được
Claude ghi trước khi train. Không sửa ADR-0041 hoặc nhãn nguồn trong task này.

## 1. Ký hiệu và RED (tr.2, §II-A, (1)–(2))

Xét một lớp, bỏ chỉ số lớp để gọn. Acoustic model phải xuất hai logit mỗi frame:

\[
s_t=\sigma(z^{start}_t)=P(e_t\mid\neg e_{t-1}),\qquad
q_t=\sigma(z^{end}_t)=P(\neg e_t\mid e_{t-1}).
\]

Đó là xác suất **chuyển trạng thái có điều kiện**. RED không có tham số học thêm.
Gọi \(p_t=P(e_t)\), ba đầu ra là:

\[
\begin{aligned}
p_t &= s_t(1-p_{t-1})+(1-q_t)p_{t-1}, &&\text{presence, (1)}\\
o_t &= s_t(1-p_{t-1}), &&\text{onset, (2)}\\
f_t &= q_t p_{t-1}, &&\text{offset, (2).}
\end{aligned}
\]

Tính onset/offset từ **presence frame trước**, rồi mới cập nhật presence hiện tại.
Ba giá trị này liên kết qua \(p_t=p_{t-1}+o_t-f_t\), không phải ba head sigmoid
độc lập. Tensor đầu vào có thể là `[B,T,C,2]`, đầu ra `[B,T,C,3]`;
layout tensor cụ thể là đề xuất kỹ thuật, PDF không khóa.

PDF không cho giá trị khởi tạo \(p_0\) trước frame đầu, reset giữa clip, hoặc
cách xử lý event đã diễn ra từ trước cửa sổ. Chọn trước chính sách này.
Đặt presence trước clip = 0 là một lựa chọn có thể kiểm, **không phải** thông số
được bài công bố; nó buộc onset ở đầu clip nếu model cần active ngay.

**Suy ra để kiểm số học:** nếu đầu vào hợp lệ thì \(p,o,f\in[0,1]\),
\(o_t+f_t\le1\). Cùng một lớp không mô hình hóa hai event chồng lấn riêng biệt;
polyphony giữa các lớp vẫn hợp lệ vì mỗi lớp có recurrence riêng.

## 2. Target và loss biên (tr.2, §II-B, (3))

Bài báo tạo \(y^{on}_{c,t},y^{off}_{c,t}\) bằng 1 tại frame có onset/offset,
0 tại frame còn lại. Presence là nhãn frame nhị phân. Không công bố kernel mềm,
độ rộng quanh biên, phép round/floor/ceil từ giây sang frame hay quy tắc clip bị cắt.
Vì vậy không được gọi Gaussian target hoặc nhãn mềm DO-3 là tái lập nguyên bản.

Với \(u\) là \(o\) hoặc \(f\), viết lại (3) dưới dạng tiện cài:

\[
L^u=-\frac{1}{CT}\sum_{c,t}
\left[y^u_{c,t}(1-u_{c,t})^2\log u_{c,t}
+(1-y^u_{c,t})u_{c,t}^2\log(1-u_{c,t})\right].
\]

**Tên tham số dễ nhầm:** PDF gọi số mũ focal là **α = 2**. Theo nhiều API,
số mũ này mang tên **γ = 2**; (3) không có hệ số cân bằng positive/negative α
riêng. Không tự đưa `alpha=.25` vào và gọi là đúng bài. Áp loss lên \(o,f\)
của RED, không lên \(s,q\) có điều kiện. BCE presence dùng \(p\) của RED
(tr.3, đoạn trước (5)); PDF không viết riêng phương trình BCE hoặc chi tiết reduction.

**Cần quyết trước ở DataSED:**

- Lưới đích 40 ms hay lưới nhãn 10 ms hiện có; một nhãn biên có đúng một frame.
- Event kết thúc đúng cuối clip có offset ngoài `[0,T)`; dùng sentinel, frame cuối,
  hay mask censoring phải được ghi rõ. Đừng làm mất hoặc dồn mọi biên về cuối.
- Cửa sổ cắt giữa event: không tạo onset/offset nhân tạo tại mép cửa sổ.
- Gán đôi DO-3: tạo target biên trên từng bản rồi kết hợp thế nào; không lấy đạo hàm
  nhãn presence mềm để mặc định đó là target của (3).
- Mask padding phải áp cho mọi loss và mẫu số; clip không có active frame vẫn có
  BCE/OOL, nhưng cần định nghĩa IoU = 0 cho clip đó thay vì chia 0.

Các điểm này là đề xuất triển khai, PDF không giải quyết.

## 3. EPN và loss vùng (tr.2–3, §II-C, (4)–(5))

EPN nhận **ba xác suất RED**, dùng **BiGRU hai lớp**, xuất hai khoảng thời gian
dương qua Softplus cho mỗi lớp/frame: thời gian từ onset \(\hat d^{on}\) và thời
gian đến offset \(\hat d^{off}\).

| Biến thể bài báo | Input mỗi chuỗi | Output mỗi frame | Thông số đã nêu |
|---|---|---|---|
| Per-Class GRUs | 3 kênh của một lớp; C GRU riêng | 2 duration | khoảng 26K tham số/lớp (tr.4 §IV-A); không nêu hidden size |
| Single GRU | 3C kênh; một GRU chung | C×2 duration | hidden dimension 256, thêm 4,1M tham số cho 447 lớp (tr.4 §IV-C) |

PDF không ghi cụ thể lớp projection sau GRU, dropout, bias, normalization,
cách khởi tạo duration hay có detach xác suất đầu vào hay không. Không suy
hidden size 256 cho biến thể per-class từ thông số của Single GRU.

Tại frame active, ground truth duration cho event chứa frame đó là:

\[
d^{on}_{c,t}=t-a_c,\quad d^{off}_{c,t}=b_c-t,\quad
r_{c,t}=[t-d^{on}_{c,t},t+d^{off}_{c,t}],\quad
\hat r_{c,t}=[t-\hat d^{on}_{c,t},t+\hat d^{off}_{c,t}].
\]

PDF dùng chung ký hiệu \(t\) cho frame index và thời gian; chú thích 2 tr.3 nêu
\(t=f\Delta t\). **Đơn vị duration trong loss không được công bố dứt khoát.**
IoU không phụ thuộc đổi đơn vị, nhưng hệ số \(1/(d^{on}+d^{off})\) có phụ thuộc.

Đúng (4), giữ cả hai mẫu số:

\[
L^{iou}=\frac{1}{\sum_{c,t}y^{pres}_{c,t}}
\sum_{c,t}y^{pres}_{c,t}
\frac{1-\operatorname{IoU}(r_{c,t},\hat r_{c,t})}
{d^{on}_{c,t}+d^{off}_{c,t}}.
\]

Không thay mẫu số ngoài bằng số event hoặc tổng trọng số nghịch duration.
Trong một event, \(d^{on}+d^{off}\) bằng độ dài event; trọng số nghịch độ dài
giảm sự lấn át của event dài. Cả hai interval chứa cùng điểm neo \(t\) nên có
giao khi độ dài dương. IoU chỉ train trên frame active; không có Hungarian matching.
Với event cùng lớp chồng lấn, PDF không nêu chọn event nào làm duration target.

**Suy ra tiện cài cho interval 1D:**

\[
I=\max(0,\min(b,\hat b)-\max(a,\hat a)),\qquad
U=(b-a)+(\hat b-\hat a)-I,\quad IoU=I/U.
\]

Loss tổng theo (5):

\[
L^{total}=L^{pres}+\lambda_{ool}(L^{on}+L^{off})+\lambda_{iou}L^{iou},
\qquad\lambda_{ool}=100.
\]

λiou được tune trong **{0.5, 1, 2, 4}** ở AS-Strong-10 (tr.3 §III-B).
Không có giá trị thắng riêng cho từng backbone trong PDF. Aux onset/offset head
độc lập trên presence head hiện có là ablation O-E có thể làm, nhưng không phải
RED đầy đủ, và không mặc nhiên thừa hưởng (1)–(5).

## 4. Suy luận (tr.3, Algorithm 1 và §II-D)

Diễn giải theo thứ tự thao tác, không thêm ngưỡng NMS:

1. Tính mean presence theo thời gian cho từng lớp; giữ **top-m lớp**.
2. Trong mỗi lớp, mỗi frame là một proposal. Sắp proposal theo **presence tại
   frame neo**, giảm dần; chưa sắp theo confidence trung bình của vùng.
3. Lấy proposal đầu: \([t^*-\hat d^{on}_{c,t^*},t^*+\hat d^{off}_{c,t^*}]\).
4. Confidence event = mean presence trong interval vừa lấy.
5. Thêm event, bỏ các proposal **chồng lấn** với proposal đã lấy.
6. Lặp đến hết proposal hoặc đủ **k event của lớp đó**; hợp event giữa các lớp.

Mặc định bài: **k = 15, m = |C|**. Algorithm ghi k theo **mỗi lớp**, dù đoạn
văn §II-D dùng diễn đạt “per recording”; dùng điều kiện vòng lặp `|E_c| < k`
để tránh nhầm thành 15 event tổng mọi lớp. PDF không cho IoU threshold NMS dương,
cách xử lý hai vùng chỉ chạm mép, tie sorting hoặc minimum confidence vận hành.
Không tự thêm threshold NMS 0.5 hoặc bỏ confidence threshold của evaluation.

Đầu ra có confidence để quét PSDS. Để dùng F1/timeline ở dự án vẫn cần khóa điểm
vận hành bằng dev/OOF theo protocol; không suy từ khẩu hiệu “không tuning hậu xử lý”
rằng confidence threshold không cần thiết. Mean vùng có biên phân số, clipping
ngoài clip và proposal độ dài gần 0 đều cần một quy tắc triển khai đã ghi trước.

## 5. Siêu tham số và độ phân giải đã xác minh

| Mục | PDF | Giới hạn khi chuyển sang dự án |
|---|---|---|
| Acoustic backbones | CRNN, MN-GRU, BEATs, ATST-F (tr.3 §III-B) | Không phải mọi backbone đều có cùng lưới frame |
| OOL | focal exponent α=2; λool=100 (tr.2–3) | Không công bố class-balance α hoặc γ khác |
| EPN | hai lớp BiGRU + Softplus; per-class ở subset, Single GRU ở full (tr.2–4) | Hidden per-class và projection không nêu |
| NMS-like | k=15, m=C (tr.3) | k được nghiên cứu cho clip **10 s** |
| Subset train | batch128, tối đa100 epoch; AdamW wd=1e-3, cosine, warmup1000; EPN lr tối đa1e-3 (tr.3) | Không phải cấu hình VRAM 8GB đã đo |
| Full train | 70 epoch, Single GRU; còn lại theo nguồn [10] (tr.4 đầu trang) | Không đủ đặc tả đầy đủ chỉ từ PDF này |
| Augmentation | Freq-MixStyle, filter augmentation; transformer thêm frequency warping (tr.3) | Không công bố toàn bộ xác suất/cường độ |
| Độ phân giải frame | Không nêu Δt riêng cho từng model trong PDF; chỉ quan hệ t=fΔt (tr.3 chú thích 2) | Không được gán 10ms hoặc 40ms là thông số paper |

## 6. Ổn định số học và tích hợp frame_mn + BiGRU

Các đoạn sau là **suy ra/khuyến nghị kỹ thuật**, không phải chi tiết PDF công bố.

- Giữ recurrence/loss ở float32 khi backbone autocast fp16. `log(0)` và
  `log(1-p)` gần p=1 cần log-space hoặc clamp có epsilon ghi rõ; clamp không được
  âm thầm thay đổi model. BCEWithLogits không áp trực tiếp lên logit start/end
  để thay BCE của presence RED.
- Một recurrence log-space hai trạng thái giữ \(\ell^1=\log p\),
  \(\ell^0=\log(1-p)\). Với `LS(z)=logsigmoid(z)`:

  \[
  \begin{aligned}
  \ell^1_t&=\operatorname{logaddexp}(LS(z^{start}_t)+\ell^0_{t-1},
                                     LS(-z^{end}_t)+\ell^1_{t-1}),\\
  \ell^0_t&=\operatorname{logaddexp}(LS(-z^{start}_t)+\ell^0_{t-1},
                                     LS(z^{end}_t)+\ell^1_{t-1}),\\
  \log o_t&=LS(z^{start}_t)+\ell^0_{t-1},\quad
  \log f_t=LS(z^{end}_t)+\ell^1_{t-1}.
  \end{aligned}
  \]

  Cập nhật đồng thời từ trạng thái cũ. Đây là biến đổi đại số của (1)–(2);
  cần đối chiếu số/gradient với recurrence tuần tự trước khi tối ưu scan.
- Bài chỉ dẫn **Heinsen scan [32]**, không đưa implementation. Dạng affine
  \(p_t=s_t+(1-s_t-q_t)p_{t-1}\) có hệ số âm khi s+q>1; không lấy log hệ số đó
  rồi dùng scan chỉ dành cho số dương. Không khẳng định scan log-space đơn giản luôn hợp lệ.
- Softplus fp16 vẫn có thể underflow về 0. Epsilon ở duration/union và loss cho
  active-count=0 phải được khóa; không thực hiện phép chia 0 rồi nhân mask sau.
- `frame_mn` bản repo cho 250 bước/10s (**40ms**) trước bước nội suy về 1000 target
  10ms. RED/EPN có thể hoạt động ở 25Hz; không có cản trở toán học từ BiGRU.
  Nếu duration chuyển từ frame sang giây ở Δt=.04, cùng IoU nhưng loss nghịch
  duration tăng 25 lần; không chuyển đơn vị rồi giữ λiou như thể tương đương.
- K=15 trên **recording DataSED dài** có thể cắt recall dù phù hợp clip10s của
  paper. Phải khóa chính sách k theo cửa sổ/recording và ghép event xuyên cửa sổ.
- Ghép xác suất/logit conditional rồi RED không tương đương RED riêng từng cửa
  sổ rồi ghép presence (recurrence phi tuyến, phụ thuộc trạng thái). Duration
  proposal cũng không có ngữ nghĩa `predictions/dev.npz` presence hiện tại.
  Cần Claude định nghĩa contract/artifact và vị trí ghép trước khi tích hợp O-A.
- Dữ liệu gán đôi, biên cửa sổ và event cùng lớp nối tiếp/chồng lấn cần fixture
  riêng. RED hai trạng thái không bảo toàn instance cùng lớp chồng lấn; đó là giới
  hạn biểu diễn, không phải lý do âm thầm sửa raw annotation.

Kết luận khả thi kỹ thuật: frame_mn 40ms + BiGRU **không bị bài loại trừ**. Chưa
có parity, benchmark, cổng T0 hoặc số cải thiện DataSED; điều kiện tích hợp còn
ở khởi tạo/censoring, đơn vị duration, nhãn biên và contract ghép cửa sổ.
