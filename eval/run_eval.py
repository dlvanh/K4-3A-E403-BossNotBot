"""
run_eval.py — Chạy trọn golden set (golden_set.py) qua ĐÚNG hàm summarize_with_ai() thật của bot
(import từ tom_tat_bot.py, dùng đúng prompt + client OpenAI thật — chỉ bỏ qua phần Discord Gateway,
giống cách replay_test.py làm), rồi tự chấm 3 chiều chất lượng:

    - citation_validity : mọi [#N] AI trích có tồn tại trong input không (bịa số = fail)
    - coverage          : bao nhiêu % tin/thông báo đầu vào được trích dẫn ít nhất 1 lần
    - format_compliance : đúng cấu trúc bắt buộc của mode (2 nhóm ưu tiên / có liệt kê chủ đề)

3 chiều trên chấm được bằng máy. Đúng-sai về NỘI DUNG (có bịa sự thật không, phân loại ưu tiên có
hợp lý không, có bị dắt mũi bởi prompt injection không...) cần đọc transcript đầy đủ — xem cột
"expect" trong golden_set.py và mục "manual_review" ở cuối bảng kết quả.

Cách dùng:
    python run_eval.py                  # chạy cả 20 case, có gọi OpenAI API thật (cần .env)
    python run_eval.py --case N1 C2     # chỉ chạy case chỉ định (debug nhanh)

Output:
    eval/results/run-<N>-full.md     transcript đầy đủ input/output từng case (KHÔNG commit —
                                      đã bị chặn trong .gitignore vì chứa trích dẫn dài từ data pack)
    eval/results/run-<N>-summary.md  bảng kết quả rút gọn (trích dẫn ≤2 câu/case, kèm msg_id) —
                                      commit được, dùng để dán vào spec.md §7
"""
import argparse
import asyncio
import csv
import io
import re
import sys
from datetime import datetime
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
BOT_DIR = HERE.parent / "codebase"  # bot thật của nhóm nằm ở codebase/ (nhánh DAQuan), không phải
sys.path.insert(0, str(BOT_DIR))    # bản tom_tat_bot.py rác còn sót lại ở gốc discord_bot/
from tom_tat_bot import tom_tat  # noqa: E402  (đúng logic prompt + client thật của bot)

from golden_set import CASES  # noqa: E402

CSV_PATH = HERE.parent.parent / "K4-3A-E403-BotNotBoss" / "data" / "discord-pack" / "k4_messages.csv"

CITATION_RE = re.compile(r"\[#(\d+)\]")


def load_csv_index():
    rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8-sig")))
    return {r["msg_id"]: r for r in rows}


def build_items(case, csv_index):
    """Trả về list item {author, content, time, jump_url, channel} theo đúng thứ tự đưa vào prompt."""
    real_items = []
    for mid in case.get("msg_ids", []):
        r = csv_index[mid]
        real_items.append({
            "author": r["author"],
            "content": r["content"],
            "time": r["created_at_vn"][-5:],
            "jump_url": f"https://discord.com/channels/eval/{mid}",
            "channel": r["channel"],
            "_msg_id": mid,
        })
    synth_items = []
    for i, it in enumerate(case.get("synthetic_items", [])):
        synth_items.append({
            "author": it["author"],
            "content": it["content"],
            "time": it["time"],
            "jump_url": f"https://discord.com/channels/eval/synthetic-{case['id']}-{i}",
            "channel": "synthetic",
            "_msg_id": f"SYN-{case['id']}-{i}",
        })

    order = case.get("order")
    if order:
        pool = {"real": real_items, "synthetic": synth_items}
        return [pool[kind][idx] for kind, idx in order]
    return real_items + synth_items


def check_citation_validity(raw_summary, n_items):
    nums = [int(m) for m in CITATION_RE.findall(raw_summary)]
    fabricated = sorted({n for n in nums if n < 1 or n > n_items})
    ok = len(fabricated) == 0 and len(nums) > 0
    return {"total_citations": len(nums), "fabricated": fabricated, "pass": ok}


def check_coverage(raw_summary, n_items, mode):
    nums = {int(m) for m in CITATION_RE.findall(raw_summary)}
    nums = {n for n in nums if 1 <= n <= n_items}
    ratio = (len(nums) / n_items) if n_items else 1.0
    threshold = 1.0 if mode == "notice" else 0.5
    return {"cited_items": len(nums), "total_items": n_items, "ratio": round(ratio, 2),
            "threshold": threshold, "pass": ratio >= threshold}


def check_format(raw_summary, mode):
    if mode == "notice":
        has_high = bool(re.search(r"Ưu tiên cao", raw_summary))
        has_low = bool(re.search(r"Thông báo khác", raw_summary))
        return {"has_high_header": has_high, "has_low_header": has_low, "pass": has_high and has_low}
    lines = raw_summary.splitlines()
    bullets = [l for l in lines if re.match(r"^\s{0,2}([-*•]|\d+[.)])\s+\S", l)]
    n = len(bullets)
    return {"topic_lines": n, "pass": 1 <= n <= 8}


async def run_case(case, csv_index):
    items = build_items(case, csv_index)
    messages_text, index_to_url, _ = tom_tat.format_indexed_messages(
        items, include_channel=case.get("include_channel", False)
    )
    raw_summary = await tom_tat.summarize_with_ai(messages_text, mode=case["mode"])
    delivered = tom_tat.linkify_citations(raw_summary, index_to_url)

    cv = check_citation_validity(raw_summary, len(items))
    cov = check_coverage(raw_summary, len(items), case["mode"])
    fmt = check_format(raw_summary, case["mode"])
    auto_pass = cv["pass"] and cov["pass"] and fmt["pass"]

    return {
        "case": case, "n_items": len(items), "input_text": messages_text,
        "raw_summary": raw_summary, "delivered": delivered,
        "citation_validity": cv, "coverage": cov, "format": fmt, "auto_pass": auto_pass,
    }


