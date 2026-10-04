"""Slide 2–16: giới thiệu, hệ thống, dữ liệu, phương pháp và kịch bản thí nghiệm."""

from __future__ import annotations

import json

from pptx.enum.text import MSO_ANCHOR

from scripts.midterm_slides import kit
from scripts.midterm_slides.deck import Deck
from scripts.midterm_slides.kit import Run

FIG = kit.ROOT / "report" / "figures"
THESIS_FIG = kit.ROOT / "docs" / "thesis" / "figures"
F2_RUN = kit.ROOT / "ml" / "runs" / "sed_ensemble_s13_f2_20260929T045053Z"

# Số slide kết quả mà các slide kịch bản trỏ tới; được kiểm lại sau khi dựng.
RESULT_PAGES = {"rq1": 18, "v2": 19, "s13": 20, "progress": 21, "rq2": 22, "rq2b": 23,
                "rq3": 24, "parser": 25}


def intro(deck: Deck) -> None:
    slide = deck.content(1, "Đề tài: nghe bản ghi dài, ghi lại sự kiện, viết mô tả và trả lời "
                               "câu hỏi")
    kit.card(slide, 0.5, 1.35, 4.1, 2.45, "Vấn đề", [
        "Máy đo tiếng ồn chỉ cho biết **ồn đến mức nào** (dB)",
        "Không cho biết **nguồn nào, lúc nào, kéo dài bao lâu**",
        "Cùng mức ồn nhưng do xe cộ hay công trường thì cách xử lý khác nhau",
    ], size=14)
    kit.card(slide, 0.5, 3.95, 4.1, 2.9, "Ba khó khăn", [
        "**Nhiều âm chồng lên nhau** trong cùng một lúc",
        "**Nhãn có mốc thời gian rất tốn công** làm, nên dữ liệu ít",
        "**Mô hình ngôn ngữ dễ “bịa”** khi viết kết quả thành câu",
    ], accent=kit.WARN_TEXT, size=14)
    steps = [
        ("Bản ghi âm dài", "Bản ghi S-0009 (tập dev), dài 125 giây"),
        ("Danh sách sự kiện", "máy bay phản lực 0,3–10,0 s · chim 10,0–29,2 s · chim 90,0–108,8 s"),
        ("Câu mô tả", "“Có thể nghe thấy tiếng máy bay phản lực từ 0,3 đến 10,0 giây. Có thể nghe "
                      "thấy tiếng chim từ 10,0 đến 29,2 giây. …”"),
        ("Hỏi đáp có bằng chứng", "Hỏi: “Có tiếng người nói trước tiếng động cơ xe chạy không tải "
                                  "không?” → Đáp: tiếng người nói 18,2–19,4 s, sau đó tiếng xe "
                                  "119,5–130,7 s (kèm mã bản ghi)"),
    ]
    y = 1.35
    for index, (head, example) in enumerate(steps, start=1):
        kit.box(slide, 4.85, y, 7.98, 1.18, fill=kit.WHITE, rounded=True)
        kit.badge(slide, 5.02, y + 0.33, str(index), size=0.5, fill=kit.NAVY, color=kit.WHITE,
                  font=16, oval=True)
        kit.text(slide, 5.7, y + 0.1, 6.95, 0.34, head, size=15, bold=True, color=kit.NAVY)
        kit.text(slide, 5.7, y + 0.45, 6.95, 0.72, example, size=13)
        y += 1.3
    kit.source_note(slide, 4.85, 6.55, 7.98, "①–③ bản ghi dev S-0009 (hệ f2, mô tả tiếng Việt "
                    "dạng khuôn); ④ lượt chạy demo 03/10/2026 (demo_script_20261003.json).")
    kit.notes(slide, """
(1 phút) Máy đo tiếng ồn hiện nay chỉ trả về một con số dB. Đề tài muốn máy làm được 4 việc
như cột bên phải: nhận một bản ghi dài, ghi lại sự kiện kèm thời điểm, viết câu mô tả, và trả
lời
câu hỏi về lịch sử có kèm bằng chứng. Ví dụ là bản ghi thật S-0009 trong tập dev.
Ba khó khăn: âm chồng nhau, dữ liệu có mốc thời gian ít, và mô hình ngôn ngữ dễ bịa.""")


