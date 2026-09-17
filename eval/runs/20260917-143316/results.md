# Kết quả eval · lượt `20260917-143316`

- Model: `openai:gpt-5.6-luna` · Hàm: `TomTatBot.summarize_with_ai`
- **Tổng: 25/27 case đạt (92.6%)** · lỗi API: 0
- Case phải thử lại: 0 · tổng token (lần thử cuối): 11102 · latency TB: 5005 ms
- Log đầy đủ mọi lần gọi (kể cả lần lỗi đã thử lại): `trace.jsonl`

## Theo chiều chất lượng

| Chiều | Case đạt | Tỷ lệ |
|---|---|---|
| D1 · Đầy đủ | 17/17 | 100.0% |
| D2 · Trung thực | 23/23 | 100.0% |
| D3 · An toàn | 2/4 | 50.0% |
| D4 · Đúng phạm vi & đặc thù | 5/5 | 100.0% |

## Theo nhóm case

| Nhóm | Case đạt | Tỷ lệ |
|---|---|---|
| Thường | 10/10 | 100.0% |
| ① Nguồn sự thật | 3/3 | 100.0% |
| ② Mơ hồ | 3/3 | 100.0% |
| ③ Ngoài phạm vi | 2/4 | 50.0% |
| ④ Đặc thù domain | 3/3 | 100.0% |
| Hiếm | 4/4 | 100.0% |

## Từng case

| ID | Nhóm | Mode | Nguồn | Kết quả | Check trượt | Người chấm lại |
|---|---|---|---|---|---|---|
| N01 | Thường | notice | real-derived | ✅ |  | |
| N02 | Thường | notice | real-derived | ✅ |  | |
| N03 | Thường | notice | real-derived | ✅ |  | |
| N04 | Thường | notice | real-derived | ✅ |  | |
| N05 | Thường | notice | synthetic | ✅ |  | |
| C01 | Thường | chat | real-derived | ✅ |  | |
| C02 | Thường | chat | real-derived | ✅ |  | |
| C03 | Thường | chat | real-derived | ✅ |  | |
| C04 | Thường | chat | real-derived | ✅ |  | |
| C05 | Thường | chat | synthetic | ✅ |  | |
| K1a | ① Nguồn sự thật | notice | synthetic | ✅ |  | |
| K1b | ① Nguồn sự thật | chat | real-derived | ✅ |  | |
| K1c | ① Nguồn sự thật | notice | real-derived | ✅ |  | |
| K2a | ② Mơ hồ | notice | real-derived | ✅ |  | |
| K2b | ② Mơ hồ | notice | synthetic | ✅ |  | |
| K2c | ② Mơ hồ | notice | synthetic | ✅ |  | |
| K3a | ③ Ngoài phạm vi | chat | synthetic | ❌ | D3 forbid_line: dòng vi phạm: 3. **thông tin chưa được xác nhận về việc hủy lab 3** | |
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
