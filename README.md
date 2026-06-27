# AI Signal Desk

Practical AI updates for people who want to understand concepts, products, repos, and workflows without drowning in hype.

## What this is

AI Signal Desk is a **live, zero-build static site** (GitHub Pages) for a curated
AI-news product. Each update is a "signal card" that answers:

- What is it?
- Why does it matter?
- What should I do next?
- Should I learn, try, watch, or ignore it?

The site is **bilingual** — English at `/` and Brazilian Portuguese at `/pt/` — with
a curated weekly newsletter (signup via Kit) and privacy-first analytics (Cloudflare).

## Design

The site uses the **"Daylight Desk"** design system: a light/dark editorial theme
driven by a CSS custom-property token set (Space Grotesk + IBM Plex Mono). See
`DESIGN.md` for the token reference. It is a multi-page static site (no build step,
no framework) with a shared header/footer/newsletter shell; every view is rendered
client-side from `content/digest.json` under a strict Content-Security-Policy.

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
- `pt/*.html` — the **Brazilian-Portuguese mirror** of the seven public pages
  (`lang="pt-BR"`, translated shell, EN↔PT header switcher, `hreflang` alternates);
  same renderers, served from the subdirectory with absolute asset paths
- `styles.css` — the Daylight Desk token system + all component styles
- `theme.js` — shared bootstrap loaded first on every page: theme (localStorage +
  `prefers-color-scheme`) **and** the i18n layer — `SD_LOCALE` (path-based: `/pt/*` is
  Portuguese), `SD_T(key)` for UI labels, `SD_PICK(item, field)` for translated content
- `signals-shared.js` — shared signal-card builder + week helpers (DOM API, no innerHTML)
- `app.js` — home "top signals" grid (consumes `signals-shared.js`)
- `archive.js` — archive: week grouping, category filter, search, deep links
- `signal.js` / `weekly.js` — article and current-week rendering from the digest
- `content/digest.json` — `{ publication, tagline, updated, items: Signal[] }` where each
  item carries a `published_date` (the date spine the archive groups by) and **pt-BR
  translations** (`title_pt`, `summary_pt`, `why_it_matters_pt`, `try_this_pt`)
- `docs/*.md` — product brief, brand foundation, editorial workflow, launch notes
- `robots.txt` / `sitemap.xml` — crawler metadata
- `DESIGN.md` — design-token/spec reference
- `assets/brand-mark.svg` / `favicon.svg` — brand mark and favicon
- `scripts/check_site.py` — deterministic site + security checks (run in CI)

> The card index (`01`, `02`, …) is each item's stable 1-based position in the
> full unfiltered digest; it does not change when you filter or sort.

## Newsletter, analytics & content

- **Newsletter** — the signup is a **link-out** to a Kit (ConvertKit) landing page
  with double opt-in. The repo holds only the public URL — no form, no backend, no
  secret — so the strict CSP and the "no third-party POST" posture are preserved.
- **Analytics** — Cloudflare Web Analytics: a cookieless beacon on every page, with no
  cookies or personal data. It is the only third-party script allowed, via a bounded,
  test-enforced CSP exception (`static.cloudflareinsights.com` / `cloudflareinsights.com`).
- **Bilingual content — translate before publishing.** Because of the `/pt/` mirror,
  every signal card is bilingual: a draft MUST include `title_pt`, `summary_pt`,
  `why_it_matters_pt`, `try_this_pt`. `scripts/publish_signal_drafts.py` rejects drafts
  without them and `scripts/check_site.py` asserts all four on every digest item.
  Renderers fall back to English per-field, but the build stays red until the digest is
  fully translated. See `CLAUDE.md` and `docs/editorial-workflow.md`.

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

1. Automate the pt-BR translation step in the editorial feeder so new cards ship
   bilingual without manual work.
2. Grow the curated back-catalog and keep the weekly brief flowing.
3. Once there is proven pull, automate the weekly Kit send (paid plan + API/MCP).