def next_run_number():
    results_dir = HERE / "results"
    results_dir.mkdir(exist_ok=True)
    existing = list(results_dir.glob("run-*-summary.md"))
    nums = [int(re.match(r"run-(\d+)-", p.name).group(1)) for p in existing if re.match(r"run-(\d+)-", p.name)]
    return (max(nums) + 1) if nums else 1


def short_quote(text, max_chars=140):
    text = text.strip().replace("\n", " ")
    return (text[:max_chars] + "…") if len(text) > max_chars else text


def write_reports(results, run_no):
    results_dir = HERE / "results"
    full_path = results_dir / f"run-{run_no}-full.md"
    summary_path = results_dir / f"run-{run_no}-summary.md"

    n_total = len(results)
    n_auto_pass = sum(1 for r in results if r["auto_pass"])
    pct = round(100 * n_auto_pass / n_total, 1) if n_total else 0.0
    n_cv = sum(1 for r in results if r["citation_validity"]["pass"])
    n_cov = sum(1 for r in results if r["coverage"]["pass"])
    n_fmt = sum(1 for r in results if r["format"]["pass"])

    with io.open(full_path, "w", encoding="utf-8") as f:
        f.write(f"# Eval run {run_no} — transcript đầy đủ (KHÔNG commit — xem .gitignore)\n\n")
        f.write(f"Chạy lúc: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        for r in results:
            c = r["case"]
            f.write(f"\n---\n## {c['id']} · mode={c['mode']} · {c['layer']}\n\n")
            f.write(f"**Mô tả:** {c['desc']}\n\n**Kỳ vọng:** {c['expect']}\n\n")
            f.write(f"**Input ({r['n_items']} tin):**\n```\n{r['input_text']}\n```\n\n")
            f.write(f"**Output thô (trước linkify):**\n```\n{r['raw_summary']}\n```\n\n")
            f.write(f"**Tự động chấm:** citation_validity={r['citation_validity']} | "
                    f"coverage={r['coverage']} | format={r['format']} | auto_pass={r['auto_pass']}\n")

    with io.open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"# Eval run {run_no} — bảng kết quả (dùng cho spec.md §7)\n\n")
        f.write(f"Chạy lúc: {datetime.now().strftime('%Y-%m-%d %H:%M')} · model=gpt-4o-mini · "
                f"{n_total} case (golden_set.py)\n\n")
        f.write(f"**Tổng: {n_auto_pass}/{n_total} case đạt cả 3 chiều tự động ({pct}%).** "
                f"citation_validity {n_cv}/{n_total} · coverage {n_cov}/{n_total} · "
                f"format_compliance {n_fmt}/{n_total}.\n\n")
        f.write("> 3 chiều dưới đây chấm được bằng máy (không bịa số trích dẫn, không bỏ sót tin, "
                "đúng cấu trúc bắt buộc). Đúng-sai về **nội dung** (có bịa sự thật, phân loại ưu "
                "tiên có hợp lý, có bị prompt injection dắt mũi không) cần người đọc — xem cột "
                "'Cần người đọc lại'.\n\n")
        f.write("| Case | Mode | Lớp/Bucket | n | citation | coverage | format | Auto | Cần người đọc lại |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for r in results:
            c = r["case"]
            cv, cov, fmt = r["citation_validity"], r["coverage"], r["format"]
            cv_cell = "✅" if cv["pass"] else f"❌ bịa {cv['fabricated']}"
            cov_cell = ("✅" if cov["pass"] else "❌") + f" {cov['cited_items']}/{cov['total_items']}"
            fmt_cell = "✅" if fmt["pass"] else "❌"
            auto_cell = "✅" if r["auto_pass"] else "❌"
            f.write(
                f"| {c['id']} | {c['mode']} | {','.join(c['bucket'])} | {r['n_items']} | "
                f"{cv_cell} | {cov_cell} | {fmt_cell} | {auto_cell} | {c['layer']} |\n"
            )
        f.write("\n## Trích ngắn từng case (≤2 câu/ví dụ, kèm msg_id — theo luật data pack)\n\n")
        for r in results:
            c = r["case"]
            first_id = c.get("msg_ids", ["(synthetic)"])[0] if c["source"] == "real" else "(synthetic)"
            f.write(f"- **{c['id']}** ({first_id}…): {c['desc']}\n"
                    f"  - Output (trích): _{short_quote(r['delivered'])}_\n")

    return full_path, summary_path, pct


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", nargs="*", help="chỉ chạy các case id này, vd --case N1 C2")
    args = ap.parse_args()

    csv_index = load_csv_index()
    cases = CASES
    if args.case:
        wanted = set(args.case)
        cases = [c for c in CASES if c["id"] in wanted]

    results = []
    for i, c in enumerate(cases, 1):
        print(f"[{i}/{len(cases)}] chạy case {c['id']} (mode={c['mode']})...")
        r = await run_case(c, csv_index)
        results.append(r)
        status = "OK" if r["auto_pass"] else "CHECK"
        print(f"    -> {status} | citation={r['citation_validity']['pass']} "
              f"coverage={r['coverage']['pass']} format={r['format']['pass']}")

    run_no = next_run_number()
    full_path, summary_path, pct = write_reports(results, run_no)
    print(f"\nXong. {sum(1 for r in results if r['auto_pass'])}/{len(results)} case đạt cả 3 chiều tự động ({pct}%).")
    print(f"Full transcript: {full_path}")
    print(f"Summary (commit được): {summary_path}")


if __name__ == "__main__":
    asyncio.run(main())
