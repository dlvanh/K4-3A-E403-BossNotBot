# History replay · `20260917-142754`

- Model: `openai:gpt-5.6-luna` · Hàm: `TomTatBot.answer_from_history`
- Mỗi câu hỏi thật (tag bot) được trả lời từ **toàn bộ lịch sử tin nhắn trước thời điểm hỏi** (bỏ tin bot cũ: có · giới hạn lịch sử: 150). Trung bình 125 tin lịch sử/câu · tổng token 68568.
- **Có căn cứ (tự chấm): 10/10 (100.0%)** · trích mã bịa: 0 · trích tin tương lai: 0

Tự chấm chỉ kiểm được **căn cứ**: có trích mã tin, mã có thật, nằm trong lịch sử trước T; hoặc nói rõ không tìm thấy. **Đúng/sai nội dung phải người chấm** — mở `trace.jsonl` (không commit) so với tin nguồn và câu trả lời của bot cũ.

| Loại câu trả lời | Số câu |
|---|---|
| nói không tìm thấy / không xem được | 1 |
| trả lời có trích dẫn | 9 |

| Câu hỏi | Lúc hỏi | Server | Tin lịch sử | Loại | Trích dẫn | Lỗi căn cứ | Bot cũ trả lời | Người chấm: đúng? |
|---|---|---|---|---|---|---|---|---|
| M56157 | 12/09 06:57 | K4-L3-4 | 0 | nói không tìm thấy / không xem được | — | — | M83291 | |
| M72229 | 12/09 18:52 | K4-L3-4 | 64 | trả lời có trích dẫn | M00499 | — | M16680 | |
| M96792 | 13/09 11:14 | K4-L3-4 | 139 | trả lời có trích dẫn | M14918, M26655, M44966, M47007, M78232 | — | M23879 | |
| M39235 | 13/09 21:08 | K4-L3-4 | 150 | trả lời có trích dẫn | M21817, M24366 | — | M16492 | |
| M12653 | 13/09 23:41 | K4-L3-4 | 150 | trả lời có trích dẫn | M09449 | — | M90248 | |
| M31759 | 14/09 09:02 | K4-L3-4 | 150 | trả lời có trích dẫn | M49863, M76564 | — | M06366 | |
| M81080 | 14/09 10:12 | K4-L3-4 | 150 | trả lời có trích dẫn | M01069, M67171 | — | M96596 | |
| M02078 | 14/09 13:19 | K4-L3-4 | 150 | trả lời có trích dẫn | M41530, M47177 | — | M47687 | |
| M04785 | 14/09 16:12 | K4-L3-4 | 150 | trả lời có trích dẫn | M46207 | — | M59385 | |
| M82163 | 14/09 19:35 | K4-L3-4 | 150 | trả lời có trích dẫn | M78917 | — | M73469 | |
