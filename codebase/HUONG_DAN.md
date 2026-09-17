# Bot Tom Tát - Discord Bot Tóm Tắt Tin Nhắn

Bot **Tom Tat** giúp bạn tóm tắt các thông báo và trò chuyện trên Discord bằng AI.

## ✨ Tính năng

Bot dùng **slash command thật của Discord** — gõ `/` trong kênh là thấy menu gợi ý đầy đủ. Kết quả tóm tắt chỉ hiện cho người gọi lệnh thấy (ephemeral), không làm phiền kênh chung.

- `/tom-tat-thong-bao` - Tóm tắt các thông báo trong 24h, từ các kênh đã đăng ký
- `/tom-tat-tro-chuyen [kenh]` - Tóm tắt trò chuyện trong 4h gần nhất
- `/them-kenh-thong-bao [kenh]` - Đăng ký kênh này (hoặc kênh chỉ định) làm nguồn thông báo, bot nhớ đến khi bỏ đăng ký
- `/xoa-kenh-thong-bao [kenh]` - Bỏ đăng ký kênh khỏi nguồn thông báo
- `/ds-kenh-thong-bao` - Xem danh sách kênh thông báo đã đăng ký

Khi bot khởi động lần đầu trong 1 server, nó tự động quét và đăng ký sẵn các kênh có tên chứa "thông-báo"/"announce" (chỉ làm 1 lần — sau đó gỡ kênh nào bằng `/xoa-kenh-thong-bao` thì kênh đó không tự quay lại nữa).

Mỗi điểm trong bản tóm tắt đều có link **[nguồn]** nhảy thẳng tới đúng tin nhắn gốc trên Discord, cộng thêm 1 embed liệt kê đầy đủ tin nhắn nguồn hiện ra đầu tiên để đối chiếu.

---

## 📋 Yêu cầu

- Python 3.8 trở lên
- Discord Bot Token
- OpenAI API Key

---

## 🚀 Cách Cài Đặt & Chạy

### Bước 1: Tạo Discord Bot

1. Vào https://discord.com/developers/applications
2. Click **"New Application"** → Đặt tên (ví dụ: "Tom Tat")
3. Vào tab **"Bot"** → Click **"Add Bot"**
4. Dưới **TOKEN** → Click **"Copy"** → Lưu token này
5. Bật các **Intents** sau:
   - ✅ **Message Content Intent** (quan trọng!)
   - ✅ **Server Members Intent**
   - ✅ **Guild Messages**

6. Vào tab **"OAuth2" → "URL Generator"**
7. Chọn scopes: `bot`
8. Chọn permissions:
   - ✅ Send Messages
   - ✅ Read Messages/View Channels
   - ✅ Embed Links
   - ✅ Read Message History
9. Copy URL được tạo → Dán vào trình duyệt để invite bot vào server

### Bước 2: Lấy API Keys

#### Lấy OpenAI API Key:
1. Vào https://platform.openai.com/api-keys
2. Login/Signup với tài khoản của bạn
3. Click **"Create new secret key"** → Copy API key

#### Discord Bot Token:
- Đã lấy ở Bước 1

### Bước 3: Cài Đặt Python Packages

```bash
# Windows
pip install -r requirements.txt

# macOS/Linux
pip3 install -r requirements.txt
```

### Bước 4: Tạo file `.env`

Tạo file `.env` trong cùng thư mục với `tom_tat_bot.py`:

```env
DISCORD_TOKEN=your_discord_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
```

**Ví dụ:**
```env
DISCORD_TOKEN=MTE0NzQxNzE4NzY2NTAwNzYyMA.GzKpL2.abc123xyz456...
OPENAI_API_KEY=sk-proj-abc123xyz456...
```

### Bước 5: Chạy Bot

#### Cách 1: Chạy trực tiếp (Windows/macOS/Linux)
```bash
python tom_tat_bot.py
```

Nếu dùng Python 3:
```bash
python3 tom_tat_bot.py
```

Bot sẽ yêu cầu nhập token nếu không tìm thấy file `.env`.

#### Cách 2: Chạy với biến môi trường

**Windows (Command Prompt):**
```cmd
set DISCORD_TOKEN=your_token_here
set OPENAI_API_KEY=your_key_here
python tom_tat_bot.py
```

**Windows (PowerShell):**
```powershell
$env:DISCORD_TOKEN='your_token_here'
$env:OPENAI_API_KEY='your_key_here'
python tom_tat_bot.py
```

**macOS/Linux:**
```bash
export DISCORD_TOKEN='your_token_here'
export OPENAI_API_KEY='your_key_here'
python3 tom_tat_bot.py
```

---

## 📖 Cách Sử Dụng

Sau khi bot online, sử dụng các command trong Discord:

