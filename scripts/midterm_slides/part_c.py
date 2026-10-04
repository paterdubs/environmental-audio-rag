"""Slide 17–26: kết quả. Mỗi slide = bảng thật từ báo cáo + 'Đọc kết quả' + 'Không có nghĩa là'."""

from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR

from scripts.midterm_slides import kit
from scripts.midterm_slides.deck import Deck
from scripts.midterm_slides.part_a import FIG

SYSTEM_NAMES = {
    "v1 — ensemble C": "v1 (gộp nhánh C)",
    "v2 — ensemble 3 seed": "v2 (gộp 3 lần chạy)",
    "S13 — T2b×3 + cSEBB (khóa)": "f2: T2b×3 + cSEBB (hệ cuối)",
}
SEARCH_NAMES = {
    "Run B — gold": "Dự đoán nhánh B", "f2 — gold": "Dự đoán f2",
    "Run B — parsed": "Nhánh B (parsed)", "f2 — parsed": "Dự đoán f2 (parsed)",
    "structured_only/en": "Chỉ lọc (EN)", "structured_only/vi": "Chỉ lọc (VI)",
    "vector_only/en": "Chỉ theo nghĩa (EN)", "vector_only/vi": "Chỉ theo nghĩa (VI)",
    "hybrid/en": "Kết hợp (EN)", "hybrid/vi": "Kết hợp (VI)",
}


def classifier(deck: Deck) -> None:
    slide = deck.content(5, "Bộ phân loại DataSEC làm tốt bài dễ: macro-F1 0,85 trên 22 loại âm",
                         key="classifier")
    data = kit.load_table("report/tables/m01_classifier.md")
    kit.table(slide, data, 0.5, 1.4, 7.6, widths=[3.6, 1.2, 2.8], size=13, row_h=0.5,
              header=["Chỉ số (tập test)", "Giá trị", "Ghi chú"], relabel={
                  "ECE trước hiệu chuẩn (T = 1)": "Sai số độ tin cậy (ECE), chưa hiệu chỉnh",
                  "ECE sau temperature scaling (T = 1.5681, chọn trên dev)":
                      "ECE sau hiệu chỉnh nhiệt độ (T = 1,5681, chọn trên dev)",
                  "Tỷ lệ nhất quán cha–con": "Lớp con nằm đúng lớp gộp",
              })
    kit.source_note(slide, 0.5, 4.95, 7.6, data)
    kit.stat(slide, 0.5, 5.35, 3.7, 1.5, "0,8466", "macro-F1 trên 22 loại âm gộp, 740 đoạn test",
             value_size=28)
    kit.stat(slide, 4.4, 5.35, 3.7, 1.5, "0,033 → 0,056", "sai số độ tin cậy **tăng** sau hiệu "
             "chỉnh → báo nguyên kết quả âm tính", value_size=24, color=kit.RED)
    kit.callouts(slide, 8.35, 1.4, 4.48, 5.45, [
        "Bài này dễ hơn phát hiện sự kiện: chỉ đoán loại cho một **đoạn ngắn đã cắt sẵn**",
        "Mô hình này là bước giữa của nhánh C trong RQ1",
    ], [
        "Nhận tốt mọi loại — yếu nhất là `vehicle_idling` 0,62 và `vehicle_pass_by` 0,65",
        "Đánh giá đủ mọi lớp con — lớp ít mẫu (dưới 10 mẫu test) chỉ báo số đếm, ví dụ "
        "`vacuum_cleaner` đúng 0/4 "
        "(Phụ lục)",
    ], size=13, split=0.42)
    kit.notes(slide, """
(1 phút) Bộ phân loại học trên DataSEC đạt macro-F1 0,85 trên 22 loại âm. Đây là bài dễ hơn vì
chỉ
đoán loại cho đoạn ngắn đã cắt sẵn. Có một kết quả âm tính: hiệu chỉnh nhiệt độ làm sai số độ
tin cậy
tăng chứ không giảm, nhóm báo nguyên như vậy. Bảng theo từng loại ở Phụ lục.""")


