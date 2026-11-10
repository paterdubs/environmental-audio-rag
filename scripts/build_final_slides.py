# ruff: noqa: E501  (nội dung slide: câu tiếng Việt dài, ngắt dòng không có lợi)
"""Dựng slide bảo vệ khóa luận (`report/slide_bao_ve.pptx`) từ template IUH.

Bảng đọc từ `report/final_tables/` (sinh từ `final_numbers`) và `docs/thesis/tables`; hình đọc
từ `report/final_figures`, `report/figures`, `docs/demo_screenshots`. Không chạy suy luận hay
đánh giá nào. Kịch bản lời nói (ghi chú người nói) in ra `report/slide/kich_ban_bao_ve.md`.

    .venv/Scripts/python.exe -m scripts.build_final_slides
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from scripts.midterm_slides import deck as deck_module
from scripts.midterm_slides import kit
from scripts.midterm_slides.deck import Deck

ROOT = kit.ROOT
OUTPUT = ROOT / "report" / "slide_bao_ve.pptx"
SCRIPT = ROOT / "report" / "slide" / "kich_ban_bao_ve.md"
FOOTER = "Khóa luận tốt nghiệp · Phạm Hoàng Phát – Thân Trọng Tính · KHDL18A"
SECTIONS = {
    1: "Đề tài và hệ thống",
    2: "Dữ liệu và cách đánh giá",
    3: "Phát hiện sự kiện (SED)",
    4: "Mô tả và truy hồi",
    5: "Kết luận",
}
MAIN_TOTAL = 19
FINAL_TABLES = "report/final_tables"
FIGURES = ROOT / "report" / "figures"
FINAL_FIGURES = ROOT / "report" / "final_figures"
SHOTS = ROOT / "docs" / "demo_screenshots"


def subset(data: kit.TableData, keep: list[int], header: list[str] | None = None) -> kit.TableData:
    """Giữ các cột theo chỉ số (0 = cột đầu)."""
    return kit.TableData(
        header=header or [data.header[i] for i in keep],
        rows=[[row[i] for i in keep] for row in data.rows],
        used=data.used,
        source=data.source,
    )


def mark_used(data: kit.TableData, first_cell: str) -> kit.TableData:
    return kit.TableData(
        data.header, data.rows, [row[0].startswith(first_cell) for row in data.rows], data.source
    )


def table_source(name: str) -> kit.TableData:
    data = kit.load_table(f"{FINAL_TABLES}/{name}")
    note = (ROOT / FINAL_TABLES / name).read_text(encoding="utf-8")
    source = note.split("**Nguồn:**")[-1].strip().rstrip(".").replace("`", "")
    return kit.TableData(data.header, data.rows, data.used, source)


# ---------------------------------------------------------------- bìa
def cover(deck: Deck) -> None:
    slide = deck.pres.slides[0]
    deck.count += 1
    for shape in list(slide.shapes):
        if shape.name not in {"Image 0", "Title card"}:
            shape._element.getparent().remove(shape._element)
    kit.box(slide, 0.86, 2.0, 2.6, 0.42, fill=kit.NAVY, line=None, rounded=True)
    kit.text(slide, 0.86, 2.0, 2.6, 0.42, "BẢO VỆ KHÓA LUẬN", size=14, bold=True,
             color=kit.WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    kit.text(slide, 3.6, 2.0, 4.2, 0.42, "Khoa học dữ liệu · IUH", size=13, bold=True,
             color=kit.GRAY, anchor=MSO_ANCHOR.MIDDLE)
    kit.text(slide, 0.86, 2.6, 6.55, 1.6,
             "Xây dựng hệ thống phát hiện, sinh mô tả và truy vấn sự kiện âm thanh môi "
             "trường dựa trên RAG", size=24, bold=True, color=kit.NAVY)
    kit.text(slide, 0.86, 4.2, 6.55, 0.6,
             "Grounded Environmental Sound Event Detection, Captioning, and RAG-based "
             "Retrieval", size=13, italic=True, color=kit.GRAY)
    kit.box(slide, 0.86, 4.92, 6.55, 0.02, fill=kit.LINE, line=None)
    kit.text(slide, 0.86, 5.08, 6.55, 1.6, [
        [kit.Run("Phạm Hoàng Phát – 22703861", bold=True, color=kit.NAVY)],
        [kit.Run("Thân Trọng Tính – 22665711", bold=True, color=kit.NAVY)],
        [kit.Run("GVHD: ", color=kit.GRAY), kit.Run("TS. Huỳnh Công Bằng", bold=True,
                                                    color=kit.NAVY)],
        [kit.Run("Lớp KHDL18A · Tháng 11/2026", color=kit.GRAY)],
    ], size=15, space=3)
    kit.notes(slide, """
