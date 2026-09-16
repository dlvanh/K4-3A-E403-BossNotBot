# CẨM NANG HÀNH ĐỘNG DÀNH CHO DATA MINING & USER VALIDATION
**Học viên:** Lại Bá Quân · **MSSV:** `2A202602495`  
**Dự án:** Discord Smart Digest (Bản tin 30 giây cá nhân hóa)  
**Nhóm:** `BossNotBot` · **Phòng:** E403 · **Lớp:** 3A

---

## I. TỔNG QUAN VAI TRÒ & TRÁCH NHIỆM
Bạn là **"Người bảo vệ sự thật"** của cả đội. Bạn chịu trách nhiệm về 2 khối điểm cực kỳ quan trọng:
1. **Khối R1 — Bằng chứng nỗi đau (15 điểm):** Cung cấp con số thống kê đếm được từ dữ liệu (Chuẩn B) và kết quả khảo sát người dùng thực tế (Chuẩn A) để đưa vào `spec.md §1 & §2`.
2. **Khối R6 — Validation với User (+8 điểm Bonus):** Điểm thưởng quyết định nhóm có đạt trần 100 điểm hay chỉ dừng ở 92 điểm. Bạn phụ trách tổ chức buổi test với ≥ 2 người dùng ngoài nhóm, ghi log nguyên văn và mang phản hồi về cải tiến sản phẩm.
3. **Quy tắc Vibe-coding:** Bạn phải hiểu sâu sắc phương pháp mining dữ liệu và câu chuyện thực tế của những người dùng bạn đã phỏng vấn để trả lời giám khảo tại CP6.

---

## II. DANH MỤC TÀI LIỆU BẮT BUỘC PHẢI ĐỌC
* [`02-guide.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/02-guide.md):
  * Đọc kỹ **§1.3** (Cách mining data & thu bằng chứng chuẩn A/B).
  * Đọc kỹ **§4.2** (Đo bằng người — Vòng validation 5 nhịp: Comfort, Context, Task, Observe, Ask).
* [`04-rubric.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/04-rubric.md):
  * Đọc kỹ tiêu chí **R1 (15 điểm)** và **R6 (8 điểm bonus)**.
* [`further-reading/mom-test-summary.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/further-reading/mom-test-summary.md): Quy tắc phỏng vấn Mom Test (hỏi về sự việc đã xảy ra, không hỏi xin ý kiến tương lai).
* [`data/discord-pack/README.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/data/discord-pack/README.md): Nắm vững quy định bảo mật (người trong dữ liệu là bạn cùng khóa; chỉ trích dẫn tối đa 2 câu/ví dụ; không đoán danh tính bạn học).

---

## III. HƯỚNG DẪN TỪNG BƯỚC CHI TIẾT THEO CÁC MỐC

### MỐC CP1 & CP2 (TỐI 16/9) — MINING SỐ LIỆU ĐẦU TIÊN
* **Mục tiêu:** Có ngay con số định lượng ban đầu từ data pack để chứng minh "Nỗi đau quá tải tin nhắn là có thật".
* **Việc làm độc lập:**
  1. Mở file dữ liệu [`data/discord-pack/k4_messages.csv`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/data/discord-pack/k4_messages.csv) (bằng Python / Excel / Google Sheets).
  2. Thực hiện đếm và phân loại:
     * Tổng số tin nhắn: `1.092 tin`.
     * Số tin do học viên gửi (`is_bot = False`): `779 tin`.
     * Lọc các từ khóa: `"deadline"`, `"nộp"`, `"lab"`, `"link"`, `"slide"`, `"lịch"`.
     * **Kết quả khai thác (Ví dụ):** Có 86 câu hỏi về deadline/thủ tục, nhưng nằm rải rác ở 5 kênh khác nhau và bị xen lẫn bởi hơn 600 tin nhắn thảo luận phiếm. Kênh đông nhất có 654 tin nhắn trong 3 ngày (trung bình > 200 tin/ngày).
  3. Lọc ra **≥ 5 ví dụ tin nhắn nguyên văn** (ghi rõ `msg_id`) thể hiện sự ức chế hoặc bối rối vì trôi tin nhắn.
* **Việc cộng tác với đồng đội:**
  * Cung cấp các con số này cho **Đỗ Lê Việt Anh** để đưa vào Canvas CP1 và nháp mục §1 trong `spec.md`.

---

