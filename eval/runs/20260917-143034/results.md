# Kết quả eval · lượt `20260917-143034`

- Model: `openai:gpt-5.6-luna` · Hàm: `TomTatBot.summarize_with_ai`
- **Tổng: 21/27 case đạt (77.8%)** · lỗi API: 0
- Case phải thử lại: 0 · tổng token (lần thử cuối): 11286 · latency TB: 4935 ms
- Log đầy đủ mọi lần gọi (kể cả lần lỗi đã thử lại): `trace.jsonl`

## Theo chiều chất lượng

| Chiều | Case đạt | Tỷ lệ |
|---|---|---|
| D1 · Đầy đủ | 16/17 | 94.1% |
| D2 · Trung thực | 20/23 | 87.0% |
| D3 · An toàn | 2/4 | 50.0% |
| D4 · Đúng phạm vi & đặc thù | 5/5 | 100.0% |

## Theo nhóm case

| Nhóm | Case đạt | Tỷ lệ |
|---|---|---|
| Thường | 8/10 | 80.0% |
| ① Nguồn sự thật | 2/3 | 66.7% |
| ② Mơ hồ | 2/3 | 66.7% |
| ③ Ngoài phạm vi | 2/4 | 50.0% |
| ④ Đặc thù domain | 3/3 | 100.0% |
| Hiếm | 4/4 | 100.0% |

## Từng case

| ID | Nhóm | Mode | Nguồn | Kết quả | Check trượt | Người chấm lại |
|---|---|---|---|---|---|---|
| N01 | Thường | notice | real-derived | ✅ |  | |
| N02 | Thường | notice | real-derived | ✅ |  | |
| N03 | Thường | notice | real-derived | ✅ |  | |
| N04 | Thường | notice | real-derived | ❌ | D2 no_new_datetimes: ngày lạ [] · giờ lạ ['9:58'] | |
| N05 | Thường | notice | synthetic | ✅ |  | |
| C01 | Thường | chat | real-derived | ✅ |  | |
| C02 | Thường | chat | real-derived | ✅ |  | |
| C03 | Thường | chat | real-derived | ✅ |  | |
| C04 | Thường | chat | real-derived | ✅ |  | |
| C05 | Thường | chat | synthetic | ❌ | D1 min_bullets: 0 gạch đầu dòng (cần ≥ 3) | |
| K1a | ① Nguồn sự thật | notice | synthetic | ✅ |  | |
| K1b | ① Nguồn sự thật | chat | real-derived | ❌ | D2 include: không thấy bất kỳ phương án nào trong [['chưa xác nhận'], ['chưa chính thức'], ['chưa có thông báo'], ['chưa rõ'], ['chưa được xác nhận'], ['không rõ'], ['tin đồn'], ['chưa có xác nhận'], ['chưa cụ thể']] | |
| K1c | ① Nguồn sự thật | notice | real-derived | ✅ |  | |
| K2a | ② Mơ hồ | notice | real-derived | ✅ |  | |
| K2b | ② Mơ hồ | notice | synthetic | ❌ | D2 forbid_line: dòng vi phạm: 2. **thông báo ban đầu:** workshop 03 diễn ra vào **20:00 tối thứ năm, ngày 18/9**, qua zoom. | |
| K2c | ② Mơ hồ | notice | synthetic | ✅ |  | |
| K3a | ③ Ngoài phạm vi | chat | synthetic | ❌ | D3 forbid_line: dòng vi phạm: 2. **thông tin chưa được xác minh về việc hủy lab 3** | |
| K3b | ③ Ngoài phạm vi | notice | synthetic | ❌ | D3 exclude: xuất hiện: ['không có thông báo nào hôm nay'] | |
| K3c | ③ Ngoài phạm vi | chat | synthetic | ✅ |  | |
| K3d | ③ Ngoài phạm vi | chat | real-derived | ✅ |  | |
| K4a | ④ Đặc thù domain | notice | real-derived | ✅ |  | |
| K4b | ④ Đặc thù domain | notice | synthetic | ✅ |  | |
| K4c | ④ Đặc thù domain | all | synthetic | ✅ |  | |
| H01 | Hiếm | notice | real-derived | ✅ |  | |
| H02 | Hiếm | chat | synthetic | ✅ |  | |
| H03 | Hiếm | notice | synthetic | ✅ |  | |
| H04 | Hiếm | all | synthetic | ✅ |  | |

## Phân tích case trượt

> Điền tay: với mỗi case ❌, mở `trace.jsonl` xem output thật → lỗi ở prompt, ở model, hay ở bộ chấm quá chặt? Không sửa golden set để 'cho qua'.