def rq1(deck: Deck) -> None:
    slide = deck.content(5, "RQ1: học thêm trên DataSEC không giúp tìm sự kiện tốt hơn", key="rq1")
    data = kit.load_table("docs/thesis/tables/03_rq1.md")
    kit.table(slide, data, 0.5, 1.4, 12.33, widths=[2.6, 0.9, 1.1, 1.2, 1.2, 2.2, 1.2], size=13,
              row_h=0.38, header=["Thí nghiệm", "Nhánh", "Số lần chạy", "Macro-F1", "Micro-F1",
                                  "KTC 95% (micro)", "p (Welch)"],
              relabel={"RQ1-v1": "Công thức v1 (test all)",
                       "RQ1-v2": "Công thức v2 (test annotated)"})
    kit.source_note(slide, 0.5, 4.08, 12.33, data)
    micro = {(row[0], row[1]): kit.number(row[4]) for row in data.rows if row[1] in ("B", "C")}
    kit.bar_chart(slide, 0.5, 4.45, 5.6, 2.4, ["v1 (test all)", "v2 (test annotated)"],
                  {"B: chỉ AudioSet": [micro[("RQ1-v1", "B")], micro[("RQ1-v2", "B")]],
                   "C: AudioSet + DataSEC": [micro[("RQ1-v1", "C")], micro[("RQ1-v2", "C")]]},
                  colors=[kit.NAVY, kit.YELLOW], title_text="Event-F1 micro trung bình")
    kit.callouts(slide, 6.35, 4.45, 6.48, 2.4, [
        "C − B âm nhẹ, khoảng tin cậy **chứa 0** ở cả hai công thức → **không có khác biệt**",
        "Học sẵn AudioSet thì giúp rõ: nhánh A (từ số 0) 0,036 so với B 0,062",
    ], [
        "DataSEC vô ích — riêng PSDS-2 của v2 tăng +0,028 (p = 0,019, chưa hiệu chỉnh so sánh bội)",
    ], size=12, split=0.58, horizontal=True)
    kit.notes(slide, """
(1,5 phút) Kết quả âm tính. Với cả hai công thức, nhánh C có điểm hơi thấp hơn B, nhưng khoảng
tin cậy
của hiệu C − B chứa số 0 và p lớn hơn nhiều so với 0,05, nên không có khác biệt.
Bảng không in đậm vì không có giá trị nào "tốt nhất" có ý nghĩa. Nhóm giữ nguyên kết quả âm tính
này,
và vì vậy trọng tâm đóng góp chuyển sang C1, C2, C4 (mô tả bám sự kiện, cách đo, hỏi đáp thời
gian).
Nếu thầy hỏi "DataSEC có vô ích không": chỉ kết luận về event-F1; PSDS-2 ở v2 có tăng.""")


