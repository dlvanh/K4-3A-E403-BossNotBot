"""
timeline_replay.py — Giả lập người dùng gọi lệnh tóm tắt ở từng thời điểm T trong 3 ngày của
discord-pack, rồi đo xem logic chọn tin của bot có đưa ĐÚNG tin vào AI không. Không gọi AI.

Nguyên tắc không nhìn trước (no look-ahead):
    - Đầu vào của bot tại T chỉ gồm tin có thời điểm <= T, qua đúng cửa sổ + limit như tom_tat_bot.py.
    - "Câu hỏi còn tồn tại T" chỉ xét reply có thời điểm <= T.
    - Đáp án (hạn chót trong timeline_labels.json) được phép biết tương lai.

Cách dùng (từ thư mục gốc repo):
    codebase/.venv/Scripts/python eval/timeline_replay.py
    codebase/.venv/Scripts/python eval/timeline_replay.py --step-min 30

Đọc data pack từ --csv, hoặc biến môi trường DATA_PACK_DIR, hoặc mặc định repo đề bài nằm cạnh repo này.
Đầu ra chỉ chứa msg_id + số đếm (không chép nội dung pack): eval/timeline/<run_id>/results.{md,json}
"""
import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = ROOT.parent / "K4-3A-Day05-06-AI-Product-Hackathon" / "data" / "discord-pack" / "k4_messages.csv"
FMT = "%d/%m %H:%M"

QUESTION_RE = re.compile(r"\?|\b(ở đâu|thế nào|như nào|khi nào|bao nhiêu|được không|kiểu gì|làm sao|phải không)\b", re.I)
RELATIVE_RE = re.compile(r"hôm nay|tối nay|sáng nay|chiều nay|ngày mai|hôm qua|tuần sau|tuần này", re.I)


