# CẨM NANG HÀNH ĐỘNG DÀNH CHO TEAM LEAD & PRODUCT SPEC
**Học viên:** Đỗ Lê Việt Anh · **MSSV:** `2A202602491`  
**Dự án:** Discord Smart Digest (Bản tin 30 giây cá nhân hóa)  
**Nhóm:** `BossNotBot` · **Phòng:** E403 · **Lớp:** 3A

---

## I. TỔNG QUAN VAI TRÒ & TRÁCH NHIỆM
Bạn là **"Kiến trúc sư sản phẩm"** kiêm **"Người giữ nhịp"** của cả đội. Thành bại về điểm số của nhóm nằm 70% ở tay bạn:
1. **Đại diện nộp bài duy nhất:** Dùng mã `2A202602491` nộp form ở cả 5 Checkpoint CP1 → CP5.
2. **Chủ trì tài liệu trung tâm `spec.md`:** Chịu trách nhiệm về chất lượng các khối điểm R1, R2, R3 (chiếm 41/67 điểm chấm repo).
3. **Điều phối tiến độ & Bảo vệ sản phẩm:** Đảm bảo nhóm không bị trễ deadline, phân bổ slide và cùng nhóm bảo vệ trước giám khảo tại CP6 (tuân thủ Vibe-coding rule).

---

## II. DANH MỤC TÀI LIỆU BẮT BUỘC PHẢI ĐỌC
Trước khi viết bất kỳ chữ nào, bạn cần mở và nắm vững các file sau trong repo:
* [`01-challenge-brief.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/01-challenge-brief.md): Nắm 5 tiêu chí nghiệm thu, format lát cắt MỘT CÂU và 4 lớp chỗ khó.
* [`02-guide.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/02-guide.md): 
  * Đọc kỹ **§1.4 & §1.5** (Bảng impact & Canvas).
  * Đọc kỹ **§2** (Thiết kế Spec, Cost-of-error, 4 lớp chỗ khó).
  * Đọc kỹ **§5.1** (Quy tắc 6 slide thuyết trình).
* [`03-ai-spec-template.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/03-ai-spec-template.md): Mẫu chuẩn 9 phần của file `spec.md`.
* [`04-rubric.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/04-rubric.md): Đọc kỹ các tiêu chí R1, R2, R3, R7 để biết giám khảo sẽ soi từng chữ ở đâu.
* [`further-reading/hax-guidelines.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/further-reading/hax-guidelines.md): 18 nguyên tắc thiết kế AI trải nghiệm người dùng của Microsoft.

---

## III. HƯỚNG DẪN TỪNG BƯỚC CHI TIẾT THEO 6 CHECKPOINT

### MỐC CP1 (19:30 16/9) — CHỐT CANVAS & REPO
* **Công việc của bạn:** 
  * Đảm bảo Repo GitHub `K4-3A-E403-BossNotBot` được tạo ở chế độ **Public**, không fork repo đề bài.
  * Cập nhật bảng phân công trong `README.md`.
  * Nộp form CP1 với Canvas 7 dòng và tên 2 willing users.

---

### MỐC CP2 (21:00 16/9) — CHO THẤY LUỒNG HOẠT ĐỘNG (FLOW)
* **Việc làm độc lập:**
  * Khởi tạo file `spec.md` trong repo của nhóm từ mẫu [`03-ai-spec-template.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/03-ai-spec-template.md).
  * Điền trước khung xương của §1, §2, §4.
* **Việc cộng tác với đồng đội:**
  * **Họp với Đoàn Anh Quân (Dev):** Thống nhất User Flow của bản mockup. Flow gồm: Màn hình Discord → Bấm `/my-digest` → Xuất hiện 3 Card (Hạn chót 24h, Thông báo mới, Thảo luận kỹ thuật kèm link tin nhắn).
  * Lấy link bản Mockup / video quay màn hình từ Anh Quân.
* **Hành động nộp bài:** Dùng MSSV `2A202602491` submit form CP2 trước 21:00.

---

### MỐC CP3 (16:00 17/9) — GỌI AI THẬT & ĐO LƯỢT ĐẦU
* **Việc làm độc lập:**
  * Hoàn thiện mục **§4. Thiết kế** trong `spec.md`:
    * Lát cắt 1 câu: *Một học viên đi làm về · gõ lệnh tóm tắt trên Discord · AI quét tin nhắn ngày, lọc bỏ 95% tin phiếm, trích xuất 3 khối tin then chốt có link nguồn · học viên nắm trọn ngày học trong 30 giây.*
    * Non-goals (≥ 3 thứ không build): 1. Không làm bot trả lời chat 1-1; 2. Không tóm tắt kênh private/tin nhắn riêng tư; 3. Không tự động tag làm phiền học viên.
    * Mức Automation: Chọn **Conditional / Augment** kèm lý do theo **Cost-of-error** (Báo sai deadline học viên bị 0 điểm, nên AI chỉ trích xuất khi có căn cứ và luôn trích dẫn nguồn).
