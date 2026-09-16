"""
seed_thong_bao_workshop.py — Bơm tin nhắn MẪU (tự viết) vào kênh thông báo
WORKSHOP/ZOOM (lịch, cú pháp đặt tên, passcode...). Dùng để test
/tom-tat-thong-bao.

Tên kênh gợi ý: "thông-báo-workshop" (phải chứa "thông-báo" để khớp filter
trong get_channel_announcements() ở tom_tat_bot.py).

Xem seed_test_channel.py để biết vì sao nội dung ở đây là tự soạn, không phải
nguyên văn dữ liệu K4 thật.

Cách dùng:
    1. Tạo kênh "thông-báo-workshop" → Cài đặt kênh → Tích hợp → Webhook →
       New Webhook → Copy URL
    2. python seed_thong_bao_workshop.py --webhook "<url>"
"""
import seed_lib

seed_lib.setup_utf8_console()

SAMPLE_MESSAGES = [
    ("BTC AI20K", "🚀 Workshop định kỳ diễn ra tối thứ 5 và chủ nhật hàng tuần, 20:00 qua Zoom. Các bạn nhớ vào sớm 10 phút để ổn định kỹ thuật nhé."),
    ("BTC AI20K", "Cú pháp đặt tên khi vào Zoom: Mã nhóm - Mã đội - Họ và tên. Đặt sai cú pháp thì hệ thống sẽ không điểm danh tự động được đâu."),
    ("BTC AI20K", "Nhớ đăng nhập Zoom bằng đúng email đã đăng ký với chương trình, dùng email khác thì không được ghi nhận điểm danh."),
    ("BTC AI20K", "Link Zoom cố định và passcode được ghim ở đầu kênh này, các bạn kiểm tra lại nếu quên."),
    ("BTC AI20K", "Buổi tối nay là Workshop chủ đề Problem → MVP Canvas, mong các bạn tham gia đầy đủ và tương tác trong khung chat để được tính điểm chuyên cần."),
]


def main():
    ap = seed_lib.build_arg_parser(__doc__)
    args = ap.parse_args()
    seed_lib.send_messages(args.webhook, SAMPLE_MESSAGES, args.delay)


if __name__ == "__main__":
    main()
