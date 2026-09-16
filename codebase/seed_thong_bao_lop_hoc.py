"""
seed_thong_bao_lop_hoc.py — Bơm tin nhắn MẪU (tự viết) vào kênh thông báo
LỚP HỌC offline (slide, điểm danh, lịch trên trường...). Dùng để test
/tom-tat-thong-bao.

Tên kênh gợi ý: "thông-báo-lớp-học" (phải chứa "thông-báo" để khớp filter
trong get_channel_announcements() ở tom_tat_bot.py).

Xem seed_test_channel.py để biết vì sao nội dung ở đây là tự soạn, không phải
nguyên văn dữ liệu K4 thật.

Cách dùng:
    1. Tạo kênh "thông-báo-lớp-học" → Cài đặt kênh → Tích hợp → Webhook →
       New Webhook → Copy URL
    2. python seed_thong_bao_lop_hoc.py --webhook "<url>"
"""
import seed_lib

seed_lib.setup_utf8_console()

SAMPLE_MESSAGES = [
    ("Vlearn Admin", "Slide buổi học sáng nay đã được cập nhật trên nền tảng, các bạn vào Vlearn để xem lại nhé."),
    ("Vlearn Admin", "Nhắc các bạn nhớ mang thẻ học viên khi vào trường, bạn nào chưa nhận thẻ thì liên hệ Lab Coach tại lớp."),
    ("Vlearn Admin", "Điểm danh buổi chiều nay dùng mã QR như thường lệ, quét xong nhớ bấm lưu câu trả lời để hệ thống ghi nhận."),
    ("Vlearn Admin", "Do trùng lịch phòng, buổi lab thứ 6 tuần này chuyển sang phòng bên cạnh, các bạn chú ý theo dõi bảng thông báo trước cửa lớp."),
    ("Vlearn Admin", "Có bạn hỏi về giấy xác nhận sinh viên: liên hệ trực tiếp phòng đào tạo, không phải qua kênh này nhé."),
]


def main():
    ap = seed_lib.build_arg_parser(__doc__)
    args = ap.parse_args()
    seed_lib.send_messages(args.webhook, SAMPLE_MESSAGES, args.delay)


if __name__ == "__main__":
    main()
