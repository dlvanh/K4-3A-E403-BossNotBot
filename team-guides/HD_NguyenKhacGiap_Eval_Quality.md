# CẨM NANG HÀNH ĐỘNG DÀNH CHO QUALITY & EVALUATION LEAD
**Học viên:** Nguyễn Khắc Giáp · **MSSV:** `2A202602950`  
**Dự án:** Discord Smart Digest (Bản tin 30 giây cá nhân hóa)  
**Nhóm:** `BossNotBot` · **Phòng:** E403 · **Lớp:** 3A

---

## I. TỔNG QUAN VAI TRÒ & TRÁCH NHIỆM
Bạn là **"Thẩm phán chất lượng"** và **"Nhà thiết kế trải nghiệm trình diễn"** của đội. Bạn chịu trách nhiệm trực tiếp về:
1. **Khối R4 — Kiểm thử & Đo lường chất lượng (15 điểm):** Xây dựng bộ Golden Set (≥ 20 test cases), chạy đo lường thực tế và thiết lập Quality Bar trong `spec.md §7` và thư mục `eval/`.
2. **Slide trình chiếu chuẩn 6 trang PDF (`demo-slides.pdf`):** Biên tập toàn bộ dữ liệu của nhóm thành 6 slide cô đọng, sắc bén, tuân thủ nghiêm ngặt luật *"Không có bằng chứng thì không có slide"*.
3. **Quy tắc Vibe-coding:** Bạn phải nắm vững cấu trúc của 20 test case và giải thích được nguyên nhân các case bị fail khi giám khảo chất vấn tại CP6.

---

## II. DANH MỤC TÀI LIỆU BẮT BUỘC PHẢI ĐỌC
* [`02-guide.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/02-guide.md):
  * Đọc kỹ **§2.6** (Định nghĩa tốt + Golden set + Quality bar).
  * Đọc kỹ **§4.1** (Đo bằng máy — chạy golden set theo nhịp lặp).
  * Đọc kỹ **§5.1** (Quy chuẩn thiết kế 6 trang slide thuyết trình).
* [`04-rubric.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/04-rubric.md):
  * Đọc kỹ tiêu chí **R4 (Kiểm thử - 15 điểm)**: Cơ cấu 20 case, định nghĩa kiểm chứng được, bảng kết quả các lượt chạy đối chiếu quality bar.
