"""
seed_thong_bao_build.py — Bơm tin nhắn MẪU (tự viết) vào kênh thông báo
BUILD PHASE (deadline Gate, AI Log, quy định đề tài...). Dùng để test
/tom-tat-thong-bao.

Tên kênh gợi ý: "thông-báo-build" (phải chứa "thông-báo" để khớp filter
trong get_channel_announcements() ở tom_tat_bot.py).

Xem seed_test_channel.py để biết vì sao nội dung ở đây là tự soạn, không phải
nguyên văn dữ liệu K4 thật.

Cách dùng:
    1. Tạo kênh "thông-báo-build" → Cài đặt kênh → Tích hợp → Webhook →
       New Webhook → Copy URL
    2. python seed_thong_bao_build.py --webhook "<url>"
"""
import seed_lib

seed_lib.setup_utf8_console()

SAMPLE_MESSAGES = [
    ("BTC Build Phase", "📌 Gate 1 - Chốt đề tài: hạn nộp 23:59 Chủ nhật tuần sau. Deliverables gồm Brief, PRD, Wireframe và GitHub repo đã setup AI Log."),
    ("BTC Build Phase", "Nhắc các team setup AI Log Hook càng sớm càng tốt, tốt nhất là ngay tuần 1, để log đủ toàn bộ phiên làm việc đến Demo Day."),
    ("BTC Build Phase", "Mỗi đề tài trong ngân hàng chỉ nhận tối đa 2 team đăng ký, nếu trùng thì ai đăng ký trước qua lệnh /topic pick sẽ được ưu tiên."),
    ("BTC Build Phase", "Về việc dùng GitHub: bắt buộc push code vào repo trong GitHub Org của chương trình, không tách sang GitLab hay repo cá nhân vì hệ thống chỉ đọc log từ Org chính thức."),
    ("BTC Build Phase", "Muốn đề xuất đề tài ngoài ngân hàng thì mở ticket loại new-topic, mô tả rõ bài toán để BTC xét duyệt nhé."),
]


def main():
    ap = seed_lib.build_arg_parser(__doc__)
    args = ap.parse_args()
    seed_lib.send_messages(args.webhook, SAMPLE_MESSAGES, args.delay)


if __name__ == "__main__":
    main()