Mở đầu (30 giây). Chào quý thầy cô, nhóm em là Phát và Tính, trình bày khóa luận "Xây dựng hệ
thống phát hiện, sinh mô tả và truy vấn sự kiện âm thanh môi trường dựa trên RAG". Bài có năm
phần: đề tài và hệ thống; dữ liệu và cách đánh giá; phát hiện sự kiện; mô tả và truy hồi; kết luận.""")


# ---------------------------------------------------------------- phần 1
def problem(deck: Deck) -> None:
    slide = deck.content(1, "Từ bản ghi âm đến câu trả lời có bằng chứng")
    kit.frame_row(slide, [
        ("Phát hiện", "Bản ghi dài → danh sách sự kiện: lớp, bắt đầu, kết thúc, độ tin cậy; các sự "
                      "kiện được phép chồng nhau"),
        ("Mô tả", "Câu văn **chỉ được viết từ danh sách sự kiện**; máy kiểm được mọi nguồn âm "
                  "nhắc đến có trong danh sách"),
        ("Truy hồi", "Hỏi về lịch sử bản ghi (kể cả \"A trước B\"); trả lời kèm bản ghi và "
                     "khoảng thời gian làm bằng chứng"),
        ("Đo", "Event-F1, PSDS; ảo giác, bỏ sót; nDCG@10, khẳng định thiếu bằng chứng"),
    ], y=1.45, h=1.55, size=13)
    kit.card(slide, 0.5, 3.3, 6.0, 3.3, "Vì sao khó", [
        "Nhiều nguồn âm vang cùng lúc (đa âm)",
        "Nhãn có thời gian chính xác ít và tốn công",
        "Mô hình ngôn ngữ dễ viết điều không có trong dữ liệu (ảo giác)",
        "Hai bộ dữ liệu cùng nhóm tác giả có thể chứa **cùng bản ghi gốc**",
    ], size=14)
    kit.card(slide, 6.83, 3.3, 6.0, 3.3, "Phạm vi", [
        "Giám sát âm thanh môi trường, xử lý theo lô",
        "21 lớp đa âm (DataSED), 22 lớp phân loại (DataSEC)",
        "Không suy ra tội phạm, ý định, khẩn cấp hay mức nguy hiểm",
        "Mô tả chỉ nói về **nguồn âm quan sát được**",
    ], size=14, accent=kit.GREEN)
    kit.notes(slide, """
(1 phút) Hệ thống nhận một bản ghi âm môi trường dài và trả về ba thứ nối tiếp: danh sách sự kiện có
thời gian, một đoạn mô tả chỉ được viết từ danh sách đó, và câu trả lời có bằng chứng cho câu hỏi
về lịch sử. Nhóm đo từng mắt xích riêng. Đề tài không suy ra ý định hay mức nguy hiểm: "phát hiện
kính vỡ lúc 5,4 giây" hợp lệ, "phát hiện đột nhập" thì không.""")


def questions(deck: Deck) -> None:
    slide = deck.content(1, "Ba câu hỏi nghiên cứu và bốn đóng góp")
    kit.card(slide, 0.5, 1.4, 6.1, 5.3, "Câu hỏi nghiên cứu", [
        "**RQ1** Huấn luyện thêm trên DataSEC có giúp SED hơn chỉ dùng AudioSet không? "
        "(so nhánh C với B)",
        "**RQ2** Bắt mô tả bám sát danh sách sự kiện giảm ảo giác bao nhiêu so với viết tự do?",
        "**RQ3** Lọc cứng kết hợp xếp hạng ngữ nghĩa so với chỉ lọc hoặc chỉ ngữ nghĩa thì sao?",
    ], size=14)
    kit.card(slide, 6.83, 1.4, 6.0, 5.3, "Đóng góp và mức khẳng định", [
        "**C1** Bộ sinh mô tả có ràng buộc, máy kiểm tra được",
        "**C2** Chỉ số bám sát theo dòng thời gian — áp dụng và mở rộng (đã có ECHO, TAC)",
        "**C3** Đo chuyển giao có kiểm soát trùng lặp — áp dụng vào cặp DataSEC–DataSED",
        "**C4** Điều kiện thời gian giữa hai sự kiện bằng SQL — đóng góp kỹ thuật (đã có LA-RAG)",
        "Không dùng chữ \"lần đầu\": tra văn liệu 11/2026 thấy công trình gần cho cả ba",
    ], size=13, accent=kit.GREEN)
    kit.notes(slide, """
(1,5 phút) Ba câu hỏi và bốn đóng góp. Điểm cần nói thẳng: sau khi tra văn liệu tháng 11, nhóm thấy
đã có công trình gần với C2, C3, C4 — ECHO và TAC đo ảo giác của mô tả âm thanh, Weck và Serra kiểm
tra trùng trong một bộ dữ liệu, LA-RAG dựng event store SQL kèm RAG. Vì vậy nhóm trình bày là áp
dụng và mở rộng, không phải lần đầu. Phạm vi tra là mức khóa luận, không phải tổng quan hệ thống.""")


def system(deck: Deck) -> None:
    slide = deck.content(1, "Hệ thống: bước ghép sự kiện nằm ở dịch vụ suy luận, không ở mô hình")
    kit.picture(slide, FINAL_FIGURES / "f02_architecture.png", 0.5, 1.3, 8.0, 5.4)
    kit.card(slide, 8.75, 1.35, 4.08, 5.3, "Điểm thiết kế", [
        "Ngưỡng và tham số ghép chọn trên dev, lưu cạnh checkpoint",
        "PostgreSQL + pgvector: lọc, điều kiện thời gian và xếp hạng vector trong một câu SQL",
        "Mô tả chỉ nhận danh sách sự kiện, không nhận âm thanh",
        "Hợp đồng JSON Schema giữa các thành phần; API không nạp PyTorch",
    ], size=13)
    kit.notes(slide, """
(1 phút) Bản ghi đi qua dịch vụ suy luận thành danh sách sự kiện; danh sách dùng hai hướng: sinh
mô tả và lưu kho để truy hồi. Ranh giới quan trọng: ngưỡng và tham số ghép là kết quả hiệu chuẩn trên
dev, nên đổi điểm vận hành mà không huấn luyện lại. Đây cũng là chỗ LBR gắn vào, ở phần SED.""")