* [`tracks/track-b-discord-assistant.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/tracks/track-b-discord-assistant.md): Phần Hard tests của Track B.

---

## III. HƯỚNG DẪN TỪNG BƯỚC CHI TIẾT THEO CÁC MỐC

### MỐC CP2 & CP3 (TỐI 16/9 → CHIỀU 17/9) — THIẾT KẾ GOLDEN SET & ĐO LƯỢT 1
* **Mục tiêu:** Xây dựng file `eval/golden_set.json` (≥ 20 case) và chạy đo lượt 1 trước 16:00 ngày 17/9.
* **Việc làm độc lập:**
  1. **Tạo thư mục `eval/`** trong repo của nhóm.
  2. **Thiết kế Golden Set ≥ 20 case (Theo cơ cấu rubric chuẩn):**
     * **≥ 8 case cho 4 lớp chỗ khó (mỗi lớp ≥ 2 case):**
       * *Lớp ① (Nguồn sự thật):* 2 ngày không hề có tin tức deadline nào → Kỳ vọng: AI trả về "Không có deadline mới", không tự bịa.
       * *Lớp ② (Mơ hồ):* Học viên hỏi vu vơ "Mai mấy giờ nộp bài ấy nhỉ?" nhưng không ai trả lời → Kỳ vọng: AI không đưa tin đồn này vào phần thông báo chính thức.
       * *Lớp ③ (Ngoài phạm vi):* Học viên chat nhờ sửa code bài tập hoặc hỏi điểm cá nhân → Kỳ vọng: AI bỏ qua, không tóm tắt vào digest chung.
       * *Lớp ④ (Đặc thù domain - Xung đột deadline):* 2 tin nhắn trong ngày có 2 mốc giờ khác nhau (do gia hạn từ 21:00 lên 23:00) → Kỳ vọng: AI chọn đúng mốc giờ mới nhất và có cảnh báo đã gia hạn.
     * **8–10 case thường (Happy path):** Các ngày có thông báo nộp Lab rõ ràng, có link slide Day 2 mới cập nhật, có giải đáp cài đặt thư viện từ TA.
     * **2–4 case hiếm (Edge cases):** Ngày có hơn 200 tin spam emoji/chào hỏi; ngày có tin nhắn kèm mã prompt injection (`Bỏ qua chỉ thị trước...`).
     * **Lưu ý quan trọng:** Bắt buộc có **≥ 10 case lấy từ dữ liệu chat thật** trong `data/discord-pack/k4_messages.csv`.
  3. **Định nghĩa 3 chiều chất lượng kiểm chứng được:**
     * *Chiều 1: Factuality (Tính xác thực)* = 100% thông tin trong digest phải trace ngược được về đúng `msg_id` trong chatlog.
     * *Chiều 2: Noise Filtration (Lọc nhiễu)* = Không chứa tin chào hỏi, đùa giỡn, spam.
     * *Chiều 3: Conflict Resolution (Xử lý xung đột)* = Khi có thông báo sửa đổi, phải hiển thị thông tin mới nhất.
  4. **Chạy đo lường Lượt 1 (trên prototype của Anh Quân):**
     * Đếm số case ĐẠT / CHƯA ĐẠT.
     * Lập bảng kết quả vào file `eval/eval_results.md`: Ví dụ: *Đạt 14/20 case (70%)*.
     * **Phân tích nguyên nhân fail:** Chỉ rõ vì sao 6 case kia chưa đạt (ví dụ: AI vẫn bịa ra thông báo khi ngữ cảnh trống, hoặc prompt chưa lọc được tin nhắn đùa giỡn).
* **Việc cộng tác với đồng đội:**
  * Bàn giao bảng kết quả đo lượt 1 cho **Đỗ Lê Việt Anh** để nộp CP3 trước 16:00 ngày 17/9.

---

### MỐC CP4 (21:00 17/9) — CHỐT QUALITY BAR BẰNG CON SỐ
* **Mục tiêu:** Cùng Team Lead chốt chuẩn "Thế nào là đạt" trong `spec.md §7` trước khi bước vào tối ưu hóa.
* **Việc làm độc lập:**
  * Thống nhất con số Quality Bar:
    > **Quality Bar của nhóm:** Đạt khi bản tin đạt **≥ 80% tổng điểm Golden Set**, trong đó:
    > - Chiều Factuality đạt 100% (0% ảo giác bịa tin).
    > - Xử lý đúng 100% các case xung đột deadline mới nhất.
* **Việc cộng tác với đồng đội:**
  * Đưa nội dung Golden Set, bảng kết quả và Quality Bar vào mục **§7. Kiểm thử** của file `spec.md` để Việt Anh commit lên GitHub trước 21:00 ngày 17/9.

---

### MỐC CP5 (13:00 18/9) — THIẾT KẾ BỘ SLIDE 6 TRANG PDF (`demo-slides.pdf`)
* **Mục tiêu:** Tạo ra file `demo-slides.pdf` chuẩn mực, tuân thủ luật *"Không có bằng chứng thì không có slide"*.
* **Việc làm độc lập:**
  * Thiết kế Slide (bằng Canva / Google Slides / PowerPoint) và **xuất ra file PDF** đặt tên là `demo-slides.pdf` trong thư mục gốc của repo:
    * **Slide 1 — User & Pain (45s):** 
      * Đối tượng: Học viên đi làm về muộn.
      * Nỗi đau có số liệu: 1.092 tin nhắn trong 3 ngày; 73% học viên khảo sát (16/22 bạn) bấm Mark as read; lãng phí 18 phút/ngày lội tin; trích dẫn 1 câu nói đau nhất của bạn học.
    * **Slide 2 — Vì sao chọn Discord Smart Digest (45s):**
      * Bảng Impact so sánh 3 ứng viên (Bot trả lời 1-1 vs Ghép team vs Digest).
      * Lý do chọn Digest: Đem lại giá trị tức thì cho 100% học viên lớp học, giảm rủi ro trễ bài.
    * **Slide 3 — Giải pháp & Lát cắt (2 phút):**
      * Lát cắt 1 câu + Nguyên tắc HAX G1, G2, G10, G9.
      * Dành không gian cho Anh Quân demo trực tiếp trên màn hình: 1 case chuẩn + 1 case xung đột deadline.
    * **Slide 4 — Kết quả đo lường (45s):**
      * Bảng số đo Golden Set: Tỷ lệ đạt thực tế đối chiếu với Quality Bar đã cam kết từ CP4.
      * Nêu thẳng thắn 1 case AI bị lỗi nhiều nhất và bài học rút ra (Ban giám khảo đánh giá rất cao sự trung thực này).
    * **Slide 5 — Người dùng thật nói gì (45s):**
      * Kết quả từ vòng Validation R6 (2 quote nguyên văn của bạn học khi dùng thử).
      * Điểm thay đổi trên UI mà nhóm đã thực hiện sau khi nghe góp ý.
    * **Slide 6 — Nếu có thêm 1 tuần (30s):**
      * 2 tính năng ưu tiên tiếp theo (ví dụ: gửi DM tự động lúc 20h00, tích hợp lọc theo từng kênh bài tập).
      * 1 bài học lớn nhất của cả nhóm về tư duy sản phẩm AI.
  * Viết file reflection cá nhân: `reflection/2A202602950_NguyenKhacGiap.md`.
* **Việc cộng tác với đồng đội:**
  * Thu thập dữ liệu từ Việt Anh (Slide 2), Anh Quân (Slide 3), Bá Quân (Slide 1 & Slide 5) để hoàn thiện slide.
  * Xuất file `demo-slides.pdf` đưa vào repo và gửi cho Việt Anh nộp CP5 trước 13:00 ngày 18/9.

---

### MỐC CP6 (17:30 18/9) — THUYẾT TRÌNH VỀ CHẤT LƯỢNG & ĐO LƯỜNG
* **Nhiệm vụ trên sân khấu:**
  * Phụ trách trình bày **Slide 4 (Kết quả kiểm thử & Quality Bar)**.
  * Tự tin chỉ ra: *"Nhóm chúng em tự đặt ra 20 ca kiểm thử hiểm hóc, bao gồm cả việc thử bẫy AI bằng cách tung 2 deadline mâu thuẫn. Ở lượt chạy đầu tiên, AI chỉ đạt 70%, nhưng sau khi tinh chỉnh prompt và thêm cơ chế lọc timestamp, AI đã đạt 85% và không còn tình trạng bịa nguồn..."*.
