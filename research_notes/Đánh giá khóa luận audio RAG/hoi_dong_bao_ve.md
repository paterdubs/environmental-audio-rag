# Hội đồng bảo vệ KLTN ngành Khoa học Dữ liệu (IUH): tiêu chí chấm và ngân hàng câu hỏi cho đề tài environmental-audio-rag

> Soạn ngày 23/11/2026. Đường dẫn trong backtick là đường dẫn tương đối tính từ gốc repo `environmental-audio-rag`.
> Số liệu dự án trích nguyên từ tệp đã khóa. Khi soạn ghi chú này không chạy thí nghiệm, không đọc tập test, không sửa tệp nào
> khác trong repo. Nguồn web ghi kèm mức tin cậy: **(IUH, chính thức)**, **(trường khác, chính thức)**,
> **(blog/tổng hợp)**. Nguồn nào chỉ đọc được đoạn trích từ máy tìm kiếm thì ghi "(đoạn trích)".

## 1. IUH quy định gì về KLTN (Khoa CNTT, ngành KHDL), chấm thế nào, và điều gì tách bài 9–10 khỏi bài 7–8?

### Takeaway
IUH không công bố phiếu chấm hay rubric KLTN của Khoa CNTT trên web. Phần chắc chắn là quy trình: GVHD duyệt → bộ môn phản biện →
phân loại "báo cáo trước Hội đồng / Poster / không đạt" → đánh giá trực tiếp. Lịch đợt này: báo cáo GVHD **trước 06/12/2026**, phản
biện **07–18/12**, công bố danh sách **trước 20/12**, đánh giá **sáng thứ Tư 23/12/2026**. Trọng số và mô tả mức điểm chỉ suy được từ
rubric công khai của trường khác (UIT, KHTN-HCMUS, ĐHSP Đà Nẵng) và từ thông báo của một khoa khác trong IUH. Theo các rubric đó,
bài 9–10 hơn bài 7–8 ở bốn chỗ: có tính mới kèm so sánh công phu hoặc so với SOTA; đáp ứng *tất cả* mục tiêu; quá trình chủ động
và báo cáo đều; trả lời tốt *các* câu hỏi chứ không phải *hầu hết*.

### Cited Findings

**Văn bản và thông báo của IUH (chính thức)**
- Quy chế đào tạo tín chỉ IUH, Điều 18 khoản 6: học phần tốt nghiệp "chỉ có một cột điểm tổng kết học phần, điểm đạt là từ 5.0 trở
  lên (theo thang điểm 10.0)". Chi tiết thực hiện và đánh giá nằm trong "Quy định về việc thực hiện học phần Thực tập doanh nghiệp và
  Khóa luận tốt nghiệp hiện hành của Nhà trường". Điểm làm tròn đến 0,1 (Điều 19). — [Cẩm nang IUH (IUH, chính thức)](https://camnang.iuh.edu.vn/quy-che-dao-tao-theo-he-thong-tin-chi.php)
