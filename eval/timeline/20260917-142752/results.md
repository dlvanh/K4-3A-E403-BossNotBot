# Timeline replay · `20260917-142752`

Giả lập gọi lệnh tóm tắt mỗi 60 phút trong 12/09 07:00 → 14/09 23:54 (65 thời điểm). Logic chọn tin mô phỏng `tom_tat_bot.py`: thông báo 24h / 20 tin mỗi kênh, trò chuyện 4h / 50 tin thô. Không gọi AI. Bot chỉ thấy tin ≤ thời điểm hỏi.

| Chỉ số | Kết quả |
|---|---|
| A · Thông báo còn hiệu lực tới được AI | 118/136 lượt (86.8%) |
| B · Tin trò chuyện trong cửa sổ tới được AI | 2496/2882 (86.6%) |
| C · Câu hỏi đang tồn (≤24h, chưa reply) tới được AI | 141/668 (21.1%) · 31 câu từng bị mất dấu |
| D · Thời điểm hỏi gặp 'hôm nay/ngày mai' đã lệch ngày | 34/65 |

## A · Thông báo có hạn

| msg_id | Nội dung (diễn đạt lại) | Đăng | Hết hiệu lực | Lượt tới AI | Rơi khỏi cửa sổ từ | Tổng khoảng mù | Giả định |
|---|---|---|---|---|---|---|---|
| M49744 | Hạn hoàn tất onboarding + ghép đội tự do (L2-3) | 12/09 18:02 | 13/09 21:00 | 24/26 | 13/09 19:00 | 3.0h |  |
| M21817 | Workshop 02 tối 13/9 | 13/09 08:42 | 13/09 20:00 | 11/11 | — | 0.0h |  |
| M16114 | Lab ngày 14/9 cần CVAT — cài trước | 13/09 11:21 | 14/09 23:59 | 24/36 | 14/09 12:00 | 12.6h | Thông báo chỉ ghi 'ngày mai', không có giờ; lấy hết ngày 14/9 |
| M41530 | Hạn hoàn tất onboarding (L3-4, remind) | 14/09 09:15 | 14/09 21:00 | 11/11 | — | 0.0h |  |
| M09449 | Hạn đăng ký đề tài | 13/09 21:49 | 20/09 23:59 | 24/26 | 14/09 22:00 | 146.2h |  |
| M91836 | Link ngân hàng đề tài (cần tới hạn đăng ký) | 13/09 22:00 | 20/09 23:59 | 24/26 | 14/09 22:00 | 146.0h |  |

*Lượt tới AI chỉ tính trong phạm vi pack; tổng khoảng mù tính tới hạn thật, kể cả sau khi pack kết thúc.*

## B · Kênh trò chuyện

| Kênh | Lần gọi bị cắt | Tin người giữ lại | Tệ nhất |
|---|---|---|---|
| K4-L2-3 channel_02 | 4/40 | 94.4% | 12/09 23:00: 68 tin người trong cửa sổ, AI nhận 50 |
| K4-L2-3 channel_08 | 0/21 | 100.0% | — |
| K4-L3-4 channel_10 | 19/60 | 73.5% | 14/09 12:00: 70 tin người trong cửa sổ, AI nhận 25 |
| K4-L3-4 channel_11 | 0/57 | 100.0% | — |

## C · Câu hỏi từng bị mất dấu khi chưa ai trả lời

M01360, M02015, M04392, M09813, M12802, M14882, M18056, M19124, M21374, M27566, M28943, M30246, M33885, M36687, M40118, M42852, M48859, M57197, M60122, M66800, M67317, M67980, M71241, M83398, M84013, M87936, M88027, M91580, M97172, M97637, M99769

## D · Thông báo có thời gian tương đối bị đưa vào AI sau khi đã sang ngày khác

| msg_id | Đăng | Từ | Số thời điểm hỏi bị ảnh hưởng |
|---|---|---|---|
| M09449 | 13/09 21:49 | hôm nay | 22 |
| M16114 | 13/09 11:21 | ngày mai | 12 |
| M16982 | 13/09 08:59 | hôm nay | 9 |
| M21817 | 13/09 08:42 | hôm nay, tối nay | 9 |
| M31445 | 13/09 08:58 | sáng nay | 9 |

> Bot chỉ gửi AI giờ `HH:MM`, không gửi ngày đăng và thời điểm tóm tắt, nên AI không thể biết 'ngày mai' đã thành 'hôm nay'.
