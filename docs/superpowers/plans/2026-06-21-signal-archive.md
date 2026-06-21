# Signal Archive Implementation Plan

> **For agentic workers:** Steps use checkbox (`- [ ]`) syntax for tracking. This repo has no unit-test runner; the test gate is `python3 scripts/check_site.py`, which encodes the page/security/data contracts. "Red" = add/adjust the assertion so the gate fails; "Green" = implement until it passes. Final gate also includes a manual UI pass in light + dark.

**Goal:** Give readers a date-grouped archive of all signal cards that scales as the digest grows daily, while turning the home page into a lean "best of" front door.

**Architecture:** Zero-build static site. A new `archive.html` + `archive.js` renders every card grouped by calendar week (Monday start), newest first, with search + category filter. Home (`app.js`) trims to the top 9 by signal score and drops its controls. A shared `signals-shared.js` holds the card-builder and date helpers used by both home and archive. `weekly.html` narrows to the current week only.

**Tech Stack:** Vanilla JS (DOM API only, no innerHTML), HTML, CSS custom-property tokens, Python validation script. No new dependencies.

## Global Constraints

- Strict CSP: no inline `style=`, no `<style>`, no inline `<script>` (every script `src=`); bar widths via `el.style.setProperty('--w', pct + '%')`.
- Renderers use the DOM API only: `createElement` + `textContent`/`createTextNode`; never `innerHTML`/`insertAdjacentHTML`.
- Every page shares the head/header/footer/newsletter shell, skip link, `<main id="main" tabindex="-1">`, `theme.js`, CSP meta, and (public pages) canonical + OG + Twitter cards.
- Deep-link contract unchanged: cards link to `signal.html?i=N`, N = 0-based index into the unfiltered digest (`?i=` is 0-based in code; displayed number is N+1).
- Allowed enums: category ∈ {concept, product, repo, workflow}; status ∈ {learn, try, watch, ignore}; confidence ∈ {high, medium, low}.
- The whole repo root deploys to the public web; never commit web-private content.
- `python3 scripts/check_site.py` must print `OK: AI Signal Desk (Daylight Desk) passes site + security checks`.

---

### Task 1: Backfill `published_date` + stamp it in the pipeline

**Files:**
- Modify: `content/digest.json` (add `published_date` to all 29 items)
- Modify: `scripts/publish_signal_drafts.py` (stamp `published_date` in `promote_card`)

**Interfaces:**
- Produces: every digest item carries `published_date` = `"YYYY-MM-DD"`.

- [ ] **Step 1:** Backfill `content/digest.json`: for each item with `source_digest_date`, set `published_date` equal to it; for the 7 seed items without one (`Agent loops`, `Context engineering`, `Herdr`, `Personal AI knowledge workflow`, `Lightweight eval harnesses`, `MCP servers`, `AGI countdown takes`), set `published_date` = `"2026-06-19"`. Use a one-off Python pass that writes back with `json.dumps(..., indent=2, ensure_ascii=False) + "\n"`.
- [ ] **Step 2:** In `scripts/publish_signal_drafts.py::promote_card`, add `"published_date": args.date` — thread `args.date` into `promote_card` (add a `publish_date` parameter, pass it from `main`). Keep `source_digest_date` as-is.
- [ ] **Step 3:** Run `python3 scripts/publish_signal_drafts.py --date 2026-06-21 --dry-run` → expect "No publishable draft cards found." (no drafts), confirming the script still parses.
- [ ] **Step 4:** Commit.

### Task 2: Shared card + date module (`signals-shared.js`)

**Files:**
- Create: `signals-shared.js`

**Interfaces:**
- Produces a global `window.SignalDesk` with:
  - `el(tag, cls, text)` → HTMLElement
  - `buildCard(item, origIdx)` → `<a class="signal-card">` (the exact DOM currently in `app.js::card`, including `setProperty('--w', ...)` bars)
  - `weekStart(dateStr)` → `Date` (Monday 00:00 of the ISO week containing `dateStr`)
  - `weekKey(dateStr)` → `"YYYY-MM-DD"` of that Monday (sortable group key)
  - `weekLabel(dateStr)` → `"Week of Jun 15, 2026"`

- [ ] **Step 1:** Create `signals-shared.js` as an IIFE assigning `window.SignalDesk`. Move `el`, `bar`, and `card` (rename exported as `buildCard`) verbatim from `app.js`. Add date helpers: parse `"YYYY-MM-DD"` as local date, compute Monday (`day = (d.getDay()+6)%7; d.setDate(d.getDate()-day)`), format label with a fixed `['Jan',…,'Dec']` array. `buildCard` must keep `setProperty('--w', pct + '%')`.
- [ ] **Step 2:** Manual sanity (node): `node -e "require('./signals-shared.js')"` will fail on `window`; instead verify by loading in the browser during Task 7. Skip automated step here.
- [ ] **Step 3:** Commit.

