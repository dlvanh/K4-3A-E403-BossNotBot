# 🚀 Khởi Động Nhanh Bot Tom Tát

## ⚡ 5 Bước để Chạy Bot

### 1. Tạo Discord Bot & Lấy Token
```
1. Vào https://discord.com/developers/applications
2. New Application → Tên: "Tom Tat"
3. Tab "Bot" → Add Bot
4. Copy TOKEN
5. Bật "Message Content Intent"
6. OAuth2 → URL Generator → Scopes: bot → Permissions: Send Messages, Read Messages, Read History
7. Copy URL → Paste vào browser → Invite vào server
```

### 2. Lấy OpenAI API Key
```
1. Vào https://platform.openai.com/api-keys
2. Create new secret key
3. Copy API Key
```

### 3. Cài Packages
```bash
pip install -r requirements.txt
```

### 4. Tạo file `.env`
```
Đổi tên `.env.example` thành `.env` và điền:

DISCORD_TOKEN=paste_token_here
OPENAI_API_KEY=paste_key_here
```

### 5. Chạy Bot
```bash
python tom_tat_bot.py
```

---

## 💬 Dùng Bot

Sau khi bot online trong Discord:

```
/tom-tat-thong-bao              → Tóm tắt thông báo
/tom-tat-tro-chuyen #kênh      → Tóm tắt kênh
/tom-tat-chung                  → Tóm tắt toàn bộ
```

---

## 🐛 Lỗi Thường Gặp

| Lỗi | Giải Pháp |
|-----|-----------|
| Bot không online | Kiểm tra token & Message Content Intent |
| Lỗi "No module named discord" | `pip install discord.py` |
| Bot không đọc tin nhắn | Kiểm tra quyền Read Message History |
| API Error | Kiểm tra OPENAI_API_KEY hợp lệ |

---

**Xong! Bot đã sẵn sàng 🎉**
