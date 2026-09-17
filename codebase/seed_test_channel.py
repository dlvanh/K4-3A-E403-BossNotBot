"""
seed_test_channel.py — Bơm tin nhắn MẪU (tự viết, KHÔNG phải dữ liệu K4 thật)
vào MỘT kênh trò chuyện test, mô phỏng học viên hỏi-đáp qua lại. Dùng để demo
/tom-tat-tro-chuyen.

Vì sao dùng tin tự viết thay vì dán lại k4_messages.csv:
    Pack dữ liệu K4 chỉ được dùng CỤC BỘ để phân tích/test (xem README của
    pack, mục "Luật dùng và bảo mật": không đưa dữ liệu lên nơi công khai).
    Đăng lại nội dung thật — dù đã ẩn danh — lên một server Discord khác (kể
    cả server riêng của bạn) là đưa dữ liệu ra ngoài phạm vi được cấp. Script
    này chỉ dùng các câu hỏi MẪU, viết lại theo đúng tinh thần chủ đề (XP,
    deadline, ghép nhóm, lỗi cài đặt...) nhưng không phải nguyên văn của ai —
    an toàn để demo. Muốn có bằng chứng từ dữ liệu thật thì dùng
    replay_test.py (chạy cục bộ, không đăng lên đâu) rồi trích dẫn kèm msg_id
    trong báo cáo, thay vì đăng cả đoạn chat lên kênh demo.

Cách dùng:
    1. Trong kênh test của bạn (tên gợi ý: "chung" hoặc "trò-chuyện"):
       Cài đặt kênh → Tích hợp → Webhook → New Webhook → Copy Webhook URL
    2. python seed_test_channel.py --webhook "<url>"
    3. Chạy /tom-tat-tro-chuyen trong kênh đó để demo.

Muốn seed thêm các kênh #thông-báo-* riêng biệt để test /tom-tat-thong-bao
(lệnh này gom tất cả kênh có "thông-báo"/"announce" trong tên) thì dùng:
    seed_thong_bao_chung.py, seed_thong_bao_lop_hoc.py,
    seed_thong_bao_build.py, seed_thong_bao_workshop.py
"""
import seed_lib

seed_lib.setup_utf8_console()

# Câu hỏi mẫu — tự viết, cùng chủ đề với các pain point thấy trong pack
# (XP/điểm danh, deadline nộp lab, ghép nhóm/đề tài, lỗi cài đặt, workshop,
# mentor duty, AI log) nhưng không phải nguyên văn tin nhắn thật của ai.
SAMPLE_MESSAGES = [
    ("Minh Anh", "Mọi người ơi cho em hỏi XP tính từ hoạt động nào vậy ạ, em thấy /rank chưa lên điểm dù em có tương tác trong kênh?"),
    ("Minh Anh", "À với cả deadline nộp lab tuần này là mấy giờ nhỉ, có phải 23:59 không ạ?"),
    ("Quốc Bảo", "mình cài CVAT bị lỗi ở bước 3, health check báo 500 hoài, có ai fix được chưa chỉ mình với"),
    ("Quốc Bảo", "à mình chạy lại lệnh docker compose pull xong rồi vẫn y vậy, chưa hết lỗi"),
    ("Thu Hà", "cho em hỏi team em 3 người có ghép thêm được không hay phải đủ 4-5 người mới được nộp đề tài"),
    ("Thu Hà", "với lại đổi đề tài sau khi pick rồi thì làm sao ạ, có được đổi lại không"),
    ("Đức Long", "mai có workshop lúc mấy giờ vậy mọi người, mình quên mất lịch rồi"),
    ("Đức Long", "đặt tên zoom kiểu gì để được điểm danh tự động nhỉ, ai nhớ cú pháp không chỉ mình với"),
    ("Ngọc Trâm", "mentor duty nộp trước mấy giờ thì được tính XP vậy ạ"),
    ("Ngọc Trâm", "daily standup mà nhóm chưa có đề tài thì ghi nội dung gì hả mọi người"),
    ("Hoàng Phúc", "AI log setup xong mà vào dashboard vẫn thấy chưa có log nào, có ai bị giống mình không"),
    ("Hoàng Phúc", "mình push code rồi mà không thấy dòng [ai-log] Submitted đâu cả, chắc mình setup sai bước nào đó"),
    ("Minh Anh", "cảm ơn mọi người đã trả lời nha, mình xin tạo ticket hỗ trợ luôn cho chắc"),
    ("Quốc Bảo", "có bạn nào biết data cho đề tài là BTC cấp hay mình tự tìm không ạ"),
]


def main():
    ap = seed_lib.build_arg_parser(__doc__)
    args = ap.parse_args()

    ok = seed_lib.send_messages(args.webhook, SAMPLE_MESSAGES, args.delay)
    if ok:
        print("\nXong. Giờ chạy /tom-tat-tro-chuyen trong kênh này để demo bot thật.")


if __name__ == "__main__":
    main()