def diagnosis(deck: Deck) -> None:
    slide = deck.content(5, "Vì sao v1 thấp, và v2 cải thiện được bao nhiêu", key="v2")
    ceilings = kit.load_table("report/tables/m03_sed_ceilings.md", "|cols=1,2")
    kit.table(slide, ceilings, 0.5, 1.4, 6.25, widths=[4.6, 1.65], size=12, row_h=0.33,
              header=["Đại lượng (tập dev)", "Event-F1 micro"], relabel={
                  "Trần độ phân giải: mô hình hoàn hảo, khối 0.32 s": "Tối đa có thể, khối 0,32 s",
                  "Trần độ phân giải: mô hình hoàn hảo, khối 0.64 s":
                      "Tối đa có thể, khối 0,64 s (như v1)",
                  "Trần độ phân giải: mô hình hoàn hảo, khối 1.28 s": "Tối đa có thể, khối 1,28 s",
                  "Trần người: 8 cặp bản ghi trùng chú giải hai lần":
                      "Người với người (8 cặp gán nhãn 2 lần)",
                  "Hệ v1 (ensemble C)": "v1 (gộp nhánh C)",
                  "Hệ v2 (ensemble 3 seed)": "v2 (gộp 3 lần chạy)",
                  "Phân rã v1: khớp / lệch biên / bỏ sót (trên 886 sự kiện)":
                      "v1: khớp / lệch biên / bỏ sót (886 sự kiện)",
                  "Phân rã v2: khớp / lệch biên / bỏ sót (trên 886 sự kiện)":
                      "v2: khớp / lệch biên / bỏ sót (886 sự kiện)",
              })
    ablation = kit.load_table("docs/thesis/tables/05_sed_v2_ablation.md",
                              r"|keep=2:seed 1\|không\|trần\|ensemble|cols=2,3,5")
    kit.text(slide, 0.5, 4.45, 6.25, 0.32, "Bỏ từng thay đổi của v2 (dev, mỗi biến thể 1 lần chạy)",
             size=12.5, bold=True, color=kit.NAVY)
    kit.table(slide, ablation, 0.5, 4.8, 6.25, widths=[3.3, 1.35, 1.6], size=11.5, row_h=0.29,
              header=["Cấu hình", "Micro-F1 (dev)", "Chênh so với v2"],
              relabel={"v2 đủ (seed 1/3)": "v2 đầy đủ (lần chạy 1)",
                       "không độ phân giải (pool /64)": "bỏ độ chi tiết thời gian (nén 64 lần)",
                       "trần pos_weight 50": "trọng số lớp dương trần 50",
                       "không augmentation": "bỏ làm giàu dữ liệu",
                       "ensemble C v1": "tham chiếu: v1 (gộp nhánh C)"})
    kit.stat(slide, 7.0, 1.4, 2.83, 1.6, "+0,054", "v2 hơn v1 trên test; khoảng tin cậy "
             "[+0,026; +0,085] **không chứa 0**", value_size=26, color=kit.GREEN, size=11.5)
    kit.stat(slide, 10.0, 1.4, 2.83, 1.6, "−0,084", "khi bỏ độ chi tiết thời gian: thay đổi có "
             "tác dụng lớn nhất", value_size=26, color=kit.RED, size=11.5)
    kit.callouts(slide, 7.0, 3.2, 5.83, 3.65, [
        "Lỗi chính là **lệch biên và bỏ sót**, không phải nhận nhầm loại",
        "v2 giảm lệch biên (417 → 377) nhưng **bỏ sót không giảm** (357 → 361)",
        "Test: micro v2 0,1476 so với v1 0,0941",
    ], [
        "v2 tốt hơn trên mọi mức nhạy — **PSDS không tăng** (0,3447 so với 0,3489); nguyên nhân "
        "chưa rõ",
        "Hai thay đổi kia vô dụng — chỉ là chưa đủ bằng chứng (1 lần chạy)",
    ], size=12, split=0.52)
    kit.source_note(slide, 0.5, 6.62, 6.25, "sed_ceilings_*_20260926.json; "
                    "sed_v2_ablation_20260926.json (dev, chỉ để chẩn đoán)")
    kit.notes(slide, """
(1,5 phút) Bảng trái là chẩn đoán trên dev. Kiến trúc v1 quyết định theo khối 0,64 s nên điểm
tối đa
chỉ 0,63; người với người chỉ khớp 0,58. Phân rã lỗi: phần lớn là lệch biên và bỏ sót.
Bảng ablation: bỏ độ chi tiết thời gian làm tụt 0,084, lớn nhất; hai thay đổi còn lại nằm trong
nhiễu.
Trên test v2 hơn v1 rõ (+0,054, khoảng tin cậy không chứa 0) — đây là cải thiện có ý nghĩa duy
nhất.
Nhưng PSDS không tăng, nghĩa là v2 tốt hơn ở đúng điểm vận hành đã chọn; giải thích việc này là
việc
trong kế hoạch tiếp theo. Lưu ý: số bảng trái là số dev in-sample, chỉ dùng để chẩn đoán.""")


