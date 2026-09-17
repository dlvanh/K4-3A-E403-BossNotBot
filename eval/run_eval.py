"""
run_eval.py — Chạy golden set qua TomTatBot.summarize_with_ai() và chấm tự động.

Cách dùng (chạy từ thư mục gốc repo):
    codebase/.venv/Scripts/python eval/run_eval.py               # lượt thật, theo LLM_PROVIDER + key trong codebase/.env
    codebase/.venv/Scripts/python eval/run_eval.py --only K3a    # chạy 1 case
    codebase/.venv/Scripts/python eval/run_eval.py --dry-run     # không gọi AI, chỉ kiểm tra script + bộ chấm

Đầu ra (mỗi lượt một thư mục eval/runs/<run_id>/):
    trace.jsonl     — input gửi AI + output thô + latency từng case (bằng chứng lời gọi AI thật cho R5)
    results.json    — kết quả từng check
    results.md      — bảng tổng hợp để dán vào eval/run_results.md và spec §7

Bộ chấm chỉ dùng luật so khớp chuỗi (không dùng LLM chấm) để người ngoài nhóm
chạy lại ra đúng kết quả. Định nghĩa từng loại check: eval/README.md.
"""
import argparse
import asyncio
import json
import re
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", line_buffering=True)  # in tiến độ ngay cả khi ghi ra file

ROOT = Path(__file__).resolve().parent.parent
CODEBASE = ROOT / "codebase"
DIM_NAMES = {
    "D1": "Đầy đủ",
    "D2": "Trung thực",
    "D3": "An toàn",
    "D4": "Đúng phạm vi & đặc thù",
}
GROUP_NAMES = {
    "thuong": "Thường",
    "kho_1_nguon_su_that": "① Nguồn sự thật",
    "kho_2_mo_ho": "② Mơ hồ",
    "kho_3_pham_vi": "③ Ngoài phạm vi",
    "kho_4_domain": "④ Đặc thù domain",
    "hiem": "Hiếm",
}


# ---------------------------------------------------------------------------
# Dựng messages_text GIỐNG HỆT tom_tat_bot.py (tom_tat_thong_bao / tom_tat_tro_chuyen / tom_tat_chung).
# Nếu bot đổi định dạng thì phải sửa cả ở đây.
# ---------------------------------------------------------------------------
def format_announcements(items):
    return "\n".join(f"[{a['time']}] {a['channel']}: {a['author']}\n{a['content']}" for a in items)


def format_messages(items):
    return "\n".join(f"[{m['time']}] {m['author']}: {m['content']}" for m in items)


def build_messages_text(case):
    inp = case["input"]
    mode = case["mode"]
    if mode == "notice":
        return format_announcements(inp["announcements"])
    if mode == "chat":
        return format_messages(inp["messages"])
    combined = "=== THÔNG BÁO ===\n" + format_announcements(inp.get("announcements", []))
    if inp.get("messages"):
        combined += "\n\n=== TRÌNH CHUYỆN ===\n" + format_messages(inp["messages"])
    return combined


# ---------------------------------------------------------------------------
# Chuẩn hoá để so khớp: chữ thường, Unicode NFC, ngày về dạng d/m, giờ về dạng H:MM
# ---------------------------------------------------------------------------
DATE_RE = re.compile(r"(?<!\d)(\d{1,2})\s*[/-]\s*(\d{1,2})(?:\s*[/-]\s*\d{2,4})?(?!\d)")
# "20:00" cần đủ phút; "20h", "20h00", "8 giờ" được phép thiếu phút. "Phần 1:" và "2 học viên" không phải giờ.
TIME_RE = re.compile(r"(?<![\d/])(\d{1,2})(?::(\d{2})|\s*(?:h|giờ)(?:\s*(\d{2}))?(?!\w))(?![\d/])")
# Không chặn dấu ":" phía sau: giờ HH:MM đã bị xoá trước khi tìm số, còn "Học viên 25:" phải được tính là có số 25
NUM_RE = re.compile(r"(?<![\w/:])\d+(?![\w/])")