- Phòng Đào tạo đăng "Quy chế đào tạo tín chỉ ban hành năm 2025" (29/10/2025). Trang không có văn bản riêng về KLTN, rubric hay phiếu
  chấm, dù quy chế có viện dẫn quy định riêng nói trên. — [PĐT IUH (IUH, chính thức)](https://pdt.iuh.edu.vn/quy-che-dao-tao)
- Thông báo Khoa CNTT ngày 05/11/2026 cho HK1/2026–2027: báo cáo GVHD "trước ngày 06/12/2026"; từ 07/12 đến 18/12/2026 các bộ môn
  phản biện; trước 20/12/2026 công bố danh sách nhóm báo cáo trước Hội đồng, nhóm đánh giá bằng poster và nhóm không đạt; đánh giá
  chính thức "sáng thứ tư ngày 23/12/2026"; hình thức "Trực tiếp"; khoa sẽ đăng hướng dẫn chi tiết sau. Thông báo không có tiêu chí
  chấm. — [FIT IUH, 05/11/2026 (IUH, chính thức)](https://fit.iuh.edu.vn/news.html@detail@155@3610@Thong-bao-thoi-gian-danh-gia-Khoa-luan-tot-nghiep,-Thuc-tap-doanh-nghiep-HK1-2026-2027)
- Khung này đã lặp lại ở đợt trước (đăng 11/04/2025): ba kết quả "báo cáo trước Hội đồng, báo cáo dạng Poster, hoặc không đạt"; báo
  cáo GVHD trước 15/5/2025, bộ môn phản biện 19–23/5, công bố trước 26/5, đánh giá 28/5/2025. — [FIT IUH, HK2/2024–2025 (IUH, chính thức)](https://fit.iuh.edu.vn/news.html@detail@155@3398@Thong-bao-thoi-gian-danh-gia-Khoa-luan-tot-nghiep,-Thuc-tap-doanh-nghiep,-Bai-tap-lon-hoc-phan-he-DH,-CD_HK2-2024-2025)
- Ngành KTPM, HK2/2025–2026 (đánh giá 05/06/2026): 35 nhóm hoàn thành KLTN; **6 nhóm** có "kết quả xuất sắc nhất" báo cáo trước hội
  đồng chuyên môn, các nhóm còn lại trình bày poster. Phần lớn đề tài tốt nhất đã trình bày ở hội nghị SSRC đầu tiên của Khoa
  (26/05/2026). — [FIT IUH, KTPM (IUH, chính thức)](https://fit.iuh.edu.vn/news.html@detail@102@3557@%5BKTPM%5D-Danh-gia-Khoa-luan-tot-nghiep-HK2-2025-2026)
- Bộ môn HTTT (cùng Khoa CNTT), HK1/2026–2027: "Mỗi đề tài gồm tối đa 2 sinh viên"; KLTN 15 tuần; email báo cáo hằng tuần cho GVHD,
  dùng làm minh chứng tiến độ, kỹ năng và thái độ; báo cáo giữa kỳ tuần 8–9; tuần 16 GVHD quyết định đề tài có được đi phản biện hay
  không; tuần 17 phản biện quyết định hội đồng hay poster; tuần 18 trình bày. Kế hoạch và nhật ký làm việc do GVHD duyệt. Đây là
  thông báo của bộ môn HTTT, không phải KHDL. — [FIT IUH, Bộ môn HTTT (IUH, chính thức)](https://fit.iuh.edu.vn/news.html@detail@155@3581@%5BIS%5D-Khoa-luan-tot-nghiep-Nganh-HTTT-HK1-nam-hoc-2026-2027)
- Mẫu báo cáo KLTN ngành KHDL của khoa (bản 2026), phần "Trình tự thực hiện":
  - "điểm cộng cho những ý tưởng sáng tạo, mới mẻ";
  - kế hoạch phải có "phân công nhiệm vụ trong nhóm";
  - "Mô hình gọn gàng, khoa học, sáng tạo, chắc chắn và vệ sinh là điểm cộng" và "các sáng kiến là điểm cộng";
  - mã nguồn "cần được sắp xếp rõ ràng, để chuẩn bị nộp cho GVHD và Khoa";
  - "chú ý trích dẫn và tránh copy/đạo văn";
  - "Các đề tài đủ tiêu chuẩn sẽ được phép liên hệ với các giảng viên phản biện";
  - báo cáo chính thức "trước hội đồng hoặc báo cáo poster tùy theo quyết định của GVHD";
  - poster in một trang A0, có "kết quả thực hiện và khả năng ứng dụng (nếu có)", "hạn chế chữ quá nhiều";
  - thành phần bắt buộc có "Trang Nhận xét và đánh giá của Giáo viên phản biện".

  — `report/Mau bao cao KLTN_DS.docx` (đọc trực tiếp văn bản trong `word/document.xml`); tóm tắt định dạng ở `report/quy_cach_bao_cao.md`.
- Khoa Công nghệ Điện IUH (thông báo 05/05/2026, *không phải Khoa CNTT*): "Điểm khóa luận được xác định là: 20% điểm của giảng viên
  hướng dẫn + 80% điểm trung bình của Hội đồng bảo vệ"; trình bày tối đa 15–20 phút; bắt buộc có PowerPoint; kiểm tra Turnitin dưới
  30% tổng và dưới 8% với một nguồn; nộp bản sửa trong 10 ngày sau buổi bảo vệ. — [Khoa CN Điện IUH (IUH, chính thức, khác khoa)](https://feet.iuh.edu.vn/news.html@detail@264@1490@Thong-bao-V-v-Bao-ve-khoa-luan-tot-nghiep-dai-hoc-cac-lop-hoc-lai-HK2-va-DHDI20AVL)

**Rubric công khai của trường khác (dùng để đối chiếu)**
- UIT, Quy định KLTN ban hành theo QĐ 159/QĐ-ĐHCNTT (05/03/2024) **(trường khác, chính thức)**:
  - Điều 5.3: mỗi đề tài 1–2 SV "với sự phân công trách nhiệm cụ thể cho từng SV có ghi rõ trong đề cương nghiên cứu".
  - Điều 9: CBPB có học vị từ thạc sĩ, khác CBHD; "SV phải báo cáo với CBPB trước khi bảo vệ trước hội đồng".
  - Điều 12.5: "SV trình bày đề tài không quá 15 phút"; CBPB (hoặc thư ký) đọc nhận xét; SV trả lời câu hỏi của CBPB và hội đồng.
  - Điều 13.1: căn cứ đánh giá gồm "tính mới, tính khoa học, tính sáng tạo, tính thực tiễn" và "Khả năng, xử lý và giải quyết vấn đề
    của SV, triển vọng của kết quả nghiên cứu".
  - Điều 13.2: thang 10, lẻ đến 0,5; CBHD và CBPB hệ số 2, thành viên còn lại hệ số 1, ví dụ "(TV1+TV2+CBHD*2+CBPB*2)/6". Điểm lệch
    từ 2 trở lên so với điểm tổng kết thì hội đồng họp lại, nếu không thống nhất thì không tính điểm đó.

  — [UIT 159/QĐ-ĐHCNTT](https://student.uit.edu.vn/sites/daa/files/202410/159-qd-dhcntt_05-03-2024_ban_hanh_quy_dinh_kltn.pdf)
- Khoa CNTT ĐH KHTN TP.HCM, "Tiêu chí và biểu mẫu chấm điểm tốt nghiệp" v4 (27/06/2023) **(trường khác, chính thức)**. Có bốn mức
  9–10 / 7–9 / 5–7 / dưới 5. Mẫu **hướng nghiên cứu** gồm:
  - *Chủ đề và ý tưởng (15%).* 9–10: "Chủ đề phù hợp, có độ khó cao, mới, và có sự quan tâm của cộng đồng nghiên cứu". 7–9: "có độ khó
    trung bình".
  - *Phương pháp (20%).* 9–10: "Các mục tiêu được rõ ràng… đáp ứng tốt **tất cả** các mục tiêu đề ra". 7–9: "tương đối rõ ràng… đáp ứng
    tốt các mục tiêu quan trọng".
  - *Đóng góp khoa học và thực tiễn (20%).* 9–10: "Bài toán, giải pháp hoặc kết quả có tính mới và sáng tạo (bao gồm việc áp dụng giải
    thuật sẵn có trên bộ dữ liệu mới)… Có đánh giá, so sánh công phu. Kết quả tốt so với các giải pháp tốt nhất (state of the art)". 7–9:
    "Bài toán hoặc giải pháp không mới (như cài đặt giải thuật), nhưng có đánh giá, so sánh tốt". 5–7: "Có đánh giá, so sánh nhưng sơ sài".
  - *Quá trình thực hiện (10%, chủ yếu do GVHD chấm).* 9–10: "Chủ động, độc lập… Tiến độ công việc được báo cáo thường xuyên. Công việc
    được thực hiện đúng tiến độ". 7–9: "tương đối đúng tiến độ".
  - *Báo cáo viết (20%).* 9–10: "cấu trúc rất rõ ràng… Nội dung đúng và đầy đủ với các luận điểm có căn cứ, có dẫn chứng. Không có lỗi chính tả".
  - *Trình bày trước hội đồng (15%).* 9–10: "Các câu hỏi của hội đồng được trả lời tốt". 7–9: "**Hầu hết** các câu hỏi… được trả lời tốt".
  - *Điểm cộng tối đa 10% cho công bố.* Bài toàn văn Q1/Q2 hoặc hội nghị A*/A/B tối đa 1,0; Q3/Q4 hoặc hạng C 0,8; Scopus 0,6; không
    xếp hạng 0,4; bài ngắn dưới 5 trang 0,2.

  Mẫu **hướng ứng dụng** gồm "Độ lớn/phức tạp của công việc" 20% (7–9: "độ phức tạp trung bình, khối lượng công việc tương đối nhiều";
  ở mẫu thực tập dự án, mức 9–10 là "độ phức tạp cao, khối lượng công việc nhiều") và "Mức độ hoàn thành" 20% ("cài đặt hoàn chỉnh,
  kiểm thử cẩn thận"). Mẫu có ghi chú về AI: "Trường không cấm sinh viên dùng ChatGPT và các công cụ hỗ trợ khác. Tuy nhiên, sinh viên
  là tác giả… phải chịu trách nhiệm về tính đúng đắn… Nội dung thiếu dẫn chứng, minh chứng được xem là sai hoặc không đáng tin cậy". —
  [HCMUS-FIT rubric v4](https://www.ctda.hcmus.edu.vn/wp-content/uploads/2024/07/Khoa-CNTT-Tieu-chi-va-bieu-mau-cham-diem-tot-nghiep-v4-20230627-1.pdf)
- ĐH Sư phạm, ĐH Đà Nẵng (biểu mẫu tải lên 08/2025, mẫu ghi năm 2016) **(trường khác, chính thức)**: phiếu thành viên hội đồng gồm "Nội
  dung và phương pháp nghiên cứu 7 điểm; Trình bày văn bản 1 điểm; Trình bày, trả lời câu hỏi tại buổi bảo vệ 2 điểm". Điểm cuối là trung
  bình cộng điểm hội đồng, phản biện và hướng dẫn. Điểm lệch quá 20% so với trung bình lần 1 bị loại. — [UED, Biểu mẫu BVKLTN](https://ued.udn.vn/wp-content/uploads/2025/08/Bieu-mau-BVKLTN.pdf)
- Học viện Nông nghiệp VN (2025) dùng ba rubric riêng cho GVHD, GVPB và hội đồng, có trọng số; mốc "Tốt 8.5–10, Khá 6.5–8.4"
  (đoạn trích). — [VNUA rubric 2025](https://file.vnua.edu.vn/data/21/documents/2025/08/22/btvcntp/55-cp04996-khoa-luan-tot-nghiep-cn-kdtp-rubric-8-2025.pdf).
  Tài liệu rubric mẫu của HUIT có mẫu C10 (thành viên hội đồng) và C11 (người hướng dẫn hoặc phản biện), thang Giỏi 10–9, Khá 8–7
  (đoạn trích). — [HUIT, Hướng dẫn rubric](https://huit.edu.vn/Images/Documents/N00CT/huong-dan-thiet-ke-su-dung-rubric-ver_1_0.pdf)
- ĐH Nguyễn Tất Thành: hội đồng chấm theo "tính mới mẻ và sáng tạo, giá trị khoa học và khả năng ứng dụng, chất lượng báo cáo viết,
  chất lượng phần trình bày và mức độ tự tin, thuyết phục trong phản biện" (đoạn trích). — [NTT, CNTT](https://cntt.ntt.edu.vn/hoat-dong/sinh-vien/danh-gia-khoa-luan-tot-nghiep-nganh-cong-nghe-thong-tin-va-ky-thuat-phan-mem-sinh-vien-k-2021/)

**Mâu thuẫn giữa các nguồn IUH**
- Mẫu báo cáo ghi hội đồng hay poster là "tùy theo quyết định của GVHD" (`report/Mau bao cao KLTN_DS.docx`). Thông báo của Khoa và Bộ
  môn HTTT ghi bộ môn phản biện xét rồi khoa công bố danh sách ([FIT 05/11/2026](https://fit.iuh.edu.vn/news.html@detail@155@3610@Thong-bao-thoi-gian-danh-gia-Khoa-luan-tot-nghiep,-Thuc-tap-doanh-nghiep-HK1-2026-2027);
  [HTTT](https://fit.iuh.edu.vn/news.html@detail@155@3581@%5BIS%5D-Khoa-luan-tot-nghiep-Nganh-HTTT-HK1-nam-hoc-2026-2027)).
  Thực tế có lẽ GVHD đề xuất và bộ môn phản biện quyết. Đây là suy luận, cần hỏi GVHD.

### Inferences
- **Phản biện (07–18/12) là vòng quyết định, không phải buổi 23/12.** KTPM chỉ đưa 6/35 nhóm (≈17%) lên hội đồng, còn lại làm poster.
  Vì vậy được vào hội đồng gần như là điều kiện để đạt điểm cao. Nhóm nên chuẩn bị cho buổi gặp GVPB kỹ như buổi bảo vệ: bản trình bày
  5–7 phút, báo cáo in, demo chạy được.
- **Cấu trúc điểm ở Khoa CNTT chưa biết.** Nên chuẩn bị cho cả hai kiểu. Kiểu UIT: GVHD và GVPB hệ số 2, nên báo cáo viết và nhận xét
  của GVPB nặng ký. Kiểu Khoa Điện IUH: 20% GVHD và 80% hội đồng, nên buổi trình bày và hỏi đáp nặng ký. Cả hai kiểu đều thưởng cho
  việc trả lời tốt câu hỏi của GVPB, và các câu này thường được hỏi lại trước hội đồng (UIT Điều 12.5).
- **Đối chiếu đề tài với mức 9–10 của rubric HCMUS.** Đây là ước lượng chủ quan, không phải điểm thật:

  | Tiêu chí (trọng số HCMUS) | Mức 9–10 đòi hỏi | Hiện trạng đề tài | Khoảng trống |
  |---|---|---|---|
  | Chủ đề (15%) | Khó, mới, cộng đồng quan tâm | SED đa âm, mô tả bám sự kiện, RAG theo thời gian; ảo giác của mô hình âm thanh–ngôn ngữ là chủ đề nóng 2024–2026 (`docs/RELATED_WORK.md`) | Không đáng kể |
  | Phương pháp (20%) | Mục tiêu rõ, đáp ứng tất cả | Ghi trước luật chọn, mở test một lần, nhiều seed, khoảng tin cậy bootstrap (`report/final_src/06_ket_qua.md`) | Mục tiêu "học chuyển giao" (RQ1) âm tính; phải trình bày là đã *trả lời* câu hỏi |
  | Đóng góp (20%) | Mới; so sánh công phu; so với SOTA | So sánh nội bộ rất công phu; tự hạ claim xuống "áp dụng và mở rộng" (`report/final_src/01_gioi_thieu.md`) | Không có SOTA ngoài trên DataSED; LBR không nằm trong bảng đóng góp C1–C4 |
  | Quá trình (10%) | Báo cáo đều, đúng tiến độ | 397 commit từ 22/09 đến 11/11/2026, 48 ADR | Nhật ký tuần 5–7 còn trống (`report/final_src/90_phan_cuoi.md`); chưa có phân công |
  | Báo cáo viết (20%) | Rất rõ, có dẫn chứng | 75 trang, số do script sinh, kiểm chéo (`report/kiem_tra_bao_cao.md`) | Thiếu trang nhận xét GVPB (`report/final_src/00_phan_dau.md` chỉ có trang GVHD) |
  | Trình bày (15%) | Trả lời tốt *các* câu hỏi | Kịch bản 18 slide chính (`report/slide/kich_ban_bao_ve.md`) | Kịch bản dài ≈25 phút, quá 15–20 phút thường gặp |
  | Điểm cộng (10%) | Bài báo hoặc ứng dụng thật | Chưa có | Hướng T2 |

- Nếu sửa xong các việc T0/T1 ở mục 4, đề tài có cơ sở nhắm mức 9 theo kiểu rubric HCMUS. Nếu không sửa, các khoảng trống về quá trình,
  trình bày và thực tiễn dễ kéo điểm về 8–8,5. Đây là suy luận, không có dữ liệu điểm thật của IUH.

### Gaps
- Không tìm được phiếu chấm GVHD, GVPB, hội đồng hay rubric của Khoa CNTT IUH cho ngành KHDL. Cũng không tìm được bản trực tuyến của
  "Quy định về việc thực hiện học phần Thực tập doanh nghiệp và Khóa luận tốt nghiệp". Trọng số thật vì vậy chưa biết.
- Chưa có thời lượng trình bày và hỏi đáp chính thức cho đợt 23/12/2026 (khoa ghi sẽ hướng dẫn sau). Chưa biết ngưỡng Turnitin của Khoa
  CNTT; con số 30%/8% là của Khoa Công nghệ Điện.
- Tiêu chí chọn hội đồng hay poster chỉ có cụm "kết quả xuất sắc nhất" (KTPM), không có tiêu chí văn bản. Cũng không rõ poster có trần
  điểm thấp hơn hội đồng hay không.

## 2. Hội đồng Việt Nam hay đặt câu hỏi và phản bác khó nào với khóa luận ML/DS?

### Takeaway
Không có nguồn học thuật nào thống kê câu hỏi của hội đồng ML/DS ở Việt Nam. Nguồn công khai chủ yếu là blog kinh nghiệm, độ tin cậy
thấp. Tuy vậy, chính tiêu chí trong rubric đã định ra các câu khó: "mới hay chỉ cài đặt giải thuật", "so với SOTA", "tính thực tiễn",
"khả năng giải quyết vấn đề của SV", "phối hợp nhóm". Từ 2025 có thêm câu hỏi về việc dùng AI tạo sinh.

### Cited Findings
- Blog lập trình cho sinh viên CNTT nêu các kiểu câu hỏi hay gặp:
  - câu hỏi "tại sao chọn A thay vì B" (ví dụ "Tại sao chọn MongoDB thay vì MySQL cho bài toán này?");
  - câu hỏi về luồng dữ liệu ở mức khái niệm;
  - trả lời kiểu "Em thấy mạng bảo dùng tốt nên dùng" làm điểm giảm mạnh;
  - mỗi thành viên phải nắm phần mình làm;
  - lỗi môi trường (chạy được trên máy mình nhưng hỏng trên máy khác).

  — [codesinhvien.vn (blog/tổng hợp)](https://codesinhvien.vn/bao-ve-do-an-tot-nghiep-it-loi-de-toang/)
- FUNiX khuyên "nắm chắc source code" và tập canh giờ để không vượt thời lượng. — [FUNiX (blog/tổng hợp)](https://funix.edu.vn/chia-se-kien-thuc/kinh-nghiem-bao-ve-do-an-tot-nghiep-funix/)
- Câu hỏi thường xoay quanh lý do chọn đề tài, phương pháp, kết quả và đề xuất ứng dụng; thường có 3–7 câu hỏi chính (đoạn trích). —
  [kiemtratailieu.vn (blog/tổng hợp)](https://kiemtratailieu.vn/blog/nhung-cau-hoi-thuong-gap-khi-bao-ve-khoa-luan-tot-nghiep/)
- Rubric HCMUS đặt sẵn câu phản bác "chỉ áp dụng mô hình có sẵn" ở mức 7–9: "Bài toán hoặc giải pháp không mới (như cài đặt giải thuật),
  nhưng có đánh giá, so sánh tốt". Mức 9–10 đòi "Kết quả tốt so với các giải pháp tốt nhất (state of the art)". — [HCMUS-FIT rubric v4](https://www.ctda.hcmus.edu.vn/wp-content/uploads/2024/07/Khoa-CNTT-Tieu-chi-va-bieu-mau-cham-diem-tot-nghiep-v4-20230627-1.pdf)
- UIT yêu cầu nhận xét "tính mới, tính khoa học, tính sáng tạo, tính thực tiễn" và "khả năng… giải quyết vấn đề của SV". Đó là gốc của
  các câu hỏi về thực tiễn và câu hỏi kiểm tra từng SV. — [UIT 159/QĐ-ĐHCNTT](https://student.uit.edu.vn/sites/daa/files/202410/159-qd-dhcntt_05-03-2024_ban_hanh_quy_dinh_kltn.pdf)
- Về AI tạo sinh:
  - HCMUS cho phép dùng nhưng SV phải là tác giả và chịu trách nhiệm ([HCMUS-FIT](https://www.ctda.hcmus.edu.vn/wp-content/uploads/2024/07/Khoa-CNTT-Tieu-chi-va-bieu-mau-cham-diem-tot-nghiep-v4-20230627-1.pdf)).
  - UEH có quy định riêng về kiểm soát đạo văn và dùng AI trong sản phẩm học thuật; theo đoạn trích, vi phạm có thể làm khóa luận không
    đạt ([UEH](https://daotao.ueh.edu.vn/quy-dinh-ve-viec-kiem-soat-xu-ly-hanh-vi-dao-van-su-dung-tri-tue-nhan-tao-ai-trong-cac-san-pham-hoc-thuat-tai-dai-hoc-kinh-te-thanh-pho-ho-chi-minh/)).
  - Khoa CNTT NEU hướng dẫn khai báo công cụ, mục đích và mức độ dùng AI (đoạn trích) ([NEU-FIT](https://fit.neu.edu.vn/post/huong-dan-sinh-vien-su-dung-ai-trong-hoc-tap-dung-liem-chinh-hoc-thuat)).
  - Báo chí đưa tin các đại học "siết" dùng AI tạo sinh (đoạn trích) ([VnExpress](https://vnexpress.net/sinh-vien-dai-hoc-hang-dau-bi-siet-dung-ai-tao-sinh-4830016.html)).

### Inferences
Đây là danh sách tổng hợp. Mỗi câu suy từ một tiêu chí rubric hoặc từ blog ở trên, chưa có nguồn thống kê tần suất:
1. "Đóng góp của nhóm là gì, hay chỉ ghép mô hình có sẵn?" (tiêu chí Đóng góp, mức 7–9 của HCMUS).
2. "Kết quả thấp vậy thì dùng được không?" (tính thực tiễn, triển vọng).
3. "Đã so với phương pháp khác hoặc SOTA chưa?" (mức 9–10 của HCMUS).
4. "Dữ liệu ở đâu ra, nhãn có tin được không, có rò rỉ không, chia tập thế nào?" (tính khoa học).
5. "Dữ liệu nước ngoài thì áp dụng ở Việt Nam thế nào?" (tính thực tiễn).
6. "Tại sao chọn X mà không chọn Y?" (blog; khả năng giải quyết vấn đề).
7. "Có quá khớp, có chọn mô hình theo test không?" (tính khoa học).
8. "Sao phải dùng LLM/RAG? Sao không gọi thẳng GPT-4o/Gemini?" (lý do chọn công nghệ).
9. "Kết quả âm tính thì đề tài có thất bại không?" (đáp ứng mục tiêu).
10. "Hai người phân công thế nào?" Hội đồng có thể hỏi riêng từng người (UIT Điều 5.3; UIT và UED chấm theo từng SV).
11. "Demo có chạy thật không, thử file của thầy được không?" (mức độ hoàn thành).
12. "Có dùng AI viết code hay báo cáo không?" (liêm chính, chính sách AI).
13. Câu hỏi định nghĩa: giải thích chỉ số, công thức, thuật toán.
14. "Hạn chế lớn nhất là gì? Nếu làm lại thì sửa gì?"

### Gaps
- Không tìm được biên bản hay bản ghi câu hỏi thật của hội đồng KHDL ở IUH, cũng không có bài viết của giảng viên IUH về chủ đề này.
- Các nguồn tiếng Việt về "câu hỏi thường gặp" phần lớn là trang dịch vụ, không kiểm chứng được. Chỉ dùng để tham khảo khuôn câu hỏi.

## 3. Trình bày kết quả âm tính (RQ1), đóng góp "áp dụng và mở rộng" và khối lượng công việc thế nào cho thuyết phục?

### Takeaway
Nên trình bày RQ1 như một câu hỏi đã được *trả lời*: thiết kế đúng cặp so sánh, nhiều seed, và khoảng tin cậy **đặt cận trên** cho lợi
ích của DataSEC (không quá khoảng +0,02 event-F1 micro). Kết quả âm tính này lại dẫn tới chẩn đoán lỗi và LBR. Với tính mới, chính
rubric HCMUS coi "áp dụng giải thuật sẵn có trên bộ dữ liệu mới" kèm so sánh công phu là tính mới mức 9–10. DataSED chưa có kết quả
SED công bố nào, nên đề tài đưa ra mốc tham chiếu tái lập được. Câu này không mâu thuẫn với lệnh cấm dùng chữ "lần đầu". Khối lượng
công việc nên đưa lên một slide toàn số đếm được, kèm nhật ký và phân công.

### Cited Findings
- Karl và cs. (2024), "Position: Embracing Negative Results in Machine Learning", lập luận rằng hiệu năng dự đoán một mình không phải
  thước đo tốt cho giá trị của công bố, và việc bỏ qua kết quả âm tính gây thiên lệch công bố. — [arXiv 2406.03980](https://arxiv.org/abs/2406.03980)
- Chuỗi workshop ICBINB ("I Can't Believe It's Not Better") cổ vũ "slow science", thảo luận kết quả bất ngờ và âm tính, và coi trọng
  công trình thực nghiệm chặt chẽ dù không đề xuất phương pháp mới (tóm tắt từ trang workshop qua máy tìm kiếm). —
  [NeurIPS 2022 ICBINB](https://neurips.cc/virtual/2022/workshop/49960); [ICLR 2025 ICBINB](https://iclr.cc/virtual/2025/workshop/23987)
- Rubric HCMUS: tính mới mức 9–10 "bao gồm việc áp dụng giải thuật sẵn có trên bộ dữ liệu mới"; mức 9–10 có "đánh giá, so sánh công
  phu". Mẫu hướng ứng dụng chấm "Độ lớn/phức tạp của công việc" 20%. — [HCMUS-FIT rubric v4](https://www.ctda.hcmus.edu.vn/wp-content/uploads/2024/07/Khoa-CNTT-Tieu-chi-va-bieu-mau-cham-diem-tot-nghiep-v4-20230627-1.pdf)
- Mẫu IUH yêu cầu chương Kết luận nêu "những điều làm được, chưa làm được… ưu nhược điểm, hạn chế". Chương đánh giá phân tích "những
  mặt mạnh yếu của hệ thống". — `report/Mau bao cao KLTN_DS.docx`
- Số liệu RQ1:
  - Công thức v1, 7 lần chạy sạch: C − B = −0,0071 [−0,0164; +0,0021], Welch p = 0,2336.
  - Công thức v2: C − B = −0,0029 [−0,0254; +0,0199], p = 0,6965.
  - Tiền huấn luyện nói chung giúp rõ: nhánh A học từ đầu đạt 0,0360 so với 0,0621 của nhánh B.
  - PSDS-2 v2 tăng +0,0279, p = 0,0193, chưa hiệu chỉnh so sánh bội.

  — `report/final_src/06_ket_qua.md`; `docs/decisions/ADR-0021-rq1-ket-qua-am-tinh.md`
- Báo cáo đã giữ nguyên nhiều kết quả kém đi khác: ECE tăng sau hiệu chuẩn (0,0332 → 0,0564); PSDS không tăng từ v1 sang v2; f2 không
  được gọi là tốt hơn v2; B0 hơn f2 không có ý nghĩa (+0,0164 [−0,0128; +0,0495]); giai đoạn P thử bốn hướng, không hướng nào vượt B0;
  LBR làm giảm PSDS-2 và độ phủ. — `report/final_src/06_ket_qua.md`; `report/kiem_tra_bao_cao.md` §4
- Claim về tính mới đã được hạ sau đợt tra văn liệu 11/2026, vì có ECHO/TAC (đo ảo giác của mô tả âm thanh), Weck & Serra (trùng trong
  một bộ), LA-RAG (event store SQL kèm RAG). — `report/final_src/01_gioi_thieu.md` (bảng đóng góp); `report/final_src/07_ket_luan.md`
- Đến 09/11/2026 "vẫn chưa có bài nào báo số SED event-based trên DataSED". PolyBench chỉ dùng 169 clip DataSED cho hỏi đáp của mô
  hình âm thanh–ngôn ngữ lớn (LALM). — `docs/RELATED_WORK.md` (nhật ký tra cứu 09/11 và mục (24))
- Số đếm khối lượng, đo trên repo ngày 23/11/2026:
  - 397 commit (22/09/2026 → 11/11/2026), đếm bằng `git rev-list --count HEAD`;
  - 48 ADR trong `docs/decisions/`, 488 tệp trong `docs/measurements/`;
  - 144 tệp kiểm thử chứa 873 hàm `def test_`; pytest 747 pass, 4 skip tại 03/10/2026 (`report/kiem_tra_bao_cao.md`);
  - khoảng 54,5 nghìn dòng Python và 1,1 nghìn dòng TS/TSX, đếm thô bằng `wc`, chưa loại dòng trống hay chú thích;
  - báo cáo cuối 75 trang, khoảng 17,7 nghìn từ, theo `docProps/app.xml` của `report/Khoa_luan_environmental_audio_rag.docx`.
- Dữ liệu: DataSEC 5.048 tệp, 23,71 giờ; DataSED 717 bản ghi, 18,68 giờ, 4.034 sự kiện đa âm, 21 lớp. — `report/final_src/03_du_lieu.md`

### Inferences
- **Câu chốt cho RQ1** (lời văn đề xuất): "Nhóm ghi trước giả thuyết và cặp so sánh đúng là C với B. Với hai công thức và nhiều seed,
  khoảng tin cậy chứa 0. Cận trên +0,0021 (v1) và +0,0199 (v2) nghĩa là nếu DataSEC có giúp thì mức giúp không quá khoảng 0,02 event-F1
  micro. Ngược lại, tiền huấn luyện AudioSet giúp gần gấp đôi (0,036 → 0,062). Kết quả này cho người làm sau một chỉ dẫn rõ: nên đầu tư
  vào tiền huấn luyện và vào xử lý biên, không phải vào thêm dữ liệu clip cùng miền. Đó cũng là hướng nhóm đã đi, dẫn tới LBR."
  Không nói "thất bại" hay "không thành công". Nói "không có bằng chứng cải thiện, và lợi ích nếu có thì bị chặn trên ở mức nhỏ".
- **Chuỗi khám phá nên kể trên slide:** RQ1 âm tính → chẩn đoán (lỗi ở biên và bỏ sót: 357/886 bỏ sót, 417 lệch biên) → v2 tăng độ
  phân giải thời gian → chọn bằng dự đoán ngoài mẫu (dev đảo chiều) → LBR (+0,116). Câu chuyện này đổi "âm tính" thành "điểm rẽ có
  căn cứ" và chứng minh "khả năng xử lý vấn đề của SV", đúng tiêu chí UIT Điều 13.1.
- **Diễn đạt "áp dụng và mở rộng" mà không tự hạ thấp:** dùng "áp dụng có kiểm chứng, và mở rộng ở X". X cụ thể:
  - C2 thêm thứ tự, từ cấm và khoảng tin cậy;
  - C3 kiểm trùng xuyên hai bộ dữ liệu bằng dấu vân âm thanh;
  - C4 điều kiện quan hệ giữa hai sự kiện, thay cho cửa sổ thời gian tuyệt đối của LA-RAG;
  - LBR, tầng hậu xử lý học được, tăng 1,6 lần.

  Thêm câu có phạm vi: "Trong phạm vi tra cứu đến 11/2026, nhóm chưa thấy kết quả SED theo sự kiện nào được công bố trên DataSED, nên
  B0 và LBR là mốc tham chiếu tái lập được (mã, tập chia khóa băm, sổ test)." Câu này chỉ nói không thấy mốc so sánh. Báo cáo cũng đã ghi
  điều đó là một hạn chế (`report/final_src/06_ket_qua.md`). Câu này không khẳng định "lần đầu".
- **Làm lộ khối lượng:** dùng một slide toàn số đếm được (xem bản nháp ở mục 5), một dải thời gian (W1–W7 → S13 → giai đoạn O → giai
  đoạn P → LBR → R1–R7), và nêu các sản phẩm kỹ thuật: Docker Compose, hợp đồng JSON Schema, kiểm thử CI chặn PyTorch trong API, sổ test,
  đóng băng artifact. Theo rubric HCMUS, khối lượng còn được chấm qua "Quá trình thực hiện", nên nhật ký tuần 5–7 còn trống làm yếu
  luận điểm khối lượng.

### Gaps
- Không tìm được nguồn tiếng Việt nói về thái độ của hội đồng trong nước với kết quả âm tính. Cách trình bày ở trên dựa trên tài liệu ML
  quốc tế và rubric.
- Số dòng mã là đếm thô. Nên đếm lại bằng `cloc`, loại tệp sinh tự động, trước khi đưa lên slide.
- Chưa có số liệu đóng góp của từng thành viên. Repo không ghi phân công (tìm "phân công" trong `report/` chỉ thấy quyết định trình bày
  của bản giữa kỳ).

## 4. Ngân hàng 27 câu hỏi dự kiến cho đề tài này: dàn ý trả lời, bằng chứng, đánh giá và việc cần bổ sung

### Takeaway
Trong 27 câu, có **9 câu đã có câu trả lời tốt**, **16 câu trả lời được nhưng yếu**, **2 câu chưa có câu trả lời** (phân công nhóm, dùng
AI). Năm rủi ro lớn nhất:
1. Chưa có phân công hai thành viên.
2. Chưa có cách trả lời câu hỏi về việc dùng AI. Repo có `AGENTS.md`, `CLAUDE.md`, `HANDOFF_CODEX.md`, `docs/AGENT_SYNC.md`, nên ai xem
   mã nguồn cũng sẽ thấy.
3. Kịch bản trình bày dài khoảng 25 phút.
4. Tính thực tiễn ở Việt Nam không có trong báo cáo cuối, dù dữ liệu cho góc nhìn 19 lớp Việt Nam đã có trong tệp đo.
5. Bảng đóng góp không có LBR, và LBR chưa được định vị so với công trình học biên đã có.

### Cited Findings
Mỗi câu ghi: câu hỏi theo giọng thành viên hội đồng, vì sao họ hỏi, dàn ý trả lời kèm tệp bằng chứng, và đánh giá.

#### Nhóm A: đóng góp và tính mới

**Q1. "Đóng góp thật sự của nhóm là gì? Nghe như các em ghép CNN14, BEATs, Qwen, BGE-M3, pgvector có sẵn lại với nhau."**
- *Vì sao hỏi:* đây là câu phản bác chuẩn; rubric HCMUS xếp "cài đặt giải thuật" vào mức 7–9.
- *Dàn ý:*
  1. Nhóm không huấn luyện mô hình nền mới. Đóng góp nằm ở các mắt xích nhóm tự thiết kế và đo được.
  2. LBR nâng event-F1 micro trên test từ 0,1806 lên 0,2965, Δ +0,1159 [+0,0741; +0,1593] (`report/final_src/06_ket_qua.md`;
     `docs/decisions/ADR-0045-lbr-tinh-chinh-bien-va-cham-lai-box.md`).
  3. Ngữ pháp giải mã đưa ảo giác, suy diễn bối cảnh và từ cấm về 0 ở cả bốn hệ SED; biến thể cover còn đưa bỏ sót về 0
     (`report/final_tables/f04_rq2.md`).
  4. Kiểm trùng xuyên bộ: tìm ra 3 nhóm trùng, loại 11 đoạn (`report/final_src/03_du_lieu.md`).
  5. Bốn điều kiện thời gian viết bằng SQL: bộ lọc đúng 100%, không có khẳng định thiếu bằng chứng.
  6. DataSED chưa có mốc SED công bố, nên đề tài là mốc tham chiếu tái lập được (`docs/RELATED_WORK.md`).
- *Đánh giá:* **trả lời được nhưng yếu.** Bảng C1–C4 (`report/final_src/01_gioi_thieu.md`) không có LBR, trong khi LBR là kết quả số
  lớn nhất; slide 3 lại mở đầu bằng việc hạ claim. *Cần thêm:* slide "Nhóm làm gì mới" có LBR và con số, kèm câu trả lời 30 giây
  (T1, khoảng 1 giờ).

**Q2. "LBR có gì mới? Học tinh chỉnh biên sự kiện thì đã có người làm rồi."**
- *Vì sao hỏi:* LBR là điểm tăng chính; ai quen DCASE sẽ hỏi ngay.
- *Dàn ý:*
  1. LBR xuất phát từ phân tích lỗi của B0: hơn nửa số sự kiện bị bỏ sót có xác suất khung từ 0,9 trở lên nhưng hộp bị loại, và onset
     dự đoán sớm có hệ thống (`report/final_src/04_phuong_phap.md`).
  2. LBR gồm hai mô hình boosting học lồng nhau trên xác suất ngoài mẫu: bộ tinh chỉnh dịch biên hộp, bộ chấm lại ước lượng hộp có
     đúng không. Đây là hậu xử lý, không huấn luyện lại encoder.
  3. Khác Boundary-Aware (Schmid và cs., 2026), vốn học biên ngay trong mạng (CRNN PSDS1 41,1 → 48,0 trên AS-Strong), và khác các hướng
     hồi quy onset/offset cũ (Phan và cs. 2014–2015; YOHO 2022) (`docs/RELATED_WORK.md`, bảng nguồn và nhật ký 09/11).
  4. Claim nên nói: "áp dụng ý tưởng hồi quy biên ở dạng hậu xử lý, không phụ thuộc mô hình, kiểm chứng trên DataSED".
- *Đánh giá:* **trả lời được nhưng yếu.** Chương 2 không định vị LBR; Phan và YOHO mới ở mức V1 (chưa đọc). *Cần thêm:* đọc tóm tắt ba
  nguồn và viết một đoạn ở Chương 2 (T0, 1–2 giờ, nếu báo cáo còn sửa được), hoặc làm slide dự phòng (T1, 1 giờ).

**Q3. "Báo cáo tự nhận 'áp dụng và mở rộng', không phải 'lần đầu'. Vậy tính mới nằm ở đâu?"**
- *Dàn ý:*
  1. Nhóm tra văn liệu tháng 11/2026 và trình bày trung thực vì đã có ECHO/TAC, Weck & Serra, LA-RAG (`report/final_src/01_gioi_thieu.md`).
  2. Phần "mở rộng" cụ thể: C2 thêm thứ tự, từ cấm, khoảng tin cậy; C3 kiểm trùng xuyên hai bộ bằng dấu vân; C4 điều kiện quan hệ giữa
     hai sự kiện (`report/final_src/02_co_so_ly_thuyet.md`).
  3. Rubric kiểu HCMUS coi việc áp dụng giải thuật có sẵn trên bộ dữ liệu mới, kèm so sánh công phu, là tính mới.
- *Đánh giá:* **đã có câu trả lời tốt.** Tập một bản 20 giây. Tránh nói "chỉ là áp dụng".

**Q4. "So với LA-RAG và các hệ event store + RAG đã có thì hệ của các em khác gì?"**
- *Dàn ý:*
  1. LA-RAG đổi biểu thức thời gian tuyệt đối thành cửa sổ thời gian (`report/final_src/02_co_so_ly_thuyet.md`).
  2. Đề tài làm điều kiện quan hệ giữa hai lớp trong cùng bản ghi. Mỗi điều kiện viết một lần bằng SQL và một lần bằng Python, có kiểm
     thử đối chiếu trên SQLite (`report/final_src/04_phuong_phap.md`).
  3. Đề tài có đo nDCG@10, độ đúng bộ lọc và khẳng định thiếu bằng chứng trên 100 truy vấn chọn trước khi xem kết quả.
  4. Chưa so trực tiếp với LA-RAG trên cùng bộ truy vấn; đây là hướng phát triển (`report/final_src/07_ket_luan.md`).
- *Đánh giá:* **trả lời được nhưng yếu.** *Cần thêm:* slide dự phòng ba dòng khác biệt (T1, 30 phút); so sánh trực tiếp để T2.

#### Nhóm B: dữ liệu và kỷ luật đánh giá

**Q5. "Dữ liệu là của nhóm tác giả nước ngoài. Ở Việt Nam có xe máy, còi xe, karaoke. Áp dụng thế nào?"**
- *Dàn ý:*
  1. Mô hình tách khỏi pipeline: thay hoặc tinh chỉnh SED bằng dữ liệu Việt Nam mà không phải đổi phần mô tả và truy hồi (hợp đồng JSON
     Schema, `report/final_src/05_trien_khai.md`).
  2. ADR-0046 có góc nhìn 19 lớp Việt Nam, bỏ máy bay cánh quạt và nhóm quạ/mòng biển/ác là. Kết quả đo trong cùng lượt mở test: B0
     micro 0,1892, LBR V2 0,3120; V3 `recall_first` phát hiện được 0,8319 số sự kiện ở mức giao nhau, precision 0,7810
     (`docs/measurements/sed_ensemble_B0_final_test_20261014T085016Z_eval_phase_lbr_annotated.md`;
     `docs/decisions/ADR-0046-thuoc-ung-dung-va-tap-lop-viet-nam.md`).
  3. Nói thẳng: chưa có bản ghi Việt Nam, nên lệch miền chưa được đo.
- *Đánh giá:* **trả lời được nhưng yếu.** Báo cáo cuối không nhắc "Việt Nam" lần nào (tìm trong `report/final_src/` không có kết quả).
  ADR-0046 tự ghi tiêu chí "hiếm ở Việt Nam" là nhận định, không có số đo tần suất. *Cần thêm:*
  - T0, 45–60 phút: đoạn "ý nghĩa thực tiễn ở Việt Nam" và số 19 lớp. Số đã có trong tệp đo nên không phải chạm test lại.
  - T1, 2 giờ, tùy chọn: chạy demo trên 3–5 đoạn tự thu ở TP.HCM, chỉ để minh họa định tính.
  - T2: bộ dữ liệu thí điểm Việt Nam.

**Q6. "Hai bộ dữ liệu cùng tác giả, các em có chắc test không bị rò rỉ không?"**
- *Dàn ý:*
  1. Kiểm trùng ba tầng. Ngưỡng hiệu chuẩn trên 24 cặp giống hệt byte và 5.000 cặp ngẫu nhiên.
  2. Tìm ra 3 nhóm trùng; hai cặp giống hoàn toàn trên đoạn 35 s và 13 s (ví dụ `Sirens-0046` với `S-0233`).
  3. Duyệt tay 35 cặp mơ hồ, loại 11 đoạn DataSEC (0,22%).
  4. Chia tập theo `leakage_group`; cổng D4 kiểm năm điều kiện; tập chia khóa bằng mã băm (`report/final_src/03_du_lieu.md`).
  5. Câu hỏi phụ có thể gặp: "Dùng DataSEC bản 3, sao không dùng bản 4?" Bản 4 chỉ sửa số tệp lớp Music; ảnh hưởng chưa đo; đã ghi
     là hạn chế (`report/final_src/06_ket_qua.md`, `report/final_src/07_ket_luan.md`).
- *Đánh giá:* **đã có câu trả lời tốt.**

**Q7. "Test chỉ 139 bản ghi. Làm sao chứng minh các em không chọn mô hình theo test? Mà sao có 10 lượt đánh giá bị gắn cờ dirty?"**
- *Dàn ý:*
  1. Test chỉ mở một lần cho mỗi cấu hình đã khóa; sổ ghi đủ 42 lượt đánh giá SED (`docs/measurements/test_ledger_20261111.md`;
     slide phụ lục 21).
  2. Ở vòng S13, f1 có micro test cao nhất (0,1817) nhưng nhóm không chọn lại.
  3. Xếp hạng trên dev không đáng tin: 3 ứng viên đảo chiều khi đo ngoài mẫu trên 564 bản ghi, nên nhóm đổi cách chọn.
  4. Khoảng tin cậy bootstrap theo bản ghi.
  5. Cờ dirty: 10/42 lượt có cờ do chính script sinh tệp báo cáo chưa commit; mã và cấu hình không đổi (`report/final_src/06_ket_qua.md`).
- *Đánh giá:* **đã có câu trả lời tốt.** Nên in sẵn một trang sổ test.

#### Nhóm C: kết quả và so sánh

**Q8. "Event-F1 chỉ khoảng 0,30, thấp vậy dùng được không? Sao không dùng collar 1 s cho điểm cao hơn?"**
- *Dàn ý:*
  1. Collar 0,2 s chặt hơn độ chính xác của chính nhãn: hai người gán nhãn chỉ khớp nhau 0,5785 (8 cặp bản ghi). Nếu ra quyết định
     theo khối 0,64 s thì trần là 0,6294.
  2. Trên thước ứng dụng, V3 phát hiện 0,8203 số sự kiện với precision 0,7812; segment-F1 1 s là 0,7821.
  3. Trên cùng tập annotated, micro tăng từ 0,0945 (v1) lên 0,2965 (V2), khoảng 3,1 lần.
  4. Đổi thước sau khi xem số là sai quy trình, nên thước chính giữ nguyên và thước ứng dụng chỉ báo kèm
     (`docs/decisions/ADR-0046-thuoc-ung-dung-va-tap-lop-viet-nam.md`; `report/final_src/06_ket_qua.md`).
- *Đánh giá:* **đã có câu trả lời tốt.** *Cần thêm:* một slide "thước chặt, trần người, thước ứng dụng" (T1, 45 phút).

**Q9. "Các em so với phương pháp khác hoặc SOTA chưa? Baseline DCASE thì sao?"**
- *Dàn ý:*
  1. Chưa có kết quả SED công bố trên DataSED; PolyBench chỉ dùng clip DataSED cho hỏi đáp của LALM (`docs/RELATED_WORK.md`).
  2. So sánh nội bộ nhiều tầng: ba nhánh A/B/C; chuỗi v1 → v2 → f2 (11 ứng viên ghi trước, có BEATs đóng băng) → B0 → LBR; bốn cách
     sinh mô tả; ba chế độ truy hồi.
  3. Số trên DESED không so được với đề tài vì khác lớp và khác dữ liệu.
- *Đánh giá:* **trả lời được nhưng yếu**, vì không có mốc ngoài. *Cần thêm:* slide "thang so sánh nội bộ" (T1); chạy baseline DCASE hoặc
  PretrainedSED trên DataSED để T2.

**Q10. "RQ1 âm tính, vậy phần học chuyển giao là thất bại? Huấn luyện DataSEC để làm gì?"**
- *Dàn ý:* dùng câu chốt ở mục 3: cận trên +0,02; tiền huấn luyện AudioSet giúp gấp đôi; kết quả âm tính dẫn tới LBR. Mô hình phân loại
  DataSEC tự nó là một sản phẩm (macro-F1 0,8466) (`report/final_src/06_ket_qua.md`; ADR-0021; [Karl và cs. 2024](https://arxiv.org/abs/2406.03980)).
- *Đánh giá:* **đã có câu trả lời tốt.** Thêm câu "kết quả này có ích cho ai" vào slide 7.

**Q11. "PSDS-2 của v2 tăng với p = 0,0193, sao không kết luận DataSEC có giúp?"**
- *Dàn ý:*
  1. Chỉ số chính ghi trước là event-F1. PSDS-2 là một trong ít nhất bốn chỉ số được so (micro, macro, PSDS-1, PSDS-2).
  2. Hiệu chỉnh Bonferroni cho 4 chỉ số cho ngưỡng 0,05/4 = 0,0125, nên p = 0,0193 không còn ý nghĩa; Holm cho cùng kết luận. Nếu chỉ
     có 3 chỉ số thì ngưỡng là 0,0167, kết luận vẫn vậy. Phép tính này là suy luận trên số trong `report/final_src/06_ket_qua.md`.
  3. Nhóm vẫn báo nguyên p chưa hiệu chỉnh.
- *Đánh giá:* **trả lời được nhưng yếu.** Có câu Bonferroni thì thành tốt (T1, 10 phút). Kiểm lại đúng số chỉ số đã kiểm định ở v2.

**Q12. "LBR V2 tăng F1 nhưng PSDS-2 và độ phủ lại giảm. Vậy LBR có thật sự tốt hơn không? Sao demo lại dùng V3?"**
- *Dàn ý:*
  1. Hai điểm vận hành cho hai mục đích.
  2. V2 cho biên chặt: precision giao nhau 0,9545 nhưng recall 0,5108, segment-F1 0,5965 so với 0,7260 của B0.
  3. V3 `recall_first` cho ít bỏ sót: sàn precision 0,6 ghi trước, đạt recall 0,8203 và precision 0,7812.
  4. Trên lưới log, PSDS-1/PSDS-2 là V2 0,3512 / 0,6116 so với B0 0,3061 / 0,7452: LBR đổi độ phủ lấy độ chính xác biên.
  5. Cả hai cấu hình đều khóa trước khi mở test (`report/final_src/06_ket_qua.md`; ADR-0045 §11).
- *Đánh giá:* **đã có câu trả lời tốt**, nhưng phức tạp; cần tập bản 30 giây.

**Q13. "F1 tăng 1,6 lần mà nDCG gần như không tăng. Vậy cải tiến SED có ích gì cho người dùng?"**
- *Dàn ý:*
  1. nDCG@10 của hybrid tiếng Anh: f2 0,415, B0 0,383, V2 0,404; khoảng tin cậy chồng nhau.
  2. V3 đạt 0,670 nhờ độ phủ: trả lời được 95/97 câu so với 58–65 của ba hệ kia. Cái giá là tỷ lệ trích đúng giảm từ 0,915 xuống 0,712
     (`report/final_tables/f05_rq3.md`).
  3. Kết luận: truy hồi bị chặn bởi việc SED dự đoán sự kiện nào. Ứng dụng tìm kiếm nên dùng điểm vận hành ưu tiên phát hiện.
- *Đánh giá:* **đã có câu trả lời tốt.**

**Q14. "Bảng RQ3 cho thấy vector_only có nDCG cao hơn hybrid (B0: 0,458 so với 0,383). Lọc cứng làm hại à? Sao lại chọn hybrid?"**
- *Dàn ý:*
  1. Trên kho B0, hybrid − vector_only (tiếng Anh) = −0,075 [−0,121; −0,028], có ý nghĩa. Nhưng chỉ 0,271 kết quả của vector_only
     thỏa đủ ràng buộc cứng, tức hơn 70% kết quả vi phạm điều câu hỏi đòi
     (`docs/measurements/retrieval_benchmark_test_s8lite_b0_gold_20261108.md`).
  2. Độ liên quan tính từ nhãn gốc, nên khi SED bỏ sót, lọc cứng loại nhầm bản ghi thật sự liên quan.
  3. Với V3 độ phủ cao thì hybrid thắng: +0,040 [+0,004; +0,079] tiếng Anh, +0,090 [+0,046; +0,137] tiếng Việt; vector_only vẫn chỉ đúng
     bộ lọc 0,493 (`docs/measurements/retrieval_benchmark_test_lbrv3_gold_20261110.md`).
  4. Chọn hybrid để có bảo đảm đúng ràng buộc và trích được bằng chứng.
- *Đánh giá:* **trả lời được nhưng yếu.** Chương 6 không nêu rõ đánh đổi này. *Cần thêm:* một câu ở Chương 6 (T0, 15 phút) hoặc slide
  dự phòng (T1, 30 phút).

**Q15. "Lớp vehicle_pass_by có 70 sự kiện mà F1 bằng 0. Đây lại là lớp phổ biến nhất ở Việt Nam."**
- *Dàn ý:*
  1. Với V2 có 3 lớp F1 bằng 0: `birds`, `vehicle_idling`, `vehicle_pass_by` (`report/final_src/06_ket_qua.md`; slide phụ lục 20).
  2. Hai lớp xe nghe rất giống nhau; ngay cả bộ phân loại cũng yếu nhất ở đây (F1 0,6154 và 0,6538).
  3. Tiếng xe chạy qua tăng và giảm dần nên khó định biên trong collar 0,2 s.
  4. Thử gộp lớp dễ nhầm chỉ thêm +0,002 micro OOF (ADR-0046, phương án 4).
- *Đánh giá:* **trả lời được nhưng yếu.** *Cần thêm:* phân tích lỗi trên OOF hoặc dev, với 2–3 dòng thời gian ví dụ (T1, 1–2 giờ). Không
  dùng test.

#### Nhóm D: thiết kế LLM và RAG

**Q16. "Tại sao phải dùng LLM và RAG? Lọc SQL theo lớp và thời gian là đủ rồi."**
- *Dàn ý:*
  1. Thừa nhận SQL thuần rất mạnh: structured 0,683 so với hybrid 0,670 trên V3, và 0,416 so với 0,415 trên f2
     (`report/final_tables/f05_rq3.md`). SQL là phần bảo đảm đúng.
  2. LLM làm ba việc: dịch câu hỏi tự nhiên tiếng Việt và tiếng Anh thành bộ lọc (240/240 câu hợp lược đồ; đúng hoàn toàn 0,855 với câu
     mẫu và 0,925 với câu diễn đạt lại; lỗi chính ở điều kiện thời gian, 0,767); xếp hạng ngữ nghĩa trong tập đã lọc; viết câu trả lời có
     trích bằng chứng, không có khẳng định thiếu bằng chứng (`report/final_src/06_ket_qua.md`).
  3. Người dùng không cần biết SQL hay 21 tên lớp.
- *Đánh giá:* **trả lời được nhưng yếu.** Chưa đo lợi ích cho người dùng so với một form lọc thủ công. *Cần thêm:* slide "SQL làm gì, LLM
  làm gì" (T1, 45 phút); nghiên cứu người dùng nhỏ để T2.

**Q17. "Sao không cho Gemini, GPT-4o hay Qwen2-Audio nghe thẳng bản ghi rồi trả lời?"**
- *Dàn ý:*
  1. Mô hình âm thanh–ngôn ngữ lớn bị ảo giác đối tượng (ECHO, Kuan và cs. 2024, [arXiv 2406.08402](https://arxiv.org/abs/2406.08402),
     xem `docs/RELATED_WORK.md`).
  2. Hiệu năng giảm trong âm thanh đa âm: PolyBench (Interspeech 2026, dùng clip DataSED) ghi nhận "consistent performance degradation
     in polyphonic settings" ([arXiv 2603.05128](https://arxiv.org/abs/2603.05128)).
  3. Câu hỏi về lịch sử cần mốc thời gian và một kho dữ liệu. Nếu dùng LALM thì mỗi câu hỏi phải nghe lại toàn bộ âm thanh; hệ thống của
     nhóm lập chỉ mục một lần, truy vấn hybrid mất 0,273 s (`docs/measurements/demo_lbrv3_e2e_20261110.md`).
  4. Hệ thống chạy ngoại tuyến trên laptop RTX 3070 8 GB (theo các tệp đo trong `docs/measurements/`), không gửi âm thanh ra ngoài.
  5. Nói thẳng: nhóm chưa chạy LALM làm mốc so sánh.
- *Đánh giá:* **trả lời được nhưng yếu.** *Cần thêm:* slide dự phòng dựa trên tài liệu (T1, 30 phút). Nếu còn thời gian, thử một LALM mã
  mở trên khoảng 20 bản ghi dev, đo bằng cùng bộ đo (T1 tùy chọn, 4–8 giờ, chỉ khi vừa 8 GB VRAM); mốc so sánh đầy đủ để T2.

**Q18. "Ràng buộc ngữ pháp thì ảo giác bằng 0 là hiển nhiên. Template cũng bằng 0. Vậy cần LLM làm gì?"**
- *Dàn ý:*
  1. RQ2 đo cái giá chứ không chỉ đo con số 0.
  2. Viết tự do thêm bối cảnh không có trong bằng chứng ở 0,259–0,403 số mô tả và gọi tên quá cụ thể ở 0,126–0,140.
  3. Ràng buộc trả giá bằng bỏ sót khi danh sách sự kiện dày: V3 0,081, hiệu +0,069 [+0,041; +0,097]; biến thể cover đưa về 0.
  4. Template là mốc để kiểm rằng bộ đo không báo lỗi giả (`report/final_src/06_ket_qua.md`).
  5. LLM viết câu tự nhiên hơn template, nhưng điều này chưa được đo.
- *Đánh giá:* **trả lời được nhưng yếu.** *Cần thêm:* chấm độ dễ đọc kiểu mù, 20–30 mô tả dev, so template với constrained-cover, 2–3
  người ngoài nhóm (T1, 2–3 giờ); hoặc nêu rõ là hạn chế.

**Q19. "Bộ đo dựa trên từ điển, chỉ một người đọc 60 mô tả. Có đáng tin không?"**
- *Dàn ý:*
  1. So với người đọc, từ điển đạt precision 0,896 và recall 0,936.
  2. Template cho 0 lỗi, xác nhận bộ đo không báo lỗi giả.
  3. Lỗi đã biết: "tiếng búa gõ" bị che sau từ "xưởng" (`report/final_src/06_ket_qua.md`).
  4. Đã ghi là hạn chế; hướng phát triển là nhiều người đọc và chỉ số FLAM (`report/final_src/07_ket_luan.md`).
- *Đánh giá:* **trả lời được nhưng yếu.** *Cần thêm:* một người đọc thứ hai, ngoài nhóm, chấm lại cùng 60 mô tả để tính Cohen κ, không
  dùng để chọn lại cấu hình (T1, 2 giờ). Nên ưu tiên mô tả dev nếu quy tắc dự án yêu cầu.

#### Nhóm E: hệ thống, demo và thực tiễn

**Q20. "Demo có chạy thật không? Nếu thầy đưa một file ghi âm bằng điện thoại thì sao?"**
- *Dàn ý:*
  1. Ba container Docker Compose, chạy ngoại tuyến; khởi động bằng `scripts/demo_up.ps1`, kiểm bằng `scripts/demo_check.ps1`.
  2. Một lần đo đầu–cuối: tải lên và phân tích 3,721 s (bản ghi train, 3 sự kiện); RAG hybrid 0,273 s
     (`docs/measurements/demo_lbrv3_e2e_20261110.md`).
  3. Dịch vụ tái tạo đầu ra đã đóng băng: V3 có 573/692 sự kiện trùng khít, 691 nằm trong collar (`report/final_src/06_ket_qua.md`).
  4. Lịch sử demo chỉ gồm bản ghi train; có ảnh dự phòng (`docs/demo_screenshots/01-start.png` … `04-rag-evidence.png`; `docs/DEMO.md`).
- *Đánh giá:* **trả lời được nhưng yếu.** Mới đo một lần, chưa có video dự phòng, chưa ghi nhận hành vi với tệp lạ (MP3/M4A, rất dài, im
  lặng). *Cần thêm:* T1, 2–3 giờ.

**Q21. "Xử lý một bản ghi mất bao lâu, trên phần cứng gì? Triển khai 100 micro thì sao?"**
- *Dàn ý:*
  1. Huấn luyện và suy luận trên RTX 3070 Laptop 8 GB.
  2. Xử lý theo lô, không thời gian thực; đúng phạm vi ADR-0001 (`report/final_src/01_gioi_thieu.md`).
  3. API tách khỏi PyTorch (có kiểm thử CI chặn) và trao đổi qua hợp đồng JSON Schema, nên dịch vụ suy luận nhân bản được. PostgreSQL kèm
     pgvector làm lọc và xếp hạng trong một câu SQL (`report/final_src/05_trien_khai.md`; `report/final_src/04_phuong_phap.md`).
  4. Chưa đo hiệu năng có thống kê (`report/final_src/07_ket_luan.md`).
- *Đánh giá:* **trả lời được nhưng yếu.** *Cần thêm:* đo trên khoảng 20 bản ghi train: trung bình, p95 và hệ số thời gian thực (giây xử lý
  trên giây âm thanh) (T1, 1–2 giờ).

**Q22. "Tính thực tiễn của đề tài là gì? Ai sẽ dùng hệ thống này?"**
- *Dàn ý:*
  1. Quy chuẩn tiếng ồn quốc gia đặt giới hạn theo mức âm tương đương dBA theo khung giờ. Theo QCVN 26:2010/BTNMT, khu vực thông thường
     là 70 dBA (6–21 giờ) và 55 dBA (21–6 giờ) (đoạn trích, [luatduonggia.vn](https://luatduonggia.vn/?p=732710)). QCVN 26:2010 đã được
     thay bằng QCVN 26:2025/BNNMT ([thuvienphapluat.vn](https://thuvienphapluat.vn/TCVN/Tai-nguyen-Moi-truong/QCVN-26-2025-BNNMT-Tieng-on-921705.aspx)).
     Con số dBA không cho biết tiếng ồn đến từ nguồn nào.
  2. Hệ thống bổ sung thông tin "nguồn nào, lúc nào, bao lâu" và cho hỏi lại lịch sử, kèm bằng chứng nghe lại được.
  3. Người dùng: cán bộ quan trắc, ban quản lý khu đô thị hoặc khu công nghiệp, nhà nghiên cứu cảnh quan âm thanh.
  4. Theo ADR-0001, hệ thống chỉ mô tả nguồn âm quan sát được, không kết luận vi phạm hay tình huống.
  5. Giới hạn: dữ liệu theo giấy phép CC-BY-NC-SA-4.0, tức phi thương mại (`report/final_src/03_du_lieu.md`); chưa có dữ liệu Việt Nam;
     chưa có xác thực người dùng.
- *Đánh giá:* **trả lời được nhưng yếu.** Báo cáo chưa có đoạn nào về thực tiễn. *Cần thêm:* T0 (đoạn văn, gộp với Q5) và T1 (slide "Tính
  thực tiễn").

**Q23. "Hệ thống có dùng để phát hiện đột nhập, tiếng súng hay cấp cứu được không?"**
- *Dàn ý:*
  1. Ngoài phạm vi có chủ ý (ADR-0001). "Phát hiện tiếng kính vỡ lúc 5,4 s" là hợp lệ, "phát hiện đột nhập" thì không
     (`report/final_src/01_gioi_thieu.md`).
  2. Lớp `thunder_fireworks_gunshot` là lớp gộp, nên hệ thống không chọn một thành viên duy nhất (`docs/thesis/ch4.md`).
  3. Dữ liệu không đủ cơ sở cho kết luận an ninh.
- *Đánh giá:* **đã có câu trả lời tốt.**

#### Nhóm F: quy trình, nhóm và liêm chính

**Q24. "Nhóm hai người phân công thế nào? Em Phát làm phần nào, em Tính làm phần nào?"** Hội đồng có thể hỏi từng người về phần của người kia.
- *Vì sao hỏi:* mẫu khoa yêu cầu kế hoạch có "phân công nhiệm vụ trong nhóm" (`report/Mau bao cao KLTN_DS.docx`); UIT Điều 5.3 yêu cầu
  ghi phân công; UIT và UED chấm điểm theo từng SV.
- *Dàn ý:* hiện chưa có bằng chứng trong repo.
- *Đánh giá:* **chưa có câu trả lời.** *Cần thêm:*
  - T0, 1 giờ: bảng phân công thật, chia theo mắt xích và việc chung, khớp nhật ký và lịch sử làm việc.
  - T1: slide phân công; mỗi người tập trả lời câu hỏi sâu về phần của người kia.

**Q25. "Các em có dùng ChatGPT, Claude hay Copilot để viết code hoặc báo cáo không?"**
- *Vì sao hỏi:* đây là xu hướng từ 2025; rubric HCMUS có ghi chú riêng về AI. Repo có tệp cấu hình tác tử AI (`AGENTS.md`, `CLAUDE.md`,
  `HANDOFF_CODEX.md`, `docs/AGENT_SYNC.md`); nếu GVPB hay hội đồng xem mã nguồn, câu hỏi này gần như chắc chắn xuất hiện. 397 commit trong
  khoảng 7 tuần cũng dễ gợi câu hỏi.
- *Dàn ý (trung thực, theo chính sách trường):*
  1. Nêu công cụ đã dùng và dùng vào việc gì.
  2. Nêu phần nhóm quyết định và kiểm chứng: 48 ADR do nhóm duyệt, luật chọn ghi trước, mọi số do script sinh và đã đối chiếu.
  3. Khẳng định nhóm chịu trách nhiệm toàn bộ nội dung.
  4. Sẵn sàng giải thích bất kỳ mô-đun nào.

  Không nên phủ nhận hay né tránh. Theo HCMUS, "nội dung thiếu dẫn chứng… được xem là sai"
  ([HCMUS-FIT](https://www.ctda.hcmus.edu.vn/wp-content/uploads/2024/07/Khoa-CNTT-Tieu-chi-va-bieu-mau-cham-diem-tot-nghiep-v4-20230627-1.pdf)).
- *Đánh giá:* **chưa có câu trả lời.** Báo cáo chưa có khai báo; chưa rõ chính sách của Khoa CNTT IUH. *Cần thêm:*
  - T0, 30 phút: hỏi GVHD có cần khai báo không, nếu có thì viết đoạn khai báo ngắn.
  - T1: luyện giải thích mã không cần tài liệu (đặc trưng của LBR, điều kiện SQL, giải mã bằng ngữ pháp).

**Q26. "Khối lượng công việc thực tế bao nhiêu? Quá trình làm có đều không?"**
- *Dàn ý:* dùng số đếm ở mục 3 (397 commit, 48 ADR, 488 tệp đo, 873 hàm kiểm thử, hơn 42 giờ âm thanh, 42 lượt test có sổ, báo cáo 75
  trang) và dải thời gian.
- *Đánh giá:* **trả lời được nhưng yếu.** Chưa có slide; nhật ký tuần 5–7 còn ghi "(chưa có ghi chép…)" và chưa có ngày báo cáo GVHD
  (`report/final_src/90_phan_cuoi.md`), mâu thuẫn với luận điểm làm đều. *Cần thêm:* T0 cho nhật ký, T1 cho slide.

**Q27. "Đây là ngành Khoa học Dữ liệu. Phần khoa học dữ liệu của đề tài nằm ở đâu, hay toàn là kỹ thuật hệ thống?"**
- *Dàn ý:*
  1. Kiểm nguồn gốc dữ liệu: kiểm MD5, tập chia khóa băm, kiểm trùng.
  2. Thiết kế thí nghiệm ghi trước; chọn bằng dự đoán ngoài mẫu trên 564 bản ghi thay vì dev nhỏ.
  3. Thống kê: bootstrap ghép cặp theo bản ghi, kiểm định Welch, nhiều seed.
  4. Phân tích lỗi dẫn tới LBR (boosting trên đặc trưng của hộp sự kiện); hiệu chuẩn xác suất (ECE); đo độ bám sát của mô tả
     (`report/final_src/03_du_lieu.md`, `report/final_src/04_phuong_phap.md`, `report/final_src/06_ket_qua.md`).
- *Đánh giá:* **đã có câu trả lời tốt.**

**Ba điểm nhất quán cần rà**
- `docs/SYSTEM.md` liệt kê RQ4 (bộ phân loại phân cấp), còn báo cáo viết "ba câu hỏi nghiên cứu chính" cộng một câu hỏi phụ
  (`report/final_src/01_gioi_thieu.md`). Khi được hỏi, luôn nói "3 câu hỏi chính và 1 câu hỏi phụ".
- Tên tiếng Anh trên bìa là "Grounded Environmental Sound Event Detection, Captioning, and RAG-based Retrieval"
  (`report/final_src/front_info.yaml`). Tên giao việc dùng là "Grounded Environmental Audio Monitoring and RAG-based Event Retrieval".
  Cần thống nhất với tên đã đăng ký.
- Mẫu khoa ghi trên bìa "THÁNG 12 NĂM 2026"; báo cáo ghi "THÁNG 11 NĂM 2026" (`report/final_src/front_info.yaml`). Nên hỏi GVHD cho bản
  bìa cứng sau bảo vệ.

### Inferences

**Danh sách việc cần làm, chia tầng**

*T0: trước 28/11/2026, tổng khoảng 6–8 giờ*

| Mã | Việc | Câu liên quan | Công |
|---|---|---|---|
| T0-1 | Điền nhật ký tuần 5–7 và ngày báo cáo GVHD (`report/final_src/90_phan_cuoi.md`) | Q26; tiêu chí "Quá trình" | 1–2 h |
| T0-2 | Thêm trang "Nhận xét của giáo viên phản biện" vào phần đầu; mẫu yêu cầu, bản giữa kỳ đã bỏ có chủ ý (`report/quy_cach_bao_cao.md` §4) | Hình thức | 20 phút + dựng lại DOCX/PDF |
| T0-3 | Bảng phân công hai thành viên, khớp nhật ký | Q24 | 1 h |
| T0-4 | Hỏi GVHD bốn việc: khai báo AI, yêu cầu Turnitin, thời lượng trình bày, chuẩn bị slide hay poster | Q25, mục 5 | 30 phút |
| T0-5 | Đoạn "ý nghĩa thực tiễn ở Việt Nam" (QCVN đo dBA, không cho biết nguồn; giấy phép NC) và số 19 lớp lấy từ tệp đo sẵn | Q5, Q22 | 45–60 phút |
| T0-6 | Đoạn định vị LBR ở Chương 2; chỉ viết khi đã đọc tóm tắt nguồn, nếu không thì chuyển sang T1 | Q2 | 1–2 h |
| T0-7 | Một câu ở Chương 6 về đánh đổi giữa hybrid và vector_only (đúng bộ lọc 0,271 và 0,493) | Q14 | 15 phút |
| T0-8 | Rà tên tiếng Anh và cách gọi "3 RQ chính + 1 RQ phụ" | Nhất quán | 15 phút |
| T0-9 | Kiểm nơi thu âm của DataSEC/DataSED trong bài *Scientific Data* | Q5 | 10 phút |

*T1: trước phản biện (07–18/12) và hội đồng (23/12), tổng khoảng 25–35 giờ*

| Mã | Việc | Câu liên quan | Công |
|---|---|---|---|
| T1-1 | Cắt kịch bản 25 phút xuống bản 15 phút, thêm bản 10 phút và bản 5–7 phút cho buổi gặp GVPB; tập ít nhất 3 lần có bấm giờ | Mục 5 | 3–4 h + tập |
| T1-2 | Bốn slide mới: "Nhóm làm gì mới" (có LBR), "Khối lượng công việc", "Tính thực tiễn", "Phân công" | Q1, Q22, Q24, Q26 | 2–3 h |
| T1-3 | Video demo dự phòng 60–90 s; tập trên đúng máy sẽ dùng; thử tệp lạ (MP3/M4A, dài, im lặng) bằng bản ghi train hoặc tự thu | Q20 | 2–3 h |
| T1-4 | Slide dự phòng: LBR so với công trình liên quan; vì sao không dùng LALM; SQL và LLM; hybrid và vector; vehicle_pass_by; thước chặt và trần người; Bonferroni cho RQ1 | Q2, Q8, Q11, Q14–Q17 | 3–4 h |
| T1-5 | Đo thời gian xử lý trên khoảng 20 bản ghi train | Q21 | 1–2 h |
| T1-6 | Người đọc thứ hai chấm 60 mô tả, tính κ | Q19 | 2–3 h |
| T1-7 | Poster A0 nháp, phòng khi bị xếp poster (danh sách ra trước 20/12, đánh giá 23/12 nên chỉ còn khoảng 3 ngày để in) | Mục 5 | 4–6 h |
| T1-8 | Hỏi đáp thử, chéo phần giữa hai người; thẻ ghi nhớ chỉ số (event-F1 collar, PSDS-1/2, nDCG@10, bootstrap, Welch, ECE) | Tất cả | 3–4 h |
| T1-9 | Tùy chọn: 3–5 đoạn tự thu ở TP.HCM chạy qua demo, chỉ minh họa định tính, tránh lời nói nhận diện được người | Q5 | 2 h |
| T1-10 | Tùy chọn, chỉ khi T1-1 đến T1-8 đã xong: thăm dò LALM mã mở trên dev | Q17 | 4–8 h |

*T2: hướng phát triển, dùng khi trả lời "nếu có thêm thời gian"*
- Bộ dữ liệu thí điểm Việt Nam và đánh giá lệch miền; mốc SED bên ngoài trên DataSED; mốc LALM đầy đủ; so trực tiếp với LA-RAG.
- Đánh giá mô tả với nhiều người đọc, thêm FLAM; chạy lại RQ1 với DataSEC bản 4; xác thực người dùng, xử lý luồng liên tục.
- Viết bài báo. Rubric HCMUS cộng tối đa 1,0 điểm cho bài Q1/Q2 hoặc hội nghị A*–B; IUH-FIT có hội nghị SSRC. Chưa rõ IUH có cộng điểm
  hay không.

**Cách trả lời chung:** mỗi câu trả lời 30–60 giây, có đúng một con số chính và một tệp hoặc slide làm chỗ dựa. Thừa nhận giới hạn trước
khi hội đồng chỉ ra; báo cáo đã liệt kê sẵn hạn chế (`report/final_src/06_ket_qua.md`), đây là điểm mạnh nên tận dụng.

### Gaps
- Chưa kiểm demo có nhận MP3/M4A, tệp tần số mẫu khác hay tệp rất dài không, vì ghi chú này không chạy ứng dụng.
- Báo cáo không có số theo lớp ở thước giao nhau cho `vehicle_pass_by`, nên Q15 chưa trả lời định lượng được.
- Không xác minh được ngoài repo rằng PolyBench có số liệu riêng trên clip DataSED; mới đọc tóm tắt arXiv.
- Chưa rõ người đọc lại 60 mô tả test có tính là "chạm test" theo quy tắc dự án không. Đề xuất dùng mô tả dev cho chắc.
- Chưa có tài liệu nêu phân công thật và mức dùng AI thật. Chỉ nhóm mới điền được hai việc này.

## 5. Hậu cần buổi bảo vệ: chia thời gian slide và demo, video dự phòng, câu không trả lời được, slide khối lượng và slide thực tiễn

### Takeaway
Hãy lên kế hoạch cho bản **15 phút**, kèm bản 10 phút dự phòng. Kịch bản hiện tại dài khoảng 25 phút và chỉ dành 1 phút cho demo. Nên
demo trực tiếp 2–2,5 phút trên dịch vụ đã khởi động sẵn; có video 60–90 s và ảnh chụp làm dự phòng. Chuẩn bị song song poster A0, vì
danh sách hội đồng/poster chỉ ra trước 20/12. Với câu không trả lời được, nói thẳng và hẹn bổ sung, không bịa số.

### Cited Findings
- UIT: "SV trình bày đề tài không quá 15 phút". Sau đó CBPB đọc nhận xét và SV trả lời câu hỏi của CBPB và hội đồng. — [UIT 159/QĐ-ĐHCNTT](https://student.uit.edu.vn/sites/daa/files/202410/159-qd-dhcntt_05-03-2024_ban_hanh_quy_dinh_kltn.pdf)
- Khoa Công nghệ Điện IUH: trình bày tối đa 15–20 phút, bắt buộc có PowerPoint. — [Khoa CN Điện IUH](https://feet.iuh.edu.vn/news.html@detail@264@1490@Thong-bao-V-v-Bao-ve-khoa-luan-tot-nghiep-dai-hoc-cac-lop-hoc-lai-HK2-va-DHDI20AVL)
- Blog CNTT:
  - buổi bảo vệ khoảng 15–20 phút;
  - demo lỗi thì bình tĩnh xin khởi động lại, không được thì xin chuyển sang video đã quay sẵn;
  - không dùng dữ liệu thử kiểu "test1", "123456";
  - slide chỉ nên có từ khóa và sơ đồ;
  - câu mẫu khi không biết: "Dạ phần này em chưa tìm hiểu sâu, em xin phép ghi nhận để nghiên cứu thêm sau buổi hôm nay ạ";
  - không cãi tay đôi với hội đồng.

  — [codesinhvien.vn (blog/tổng hợp)](https://codesinhvien.vn/bao-ve-do-an-tot-nghiep-it-loi-de-toang/)
- FUNiX: tập to tiếng và canh giờ "đúng thời lượng thời gian cho phép"; xem lại video buổi bảo vệ của khóa trước. — [FUNiX (blog/tổng hợp)](https://funix.edu.vn/chia-se-kien-thuc/kinh-nghiem-bao-ve-do-an-tot-nghiep-funix/)
- Khoa CNTT IUH: đánh giá "Trực tiếp" sáng 23/12/2026, có cả hội đồng và poster; danh sách ra trước 20/12; hướng dẫn chi tiết sẽ đăng
  sau. — [FIT IUH, 05/11/2026](https://fit.iuh.edu.vn/news.html@detail@155@3610@Thong-bao-thoi-gian-danh-gia-Khoa-luan-tot-nghiep,-Thuc-tap-doanh-nghiep-HK1-2026-2027)
- Mẫu khoa: slide "súc tích, nêu bật được các ý tưởng"; poster một trang A0 gồm đặt vấn đề, mục tiêu, kế hoạch, phương pháp, kết quả,
  kết luận, tài liệu tham khảo chính, "hạn chế chữ quá nhiều". — `report/Mau bao cao KLTN_DS.docx`
- Kịch bản hiện tại có 18 slide chính. Cộng thời lượng ghi trên từng slide được khoảng 25 phút (0,5 + 1 + 1,5 + 1 + 1,5 + 1 + 1,5 × 4 +
  2 + 1,5 + 2 + 1,5 + 2 + 1 + 1 + 1,5). Demo chỉ có 1 phút (slide 16). — `report/slide/kich_ban_bao_ve.md`
- Demo đã có sẵn: script khởi động và kiểm tra; chạy không cần Internet; lịch sử demo gồm 15 bản ghi train phủ đủ 21 lớp; 4 ảnh dự phòng
  1440×900; danh mục kiểm tra trong `docs/DEMO.md`. — `report/final_src/05_trien_khai.md`; `docs/DEMO.md`; `docs/demo_screenshots/`

### Inferences

**Bản 15 phút đề xuất (≈ 14,5 phút), dựng lại từ slide hiện có**

| Thời điểm | Nội dung | Slide gốc |
|---|---|---|
| 0:00–0:30 | Mở đầu | S1 |
| 0:30–2:00 | Bài toán và kiến trúc, gộp hai slide | S2 + S4 |
| 2:00–3:00 | Câu hỏi nghiên cứu và "nhóm làm gì mới" (viết lại, có LBR) | S3 |
| 3:00–4:00 | Dữ liệu, rò rỉ và luật mở test một lần | S5 + S6 |
| 4:00–5:00 | RQ1 âm tính, nêu cận trên +0,02 | S7 |
| 5:00–6:30 | Chẩn đoán lỗi dẫn tới LBR | S8 + S10 |
| 6:30–8:00 | Kết quả SED và hai điểm vận hành | S11 |
| 8:00–9:30 | RQ2 | S13 + S14 |
| 9:30–10:45 | RQ3 | S15 |
| 10:45–13:15 | Demo trực tiếp | S16 |
| 13:15–14:30 | Thực tiễn, hạn chế, kết luận, kèm một dải "khối lượng" | S17 + S18 + slide mới |

Chuyển S9 (giai đoạn O) và S12 (PSDS) vào phụ lục, cùng các slide dự phòng ở mục 4. Bản 10 phút bỏ thêm S5+S6 và S13+S14 (chỉ giữ một
câu cho mỗi phần) và rút demo còn 1,5 phút.

**Kịch bản demo 2,5 phút**
- Chuẩn bị: chạy `demo_up.ps1` trước 15 phút và `demo_check.ps1` phải pass; mở sẵn trình duyệt; tắt chế độ ngủ; chạy ngoại tuyến.
- Bước 1: tải lên một bản ghi train, mất khoảng 4 s, rồi chỉ vào dòng thời gian.
- Bước 2: mô tả song ngữ; chỉ cho hội đồng thấy mọi nguồn âm trong mô tả đều có trên dòng thời gian.
- Bước 3: hỏi bằng tiếng Việt một câu có quan hệ thời gian, bấm vào bằng chứng để nghe đúng đoạn đó.
- Bước 4: nói một câu "đây là chế độ ưu tiên phát hiện V3, chạy trên laptop, không cần mạng".
- Nếu lỗi: một lần khởi động lại → video → ảnh chụp.

**Quy tắc khi hỏi đáp**
- Ghi lại câu hỏi. Chia người trả lời theo mắt xích, nhưng cả hai phải trả lời được mọi phần.
- Mỗi câu trả lời có một con số và một chỗ dựa.
- Câu ngoài hiểu biết: dùng câu mẫu ở trên, sau đó gửi bổ sung qua GVHD nếu hội đồng muốn.
- Câu chạm phạm vi ADR-0001 (an ninh, tội phạm, khẩn cấp): trả lời theo Q23.
- Tuyệt đối không ước số tại chỗ.

**Bản nháp slide "Khối lượng công việc"** (số cần kiểm lại trước khi dùng)
- *Dữ liệu:* 2 bộ, 5.765 tệp, 42,4 giờ âm thanh; kiểm trùng ba tầng (hiệu chuẩn bằng 24 cặp dương và 5.000 cặp âm; duyệt tay 35 cặp).
- *Phát hiện sự kiện:* 5 thế hệ v1 → v2 → f2 (11 ứng viên) → B0 (chọn ngoài mẫu trên 564 bản ghi) → LBR V2/V3. RQ1 gồm 10 lần chạy v1
  và 6 lần chạy v2.
- *Mô tả:* 4 cách sinh × 4 hệ SED × 139 bản ghi, ở cả mức đầu–cuối và mức oracle.
- *Truy hồi:* 100 truy vấn × 3 chế độ × 4 kho × 2 ngôn ngữ; bộ phân tích câu hỏi thử trên 240 câu.
- *Kỹ thuật:* 3 dịch vụ Docker, 8 hợp đồng JSON Schema, CI chặn PyTorch trong API, giao diện song ngữ chạy ngoại tuyến.
- *Kỷ luật:* 48 ADR, 42 lượt chạm test có sổ, 488 tệp đo, khoảng 870 hàm kiểm thử, 397 commit, báo cáo 75 trang.

**Bản nháp slide "Tính thực tiễn"**
- *Vấn đề:* QCVN tiếng ồn đo dBA theo khung giờ, không trả lời được "nguồn nào".
- *Hệ thống:* cho dòng thời gian nguồn âm và cho hỏi lịch sử bằng tiếng Việt hoặc tiếng Anh, có bằng chứng nghe lại.
- *Hai kịch bản:* rà bản ghi dài khi có phản ánh tiếng ồn; thống kê nguồn âm cho nghiên cứu cảnh quan âm thanh đô thị. Chỉ nói về nguồn
  âm quan sát được.
- *Số liệu:* góc nhìn 19 lớp Việt Nam, V3 phát hiện khoảng 83% sự kiện với precision 0,78.
- *Giới hạn:* chưa có dữ liệu Việt Nam; giấy phép phi thương mại; chưa có xác thực; xử lý theo lô.

**Buổi gặp GVPB (07–18/12)**
- Mang bản trình bày 5–7 phút, báo cáo in và máy chạy demo.
- Ghi lại mọi câu hỏi của GVPB: đó là bản nháp câu hỏi của hội đồng ngày 23/12 (theo trình tự kiểu UIT, nhận xét GVPB được đọc trước hội
  đồng).

### Gaps
- Chưa có thời lượng chính thức của Khoa CNTT cho đợt 23/12/2026. Chưa biết hội đồng có cho demo trực tiếp, có máy chiếu và ổ cắm, có cho
  dùng laptop cá nhân không. Khoa ghi sẽ đăng hướng dẫn sau, cần theo dõi website.
- Không tìm được hướng dẫn chính thức của IUH về cách chấm poster (ai chấm, chấm theo tiêu chí gì).
