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

# Create a draft card from a user-shared Discord/Telegram/manual link synthesis payload
python3 scripts/create_link_signal_draft.py --source-platform discord --date YYYY-MM-DD --input payload.json
python3 scripts/create_link_signal_draft.py --source-platform telegram --date YYYY-MM-DD --input payload.json

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

`theme.js` is shared by every page (loaded first): it bootstraps the theme (light/dark via
localStorage + `prefers-color-scheme`) **and** the i18n layer — `window.SD_LOCALE` (path-based:
`/pt/*` is Portuguese), `SD_T(key)` for UI labels, and `SD_PICK(item, field)` which returns a
card's `<field>_pt` value on pt pages (falling back to English). The renderers above use these so
the same code drives both `/` and the `/pt/` mirror; `assert_i18n_contract` enforces the wiring.

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
- **Public/private separation.** This repo deploys its **entire root** to the public web
  **and the repo itself is public** — never commit anything web-private. `publish_signal_drafts.py`
  scrubs drafts against `PRIVATE_PATTERNS` and refuses to promote a card that leaks them. That
  list is the union of generic in-source patterns (`DEFAULT_PRIVATE_PATTERNS`, e.g. local paths)
  and account-specific terms loaded from `scripts/private_patterns.local.txt` — a **gitignored**
  file (so the real handles/tool names never enter this public repo); copy `private_patterns.example.txt`
  to seed it. CI only runs `check_site.py`, never the publish script, so the local file is needed
  only on the editor's machine.

## Editorial pipeline

Draft cards live in `content/drafts/<date>-*.json` with `human_reviewed:false`,
`published:false`, `sanitized:true`. `publish_signal_drafts.py` validates each (schema,
allowed enums, privacy patterns, live `source_url` HTTP check, dedupe by url/title-slug),
computes `signal_score`/`hype_score` if absent, and appends promoted items to
`content/digest.json` (bumping `updated`). Allowed enums: category ∈ {concept, product,
repo, workflow}, status ∈ {learn, try, watch, ignore}, confidence ∈ {high, medium, low}.
See `docs/signal-card-schema.md` and `docs/editorial-workflow.md`.

**Bilingual content — translate BEFORE adding a card.** The site has a Portuguese
mirror at `/pt/`, so the digest is bilingual: every card MUST carry pt-BR translations
`title_pt`, `summary_pt`, `why_it_matters_pt`, `try_this_pt` next to the English fields.
`publish_signal_drafts.py` **rejects** any draft missing them and copies them into
`content/digest.json`; `check_site.py` asserts all four on every item. Never publish an
English-only card — translate first (an LLM translation step is the natural fit; keep
product/proper names untranslated). Renderers fall back to English per-field if one is
ever missing, but the gate stays red until the digest is fully translated.

## Deploy

Pushing to `main` triggers `.github/workflows/deploy-pages.yml`: it runs
`scripts/check_site.py`, then uploads the repo root to GitHub Pages. A red
`check_site.py` blocks deploy. Custom domain `aisignaldesk.ai` is in `CNAME`;
`.nojekyll` disables Jekyll. Workflow action versions are **pinned to commit SHAs**
(with version comments) for supply-chain safety — update both SHA and comment when bumping.