### Task 3: Trim the home page

**Files:**
- Modify: `app.js` (render top 9 by signal via shared `buildCard`; remove chips/sort/search wiring; keep wayfinding counts)
- Modify: `index.html` (load `signals-shared.js` before `app.js`; remove toolbar; convert hero search bar into an archive link; add "Browse the full archive" CTA; retarget wayfinding tiles to `archive.html?filter=`)

**Interfaces:**
- Consumes: `window.SignalDesk.buildCard`.

- [ ] **Step 1:** Rewrite `app.js`: fetch digest → `items`; render the top 9 items by `signal_score` desc into `[data-digest-grid]` using `SignalDesk.buildCard(it, origIdx)` (origIdx = original index in `items`); keep `fillWayfinding()` (the `data-count` tiles) and the catch/empty-note. Delete `FILTER_DEFS`, `SORT_DEFS`, `state`, `readParams`, `syncUrl`, `renderChips`, `renderSorts`, `visibleItems`, `wireSearch`, `jumpToDigest`, and the local `el`/`bar`/`card` (now in shared). Update the results label `[data-results-count]` to `"Top 9 signals"` (guard if absent).
- [ ] **Step 2:** Edit `index.html`: add `<script src="signals-shared.js"></script>` before `<script src="app.js"></script>`. Remove the `<div class="toolbar">…</div>` block (chips + sort). Replace the hero `<div class="search-bar">…</div>` with an anchor `<a class="search-bar search-bar-link" href="archive.html" aria-label="Search the full signal archive">` containing the glyph span, a `<span class="search-placeholder">Search the full signal archive…</span>`, and a `<span class="btn-accent">Open archive</span>`. Change the four `way-tile` hrefs and the four nav category links from `index.html?filter=X` to `archive.html?filter=X`. Add, after the cards grid, `<div class="digest-cta"><a class="btn-accent" href="archive.html">Browse the full archive →</a></div>`. Change `<h2>Classified signal cards</h2>` keep; set `[data-results-count]` initial text to `Top signals`.
- [ ] **Step 3:** Serve and eyeball in Task 7.
- [ ] **Step 4:** Commit.

### Task 4: Narrow `weekly.html` to the current week

**Files:**
- Modify: `weekly.js` (filter to the latest week before grouping)
- Modify: `weekly.html` (add "Full archive →" link; clarify heading copy)

**Interfaces:**
- Consumes: `window.SignalDesk.weekKey` (load `signals-shared.js` before `weekly.js`).

- [ ] **Step 1:** In `weekly.html`, add `<script src="signals-shared.js"></script>` before `weekly.js`, and add a link `<a class="wk-archive-link" href="archive.html">Full archive →</a>` near the page intro. Add the nav "Archive" link (handled in Task 6).
- [ ] **Step 2:** In `weekly.js`, after loading `items`, compute the max `weekKey(it.published_date)` across items and filter `items` to only those whose `weekKey` equals it; pass the filtered list to `renderGroups`. `row()` must use the item's original index in the full digest for `signal.html?i=` — map indices before filtering (`items.map((it,i)=>({it,i}))`, filter, then render rows from `{it,i}`).
- [ ] **Step 3:** Eyeball in Task 7 (weekly shows only current week).
- [ ] **Step 4:** Commit.

### Task 5: The archive page

**Files:**
- Create: `archive.html` (shared shell; lightweight controls: search + chips; `data-archive` mount)
- Create: `archive.js` (group by week, filter + search, deep-link params)

**Interfaces:**
- Consumes: `window.SignalDesk.{buildCard, weekKey, weekLabel}`.

- [ ] **Step 1:** Create `archive.html` by copying `index.html`'s shell (head with CSP/referrer/fonts/canonical+OG+Twitter for `https://aisignaldesk.ai/archive.html`, header, newsletter, footer). Title: "Signal archive — AI Signal Desk". Main content: `<h1>Signal archive</h1>` + intro, a toolbar with `<div class="chips" data-filters>` and a search `<input type="search" data-search aria-label="Search the archive" placeholder="Search the archive…">`, then `<div data-archive><noscript><p class="empty-note">Enable JavaScript to view the archive.</p></noscript></div>`. Load `signals-shared.js` then `archive.js` before `</body>`.
- [ ] **Step 2:** Create `archive.js`: fetch digest → `items`; read `?filter=` / `?q=` params and `history.replaceState` sync (reuse the pattern removed from `app.js`); render category chips (All + 4) with counts; wire search input. Render: map items to `{it,i}`, apply filter+query, group surviving rows by `weekKey(it.published_date)`, sort week keys desc, and for each week append a `<section class="archive-week">` with `<div class="archive-week-head"><h2>` = `weekLabel` + a count, then a `<div class="cards-grid">` of `SignalDesk.buildCard(it, i)`. Empty-state `empty-note` when nothing matches. Catch → empty-note.
- [ ] **Step 3:** Eyeball in Task 7 (weeks, filter, search, deep links, light/dark).
- [ ] **Step 4:** Commit.