# ---------------------------------------------------------------- phần 2
def data(deck: Deck) -> None:
    slide = deck.content(2, "Dữ liệu: hai bộ cùng nhóm tác giả, có chung bản ghi gốc")
    kit.stat(slide, 0.5, 1.4, 2.95, 1.6, "5.048", "đoạn DataSEC (23,7 giờ), 22 lớp gộp + 28 lớp con",
             value_size=30)
    kit.stat(slide, 3.62, 1.4, 2.95, 1.6, "717", "bản ghi DataSED (18,7 giờ), 21 lớp đa âm",
             value_size=30)
    kit.stat(slide, 6.74, 1.4, 2.95, 1.6, "3", "nhóm trùng xuyên bộ dữ liệu (2 cặp similarity "
             "1,000000)", value_size=30, color=kit.RED)
    kit.stat(slide, 9.86, 1.4, 2.97, 1.6, "11", "đoạn DataSEC bị loại = 0,22%, dải `minor`",
             value_size=30, color=kit.GREEN)
    kit.card(slide, 0.5, 3.3, 6.1, 3.35, "Quy trình", [
        "D0–D2: kiểm tệp nén, kiểm kê, chuẩn hóa nhãn",
        "D3: dấu vân âm thanh ba tầng; 35 cặp mơ hồ do người duyệt",
        "D4: năm kiểm tra rò rỉ, đã chứng minh không đạt rỗng",
        "Tập chia khóa bằng mã băm: DataSED 438/137/142",
    ], size=13)
    kit.card(slide, 6.83, 3.3, 6.0, 3.35, "Nhìn thẳng", [
        "Bài mô tả dataset không báo baseline nào; chưa thấy số SED của bên khác",
        "Collar 0,2 s chặt hơn độ chính xác của nhãn (8 cặp gán đôi: 67/94 biên trong collar)",
        "14 bản ghi `wind_turbine` thiếu nhãn đa âm: dev/test chấm trên bản ghi có nhãn (139)",
    ], size=13, accent=kit.WARN_TEXT)
    kit.notes(slide, """
(1,5 phút) Hai bộ dữ liệu cùng sáu tác giả, cùng miền, công bố cách nhau bốn tháng, nên nhóm giả định
chúng có thể chung bản ghi gốc cho tới khi đo được. Kiểm tra bằng dấu vân âm thanh tìm ra ba nhóm
trùng; có hai cặp giống nhau hoàn toàn trên 35 và 13 giây. Sau khi người duyệt tay 35 cặp mơ hồ,
11 đoạn DataSEC (0,22%) bị loại trước khi huấn luyện. Từ đó mọi phép đo chuyển giao nằm trong điều
kiện rò rỉ đã được kiểm soát.""")


def evaluation(deck: Deck) -> None:
    slide = deck.content(2, "Cách đánh giá: chọn trước, mở test đúng một lần")
    kit.card(slide, 0.5, 1.4, 4.0, 5.3, "Chọn ở đâu", [
        "Ngưỡng, checkpoint, cấu hình chọn trên **dev** hoặc **dự đoán ngoài mẫu** (OOF 564 bản ghi)",
        "Luật chọn ghi vào ADR **trước** khi có số",
        "Lựa chọn commit vào git trước khi sinh dự đoán test",
    ], size=13)
    kit.card(slide, 4.67, 1.4, 4.0, 5.3, "Đo thế nào", [
        "Event-F1 collar 0,2 s (`sed_eval`), PSDS (`psds_eval`)",
        "Bootstrap theo bản ghi; hiệu ghép cặp",
        "Chênh lệch có CI chồng lấp hoặc nhỏ hơn độ lệch chuẩn giữa fold/seed **không** gọi là cải thiện",
    ], size=13, accent=kit.GREEN)
    kit.card(slide, 8.83, 1.4, 4.0, 5.3, "Minh bạch", [
        "Sổ ghi mọi lần chạm test: 42 lượt đánh giá SED, 10 lượt có cờ `dirty` (công khai)",
        "Đóng băng artifact: 129 run, SHA-256, không thiếu tệp",
        "Ba bộ kiểm tài liệu đối chiếu số ↔ artifact",
    ], size=13, accent=kit.WARN_TEXT)
    kit.notes(slide, """
(1 phút) Quy tắc cứng: không tinh chỉnh trên test. Mọi lựa chọn làm trên dev hoặc trên dự đoán
ngoài mẫu, luật chọn ghi trước, và test mở đúng một lần cho cấu hình đã khóa. Nhóm công khai cả
những chỗ sai lệch: 10 trong 42 lượt đánh giá SED có cờ dirty do chính script sinh ra tệp báo cáo
chưa commit; mã và cấu hình không đổi.""")


# ---------------------------------------------------------------- phần 3
def rq1(deck: Deck) -> None:
    slide = deck.content(3, "RQ1: học thêm trên DataSEC không giúp SED tốt hơn", key="rq1")
    data = table_source("f03_rq1.md")
    kit.table(slide, data, 0.5, 1.4, 12.33, widths=[1.2, 2.4, 2.4, 2.6, 2.6], size=13,
              row_h=0.5, header=["Công thức", "B (AudioSet): micro ± sd (n)",
                                 "C (+DataSEC): micro ± sd (n)", "C − B (bootstrap)",
                                 "Welch p: event-F1 / PSDS-1 / PSDS-2"])
    kit.source_note(slide, 0.5, 2.95, 12.33, data)
    kit.callouts(slide, 0.5, 3.45, 12.33, 3.2, [
        "Hiệu C − B có khoảng tin cậy **chứa 0** ở cả hai công thức: v1 −0,0071 [−0,0164; +0,0021], "
        "v2 −0,0029 [−0,0254; +0,0199]",
        "Tiền huấn luyện nói chung giúp rõ: nhánh A (từ đầu) event-F1 0,036 so với B 0,062 (v1)",
    ], [
        "DataSEC vô ích nói chung — PSDS-2 của v2 tăng +0,028 (p = 0,019, chưa hiệu chỉnh so sánh bội)",
        "Kết quả âm tính được giữ nguyên; trọng tâm chuyển sang C1, C2, C4",
    ], size=13, split=0.6, horizontal=True)
    kit.notes(slide, """
(1,5 phút) Kết quả âm tính. Với cả hai công thức huấn luyện và nhiều seed, nhánh C không hơn nhánh B
về event-F1: hiệu C − B có khoảng tin cậy chứa 0. Đừng hiểu là DataSEC vô ích: PSDS-2 của công thức
v2 có tăng, nhưng chưa hiệu chỉnh so sánh bội. Nhóm giữ nguyên kết quả âm tính và chuyển trọng tâm
sang mô tả bám sự kiện và hỏi đáp thời gian.""")