def canon(text):
    text = unicodedata.normalize("NFC", text).lower()
    text = DATE_RE.sub(lambda m: f"{int(m.group(1))}/{int(m.group(2))}", text)
    text = TIME_RE.sub(lambda m: f"{int(m.group(1))}:{int(m.group(2) or m.group(3) or 0):02d}", text)
    return text


def datetimes_in(text):
    t = canon(text)
    dates = set(re.findall(r"(?<!\d)\d{1,2}/\d{1,2}(?!\d)", t))
    times = set(re.findall(r"(?<!\d)\d{1,2}:\d{2}(?!\d)", t))
    return dates, times


def numbers_in(text):
    t = canon(text)
    t = re.sub(r"\d{1,2}/\d{1,2}|\d{1,2}:\d{2}", " ", t)
    return set(NUM_RE.findall(t))


# Lỗi tạm thời đáng thử lại: rate limit (429) và quá tải phía provider (503)
RATE_LIMIT_RE = re.compile(r"429|503|rate.?limit|resource.?exhausted|quota|too many requests|unavailable|high demand|overloaded", re.I)
BULLET_RE = re.compile(r"^\s*(?:\*\*)?\s*(?:[-*•+]|\d+[.)])\s+")


# ---------------------------------------------------------------------------
# Các loại check
# ---------------------------------------------------------------------------
def check_include(chk, output, _input_text):
    out = canon(output)
    lines = out.splitlines()
    for alt in chk["any_of"]:
        tokens = [canon(t) for t in alt]
        if chk.get("same_line"):
            if any(all(t in line for t in tokens) for line in lines):
                return True, f"khớp {alt}"
        elif all(t in out for t in tokens):
            return True, f"khớp {alt}"
    return False, f"không thấy bất kỳ phương án nào trong {chk['any_of']}" + (" (cùng một dòng)" if chk.get("same_line") else "")


def check_exclude(chk, output, _input_text):
    out = canon(output)
    found = [t for t in chk["tokens"] if canon(t) in out]
    return (not found), (f"xuất hiện: {found}" if found else "không xuất hiện chuỗi cấm")


def check_forbid_line(chk, output, _input_text):
    has = [canon(t) for t in chk["has"]]
    and_any = [canon(t) for t in chk.get("and_any", [])]
    unless_any = [canon(t) for t in chk.get("unless_any", [])]
    for line in canon(output).splitlines():
        if not all(t in line for t in has):
            continue
        if and_any and not any(t in line for t in and_any):
            continue
        if any(t in line for t in unless_any):
            continue
        return False, f"dòng vi phạm: {line.strip()[:160]}"
    return True, "không có dòng vi phạm"


def check_no_new_datetimes(_chk, output, input_text):
    in_dates, in_times = datetimes_in(input_text)
    out_dates, out_times = datetimes_in(output)
    new_dates = out_dates - in_dates

    def time_ok(t):
        h, mm = t.split(":")
        alt = f"{(int(h) + 12) % 24}:{mm}"  # chấp nhận "8:00 tối" khi đầu vào ghi 20:00
        return t in in_times or alt in in_times

    new_times = {t for t in out_times if not time_ok(t)}
    ok = not new_dates and not new_times
    return ok, ("không có ngày/giờ lạ" if ok else f"ngày lạ {sorted(new_dates)} · giờ lạ {sorted(new_times)}")


def check_no_new_numbers(_chk, output, input_text):
    allowed = numbers_in(input_text) | {str(i) for i in range(0, 11)}  # 0–10: đánh số danh sách
    new = sorted(numbers_in(output) - allowed, key=lambda x: int(x))
    return (not new), (f"số lạ: {new}" if new else "không có số lạ")


def check_min_bullets(chk, output, _input_text):
    n = sum(1 for line in output.splitlines() if BULLET_RE.match(line))
    return n >= chk["n"], f"{n} gạch đầu dòng (cần ≥ {chk['n']})"


