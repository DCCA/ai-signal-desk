# Design: Date-grouped Signal Archive

**Date:** 2026-06-21
**Status:** Approved (pre-implementation)
**Branch:** `feat/signal-archive`

## Problem

`index.html` is the only place to browse signal cards. Its grid renders **all**
items into one unbounded list (29 cards today, growing daily via the publish
pipeline) with no pagination. As the back-catalog grows, one infinite grid does
not scale, and there is no date-based way to browse history. The user thinks in
**weeks** and wants both a lean front door and a dedicated archive.

## Goals

- A lean home page that showcases the strongest signals, not the whole history.
- A dedicated archive that scales to hundreds of cards, organized by **calendar
  week** (newest first), with lightweight browsing controls.
- A reliable per-card publish date as the foundation for date grouping.

## Non-goals

- No backend, build step, or framework — stays a zero-build static site.
- No real pagination/infinite-scroll library; week sections are the scaling unit.
- No change to the `signal.html?i=N` deep-link contract (N = 1-based index into
  the unfiltered digest).

## Current-state facts (verified 2026-06-21)

- `content/digest.json` has **29 items**. All carry `signal_score`/`hype_score`.
- Date coverage: **22/29** items have `source_digest_date`; **7 seed items have
  no date** (`Agent loops`, `Context engineering`, `Herdr`, `Personal AI
  knowledge workflow`, `Lightweight eval harnesses`, `MCP servers`, `AGI
  countdown takes`).
- All dated items fall in **2026-06-19 → 2026-06-21** — a single calendar week
  (week of Mon **2026-06-15**). The archive's payoff is future-facing.
- Home grid (`app.js`) already has category filter chips, a sort toggle
  (signal/hype/newest), and live search. "Newest" sorts by array position
  (`b.i - a.i`), not a real date.
- `weekly.html` groups the *current* set by verdict (learn/try/watch/ignore).

## Design

### 1. Data model — canonical per-card date

Introduce **`published_date`** (`YYYY-MM-DD`) on every digest item as the single
source of truth for display and ordering. Rationale: `source_digest_date` means
"date of the *source* digest" (provenance) and is missing on 7 items; a dedicated
field avoids overloading one field with two meanings.

- **Backfill** the 29 existing items: the 22 dated items get `published_date` =
  their `source_digest_date`; the 7 seed items get `published_date` =
  **`2026-06-19`** (launch day). All current content lands in the launch week;
  future cards form new weeks.
- **Pipeline:** `publish_signal_drafts.py::promote_card` stamps
  `published_date = args.date` automatically at promotion time. `source_digest_date`
  is preserved as provenance. `published_date` is stamped server-side, so it is
  NOT a required draft field.
- **Week derivation** is computed client-side (ISO week, **Monday start**) — no
  stored week field, no library. A pure helper returns the Monday of a date's
  week; label format is **"Week of Jun 15, 2026."**

### 2. Home (`index.html` / `app.js`) — trim to a "best of" front door

- Render the **top 9** cards by `signal_score` descending (3×3 grid).
- **Remove** the filter chips, sort toggle, and live search from home (they move
  to the archive). Home becomes a clean showcase.
- Keep the hero and "This week at a glance." Retarget the category wayfinding
  links from `index.html?filter=…` to **`archive.html?filter=…`**.
- Add a prominent **"Browse the full archive →"** CTA below the grid linking to
  `archive.html`.
- Fix the stale hardcoded "18 results" label (reflect the top-N count, or drop
  the count in favor of a "Top signals" heading).

### 3. `weekly.html` / `weekly.js` — narrow to the current week

Filter items to the **most-recent week only** (the week of the max
`published_date`), then group by verdict exactly as today. Add a **"Full archive
→"** link. This stops the weekly brief from competing with the archive as
history grows. Empty verdict groups are omitted (current behavior).

### 4. `archive.html` / `archive.js` — the new workhorse

- Standard shared page shell (head/header/footer/newsletter band, skip link,
  `<main id="main" tabindex="-1">`, `theme.js`, CSP meta, SEO/social cards) so it
  passes the existing shared-page contract.
- **Lightweight controls:** a search box + category filter chips. **No sort** —
  date is the organizing spine.
- **Layout:** all cards ordered newest-week-first, grouped into **"Week of …"
  sections**; within a week, ordered by `signal_score` descending. Filter and
  search apply across every week; weeks with no matching cards are hidden; an
  empty-state note shows when nothing matches.
- **Deep-link contract:** `?filter=<category>` and `?q=<text>` mirror today's
  home behavior so wayfinding links and nav work. Cards link to
  `signal.html?i=N` using the original unfiltered digest index.
- `<noscript>` fallback consistent with the other pages.

### 5. Shared card component (small refactor)

Extract the card-building DOM function (currently inline in `app.js` `card()`)
plus date helpers into one shared **`signals-shared.js`**, exposing
`buildCard(item, index)`, `weekOf(date)`, and `formatDate(date)`. `app.js` and
`archive.js` both consume it, keeping render-safety rules (DOM API only,
`setProperty('--w', …)` for bar widths, no `innerHTML`) in one place. Pages load
`signals-shared.js` before their view script.

### 6. Validation, navigation, SEO

- **Nav:** add an "Archive" link to the shared header and footer on every page.
- **`scripts/check_site.py`:**
  - Add `archive.html` to `PAGES`; require `archive.html`, `archive.js`,
    `signals-shared.js` in `REQUIRED_FILES`.
  - Assert archive hooks (`data-archive` mount, `data-filters`, `data-search`)
    and that nav/footer include `archive.html`.
  - Digest contract: every item must have a valid `published_date`
    (`YYYY-MM-DD`).
  - Render-safety checks extended to `archive.js` (no `innerHTML`/
    `insertAdjacentHTML`, uses `textContent`, `setProperty('--w'`).
  - Update home contract (top-N cap + archive CTA, controls removed) and weekly
    contract (current-week + "Full archive" link).
- **`sitemap.xml`:** add `archive.html`.

### 7. Definition of done

- `python3 scripts/check_site.py` prints the OK line.
- Manual verification (serve via `python3 -m http.server 8080`):
  - Home shows the top 9 cards plus the archive CTA; no filter/sort/search.
  - Archive groups cards by week (newest first); filter + search + `?filter=`/`?q=`
    deep links work; cards open the correct `signal.html?i=N`.
  - Weekly shows only the current week, grouped by verdict, with the archive link.
  - All verified in **light and dark** mode.

## Open knobs (defaults approved)

- Home count = **9**; week start = **Monday**; search/filter **removed** from home.