def research_questions(deck: Deck) -> None:
    slide = deck.content(1, "Ba câu hỏi nghiên cứu (RQ) và những gì đề tài không làm")
    cards = [
        ("RQ1", "Học thêm có giúp không?",
         "Cho mô hình học trước trên 5.048 đoạn âm ngắn (DataSEC) rồi mới học bài chính, có "
         "phát hiện sự kiện tốt hơn không?", "Hai bộ cùng tác giả → phải kiểm trùng trước khi so.",
         RESULT_PAGES["rq1"]),
        ("RQ2", "Câu mô tả có bịa không?",
         "Nếu ép câu mô tả chỉ được nói những gì có trong danh sách sự kiện, giảm bịa bao nhiêu "
         "và mất gì?", "Đo bằng máy, không cần người viết câu mẫu.", RESULT_PAGES["rq2"]),
        ("RQ3", "Tìm lại sự kiện cách nào tốt?",
         "Lọc đúng điều kiện, tìm theo nghĩa câu hỏi, hay kết hợp cả hai?",
         "Câu hỏi có điều kiện thời gian, ví dụ “A xảy ra trước B”.", RESULT_PAGES["rq3"]),
    ]
    width = (12.33 - 0.3) / 3
    for index, (code, question, detail, why, page) in enumerate(cards):
        x = 0.5 + index * (width + 0.15)
        kit.box(slide, x, 1.35, width, 3.95, fill=kit.WHITE, rounded=True)
        kit.badge(slide, x + 0.2, 1.55, code, size=0.62, fill=kit.NAVY, color=kit.WHITE, font=15)
        kit.text(slide, x + 0.95, 1.5, width - 1.1, 0.75, question, size=17, bold=True,
                 color=kit.NAVY, anchor=MSO_ANCHOR.MIDDLE)
        kit.text(slide, x + 0.2, 2.4, width - 0.4, 1.5, detail, size=14)
        kit.text(slide, x + 0.2, 3.85, width - 0.4, 0.8, why, size=12.5, color=kit.GRAY,
                 italic=True)
        kit.text(slide, x + 0.2, 4.75, width - 0.4, 0.4, f"→ Kết quả: slide {page}", size=12.5,
                 bold=True, color=kit.BLUE)
    kit.box(slide, 0.5, 5.5, 12.33, 1.33, fill=kit.WARN_FILL, line=None, rounded=True)
    kit.text(slide, 0.72, 5.6, 11.9, 0.35, "Không làm (ngoài phạm vi)", size=14, bold=True,
             color=kit.WARN_TEXT)
    kit.text(slide, 0.72, 5.98, 11.9, 0.82, [
        "Nhận dạng nội dung lời nói · Suy ra tội phạm, tai nạn, khẩn cấp · Chấm điểm nguy hiểm · "
        "Xử lý thời gian thực.",
        "Mô tả chỉ nói về **nguồn âm nghe được**: “tiếng kính vỡ lúc 5,4 s” là hợp lệ; “có đột "
        "nhập” thì không.",
    ], size=13.5)
    kit.notes(slide, """
(1 phút) Ba câu hỏi nghiên cứu nói bằng lời thường. RQ1 hỏi việc học thêm có giúp không.
RQ2 hỏi câu mô tả có bịa không. RQ3 hỏi nên tìm kiếm theo cách nào.
Mỗi thẻ ghi luôn slide kết quả tương ứng để thầy dễ đối chiếu.
Ngoài phạm vi: không nghe nội dung lời nói, không suy ra tội phạm hay mức nguy hiểm, vì dữ liệu
không có cơ sở cho các kết luận đó.""")