def diagnosis(deck: Deck) -> None:
    slide = deck.content(3, "Chẩn đoán: lỗi nằm ở biên sự kiện và bỏ sót, không ở nhận dạng lớp")
    kit.stat(slide, 0.5, 1.4, 3.0, 1.7, "0,6294", "trần event-F1 khi mô hình nén thời gian 64 lần "
             "(khối 0,64 s), dù nhận dạng hoàn hảo", value_size=28)
    kit.stat(slide, 3.7, 1.4, 3.0, 1.7, "0,2325 / 0,4975", "event-F1 chỉ xét thời điểm bắt đầu / "
             "chỉ xét kết thúc (v1, dev)", value_size=22)
    kit.stat(slide, 6.9, 1.4, 3.0, 1.7, "112 / 417 / 357", "trong 886 sự kiện: khớp collar / đúng "
             "lớp nhưng lệch biên / bỏ sót", value_size=22, color=kit.RED)
    kit.stat(slide, 10.1, 1.4, 2.73, 1.7, "×3", "event-F1 tăng khi nới collar bắt đầu 0,2 → 1 s "
             "(B: 0,062 → 0,185)", value_size=28, color=kit.GREEN)
    kit.card(slide, 0.5, 3.4, 12.33, 3.25, "Từ chẩn đoán đến thay đổi", [
        "v2: nén thời gian 8 lần, BiGRU, 30 epoch, tăng cường dữ liệu → độ phân giải là thứ duy nhất phân "
        "biệt được (bỏ đi: −0,084 event-F1)",
        "Track 2: bộ mã hóa theo khung 40 ms (BEATs đóng băng, Frame-MobileNet tinh chỉnh) → hệ f2",
        "Giả thuyết \"xác suất bão hòa\" đã được đo và **bác bỏ**: biên tản rộng và đối xứng",
    ], size=14)
    kit.notes(slide, """
(1,5 phút) Event-F1 của bản đầu rất thấp nên nhóm chẩn đoán trước khi cải tiến. Số đo trên dev: ngay cả
mô hình nhận dạng hoàn hảo nhưng quyết định theo khối 0,64 giây cũng chỉ tối đa 0,63; chỉ xét thời điểm
bắt đầu thì 0,23; trong 886 sự kiện, 357 bị bỏ sót và 417 đúng lớp nhưng lệch biên. Lỗi nằm ở biên và
bỏ sót, không phải nhận dạng. Đây là số dev in-sample dùng để chẩn đoán.""")


def phase_o(deck: Deck) -> None:
    slide = deck.content(3, "Chọn bằng dự đoán ngoài mẫu: hệ B0, và vì sao không tin dev")
    kit.card(slide, 0.5, 1.4, 6.1, 5.3, "Vì sao đổi cách chọn", [
        "Dev chỉ 134 bản ghi: **ba ứng viên qua sàng lọc trên dev đều đảo chiều** khi đo ngoài mẫu",
        "Tầng C: 5 fold trên 564 bản ghi (train ∪ dev); mỗi bản ghi do mô hình chưa thấy nó dự đoán",
        "B0 = T2b + bỏ bản ghi thiếu nhãn + 5 mô hình theo fold + suy luận chồng lấn bước 5 s + cSEBB",
        "Giai đoạn P (thêm seed, chưng cất, cửa sổ 20 s, gain/EQ): **không hướng nào vượt B0**",
    ], size=13)
    kit.card(slide, 6.83, 1.4, 6.0, 3.0, "Số đo", [
        "B0 ngoài mẫu: micro 0,2342, macro 0,1797",
        "B0 test: macro 0,1366, micro 0,1806 [0,1261; 0,2384]",
        "B0 − f2 micro: +0,0164 [−0,0128; +0,0495]",
    ], size=14, accent=kit.GREEN)
    kit.card(slide, 6.83, 4.6, 6.0, 2.1, "Không có nghĩa là", [
        "B0 tốt hơn f2 có ý nghĩa — khoảng tin cậy chứa 0",
        "P4: qua sàng lọc dev (0,2402), ngoài mẫu −0,0082 [−0,0258; +0,0088]",
    ], size=12.5, accent=kit.WARN_TEXT, fill=kit.WARN_FILL, line=kit.WARN_FILL)
    kit.notes(slide, """
(1,5 phút) Sau vòng chọn đầu, nhóm thấy xếp hạng trên 134 bản ghi dev không đáng tin: ba ứng viên
đều đảo chiều khi chạy dự đoán ngoài mẫu trên 564 bản ghi. Hệ B0 được chọn theo luật ghi trước. Trên
test, B0 hơn f2 không đáng kể về thống kê. Giai đoạn P thử thêm bốn hướng, không hướng nào vượt B0,
và test không được mở trong giai đoạn này.""")