### Task 6: Navigation, footer, styles, sitemap

**Files:**
- Modify: all 8 HTML pages (`index, signal, weekly, about, privacy, contact, brand, logo-exploration`.html) — shared header nav + footer
- Modify: `styles.css` (`.search-bar-link`, `.digest-cta`, `.archive-week`, `.archive-week-head`, `.wk-archive-link`)
- Modify: `sitemap.xml` (add `archive.html`)

- [ ] **Step 1:** In every page's shared header `<nav class="site-nav">`, add `<a href="archive.html">Archive</a>` (before `weekly.html`) and retarget the four category links to `archive.html?filter=…`. In every page's `<div class="footer-links">`, add `<a href="archive.html">Archive</a>`. (Deterministic project-wide replacement of the exact nav/footer blocks; verify with `grep -c`.)
- [ ] **Step 2:** Add CSS: `.search-bar-link` (flex row matching `.search-bar`, cursor pointer, text-decoration none, `.search-placeholder` muted); `.digest-cta` (centered, margin); `.archive-week` (margin-block) + `.archive-week-head` (flex, baseline, accent rule); `.wk-archive-link`. Use only tokens already in `:root`/dark.
- [ ] **Step 3:** Add `<url><loc>https://aisignaldesk.ai/archive.html</loc>…</url>` to `sitemap.xml`.
- [ ] **Step 4:** Commit.

### Task 7: Update the validation gate + full verification

**Files:**
- Modify: `scripts/check_site.py`

- [ ] **Step 1 (red):** Update `check_site.py`:
  - `PAGES` += `"archive.html"`; `REQUIRED_FILES` += `"archive.html"`, `"archive.js"`, `"signals-shared.js"`.
  - `assert_shared_page_contract`: add `archive.html` to the nav-targets list (`["archive.html","weekly.html","about.html"]`).
  - `assert_home_contract`: replace `index.html?filter={cat}` with `archive.html?filter={cat}`; drop the `data-filters`/`data-sorts`/`data-results-count`/`data-search` hook asserts (home no longer has them); keep `data-digest-grid`, `id="digest"`; assert `archive.html` CTA present (`href="archive.html"`).
  - New `assert_archive_contract()`: `archive.html` has `data-archive`, `data-filters`, `data-search`, loads `signals-shared.js` and `archive.js`, and has canonical/OG/Twitter; `archive.js` groups by week (`weekKey`/`weekLabel` referenced) and links `signal.html?i=`.
  - `assert_js_render_safety`: add `archive.js` and `signals-shared.js` to the innerHTML/textContent loop; move the `setProperty('--w'` assertion to require it in `signals-shared.js` (and keep `signal.js`).
  - `assert_digest_contract`: assert each item has `published_date` matching `^\d{4}-\d{2}-\d{2}$`.
  - `assert_seo_files`: assert `archive.html` in `sitemap.xml`.
  - Call `assert_archive_contract()` in `main()`.
- [ ] **Step 2 (green):** Run `python3 scripts/check_site.py` and fix until it prints the OK line.
- [ ] **Step 3 (UI):** `python3 -m http.server 8080`, then with Playwright screenshot home, archive (default + `?filter=repo` + `?q=`), weekly, and a signal — in light and dark. Confirm: home top-9 + CTA, archive week sections + working filter/search, weekly current-week only, deep links resolve.
- [ ] **Step 4:** Commit.

### Task 8: Ship

- [ ] **Step 1:** Final `python3 scripts/check_site.py` → OK.
- [ ] **Step 2:** Push `feat/signal-archive`, open PR, wait for the Pages workflow check to pass, merge, delete branch.

## Self-review notes

- Spec §1 data model → Task 1 + Task 7 digest assertion. §2 home → Task 3 + home-contract update. §3 weekly → Task 4. §4 archive → Task 5 + archive-contract. §5 shared module → Task 2 + render-safety move. §6 validation/nav/SEO → Task 6 + Task 7. §7 done → Task 7 Step 3 + Task 8.
- `buildCard`'s `setProperty('--w')` moves to `signals-shared.js`, so the render-safety assertion must move there too (Task 7) — otherwise the gate would check `app.js` for a string that no longer exists.
- Index naming: `?i=` is 0-based in `signal.js`; `buildCard` uses `origIdx` (0-based) and displays `origIdx+1`. Weekly/archive must pass the original digest index, not the post-filter index.
