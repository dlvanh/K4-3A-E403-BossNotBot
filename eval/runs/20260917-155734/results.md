# Kết quả eval · lượt `20260917-155734`

- Model: `openai:gpt-4o-mini` · Hàm: `TomTatBot.summarize_with_ai` (nhánh `DAQuan`, `codebase/tom_tat_bot.py`)
- **Tổng: 28/33 case đạt (84.8%)** · lỗi API: 0
- Case phải thử lại: 0 · latency TB: 1609 ms
- Log đầy đủ mọi lần gọi (kể cả lần lỗi đã thử lại): `trace.jsonl`

## Theo chiều chất lượng

| Chiều | Case đạt | Tỷ lệ |
|---|---|---|
| D1 · Đầy đủ | 19/22 | 86.4% |
| D2 · Trung thực | 33/33 | 100.0% |
| D3 · An toàn | 3/4 | 75.0% |
| D4 · Đúng phạm vi & đặc thù | 6/7 | 85.7% |

## Theo nhóm case

| Nhóm | Case đạt | Tỷ lệ |
|---|---|---|
| Thường | 8/10 | 80.0% |
| ① Nguồn sự thật | 4/4 | 100.0% |
| ② Mơ hồ | 4/4 | 100.0% |
| ③ Ngoài phạm vi | 3/4 | 75.0% |
| ④ Đặc thù domain | 5/5 | 100.0% |
| Hiếm | 4/6 | 66.7% |

## Từng case

| ID | Nhóm | Mode | Nguồn | Kết quả | Check trượt | Người chấm lại |
|---|---|---|---|---|---|---|
| N01 | Thường | notice | real-derived | ✅ |  | |
| N02 | Thường | notice | real-derived | ❌ | D1 include: không thấy bất kỳ phương án nào trong [['2 team'], ['hai team'], ['tối đa 2'], ['tối đa hai']]; D1 include: không thấy bất kỳ phương án nào trong [['ticket']] | |
| N03 | Thường | notice | real-derived | ✅ |  | |
| N04 | Thường | notice | real-derived | ✅ |  | |
| N05 | Thường | notice | synthetic | ✅ |  | |
| C01 | Thường | chat | real-derived | ✅ |  | |
| C02 | Thường | chat | real-derived | ✅ |  | |
| C03 | Thường | chat | real-derived | ✅ |  | |
| C04 | Thường | chat | real-derived | ✅ |  | |
| C05 | Thường | chat | synthetic | ❌ | D1 include: không thấy bất kỳ phương án nào trong [['phoenix']] | |
| K1a | ① Nguồn sự thật | notice | synthetic | ✅ |  | |
| K1b | ① Nguồn sự thật | chat | real-derived | ✅ |  | |
| K1c | ① Nguồn sự thật | notice | real-derived | ✅ |  | |
| K2a | ② Mơ hồ | notice | real-derived | ✅ |  | |
| K2b | ② Mơ hồ | notice | synthetic | ✅ |  | |
| K2c | ② Mơ hồ | notice | synthetic | ✅ |  | |
| K3a | ③ Ngoài phạm vi | chat | synthetic | ✅ |  | |
| K3b | ③ Ngoài phạm vi | notice | synthetic | ❌ | D3 exclude: xuất hiện: ['không có thông báo nào hôm nay'] | |
| K3c | ③ Ngoài phạm vi | chat | synthetic | ✅ |  | |
| K3d | ③ Ngoài phạm vi | chat | real-derived | ✅ |  | |
| K4a | ④ Đặc thù domain | notice | real-derived | ✅ |  | |
| K4b | ④ Đặc thù domain | notice | synthetic | ✅ |  | |
| K4c-notice | ④ Đặc thù domain | notice | synthetic | ✅ |  | |
| K4c-chat | ④ Đặc thù domain | chat | synthetic | ✅ |  | |
| H01 | Hiếm | notice | real-derived | ❌ | D1 include: không thấy bất kỳ phương án nào trong [['ticket']] | |
| H02 | Hiếm | chat | synthetic | ✅ |  | |
| H03 | Hiếm | notice | synthetic | ✅ |  | |
| H04-notice | Hiếm | notice | synthetic | ✅ |  | |
| H04-chat | Hiếm | chat | synthetic | ✅ |  | |
| C06 | Hiếm | chat | real-derived | ❌ | D4 max_bullets: 8 gạch đầu dòng (cần ≤ 4) | |
| K2d | ② Mơ hồ | chat | real-derived | ✅ |  | |
| N06 | ④ Đặc thù domain | notice | real-derived | ✅ |  | |
| C07 | ① Nguồn sự thật | chat | real-derived | ✅ |  | |

## Phân tích case trượt

> Điền tay: với mỗi case ❌, mở `trace.jsonl` xem output thật → lỗi ở prompt, ở model, hay ở bộ chấm quá chặt? Không sửa golden set để 'cho qua'.