def selection(deck: Deck) -> None:
    slide = deck.content(5, "Chọn hệ cuối: f2 đứng đầu trên dev, nhưng test xếp hạng khác",
                         key="s13")
    kit.picture(slide, FIG / "m03_s13_dev_vs_test.png", 0.5, 1.4, 5.9, 4.95)
    kit.source_note(slide, 0.5, 6.45, 5.9, "s13_selection_20261018.json; s13_test_20261018.json")
    data = kit.load_table("docs/thesis/tables/06_s13_ranking_test.md",
                          r"|keep=2:^(f2\|f4\|g2\|f1\|g1\|c)$|cols=1,2,5,6,7,8|best=5+,7+,8+"
                          r"|used=2:^f2$")
    kit.table(slide, data, 6.65, 1.4, 6.18, widths=[0.9, 0.7, 1.15, 1.2, 1.1, 1.13], size=12,
              row_h=0.36, header=["Hạng dev", "Mã", "Dev micro", "Dao động", "Test macro",
                                  "Test micro"])
    kit.legend_note(slide, 6.65, 3.98, 6.18)
    kit.callouts(slide, 6.65, 4.35, 6.18, 2.5, [
        "f2 hơn f4 trên dev chỉ 0,003, nhỏ hơn độ dao động 0,056 → **được chọn theo luật**, "
        "không gọi là tốt hơn",
        "Test: f1 micro cao nhất (0,1817), g1 macro cao nhất (0,1617)",
    ], [
        "Nên đổi sang f1 — chọn lại theo điểm test là “học thuộc đề”; khoảng tin cậy test các "
        "ứng viên đầu đều chồng nhau",
    ], size=12, split=0.56)
    kit.notes(slide, """
(1,5 phút) Hình trái: chấm cam là điểm trên dev (trung bình 5 phần), chấm xanh là điểm test với
khoảng tin cậy.
Theo luật ghi trước, f2 đứng đầu dev nên được chọn, nhưng f2 chỉ hơn f4 0,003 — nhỏ hơn độ dao
động.
Trên test thứ hạng khác: f1 và g1 cao hơn. Nhóm không đổi sang f1, vì chọn theo điểm test là
gian lận,
và khoảng tin cậy các ứng viên đầu đều chồng nhau. Đây là minh chứng cho sai số khi chọn trên
dev nhỏ.
Bảng đầy đủ 11 ứng viên ở Phụ lục 1.""")


def progress(deck: Deck) -> None:
    slide = deck.content(5, "v1 → v2 → f2: tiến bộ rõ so với v1, nhưng f2 chưa chắc hơn v2",
                         key="progress")
    data = kit.load_table("docs/thesis/tables/04_sed_progress.md",
                          "|cols=1,3,4,5,6,7|best=3+,4+,6+,7+|used=1:^S13")
    kit.table(slide, data, 0.5, 1.4, 12.33, widths=[3.4, 1.4, 1.4, 2.3, 1.4, 1.4], size=13,
              row_h=0.42, header=["Hệ thống (test annotated, 139 bản ghi)", "Macro-F1",
                                  "Micro-F1", "KTC 95% (micro)", "PSDS-1", "PSDS-2"],
              relabel=SYSTEM_NAMES)
    kit.legend_note(slide, 0.5, 3.12, 12.33)
    names = [SYSTEM_NAMES[kit.plain(row[0])].split(" (")[0].split(":")[0] for row in data.rows]
    kit.bar_chart(slide, 0.5, 3.5, 5.6, 3.35, names,
                  {"Macro-F1": kit.column(data, "Macro-F1"),
                   "Micro-F1": kit.column(data, "Micro-F1")},
                  colors=[kit.BLUE, kit.NAVY], title_text="Event-F1 trên test annotated",
                  max_value=0.2)
    kit.callouts(slide, 6.35, 3.5, 6.48, 3.35, [
        "f2 hơn v1 rõ (micro 0,164 so với 0,095)",
        "f2 chỉ báo **295 sự kiện / 740 thật**; 7/21 loại âm điểm 0 → bị giới hạn bởi **bỏ sót**",
        "cSEBB lần đầu thắng ngưỡng chung ở f2 (0,2383 so với 0,2107 trên dev, trong biên dao "
        "động)",
    ], [
        "f2 là tốt nhất — macro và PSDS-1 thấp hơn v2, khoảng tin cậy micro chồng nhau → f2 là hệ "
        "**được chọn theo luật**, chưa chứng minh là tốt nhất",
    ], size=12, split=0.62)
    kit.notes(slide, """
(1 phút) So ba thế hệ trên cùng tập test annotated. f2 hơn v1 rõ ở micro. So với v2 thì không
kết luận
được: f2 cao hơn ở micro và PSDS-2 nhưng thấp hơn ở macro và PSDS-1.
Điểm yếu lớn nhất của f2 là bỏ sót: báo 295 sự kiện trong khi có 740 sự kiện thật; 7 loại âm
điểm 0.
Bảng theo từng loại âm ở Phụ lục 4.""")


