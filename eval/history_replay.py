"""
history_replay.py — Với mỗi câu hỏi THẬT học viên tag bot trong discord-pack, dựng lại đúng thời điểm hỏi T:
bot đọc TOÀN BỘ lịch sử tin nhắn của server trước T (không cửa sổ 24h/4h), rồi trả lời bằng
TomTatBot.answer_from_history(). Ghi log mọi lần gọi và chấm tự động phần kiểm được không cần nhãn.

Không nhìn trước:
    - Lịch sử = tin cùng server có thời điểm < T (chặt, theo phút). Bỏ chính câu hỏi.
    - Mặc định bỏ tin của bot cũ (câu trả lời cũ có thể sai) — bật lại bằng --include-bot.
    - Câu trả lời thật của bot cũ (nếu có) chỉ ghi msg_id để người chấm so sánh, KHÔNG đưa vào prompt.

Cách dùng (từ thư mục gốc repo):
    codebase/.venv/Scripts/python eval/history_replay.py --dry-run --limit 5     # fake provider, không gửi data đi đâu
    codebase/.venv/Scripts/python eval/history_replay.py --limit 10 --delay 13   # gọi LLM thật (free tier Gemini: 5 request/phút)
    codebase/.venv/Scripts/python eval/history_replay.py --ids M56777,M72229

⚠ Chế độ thật gửi NGUYÊN VĂN lịch sử tin nhắn của pack cho LLM provider. Quy định dữ liệu của khoá:
  chỉ đưa phần tối thiểu ra công cụ ngoài; free tier có thể dùng dữ liệu để huấn luyện. Cân nhắc --max-history.

Đầu ra: eval/history_runs/<run_id>/
    trace.jsonl  — prompt + output từng lần gọi (CHỨA NỘI DUNG PACK → đã gitignore, không commit)
    results.json / results.md — chỉ msg_id + chỉ số, commit được
"""
import argparse
import asyncio
import csv
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", line_buffering=True)

ROOT = Path(__file__).resolve().parent.parent
CODEBASE = ROOT / "codebase"
DEFAULT_CSV = ROOT.parent / "K4-3A-Day05-06-AI-Product-Hackathon" / "data" / "discord-pack" / "k4_messages.csv"

CITE_RE = re.compile(r"\bM\d{5}\b")
NOT_FOUND_RE = re.compile(r"không tìm thấy|không có thông tin|chưa có thông tin|không có trong|không xem được|không thể (xem|kiểm tra)", re.I)
TRANSIENT_RE = re.compile(r"429|503|rate.?limit|resource.?exhausted|quota|too many requests|unavailable|high demand|overloaded", re.I)
RETRY_AFTER_RE = re.compile(r"retry in ([\d.]+)s", re.I)
ERROR_PREFIX = "Lỗi khi trả lời:"


