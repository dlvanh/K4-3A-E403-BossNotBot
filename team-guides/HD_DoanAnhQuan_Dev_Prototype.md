# CẨM NANG HÀNH ĐỘNG DÀNH CHO DEV & PROTOTYPE LEAD
**Học viên:** Đoàn Anh Quân · **MSSV:** `2A202602803`  
**Dự án:** Discord Smart Digest (Bản tin 30 giây cá nhân hóa)  
**Nhóm:** `BossNotBot` · **Phòng:** E403 · **Lớp:** 3A

---

## I. TỔNG QUAN VAI TRÒ & TRÁCH NHIỆM
Bạn là **"Kỹ sư xây dựng giải pháp"** của nhóm. Bạn chịu trách nhiệm trực tiếp về **Khối R5 (Prototype chạy được - 8 điểm)** và bằng chứng kỹ thuật tại CP2, CP3, CP5:
1. **Xây dựng bản Mockup (CP2):** Giao diện mô phỏng Discord bấm được thông suốt flow.
2. **Nối AI thật (CP3):** Gọi API LLM thật (Gemini / OpenAI) trích xuất tin nhắn từ dữ liệu pack.
3. **Hiện thực hoá các nguyên tắc HAX/PAIR trên UI:** Đính kèm mã nguồn trích dẫn, xử lý lỗi mâu thuẫn deadline.
4. **Quay video:** Video 30s chứng minh chạy AI thật (CP3) và Video demo dự phòng 2 phút (CP5).
5. **Tuân thủ Vibe-coding rule:** Hiểu rõ từng dòng code, prompt, pipeline để trả lời câu hỏi kỹ thuật từ giám khảo tại CP6.

---

## II. DANH MỤC TÀI LIỆU BẮT BUỘC PHẢI ĐỌC
* [`02-guide.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/02-guide.md): 
  * Đọc kỹ **§3 (Build)**: 3 mức prototype (Sketch / Mock / Working), quy tắc an toàn bảo mật, cách chọn công cụ.
* [`04-rubric.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/04-rubric.md): 
  * Đọc kỹ **Khối R5 (Prototype)**: Chạy end-to-end, ≥ 1 lời gọi AI thật, ghi rõ phần mock.