def load_messages(csv_path):
    with open(csv_path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["t"] = datetime.strptime(r["created_at_vn"], "%Y-%m-%d %H:%M")
        r["is_bot"] = r["is_bot"] == "True"
    rows.sort(key=lambda r: r["t"])
    return rows


# ---------------------------------------------------------------------------
# Mô phỏng đúng logic chọn tin của tom_tat_bot.py tại thời điểm T
# channel.history(limit=N, after=T-window, oldest_first=False) → N tin THÔ mới nhất trong cửa sổ,
# sau đó mới lọc bỏ tin bot và tin rỗng.
# ---------------------------------------------------------------------------
def bot_view(msgs, now, window_hours, limit):
    in_window = [m for m in msgs if now - timedelta(hours=window_hours) < m["t"] <= now]
    raw = in_window[-limit:]
    kept = [m for m in raw if not m["is_bot"] and m["content"].strip()]
    assert all(m["t"] <= now for m in kept), "rò rỉ tin tương lai vào đầu vào bot"
    return in_window, kept


def ticks(start, end, step):
    t = start
    while t <= end:
        yield t
        t += step


def run(args):
    labels = json.loads((Path(__file__).parent / "timeline_labels.json").read_text(encoding="utf-8"))
    p = labels["bot_params"]
    csv_path = args.csv or (Path(os.environ["DATA_PACK_DIR"]) / "k4_messages.csv" if os.getenv("DATA_PACK_DIR") else DEFAULT_CSV)
    rows = load_messages(csv_path)

    by_channel = {}
    for r in rows:
        by_channel.setdefault((r["guild"], r["channel"]), []).append(r)

    start = rows[0]["t"].replace(minute=0) + timedelta(hours=1)
    end = rows[-1]["t"]
    step = timedelta(minutes=args.step_min)
    all_ticks = list(ticks(start, end, step))

    # ---------------- A. Thông báo còn hiệu lực có tới được AI không ----------------
    by_id = {r["msg_id"]: r for r in rows}
    items = []
    for it in labels["time_bound_items"]:
        msg = by_id[it["msg_id"]]
        valid_until = datetime.strptime(it["valid_until"], "%Y-%m-%d %H:%M")
        should, seen, missed_ticks = 0, 0, []
        for now in all_ticks:
            if not (msg["t"] <= now < valid_until):
                continue
            should += 1
            visible_ids = set()
            for ch in labels["channels"][it["guild"]]["announcement"]:
                _, kept = bot_view(by_channel.get((it["guild"], ch), []), now, p["announcement_window_hours"], p["announcement_limit_per_channel"])
                visible_ids |= {m["msg_id"] for m in kept}
            if it["msg_id"] in visible_ids:
                seen += 1
            else:
                missed_ticks.append(now)
        drop_at = msg["t"] + timedelta(hours=p["announcement_window_hours"])
        items.append({
            "msg_id": it["msg_id"], "guild": it["guild"], "label": it["label"],
            "posted": msg["t"].strftime(FMT), "valid_until": valid_until.strftime(FMT),
            "ticks_should_see": should, "ticks_seen": seen,
            "first_missed": missed_ticks[0].strftime(FMT) if missed_ticks else None,
            "blind_hours_total": round(max(0.0, (valid_until - drop_at).total_seconds() / 3600), 1),
            "assumption": it.get("assumption", ""),
        })
    a_should = sum(i["ticks_should_see"] for i in items)
    a_seen = sum(i["ticks_seen"] for i in items)

    # ---------------- B. Tin trò chuyện bị cắt bởi limit ----------------
    chat = []
    for guild, cfg in labels["channels"].items():
        if guild.startswith("_"):
            continue
        for ch in cfg["chat"]:
            msgs = by_channel.get((guild, ch), [])
            calls = truncated = human_total = human_kept = 0
            worst = None
            for now in all_ticks:
                in_window, kept = bot_view(msgs, now, p["chat_window_hours"], p["chat_limit"])
                if not in_window:
                    continue
                human = [m for m in in_window if not m["is_bot"] and m["content"].strip()]
                calls += 1
                human_total += len(human)
                human_kept += len(kept)
                if len(in_window) > p["chat_limit"]:
                    truncated += 1
                    if not worst or len(human) - len(kept) > worst["human_dropped"]:
                        worst = {"at": now.strftime(FMT), "raw_in_window": len(in_window), "human_in_window": len(human),
                                 "human_sent_to_ai": len(kept), "human_dropped": len(human) - len(kept)}
            chat.append({
                "guild": guild, "channel": ch, "calls_with_messages": calls, "calls_truncated": truncated,
                "human_msgs_in_window": human_total, "human_msgs_sent_to_ai": human_kept,
                "kept_rate": round(100 * human_kept / human_total, 1) if human_total else None, "worst": worst,
            })

    # ---------------- C. Câu hỏi đang tồn có tới được AI không ----------------
    replies = {}
    for r in rows:
        if r["reply_to"]:
            replies.setdefault(r["reply_to"], []).append(r["t"])
    q_should = q_seen = 0
    invisible_while_open = set()
    for guild, cfg in labels["channels"].items():
        if guild.startswith("_"):
            continue
        for ch in cfg["chat"]:
            msgs = by_channel.get((guild, ch), [])
            questions = [m for m in msgs if not m["is_bot"] and QUESTION_RE.search(m["content"])]
            for now in all_ticks:
                _, kept = bot_view(msgs, now, p["chat_window_hours"], p["chat_limit"])
                kept_ids = {m["msg_id"] for m in kept}
                for q in questions:
                    if not (now - timedelta(hours=24) < q["t"] <= now):
                        continue
                    answered = any(t <= now for t in replies.get(q["msg_id"], []))  # chỉ reply đã xảy ra
                    if answered:
                        continue
                    q_should += 1
                    if q["msg_id"] in kept_ids:
                        q_seen += 1
                    else:
                        invisible_while_open.add(q["msg_id"])

    # ---------------- D. Thời gian tương đối bị lệch ngày ----------------
    stale = {}
    stale_ticks = 0
    for guild, cfg in labels["channels"].items():
        if guild.startswith("_"):
            continue
        for now in all_ticks:
            hit = False
            for ch in cfg["announcement"]:
                _, kept = bot_view(by_channel.get((guild, ch), []), now, p["announcement_window_hours"], p["announcement_limit_per_channel"])
                for m in kept:
                    if RELATIVE_RE.search(m["content"]) and m["t"].date() != now.date():
                        stale.setdefault(m["msg_id"], {"posted": m["t"].strftime(FMT), "words": sorted({w.lower() for w in RELATIVE_RE.findall(m["content"])}), "ticks": 0})
                        stale[m["msg_id"]]["ticks"] += 1
                        hit = True
            stale_ticks += hit

    summary = {
        "range": f"{start.strftime(FMT)} → {end.strftime(FMT)}",
        "step_minutes": args.step_min,
        "ticks": len(all_ticks),
        "A_deadline_recall": {"seen": a_seen, "should": a_should, "rate": round(100 * a_seen / a_should, 1) if a_should else None},
        "B_chat_kept": {"sent": sum(c["human_msgs_sent_to_ai"] for c in chat), "in_window": sum(c["human_msgs_in_window"] for c in chat)},
        "C_open_question_recall": {"seen": q_seen, "should": q_should, "rate": round(100 * q_seen / q_should, 1) if q_should else None,
                                   "distinct_questions_invisible_while_open": len(invisible_while_open)},
        "D_stale_relative_time": {"ticks_affected": stale_ticks, "msg_ids": sorted(stale)},
    }
    b = summary["B_chat_kept"]
    b["rate"] = round(100 * b["sent"] / b["in_window"], 1) if b["in_window"] else None

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.out) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"run_id": run_id, "summary": summary, "items": items, "chat": chat,
               "open_questions_invisible": sorted(invisible_while_open), "stale_relative": stale}
    (out_dir / "results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "results.md").write_text(render_md(payload, p), encoding="utf-8")

    print(f"Replay {summary['range']} · mỗi {args.step_min} phút · {len(all_ticks)} thời điểm hỏi")
    print(f"A. Thông báo còn hiệu lực tới được AI: {a_seen}/{a_should} lượt ({summary['A_deadline_recall']['rate']}%)")
    for i in items:
        flag = "" if i["ticks_seen"] == i["ticks_should_see"] else f" · rơi từ {i['first_missed']}"
        print(f"   {i['msg_id']} {i['label']}: {i['ticks_seen']}/{i['ticks_should_see']}{flag} · tổng khoảng mù {i['blind_hours_total']}h")
    print(f"B. Tin trò chuyện tới được AI: {b['sent']}/{b['in_window']} ({b['rate']}%)")
    for c in chat:
        print(f"   {c['guild']} {c['channel']}: bị cắt {c['calls_truncated']}/{c['calls_with_messages']} lần · giữ {c['kept_rate']}%")
    qc = summary["C_open_question_recall"]
    print(f"C. Câu hỏi đang tồn tới được AI: {qc['seen']}/{qc['should']} ({qc['rate']}%) · {qc['distinct_questions_invisible_while_open']} câu từng bị mất dấu khi chưa ai trả lời")
    print(f"D. Thời điểm hỏi có thông báo 'hôm nay/ngày mai' đã lệch ngày: {stale_ticks}/{len(all_ticks)} · {sorted(stale)}")
    print(f"Đã ghi: {out_dir}")


def render_md(d, p):
    s = d["summary"]
    L = [
        f"# Timeline replay · `{d['run_id']}`",
        "",
        f"Giả lập gọi lệnh tóm tắt mỗi {s['step_minutes']} phút trong {s['range']} ({s['ticks']} thời điểm). "
        f"Logic chọn tin mô phỏng `tom_tat_bot.py`: thông báo {p['announcement_window_hours']}h / {p['announcement_limit_per_channel']} tin mỗi kênh, "
        f"trò chuyện {p['chat_window_hours']}h / {p['chat_limit']} tin thô. Không gọi AI. Bot chỉ thấy tin ≤ thời điểm hỏi.",
        "",
        "| Chỉ số | Kết quả |",
        "|---|---|",
        f"| A · Thông báo còn hiệu lực tới được AI | {s['A_deadline_recall']['seen']}/{s['A_deadline_recall']['should']} lượt ({s['A_deadline_recall']['rate']}%) |",
        f"| B · Tin trò chuyện trong cửa sổ tới được AI | {s['B_chat_kept']['sent']}/{s['B_chat_kept']['in_window']} ({s['B_chat_kept']['rate']}%) |",
        f"| C · Câu hỏi đang tồn (≤24h, chưa reply) tới được AI | {s['C_open_question_recall']['seen']}/{s['C_open_question_recall']['should']} ({s['C_open_question_recall']['rate']}%) · {s['C_open_question_recall']['distinct_questions_invisible_while_open']} câu từng bị mất dấu |",
        f"| D · Thời điểm hỏi gặp 'hôm nay/ngày mai' đã lệch ngày | {s['D_stale_relative_time']['ticks_affected']}/{s['ticks']} |",
        "",
        "## A · Thông báo có hạn",
        "",
        "| msg_id | Nội dung (diễn đạt lại) | Đăng | Hết hiệu lực | Lượt tới AI | Rơi khỏi cửa sổ từ | Tổng khoảng mù | Giả định |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for i in d["items"]:
        L.append(f"| {i['msg_id']} | {i['label']} | {i['posted']} | {i['valid_until']} | {i['ticks_seen']}/{i['ticks_should_see']} | {i['first_missed'] or '—'} | {i['blind_hours_total']}h | {i['assumption']} |")
    L += ["", "*Lượt tới AI chỉ tính trong phạm vi pack; tổng khoảng mù tính tới hạn thật, kể cả sau khi pack kết thúc.*", "",
          "## B · Kênh trò chuyện", "", "| Kênh | Lần gọi bị cắt | Tin người giữ lại | Tệ nhất |", "|---|---|---|---|"]
    for c in d["chat"]:
        w = c["worst"]
        worst = f"{w['at']}: {w['human_in_window']} tin người trong cửa sổ, AI nhận {w['human_sent_to_ai']}" if w else "—"
        L.append(f"| {c['guild']} {c['channel']} | {c['calls_truncated']}/{c['calls_with_messages']} | {c['kept_rate']}% | {worst} |")
    L += ["", "## C · Câu hỏi từng bị mất dấu khi chưa ai trả lời", "", ", ".join(d["open_questions_invisible"]) or "—",
          "", "## D · Thông báo có thời gian tương đối bị đưa vào AI sau khi đã sang ngày khác", "",
          "| msg_id | Đăng | Từ | Số thời điểm hỏi bị ảnh hưởng |", "|---|---|---|---|"]
    for mid, v in sorted(d["stale_relative"].items()):
        L.append(f"| {mid} | {v['posted']} | {', '.join(v['words'])} | {v['ticks']} |")
    L += ["", "> Bot chỉ gửi AI giờ `HH:MM`, không gửi ngày đăng và thời điểm tóm tắt, nên AI không thể biết 'ngày mai' đã thành 'hôm nay'.", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", help="đường dẫn k4_messages.csv")
    ap.add_argument("--step-min", type=int, default=60, help="khoảng cách giữa các thời điểm hỏi (phút)")
    ap.add_argument("--out", default=str(ROOT / "eval" / "timeline"))
    run(ap.parse_args())


if __name__ == "__main__":
    main()