### MỐC CP3 & CP4 (NGÀY 17/9) — KHẢO SÁT CHUẨN A (≥ 20 NGƯỜI) & TÌM WILLING USERS
* **Mục tiêu:** Hoàn thiện Bằng chứng chuẩn A (Khảo sát ≥ 20 bạn ngoài nhóm, ≥ 50% xác nhận) và chốt 2 Willing Users cho vòng R6.
* **Việc làm độc lập:**
  1. **Thực hiện khảo sát:** Dùng mẫu khảo sát Mom Test (đã chuẩn bị ở phần trước), đi phỏng vấn trực tiếp các bạn học viên trong phòng E403 (trong giờ nghỉ sáng/chiều hoặc buổi trưa).
     * *Câu hỏi trọng tâm:* "Lần gần nhất mở Discord thấy cả trăm tin nhắn chưa đọc, bạn có đọc hết không hay ấn Mark as read?", "Mỗi tối bạn mất bao nhiêu phút để tìm thông báo mới?".
  2. **Lập bảng nhật ký khảo sát:** Lưu vào tài liệu của nhóm:
     * Danh sách 20–22 học viên (Mã HV/Tên, Hành vi, Quote nguyên văn, Số phút lãng phí/ngày).
     * Tính tỷ lệ % xác nhận (Mục tiêu: ≥ 60–70% học viên thừa nhận bị ngợp và bấm Mark as read).
  3. **Chốt danh sách 2 Willing Users:** Xin số điện thoại / Discord handle của 2 bạn cam kết sẽ thử bản prototype vào sáng ngày 18/9.
* **Việc cộng tác với đồng đội:**
  * Chuyển toàn bộ bảng kết quả khảo sát và các trích dẫn cho **Đỗ Lê Việt Anh** trước 19:00 ngày 17/9 để Việt Anh hoàn thiện mục §1 & §2 trong `spec.md` trước hạn chốt CP4 (21:00).

---

### MỐC CP5 (13:00 18/9) — TIẾN HÀNH VALIDATION R6 (+8 ĐIỂM BONUS)
*Đây là nhiệm vụ then chốt nhất của bạn. Nếu làm tốt, nhóm bạn được cộng thẳng 8 điểm vào tổng điểm!*
* **Mục tiêu:** Đưa bản prototype cho ≥ 2 người dùng ngoài nhóm trải nghiệm thật, ghi chép nhật ký chi tiết vào `validation/user_test_log.md`.
* **Việc làm độc lập:**
  1. **Chuẩn bị kịch bản test (10 phút/người theo 5 nhịp):**
     * *Nhịp 1 (Comfort - 1'):* "Bọn mình đang đánh giá phần mềm, không đánh giá bạn. Bạn cứ tự nhiên nói to suy nghĩ nhé."
     * *Nhịp 2 (Context - 1'):* "Hãy tưởng tượng bạn vừa đi làm cả ngày về, muốn biết hôm nay lớp có gì cần làm gấp."
     * *Nhịp 3 (Task - 1'):* Giao task: "Bạn hãy dùng công cụ này để tìm xem trong 24h tới mình cần nộp bài gì và tài liệu mới nhất ở đâu." (Để họ tự cầm chuột/bấm phím).
     * *Nhịp 4 (Observe - 5'):* **Im lặng hoàn toàn quan sát.** Ghi chép: Họ bấm vào đâu trước? Họ có bị lúng túng ở chỗ nào không? Họ có tìm thấy mã trích dẫn tin nhắn không?
     * *Nhịp 5 (Ask - 2'):* Hỏi sau khi dùng: "Chỗ nào làm bạn khó hiểu nhất?", "Bạn có tin vào thông tin deadline này không — vì sao?", "Nếu mai không được dùng cái này nữa bạn thấy thế nào?".
  2. **Viết biên bản vào `validation/user_test_log.md`:**
     * Bảng nhật ký: Tên người thử, task đã giao, quan sát hành vi, **quote nguyên văn** (kể cả câu chê như *"Chữ deadline hơi nhỏ", "Mình muốn bấm vào link nhảy thẳng đến Discord"*).
     * 4 dòng tổng hợp cuối bảng: 1. Chủ đề lặp lại nhiều nhất; 2. Đề xuất sửa trước demo; 3. Giữ nguyên cái gì vì sao; 4. Việc để dành phát triển sau.
* **Việc cộng tác với đồng đội:**
  * **Họp với Đoàn Anh Quân (Dev):** Đưa góp ý của người dùng để Anh Quân sửa ngay 1 chi tiết trên giao diện UI (ví dụ: làm nổi bật màu thẻ Deadline).
  * **Báo cho Đỗ Lê Việt Anh:** Đưa thay đổi này vào mục **§9 Changelog** trong `spec.md` (Điều kiện bắt buộc để ăn trọn 4/4 điểm mục R6!).
  * Viết file reflection cá nhân: `reflection/2A202602495_LaiBaQuan.md`.

---

### MỐC CP6 (17:30 18/9) — THUYẾT TRÌNH VỀ NGƯỜI DÙNG & FEEDBACK
* **Nhiệm vụ trên sân khấu:**
  * Phụ trách trình bày **Slide 1 (User & Pain Point thực tế từ khảo sát)** và **Slide 5 (Phản hồi thực tế từ người dùng ở vòng validation)**.
  * Tự tin kể câu chuyện của những người bạn đã phỏng vấn: *"Khi phỏng vấn bạn Nam ở bàn bên, bạn ấy chia sẻ rằng hôm trước suýt nộp muộn Lab 1 vì tin nhắn bị trôi giữa 500 tin chat phiếm..."*. Giám khảo cực kỳ ấn tượng với những bằng chứng sống động này!