* [`tracks/track-b-discord-assistant.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/tracks/track-b-discord-assistant.md): Phần Hard tests & Ràng buộc an toàn.
* [`data/discord-pack/README.md`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/data/discord-pack/README.md) & [`k4_messages.csv`](file:///c:/Users/Vxtor/Documents/workspace/ai20k/K4-3A-Day05-06-AI-Product-Hackathon/data/discord-pack/k4_messages.csv): Hiểu định dạng dữ liệu (`msg_id`, `author_id`, `timestamp`, `content`, `reply_to_msg_id`).

---

## III. HƯỚNG DẪN TỪNG BƯỚC CHI TIẾT THEO CÁC MỐC

### MỐC CP2 (21:00 16/9) — DỰNG BẢN MOCKUP BẤM ĐƯỢC (LÀM NGAY TỐI NAY)
* **Mục tiêu:** Tạo bản Mock UI bấm được từ đầu đến cuối luồng, đẩy vào thư mục `codebase/` trên repo.
* **Việc làm độc lập:**
  1. Tạo thư mục `codebase/` trong repo của nhóm.
  2. Dựng 1 trang web HTML/CSS/JS đơn giản (hoặc dùng v0.dev / Streamlit / HTML tĩnh):
     * Bên trái: Cột danh sách kênh (`#announcements`, `#chat-chung`, `#q-and-a`).
     * Ở giữa: Khung chat có các tin nhắn mẫu.
     * Thanh nhập liệu: Có nút bấm hoặc slash command `/my-digest`.
     * Khi click, hiện ra **Bản tin 3 Card mẫu**:
       * 🔴 **Hạn chót 24h tới:** Deadline nộp bài Lab kèm link tin nhắn.
       * 📢 **Thông báo mới nhất:** Lịch học, cập nhật tài liệu.
       * 💡 **Giải đáp kỹ thuật hot:** Lỗi hay gặp trong ngày kèm cách sửa.
  3. Commit code lên repo GitHub với thông điệp: `feat: initial clickable mockup for CP2`.
* **Việc cộng tác với đồng đội:**
  * Thống nhất bố cục hiển thị với **Đỗ Lê Việt Anh (Lead)**.
  * Gửi link repo / video quay màn hình thao tác cho Việt Anh để nộp form CP2 trước 21:00.

---

### MỐC CP3 (16:00 17/9) — TÍCH HỢP AI THẬT & QUAY VIDEO 30S
* **Mục tiêu:** Bản prototype có ít nhất 1 lời gọi AI thật + quay video 30s.
* **Việc làm độc lập:**
  1. **Tạo pipeline gọi LLM:**
     * Dùng API Google AI Studio (Gemini 1.5 Flash - miễn phí, nhanh) hoặc OpenAI API.
     * **Quy tắc an toàn sống còn:** Không bao giờ push API Key hay file `.env` lên GitHub public! Hãy để trong file `.env.example` và đưa `.env` vào `.gitignore`.
  2. **Viết System Prompt trích xuất Digest:**
     ```text
     Bạn là Trợ lý Tóm tắt Thông tin Discord K4 (Discord Smart Digest).
     Nhiệm vụ: Đọc danh sách tin nhắn chat được cung cấp và trích xuất đúng 3 mục:
     1. [DEADLINE]: Các mốc thời gian/hạn nộp trong 24h tới (Kèm mã msg_id thông báo).
     2. [ANNOUNCEMENT]: Các cập nhật tài liệu/thay đổi lịch học chính thức (Kèm mã msg_id).
     3. [TECH_QNA]: 1 giải đáp lỗi kỹ thuật phổ biến nhất trong ngày (Kèm mã msg_id).
     Ràng buộc quan trọng:
     - Lọc bỏ 100% tin nhắn chào hỏi, tin phiếm, spam.
     - Tuyệt đối KHÔNG BỊA ĐẶT thông tin không có trong văn bản được cung cấp.
     - Nếu không có thông tin ở mục nào, ghi rõ "Không có cập nhật".
     - Luôn đính kèm [msg_id] bên cạnh mỗi thông tin để người dùng đối chiếu.
     ```
  3. **Đưa dữ liệu đầu vào:** Lấy 50–100 dòng tin nhắn từ `data/discord-pack/k4_messages.csv` đưa vào context của prompt.
  4. **Quay Video thao tác 30 giây:**
     * Mở ứng dụng → Bấm nút `/my-digest` → Chờ 2-3 giây → AI trả về kết quả thật có mã trích dẫn tin nhắn.
     * Lưu video hoặc upload lên YouTube (chế độ Unlisted) / Google Drive (mở quyền truy cập).
* **Việc cộng tác với đồng đội:**
  * Bàn giao pipeline chạy test cho **Nguyễn Khắc Giáp (Eval Lead)** để Giáp chạy thử nghiệm 20 kịch bản trong Golden Set.
  * Bàn giao link video 30s cho **Đỗ Lê Việt Anh** để nộp form CP3 trước 16:00 ngày 17/9.

---

### MỐC CP4 (21:00 17/9) — CẢI TIẾN PROTOTYPE THEO HAX/PAIR & 4 LỚP CHỖ KHÓ
* **Mục tiêu:** Đưa các xử lý edge cases vào code để đáp ứng cam kết trong `spec.md`.
* **Việc làm độc lập:**
  1. **Code giao diện theo nguyên tắc HAX/PAIR:**
     * *HAX G1 (Làm rõ khả năng):* Hiện dòng ghi chú: *"Bản tin chỉ quét tin nhắn 24h qua tại các kênh công khai"*.
     * *HAX G2 & G11 (Giải thích căn cứ):* Bên cạnh mỗi gạch đầu dòng, hiển thị badge: `[msg_042]` (bấm vào nhảy đến tin nhắn đó).
     * *HAX G9 (Sửa lỗi):* Thêm nút *"Báo sai thông tin"* để người dùng phản hồi.
  2. **Xử lý case xung đột deadline (Lớp ④):**
     * Thêm logic sắp xếp tin nhắn theo `timestamp`. Nếu có 2 tin nhắn nói về deadline của cùng một bài Lab, chọn tin có timestamp mới nhất và hiển thị thêm nhãn: *"Đã gia hạn từ [giờ cũ] lên [giờ mới]"*.
* **Việc cộng tác với đồng đội:**
  * Kiểm tra lại với **Đỗ Lê Việt Anh** xem giao diện đã khớp 100% với những gì viết trong `spec.md §4 & §4b` chưa.

---

### MỐC CP5 (13:00 18/9) — CẬP NHẬT THEO USER TEST & QUAY VIDEO DỰ PHÒNG
* **Việc làm độc lập:**
  1. **Cập nhật tính năng theo phản hồi của User Testing (R6):**
     * Nhận phản hồi từ Lại Bá Quân (ví dụ: người dùng phàn nàn chữ nhỏ, hoặc muốn phân biệt rõ tin của TA với tin của học viên).
     * Sửa code cập nhật giao diện ngay, commit lên GitHub.
  2. **Quay Video Demo Dự Phòng (2 phút):**
     * Quay lại toàn bộ kịch bản định demo tại buổi pitch (1 case chuẩn trích xuất deadline đẹp + 1 case bẫy xử lý xung đột deadline thành công).
     * Video này dùng làm phương án cứu cánh nếu tại phòng thi mạng WiFi bị lỗi.
  3. Viết file reflection cá nhân: `reflection/2A202602803_DoanAnhQuan.md`.
* **Việc cộng tác với đồng đội:**
  * Cung cấp link video dự phòng cho Việt Anh nộp CP5 trước 13:00 ngày 18/9.
  * Cùng nhóm tham gia Dry-run (tập dượt demo mượt mà trong 2 phút).

---

### MỐC CP6 (17:30 18/9) — DEMO TRỰC TIẾP & BẢO VỆ KỸ THUẬT
* **Nhiệm vụ trên sân khấu:**
  * Phụ trách trình bày **Slide 3 (Giải pháp & Demo Live)**: Thao tác trực tiếp trên màn hình, giải thích ngắn gọn cơ chế gọi LLM và cách AI nhận biết nguồn tin cậy.
  * Sẵn sàng trả lời câu hỏi của giám khảo: *"Nếu học viên cố tình spam tin giả thì bot xử lý thế nào?"*, *"Vì sao lại chọn prompt này mà không phải chia thành nhiều bước agent?"*.