* **Việc cộng tác với đồng đội:**
  * **Họp với Đoàn Anh Quân:** Kiểm tra video quay màn hình 30s thao tác gọi AI thật.
  * **Họp với Nguyễn Khắc Giáp:** Thống nhất danh sách 20 case test (Golden Set) và nhận bảng số liệu đo lường lượt 1.
* **Hành động nộp bài:** Submit form CP3 trước 16:00 (link video 30s + số liệu đo lượt đầu).

---

### MỐC CP4 (21:00 17/9) — CHỐT SPEC & KHOÁ QUALITY BAR (CỰC KỲ QUAN TRỌNG)
*Đây là hạn chốt của tài liệu `spec.md`. Sau 21:00 không được sửa Quality Bar!*
* **Việc làm độc lập:**
  * Hoàn thiện **§4b. Nguyên tắc HAX/PAIR** (Chọn 4 nguyên tắc và chỉ rõ vị trí trên UI):
    1. *HAX G1 (Làm rõ khả năng):* Dòng thông báo đầu digest ghi rõ phạm vi: chỉ tổng hợp tin tức trong 24h của các kênh chung.
    2. *HAX G2 (Làm rõ mức tin cậy):* Mỗi bullet point đều có tag `#channel [msg_id]`.
    3. *HAX G10 (Thu hẹp phạm vi khi nghi ngờ):* Khi gặp tin nhắn thảo luận chưa ngã ngũ về deadline, bot đánh dấu: *"Chờ TA xác nhận"*.
    4. *HAX G9 (Sửa lỗi dễ dàng):* Có nút "Báo tin nhắn sai/sót" dưới bản digest.
  * Hoàn thiện **§5 & §6. Bốn lớp chỗ khó & kịch bản rủi ro (≥ 8 kịch bản)**:
    * *Lớp ① (Nguồn sự thật):* Kịch bản AI bịa hạn nộp lab khi không có tin nào nhắc đến → Hành vi: Ghi "Không có deadline mới trong 24h qua".
    * *Lớp ② (Mơ hồ):* Học viên hỏi "khi nào nộp?" nhưng không ai đáp → Hành vi: Không đưa vào thông báo chính thức.
    * *Lớp ③ (Ngoài thẩm quyền):* Học viên yêu cầu tra điểm/điểm danh cá nhân → Hành vi: Báo từ chối và hướng dẫn liên hệ TA.
    * *Lớp ④ (Đặc thù domain):* Có 2 deadline mâu thuẫn (do gia hạn) → Hành vi: Lấy tin có timestamp mới nhất và cảnh báo đã gia hạn.
  * Hoàn thiện **Quality Bar (§7)**: Chốt số cụ thể: *"Đạt khi ≥ 80% case trích dẫn đúng nguồn; 0% bịa đặt tin tức; 100% case mâu thuẫn deadline lấy đúng thông báo mới nhất"*.
* **Việc cộng tác với đồng đội:**
  * **Lấy từ Lại Bá Quân:** Số liệu khảo sát n = 20 và ≥ 5 quote nguyên văn để điền trọn vẹn §1 & §2.
  * **Lấy từ Nguyễn Khắc Giáp:** Link file `eval/golden_set.json` và kết quả chạy đo để đưa vào §7.
* **Hành động nộp bài:** Commit `spec.md` lên repo và submit form CP4 trước 21:00.

---

### MỐC CP5 (13:00 18/9) — NỘP SLIDE PDF & VIDEO DỰ PHÒNG
* **Việc làm độc lập:**
  * Viết file reflection cá nhân của bạn: `reflection/2A202602491_DoLeVietAnh.md`.
  * Soát lại cấu trúc toàn bộ Repo theo chuẩn R7.
* **Việc cộng tác với đồng đội:**
  * **Họp với Lại Bá Quân:** Kiểm tra nhật ký test người dùng trong `validation/user_test_log.md` và thêm 1 mục cập nhật vào `§9 Changelog` của `spec.md` (Ăn trọn 8 điểm bonus R6).
  * **Họp với Nguyễn Khắc Giáp:** Rà soát Slide 6 trang xuất ra file `demo-slides.pdf`.
  * **Họp với Đoàn Anh Quân:** Kiểm tra video demo dự phòng 2 phút.
  * **Tổ chức Dry-run (Tập dượt):** Cả nhóm tập thuyết trình, bấm giờ đúng 5 phút. Phân công rõ:
    * Việt Anh: Nói Slide 1 (Bối cảnh & Pain) + Slide 2 (Tại sao chọn Digest).
    * Anh Quân: Nói Slide 3 (Demo trực tiếp sản phẩm).
    * Khắc Giáp: Nói Slide 4 (Kết quả đo lường vs Quality Bar).
    * Bá Quân: Nói Slide 5 (User Feedback R6) + Slide 6 (Bài học & Nếu có 1 tuần).
* **Hành động nộp bài:** Submit form CP5 trước 13:00 (Nộp file slide PDF + link video backup).

---

### MỐC CP6 (17:30 18/9) — THUYẾT TRÌNH & VÒNG THI
* Trình bày phần của mình thật tự tin, mạch lạc.
* Sẵn sàng trả lời câu hỏi phản biện của giám khảo về tư duy thiết kế, các quyết định đánh đổi và cách xử lý khi AI bị ảo giác (hallucination).