def lbr(deck: Deck) -> None:
    slide = deck.content(3, "LBR: học sửa biên và chấm lại hộp sự kiện")
    kit.card(slide, 0.5, 1.4, 6.1, 5.3, "Chẩn đoán dẫn tới LBR", [
        "Trên dự đoán ngoài mẫu của B0: **hơn nửa số sự kiện bị bỏ sót có xác suất khung ≥ 0,9** nhưng "
        "hộp cSEBB bị loại",
        "Thời điểm bắt đầu dự đoán **sớm có hệ thống**",
        "→ nút thắt ở biên hộp sau hậu xử lý, không ở nhận dạng",
    ], size=14)
    kit.card(slide, 6.83, 1.4, 6.0, 2.6, "LBR gồm hai mô hình", [
        "**Bộ tinh chỉnh**: dịch bắt đầu/kết thúc của từng hộp",
        "**Bộ chấm lại**: ước lượng xác suất hộp đúng",
        "HistGradientBoosting, học lồng nhau 5 fold (không thấy fold nó chấm)",
    ], size=13, accent=kit.GREEN)
    kit.card(slide, 6.83, 4.15, 6.0, 2.55, "Hai biến thể", [
        "**V2** (số chính): nhãn khớp collar, điểm f1; ngoài mẫu 0,2342 → 0,3332 (+0,0990)",
        "**V3** (demo): nhãn giao nhau, điểm `recall_first` (precision ≥ 0,6), ghi trước test",
    ], size=13, accent=kit.WARN_TEXT)
    kit.notes(slide, """
(1,5 phút) Từ chẩn đoán lỗi, nhóm đề xuất LBR: hai mô hình boosting học trên xác suất ngoài mẫu. Bộ
tinh chỉnh dịch biên của hộp, bộ chấm lại ước lượng hộp có đúng không. Học lồng nhau để mô hình không
thấy fold nó chấm. V2 tối ưu khớp biên chặt; V3 tối ưu ít bỏ sót, dùng cho demo. Cấu hình V3 được ghi
trước khi mở test.""")


def sed_result(deck: Deck) -> None:
    slide = deck.content(3, "Kết quả SED trên test: LBR V2 tăng event-F1 micro khoảng 1,6 lần",
                         key="sed")
    data = table_source("f01_sed.md")
    shown = subset(data, [0, 1, 2, 3, 4], ["Hệ thống", "Macro", "Micro [CI 95%]",
                                           "Δ micro so B0", "Nsys/Nref"])
    shown = mark_used(shown, "LBR V2")
    kit.table(slide, shown, 0.5, 1.4, 12.33, widths=[2.4, 1.0, 2.6, 2.8, 1.3], size=13,
              row_h=0.42)
    kit.source_note(slide, 0.5, 4.0, 12.33, data)
    kit.callouts(slide, 0.5, 4.4, 12.33, 2.4, [
        "V2: micro 0,2965, Δ so B0 **+0,1159 [+0,0741; +0,1593]** — CI không chứa 0",
        "V3 recall_first: recall giao nhau **0,8203**, precision 0,7812, dự đoán 668/740 sự kiện",
    ], [
        "V2 hơn B0 ở mọi mặt — recall giao nhau 0,5108 < B0 0,5351; segment-F1 0,5965 < 0,7260; "
        "PSDS-2 thấp hơn (slide sau)",
        "Test 139 bản ghi; chưa kiểm trên bộ dữ liệu khác",
    ], size=12.5, split=0.55, horizontal=True)
    kit.notes(slide, """
(2 phút) Trên test có nhãn, 139 bản ghi, mở một lần cho cấu hình đã khóa. LBR V2 đạt micro 0,2965 và
macro 0,2356; hiệu so với B0 là +0,116, khoảng tin cậy không chứa 0. Cái giá: độ phủ giảm — recall giao
nhau và segment-F1 của V2 thấp hơn B0. Vì vậy V3 ở điểm recall_first được dùng cho demo: phát hiện được
khoảng 82% sự kiện tham chiếu ở mức chồng lấn với precision 0,78, event-F1 micro 0,2287. Hai điểm vận
hành cho hai mục đích.""")


def psds(deck: Deck) -> None:
    slide = deck.content(3, "PSDS phụ thuộc lưới ngưỡng; PSDS-2 của LBR thấp hơn B0")
    kit.stat(slide, 0.5, 1.4, 3.0, 1.55, "0,3061 / 0,7452", "B0, lưới log (PSDS-1 / PSDS-2)",
             value_size=22)
    kit.stat(slide, 3.7, 1.4, 3.0, 1.55, "0,3512 / 0,6116", "LBR V2, lưới log", value_size=22,
             color=kit.BLUE)
    kit.stat(slide, 6.9, 1.4, 3.0, 1.55, "0,3369 / 0,6167", "LBR V3, lưới log", value_size=22,
             color=kit.BLUE)
    kit.stat(slide, 10.1, 1.4, 2.73, 1.55, "0,2146 / 0,2960", "V2 trên lưới tuyến tính cũ — cắt "
             "phần lớn hộp", value_size=18, color=kit.RED)
    data = table_source("f06_psds.md")
    kit.table(slide, data, 0.5, 3.25, 6.3, widths=[3.6, 1.7], size=12, row_h=0.4,
              header=["Chẩn đoán S21 (dev annotated, v1 → v2)", "Giá trị"])
    kit.source_note(slide, 0.5, 6.1, 6.3, data)
    kit.callouts(slide, 7.0, 3.25, 5.83, 3.4, [
        "Event-F1 tăng +0,0534 nhưng PSDS-2 giảm −0,0078: **tái hiện** hiện tượng ở test",
        "Lưới log đổi dấu hiệu PSDS-2 (+0,0095); `alpha_st = 0` đưa về −0,0010",
    ], [
        "Phép đo in-sample, hiệu nhỏ, không có CI: chỉ là **gợi ý** (lưới và độ lệch giữa lớp)",
        "So PSDS giữa hai lưới khác nhau",
    ], size=12, split=0.62)
    kit.notes(slide, """
(1,5 phút) PSDS lấy từ đường PSD-ROC trên một tập ngưỡng, nên phụ thuộc lưới. Lưới tuyến tính mặc định
cắt phần lớn hộp của LBR; nhóm ghi trước lưới log và đo B0 trên cùng lưới. LBR có PSDS-1 cao hơn
nhưng PSDS-2 thấp hơn B0 rõ rệt, nhất quán với việc đổi độ phủ lấy độ chính xác. Chẩn đoán trên dev cho
hiện tượng v1 sang v2: lưới và độ lệch giữa các lớp giải thích phần lớn, nhưng đây chỉ là gợi ý.""")