def rq2(deck: Deck) -> None:
    slide = deck.content(5, "RQ2: ép theo luật đưa “bịa” và “thêm bối cảnh” về 0, đổi lại dễ "
                               "bỏ sót",
                         key="rq2")
    data = kit.load_table("report/tables/m04_rq2_levels.md",
                          "|cols=1,2,3,4,5,6,7,8|group=2|best=3-,4-,6-,7-,8-|used=1:^Template")
    kit.table(slide, data, 0.5, 1.4, 12.33, widths=[2.0, 1.2, 1.4, 1.2, 1.8, 1.7, 1.6, 1.2],
              size=12.5, row_h=0.34, header=["Cách viết", "Mức chấm", "Bịa nguồn âm", "Bỏ sót",
                                             "Đúng thứ tự (số câu)", "Tên quá cụ thể",
                                             "Thêm bối cảnh", "Từ cấm"])
    kit.legend_note(slide, 0.5, 4.78, 8.0)
    kit.source_note(slide, 8.3, 4.78, 4.53, "caption_grounding_…_f2_test.json (142 bản ghi)")
    kit.callouts(slide, 0.5, 5.12, 12.33, 1.73, [
        "Viết tự do **hiếm bịa nguồn âm** (0,0065 / 0,0112), nhưng 28,9% / 40,1% câu **thêm bối "
        "cảnh**, ~14% gọi tên quá cụ thể",
        "Ép theo ngữ pháp → các lỗi này về 0; cái giá là bỏ sót (oracle 0,0925); bản cover → bỏ "
        "sót 0",
    ], [
        "Câu “0 bịa” là câu đúng với âm thanh — xem slide sau",
        "Bộ đếm lỗi hoàn hảo — dựa trên từ điển, mới đối chiếu 1 người / 60 câu",
    ], size=12, split=0.64, horizontal=True)
    kit.notes(slide, """
(1,5 phút) Đọc theo cột: mỗi cột là một loại lỗi, càng thấp càng tốt; số in đậm là thấp nhất
trong mỗi mức chấm.
Phát hiện bất ngờ: viết tự do ít khi bịa ra nguồn âm, nhưng hay "thêm mắm muối": 40% câu
đầu–cuối thêm bối
cảnh, khoảng 14% gọi tên quá cụ thể (nói "xe cứu thương" khi nhãn chỉ là "còi").
Ép theo ngữ pháp đưa các lỗi này về 0; cái giá là bỏ sót ở mức oracle. Bản cover khử được cái
giá này.
Hiệu bối cảnh constrained − unconstrained ở đầu–cuối là −0,401 [−0,479; −0,324].""")


