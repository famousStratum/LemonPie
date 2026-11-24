# Security Policy

## Supported Versions

LemonPie is in active pre-1.0 development. Only the latest release
published on PyPI receives security fixes.

## Reporting a Vulnerability

> [!CAUTION]
Please **do not** report security issues in public GitHub issues.
Use GitHub's private reporting: [Open a draft security advisory](https://github.com/famousStratum/LemonPie/security/advisories/new)

Please include affected version, steps to reproduce, and impact.

**What to expect**:
You'll get an acknowledgment within 7 days and a status
update within 14 days. If the report is accepted, the fix will ship in
the next release along with a GitHub security advisory, and you'll be
credited if you'd like. If it's declined, I'll explain why.

## Scope

In scope: handling of API keys and config/session files, path
handling, TLS/HTTP client behavior, terminal output injection, and
vulnerable dependencies or release-pipeline issues.

Out of scope: vulnerabilities in the inference servers LemonPie
connects to, model output or prompt injection, and attacks requiring
existing local access to your user account.

> [!NOTE]
The API key (if configured) is stored in plaintext in your user
config directory, and session history is stored unencrypted in your
user data directory. Protect those directories accordingly.