# AI Signal Desk

Practical AI updates for people who want to understand concepts, products, repos, and workflows without drowning in hype.

## What this is

AI Signal Desk is a static MVP for a content product based on the AI Daily Digest idea.

It is designed to become a public website/newsletter where each AI update answers:

- What is it?
- Why does it matter?
- What should I do next?
- Should I learn, try, watch, or ignore it?

## MVP contents

- `index.html` — static landing page and digest UI
- `about.html` — editorial standard and trust page
- `privacy.html` — free beta email/privacy expectations
- `contact.html` — contact route for signals and feedback
- `weekly.html` — Issue 001 weekly field brief
- `posts/` — launch sample signal reports
- `brand.html` — brand-system preview page
- `logo-exploration.html` — comparison board for six SVG logo directions
- `styles.css` — dark editorial Signal Desk visual system
- `app.js` — loads and filters digest cards
- `content/digest.json` — seeded MVP content
- `docs/product-brief.md` — product direction and editorial rules
- `docs/brand-foundation.md` — positioning, voice, taxonomy, tagline, and copy rules
- `docs/launch-readiness-plan.md` — free beta launch plan, validation path, and launch checklist
- `docs/launch-config.md` — free hosting, waitlist, and beta validation configuration notes
- `docs/editorial-workflow.md` — Hermes-assisted draft-to-publish workflow
- `docs/signal-card-schema.md` — required fields for draft and published signal cards
- `docs/launch-checklist.md` — beta sharing checklist
- `robots.txt` / `sitemap.xml` — launch metadata for crawlers and sharing checks
- `DESIGN.md` — formal design-token/spec file for future agents and UI work
- `assets/brand-mark.svg` — selected Option F minimal ASD brand mark
- `favicon.svg` — site favicon using the selected Option F mark
- `assets/logo-*.svg` — logo exploration variants
- `scripts/check_site.py` — deterministic scaffold/site/brand checks

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
OK: AI Signal Desk static MVP passes scaffold checks
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
2. Add a `/weekly` archive page.
3. Connect a newsletter provider or simple waitlist form.
4. Add a Hermes workflow that turns daily digest notes into draft cards for review.
