---
name: email-receive
description: Receive and read emails via IMAP using settings from a local .env file, with optional attachment download. Use when the user asks to fetch, check, read, or pull emails from a configured mailbox (e.g. "check my inbox", "fetch recent emails").
---

# Email Receive

Fetches messages from an IMAP mailbox using credentials from `.env`, then presents sender, subject, and date (and optionally body and attachments) to the user.

## When to use
- The user asks to check / fetch / read new or recent email.
- The user asks to pull email or download attachments for an account configured in `.env`.

## Workflow
1. Locate `.env` (search order: current working directory, then the skill folder, then the home directory; override with `--env <path>`).
2. Make sure the required keys are set: `IMAP_HOST`, `EMAIL_USER`, `EMAIL_PASSWORD`. Copy the template [.env.example](.env.example) to `.env`, and see [references/providers.md](references/providers.md) for provider-specific help.
3. Run the fetch script and summarize the results:
   ```bash
   python scripts/fetch_emails.py --limit 10
   ```
4. Present sender / subject / date to the user. Use `--full` for body text, `--attachments <dir>` to save attachments.
5. Draft or send replies only at the user's explicit request.

## Options
- `--limit N` — max messages to fetch (default: `EMAIL_FETCH_LIMIT` or 10)
- `--folder NAME` — IMAP folder (default: `IMAP_MAILBOX` or `INBOX`)
- `--days N` — only messages from the last N days
- `--full` — include body text
- `--attachments DIR` — save attachments into `DIR` (created if missing); attachment names are always listed
- `--list-folders` — list available IMAP folders and exit
- `--env PATH` — path to a specific `.env` file

## Examples
```bash
python scripts/fetch_emails.py --limit 5
python scripts/fetch_emails.py --days 1 --full
python scripts/fetch_emails.py --attachments downloads
python scripts/fetch_emails.py --list-folders
```

## Security
- Never print, log, or commit passwords / authorization codes.
- `.env` is local-only; use app-specific passwords or authorization codes where the provider offers them.
- If a credential may have leaked, revoke it in the provider's account settings immediately.