# ---------------------------------------------------------------- phần 4
def rq2(deck: Deck) -> None:
    slide = deck.content(4, "RQ2: ràng buộc ngữ pháp loại ảo giác ở cả bốn hệ SED", key="rq2")
    data = table_source("f04_rq2.md")
    kit.table(slide, data, 0.5, 1.4, 12.33, widths=[2.8, 2.4, 2.4, 2.4, 2.4], size=11.5,
              row_h=0.36, header=["Chế độ — chỉ số", "f2", "B0", "LBR V2", "LBR V3"])
    kit.source_note(slide, 0.5, 4.95, 12.33, data)
    kit.callouts(slide, 0.5, 5.3, 12.33, 1.55, [
        "Template = 0; constrained và cover: ảo giác, bối cảnh, gọi tên quá mức, từ cấm = **0**; "
        "unconstrained: bối cảnh 0,26–0,40",
        "Cover bỏ sót = 0 ở mọi hệ",
    ], [
        "Mô tả \"không ảo giác\" là đúng với âm thanh — nó chỉ trung thành với **dự đoán** của SED",
    ], size=12, split=0.6, horizontal=True)
    kit.notes(slide, """
(2 phút) Bốn cách sinh trên cùng danh sách sự kiện của từng hệ SED, mức đầu–cuối, 139 bản ghi. Template
cho 0 ở mọi chỉ số — kiểm chứng bộ đo. Viết tự do hiếm khi bịa nguồn âm nhưng hay thêm bối cảnh
không có trong bằng chứng, 26 đến 40% số mô tả. Ngữ pháp giải mã đưa ảo giác, bối cảnh, gọi tên quá
mức và từ cấm về 0 ở cả bốn hệ. Cần nhớ: danh sách sự kiện là dự đoán của SED, nên 0 ảo giác không
có nghĩa mô tả đúng với âm thanh.""")


def rq2_cost(deck: Deck) -> None:
    slide = deck.content(4, "RQ2: cái giá là bỏ sót khi danh sách dày — và các giới hạn của bộ đo")
    kit.stat(slide, 0.5, 1.4, 3.0, 1.6, "0,081", "bỏ sót của constrained với LBR V3 (f2: 0,012)",
             value_size=30, color=kit.RED)
    kit.stat(slide, 3.7, 1.4, 3.0, 1.6, "+0,069", "V3 − f2: [+0,041; +0,097]", value_size=30)
    kit.stat(slide, 6.9, 1.4, 3.0, 1.6, "668", "sự kiện trên 139 bản ghi — danh sách của V3 dày",
             value_size=30)
    kit.stat(slide, 10.1, 1.4, 2.73, 1.6, "0", "bỏ sót của constrained-cover ở mọi hệ",
             value_size=30, color=kit.GREEN)
    kit.card(slide, 0.5, 3.3, 6.1, 3.4, "Đọc kết quả", [
        "Constrained chỉ nhắc một dãy con sự kiện → bỏ sót lớp khi danh sách dài (giải thích khớp số "
        "liệu, chưa kiểm bằng thí nghiệm kiểm soát)",
        "Cover: bắt buộc nhắc sự kiện đầu của mỗi lớp → bỏ sót bằng 0 theo cấu tạo",
        "Mức oracle: constrained bỏ sót 0,094 so với 0,019 của unconstrained",
    ], size=13)
    kit.card(slide, 6.83, 3.4 - 0.1, 6.0, 3.4, "Giới hạn", [
        "Bộ đo dựa trên từ điển: so với **một** người đọc trên 60 mô tả, precision 0,896, recall 0,936",
        "Llama.cpp hết bộ nhớ GPU một lần khi sinh V3 trên dev; chạy tiếp, tệp sau điểm này không chắc "
        "tái tạo từng ký tự",
        "Không so trực tiếp với TAC/ECHO",
    ], size=13, accent=kit.WARN_TEXT, fill=kit.WARN_FILL, line=kit.WARN_FILL)
    kit.notes(slide, """
(1,5 phút) Ràng buộc có giá. Với V3, danh sách có 668 sự kiện, constrained chỉ nhắc một dãy con nên
bỏ sót 8,1% lớp, so với 1,2% ở f2; hiệu +0,069 khoảng tin cậy không chứa 0. Nhánh cover giải quyết
bằng cấu tạo. Giới hạn: bộ đo dựa trên từ điển, đối chiếu một người đọc trên 60 mô tả; và một lần
llama.cpp hết bộ nhớ GPU khi sinh V3 trên dev, nhóm khởi động lại và chạy tiếp — đã ghi trong ADR.""")


def rq3(deck: Deck) -> None:
    slide = deck.content(4, "RQ3: lọc cứng đúng tuyệt đối; xếp hạng bị chặn bởi SED dự đoán gì",
                         key="rq3")
    data = table_source("f05_rq3.md")
    kit.table(slide, data, 0.5, 1.4, 12.33, widths=[1.0, 2.2, 2.2, 2.2, 1.1, 1.6, 1.3], size=12,
              row_h=0.46, header=["Kho", "structured", "vector", "hybrid", "Có trả lời",
                                  "Khẳng định thiếu bằng chứng", "Trích đúng GT"])
    kit.source_note(slide, 0.5, 3.85, 12.33, data)
    kit.callouts(slide, 0.5, 4.25, 12.33, 2.55, [
        "f2, B0, V2: CI chồng lấn (hybrid 0,415; 0,383; 0,404) dù V2 tăng event-F1 ×1,6",
        "V3: hybrid 0,670, trả lời 95/97 — **hiệu ứng độ phủ**; khẳng định thiếu bằng chứng = 0,000 ở mọi kho",
    ], [
        "V3 xếp hạng tốt hơn — trích đúng GT giảm 0,915 → 0,712 (nhiều kết quả hơn, kém liên quan hơn)",
        "Bộ lọc gold là cận trên; parsed thấp hơn 0,006–0,015",
    ], size=12.5, split=0.55, horizontal=True)
    kit.notes(slide, """
(2 phút) Bốn kho sự kiện, cùng bộ 100 truy vấn, 97 câu có kết quả liên quan. Lọc cứng luôn đúng điều kiện.
f2, B0 và V2 không phân biệt được, dù V2 tăng event-F1 micro khoảng 1,6 lần: truy hồi bị chặn bởi việc SED
dự đoán những sự kiện nào. V3 cao hẳn vì độ phủ: trả lời được 95 trên 97 câu, nhưng tỷ lệ trích dẫn
đúng giảm từ 0,915 xuống 0,712. Vì vậy mức tăng nDCG không phải xếp hạng tốt hơn. Không câu trả lời nào
chứa khẳng định thiếu bằng chứng.""")