def system(deck: Deck) -> None:
    slide = deck.content(2, "Hệ thống: 5 bước từ file âm thanh tới câu trả lời có bằng chứng")
    kit.picture(slide, FIG / "m01_architecture.png", 0.5, 1.35, 6.2, 5.45)
    steps = [
        ("Tải bản ghi lên", "Giao diện web nhận file âm thanh (tối đa 600 giây)."),
        ("Phát hiện sự kiện", "Mô hình cho xác suất từng loại âm theo thời gian, rồi ghép thành "
                              "danh sách: loại âm, giây bắt đầu, giây kết thúc."),
        ("Viết mô tả", "Chỉ dựa vào danh sách sự kiện; tiếng Anh để chấm điểm, tiếng Việt để "
                       "hiển thị."),
        ("Lưu vào kho", "PostgreSQL lưu sự kiện có cấu trúc, kèm vector để tìm theo nghĩa."),
        ("Hỏi đáp", "Câu hỏi → bộ lọc → tìm → trả lời kèm mã bản ghi và khoảng thời gian."),
    ]
    y = 1.35
    for index, (head, body) in enumerate(steps, start=1):
        kit.badge(slide, 6.95, y + 0.05, str(index), size=0.42, fill=kit.NAVY, color=kit.WHITE,
                  font=14, oval=True)
        kit.text(slide, 7.5, y, 5.33, 0.32, head, size=15, bold=True, color=kit.NAVY)
        kit.text(slide, 7.5, y + 0.33, 5.33, 0.55, body, size=13)
        y += 0.92
    kit.box(slide, 6.95, 6.0, 5.88, 0.85, fill=kit.READ_FILL, line=None, rounded=True)
    kit.text(slide, 7.12, 6.05, 5.6, 0.75, "Điểm then chốt: bộ viết mô tả **không nghe âm "
             "thanh**, chỉ đọc danh sách sự kiện → không thể tự thêm nguồn âm mới.", size=13.5,
             anchor=MSO_ANCHOR.MIDDLE)
    kit.notes(slide, """
(1 phút) Đi theo hình bên trái từ trên xuống. Bước 2 là mô hình SED; tham số ghép xác suất thành
sự kiện được chọn trên dev và lưu cạnh mô hình, nên đổi độ nhạy không cần huấn luyện lại.
Nhấn mạnh ô xanh: bộ viết mô tả chỉ đọc danh sách sự kiện, đây là cách "khóa" việc bịa nguồn âm.""")


def demo(deck: Deck) -> None:
    slide = deck.content(2, "Demo chạy được trên máy cá nhân, không cần Internet")
    kit.picture(slide, THESIS_FIG / "07_demo_interface.png", 0.5, 1.35, 7.7, 5.1)
    kit.card(slide, 8.45, 1.35, 4.38, 2.85, "Người dùng làm được gì", [
        "Tải file lên → xem dòng thời gian, bấm sự kiện để nghe đúng đoạn",
        "Đọc mô tả tiếng Anh và tiếng Việt kèm bằng chứng",
        "Hỏi bằng câu tự nhiên; bộ lọc hiện thành thẻ, sửa được",
        "Bấm trích dẫn → mở đúng bản ghi, đúng giây",
    ], size=13)
    kit.stat(slide, 8.45, 4.35, 2.12, 1.45, "2,0 s", "phân tích 1 bản ghi bằng CPU",
             value_size=26, size=11.5)
    kit.stat(slide, 10.71, 4.35, 2.12, 1.45, "0,25 s", "trả lời 1 câu hỏi", value_size=26,
             size=11.5)
    kit.text(slide, 8.45, 5.9, 4.38, 0.95, "Số đo của một lượt trên một bản ghi, không phải đo "
             "hiệu năng có thống kê. Lịch sử demo chỉ dùng bản ghi tập train.", size=11.5,
             color=kit.GRAY, italic=True)
    kit.source_note(slide, 0.5, 6.55, 7.7, "docs/demo_screenshots (Playwright); "
                    "demo_f2_e2e_20261002.")
    kit.notes(slide, """
(1 phút) Demo chạy bằng Docker trên máy cá nhân: cơ sở dữ liệu, dịch vụ suy luận và giao diện.
Nếu thầy muốn xem trực tiếp: chạy scripts/demo_up.ps1 rồi mở http://127.0.0.1:8088.
Lịch sử demo chỉ gồm bản ghi tập train để không lộ dữ liệu test.""")


