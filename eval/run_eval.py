"""
run_eval.py — Chạy golden set (golden_set.json) qua TomTatBot.summarize_with_ai() THẬT của nhánh
DAQuan (codebase/tom_tat_bot.py — có cơ chế trích dẫn [#N] -> link nguồn, kênh thông báo riêng
từng người) và chấm tự động.

Lịch sử: bộ chấm rule-based (include/exclude/forbid_line/no_new_datetimes/no_new_numbers/
min_bullets/max_chars) và 23/27 case gốc do Nguyễn Khắc Giáp thiết kế trên nhánh main, đo trên
một bản bot khác (có llm_provider.py + tính năng hỏi-đáp, KHÔNG có cơ chế trích dẫn [#N]). File
này là bản gộp: giữ nguyên bộ chấm + phần lớn case của Giáp, chuyển sang gọi đúng bot thật của
DAQuan, và thêm check citation_valid (D2) + max_bullets (D4) cho phù hợp cơ chế trích dẫn.

Cách dùng (chạy từ thư mục gốc repo, cần OPENAI_API_KEY trong codebase/.env):
    python eval/run_eval.py                  # lượt thật, cả 33 case
    python eval/run_eval.py --only K3a,H02    # chỉ chạy case chỉ định
    python eval/run_eval.py --dry-run         # không gọi AI, chỉ kiểm tra script + bộ chấm

Đầu ra (mỗi lượt một thư mục eval/runs/<run_id>/):
    trace.jsonl     — input gửi AI + output thô + latency từng case (bằng chứng lời gọi AI thật cho R5)
    results.json    — kết quả từng check
    results.md      — bảng tổng hợp để dán vào eval/run_results.md và spec.md §7

Bộ chấm chỉ dùng luật so khớp chuỗi (không dùng LLM chấm) để người ngoài nhóm chạy lại ra đúng kết
quả. Định nghĩa từng loại check: eval/README.md.
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
        _stream.reconfigure(encoding="utf-8", line_buffering=True)

ROOT = Path(__file__).resolve().parent.parent
CODEBASE = ROOT / "codebase"
sys.path.insert(0, str(CODEBASE))

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
# Dựng messages_text ĐÚNG như bot thật dùng: tom_tat.format_indexed_messages() — đánh số [#N]
# trước mỗi tin để bot trích dẫn lại, y hệt luồng /tom-tat-thong-bao và /tom-tat-tro-chuyen thật.
# jump_url là placeholder (không có Discord thật đứng sau) — chỉ dùng để kiểm citation hợp lệ.
# ---------------------------------------------------------------------------
def build_items(case):
    inp = case["input"]
    items = []
    for a in inp.get("announcements", []):
        items.append({**a, "jump_url": f"https://discord.com/channels/eval/{case['id']}-{len(items)}"})
    for m in inp.get("messages", []):
        items.append({**m, "channel": m.get("channel", ""), "jump_url": f"https://discord.com/channels/eval/{case['id']}-{len(items)}"})
    return items


def build_messages_text(case, tom_tat):
    items = build_items(case)
    include_channel = bool(case["input"].get("announcements")) and case["mode"] == "notice"
    text, index_to_url, _ = tom_tat.format_indexed_messages(items, include_channel=include_channel)
    return text, len(items)


# ---------------------------------------------------------------------------
# Chuẩn hoá để so khớp: chữ thường, Unicode NFC, ngày về dạng d/m, giờ về dạng H:MM
# ---------------------------------------------------------------------------
DATE_RE = re.compile(r"(?<!\d)(\d{1,2})\s*[/-]\s*(\d{1,2})(?:\s*[/-]\s*\d{2,4})?(?!\d)")
TIME_RE = re.compile(r"(?<![\d/])(\d{1,2})(?::(\d{2})|\s*(?:h|giờ)(?:\s*(\d{2}))?(?!\w))(?![\d/])")
# ':' KHÔNG nằm trong tập loại trừ: thời gian "H:MM" thật đã bị regex ở numbers_in() cắt bỏ TRƯỚC
# khi NUM_RE chạy, nên giữ ':' ở đây chỉ gây lệch giả — số ngay trước dấu ':' kiểu nhãn người nói
# ("Học viên 01:") bị loại khỏi tập input hợp lệ, trong khi cùng số đó đứng trước dấu cách trong
# output ("Học viên 01 báo cáo...") lại được tính — phát hiện qua case C01 (17/9).
NUM_RE = re.compile(r"(?<![\w/])\d+(?![\w/])")
CITATION_RE = re.compile(r"\[#(\d+)\]")


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


RATE_LIMIT_RE = re.compile(r"429|503|rate.?limit|resource.?exhausted|quota|too many requests|unavailable|high demand|overloaded", re.I)
BULLET_RE = re.compile(r"^\s*(?:\*\*)?\s*(?:[-*•+]|\d+[.)])\s+")


# ---------------------------------------------------------------------------
# Các loại check (giữ nguyên bộ của Giáp, thêm max_bullets + citation_valid)
# ---------------------------------------------------------------------------
def check_include(chk, output, _input_text, _n_items):
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


def check_exclude(chk, output, _input_text, _n_items):
    out = canon(output)
    found = [t for t in chk["tokens"] if canon(t) in out]
    return (not found), (f"xuất hiện: {found}" if found else "không xuất hiện chuỗi cấm")


def check_forbid_line(chk, output, _input_text, _n_items):
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


def check_no_new_datetimes(_chk, output, input_text, _n_items):
    in_dates, in_times = datetimes_in(input_text)
    out_dates, out_times = datetimes_in(output)
    new_dates = out_dates - in_dates

    def time_ok(t):
        h, mm = t.split(":")
        alt = f"{(int(h) + 12) % 24}:{mm}"
        return t in in_times or alt in in_times

    new_times = {t for t in out_times if not time_ok(t)}
    ok = not new_dates and not new_times
    return ok, ("không có ngày/giờ lạ" if ok else f"ngày lạ {sorted(new_dates)} · giờ lạ {sorted(new_times)}")


def check_no_new_numbers(_chk, output, input_text, _n_items):
    allowed = numbers_in(input_text) | {str(i) for i in range(0, 11)}
    # Số trong thẻ trích dẫn [#N] không tính là "số lạ" (đó là chỉ số nguồn, không phải nội dung)
    out_no_cite = CITATION_RE.sub(" ", output)
    new = sorted(numbers_in(out_no_cite) - allowed, key=lambda x: int(x))
    return (not new), (f"số lạ: {new}" if new else "không có số lạ")


def check_min_bullets(chk, output, _input_text, _n_items):
    n = sum(1 for line in output.splitlines() if BULLET_RE.match(line))
    return n >= chk["n"], f"{n} gạch đầu dòng (cần ≥ {chk['n']})"


def check_max_bullets(chk, output, _input_text, _n_items):
    n = sum(1 for line in output.splitlines() if BULLET_RE.match(line))
    return n <= chk["n"], f"{n} gạch đầu dòng (cần ≤ {chk['n']})"


def check_max_chars(chk, output, _input_text, _n_items):
    return len(output) <= chk["n"], f"{len(output)} ký tự (tối đa {chk['n']})"


def check_citation_valid(_chk, output, _input_text, n_items):
    """D2 — mọi [#N] AI trích phải trỏ tới 1 tin có thật trong input (không bịa số)."""
    nums = [int(m) for m in CITATION_RE.findall(output)]
    fabricated = sorted({n for n in nums if n < 1 or n > n_items})
    ok = not fabricated
    return ok, ("không bịa số trích dẫn" if ok else f"bịa số trích dẫn: {fabricated}")


CHECKS = {
    "include": check_include,
    "exclude": check_exclude,
    "forbid_line": check_forbid_line,
    "no_new_datetimes": check_no_new_datetimes,
    "no_new_numbers": check_no_new_numbers,
    "min_bullets": check_min_bullets,
    "max_bullets": check_max_bullets,
    "max_chars": check_max_chars,
    "citation_valid": check_citation_valid,
}


def grade(case, output, input_text, n_items):
    results = []
    for chk in case["checks"]:
        ok, detail = CHECKS[chk["type"]](chk, output, input_text, n_items)
        results.append({"type": chk["type"], "dim": chk["dim"], "passed": ok, "detail": detail, "note": chk.get("note", "")})
    # citation_valid áp dụng cho MỌI case (không cần khai riêng trong golden_set.json) — cơ chế
    # trích dẫn [#N] là hành vi bắt buộc của bot thật (xem prompt trong codebase/tom_tat_bot.py).
    ok, detail = check_citation_valid(None, output, input_text, n_items)
    results.append({"type": "citation_valid", "dim": "D2", "passed": ok, "detail": detail, "note": "áp dụng tự động cho mọi case"})
    return results


# ---------------------------------------------------------------------------
# Gọi AI — dùng đúng module thật của DAQuan (client OpenAI trực tiếp, không qua llm_provider)
# ---------------------------------------------------------------------------
class FakeTomTat:
    """--dry-run: không gọi mạng, chỉ thử luồng script + bộ chấm."""

    def format_indexed_messages(self, items, include_channel=False, start_index=1):
        lines, index_to_url, idx = [], {}, start_index
        for it in items:
            prefix = f"[#{idx}] [{it.get('time', '')}]"
            if include_channel:
                prefix += f" {it.get('channel', '')}:"
            lines.append(f"{prefix} {it.get('author', '?')}: {it.get('content', '')}")
            index_to_url[idx] = it.get("jump_url")
            idx += 1
        return "\n".join(lines), index_to_url, idx

    async def summarize_with_ai(self, messages_text, mode="notice"):
        lines = [l for l in messages_text.splitlines() if l.strip()]
        return "\n".join(f"- {l}" for l in lines[:5])


def load_summarizer(dry_run):
    if dry_run:
        return FakeTomTat(), "fake:echo"
    from tom_tat_bot import tom_tat  # noqa: E402  (đúng prompt + client thật, nạp codebase/.env)
    return tom_tat, f"openai:{__import__('tom_tat_bot').OPENAI_MODEL}"


async def run(args):
    golden = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    cases = golden["cases"]
    if args.only:
        wanted = set(args.only.split(","))
        cases = [c for c in cases if c["id"] in wanted]

    tom_tat, model = load_summarizer(args.dry_run)
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + ("-dry" if args.dry_run else "")
    out_dir = Path(args.out) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Lượt {run_id} · {model} · {len(cases)} case · nghỉ {args.delay}s/case · log: {out_dir / 'trace.jsonl'}")

    records = []
    with open(out_dir / "trace.jsonl", "w", encoding="utf-8", buffering=1) as trace:
        for case in cases:
            if records and args.delay:
                await asyncio.sleep(args.delay)
            input_text, n_items = build_messages_text(case, tom_tat)
            attempts = []
            is_error = False
            for attempt in range(1, args.retries + 2):
                t0 = time.perf_counter()
                output = await tom_tat.summarize_with_ai(input_text, mode=case["mode"])
                latency_ms = int((time.perf_counter() - t0) * 1000)
                is_error = output.startswith("Lỗi khi tóm tắt:")
                retryable = is_error and bool(RATE_LIMIT_RE.search(output))
                will_retry = retryable and attempt <= args.retries
                trace.write(json.dumps({
                    "run_id": run_id, "case_id": case["id"], "attempt": attempt, "final": not will_retry,
                    "model": model, "mode": case["mode"], "api_error": is_error,
                    "latency_ms": latency_ms, "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "input_text": input_text, "output": output,
                }, ensure_ascii=False) + "\n")
                attempts.append({"attempt": attempt, "api_error": is_error, "latency_ms": latency_ms})
                if not will_retry:
                    break
                wait = max(args.delay, 5) * 2 ** attempt
                print(f"          … lần {attempt} lỗi tạm thời ({output[16:90].strip()}…), chờ {wait:.0f}s rồi thử lại")
                await asyncio.sleep(wait)
            checks = grade(case, output, input_text, n_items)
            passed = (not is_error) and all(c["passed"] for c in checks)
            rec = {
                "id": case["id"], "group": case["group"], "mode": case["mode"], "title": case["title"],
                "source": case["source"], "passed": passed, "api_error": is_error,
                "latency_ms": latency_ms, "attempts": len(attempts), "checks": checks,
            }
            records.append(rec)
            mark = "PASS" if passed else ("API-ERR" if is_error else "FAIL")
            print(f"[{mark:7}] {case['id']:11} {case['title']} · {latency_ms} ms")
            for c in checks:
                if not c["passed"]:
                    print(f"          ✗ {c['dim']} {c['type']}: {c['detail']}")

    summary = summarize_records(records)
    (out_dir / "results.json").write_text(
        json.dumps({"run_id": run_id, "model": model, "summary": summary, "cases": records}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "results.md").write_text(render_markdown(run_id, model, summary, records), encoding="utf-8")
    print(f"\nTổng: {summary['cases_passed']}/{summary['cases_total']} case đạt ({summary['case_pass_rate']}%)")
    for dim, d in summary["by_dim"].items():
        print(f"  {dim} {DIM_NAMES[dim]}: {d['cases_passed']}/{d['cases_total']} case ({d['rate']}%)")
    print(f"Đã ghi: {out_dir}")


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
        "avg_latency_ms": int(sum(r["latency_ms"] for r in records) / total) if total else 0,
    }


def render_markdown(run_id, model, summary, records):
    lines = [
        f"# Kết quả eval · lượt `{run_id}`",
        "",
        f"- Model: `{model}` · Hàm: `TomTatBot.summarize_with_ai` (nhánh `DAQuan`, `codebase/tom_tat_bot.py`)",
        f"- **Tổng: {summary['cases_passed']}/{summary['cases_total']} case đạt ({summary['case_pass_rate']}%)** · lỗi API: {summary['api_errors']}",
        f"- Case phải thử lại: {summary['retried_cases']} · latency TB: {summary['avg_latency_ms']} ms",
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
    ap.add_argument("--cases", default=str(Path(__file__).parent / "golden_set.json"))
    ap.add_argument("--out", default=str(Path(__file__).parent / "runs"))
    ap.add_argument("--only", help="danh sách id, cách nhau bởi dấu phẩy, ví dụ K3a,H02")
    ap.add_argument("--delay", type=float, default=4.0, help="giây nghỉ giữa các case (tránh rate limit)")
    ap.add_argument("--retries", type=int, default=3, help="số lần thử lại khi bị rate limit (chờ tăng dần)")
    ap.add_argument("--dry-run", action="store_true", help="không gọi AI; dùng FakeTomTat để thử bộ chấm")
    asyncio.run(run(ap.parse_args()))


if __name__ == "__main__":
    main()
