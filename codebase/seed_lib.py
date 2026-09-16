"""
seed_lib.py — Hàm dùng chung cho các script seed_*.py: bơm tin nhắn mẫu vào
một kênh Discord qua Webhook (mỗi webhook gắn với đúng 1 kênh).

Mọi nội dung trong các script seed_*.py PHẢI là tin TỰ SOẠN, không phải
nguyên văn dữ liệu K4 thật — xem lý do trong seed_test_channel.py.
"""
import argparse
import sys
import time

import requests


def setup_utf8_console():
    """Console Windows mặc định dùng cp1252, không encode được tiếng Việt có dấu"""
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")


def build_arg_parser(doc):
    ap = argparse.ArgumentParser(description=doc, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--webhook", required=True, help="Discord webhook URL của kênh test tương ứng")
    ap.add_argument("--delay", type=float, default=1.5, help="giây nghỉ giữa các tin (tránh rate limit)")
    return ap


def send_messages(webhook_url, messages, delay=1.5):
    """messages: list[(author_display_name, content)]. Trả về True nếu gửi hết thành công."""
    for author, content in messages:
        resp = requests.post(webhook_url, json={"username": author, "content": content}, timeout=10)
        if resp.status_code >= 300:
            print(f"Lỗi gửi ({resp.status_code}): {resp.text}")
            return False
        preview = content[:60].replace("\n", " ")
        print(f"Đã gửi: {author}: {preview}...")
        time.sleep(delay)
    return True
