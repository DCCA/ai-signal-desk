# Newsletter: Kit link-out — design

**Date:** 2026-06-27
**Status:** Approved (design); implementation pending Kit URL
**Supersedes:** the `mailto:` waitlist signup described in `docs/launch-config.md`

## Context

Today the newsletter "signup" on every page is **cosmetic**: a non-functional
`<input type="email">` sitting next to a `mailto:signals@aisignaldesk.ai` link
that opens the visitor's mail client. There is no real list and no way to send
the weekly field brief. We want the full loop — **capture + send** — without
breaking the project's hard invariants.

Three constraints dominate the design:

1. **Public repo.** No secret (API key, token) may ever be committed or shipped
   in client JS. The capture path must require *zero* secrets in the repo or browser.
2. **Strict CSP.** `connect-src 'self'`, `form-action 'self'`, `script-src 'self'`
   — no third-party posts, fetches, iframes, or inline script without loosening it.
3. **Zero-build static / no backend.** GitHub Pages, no server, `check_site.py`
   is the whole gate.

For on-site email capture you can have at most two of {form on our page, strict
CSP unchanged, no backend}. We chose the corner that preserves **strict CSP +
no backend**: **link-out**. The signup form lives on a provider-hosted page; our
site holds only one public URL.

**Provider:** Kit (ConvertKit). It hosts the subscribe page, owns double opt-in /
unsubscribe / GDPR, and sends the brief. Its free plan covers all of this from
the dashboard. (Kit's MCP/API is paywalled, but we don't need it — automating
sends is deferred per the launch guardrails. The MCP is local tooling only and
never touches the repo.)

## Goal

Replace the fake form on all pages with an honest, frictionless link-out to a Kit
landing page, change nothing about the CSP/security posture, and update the
contract (`check_site.py`) and docs to match.

## Design

### On-page newsletter band (all 9 pages)

The shared `#newsletter` band becomes a clean call-to-action:

- Headline + value-prop paragraph: **unchanged** (existing copy).
- Replace the `<form class="news-field" …>` (with its `<input>`, `action="mailto:"`,
  `enctype`, `method`, `data-waitlist-link`, and the `mailto:` anchor) with a
  **single link**: `<a class="btn-accent" href="<KIT_URL>" target="_blank" rel="noopener">Subscribe free →</a>`.
- The `.news-trust` line ("Free weekly · No spam · Unsubscribe anytime"): **unchanged**.

`<KIT_URL>` is the Kit landing-page public URL (form: `https://<handle>.kit.com/<slug>`).
The band is byte-identical across pages — `assert_shared_page_contract` already
enforces that, so the URL stays consistent for free.

**Removed:** every `<input type="email">` in the band, every `data-waitlist-link`
attribute, every `action="mailto:…"` / `mailto:` signup anchor, and the now-unused
`<form>` wrapper. The `.news-field` CSS class may be retired or repurposed for the
button row (decide at implementation; keep CSS/JS class names in sync per the
design-system rule).

**Not touched:** `contact.html`'s body link to `mailto:signals@aisignaldesk.ai`
(line ~82) — that is the contact route, not newsletter signup, and stays.

### Hero CTA

`index.html` hero keeps `<a class="btn-accent" href="#newsletter">Subscribe free</a>`
— an in-page scroll to the band. The band is the single place the outbound Kit
link lives; the hero just routes there. No change.

### Security / CSP

**No CSP change.** A plain `<a href>` to Kit is top-level navigation, which is not
governed by `form-action`, `connect-src`, or `script-src`. No third-party script,
no fetch, no iframe, no secret, no backend. The strict-CSP invariant is preserved
exactly.

### Kit configuration (manual, dashboard, free plan)

1. Create a **Landing Page** (or hosted Form) named "AI Signal Desk — Field Brief".
2. Reuse the band copy as headline/subtext.
3. **Opt-in confirmation (double opt-in) ON** — the abuse guard for a public
   subscribe link: entering a stranger's address mails nobody until the owner confirms.
4. Publish; copy the public URL → becomes `<KIT_URL>`.

### Privacy page

Add one disclosure line to `privacy.html`: signups are processed by **Kit
(ConvertKit)** as a third-party email service, with double opt-in and unsubscribe,
linking to Kit's privacy policy. This is the only content change outside the band.

### Docs

- `docs/launch-config.md`: replace the "mailto now / Tally later" waitlist stance
  with "Kit landing-page link-out (free); upgrade to paid Kit + MCP only to
  automate sends once pull is proven."
- `docs/launch-checklist.md`: the Signup item changes from "mailto opens prefilled
  message" to "Subscribe button opens the Kit landing page; double opt-in confirmed".

## `check_site.py` contract changes (the assertions ARE the spec)

Update the newsletter/signup assertions to encode the new behavior:

- **Keep:** `id="newsletter"` band present on every page.
- **Add:** on every public+preview page, the band's CTA `href` equals the real Kit
  URL and matches `https://…kit.com/…` (or the chosen Kit host). Centralize the
  expected URL as one constant in `check_site.py`.
- **Add:** the band carries no `<input>` and no `mailto:` in its signup CTA.
- **Add:** the outbound subscribe link uses `target="_blank"` with `rel="noopener"`.
- **Add (anti-stub guard):** the literal placeholder string (see Sequencing) does
  not appear anywhere — fails the build if a stub ships.
- **Remove:** assertions tied to `data-waitlist-link` / `action="mailto:"` /
  the cosmetic input, if any.

## Sequencing

Implementation is unblocked either way:

- **Preferred:** Kit URL in hand → wire the real URL from the start.
- **Fallback:** build against a single clearly-marked placeholder constant
  `https://KIT-LANDING-URL-PENDING`; `check_site.py`'s anti-stub guard fails until
  it's swapped. One swap per page (the shared band), enforced consistent by the
  page-contract check.

## Out of scope

- Automated/programmatic sending of the brief via Kit API/MCP (paid plan; deferred
  until pull is proven).
- Keeping subscribers on-site (rejected: would require loosening CSP or adding a
  backend).
- Email prefill into Kit from an on-site input (rejected with the input).

## Verification

1. `python3 scripts/check_site.py` → `OK: AI Signal Desk (Daylight Desk) passes
   site + security checks` (new assertions green; placeholder guard green).
2. Serve locally (`python3 -m http.server 8080`); on each page confirm the band
   shows a single "Subscribe free →" button, clicking it opens the Kit landing
   page in a new tab, and no email input remains.
3. Submit a test email on the Kit page → confirm the double opt-in email arrives
   and confirming adds the subscriber in Kit.
4. Visually verify the band in light and dark mode.
