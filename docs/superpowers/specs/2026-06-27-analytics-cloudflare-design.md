# Analytics: Cloudflare Web Analytics — design

**Date:** 2026-06-27
**Status:** Approved (design); implementation pending CF beacon token
**Branch:** `feat/analytics`

## Context

We have no analytics. The goal is **basic traffic + which pages are consumed
most** — not product analytics (funnels/retention/replay). Mixpanel/PostHog were
considered and rejected for this site: heaviest CSP cost, cookie-consent burden,
and overkill pre-pull (`launch-readiness-plan.md` lists "perfect analytics event
taxonomy" as *not needed yet*). Cloudflare Web Analytics is cookieless, free,
privacy-first, and is already the tool named in `launch-config.md`.

Constraints: public repo (no secrets — the beacon token is public by design,
like the Kit URL), and a **strict CSP** (`script-src 'self'; connect-src 'self'`).

## Decision

**Manual Cloudflare Web Analytics beacon on GitHub Pages**, behind a **bounded,
test-enforced CSP exception**. CF Web Analytics is fundamentally a JS beacon
(loads `static.cloudflareinsights.com`, POSTs to `cloudflareinsights.com`), so a
CSP carve-out is unavoidable for *any* client analytics. We make it explicit,
minimal, and enforced — rather than moving DNS to a Cloudflare proxy for
coarser, JS-free edge metrics (the rejected alternative B).

## Design

### Beacon (all 9 pages)

In the shared head shell, immediately after `<script src="theme.js"></script>`:

```html
<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{"token": "<CF_TOKEN>"}'></script>
```

- External script (`src=`) → satisfies `script-src` with no inline code; the
  `data-cf-beacon` JSON attribute is data, not executable inline script.
- `<CF_TOKEN>` is a 32-hex public token from the Cloudflare dashboard
  (Web Analytics → Add a site). Public by design; safe in a public repo.
- Added to all 9 pages (7 public + 2 preview) so the shared shell stays uniform.

### CSP exception (all 9 pages)

Exactly two hosts added — nothing more:

- `script-src 'self'` → `script-src 'self' https://static.cloudflareinsights.com`
- `connect-src 'self'` → `connect-src 'self' https://cloudflareinsights.com`

The CSP already carries Google-Fonts exceptions (`style-src`/`font-src`); these
are the analytics analog. Everything else (`default-src 'self'`, `object-src
'none'`, no `unsafe-inline`/`unsafe-eval`, `form-action 'self'`) is unchanged.

### `check_site.py` — the exception is the spec

- **Exact CSP:** define the canonical CSP string and assert every page matches it
  verbatim. This *bounds* the exception — any extra domain or drift fails the
  build. "Two documented exceptions" can't silently become a loose CSP.
- **Beacon contract:** `assert_analytics_contract` asserts every page carries the
  CF beacon with a **real 32-hex token**. The placeholder token does not match
  `[0-9a-f]{32}`, so it doubles as the anti-stub guard — red until the real token
  is wired.

### Privacy

`privacy.html` gains a short "Analytics" disclosure: Cloudflare Web Analytics,
**cookieless, no personal data, no cross-site tracking** — consistent with the
Kit disclosure and the site's privacy posture. No consent banner needed
(cookieless).

### Docs

`launch-config.md` note updated to record the manual-beacon + bounded-CSP
approach (it already names Cloudflare Web Analytics as the choice).

## Sequencing

Build against placeholder token `CF-BEACON-TOKEN-PENDING`; the 32-hex regex guard
fails until the real token (from the CF dashboard) is swapped into all 9 pages.

## Out of scope

- Custom events (Subscribe-click conversion, search/filter usage) — RUM pageviews
  only for now.
- Cloudflare-proxy / edge analytics (rejected: DNS migration + coarser metrics).
- Analytics on the `/pt/` pages — those live on `feat/i18n-pt-br`; whoever merges
  both branches must add the beacon there too (follow-up).

## Verification

1. `python3 scripts/check_site.py` → green (exact-CSP + beacon contract pass with
   a real-shaped token; anti-stub guard catches the placeholder).
2. Headless load of a page → the beacon request to `static.cloudflareinsights.com`
   is **allowed by CSP** (no CSP violation in console) and the page still renders.
3. Live, post-deploy: confirm visits appear in the Cloudflare Web Analytics
   dashboard (only the site owner can verify this — like the Kit signup test).
