# Security Policy

## Reporting a vulnerability

If you discover a security issue in AI Signal Desk, please report it privately.

- Preferred: open a [GitHub private security advisory](https://github.com/DCCA/ai-signal-desk/security/advisories/new).
- Alternatively, email the maintainers via the address listed on the
  [contact page](https://aisignaldesk.ai/contact.html).

Please do not open public issues for security problems. We aim to acknowledge
reports within a few business days.

## Scope

This is a static website (HTML, CSS, and a small amount of client-side
JavaScript) deployed to GitHub Pages. There is no backend, database, or stored
user data. The most relevant areas are:

- Cross-site scripting (XSS) in the client-side digest renderer (`app.js`).
- Content injection via `content/digest.json`.
- Supply-chain issues in the GitHub Actions deploy workflow.

## Hardening in place

- **Content-Security-Policy** is set via a `<meta>` tag on every page with
  `script-src 'self'` (no inline scripts), restricting styles, fonts, images,
  and connections to known origins.
- **No inline scripts or event handlers**; all JavaScript is loaded from
  same-origin files.
- **Output encoding**: all dynamic digest fields are HTML-escaped, and link
  URLs are scheme-validated (only `http(s)`, `mailto`, and relative paths) in
  `app.js`.
- **Pinned, minimal-permission CI**: deploy actions are pinned to commit SHAs,
  the workflow uses least-privilege `GITHUB_TOKEN` permissions, and Dependabot
  keeps the pinned actions patched.
- **Custom domain** served over HTTPS with domain verification to prevent
  takeover.

## Known platform limitations

GitHub Pages cannot send custom HTTP response headers, so header-only controls
(HSTS, `X-Content-Type-Options`, `X-Frame-Options` / CSP `frame-ancestors`)
cannot be enforced from this repo alone. To add them, front the site with a CDN
or reverse proxy (for example, Cloudflare) that injects these headers.