def check_max_chars(chk, output, _input_text):
    return len(output) <= chk["n"], f"{len(output)} ký tự (tối đa {chk['n']})"


CHECKS = {
    "include": check_include,
    "exclude": check_exclude,
    "forbid_line": check_forbid_line,
    "no_new_datetimes": check_no_new_datetimes,
    "no_new_numbers": check_no_new_numbers,
    "min_bullets": check_min_bullets,
    "max_chars": check_max_chars,
}


def grade(case, output, input_text):
    results = []
    for chk in case["checks"]:
        ok, detail = CHECKS[chk["type"]](chk, output, input_text)
        results.append({"type": chk["type"], "dim": chk["dim"], "passed": ok, "detail": detail, "note": chk.get("note", "")})
    return results


# ---------------------------------------------------------------------------
# Gọi AI
# ---------------------------------------------------------------------------
def load_summarizer(provider_name):
    sys.path.insert(0, str(CODEBASE))
    from llm_provider import create_provider  # noqa: E402
    from tom_tat_bot import TomTatBot  # noqa: E402  (đúng prompt của bot; nạp codebase/.env)

    try:
        llm = create_provider(provider_name)
    except ValueError as e:
        sys.exit(f"{e} — hoặc chạy --dry-run để thử bộ chấm.")
    return TomTatBot(llm=llm).summarize_with_ai, f"{llm.name}:{llm.model}", llm


async def run(args):
    golden = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    cases = golden["cases"]
    if args.only:
        wanted = set(args.only.split(","))
        cases = [c for c in cases if c["id"] in wanted]

    summarize, model, llm = load_summarizer("fake" if args.dry_run else args.provider)
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + ("-dry" if args.dry_run else "")
    out_dir = Path(args.out) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Lượt {run_id} · {model} · {len(cases)} case · nghỉ {args.delay}s/case · log: {out_dir / 'trace.jsonl'}")

    records = []
    # buffering=1: ghi từng dòng xuống đĩa ngay, xem được tiến độ khi đang chạy / còn log nếu bị dừng giữa chừng
    with open(out_dir / "trace.jsonl", "w", encoding="utf-8", buffering=1) as trace:
        for case in cases:
            if records and args.delay:
                await asyncio.sleep(args.delay)
            input_text = build_messages_text(case)
            attempts = []
            for attempt in range(1, args.retries + 2):
                t0 = time.perf_counter()
                output = await summarize(input_text, mode=case["mode"])
                latency_ms = int((time.perf_counter() - t0) * 1000)
                is_error = output.startswith("Lỗi khi tóm tắt:")
                retryable = is_error and bool(RATE_LIMIT_RE.search(output))
                will_retry = retryable and attempt <= args.retries
                # Ghi MỌI lần gọi, kể cả lần lỗi đã được thử lại
                trace.write(json.dumps({
                    "run_id": run_id, "case_id": case["id"], "attempt": attempt, "final": not will_retry,
                    "model": model, "mode": case["mode"], "api_error": is_error,
                    "usage": None if is_error else getattr(llm, "last_usage", None),
                    "finish_reason": None if is_error else getattr(llm, "last_finish_reason", None),
                    "latency_ms": latency_ms, "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "input_text": input_text, "output": output,
                }, ensure_ascii=False) + "\n")
                attempts.append({"attempt": attempt, "api_error": is_error, "latency_ms": latency_ms})
                if is_error and "PerDay" in output:
                    sys.exit(f"Hết quota theo NGÀY của provider ({model}) — thử lại vô ích. Đổi model/provider hoặc chờ reset quota. Log: {out_dir}")
                if not will_retry:
                    break
                wait = max(args.delay, 5) * 2 ** attempt
                print(f"          … lần {attempt} lỗi tạm thời ({output[16:90].strip()}…), chờ {wait:.0f}s rồi thử lại")
                await asyncio.sleep(wait)
            checks = grade(case, output, input_text)
            passed = (not is_error) and all(c["passed"] for c in checks)
            usage = None if is_error else getattr(llm, "last_usage", None)
            rec = {
                "id": case["id"], "group": case["group"], "mode": case["mode"], "title": case["title"],
                "source": case["source"], "passed": passed, "api_error": is_error,
                "latency_ms": latency_ms, "attempts": len(attempts), "usage": usage, "checks": checks,
            }
            records.append(rec)
            mark = "PASS" if passed else ("API-ERR" if is_error else "FAIL")
            tokens = f" · {usage['total_tokens']} tok" if usage and usage.get("total_tokens") else ""
            print(f"[{mark:7}] {case['id']:4} {case['title']} · {latency_ms} ms{tokens}")
            for c in checks:
                if not c["passed"]:
                    print(f"          ✗ {c['dim']} {c['type']}: {c['detail']}")

    write_results(out_dir, run_id, model, records)