def rq2_limits(deck: Deck) -> None:
    slide = deck.content(5, "RQ2: “không bịa” chưa có nghĩa là “đúng với âm thanh”", key="rq2b")
    kit.picture(slide, FIG / "m05_dev_timeline.png", 0.5, 1.4, 7.4, 3.87)
    kit.box(slide, 0.5, 5.45, 7.4, 1.4, fill=kit.SOFT, line=None, rounded=True)
    kit.text(slide, 0.7, 5.5, 7.0, 1.3, [
        "Câu mô tả (constrained-cover, S-0009): “The sound of jet aircrafts can be heard from "
        "0.3 to 10.0 seconds, followed by the sound of birds …”",
        "→ Hợp lệ G1–G3, nhưng đặt máy bay sai chỗ và bỏ sót 4 sự kiện so với nhãn gốc.",
    ], size=12.5, italic=False)
    kit.stat(slide, 8.15, 1.4, 4.68, 1.5, "349 / 740", "sự kiện thật mà hệ f2 bỏ sót trên test",
             value_size=28, color=kit.RED)
    kit.stat(slide, 8.15, 3.05, 4.68, 1.5, "0,896 / 0,936", "precision / recall của bộ đếm từ "
             "điển so với 1 người đọc trên 60 câu", value_size=26)
    kit.card(slide, 8.15, 4.7, 4.68, 2.15, "Vì vậy", [
        "Câu mô tả trung thành với **danh sách máy đoán**",
        "Máy nghe sai thì câu cũng sai theo; ràng buộc chỉ giúp **truy ra** lỗi đến từ sự kiện nào",
    ], size=12.5)
    kit.notes(slide, """
(1 phút) Đây là giới hạn quan trọng nhất của RQ2. Hình trên: nhãn gốc; hình dưới: hệ f2 dự đoán.
Câu mô tả đúng với danh sách dự đoán, nhưng so với âm thanh thật thì sai vị trí máy bay và bỏ
sót 4 sự kiện.
Nhóm tách rõ hai mức: oracle đo riêng bộ viết mô tả; đầu–cuối đo cả hệ thống.""")


def rq3(deck: Deck) -> None:
    slide = deck.content(5, "RQ3: lọc cứng luôn đúng điều kiện, nhưng xếp hạng phụ thuộc SED",
                         key="rq3")
    data = kit.load_table("docs/thesis/tables/09_rq3_retrieval.md",
                          "|keep=1:gold$&2:/en$|cols=1,2,4,5,8,9|group=1|best=4+,9+"
                          "|used=1:^f2 — gold$&2:^hybrid")
    kit.table(slide, data, 0.5, 1.4, 7.45, widths=[1.5, 1.75, 1.15, 1.6, 1.2, 1.15], size=12,
              row_h=0.4, header=["Kho sự kiện", "Cách tìm", "nDCG@10", "KTC 95%", "Recall@10",
                                 "Đúng bộ lọc"], relabel={
                  "Run B — gold": "Nhánh B", "f2 — gold": "f2 (hệ cuối)",
                  "structured_only/en": "Chỉ lọc", "vector_only/en": "Chỉ theo nghĩa",
                  "hybrid/en": "Kết hợp"})
    kit.legend_note(slide, 0.5, 4.27, 7.45)
    kit.source_note(slide, 0.5, 4.55, 7.45, "s8_summary_20261002.json (test, tiếng Anh, bộ lọc "
                    "chuẩn; bảng đầy đủ ở Phụ lục 2)")
    kit.stat(slide, 0.5, 5.05, 3.65, 1.8, "0,000", "khẳng định thiếu bằng chứng trong câu trả "
             "lời, ở cả 8 cấu hình", value_size=28, color=kit.GREEN, size=12)
    kit.stat(slide, 4.3, 5.05, 3.65, 1.8, "97 / 97", "câu trả lời đúng khuôn, có bằng chứng "
             "thật, trích dẫn thỏa bộ lọc", value_size=28, color=kit.GREEN, size=12)
    kit.callouts(slide, 8.2, 1.4, 4.63, 5.45, [
        "Kho B: **chỉ lọc** cao nhất (0,523); kết hợp kém hơn −0,042 [−0,085; −0,004]",
        "Đổi sang kho f2: hai cách có lọc **giảm** (0,523 → 0,416)",
        "Chỉ theo nghĩa tăng lên 0,526, nhưng **73% kết quả sai điều kiện**",
    ], [
        "Phần tìm kiếm hỏng — giả thuyết là f2 bỏ sót sự kiện nên bộ lọc loại mất bản ghi "
        "đúng (chưa kiểm chứng)",
        "Kết quả thực tế cao như vậy — bộ lọc chuẩn giả định hiểu đúng câu hỏi, nên đây là "
        "cận trên",
    ], size=12, split=0.55)
    kit.notes(slide, """
(1,5 phút) Đọc theo từng kho: số in đậm là tốt nhất trong mỗi kho. Hàng xám là cấu hình demo
dùng.
Cách có lọc luôn đúng điều kiện 100%. Cách chỉ theo nghĩa có nDCG cao trên kho f2 nhưng 73% kết
quả sai điều kiện,
ví dụ hỏi "dài hơn 30 giây" vẫn trả bản ghi ngắn.
Khi đổi sang kho f2, điểm của hai cách có lọc giảm — nhóm báo nguyên kết quả kém đi. Giả thuyết:
f2 bỏ sót
nhiều sự kiện nên kho thiếu, bộ lọc loại mất bản ghi đúng. Muốn cải thiện phải nâng recall của
SED.""")


