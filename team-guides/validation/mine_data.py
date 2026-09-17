import csv
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

with open('data/discord-pack/k4_messages.csv', mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

total = len(rows)
bot_msgs = [r for r in rows if r['is_bot'].lower() == 'true']
user_msgs = [r for r in rows if r['is_bot'].lower() == 'false']

print(f"Total: {total}")
print(f"Bot: {len(bot_msgs)}")
print(f"User: {len(user_msgs)}")

channel_counts = Counter(r['channel'] for r in rows)
user_channel_counts = Counter(r['channel'] for r in user_msgs)

print("\nTotal by Channel:")
for ch, count in channel_counts.most_common():
    print(f"  {ch}: {count}")

print("\nUser by Channel:")
for ch, count in user_channel_counts.most_common():
    print(f"  {ch}: {count}")

# Check date range
dates = sorted(list(set(r['created_at_vn'][:10] for r in rows)))
print(f"\nDate range: {dates}")

# Search keywords
keywords = ['deadline', 'nộp', 'lab', 'link', 'slide', 'lịch', 'bài tập', 'chấm', 'điểm', 'trôi', 'miss', 'hỏi lại', 'ở đâu', 'mấy giờ', 'khi nào']
kw_regex = re.compile(r'(' + '|'.join(keywords) + r')', re.IGNORECASE)

kw_matches = [r for r in user_msgs if kw_regex.search(r['content'])]
print(f"\nKeyword matches (user messages): {len(kw_matches)}")

# Breakdown by specific categories
dl_kw = re.compile(r'(deadline|hạn chót|hạn nộp|mấy giờ nộp|khi nào nộp)', re.IGNORECASE)
link_kw = re.compile(r'(link|slide|tài liệu|folder|drive)', re.IGNORECASE)
lost_kw = re.compile(r'(trôi|tìm lại|ở đâu|lội|miss|chỗ nào)', re.IGNORECASE)

dl_matches = [r for r in user_msgs if dl_kw.search(r['content'])]
link_matches = [r for r in user_msgs if link_kw.search(r['content'])]
lost_matches = [r for r in user_msgs if lost_kw.search(r['content'])]

print(f"Deadline/Hạn nộp: {len(dl_matches)}")
print(f"Link/Slide/Tài liệu: {len(link_matches)}")
print(f"Trôi/Tìm lại/Ở đâu: {len(lost_matches)}")

print("\n--- SAMPLE MESSAGES: DEADLINE & CONFUSION ---")
for r in dl_matches[:10]:
    print(f"ID: {r['msg_id']} | Ch: {r['channel']} | Time: {r['created_at_vn']} | Text: {r['content']}")

print("\n--- SAMPLE MESSAGES: LOST / SEARCHING ---")
for r in lost_matches[:10]:
    print(f"ID: {r['msg_id']} | Ch: {r['channel']} | Time: {r['created_at_vn']} | Text: {r['content']}")
