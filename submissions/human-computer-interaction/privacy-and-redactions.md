# Privacy and Redactions

## Redacted categories

The following information is intentionally excluded from the HCI records:

- API keys, tokens, and credentials.
- `.env` values.
- Private account emails or identifiers.
- Raw uploaded resumes or pasted personal documents.
- Full unredacted chat logs.
- Hidden infrastructure identifiers not required for product evaluation.
- Raw Cloudflare login callback URLs, OAuth/device-login codes, and tunnel credential material.
- Raw terminal outputs from auth checks when they contain account-specific or request-specific details.
- Any tool output that could reveal secrets.

## Preserved categories

The records preserve:

- Product requirements.
- UX critiques and design direction.
- Data-source transparency requirements.
- Implementation coordination decisions.
- Testing and verification expectations.
- Sanitized user feedback excerpts.

## Rationale

The purpose of this folder is to document the human-computer interaction that shaped the product without leaking private operational details. This preserves design evidence for review while keeping the repository safe to share privately.
