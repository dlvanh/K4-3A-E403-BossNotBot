"""
replay_test.py — Kiểm thử tom_tat_bot.py NGOẠI TUYẾN bằng k4_messages.csv,
không cần bot có mặt trong server Discord nào cả.

Cách dùng:
    python replay_test.py --list-channels K4-L3-4
    python replay_test.py --guild K4-L3-4 --channel channel_10 --mode chat
    python replay_test.py --guild K4-L2-3 --channel channel_02 --mode chat --limit 50

Cách hoạt động:
    Script đọc thẳng k4_messages.csv, dựng lại đúng định dạng messages_text mà
    get_recent_messages() trong tom_tat_bot.py tạo ra, rồi gọi thẳng
    TomTatBot.summarize_with_ai() — dùng đúng prompt + client thật của bot,
    chỉ bỏ qua phần discord.py/Gateway. Vẫn cần OPENAI_API_KEY hợp lệ trong .env.

Giới hạn của cách test này (đọc DATA_DICTIONARY.md của pack để hiểu thêm):
    - channel chỉ là mã channel_01..channel_12, KHÔNG có tên kênh thật, nên
      không thể test được nhánh get_channel_announcements() (lọc theo tên kênh
      chứa "thông-báo"/"announce") — script này chỉ test chất lượng tóm tắt
      của summarize_with_ai(), không test logic chọn kênh thông báo.
    - Nội dung đã bị mask ([HV], [MSSV], [link:domain]...). Đừng cố đoán danh
      tính người viết.
    - Đây là dữ liệu được cấp riêng cho hackathon: chỉ dùng cục bộ để test,
      không copy k4_messages.csv vào repo nộp bài hay nơi công khai. Khi trích
      để báo cáo/demo: tối đa 2 câu/ví dụ, kèm msg_id.
"""
import argparse
import asyncio
import csv
import sys
from pathlib import Path

# Console Windows mặc định dùng cp1252, không encode được tiếng Việt có dấu
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
from tom_tat_bot import tom_tat  # noqa: E402  (dùng đúng logic prompt + client thật của bot)

DEFAULT_CSV = Path(__file__).parent.parent / "K4-3A-E403-BotNotBoss" / "data" / "discord-pack" / "k4_messages.csv"


def load_rows(csv_path):
    with open(csv_path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def list_channels(rows, guild):
    counts = {}
    for r in rows:
        if r["guild"] != guild:
            continue
        counts[r["channel"]] = counts.get(r["channel"], 0) + 1
    for ch, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"{ch}: {n} tin")


def build_messages_text(rows, guild, channel, limit, include_bot):
    filtered = [
        r for r in rows
        if r["guild"] == guild and r["channel"] == channel
        and r["content"].strip()
        and (include_bot or r["is_bot"] != "True")
    ]
    filtered = filtered[-limit:]  # giống MESSAGE_LIMIT: N tin gần nhất, giữ nguyên thứ tự thời gian
    lines = [f"[{r['created_at_vn'][-5:]}] {r['author']}: {r['content']}" for r in filtered]
    return "\n".join(lines), filtered


async def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", default=str(DEFAULT_CSV))
    ap.add_argument("--guild", choices=["K4-L2-3", "K4-L3-4"])
    ap.add_argument("--channel")
    ap.add_argument("--mode", choices=["notice", "chat", "all"], default="chat")
    ap.add_argument("--limit", type=int, default=50, help="tương đương MESSAGE_LIMIT trong bot")
    ap.add_argument("--include-bot", action="store_true", help="không loại tin của BOT (mặc định loại, giống get_recent_messages)")
    ap.add_argument("--list-channels", metavar="GUILD", help="chỉ in số tin theo channel của guild rồi thoát")
    args = ap.parse_args()

    rows = load_rows(args.csv)

    if args.list_channels:
        list_channels(rows, args.list_channels)
        return

    if not args.guild or not args.channel:
        ap.error("cần --guild và --channel (dùng --list-channels GUILD trước để xem kênh nào có nhiều tin)")

    messages_text, used_rows = build_messages_text(rows, args.guild, args.channel, args.limit, args.include_bot)
    if not messages_text:
        print("Không có tin nhắn nào khớp bộ lọc.")
        return

    print(f"--- {len(used_rows)} tin nhắn đưa vào prompt (mode={args.mode}) ---")
    preview = messages_text[:2000]
    print(preview, "..." if len(messages_text) > 2000 else "")

    print("\n--- Gọi summarize_with_ai() y hệt bot thật (cần OPENAI_API_KEY trong .env) ---")
    summary = await tom_tat.summarize_with_ai(messages_text, mode=args.mode)
    print(summary)

    print("\n--- msg_id đã dùng (để trích dẫn khi báo cáo/demo, tối đa 2 câu/ví dụ) ---")
    print(" ".join(r["msg_id"] for r in used_rows))


if __name__ == "__main__":
    asyncio.run(main())
