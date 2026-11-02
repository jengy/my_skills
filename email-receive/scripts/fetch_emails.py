#!/usr/bin/env python3
"""Fetch emails via IMAP using settings from a .env file.

No third-party dependencies: uses imaplib / email from the standard library.

Usage:
    python fetch_emails.py [options]

Options:
    --limit N          Max messages to fetch (default: EMAIL_FETCH_LIMIT or 10)
    --folder NAME      IMAP folder, e.g. INBOX (default: IMAP_MAILBOX or INBOX)
    --days N           Only fetch messages from the last N days
    --full             Also print the message body text
    --list-folders     List available IMAP folders and exit
    --env PATH         Path to a specific .env file
"""

import argparse
import email
import imaplib
import re
import sys
from datetime import datetime, timedelta
from email.header import decode_header
from pathlib import Path


def parse_env_file(path):
    """Load KEY=VALUE pairs from a .env file without python-dotenv."""
    values = {}
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return values
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def find_env_file(explicit):
    if explicit:
        return Path(explicit)
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent / ".env",
        Path.home() / ".env",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path.cwd() / ".env"


def as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def decode_mime_header(value):
    if not value:
        return ""
    parts = decode_header(value)
    out = []
    for raw, charset in parts:
        if isinstance(raw, bytes):
            out.append(raw.decode(charset or "utf-8", errors="replace"))
        else:
            out.append(str(raw))
    return "".join(out)


def decode_part(part):
    payload = part.get_payload(decode=True)
    if payload is None:
        return ""
    charset = part.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace")


def strip_html(html):
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    text = re.sub(r"(?is)<br\s*/?>", "\n", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_body(msg, max_chars=2000):
    parts = []
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                parts.append(decode_part(part))
        if not any(parts):
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    parts.append(strip_html(decode_part(part)))
    elif msg.get_content_type() == "text/plain":
        parts.append(decode_part(msg))
    body = "\n".join(part for part in parts if part).strip()
    return body[:max_chars]


def main():
    parser = argparse.ArgumentParser(
        description="Fetch emails via IMAP using .env settings."
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--folder", default=None)
    parser.add_argument("--days", type=int, default=None)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--list-folders", action="store_true")
    parser.add_argument("--env", default=None)
    args = parser.parse_args()

    env_path = find_env_file(args.env)
    if not env_path.exists():
        sys.exit(
            f"[ERROR] .env file not found at: {env_path}\n"
            "Copy .env.example to .env and fill in the IMAP_*/EMAIL_* settings."
        )
    config = parse_env_file(env_path)

    host = config.get("IMAP_HOST", "").strip()
    port = int(config.get("IMAP_PORT", "993"))
    username = config.get("EMAIL_USER", "").strip()
    password = config.get("EMAIL_PASSWORD", "").strip()
    use_ssl = as_bool(config.get("IMAP_SSL"), True)
    folder = args.folder or config.get("IMAP_MAILBOX", "INBOX")
    limit = args.limit if args.limit is not None else int(
        config.get("EMAIL_FETCH_LIMIT", "10")
    )
    days = args.days if args.days is not None else int(
        config.get("EMAIL_FETCH_DAYS", "0") or 0
    )

    missing = [key for key, value in (
        ("IMAP_HOST", host),
        ("EMAIL_USER", username),
        ("EMAIL_PASSWORD", password),
    ) if not value]
    if missing:
        sys.exit(
            f"[ERROR] Missing required settings in {env_path}: " + ", ".join(missing)
        )

    try:
        if use_ssl:
            conn = imaplib.IMAP4_SSL(host, port)
        else:
            conn = imaplib.IMAP4(host, port)
    except OSError as exc:
        sys.exit(f"[ERROR] Could not connect to {host}:{port}: {exc}")

    try:
        try:
            conn.login(username, password)
        except imaplib.IMAP4.error as exc:
            sys.exit(f"[ERROR] Login failed for {username} on {host}: {exc}")

        if args.list_folders:
            status, folders = conn.list()
            if status != "OK":
                sys.exit("[ERROR] Could not list folders.")
            for entry in folders:
                print(entry.decode(errors="replace"))
            return

        status, _ = conn.select(folder, readonly=True)
        if status != "OK":
            sys.exit(f"[ERROR] Cannot select folder {folder!r}. Check IMAP_MAILBOX.")

        if days > 0:
            since = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
            status, data = conn.search(None, f'(SINCE "{since}")')
        else:
            status, data = conn.search(None, "ALL")

        if status != "OK" or not data or not data[0]:
            print("No messages found.")
            return

        ids = data[0].split()[-limit:]
        for num in reversed(ids):
            status, msg_data = conn.fetch(num, "(RFC822)")
            if status != "OK" or not msg_data or not isinstance(msg_data[0], tuple):
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            sender = decode_mime_header(msg.get("From", ""))
            subject = decode_mime_header(msg.get("Subject", "")) or "(no subject)"
            date = msg.get("Date", "?")
            print(f"From:    {sender}")
            print(f"Subject: {subject}")
            print(f"Date:    {date}")
            if args.full:
                print("Body:")
                print(extract_body(msg))
            print("-" * 60)
    finally:
        try:
            conn.logout()
        except Exception:
            pass


if __name__ == "__main__":
    main()