def datasets(deck: Deck) -> None:
    slide = deck.content(3, "Hai bộ dữ liệu cùng nhóm tác giả, bổ trợ cho nhau")
    split = kit.load_table("docs/thesis/tables/01_data_split.md")
    files = {row[0]: (row[2], row[3]) for row in split.rows}
    data = kit.TableData(
        ["Bộ dữ liệu", "Dạng", "Số tệp", "Số giờ", "Nhãn", "Dùng để"],
        [["DataSEC", "Đoạn âm ngắn, rời nhau", *files["DataSEC"],
          "Mỗi đoạn 1 nhãn: 22 loại âm (+28 loại con)", "Học thêm (nhánh C); bài phân loại"],
         ["DataSED", "Bản ghi dài (~94 giây)", *files["DataSED"],
          "4.034 sự kiện có giây bắt đầu/kết thúc; 21 loại âm",
          "Bài thi chính: phát hiện sự kiện"]],
        [False, False], split.source)
    kit.table(slide, data, 0.5, 1.4, 12.33, widths=[1.2, 2.0, 0.9, 0.9, 3.4, 2.6], size=13,
              row_h=0.62)
    kit.source_note(slide, 0.5, 3.3, 12.33, data)
    facts = [
        ("57,5%", "của DataSEC là tiếng nói + nhạc → khi học phải lấy mẫu cân bằng giữa các "
                   "loại âm."),
        ("2 loại gộp", "“còi / chuông báo” và “sấm / pháo / súng” → mô tả phải giữ mơ hồ, không "
                       "được nói “tiếng súng”."),
        ("Đo lại", "mọi con số từ tệp tải về (khớp mã MD5); giấy phép CC-BY-NC-SA 4.0."),
    ]
    width = (12.33 - 0.3) / 3
    for index, (value, label) in enumerate(facts):
        kit.stat(slide, 0.5 + index * (width + 0.15), 3.85, width, 2.0, value, label,
                 value_size=26, size=13.5)
    kit.text(slide, 0.5, 6.05, 12.33, 0.7, "Kết quả trên 21 loại (DataSED) và 22 loại (DataSEC) "
             "không so trực tiếp với nhau: khác tập loại âm và khác cách gán nhãn.", size=13,
             color=kit.GRAY, italic=True)
    kit.notes(slide, """
(1 phút) DataSEC giống bộ thẻ học từ vựng: đoạn ngắn, mỗi đoạn một nhãn.
DataSED giống phim có phụ đề chi tiết: bản ghi dài, đánh dấu từng sự kiện bắt đầu và kết thúc
lúc nào.
DataSED là bài thi chính; DataSEC là tài liệu học thêm cho nhánh C của RQ1.""")