def demo(deck: Deck) -> None:
    slide = deck.content(4, "Demo chạy trên máy cá nhân với LBR V3, không cần Internet")
    kit.picture(slide, SHOTS / "04-rag-evidence.png", 0.5, 1.35, 7.7, 5.1)
    kit.card(slide, 8.45, 1.35, 4.38, 2.85, "Người dùng làm được gì", [
        "Tải file lên → dòng thời gian, bấm sự kiện để nghe đúng đoạn",
        "Mô tả tiếng Anh và tiếng Việt kèm bằng chứng",
        "Hỏi bằng câu tự nhiên; bộ lọc hiện thành thẻ, sửa được",
        "Bấm trích dẫn → mở đúng bản ghi, đúng giây",
    ], size=13)
    kit.stat(slide, 8.45, 4.35, 2.12, 1.45, "3,7 s", "tải lên + phân tích 1 bản ghi", value_size=26,
             size=11.5)
    kit.stat(slide, 10.71, 4.35, 2.12, 1.45, "0,27 s", "trả lời 1 câu hỏi", value_size=26,
             size=11.5)
    kit.text(slide, 8.45, 5.9, 4.38, 0.95, "Parity với đầu ra đóng băng: 573/692 sự kiện trùng khít, "
             "665 lệch ≤ 1 khung, 691 trong collar. Một lượt, không phải đo hiệu năng.",
             size=11.5, color=kit.GRAY, italic=True)
    kit.source_note(slide, 0.5, 6.55, 7.7, "docs/demo_screenshots; demo_lbrv3_e2e_20261110; "
                    "inference_parity LBR V3.")
    kit.notes(slide, """
(1 phút) Demo chạy bằng Docker: cơ sở dữ liệu, dịch vụ suy luận, giao diện; mặc định phục vụ LBR V3.
Nếu cần chạy trực tiếp: scripts/demo_up.ps1 rồi mở http://127.0.0.1:8088. Lịch sử demo chỉ gồm bản ghi
tập train. Nếu live lỗi: dùng ảnh fallback hoặc bộ lọc thủ công.""")


# ---------------------------------------------------------------- phần 5
def limits(deck: Deck) -> None:
    slide = deck.content(5, "Hạn chế: những gì khóa luận không khẳng định")
    kit.card(slide, 0.5, 1.4, 6.1, 5.3, "Về số đo", [
        "Test chỉ 139 bản ghi → CI rộng; bootstrap không phản ánh dao động giữa seed",
        "Huấn luyện SED không tất định cùng seed",
        "PSDS phụ thuộc lưới; PSDS lưới log của f2 thiếu (trần bộ nhớ)",
        "Bộ đo mô tả dựa từ điển, một người đọc, 60 mô tả",
        "10/42 lượt đánh giá SED có cờ `dirty` (công khai)",
    ], size=13)
    kit.card(slide, 6.83, 1.4, 6.0, 5.3, "Về phạm vi", [
        "Không \"lần đầu\": đã có ECHO, TAC, Weck & Serra, LA-RAG",
        "Tra văn liệu ở mức khóa luận, không phải tổng quan hệ thống",
        "DataSEC bản 3 (bản 4 sửa số tệp lớp Music); trùng nguồn với AudioSet không định lượng được",
        "Chưa có baseline công bố trên DataSED",
        "Chưa có xác thực người dùng → chưa triển khai công khai",
    ], size=13, accent=kit.WARN_TEXT, fill=kit.WARN_FILL, line=kit.WARN_FILL)
    kit.notes(slide, """
(1 phút) Nhóm nêu thẳng các hạn chế: tập test nhỏ; huấn luyện không tất định; PSDS phụ thuộc lưới;
bộ đo mô tả dựa từ điển; một số lượt đánh giá có cờ dirty; tra văn liệu mức khóa luận nên không
dùng chữ lần đầu; và ứng dụng chưa có xác thực.""")


def conclusion(deck: Deck) -> None:
    slide = deck.content(5, "Kết luận và hướng phát triển")
    kit.card(slide, 0.5, 1.4, 6.1, 5.3, "Đã làm được", [
        "Quy trình tái lập: dữ liệu có nguồn gốc, tập chia khóa, test một lần",
        "SED: B0 + LBR, event-F1 micro 0,1806 → 0,2965 (Δ +0,1159)",
        "Mô tả có ràng buộc: 0 ảo giác nguồn âm, bối cảnh, gọi tên quá mức; cover bỏ sót 0",
        "Truy hồi có điều kiện thời gian giữa hai sự kiện; 0 khẳng định thiếu bằng chứng",
        "RQ1 âm tính được giữ nguyên",
    ], size=13.5)
    kit.card(slide, 6.83, 1.4, 6.0, 5.3, "Hướng phát triển", [
        "Chạy lại RQ1 với DataSEC bản 4; thêm nhãn lớp con cho một tập con DataSED",
        "Kiểm LBR trên bộ dữ liệu khác; huấn luyện chung nhãn mạnh/yếu; soundscape tổng hợp",
        "Đánh giá mô tả: nhiều người đọc, thêm chỉ số phía âm thanh (FLAM)",
        "Hỗ trợ câu hỏi tổng quát về bản ghi; so sánh trực tiếp với hệ event store + RAG khác",
        "Xác thực, luồng liên tục, đo hiệu năng có thống kê",
    ], size=13.5, accent=kit.GREEN)
    kit.notes(slide, """
(1,5 phút) Tóm lại: nhóm có một quy trình tái lập đi từ dữ liệu đến câu trả lời có bằng chứng. Điểm
tiến bộ lớn nhất của SED là LBR; mô tả có ràng buộc loại ảo giác nguồn âm theo cấu tạo; truy hồi bị chặn
bởi những sự kiện SED dự đoán. Kết quả âm tính của RQ1 được giữ nguyên. Hướng tiếp theo ở bên phải.
Xin cảm ơn quý thầy cô, nhóm sẵn sàng trả lời câu hỏi.""")


