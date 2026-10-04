"""Slide 27–29 (tiến độ, kế hoạch, hỏi đáp) và các slide phụ lục."""

from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR

from scripts.midterm_slides import kit
from scripts.midterm_slides.deck import Deck
from scripts.midterm_slides.part_c import SEARCH_NAMES

CH7 = "report/src/07_tien_do_ke_hoach.md"


def schedule(deck: Deck) -> None:
    slide = deck.content(6, "Tiến độ: phần kỹ thuật đi trước lịch, kỷ luật đánh giá giữ nguyên")
    data = kit.source_table(CH7, "schedule")
    status = data.header.index("Trạng thái")
    data.used = [row[status] != "Đã kiểm chứng" for row in data.rows]
    kit.table(slide, data, 0.5, 1.4, 12.33, widths=[4.2, 2.3, 3.8, 2.0], size=12, row_h=0.4)
    kit.source_note(slide, 0.5, 6.0, 12.33, data.source)
    kit.text(slide, 0.5, 6.3, 12.33, 0.6, "Nền xám: việc chưa xong. Ba hạng mục phát sinh ngoài kế "
             "hoạch, đều do số đo chỉ ra: cải tiến SED, tập đánh giá annotated, bộ đổi câu hỏi "
             "ra bộ lọc.", size=13, color=kit.GRAY)
    kit.notes(slide, """
(45 giây) Phần kỹ thuật đã xong sớm hơn lịch vì các việc độc lập được làm song song và thí
nghiệm dài
chạy theo hàng đợi ngoài giờ. Mốc khóa mô hình dự kiến 18/10 được làm sớm vào 29/09, nhưng luật
chọn
vẫn ghi trước và lựa chọn vẫn commit trước khi mở test. Còn lại: viết báo cáo cuối và slide bảo
vệ.""")


def next_plan(deck: Deck) -> None:
    slide = deck.content(6, "Kế hoạch đến hạn nộp 09/11: làm rõ kết quả, không mở rộng phạm vi")
    data = kit.source_table(CH7, "nextplan")
    kit.table(slide, data, 0.5, 1.4, 12.33, widths=[1.5, 7.0, 3.83], size=12, row_h=0.47)
    kit.source_note(slide, 0.5, 5.5, 12.33, data.source)
    kit.box(slide, 0.5, 5.85, 12.33, 1.0, fill=kit.WARN_FILL, line=None, rounded=True)
    kit.text(slide, 0.72, 5.85, 11.9, 1.0, "Nguyên tắc: **không** chạy thêm đánh giá trên test cho "
             "hệ đã khóa; mọi phân tích bổ sung (vì sao PSDS không tăng, tương quan lỗi giữa các "
             "mô hình) **chỉ làm trên dev**.", size=13.5, anchor=MSO_ANCHOR.MIDDLE)
    kit.notes(slide, """
(45 giây) Ưu tiên: nhận góp ý của thầy, tổng quan văn liệu có hệ thống để kiểm tra tính mới,
giải thích vì sao PSDS không tăng (chỉ trên dev), rồi viết báo cáo cuối.
Nhóm xin thầy góp ý về phạm vi và cách trình bày kết quả âm tính.""")


def questions(deck: Deck) -> None:
    slide = deck.dark()
    kit.text(slide, 0.9, 2.2, 11.5, 1.3, "Hỏi đáp", size=54, bold=True, color=kit.WHITE)
    kit.box(slide, 0.95, 3.55, 1.2, 0.08, fill=kit.YELLOW, line=None)
    kit.text(slide, 0.9, 3.85, 11.5, 0.6, "Cảm ơn thầy đã lắng nghe. Nhóm xin nhận câu hỏi và "
             "góp ý.", size=20, color=kit.WHITE)
    kit.text(slide, 0.9, 4.6, 11.5, 0.5,
             "Phạm Hoàng Phát – 22703861 · Thân Trọng Tính – 22665711 · "
             "GVHD: TS. Huỳnh Công Bằng", size=14, color="C9D6E6")
    kit.text(slide, 0.9, 6.6, 11.5, 0.4, "Phụ lục phía sau: bảng đầy đủ và từ điển thuật ngữ",
             size=12, color="C9D6E6", italic=True)
    kit.notes(slide, """
Câu hỏi có thể gặp:
- "Event-F1 0,16 có quá thấp?" → DCASE 2016 (ghi âm đời thực) chỉ 4,7–6,3%, chỉ để định cỡ;
  người với người chỉ khớp 0,58; lỗi chủ yếu là biên và bỏ sót.
- "Sao không chọn f1 khi test cao hơn?" → chọn theo test là học thuộc đề; khoảng tin cậy chồng
nhau.
- "RQ1 âm tính thì DataSEC vô ích?" → chỉ kết luận về event-F1; PSDS-2 ở v2 có tăng (p = 0,019).
- "Sao kết hợp lại kém chỉ lọc?" → tài liệu dạng khuôn, xếp theo nghĩa trong tập đã lọc không
giúp (−0,042).
- "Không bịa có nghĩa là đúng?" → không, chỉ đúng với danh sách máy đoán (slide 23).
- "Có tự gán nhãn thêm không?" → không sửa nhãn gốc; 14 bản ghi thiếu nhãn xử lý bằng tập
annotated.""")


