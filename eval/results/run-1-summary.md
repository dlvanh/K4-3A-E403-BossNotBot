# Eval run 1 — bảng kết quả (dùng cho spec.md §7)

Chạy lúc: 2026-09-17 14:19 · model=gpt-4o-mini · 3 case (golden_set.py)

**Tổng: 3/3 case đạt cả 3 chiều tự động (100.0%).** citation_validity 3/3 · coverage 3/3 · format_compliance 3/3.

> 3 chiều dưới đây chấm được bằng máy (không bịa số trích dẫn, không bỏ sót tin, đúng cấu trúc bắt buộc). Đúng-sai về **nội dung** (có bịa sự thật, phân loại ưu tiên có hợp lý, có bị prompt injection dắt mũi không) cần người đọc — xem cột 'Cần người đọc lại'.

| Case | Mode | Lớp/Bucket | n | citation | coverage | format | Auto | Cần người đọc lại |
|---|---|---|---|---|---|---|---|---|
| N4 | notice | layer1 | 1 | ✅ | ✅ 1/1 | ✅ | ✅ | ① nguồn sự thật — input không có deadline/ngày giờ cụ thể nào |
| N6 | notice | hiem | 1 | ✅ | ✅ 1/1 | ✅ | ✅ | case hiếm — chỉ 1 thông báo duy nhất trong khung giờ |
| C9 | chat | hiem | 3 | ✅ | ✅ 3/3 | ✅ | ✅ | case hiếm — cực ít tin (3 tin) trong cả khung 4h |

## Trích ngắn từng case (≤2 câu/ví dụ, kèm msg_id — theo luật data pack)

- **N4** (M47011…): Chỉ 1 tin: yêu cầu đổi tên theo cú pháp, không có hạn chót nào được nêu.
  - Output (trích): _**🔴 Ưu tiên cao** 1. Tất cả học viên cần đổi tên theo cú pháp: Mã Nhóm - Họ và tên - 5 số cuối mã sinh viên để BTC và Lab Coach dễ dàng quản…_
- **N6** (M21817…): Chỉ 1 tin: workshop tối nay.
  - Output (trích): _**🔴 Ưu tiên cao**  1. Tham gia workshop online vào tối nay (13/09) lúc 20:00 với chủ đề "Problem → MVP Canvas". Vui lòng vào sớm 10 phút để …_
- **C9** (M21463…): Cụm chat 10:39-11:14 14/9 channel_11: chỉ 3 tin, 2 chủ đề không liên quan nhau (điểm danh daily vs offline, gợi ý dùng Deepseek).
  - Output (trích): _### Các chủ đề chính: 1. **Điểm danh trong lớp học**: Người hỏi thắc mắc về việc nộp bài daily standup muộn thì có bị ảnh hưởng đến điểm dan…_
