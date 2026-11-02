---
name: email-send
description: Send emails via SMTP using settings from a local .env file, with optional HTML body and attachments. Use when the user asks to send, compose, or deliver an email to one or more recipients (e.g. "send an email", "email this report").
---

# Email Send

Sends messages through an SMTP server using credentials from `.env`, supporting plain text or HTML bodies and file attachments.

## When to use
- The user asks to send / compose / deliver an email.
- The user asks to email a file, report, or notification to one or more recipients.

## Workflow
1. Locate `.env` (search order: current working directory, then the skill folder, then home; override with `--env <path>`).
2. Make sure the required keys are set: `SMTP_HOST`, `EMAIL_USER`, `EMAIL_PASSWORD`. Copy the template [.env.example](.env.example) to `.env`, and see [references/providers.md](references/providers.md) for provider-specific help.
3. Confirm recipients and content with the user, then send:
   ```bash
   python scripts/send_email.py --to "a@example.com" --subject "Hello" --body "Hi"
   ```
4. Report the result; suggest retrying with `--check-auth` first if authentication fails.

## Options
- `--to` — recipient(s), comma separated (required)
- `--cc`, `--bcc` — optional additional recipients
- `--subject` — subject line
- `--body` — body text, or `--body-file <path>` to read it from a file; `--html` treats it as HTML
- `--attach <file>` — attach a file (repeatable)
- `--check-auth` — verify SMTP login only, send nothing
- `--dry-run` — render the message and print it without sending
- `--env PATH` — path to a specific `.env` file

## Examples
```bash
python scripts/send_email.py --to "a@example.com" --subject "Hello" --body "Hi"
python scripts/send_email.py --to "a@example.com" --subject "Report" --body-file report.txt --attach report.pdf
python scripts/send_email.py --to "a@example.com" --subject "Alert" --html --body "<b>Build failed</b>"
python scripts/send_email.py --check-auth
```

## Security
- Never print, log, or commit passwords / authorization codes.
- `.env` is local-only; use app-specific passwords or authorization codes where the provider offers them.
- Prefer `--check-auth` or `--dry-run` before the first real send to avoid mistakes.
- If a credential may have leaked, revoke it in the provider's account settings immediately.