def _two_tables(slide, data: kit.TableData, header, widths, *, size=11.5, row_h=0.4, relabel=None):
    half = (len(data.rows) + 1) // 2
    for index, (rows, used) in enumerate([(data.rows[:half], data.used[:half]),
                                          (data.rows[half:], data.used[half:])]):
        part = kit.TableData(data.header, rows, used, data.source)
        kit.table(slide, part, 0.5 + index * 6.3, 1.4, 6.03, widths=widths, size=size,
                  row_h=row_h, header=header, relabel=relabel)


def appendix(deck: Deck) -> None:
    slide = deck.appendix_slide("Phụ lục 1 — Đầy đủ 11 ứng viên: kiểm chứng chéo dev và test")
    data = kit.load_table("docs/thesis/tables/06_s13_ranking_test.md",
                          "|best=5+,7+,8+|used=2:^f2$")
    kit.table(slide, data, 0.5, 1.4, 12.33, widths=[0.9, 0.6, 0.8, 1.1, 1.0, 1.0, 1.1, 1.1, 1.9],
              size=12, row_h=0.38, header=["Hạng dev", "Mã", "Số mô hình", "Cách ghép",
                                           "Dev micro", "Dao động", "Test macro", "Test micro",
                                           "KTC 95% test micro"],
              relabel={"csebb": "cSEBB", "theta": "ngưỡng chung"})
    kit.legend_note(slide, 0.5, 6.05, 12.33)
    kit.source_note(slide, 0.5, 6.35, 12.33, data)

    slide = deck.appendix_slide("Phụ lục 2 — RQ3 đầy đủ: bộ lọc chuẩn (gold) và bộ lọc máy "
                                "đổi (parsed)")
    data = kit.load_table("docs/thesis/tables/09_rq3_retrieval.md",
                          "|cols=1,2,4,5,6,7,8,9|group=1|best=4+,9+|used=1:^f2 — gold$&2:^hybrid")
    kit.table(slide, data, 0.5, 1.35, 12.33, widths=[2.0, 2.2, 1.0, 1.6, 0.9, 0.9, 0.9, 1.2],
              size=10.5, row_h=0.268, header=["Kho / bộ lọc", "Cách tìm", "nDCG@10", "KTC 95%",
                                               "R@1", "R@5", "R@10", "Đúng bộ lọc"],
              relabel=SEARCH_NAMES)
    kit.source_note(slide, 0.5, 6.5, 12.33, data)

    slide = deck.appendix_slide("Phụ lục 3 — RQ2 ở mức đầu–cuối: hệ v1 so với hệ f2 (test)")
    data = kit.load_table("docs/thesis/tables/08_rq2_caption.md")
    kit.table(slide, data, 0.5, 1.4, 12.33, widths=[1.6, 2.0, 0.6, 1.4, 1.9, 1.2, 1.9, 0.8],
              size=11.5, row_h=0.37, header=["Hệ — tập", "Cách viết", "n", "Bịa nguồn âm",
                                             "KTC 95%", "Bỏ sót", "KTC 95%", "G3"])
    kit.source_note(slide, 0.5, 6.35, 12.33, data)

    slide = deck.appendix_slide("Phụ lục 4 — Event-F1 theo từng loại âm của hệ f2 (test annotated)")
    data = kit.load_table("report/tables/m05_f2_per_class.md")
    _two_tables(slide, data, ["Loại âm", "Sự kiện thật", "F1", "Precision", "Recall"],
                [2.9, 0.9, 0.75, 0.8, 0.7], size=11, row_h=0.4)
    kit.source_note(slide, 0.5, 6.35, 12.33, "evaluation_cv_annotated.json của f2; loại có dưới 10 "
                    "sự kiện chỉ báo số đếm")

    slide = deck.appendix_slide("Phụ lục 5 — Bộ phân loại DataSEC theo 22 loại âm gộp (test)")
    data = kit.load_table("report/tables/m02_classifier_per_class.md")
    _two_tables(slide, data, ["Loại âm", "Đúng / tổng", "F1"], [3.6, 1.2, 1.2], size=11,
                row_h=0.4)
    kit.source_note(slide, 0.5, 6.35, 12.33, data)

    slide = deck.appendix_slide("Phụ lục 6 — Ablation v2 (dev) và sổ ghi các lần chạm tập test")
    data = kit.load_table("docs/thesis/tables/05_sed_v2_ablation.md", "|cols=1,2,3,4,5")
    kit.table(slide, data, 0.5, 1.4, 7.4, widths=[1.1, 2.6, 1.2, 1.0, 1.5], size=11.5,
              row_h=0.42, header=["Nhóm", "Cấu hình", "Micro-F1 (dev)", "Dao động",
                                  "Chênh so với v2 lần 1"])
    kit.source_note(slide, 0.5, 4.85, 7.4, data)
    data = kit.load_table("report/tables/m06_test_ledger.md")
    kit.table(slide, data, 8.15, 1.4, 4.68, widths=[3.4, 1.0], size=11.5, row_h=0.42,
              header=["Nhóm lần chạm test", "Số mục"])
    kit.source_note(slide, 8.15, 5.3, 4.68, data)

    _glossary(deck)