def leakage(deck: Deck) -> None:
    slide = deck.content(3, "Hai bộ có chung bản ghi gốc, nên phải loại trùng trước khi học")
    kit.picture(slide, FIG / "m04_data_pipeline.png", 0.5, 1.35, 6.4, 3.19)
    data = kit.load_table("docs/thesis/tables/02_leakage_d3_d4.md")
    kit.table(slide, data, 0.5, 4.62, 6.4, widths=[0.6, 2.5, 1.2, 2.1], size=11, row_h=0.27,
              header=["Bước", "Kiểm tra", "Kết quả", "Ý nghĩa"], relabel={
                  "Cặp ứng viên T1/T2/T3": "Cặp nghi trùng (tầng 1/2/3)",
                  "Nhóm duplicate": "Nhóm trùng", "Audit 3 tầng": "3 tầng kiểm tra",
                  "Nội bộ và xuyên dataset": "Trong và giữa 2 bộ",
                  "Nhóm xuyên DataSEC–DataSED": "Nhóm trùng giữa 2 bộ",
                  "Đã gom theo leakage group": "Gom chung một nhóm",
                  "Clip pretraining bị loại": "Đoạn học thêm bị loại",
                  "Trùng DataSED dev/test": "Trùng dev/test DataSED",
                  "Cổng DataSEC": "Cổng kiểm tra DataSEC", "Cổng DataSED": "Cổng kiểm tra DataSED",
              })
    kit.source_note(slide, 0.5, 6.62, 6.4, "duplicate_audit.json; *_leakage_report.json")
    kit.card(slide, 7.15, 1.35, 5.68, 2.55, "Phát hiện: có trùng thật", [
        "Đoạn Sirens-0046 (DataSEC) giống **100%** với 35 giây của S-0233 (DataSED, tập dev)",
        "35 cặp đáng ngờ được **nghe tay**: 10 trùng, 1 không chắc, 24 khác",
        "→ Loại **11 đoạn DataSEC (0,22%)** khỏi dữ liệu học thêm",
    ], size=13)
    kit.card(slide, 7.15, 4.05, 5.68, 1.5, "Tìm trùng 3 tầng", [
        "Giống từng byte · giống sau khi đổi định dạng · nghe giống nhau (so “vân tay âm "
        "thanh”, ngưỡng đặt bằng thực nghiệm)",
    ], size=13)
    kit.card(slide, 7.15, 5.7, 5.68, 1.15, "Vì sao quan trọng", [
        "Không loại thì nhánh C được “xem trước đề thi” → RQ1 mất ý nghĩa.",
    ], accent=kit.WARN_TEXT, fill=kit.WARN_FILL, line=kit.WARN_FILL, size=13)
    kit.notes(slide, """
(1,5 phút) Hai bộ dữ liệu cùng sáu tác giả nên nhóm giả định có trùng cho tới khi đo được điều
ngược lại.
Quy trình D0–D4 trong hình: kiểm tệp tải → kiểm kê → chuẩn hóa nhãn → tìm trùng → chia tập.
Tìm trùng ba tầng; tầng 3 so "vân tay âm thanh" (MFCC). Ngưỡng được hiệu chuẩn: cặp trùng thật
đạt
1,0000, cặp khác nhau cao nhất 0,9205, nên chọn ngưỡng 0,95.
Câu hỏi có thể gặp: "Loại 11 đoạn có đủ chưa?" → còn một rủi ro không đo được: hai bộ lấy một
phần âm
thanh từ AudioSet, mà mô hình nền cũng học AudioSet; nhóm ghi rõ đây là hạn chế.""")


def split_rules(deck: Deck) -> None:
    slide = deck.content(3, "Chia dữ liệu theo nhóm trùng và khóa lại trước khi huấn luyện")
    parts = [("Train", "438 bản ghi · học mô hình", kit.NAVY, 438),
             ("Dev", "137 · thử và chọn", kit.BLUE, 137),
             ("Test", "142 · thi một lần", kit.GREEN, 142)]
    total = sum(part[3] for part in parts)
    x = 0.5
    for label, detail, color, count in parts:
        width = 12.33 * count / total
        kit.box(slide, x, 1.4, width - 0.04, 1.0, fill=color, line=None)
        kit.text(slide, x + 0.15, 1.45, width - 0.3, 0.9, [
            [Run(label, bold=True, color=kit.WHITE)],
            [Run(detail, color=kit.WHITE)]], size=14, anchor=MSO_ANCHOR.MIDDLE)
        x += width
    kit.text(slide, 0.5, 2.45, 12.33, 0.3, "DataSED, tỷ lệ 60 / 20 / 20 theo bản ghi; DataSEC "
             "chia 70 / 15 / 15.", size=11.5, color=kit.GRAY, italic=True)
    split = kit.load_table("docs/thesis/tables/01_data_split.md", "|cols=1,5,6,7,8")
    kit.table(slide, split, 0.5, 2.95, 5.6, header=["Bộ", "Train", "Dev", "Test",
                                                    "Số nhóm trùng"], size=13, row_h=0.42)
    kit.source_note(slide, 0.5, 4.25, 5.6, "data/splits/*.frozen.json")
    kit.card(slide, 0.5, 4.7, 5.6, 2.15, "Quy tắc chia", [
        "Các tệp trùng nhau luôn nằm **cùng một phần**",
        "Mỗi phần đều có đủ 21 loại âm",
        "Khóa bằng mã băm SHA-256: sửa tệp chia thì bước kiểm tra từ chối chạy",
    ], size=13)
    kit.card(slide, 6.35, 2.95, 6.48, 1.85, "14 bản ghi thiếu nhãn", [
        "14 bản ghi `wind_turbine` không có nhãn sự kiện đa âm → chấm vào sẽ bị tính sai oan",
        "→ Chấm trên tập **annotated**: dev 134, test 139 bản ghi",
    ], accent=kit.WARN_TEXT, size=13)
    kit.card(slide, 6.35, 4.95, 6.48, 1.9, "Nhãn của người cũng không tuyệt đối", [
        "8 bản ghi bị gán nhãn hai lần: hai lần chỉ khớp nhau **0,58** (event-F1)",
        "→ Không nên kỳ vọng máy đạt gần 1,0",
    ], size=13)
    kit.notes(slide, """
(1 phút) Train để học, dev để thử và chọn, test là bài thi thật chỉ làm một lần.
Không chia theo từng tệp mà theo nhóm trùng, để hai bản giống nhau không rơi vào hai phần khác
nhau.
Hai phát hiện phụ: 14 bản ghi thiếu nhãn (xử lý bằng tập annotated), và nhãn của chính con người
chỉ khớp nhau 0,58, nên điểm của máy cần đọc trong bối cảnh này.""")


