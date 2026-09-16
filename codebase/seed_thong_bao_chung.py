"""
seed_thong_bao_chung.py — Bơm tin nhắn MẪU (tự viết) vào kênh thông báo
CHUNG (onboarding, ghép đội, ticket hỗ trợ...). Dùng để test /tom-tat-thong-bao.

Tên kênh gợi ý: "thông-báo-chung" (phải chứa "thông-báo" để khớp filter
trong get_channel_announcements() ở tom_tat_bot.py).

Xem seed_test_channel.py để biết vì sao nội dung ở đây là tự soạn, không phải
nguyên văn dữ liệu K4 thật.

Cách dùng:
    1. Tạo kênh "thông-báo-chung" → Cài đặt kênh → Tích hợp → Webhook →
       New Webhook → Copy URL
    2. python seed_thong_bao_chung.py --webhook "<url>"
"""
import seed_lib

seed_lib.setup_utf8_console()

SAMPLE_MESSAGES = [
    ("BTC AI20K", "@everyone Chào mừng cả nhà đến với chương trình! Mọi người nhớ đổi tên theo cú pháp: Mã nhóm - Họ và tên - 5 số cuối MSSV để BTC dễ theo dõi điểm cộng nhé."),
    ("BTC AI20K", "🗓️ Hạn hoàn thành onboarding (xác minh danh tính + kết nối Discord) là 21:00 hôm nay. Sau giờ đó hệ thống sẽ tự ghép đội cho các bạn chưa tìm được nhóm."),
    ("BTC AI20K", "Nhắc lại: khác lớp vẫn ghép chung team được, miễn là cùng một khoá và cùng level nhé. Một team tối đa 5 thành viên."),
    ("BTC AI20K", "Gặp vướng mắc gì trong lúc onboarding thì mở ticket giúp mình nha: gõ lệnh /ticket create tại kênh hỗ trợ, chọn đúng loại vấn đề để được xử lý nhanh hơn."),
    ("BTC AI20K", "📢 Ngân hàng đề tài chính thức sẽ công bố vào 22:00 tối nay. Các team đọc kỹ mô tả từng đề trước khi đăng ký, mỗi đề chỉ nhận tối đa 2 team."),
]


def main():
    ap = seed_lib.build_arg_parser(__doc__)
    args = ap.parse_args()
    seed_lib.send_messages(args.webhook, SAMPLE_MESSAGES, args.delay)


if __name__ == "__main__":
    main()