GLOSSARY = [
    ("SED", "Phát hiện sự kiện âm thanh: tìm loại âm và thời điểm bắt đầu, kết thúc"),
    ("Event-F1", "Điểm 0–1; sự kiện đúng khi đúng loại và lệch bắt đầu ≤ 0,2 s"),
    ("Precision / Recall", "Trong cái máy báo bao nhiêu đúng / tìm ra bao nhiêu sự kiện thật"),
    ("Micro / Macro", "Gộp mọi sự kiện rồi tính / tính từng loại rồi lấy trung bình"),
    ("PSDS", "Điểm chấm trên mọi mức nhạy (mọi ngưỡng), không chỉ một ngưỡng"),
    ("KTC 95%", "Khoảng tin cậy: điểm thật có thể nằm trong khoảng này"),
    ("Welch t-test", "Kiểm định xem chênh lệch hai nhóm có lớn hơn dao động bình thường"),
    ("Dev / Test", "Tập để thử và chọn / tập thi, chỉ chấm một lần"),
    ("Kiểm chứng chéo 5 phần", "Chia dev làm 5, lần lượt chọn trên 4 phần, chấm phần còn lại"),
    ("annotated", "Tập chấm chỉ gồm bản ghi có nhãn đa âm (dev 134, test 139)"),
    ("Ensemble", "Gộp nhiều mô hình bằng cách lấy trung bình xác suất"),
    ("Seed", "Số khởi tạo ngẫu nhiên; mỗi seed là một lần chạy"),
    ("Ablation", "Bỏ từng thành phần để xem thành phần nào có tác dụng"),
    ("cSEBB", "Cách ghép sự kiện: lấy biên ở chỗ xác suất tăng/giảm mạnh nhất"),
    ("CNN / CRNN / BiGRU", "Mạng tích chập / tích chập + đọc chuỗi / lớp đọc chuỗi hai chiều"),
    ("AudioSet", "Kho âm thanh lớn (527 loại) dùng để học sẵn mô hình"),
    ("Oracle / Đầu–cuối", "Chấm với danh sách sự kiện đúng / với danh sách máy đoán"),
    ("G1 – G3", "Ba luật của câu mô tả: có trong danh sách, có bằng chứng, không từ cấm"),
    ("RAG", "Tra cứu kho dữ liệu trước rồi mới trả lời"),
    ("nDCG@10", "Điểm 0–1: đáp án đúng có nằm ở vị trí cao trong 10 kết quả đầu"),
]


def _glossary(deck: Deck) -> None:
    slide = deck.appendix_slide("Phụ lục 7 — Từ điển thuật ngữ")
    half = len(GLOSSARY) // 2
    for index, chunk in enumerate([GLOSSARY[:half], GLOSSARY[half:]]):
        data = kit.TableData(["Thuật ngữ", "Nghĩa"], [list(item) for item in chunk],
                             [False] * len(chunk), "")
        kit.table(slide, data, 0.5 + index * 6.3, 1.4, 6.03, widths=[1.9, 4.1], size=11.5,
                  row_h=0.5)
