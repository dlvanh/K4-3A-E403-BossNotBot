# NHẬT KÝ VALIDATION VỚI NGƯỜI DÙNG (KHỐI R6 — BONUS +8 ĐIỂM)
**Người thực hiện:** Lại Bá Quân (`2A202602495`) · **Nhóm:** `BossNotBot` · **Phòng:** E403  
**Dự án:** Discord Smart Digest (Bản tin 30 giây cá nhân hóa)  
**Tiêu chí Rubric R6:** $\ge 2$ người dùng ngoài nhóm test prototype thật + ghi log nguyên văn + có $\ge 1$ thay đổi đưa vào Changelog hoặc giữ nguyên có lý do.

---

## I. KỊCH BẢN TEST 5 NHỊP (10 PHÚT / USER)
1. **Nhịp 1 — Comfort (1'):** *"Bọn mình đang đánh giá phần mềm xem có dễ dùng không, hoàn toàn không đánh giá bạn. Bạn cứ tự nhiên vừa thao tác vừa nói to suy nghĩ (think-aloud) nhé."*
2. **Nhịp 2 — Context (1'):** *"Hãy tưởng tượng bạn vừa đi làm cả ngày về lúc 19:30, mở Discord thấy hơn 200 tin nhắn chưa đọc và muốn biết trong tối nay mình cần nộp bài gì gấp và tài liệu mới nhất ở đâu."*
3. **Nhịp 3 — Task (1'):** Giao quyền điều khiển chuột/phím cho user:  
   - **Task 1:** Tìm xem trong vòng 24 giờ tới bạn có deadline nào cần nộp không và hạn chót là mấy giờ?
   - **Task 2:** Tìm link tài liệu hoặc slide mới nhất được nhắc đến.
   - **Task 3:** Bấm vào mã trích dẫn (`msg_id`) để kiểm tra xem thông tin tóm tắt có đúng tin gốc không.
4. **Nhịp 4 — Observe (5'):** **Người phỏng vấn im lặng quan sát 100%, ghi chép:**
   - Họ bấm vào đâu trước tiên? Có bị khựng lại hay nhầm lẫn nút bấm không?
   - Mất bao nhiêu giây để họ tìm thấy thẻ Deadline?
5. **Nhịp 5 — Ask (2'):**
   - *"Chỗ nào trên giao diện làm bạn lúng túng hoặc khó hiểu nhất?"*
   - *"Bạn có tin vào con số deadline này không — vì sao có / vì sao không?"*
   - *"Nếu ngày mai không được dùng công cụ này nữa, bạn cảm thấy thế nào?"*

---

## II. BẢNG NHẬT KÝ THỬ NGHIỆM CHI TIẾT

| Thông tin | User 1: Trần Minh T. (Lớp 3A) | User 2: Vũ Đức T. (Lớp 3B) |
|---|---|---|
| **Thời gian test** | 09:30 - 09:42 ngày 18/9/2026 | 10:30 - 10:43 ngày 18/9/2026 |
| **Bối cảnh user** | Học viên chính khóa, hay lo bị trôi bài Lab | Học viên đi làm, thường mở máy sau giờ làm |
| **Task đã giao** | 1. Tìm deadline 24h tới<br>2. Tìm link tài liệu<br>3. Kiểm chứng qua `msg_id` | 1. Tìm deadline 24h tới<br>2. Tìm link tài liệu<br>3. Kiểm chứng qua `msg_id` |
| **Thời gian hoàn thành** | 25 giây (Task 1: 8s, Task 2: 12s, Task 3: 5s) | 32 giây (Task 1: 10s, Task 2: 15s, Task 3: 7s) |
| **Quan sát hành vi** | - Mắt nhìn ngay vào thẻ Deadline màu đỏ đầu tiên.<br>- Bấm thử vào nút chip `[M72484]` xem có bung tin nhắn gốc không.<br>- Di chuột tìm nút copy tóm tắt sang clipboard. | - Đọc lướt qua dòng tóm tắt 30 giây trước.<br>- Thấy số lượng tin 654 tin nhắn thì gật đầu đồng cảm.<br>- Hơi ngập ngừng ở icon phân loại kênh. |
| **Quote nguyên văn (Lời khen & Thừa nhận)** | *"Nhìn vào phát biết luôn tối nay 23:59 nộp Lab02, đỡ phải lội ngược cả trăm tin nhắn."* | *"Cái này tiện cho người đi làm như mình, mở lên 10 giây là biết hôm nay phải làm gì."* |
| **Quote nguyên văn (Góp ý & Điểm chê)** | *"Cái mã tin nhắn `[M72484]` để chữ hơi nhỏ, với cả màu thẻ Deadline hơi giống thẻ Thông báo thường, nên làm đỏ hẳn lên để đập vào mắt."* | *"Mình muốn có thêm nút bấm nhảy thẳng đến đúng tin nhắn đó trên Discord để xem ngữ cảnh nếu cần."* |

---

## III. TỔNG HỢP 4 DÒNG KẾT LUẬN (BẮT BUỘC THEO RUBRIC R6)

1. **Chủ đề lặp lại nhiều nhất từ phản hồi:**  
   Người dùng muốn thẻ **Deadline** phải cực kỳ nổi bật về mặt thị giác (màu sắc cảnh báo rõ ràng), và mã trích dẫn nguồn tin (`msg_id`) cần kích thước lớn hơn, dễ bấm để đối soát tin cậy.
2. **Đề xuất sửa ngay trước buổi Demo (Actionable Feedback):**  
   - Đổi màu thẻ Deadline sang viền đỏ rực / badge cảnh báo nguy cấp (`Urgent: Red-500`).  
   - Tăng cỡ chữ và độ tương phản của mã tin nhắn nguồn `[M#####]`.  
   *(Đã báo cho Đoàn Anh Quân - Dev cập nhật UI; Đỗ Lê Việt Anh - PM ghi vào §9 Changelog của `spec.md`)*.
3. **Giữ nguyên cái gì & Vì sao:**  
   Giữ nguyên độ dài tóm tắt ở mức **3 gạch đầu dòng ngắn gọn** (dưới 100 từ). Mặc dù người dùng muốn thêm chi tiết thảo luận, nhưng việc giữ ngắn đảm bảo đúng cam kết cốt lõi: *"Bản tin 30 giây không gây quá tải ngược"*.
4. **Việc để dành phát triển sau Hackathon:**  
   Tính năng Deep link mở trực tiếp ứng dụng Discord Client tại đúng vị trí tin nhắn nguồn (`discord://...`), do cần API bot cấp quyền cao hơn.
