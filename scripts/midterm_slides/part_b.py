"""Slide 11–16: sáu kịch bản thí nghiệm, mỗi slide một khung 4 ô (hỏi · làm · so · đo)."""

from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from scripts.midterm_slides import kit
from scripts.midterm_slides.deck import Deck
from scripts.midterm_slides.kit import Run
from scripts.midterm_slides.part_a import FIG, RESULT_PAGES


def kb1(deck: Deck) -> None:
    slide = deck.content(4, "KB1 (RQ1): ba cách khởi đầu, chỉ khác nhau ở bước học thêm")
    kit.frame_row(slide, [
        ("Câu hỏi", "Học thêm trên DataSEC có giúp phát hiện sự kiện tốt hơn không?"),
        ("Cách làm", "Ba nhánh dùng cùng cách chia dữ liệu, cùng số vòng học, cùng cách ghép "
                     "sự kiện."),
        ("So sánh", "Nhánh C với nhánh B, lặp ở 2 công thức: v1 (3 lần B, 4 lần C), v2 (3 và 3)."),
        ("Đo bằng", "Event-F1, PSDS; khoảng tin cậy 95% và kiểm định t (Welch)."),
    ])
    lanes = [
        ("A", "Bắt đầu từ số 0", "Mạng nhỏ (CRNN)", None),
        ("B", "Mô hình CNN14 đã học AudioSet", "AudioSet: kho âm thanh lớn, 527 loại", None),
        ("C", "Mô hình CNN14 đã học AudioSet", "AudioSet: kho âm thanh lớn, 527 loại",
         "Học thêm DataSEC (22 loại âm)"),
    ]
    heads = [("Khởi đầu", 1.15), ("Học thêm", 5.45), ("Học bài chính", 9.1)]
    for label, x in heads:
        kit.text(slide, x, 2.6, 3.4, 0.32, label, size=12.5, bold=True, color=kit.GRAY)
    y = 3.0
    for code, start, start_note, extra in lanes:
        kit.badge(slide, 0.5, y + 0.2, code, size=0.55, fill=kit.NAVY, color=kit.WHITE, font=18)
        kit.box(slide, 1.15, y, 3.85, 0.95, fill=kit.WHITE, rounded=True)
        kit.text(slide, 1.3, y + 0.08, 3.6, 0.82, [[Run(start, bold=True, color=kit.NAVY)],
                                                   [Run(start_note, color=kit.GRAY)]],
                 size=13, anchor=MSO_ANCHOR.MIDDLE)
        kit.arrow(slide, 5.05, y + 0.33)
        if extra:
            kit.box(slide, 5.45, y, 3.2, 0.95, fill=kit.YELLOW, line=None, rounded=True)
            kit.text(slide, 5.6, y, 2.95, 0.95, extra, size=13.5, bold=True, color=kit.NAVY,
                     anchor=MSO_ANCHOR.MIDDLE)
        else:
            kit.box(slide, 5.45, y, 3.2, 0.95, fill="F5F7FA", line=kit.LINE, rounded=True)
            kit.text(slide, 5.6, y, 2.95, 0.95, "(không có)", size=13, color=kit.GRAY,
                     anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
        kit.arrow(slide, 8.7, y + 0.33)
        kit.box(slide, 9.1, y, 3.73, 0.95, fill=kit.READ_FILL, line=None, rounded=True)
        kit.text(slide, 9.25, y, 3.5, 0.95, "Học phát hiện sự kiện trên DataSED", size=13.5,
                 color=kit.NAVY, anchor=MSO_ANCHOR.MIDDLE)
        y += 1.1
    kit.box(slide, 0.5, 6.3, 12.33, 0.56, fill=kit.WARN_FILL, line=None, rounded=True)
    kit.text(slide, 0.7, 6.3, 12.0, 0.56, "Chỉ so **C với B**: hai nhánh chỉ khác đúng bước "
             "học thêm. So C với A sẽ trộn lẫn cả tác dụng của AudioSet.", size=13.5,
             anchor=MSO_ANCHOR.MIDDLE)
    kit.notes(slide, f"""
(1 phút) Ba nhánh có cùng điểm cuối: học phát hiện sự kiện trên DataSED. Khác nhau ở điểm khởi
đầu.
Câu hỏi RQ1 là C có hơn B không, vì hai nhánh này chỉ khác đúng một bước học thêm DataSEC.
Huấn luyện mô hình SED cho kết quả hơi khác nhau dù cùng seed, nên phải chạy nhiều lần và dùng
thống kê.
Kết quả ở slide {RESULT_PAGES['rq1']}.""")


def kb2(deck: Deck) -> None:
    slide = deck.content(4, "KB2: đo xem mô hình đầu (v1) sai ở đâu, rồi mới sửa")
    kit.frame_row(slide, [
        ("Câu hỏi", "Vì sao v1 tìm sự kiện kém, nên sửa chỗ nào?"),
        ("Cách làm", "Đo trên dev trước: điểm tối đa kiến trúc cho phép và loại lỗi."),
        ("So sánh", "v2 đầy đủ với v2 bỏ từng thay đổi (ablation), mỗi biến thể 1 lần chạy."),
        ("Đo bằng", "Event-F1 kiểm chứng chéo 5 phần trên dev; test chỉ chấm v2 đã chọn."),
    ])
    kit.stat(slide, 0.5, 2.6, 4.2, 1.95, "tối đa 0,63",
             "điểm cao nhất v1 có thể đạt, kể cả khi đoán đúng loại âm 100%: v1 chỉ quyết định "
             "theo khối 0,64 s, còn luật chấm cho lệch ≤ 0,2 s", value_size=26, size=12.5)
    kit.stat(slide, 0.5, 4.7, 4.2, 2.15, "112 · 417 · 357",
             "trong 886 sự kiện dev: khớp · đúng loại nhưng lệch biên · bỏ sót → lỗi nằm ở "
             "**biên sự kiện** và **bỏ sót**, không ở nhận nhầm loại", value_size=26, size=12.5)
    data = kit.TableData(["Thay đổi", "v1", "v2"], [
        ["Độ chi tiết thời gian", "khối 0,64 s (nén 64 lần)", "**khối 0,08 s (nén 8 lần)**"],
        ["Đọc theo trình tự thời gian", "không", "có (BiGRU 2 lớp)"],
        ["Số vòng huấn luyện", "8 vòng", "30 vòng"],
        ["Làm giàu dữ liệu", "không", "trộn hai âm (mixup), làm méo dải tần (FilterAugment)"],
    ], [False] * 4, "")
    kit.text(slide, 4.95, 2.6, 7.88, 0.35, "v2 sửa đúng những chỗ đã đo được", size=15,
             bold=True, color=kit.NAVY)
    kit.table(slide, data, 4.95, 3.0, 7.88, widths=[2.2, 2.3, 3.4], size=13, row_h=0.5)
    kit.card(slide, 4.95, 5.65, 7.88, 1.2, "", [
        f"Ablation: bỏ lần lượt từng thay đổi để biết thay đổi nào thật sự có tác dụng → kết "
        f"quả ở slide {RESULT_PAGES['v2']}.",
        "Giả thuyết ban đầu “xác suất bão hòa làm trễ biên” đã được đo và **bác bỏ**.",
    ], size=12.5)
    kit.notes(slide, f"""
(1 phút) Thay vì dò thử tham số, nhóm đo trước. Mô hình CNN14 bản v1 thu nhỏ trục thời gian 64
lần,
mỗi quyết định ứng với 0,64 giây, trong khi luật chấm chỉ cho lệch 0,2 giây; nên dù đoán đúng
loại 100%
điểm tối đa cũng chỉ 0,63. Phân loại lỗi trên dev cho thấy lỗi chủ yếu là lệch biên và bỏ sót.
v2 sửa đúng các chỗ này. Kết quả ở slide {RESULT_PAGES['v2']}.""")


def kb3(deck: Deck) -> None:
    slide = deck.content(4, "KB3: thử mô hình nền đã quen “nghe theo từng 40 ms”")
    kit.frame_row(slide, [
        ("Câu hỏi", "Mô hình nền đã học nhãn theo từng 40 ms có tốt hơn v2 không?"),
        ("Cách làm", "Mỗi cấu hình chạy 3 lần (3 seed), lấy trung bình xác suất (ensemble)."),
        ("So sánh", "T2a, T2b, focal loss và các tổ hợp với v2, trên cùng tập dev."),
        ("Đo bằng", "Event-F1 kiểm chứng chéo trên dev; chưa mở test ở bước này."),
    ])
    kit.picture(slide, FIG / "m02_sed_architectures.png", 0.5, 2.6, 4.9, 4.25)
    cards = [
        ("T2a · BEATs giữ nguyên", "Mô hình lớn (~90,4 triệu tham số), giữ nguyên; chỉ dạy phần "
         "đầu ra (~3,3 triệu tham số).", kit.NAVY),
        ("T2b · Frame-MobileNet dạy lại", "Mô hình nhỏ (~3 triệu tham số), dạy lại toàn bộ trên "
         "DataSED; ra kết quả mỗi 40 ms. **Hệ cuối f2 = T2b × 3 lần chạy.**", kit.BLUE),
        ("g1, g2 · Focal loss", "Đổi cách tính lỗi để mô hình chú ý hơn vào chỗ đoán sai khó, "
         "mong cứu các loại âm ít gặp.", kit.GREEN),
    ]
    y = 2.6
    for head, body, color in cards:
        kit.card(slide, 5.65, y, 7.18, 1.15, head, [body], accent=color, size=13, bullets=False)
        y += 1.27
    kit.box(slide, 5.65, 6.41, 7.18, 0.45, fill=kit.READ_FILL, line=None, rounded=True)
    kit.text(slide, 5.8, 6.41, 6.9, 0.45, "Lý do thử: văn liệu (Schmid và cộng sự, 2025) cho "
             "thấy giữ nguyên mô hình nền gần bằng dạy lại → rẻ, vừa GPU 8 GB.", size=11.5,
             anchor=MSO_ANCHOR.MIDDLE)
    kit.notes(slide, """
(1 phút) Mô hình CNN14 được dạy để nói "đoạn này có tiếng gì". Hai mô hình nền T2a, T2b được dạy
sẵn để nói "lúc nào có tiếng gì" theo từng 40 ms, nên hợp với bài đánh dấu thời điểm hơn.
Hình bên trái so kiến trúc v1, v2 và f2. Mỗi cấu hình chạy 3 lần rồi lấy trung bình vì huấn
luyện
không ổn định. Ở bước này chỉ dùng dev; test chỉ mở ở vòng chọn cuối (KB4).""")


def kb4(deck: Deck) -> None:
    slide = deck.content(4, "KB4: chọn hệ cuối bằng luật viết trước khi có kết quả")
    steps = ["Ghi trước 11 ứng viên và luật chọn", "Chấm cả 11 trên dev (kiểm chứng chéo 5 phần)",
             "Chọn ứng viên cao nhất là f2, commit lên git (c3f0033)",
             "Sau commit mới tạo dự đoán trên test", "Chấm test 1 lần, báo hết, không chọn lại"]
    width = (12.33 - 4 * 0.42) / 5
    for index, step in enumerate(steps):
        x = 0.5 + index * (width + 0.42)
        kit.box(slide, x, 1.4, width, 1.35, fill=kit.NAVY if index in (2, 4) else kit.WHITE,
                rounded=True)
        color = kit.WHITE if index in (2, 4) else kit.NAVY
        kit.text(slide, x + 0.12, 1.45, width - 0.24, 0.35, f"Bước {index + 1}", size=12,
                 bold=True, color=kit.YELLOW if index in (2, 4) else kit.BLUE)
        kit.text(slide, x + 0.12, 1.8, width - 0.24, 0.92, step, size=13, color=color)
        if index < 4:
            kit.arrow(slide, x + width + 0.04, 1.93, w=0.34)
    data = kit.TableData(["Nhóm", "Ứng viên (×3 = gộp 3 lần chạy)"], [
        ["a – e", "Từ v1/v2: a = gộp nhánh C của v1 · b = 1 lần chạy v2 · c = v2×3 · d = C-v2×3 "
                  "· e = B-v2×3 + C-v2×3"],
        ["f1 – f4", "Mô hình nền 40 ms: f1 = T2a×3 · f2 = T2b×3 (hệ cuối) · f3 = T2a×3 + B-v2×3 · "
                    "f4 = T2b×3 + B-v2×3"],
        ["g1, g2", "Focal loss: g1 = T2b focal×3 · g2 = g1 + f2"],
    ], [False, True, False], "")
    kit.text(slide, 0.5, 2.95, 7.4, 0.35, "11 ứng viên", size=15, bold=True, color=kit.NAVY)
    kit.table(slide, data, 0.5, 3.35, 7.4, widths=[1.0, 6.4], size=12, row_h=0.55)
    kit.text(slide, 0.5, 5.9, 7.4, 0.95, "Luật chọn: **event-F1 micro cao nhất**, tính trung bình "
             "trên 5 phần của dev. Chênh nhỏ hơn độ dao động thì chỉ nói “được chọn”, không nói "
             "“tốt hơn”.", size=13)
    kit.card(slide, 8.15, 2.95, 4.68, 3.9, "Cùng lúc chọn cách ghép sự kiện", [
        "**Ngưỡng chung**: xác suất vượt ngưỡng thì coi là có sự kiện",
        "**cSEBB**: lấy biên ở chỗ xác suất tăng hoặc giảm mạnh nhất",
        "**Ngưỡng riêng từng loại** bị loại: 21 ngưỡng “học thuộc” dev, sang test tụt 39–48%",
    ], size=13)
    kit.notes(slide, """
(1,5 phút) Đây là phần quan trọng để chống gian lận: luật chọn và danh sách 11 ứng viên được ghi
vào tài liệu (ADR-0031) trước khi có số; lựa chọn f2 được commit lên git trước khi tạo dự đoán
test.
Sau đó chấm test đúng một lần cho tất cả và báo hết, kể cả khi ứng viên khác có điểm test cao
hơn.
Mỗi ứng viên cũng chọn luôn cách ghép xác suất thành sự kiện; ngưỡng riêng từng loại bị loại vì
quá khớp dev (bằng chứng ở ablation A2 trên cả ba nhánh).""")


def kb5(deck: Deck) -> None:
    slide = deck.content(4, "KB5 (RQ2): cùng một danh sách sự kiện, bốn cách viết mô tả")
    kit.frame_row(slide, [
        ("Câu hỏi", "Ép câu mô tả bám danh sách sự kiện thì giảm bịa bao nhiêu, mất gì?"),
        ("Cách làm", "Cùng một danh sách sự kiện, cùng mô hình ngôn ngữ Qwen3.5-9B chạy trên máy."),
        ("So sánh", "4 cách viết, ở 2 mức: danh sách đúng (oracle) và danh sách máy đoán "
                    "(đầu–cuối)."),
        ("Đo bằng", "Tỷ lệ bịa nguồn âm, bỏ sót, thêm bối cảnh, gọi tên quá cụ thể, từ cấm."),
    ], h=1.05, size=12)
    kit.box(slide, 0.5, 2.48, 12.33, 0.42, fill=kit.SOFT, line=None, rounded=True)
    kit.text(slide, 0.65, 2.48, 12.1, 0.42, "Danh sách sự kiện máy đoán cho S-0009:  máy bay phản "
             "lực 0,3–10,0 s  ·  chim 10,0–29,2 s  ·  chim 90,0–108,8 s", size=13, bold=True,
             color=kit.NAVY, anchor=MSO_ANCHOR.MIDDLE)
    data = kit.TableData(["Cách viết", "Câu sinh ra (thật, mức đầu–cuối)", "Đặc điểm"], [
        ["Template", "Có thể nghe thấy tiếng máy bay phản lực từ 0,3 đến 10,0 giây. Có thể nghe "
                     "thấy tiếng chim từ 10,0 đến 29,2 giây. …", "Điền khuôn, không thể bịa; "
                                                               "demo đang dùng"],
        ["Unconstrained", "A brief jet aircraft roar fades into a peaceful chorus of birds "
                          "singing in the forest.", "Viết tự do → tự thêm bối cảnh "
                                                        "“in the forest”"],
        ["Constrained", "The sound of jet aircrafts can be heard from 0.3 to 10.0 seconds, "
                        "followed by the sound of birds from 10.0 to 29.2 seconds and …",
         "Bị “ngữ pháp” ép: chỉ liệt kê sự kiện có thật, đúng tên, đúng giây"],
        ["Constrained-cover", "(giống câu trên ở ví dụ này)", "Thêm điều kiện: phải nhắc đủ "
                                                             "mọi loại âm"],
    ], [True, False, False, False], "")
    kit.table(slide, data, 0.5, 3.0, 12.33, widths=[1.7, 6.6, 4.0], size=12, row_h=0.53)
    rules = [("G1", "Nguồn âm được nhắc phải có trong danh sách"),
             ("G2", "Mỗi lần nhắc chỉ ra được sự kiện làm bằng chứng"),
             ("G3", "Cấm từ về nguyên nhân, ý định, nguy hiểm")]
    width = (12.33 - 0.3) / 3
    for index, (code, rule) in enumerate(rules):
        x = 0.5 + index * (width + 0.15)
        kit.box(slide, x, 6.3, width, 0.56, fill=kit.WHITE, rounded=True)
        kit.badge(slide, x + 0.1, 6.36, code, size=0.44, fill=kit.YELLOW, font=12)
        kit.text(slide, x + 0.65, 6.3, width - 0.75, 0.56, rule, size=12,
                 anchor=MSO_ANCHOR.MIDDLE)
    kit.source_note(slide, 0.5, 5.98, 12.33, "ml/runs/sed_ensemble_s13_f2_20260929T045053Z/"
                    "captions/*_dev.jsonl (bản ghi dev S-0009); câu template là bản tiếng Việt.")
    kit.notes(slide, f"""
(1,5 phút) Cùng một danh sách sự kiện máy đoán cho S-0009, bốn cách viết cho ra bốn câu.
Câu viết tự do nghe tự nhiên nhưng tự thêm "in the forest" — đó là kiểu lỗi chính của mô hình
ngôn ngữ.
Cách constrained dùng một "ngữ pháp" sinh riêng cho từng bản ghi: mô hình chỉ được chọn từ tên
nguồn âm
và số giây có trong danh sách. Nó chỉ còn quyền chọn nhắc sự kiện nào và dừng ở đâu, nên có thể
bỏ sót;
bản cover chặn lỗi bỏ sót. Ba luật G1–G3 có kiểm thử tự động. Kết quả ở slide
{RESULT_PAGES['rq2']}.""")


def kb6(deck: Deck) -> None:
    slide = deck.content(4, "KB6 (RQ3): ba cách tìm, đo trên 100 câu hỏi mẫu")
    kit.frame_row(slide, [
        ("Câu hỏi", "Tìm lại sự kiện: lọc cứng, tìm theo nghĩa, hay kết hợp?"),
        ("Cách làm", "100 câu hỏi mẫu, 4 nhóm; đáp án đúng tính từ nhãn gốc, viết trước khi xem "
                     "kết quả."),
        ("So sánh", "3 cách tìm × 2 kho sự kiện (dự đoán nhánh B và dự đoán f2) × tiếng Anh/Việt."),
        ("Đo bằng", "nDCG@10, độ đúng bộ lọc, tỷ lệ khẳng định thiếu bằng chứng."),
    ], h=1.05, size=12)
    flow = [
        ("Câu hỏi", "“Có tiếng người nói trước tiếng động cơ xe chạy không tải không?”"),
        ("Bộ lọc (mô hình ngôn ngữ đổi ra)", "điều kiện: trước · A = tiếng người nói · "
                                            "B = xe chạy không tải"),
        ("Câu trả lời", "“…tiếng người nói ở 18,2–19,4 giây, sau đó tiếng động cơ xe chạy không "
                        "tải ở 119,5–130,7 giây.” (kèm mã bản ghi)"),
    ]
    y = 2.5
    for index, (head, body) in enumerate(flow):
        kit.card(slide, 0.5, y, 6.0, 1.05, head, [body], size=13, bullets=False,
                 accent=[kit.NAVY, kit.BLUE, kit.GREEN][index], head_size=12.5)
        y += 1.18
    kit.text(slide, 0.5, 6.05, 6.0, 0.8, "Ví dụ thật từ lượt chạy demo 03/10. Bộ lọc hiện trên "
             "giao diện dưới dạng thẻ để người dùng sửa.", size=11.5, color=kit.GRAY,
             italic=True)
    modes = [("Chỉ lọc (structured_only)", "Giữ đúng bản ghi thỏa mọi điều kiện, xếp theo thời "
              "điểm.", kit.NAVY),
             ("Chỉ theo nghĩa (vector_only)", "Tìm bản ghi có mô tả “na ná” câu hỏi, không xét "
              "điều kiện.", kit.BLUE),
             ("Kết hợp (hybrid) — demo dùng", "Lọc trước, rồi xếp hạng theo nghĩa trong tập đã "
              "lọc.", kit.GREEN)]
    y = 2.5
    for head, body, color in modes:
        kit.card(slide, 6.75, y, 6.08, 0.98, head, [body], accent=color, size=13, bullets=False,
                 head_size=13)
        y += 1.08
    kit.card(slide, 6.75, 5.75, 6.08, 1.1, "4 điều kiện thời gian", [
        "trước · sau · chồng nhau · nằm trong (viết 1 lần SQL + 1 lần Python, kiểm khớp nhau)",
    ], size=12.5, bullets=False)
    kit.notes(slide, f"""
(1 phút) Ví dụ bên trái lấy từ lượt chạy demo thật: câu hỏi tiếng Việt được mô hình ngôn ngữ đổi
thành bộ lọc có điều kiện "trước", rồi hệ thống tìm và trả lời kèm thời điểm.
Ba cách tìm khác nhau ở chỗ có lọc cứng hay không. nDCG@10 thưởng cho việc đặt đáp án đúng ở vị
trí cao
trong 10 kết quả đầu. Kết quả ở slide {RESULT_PAGES['rq3']}.""")
