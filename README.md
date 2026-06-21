# AI Signal Desk

Practical AI updates for people who want to understand concepts, products, repos, and workflows without drowning in hype.

## What this is

AI Signal Desk is a static MVP for a content product based on the AI Daily Digest idea.

It is designed to become a public website/newsletter where each AI update answers:

- What is it?
- Why does it matter?
- What should I do next?
- Should I learn, try, watch, or ignore it?

## Design

The site uses the **"Daylight Desk"** design system: a light/dark editorial
theme driven by a CSS custom-property token set. See `DESIGN.md` for the full
token reference. It is a multi-page static site (no build step) with a shared
header/footer/newsletter and a digest rendered from `content/digest.json`.

## Site contents

- `index.html` — home: a lean front door with hero, "this week at a glance",
  wayfinding, and the **top signals** by score (links into the archive)
- `archive.html` — the full back-catalog, grouped by calendar week (newest
  first), with category filter chips + live search (`archive.html?filter=N`,
  `?q=…`), rendered from the digest
- `signal.html` — article / signal deep-dive (`signal.html?i=N`, rendered from
  the digest; deep-linkable, with related signals)
- `weekly.html` — the weekly field brief, grouped by verdict (learn/try/watch/ignore)
- `about.html` — method (classify / score / action) and principles
- `privacy.html` — email/privacy expectations
- `contact.html` — contact route for signals and feedback
- `styles.css` — the Daylight Desk token system + all component styles
- `theme.js` — theme bootstrap (localStorage + `prefers-color-scheme`) and toggle
- `signals-shared.js` — shared signal-card builder + week helpers (DOM API, no innerHTML)
- `app.js` — home "top signals" grid (consumes `signals-shared.js`)
- `archive.js` — archive: week grouping, category filter, search, deep links
- `signal.js` / `weekly.js` — article and current-week rendering from the digest
- `content/digest.json` — `{ publication, tagline, updated, items: Signal[] }`
  where each item carries a `published_date` (the date spine the archive groups by)
- `docs/*.md` — product brief, brand foundation, editorial workflow, launch notes
- `robots.txt` / `sitemap.xml` — crawler metadata
- `DESIGN.md` — design-token/spec reference
- `assets/brand-mark.svg` / `favicon.svg` — brand mark and favicon
- `scripts/check_site.py` — deterministic site + security checks (run in CI)

> The card index (`01`, `02`, …) is each item's stable 1-based position in the
> full unfiltered digest; it does not change when you filter or sort.

## Run locally

From the repo root:

```bash
python3 -m http.server 8080
```

Open:

```text
http://localhost:8080
```

## Validate

```bash
python3 scripts/check_site.py
```

Expected output:

```text
OK: AI Signal Desk (Daylight Desk) passes site + security checks
```

## Deploy (GitHub Pages)

The site deploys to GitHub Pages from `main` via `.github/workflows/deploy-pages.yml`.
It runs `scripts/check_site.py`, then uploads the repo root and publishes it.
The site is plain static HTML/CSS/JS (a `.nojekyll` file disables Jekyll
processing), and the custom domain is set in `CNAME`.

### First-time setup

1. **Settings -> Pages -> Build and deployment -> Source: GitHub Actions.**
2. Push to `main` (or run the workflow manually from the Actions tab) to deploy.

### Custom domain, DNS, and HTTPS

The primary domain is `aisignaldesk.ai` (in `CNAME`). `aisignaldesk.com` is a
redirect configured at the registrar/DNS (GitHub Pages serves only the single
`CNAME` domain).

1. **DNS for `aisignaldesk.ai`** (apex): add four A records to GitHub Pages:
   `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   (or an `ALIAS`/`ANAME` to `dcca.github.io`). Add a `www` CNAME to
   `dcca.github.io` if you want `www` too.
2. In **Settings -> Pages**, set the custom domain to `aisignaldesk.ai` and,
   once the certificate provisions, enable **Enforce HTTPS**.
3. Point `aisignaldesk.com` at `aisignaldesk.ai` with a registrar/DNS redirect.

### Security notes

- **Verify the domain** to prevent takeover: Settings -> Pages -> "Verify domain"
  (or org-level domain verification). A verified domain cannot be claimed on any
  other GitHub account, which protects against dangling-DNS / subdomain takeover.
  If you ever stop using Pages, remove the DNS records first.
- **Always enable Enforce HTTPS** once the Let's Encrypt certificate is issued.
- **Protect the registrar account** (2FA + registrar/transfer lock). The
  registrar is the most common hijack vector, not GitHub.
- Workflow actions are **pinned to commit SHAs** (with version comments) for
  supply-chain safety. When bumping a version, update both the SHA and comment.
- The deploy publishes the **entire repo root**, so do not commit anything that
  should not be web-accessible.

## Next steps

1. Convert existing AI Daily Digest entries into three long-form sample posts.
2. Connect a newsletter provider or simple waitlist form.
3. Add a Hermes workflow that turns daily digest notes into draft cards for review.