def write_results(out_dir, run_id, model, records, suffix=""):
    summary = summarize_records(records)
    (out_dir / f"results{suffix}.json").write_text(
        json.dumps({"run_id": run_id, "model": model, "summary": summary, "cases": records}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / f"results{suffix}.md").write_text(render_markdown(run_id, model, summary, records), encoding="utf-8")
    print(f"\nTổng: {summary['cases_passed']}/{summary['cases_total']} case đạt ({summary['case_pass_rate']}%)")
    for dim, d in summary["by_dim"].items():
        print(f"  {dim} {DIM_NAMES[dim]}: {d['cases_passed']}/{d['cases_total']} case ({d['rate']}%)")
    print(f"Đã ghi: {out_dir / f'results{suffix}.md'}")


def regrade(args):
    """Chấm lại output đã lưu trong trace.jsonl bằng golden set + bộ chấm hiện tại. Không gọi AI.
    Ghi ra results_regrade.{md,json}, giữ nguyên results.{md,json} gốc để đối chiếu."""
    run_dir = Path(args.regrade)
    cases = {c["id"]: c for c in json.loads(Path(args.cases).read_text(encoding="utf-8"))["cases"]}
    finals, attempts, model = {}, {}, None
    for line in (run_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines():
        t = json.loads(line)
        model = t["model"]
        attempts[t["case_id"]] = attempts.get(t["case_id"], 0) + 1
        if t.get("final", True):
            finals[t["case_id"]] = t
    records = []
    for cid, t in finals.items():
        case = cases[cid]
        is_error = t["output"].startswith("Lỗi khi tóm tắt:")
        checks = grade(case, t["output"], build_messages_text(case))
        records.append({
            "id": cid, "group": case["group"], "mode": case["mode"], "title": case["title"], "source": case["source"],
            "passed": (not is_error) and all(c["passed"] for c in checks), "api_error": is_error,
            "latency_ms": t["latency_ms"], "attempts": attempts[cid], "usage": t.get("usage"), "checks": checks,
        })
    print(f"Chấm lại {len(records)} case từ {run_dir / 'trace.jsonl'} (không gọi AI)")
    write_results(run_dir, run_dir.name + " (chấm lại)", model, records, suffix="_regrade")


def pct(a, b):
    return round(100 * a / b, 1) if b else 0.0


def summarize_records(records):
    by_group, by_dim = {}, {}
    for r in records:
        g = by_group.setdefault(r["group"], {"cases_total": 0, "cases_passed": 0})
        g["cases_total"] += 1
        g["cases_passed"] += r["passed"]
        for dim in sorted({c["dim"] for c in r["checks"]}):
            d = by_dim.setdefault(dim, {"cases_total": 0, "cases_passed": 0})
            d["cases_total"] += 1
            d["cases_passed"] += all(c["passed"] for c in r["checks"] if c["dim"] == dim) and not r["api_error"]
    for bucket in (*by_group.values(), *by_dim.values()):
        bucket["rate"] = pct(bucket["cases_passed"], bucket["cases_total"])
    total, ok = len(records), sum(r["passed"] for r in records)
    return {
        "cases_total": total, "cases_passed": ok, "case_pass_rate": pct(ok, total),
        "by_group": by_group, "by_dim": dict(sorted(by_dim.items())),
        "api_errors": sum(r["api_error"] for r in records),
        "retried_cases": sum(r["attempts"] > 1 for r in records),
        "total_tokens": sum((r["usage"] or {}).get("total_tokens") or 0 for r in records),
        "avg_latency_ms": int(sum(r["latency_ms"] for r in records) / total) if total else 0,
    }


def render_markdown(run_id, model, summary, records):
    lines = [
        f"# Kết quả eval · lượt `{run_id}`",
        "",
        f"- Model: `{model}` · Hàm: `TomTatBot.summarize_with_ai`",
        f"- **Tổng: {summary['cases_passed']}/{summary['cases_total']} case đạt ({summary['case_pass_rate']}%)** · lỗi API: {summary['api_errors']}",
        f"- Case phải thử lại: {summary['retried_cases']} · tổng token (lần thử cuối): {summary['total_tokens']} · latency TB: {summary['avg_latency_ms']} ms",
        "- Log đầy đủ mọi lần gọi (kể cả lần lỗi đã thử lại): `trace.jsonl`",
        "",
        "## Theo chiều chất lượng",
        "",
        "| Chiều | Case đạt | Tỷ lệ |",
        "|---|---|---|",
    ]
    for dim, d in summary["by_dim"].items():
        lines.append(f"| {dim} · {DIM_NAMES[dim]} | {d['cases_passed']}/{d['cases_total']} | {d['rate']}% |")
    lines += ["", "## Theo nhóm case", "", "| Nhóm | Case đạt | Tỷ lệ |", "|---|---|---|"]
    for g, d in summary["by_group"].items():
        lines.append(f"| {GROUP_NAMES.get(g, g)} | {d['cases_passed']}/{d['cases_total']} | {d['rate']}% |")
    lines += [
        "", "## Từng case", "",
        "| ID | Nhóm | Mode | Nguồn | Kết quả | Check trượt | Người chấm lại |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in records:
        failed = "; ".join(f"{c['dim']} {c['type']}: {c['detail']}" for c in r["checks"] if not c["passed"])
        if r["api_error"]:
            failed = "Lỗi API — " + failed
        verdict = "✅" if r["passed"] else "❌"
        failed = failed.replace("|", "\\|")
        lines.append(f"| {r['id']} | {GROUP_NAMES.get(r['group'], r['group'])} | {r['mode']} | {r['source']} | {verdict} | {failed} | |")
    lines += [
        "",
        "## Phân tích case trượt",
        "",
        "> Điền tay: với mỗi case ❌, mở `trace.jsonl` xem output thật → lỗi ở prompt, ở model, hay ở bộ chấm quá chặt? Không sửa golden set để 'cho qua'.",
        "",
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cases", default=str(ROOT / "eval" / "golden_set.json"))
    ap.add_argument("--out", default=str(ROOT / "eval" / "runs"))
    ap.add_argument("--only", help="danh sách id, cách nhau bởi dấu phẩy, ví dụ K3a,K3b")
    ap.add_argument("--delay", type=float, default=4.0, help="giây nghỉ giữa các case (tránh rate limit)")
    ap.add_argument("--retries", type=int, default=3, help="số lần thử lại khi bị rate limit (chờ tăng dần)")
    ap.add_argument("--provider", help="ghi đè LLM_PROVIDER trong .env")
    ap.add_argument("--dry-run", action="store_true", help="không gọi AI; dùng FakeProvider để thử bộ chấm")
    ap.add_argument("--regrade", metavar="RUN_DIR", help="chấm lại trace.jsonl của một lượt cũ, không gọi AI")
    args = ap.parse_args()
    if args.regrade:
        regrade(args)
    else:
        asyncio.run(run(args))


if __name__ == "__main__":
    main()