def parser_parity(deck: Deck) -> None:
    slide = deck.content(5, "Bộ đổi câu hỏi ra bộ lọc đúng khuôn 100%, hiểu đúng nghĩa 86–93%",
                         key="parser")
    parser = kit.load_table("docs/thesis/tables/10_parser_l2.md", "|cols=1,2,3,4,5,6,7")
    kit.table(slide, parser, 0.5, 1.4, 8.0, widths=[1.8, 0.8, 1.1, 1.2, 1.1, 1.1, 1.5], size=12,
              row_h=0.5, header=["Tập câu hỏi", "Số câu", "Đúng khuôn", "Đúng hoàn toàn",
                                 "Loại âm (P)", "Loại âm (R)", "Đúng điều kiện thời gian"],
              relabel={"template": "Câu mẫu", "paraphrase": "Câu diễn đạt lại"})
    kit.source_note(slide, 0.5, 2.95, 8.0, parser)
    parity = kit.load_table("docs/thesis/tables/11_serving_parity.md", "|cols=1,5,6,7,8,9")
    kit.text(slide, 0.5, 3.5, 8.0, 0.35, "Hệ đang phục vụ có tái tạo đúng hệ đã đo không?", size=14,
             bold=True, color=kit.NAVY)
    kit.table(slide, parity, 0.5, 3.9, 8.0, widths=[1.7, 1.2, 1.2, 1.2, 1.4, 1.3], size=12,
              row_h=0.5, header=["Nơi chạy", "Sự kiện chuẩn", "Sự kiện phục vụ", "Trùng khít",
                                 "Trong sai số 0,2 s", "Lệch xác suất lớn nhất"],
              relabel={"Host CUDA": "Máy chủ, GPU", "Container CPU": "Docker, CPU"})
    kit.source_note(slide, 0.5, 5.45, 8.0, parity)
    kit.callouts(slide, 8.75, 1.4, 4.08, 5.45, [
        "Lỗi chủ yếu ở điều kiện thời gian (0,767 trên câu mẫu): đảo vai trò A/B, nhầm "
        "“nằm trong” với “chồng nhau”",
        "GPU tái tạo đúng 299/299 sự kiện",
    ], [
        "Bản demo trùng khít hệ đã đo — chạy CPU thì 290/299 trùng khít, 294/299 trong sai số",
        "Bộ đổi câu hỏi làm tìm kiếm tốt lên — nDCG@10 lệch với bộ lọc chuẩn chỉ −0,006 … 0,000",
    ], size=12, split=0.52)
    kit.notes(slide, """
(1 phút) Bộ đổi câu hỏi dùng mô hình ngôn ngữ bị ép theo lược đồ JSON nên luôn đúng khuôn
240/240.
Hiểu đúng nghĩa hoàn toàn 85,5% trên câu mẫu và 92,5% trên câu diễn đạt lại; lỗi ở điều kiện
thời gian.
Bảng dưới kiểm tra hệ đang phục vụ: trên GPU trùng khít 100%; trên CPU (demo) lệch nhẹ do phép
tính số thực khác.""")