def rules(deck: Deck) -> None:
    slide = deck.content(4, "Luật chơi: học trên train, chọn trên dev, thi test đúng một lần")
    stages = [
        ("Train", "Học mô hình", ["Suy giới hạn độ dài sự kiện từ đây"], kit.NAVY),
        ("Dev", "Thử và chọn", ["Chọn ngưỡng, cấu hình, ứng viên", "**Luật chọn ghi trước**, "
                                "lựa chọn commit lên git trước khi mở test"], kit.BLUE),
        ("Test", "Thi một lần", ["Chỉ chấm cấu hình đã chọn", "Báo cả kết quả xấu, **không "
                                 "chọn lại** theo điểm test"], kit.GREEN),
    ]
    width = 3.75
    for index, (name, role, items, color) in enumerate(stages):
        x = 0.5 + index * (width + 0.54)
        kit.box(slide, x, 1.4, width, 2.15, fill=kit.WHITE, rounded=True)
        kit.badge(slide, x + 0.18, 1.55, name, size=0.62, fill=color, color=kit.WHITE, font=12)
        kit.text(slide, x + 0.95, 1.55, width - 1.1, 0.62, role, size=16, bold=True, color=color,
                 anchor=MSO_ANCHOR.MIDDLE)
        kit.text(slide, x + 0.18, 2.3, width - 0.36, 1.2, items, size=13, bullets=True)
        if index < 2:
            kit.arrow(slide, x + width + 0.09, 2.32)
    run = json.loads((F2_RUN / "evaluation_cv_annotated.json").read_text(encoding="utf-8"))
    f1 = run["event_based_f1"]
    per_class = kit.load_table("report/tables/m05_f2_per_class.md")
    n_ref = sum(int(row[1]) for row in per_class.rows)
    n_tp = round(f1["recall"] * n_ref)
    n_sys = round(n_tp / f1["precision"])
    kit.text(slide, 0.5, 3.75, 12.33, 0.4, "Cách đọc điểm event-F1 — ví dụ thật của hệ cuối (f2) "
             "trên tập test", size=16, bold=True, color=kit.NAVY)
    stats = [(f"{n_ref}", "sự kiện thật trong tập test"),
             (f"{n_sys}", "sự kiện máy báo ra"),
             (f"{n_tp}", "báo đúng: đúng loại âm, lệch thời điểm bắt đầu ≤ 0,2 s")]
    for index, (value, label) in enumerate(stats):
        kit.stat(slide, 0.5 + index * 2.6, 4.25, 2.45, 1.45, value, label, value_size=26,
                 size=12)
    kit.card(slide, 8.3, 4.25, 4.53, 2.6, "Ba con số", [
        f"**Precision** = {n_tp}/{n_sys} = {vn(f1['precision'])}: trong cái máy báo, bao "
        "nhiêu đúng",
        f"**Recall** = {n_tp}/{n_ref} = {vn(f1['recall'])}: tìm ra bao nhiêu sự kiện thật",
        f"**F1** = {vn(f1['f_measure'])}: cân bằng hai số trên",
    ], size=12.5)
    kit.text(slide, 0.5, 5.85, 7.6, 1.0, [
        "**Micro**: gộp mọi sự kiện rồi tính · **Macro**: tính từng loại âm rồi lấy trung bình",
        "**Khoảng tin cậy 95%** chồng nhau, hoặc chênh nhỏ hơn độ dao động → không gọi là "
        "“tốt hơn”",
    ], size=12.5, bullets=True)
    kit.notes(slide, f"""
(1,5 phút) Đây là luật chơi chống "học thuộc đề", áp dụng cho mọi kịch bản phía sau.
Ví dụ đọc điểm: tập test có {n_ref} sự kiện thật, f2 báo {n_sys}, trong đó {n_tp} đúng.
Precision {vn(f1['precision'])} nghĩa là trong cái máy báo có khoảng 29% đúng; recall
{vn(f1['recall'])}
nghĩa là máy chỉ tìm ra khoảng 11% sự kiện thật. Recall thấp là điểm nghẽn chính của hệ thống.
Các số này tính từ evaluation_cv_annotated.json đã khóa, không chạy lại test.""")