def load_rows(csv_path):
    with open(csv_path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for i, r in enumerate(rows):
        r["t"] = datetime.strptime(r["created_at_vn"], "%Y-%m-%d %H:%M")
        r["is_bot"] = r["is_bot"] == "True"
        r["_i"] = i
    rows.sort(key=lambda r: (r["t"], r["_i"]))
    return rows


def channel_labels():
    labels = json.loads((Path(__file__).parent / "timeline_labels.json").read_text(encoding="utf-8"))["channels"]
    out = {}
    for guild, cfg in labels.items():
        if guild.startswith("_"):
            continue
        for ch in cfg["announcement"]:
            out[(guild, ch)] = f"thông-báo ({ch})"
        for ch in cfg["chat"]:
            out[(guild, ch)] = f"trò-chuyện ({ch})"
    return out


def pick_questions(rows, args):
    questions = [
        r for r in rows
        if r["mentions_bot"] == "True" and not r["is_bot"]
        and len(r["content"].replace("[@BOT]", "").strip()) >= 8
    ]
    if args.ids:
        wanted = set(args.ids.split(","))
        return [q for q in questions if q["msg_id"] in wanted]
    if args.limit and len(questions) > args.limit:
        step = len(questions) / args.limit  # rải đều theo thời gian, cố định để chạy lại ra cùng tập
        questions = [questions[int(i * step)] for i in range(args.limit)]
    return questions


def build_history(rows, question, labels, include_bot, max_history):
    T = question["t"]
    hist = [
        r for r in rows
        if r["guild"] == question["guild"] and r["t"] < T and r["msg_id"] != question["msg_id"]
        and (include_bot or not r["is_bot"]) and r["content"].strip()
    ]
    if max_history:
        hist = hist[-max_history:]
    assert all(r["t"] < T for r in hist), "rò rỉ tin tương lai vào lịch sử"
    return hist


async def run(args):
    sys.path.insert(0, str(CODEBASE))
    from llm_provider import create_provider  # noqa: E402
    from tom_tat_bot import TomTatBot  # noqa: E402  (nạp codebase/.env)

    csv_path = args.csv or (Path(os.environ["DATA_PACK_DIR"]) / "k4_messages.csv" if os.getenv("DATA_PACK_DIR") else DEFAULT_CSV)
    rows = load_rows(csv_path)
    by_id = {r["msg_id"]: r for r in rows}
    labels = channel_labels()
    questions = pick_questions(rows, args)

    try:
        llm = create_provider("fake" if args.dry_run else args.provider)
    except ValueError as e:
        sys.exit(str(e))
    bot = TomTatBot(llm=llm)
    model = f"{llm.name}:{llm.model}"

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + ("-dry" if args.dry_run else "")
    out_dir = Path(args.out) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Lượt {run_id} · {model} · {len(questions)} câu hỏi · nghỉ {args.delay}s/lần gọi · log: {out_dir / 'trace.jsonl'}")
    if not args.dry_run:
        print("⚠ Đang gửi nguyên văn lịch sử tin nhắn của pack cho provider bên ngoài.")

    records = []
    with open(out_dir / "trace.jsonl", "w", encoding="utf-8", buffering=1) as trace:
        for n, q in enumerate(questions, 1):
            if records and args.delay:
                await asyncio.sleep(args.delay)
            hist = build_history(rows, q, labels, args.include_bot, args.max_history)
            history_ids = {r["msg_id"] for r in hist}
            history_text = "\n".join(
                bot.format_history_line(r["msg_id"], r["t"], labels.get((r["guild"], r["channel"]), f"khác ({r['channel']})"),
                                        r["content"], r["reply_to"] or None)
                for r in hist
            )
            question_text = q["content"].replace("[@BOT]", "").strip()
            old_bot_reply = next((r["msg_id"] for r in rows if r["reply_to"] == q["msg_id"] and r["is_bot"]), None)

            for attempt in range(1, args.retries + 2):
                t0 = time.perf_counter()
                output = await bot.answer_from_history(question_text, history_text, q["t"])
                latency_ms = int((time.perf_counter() - t0) * 1000)
                is_error = output.startswith(ERROR_PREFIX)
                will_retry = is_error and bool(TRANSIENT_RE.search(output)) and attempt <= args.retries
                trace.write(json.dumps({
                    "run_id": run_id, "question_id": q["msg_id"], "asked_at": q["t"].isoformat(), "guild": q["guild"],
                    "attempt": attempt, "final": not will_retry, "model": model, "api_error": is_error,
                    "usage": None if is_error else getattr(llm, "last_usage", None),
                    "finish_reason": None if is_error else getattr(llm, "last_finish_reason", None),
                    "latency_ms": latency_ms, "history_msgs": len(hist), "history_chars": len(history_text),
                    "old_bot_reply_id": old_bot_reply, "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "question": question_text, "output": output,
                }, ensure_ascii=False) + "\n")
                if is_error and "PerDay" in output:
                    sys.exit(f"Hết quota theo NGÀY của provider ({model}) — thử lại vô ích. Đổi model/provider hoặc chờ reset quota. Log: {out_dir}")
                if not will_retry:
                    break
                hinted = RETRY_AFTER_RE.search(output)
                wait = max(float(hinted.group(1)) + 1 if hinted else 0, max(args.delay, 5) * 2 ** attempt)
                print(f"          … lần {attempt} lỗi tạm thời, chờ {wait:.0f}s rồi thử lại")
                await asyncio.sleep(wait)

            cited = sorted(set(CITE_RE.findall(output))) if not is_error else []
            fabricated = [c for c in cited if c not in by_id]
            future = [c for c in cited if c in by_id and by_id[c]["t"] >= q["t"]]
            outside_history = [c for c in cited if c in by_id and c not in history_ids and c not in future]
            if is_error:
                kind = "api_error"
            elif cited:
                kind = "trả lời có trích dẫn"
            elif NOT_FOUND_RE.search(output):
                kind = "nói không tìm thấy / không xem được"
            else:
                kind = "trả lời KHÔNG trích dẫn"
            grounded_ok = not is_error and not fabricated and not future and not outside_history and kind != "trả lời KHÔNG trích dẫn"
            usage = None if is_error else getattr(llm, "last_usage", None)
            rec = {
                "question_id": q["msg_id"], "asked_at": q["t"].strftime("%d/%m %H:%M"), "guild": q["guild"],
                "history_msgs": len(hist), "kind": kind, "cited": cited, "fabricated_citations": fabricated,
                "future_citations": future, "citations_outside_history": outside_history,
                "grounded_ok": grounded_ok, "api_error": is_error, "latency_ms": latency_ms,
                "total_tokens": (usage or {}).get("total_tokens"), "old_bot_reply_id": old_bot_reply,
            }
            records.append(rec)
            mark = "OK  " if grounded_ok else ("ERR " if is_error else "LỖI ")
            tok = f" · {rec['total_tokens']} tok" if rec["total_tokens"] else ""
            print(f"[{mark}] {n:>3}/{len(questions)} {q['msg_id']} {rec['asked_at']} · {len(hist)} tin lịch sử · {kind} · {latency_ms} ms{tok}")
            for label, ids in (("trích mã không tồn tại", fabricated), ("trích tin TƯƠNG LAI", future), ("trích tin ngoài lịch sử", outside_history)):
                if ids:
                    print(f"          ✗ {label}: {ids}")

    summary = summarize(records)
    payload = {"run_id": run_id, "model": model, "include_bot": args.include_bot, "max_history": args.max_history,
               "summary": summary, "questions": records}
    (out_dir / "results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "results.md").write_text(render_md(payload), encoding="utf-8")
    print(f"\nĐạt tiêu chí có căn cứ: {summary['grounded_ok']}/{summary['total']} ({summary['grounded_rate']}%)")
    for k, v in summary["by_kind"].items():
        print(f"  {k}: {v}")
    print(f"Đã ghi: {out_dir}")


def summarize(records):
    total = len(records)
    ok = sum(r["grounded_ok"] for r in records)
    by_kind = {}
    for r in records:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
    return {
        "total": total, "grounded_ok": ok, "grounded_rate": round(100 * ok / total, 1) if total else 0,
        "by_kind": by_kind,
        "fabricated_citation_answers": sum(bool(r["fabricated_citations"]) for r in records),
        "future_citation_answers": sum(bool(r["future_citations"]) for r in records),
        "total_tokens": sum(r["total_tokens"] or 0 for r in records),
        "avg_history_msgs": int(sum(r["history_msgs"] for r in records) / total) if total else 0,
    }


def render_md(d):
    s = d["summary"]
    L = [
        f"# History replay · `{d['run_id']}`",
        "",
        f"- Model: `{d['model']}` · Hàm: `TomTatBot.answer_from_history`",
        f"- Mỗi câu hỏi thật (tag bot) được trả lời từ **toàn bộ lịch sử tin nhắn trước thời điểm hỏi** "
        f"(bỏ tin bot cũ: {'không' if d['include_bot'] else 'có'} · giới hạn lịch sử: {d['max_history'] or 'không'}). "
        f"Trung bình {s['avg_history_msgs']} tin lịch sử/câu · tổng token {s['total_tokens']}.",
        f"- **Có căn cứ (tự chấm): {s['grounded_ok']}/{s['total']} ({s['grounded_rate']}%)** · "
        f"trích mã bịa: {s['fabricated_citation_answers']} · trích tin tương lai: {s['future_citation_answers']}",
        "",
        "Tự chấm chỉ kiểm được **căn cứ**: có trích mã tin, mã có thật, nằm trong lịch sử trước T; hoặc nói rõ không tìm thấy. "
        "**Đúng/sai nội dung phải người chấm** — mở `trace.jsonl` (không commit) so với tin nguồn và câu trả lời của bot cũ.",
        "",
        "| Loại câu trả lời | Số câu |",
        "|---|---|",
    ]
    L += [f"| {k} | {v} |" for k, v in s["by_kind"].items()]
    L += ["", "| Câu hỏi | Lúc hỏi | Server | Tin lịch sử | Loại | Trích dẫn | Lỗi căn cứ | Bot cũ trả lời | Người chấm: đúng? |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in d["questions"]:
        errs = "; ".join(f"{k}: {v}" for k, v in (("bịa", r["fabricated_citations"]), ("tương lai", r["future_citations"]),
                                                   ("ngoài lịch sử", r["citations_outside_history"])) if v) or "—"
        L.append(f"| {r['question_id']} | {r['asked_at']} | {r['guild']} | {r['history_msgs']} | {r['kind']} | "
                 f"{', '.join(r['cited']) or '—'} | {errs} | {r['old_bot_reply_id'] or '—'} | |")
    L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", help="đường dẫn k4_messages.csv (mặc định: DATA_PACK_DIR hoặc repo đề bài cạnh repo này)")
    ap.add_argument("--limit", type=int, default=10, help="số câu hỏi, rải đều theo thời gian (0 = tất cả)")
    ap.add_argument("--ids", help="chỉ chạy các câu hỏi này, vd M56777,M72229")
    ap.add_argument("--max-history", type=int, default=0, help="chỉ lấy N tin gần nhất trước T (0 = toàn bộ)")
    ap.add_argument("--include-bot", action="store_true", help="đưa cả tin của bot cũ vào lịch sử")
    ap.add_argument("--delay", type=float, default=13.0, help="giây nghỉ giữa các lần gọi (free tier Gemini: 5 request/phút)")
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--provider", help="ghi đè LLM_PROVIDER")
    ap.add_argument("--dry-run", action="store_true", help="FakeProvider, không gửi dữ liệu đi đâu")
    ap.add_argument("--out", default=str(ROOT / "eval" / "history_runs"))
    asyncio.run(run(ap.parse_args()))


if __name__ == "__main__":
    main()
