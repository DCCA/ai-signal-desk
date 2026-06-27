# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

AI Signal Desk is a **zero-build static site** (GitHub Pages) for a curated AI-news
product. Plain HTML/CSS/vanilla JS — no bundler, no framework, no `package.json`.
Content is data-driven: every signal card and view is rendered client-side from
`content/digest.json`.

## Commands

```bash
# Serve locally (no build step)
python3 -m http.server 8080        # then open http://localhost:8080

# Validate — the single source of truth for "is this correct?" (also runs in CI)
python3 scripts/check_site.py      # expect: "OK: AI Signal Desk (Daylight Desk) passes site + security checks"

# Promote reviewed draft cards into the public digest
python3 scripts/publish_signal_drafts.py --date YYYY-MM-DD --dry-run   # preview
python3 scripts/publish_signal_drafts.py --date YYYY-MM-DD             # apply
```

There is no test runner beyond `check_site.py`. Treat it as the full gate: it
encodes the page contract, the strict-CSP security invariants, the design-token
system, the JS render-safety rules, and the digest data contract. **Run it after
any change to HTML/CSS/JS/digest before claiming done.** When you add a feature,
extend `check_site.py` to assert it (the assertions ARE the spec).

## Architecture

**Data flow.** `content/digest.json` (`{ publication, tagline, updated, items: Signal[] }`,
where each `Signal` carries a `published_date` — the date spine the archive groups weeks by)
is fetched at runtime and rendered by per-page scripts:
- `signals-shared.js` → `window.SignalDesk`: the shared `buildCard` (DOM-only signal-card
  builder) plus week helpers (`weekKey`/`weekLabel`). Must load **before** its consumers
  `app.js`/`archive.js` (enforced by `assert_archive_contract`).
- `app.js` → home top-signals grid (`index.html`): top N by `signal_score` + wayfinding
  counts, linking into the archive. No filter/sort/search of its own.
- `archive.js` → full back-catalog (`archive.html`): grouped by calendar week (newest first),
  category filter chips, live search, URL-param deep links (`?filter=`, `?q=`). Date is the
  spine; there is deliberately no sort control.
- `signal.js` → article deep-dive (`signal.html?i=N`, where `N` is the 1-based index into the unfiltered digest) + related signals.
- `weekly.js` → weekly brief (`weekly.html`) grouped by verdict (learn/try/watch/ignore).

`theme.js` is shared by every page (light/dark via localStorage + `prefers-color-scheme`).

**Shared page shell.** All seven public pages (`index/archive/signal/weekly/about/privacy/contact`)
plus two preview pages (`brand.html`, `logo-exploration.html`) must carry an identical
head/header/footer/newsletter shell, a11y landmarks (skip link, `<main id="main" tabindex="-1">`),
and the same nav/footer links. `check_site.py::assert_shared_page_contract` enforces this —
copy an existing page's shell when adding one.

**Design system ("Daylight Desk").** All styling lives in `styles.css`, driven by CSS
custom-property tokens on `:root` / `[data-theme="dark"]`. Type is Space Grotesk + IBM
Plex Mono (never Inter). `DESIGN.md` is the token reference. Component classes consumed
by the JS (`.signal-card`, `.bar-fill`, `.chip`, `.seg-btn`, etc.) are checked for
existence — keep CSS and JS class names in sync.

## Non-negotiable invariants (enforced by check_site.py)

- **Strict CSP, no exceptions.** No inline `style="..."`, no `<style>` blocks, no inline
  `<script>` (every script is `src=`). No `'unsafe-inline'` / `'unsafe-eval'`. Dynamic bar
  widths are set via CSSOM (`el.style.setProperty('--w', ...)`), never inline markup.
- **DOM API only in renderers.** `signals-shared.js`/`app.js`/`archive.js`/`signal.js`/`weekly.js`
  build nodes with `createElement` + `textContent`/`createTextNode`. Never `innerHTML =` or `insertAdjacentHTML`
  — digest fields are treated as untrusted. External source links go through `safeUrl` in
  `signal.js` and any `target="_blank"` needs `rel="noopener"`.
- **Public/private separation.** This repo deploys its **entire root** to the public web.
  Never commit anything web-private. `publish_signal_drafts.py` scrubs drafts against
  `PRIVATE_PATTERNS` (e.g. local paths, internal tool names) and refuses to promote a card
  that leaks them.

## Editorial pipeline

Draft cards live in `content/drafts/<date>-*.json` with `human_reviewed:false`,
`published:false`, `sanitized:true`. `publish_signal_drafts.py` validates each (schema,
allowed enums, privacy patterns, live `source_url` HTTP check, dedupe by url/title-slug),
computes `signal_score`/`hype_score` if absent, and appends promoted items to
`content/digest.json` (bumping `updated`). Allowed enums: category ∈ {concept, product,
repo, workflow}, status ∈ {learn, try, watch, ignore}, confidence ∈ {high, medium, low}.
See `docs/signal-card-schema.md` and `docs/editorial-workflow.md`.

## Deploy

Pushing to `main` triggers `.github/workflows/deploy-pages.yml`: it runs
`scripts/check_site.py`, then uploads the repo root to GitHub Pages. A red
`check_site.py` blocks deploy. Custom domain `aisignaldesk.ai` is in `CNAME`;
`.nojekyll` disables Jekyll. Workflow action versions are **pinned to commit SHAs**
(with version comments) for supply-chain safety — update both SHA and comment when bumping.