def vn(value: float) -> str:
    return f"{value:.2f}".replace(".", ",")


def scenario_map(deck: Deck) -> None:
    slide = deck.content(4, "Sáu kịch bản thí nghiệm, mỗi kịch bản trả lời một câu hỏi")
    p = RESULT_PAGES
    rows = [
        ["KB1", "Học thêm DataSEC có giúp? (RQ1)", "Nhánh C với nhánh B, nhiều lần chạy",
         "Event-F1, PSDS, khoảng tin cậy", f"{p['rq1']}"],
        ["KB2", "Vì sao v1 kém và sửa thế nào?", "v1 với v2; bỏ từng thành phần của v2",
         "Event-F1 trên dev", f"{p['v2']}"],
        ["KB3", "Mô hình nền “nghe theo từng 40 ms” có tốt hơn?",
         "T2a, T2b, focal loss so với v2", "Event-F1 trên dev", f"{p['s13']}"],
        ["KB4", "Chọn hệ cuối thế nào cho công bằng?", "11 ứng viên, luật viết trước",
         "Event-F1 micro (dev), test 1 lần", f"{p['s13']}–{p['progress']}"],
        ["KB5", "Câu mô tả có bịa không? (RQ2)", "4 cách viết mô tả, 2 mức chấm",
         "Tỷ lệ bịa, bỏ sót, thêm bối cảnh", f"{p['rq2']}–{p['rq2b']}"],
        ["KB6", "Tìm lại sự kiện cách nào tốt? (RQ3)", "3 cách tìm × 2 kho × Anh/Việt",
         "nDCG@10, độ đúng bộ lọc", f"{p['rq3']}–{p['parser']}"],
    ]
    data = kit.TableData(["", "Câu hỏi", "So sánh gì", "Đo bằng gì", "Kết quả (slide)"], rows,
                         [False] * len(rows), "")
    kit.table(slide, data, 0.5, 1.4, 12.33, widths=[0.6, 3.9, 3.4, 2.9, 1.5], size=14,
              row_h=0.66)
    kit.text(slide, 0.5, 6.15, 12.33, 0.7, "Mỗi slide kịch bản dùng cùng một khung 4 ô: **Câu "
             "hỏi → Cách làm → So sánh → Đo bằng**. KB2–KB4 là các bước cải thiện mô hình phát "
             "hiện sự kiện (SED).", size=13.5, color=kit.GRAY)
    kit.notes(slide, """
(1 phút) Bản đồ để thầy theo dõi: sáu kịch bản, mỗi cái trả lời một câu hỏi, cột cuối ghi slide
kết quả.
KB1 là RQ1; KB2–KB4 là chuỗi cải thiện mô hình phát hiện sự kiện; KB5 là RQ2; KB6 là RQ3.""")