def summary(deck: Deck) -> None:
    slide = deck.content(5, "Tổng kết: hệ thống chạy đầu–cuối; điểm nghẽn là SED còn bỏ sót")
    cards = [
        ("RQ1", "Âm tính", kit.GRAY, "Học thêm DataSEC không làm event-F1 tốt hơn, ở cả 2 "
         "công thức và nhiều lần chạy."),
        ("RQ2", "Hiệu quả, có giá", kit.GREEN, "Ép theo ngữ pháp → 0 bịa, 0 bối cảnh, 0 từ cấm; "
         "cái giá là bỏ sót, bản cover khử được."),
        ("RQ3", "Lọc đúng, xếp hạng bị chặn", kit.BLUE, "Lọc cứng đúng điều kiện 100%; chất lượng "
         "xếp hạng phụ thuộc recall của SED."),
    ]
    width = (12.33 - 0.3) / 3
    for index, (code, verdict, color, body) in enumerate(cards):
        x = 0.5 + index * (width + 0.15)
        kit.box(slide, x, 1.4, width, 2.55, fill=kit.WHITE, rounded=True)
        kit.badge(slide, x + 0.2, 1.58, code, size=0.62, fill=kit.NAVY, color=kit.WHITE, font=15)
        kit.text(slide, x + 0.95, 1.58, width - 1.1, 0.62, verdict, size=17, bold=True,
                 color=color, anchor=MSO_ANCHOR.MIDDLE)
        kit.text(slide, x + 0.2, 2.4, width - 0.4, 1.5, body, size=14)
    kit.card(slide, 0.5, 4.15, 7.6, 2.7, "Hạn chế", [
        "SED còn yếu: event-F1 micro 0,164, bỏ sót nhiều",
        "Tập dev/test nhỏ (134/139 bản ghi), huấn luyện không ổn định giữa các lần chạy",
        "Bộ đếm lỗi mô tả dựa trên từ điển, mới đối chiếu 1 người",
        "10/40 lượt chấm test SED ghi cờ `dirty` (đã công khai, mã không đổi)",
        "Âm thanh nguồn trùng AudioSet: không đo được mức trùng",
    ], accent=kit.WARN_TEXT, size=13)
    kit.box(slide, 8.35, 4.15, 4.48, 2.7, fill=kit.NAVY, line=None, rounded=True)
    kit.text(slide, 8.6, 4.3, 4.0, 2.4, [
        [kit.Run("Điều nhóm làm được", bold=True, color=kit.YELLOW)],
        [kit.Run("Hệ thống không chỉ chạy, mà ", color=kit.WHITE),
         kit.Run("biết và đo được giới hạn của mình", bold=True, color=kit.YELLOW),
         kit.Run(": dữ liệu trùng, RQ1 âm tính, lỗi nằm ở biên và bỏ sót, cái giá của ràng "
                 "buộc, và vì sao tìm kiếm bị chặn.", color=kit.WHITE)],
    ], size=14, space=8)
    kit.notes(slide, """
(1 phút) Tóm tắt ba câu trả lời. Điểm yếu lớn nhất là bước phát hiện sự kiện: recall thấp kéo
theo
cả câu mô tả lẫn kết quả tìm kiếm. Các hạn chế đều được ghi trong báo cáo, kể cả sự cố cờ dirty.""")