def closing(deck: Deck) -> None:
    slide = deck.dark()
    kit.text(slide, 0.9, 2.6, 11.5, 1.2, "Xin cảm ơn quý thầy cô", size=40, bold=True,
             color=kit.WHITE)
    kit.text(slide, 0.9, 3.9, 11.5, 0.8, "Phạm Hoàng Phát · Thân Trọng Tính · GVHD: TS. Huỳnh Công Bằng",
             size=18, color=kit.WHITE)
    kit.text(slide, 0.9, 4.7, 11.5, 0.6, "Hỏi đáp · Phụ lục ở các trang sau", size=16,
             color=kit.YELLOW)
    kit.notes(slide, "Chuyển sang hỏi đáp. Phụ lục: kết quả theo lớp, sổ ghi test, bộ phân tích câu hỏi.")


# ---------------------------------------------------------------- phụ lục
def appendix(deck: Deck) -> None:
    slide = deck.appendix_slide("Event-F1 theo lớp của B0 và LBR V2 (test annotated)")
    data = table_source("f09_per_class.md")
    kit.table(slide, data, 0.5, 1.3, 12.33, widths=[3.2, 1.3, 1.2, 1.2, 1.5, 1.4], size=9.5,
              row_h=0.235, header=["Lớp", "Sự kiện tham chiếu", "B0 F1", "V2 F1", "V2 precision",
                                   "V2 recall"])
    kit.source_note(slide, 0.5, 6.65, 12.33, "evaluation_phase_o/lbr_annotated.json của run sed_ensemble_B0_final_test_20261014T085016Z; nhãn gốc DataSED.")
    kit.notes(slide, "Lớp dưới 10 mẫu chỉ báo số khớp tuyệt đối. 3 lớp V2 F1 bằng 0: birds, "
              "vehicle_idling, vehicle_pass_by.")

    slide = deck.appendix_slide("Sổ ghi mọi lần chạm test")
    data = table_source("f07_ledger.md")
    kit.table(slide, data, 0.5, 1.4, 7.5, widths=[5, 1.5], size=13, row_h=0.42,
              header=["Nhóm", "Số mục"])
    kit.source_note(slide, 0.5, 5.85, 7.5, data)
    kit.card(slide, 8.3, 1.4, 4.53, 3.2, "Ghi chú", [
        "10/42 lượt SED có cờ `dirty`: tệp báo cáo chưa commit do script sinh ra",
        "Mã và cấu hình không đổi; test không chạy lại",
    ], size=13, accent=kit.WARN_TEXT)
    kit.notes(slide, "Sổ sinh tự động từ các tệp kết quả đã khóa (test_ledger_20261111).")

    slide = deck.appendix_slide("Bộ phân tích câu hỏi: hợp lược đồ 240/240, lỗi ở điều kiện thời gian")
    data = kit.load_table("docs/thesis/tables/10_parser_l2.md", "cols=1,2,3,4,5,6,7")
    kit.table(slide, data, 0.5, 1.4, 12.33, size=11, row_h=0.4)
    kit.source_note(slide, 0.5, 4.6, 12.33, data)
    kit.notes(slide, "Độ đúng ngữ nghĩa hoàn toàn 0,855 (template) và 0,925 (diễn đạt lại); lỗi chủ "
              "yếu đảo vai trò a/b, nhầm within/overlaps.")


SLIDES = [
    problem, questions, system, data, evaluation, rq1, diagnosis, phase_o, lbr, sed_result, psds,
    rq2, rq2_cost, rq3, demo, limits, conclusion,
]


def build(output: Path) -> Deck:
    deck = deck_module.open_template(FOOTER)
    deck.total = MAIN_TOTAL
    deck.sections = dict(SECTIONS)
    cover(deck)
    for make in SLIDES:
        make(deck)
    closing(deck)
    if deck.count != MAIN_TOTAL:
        raise RuntimeError(f"Có {deck.count} slide chính, footer ghi {MAIN_TOTAL}")
    appendix(deck)
    deck_module.save(deck, output)
    return deck


def write_script(pptx: Path, output: Path) -> None:
    from pptx import Presentation

    lines = ["# Kịch bản bảo vệ khóa luận", "",
             "> Sinh tự động bởi `scripts.build_final_slides` từ `report/slide_bao_ve.pptx`; sửa "
             "nội dung trong `scripts/build_final_slides.py`, không sửa tay tệp này.", ""]
    for index, slide in enumerate(Presentation(str(pptx)).slides, start=1):
        title = next((s.text_frame.text for s in slide.shapes
                      if s.has_text_frame and s.name == "Title"), "")
        note = slide.notes_slide.notes_text_frame.text if slide.has_notes_slide else ""
        lines += [f"## Slide {index}. {title}".rstrip(". "), "", note or "(không có ghi chú)", ""]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--script-output", type=Path, default=SCRIPT)
    args = parser.parse_args()
    deck = build(args.output)
    write_script(args.output, args.script_output)
    print(f"Đã ghi {args.output}: {deck.count} slide chính, {deck.appendix} phụ lục")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
