#!/usr/bin/env python3
"""Send email via SMTP using settings from a .env file.

No third-party dependencies: uses smtplib / email from the standard library.

Usage:
    python send_email.py --to a@example.com --subject "Hello" --body "Hi"
    python send_email.py --to a@example.com --subject "Report" --body-file report.txt --attach report.pdf
    python send_email.py --to a@example.com,b@example.com --cc c@example.com --subject "Hi" --body "x"
    python send_email.py --check-auth              # verify SMTP login only (no send)
    python send_email.py ... --dry-run             # render message, do not send
"""

import argparse
import mimetypes
import smtplib
import sys
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from pathlib import Path


def force_utf8_stdout():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        pass


def parse_env_file(path):
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
        values[key.strip()] = value.strip().strip('"').strip("'")
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


def friendly_smtp_error(message):
    text = str(message)
    lower = text.lower()
    if "basic authentication is disabled" in lower:
        hint = ("This provider (Outlook.com / Hotmail / MSN) disabled basic auth: "
                "enable two-step verification and use an app password. "
                "See references/providers.md.")
    elif "authentication" in lower or "username and password not accepted" in lower:
        hint = ("Check EMAIL_USER / EMAIL_PASSWORD - QQ & 163 use an authorization "
                "code, Gmail & Microsoft accounts use an app password.")
    elif "4.7.0" in lower or "5.7." in lower or "blocked" in lower or "rejected" in lower:
        hint = ("Message rejected by the server (spam / frequency limit / invalid "
                "recipient). Slow down and double-check recipients.")
    else:
        hint = ("Check SMTP_HOST / SMTP_PORT / SMTP_SSL / SMTP_STARTTLS and the "
                "credentials. See references/providers.md.")
    return f"[ERROR] SMTP failed: {text}\nHint: {hint}"


def load_config(args):
    env_path = find_env_file(args.env)
    if not env_path.exists():
        sys.exit(
            f"[ERROR] .env file not found at: {env_path}\n"
            "Copy .env.example (next to this script) to .env and fill in the "
            "SMTP_*/EMAIL_* settings."
        )
    config = parse_env_file(env_path)
    host = config.get("SMTP_HOST", "").strip()
    user = config.get("EMAIL_USER", "").strip()
    password = config.get("EMAIL_PASSWORD", "").strip()
    missing = [key for key, value in (
        ("SMTP_HOST", host),
        ("EMAIL_USER", user),
        ("EMAIL_PASSWORD", password),
    ) if not value]
    if missing:
        sys.exit(f"[ERROR] Missing required settings in {env_path}: " + ", ".join(missing))
    use_ssl = as_bool(config.get("SMTP_SSL"), True)
    starttls = as_bool(config.get("SMTP_STARTTLS"), False)
    port = int(config.get("SMTP_PORT") or (465 if use_ssl else 587))
    return {
        "host": host, "port": port, "user": user, "password": password,
        "use_ssl": use_ssl, "starttls": starttls,
        "from_addr": (config.get("EMAIL_FROM") or user).strip(),
        "from_name": config.get("EMAIL_FROM_NAME", "").strip(),
        "reply_to": config.get("EMAIL_REPLY_TO", "").strip(),
        "env_path": env_path,
    }


def connect(cfg):
    try:
        if cfg["use_ssl"]:
            server = smtplib.SMTP_SSL(cfg["host"], cfg["port"], timeout=30)
        else:
            server = smtplib.SMTP(cfg["host"], cfg["port"], timeout=30)
            if cfg["starttls"]:
                server.starttls()
        return server
    except OSError as exc:
        sys.exit(f"[ERROR] Could not connect to {cfg['host']}:{cfg['port']}: {exc}")


def build_message(cfg, args):
    msg = EmailMessage()
    sender = formataddr((cfg["from_name"], cfg["from_addr"])) if cfg["from_name"] else cfg["from_addr"]
    msg["From"] = sender
    msg["To"] = args.to
    if args.cc:
        msg["Cc"] = args.cc
    if args.bcc:
        msg["Bcc"] = args.bcc
    msg["Subject"] = args.subject
    if cfg["reply_to"]:
        msg["Reply-To"] = cfg["reply_to"]
    msg["Message-ID"] = make_msgid(domain=cfg["from_addr"].split("@")[-1])

    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8", errors="replace")
    else:
        body = args.body or ""

    if args.html:
        msg.set_content(body)
        msg.add_alternative(body, subtype="html")
    else:
        msg.set_content(body)

    for path in args.attach:
        path = Path(path)
        if not path.exists():
            sys.exit(f"[ERROR] Attachment not found: {path}")
        ctype, encoding = mimetypes.guess_type(str(path))
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        msg.add_attachment(path.read_bytes(), maintype=maintype, subtype=subtype, filename=path.name)
    return msg


def main():
    parser = argparse.ArgumentParser(description="Send email via SMTP using .env settings.")
    parser.add_argument("--to", help="Recipient(s), comma separated (required unless --check-auth)")
    parser.add_argument("--cc", default=None)
    parser.add_argument("--bcc", default=None)
    parser.add_argument("--subject", default="")
    parser.add_argument("--body", default=None)
    parser.add_argument("--body-file", default=None)
    parser.add_argument("--html", action="store_true", help="Treat body as HTML")
    parser.add_argument("--attach", action="append", default=[], help="File to attach (repeatable)")
    parser.add_argument("--check-auth", action="store_true", help="Only verify SMTP login, send nothing")
    parser.add_argument("--dry-run", action="store_true", help="Render the message, do not send")
    parser.add_argument("--env", default=None)
    args = parser.parse_args()
    force_utf8_stdout()

    cfg = load_config(args)
    server = connect(cfg)
    try:
        try:
            server.login(cfg["user"], cfg["password"])
        except smtplib.SMTPAuthenticationError as exc:
            sys.exit(friendly_smtp_error(exc))
        except smtplib.SMTPException as exc:
            sys.exit(friendly_smtp_error(exc))

        if args.check_auth:
            print(f"[OK] SMTP authentication verified for {cfg['user']} on {cfg['host']}:{cfg['port']}")
            return

        if not args.to:
            sys.exit("[ERROR] --to is required (or use --check-auth to only verify login).")

        msg = build_message(cfg, args)
        if args.dry_run:
            print(msg.as_string())
            return

        server.send_message(msg, from_addr=cfg["from_addr"])
        print(f"[OK] Email sent to {args.to} - subject: {args.subject!r} via {cfg['host']}:{cfg['port']}")
    finally:
        try:
            server.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