### 0️⃣ Quản lý kênh thông báo
```
/them-kenh-thong-bao
/xoa-kenh-thong-bao
/ds-kenh-thong-bao
```
Bot tự động đăng ký sẵn các kênh có tên chứa "thông-báo" khi mới khởi động trong 1 server (chỉ 1 lần). Muốn thêm/bớt thủ công thì dùng 2 lệnh trên — bot nhớ vĩnh viễn (kể cả restart) đến khi bạn đổi lại. Dùng `/ds-kenh-thong-bao` để xem hiện đang đăng ký kênh nào.

### 1️⃣ Tóm tắt Thông báo
```
/tom-tat-thong-bao
```
→ Tóm tắt tất cả thông báo trong 24h từ các kênh đã đăng ký ở trên. Chỉ bạn (người gõ lệnh) thấy được kết quả.

### 2️⃣ Tóm tắt Trò Chuyện
```
/tom-tat-tro-chuyen kenh:#tên-kênh
```
→ Tóm tắt 4h tin nhắn gần nhất từ kênh đó. Không chỉ định `kenh` thì tóm tắt kênh hiện tại.

---

## 🔧 Khắc Phục Sự Cố

### ❌ "Bot không kết nối được"
- Kiểm tra token có đúng không
- Kiểm tra Message Content Intent có bật chưa

### ❌ "Bot không đọc được tin nhắn"
- Kiểm tra bot có quyền "Read Message History" không
- Kiểm tra bot có quyền trong kênh đó không

### ❌ "Không tìm thấy tin nhắn nào"
- Thử vào kênh có tin nhắn trong 4h gần đây không?
- Kênh thông báo đã được `/them-kenh-thong-bao` hoặc tự động quét chưa? Kiểm tra bằng `/ds-kenh-thong-bao`
- Xem log `[debug]` trong terminal chạy bot — có ghi rõ quét được bao nhiêu tin thô, giữ lại bao nhiêu tin sau lọc

### ❌ "API Error: Lỗi từ OpenAI"
- Kiểm tra OPENAI_API_KEY có đúng không
- Kiểm tra quota API của bạn có đủ không (https://platform.openai.com/usage)

---

## 📦 Cấu Trúc File

```
tom-tat-bot/
├── tom_tat_bot.py                  # File chính của bot
├── replay_test.py                  # Test tóm tắt AI ngoại tuyến bằng dữ liệu k4_messages.csv (không cần Discord)
├── seed_lib.py                     # Hàm dùng chung để bơm tin nhắn mẫu qua Webhook
├── seed_test_channel.py            # Seed 1 kênh chat mẫu (để test /tom-tat-tro-chuyen)
├── seed_thong_bao_chung.py         # Seed kênh thông báo chung mẫu
├── seed_thong_bao_lop_hoc.py       # Seed kênh thông báo lớp học mẫu
├── seed_thong_bao_build.py         # Seed kênh thông báo Build Phase mẫu
├── seed_thong_bao_workshop.py      # Seed kênh thông báo workshop mẫu
├── requirements.txt                # Các thư viện cần cài
├── .env                            # File config (tạo riêng, không commit)
└── HUONG_DAN.md                    # File hướng dẫn này
```

---

## 🔐 Bảo Mật

⚠️ **QUAN TRỌNG:**
- ❌ Không chia sẻ `DISCORD_TOKEN` và `OPENAI_API_KEY`
- ❌ Không commit `.env` lên Git (`.gitignore` của repo đã chặn sẵn)
- ❌ Nếu token bị lộ → Vào Discord Developers xoá đi, tạo cái mới
- ❌ Không dán nguyên văn dữ liệu `data/discord-pack/` lên kênh demo — dùng `replay_test.py` để test cục bộ, hoặc các script `seed_*.py` (nội dung mẫu tự soạn) để demo trên server test

---

## 📝 Ghi Chú

- Bot sẽ đọc tin nhắn có tính năng "Message Content Intent"
- Chỉ tóm tắt tin nhắn từ user, bỏ qua tin từ bot khác
- Thời gian lấy tin nhắn:
  - Thông báo: 24 giờ
  - Trò chuyện: 4 giờ
  - Giới hạn: tối đa 50 tin nhắn/kênh

---

## 💡 Mẹo

- Dùng `/them-kenh-thong-bao` nếu bot chưa tự nhận diện đúng kênh thông báo (tên kênh không dấu như "thong-bao" vẫn khớp, nhưng tên khác hẳn thì phải đăng ký tay)
- Dùng command trong các kênh có nhiều tin nhắn để kết quả tốt hơn
- AI sẽ nhóm theo chủ đề và highlight những vấn đề chưa giải quyết
- Mỗi bản tóm tắt có kèm link tin nhắn nguồn — dùng để đối chiếu AI tóm đúng chưa

---

## 🤝 Hỗ Trợ

Nếu có lỗi, kiểm tra:
1. Python version ≥ 3.8
2. Tất cả packages đã cài (kiểm tra: `pip list`)
3. Token/API key có hợp lệ
4. Bot có quyền đọc kênh
5. File `.env` nếu dùng

---

**Chúc bạn sử dụng vui vẻ! 🎉**
