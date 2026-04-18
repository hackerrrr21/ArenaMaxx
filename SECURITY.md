# Security Policy

## Supported Versions

ArenaMaxx is currently in active development for the PromptWars Virtual event. We only provide security support for the latest branch.

| Version | Supported          |
| ------- | ------------------ |
| 3.0.x   | :white_check_mark: |
| < 3.0   | :x:                |

## Reporting a Vulnerability

We take the security of the ArenaMaxx platform seriously. If you believe you have found a security vulnerability, please report it to us responsibly.

**Please do not report security vulnerabilities via public GitHub issues.**

Instead, please send an email to `security-audit@arenamaxx.local`. 

### What to include in your report:

-   A detailed description of the vulnerability.
-   Steps to reproduce the issue (PoC scripts or screenshots are highly encouraged).
-   Potential impact of the vulnerability.
-   Any suggested fixes or mitigations.

### Our Commitment:

-   We will acknowledge receipt of your report within 48 hours.
-   We will provide an estimated timeline for a fix.
-   We will notify you once the vulnerability has been resolved.
-   We will prioritize critical vulnerabilities (e.g., RCE, Data Exfiltration) for immediate patching.

## Security Features in ArenaMaxx

-   **Input Sanitization**: All user-provided strings are sanitized using `bleach` to prevent XSS and injection attacks.
-   **Security Headers**: Industry-standard headers (CSP, HSTS, X-Frame-Options) are enforced via `Flask-Talisman`.
-   **Rate Limiting**: API endpoints are protected against brute-force and DoS attacks using `Flask-Limiter`.
-   **Secret Management**: Sensitive credentials (API keys) are managed via **Google Cloud Secret Manager**.
-   **Audit Logging**: Security events are streamed to **Google Cloud Logging** for forensic analysis.
-   **Encryption**: All client-server communication is expected to be over TLS (HTTPS).

---
*Last updated: April 18, 2026*
