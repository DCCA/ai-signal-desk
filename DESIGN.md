---
version: beta
name: AI Signal Desk
description: "Daylight Desk: a light/dark editorial-premium system for a weekly AI field brief. Signal/field-brief DNA, classified and scored, with a calm operations-desk feel."
themes: [light, dark]
fonts:
  display: "Space Grotesk (400/500/600/700), fallback system-ui, -apple-system, sans-serif"
  mono: "IBM Plex Mono (400/500/600) for labels, metadata, category tags, scores, kickers"
  google: "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap"
accent:
  default: "#0a7ea4"   # teal; brand-tweakable (also blue #2a6fdb / green #1a8a5a)
  fg: "#ffffff"
tokens_light:
  bg: "#f7f5f0"
  surface: "#ffffff"
  ink: "#16181d"
  muted: "#5b6470"
  faint: "#8a9099"
  line: "#e6e2d9"
  line2: "#f0ece3"
  track: "#ece8df"
  c-concept: "#0a7ea4"
  c-product: "#6d4bd6"
  c-repo: "#1a8a5a"
  c-workflow: "#a76a00"
  s-learn: "#0a7ea4"
  s-try: "#1a8a5a"
  s-watch: "#a76a00"
  s-ignore: "#c5482f"
  signal: "#1a8a5a"
  hype: "#c5482f"
  panel-bg: "#16181d"
tokens_dark:
  bg: "#0c0e12"
  surface: "#14171d"
  ink: "#f2f1ec"
  muted: "#9aa0ab"
  faint: "#6f7682"
  c-concept: "#58e6ff"
  c-product: "#b3a4ff"
  c-repo: "#5fd39a"
  c-workflow: "#f6c85f"
  s-learn: "#58e6ff"
  s-try: "#5fd39a"
  s-watch: "#f6c85f"
  s-ignore: "#ff7a66"
  signal: "#5fd39a"
  hype: "#ff7a66"
  panel-bg: "#1a1e25"
radius:
  control: 8px      # buttons, chips active, inputs-in-header
  pill: 999px       # category/verdict/eyebrow/filter chips
  card: 14px        # signal cards, meta, try-this (12px for compact tiles)
  panel: 16px       # aside, method cards
  band: 18px        # newsletter band
spacing:
  page-max: 1200px  # article 780, weekly 920, about hero 820 / sections 1080
  page-pad: 28px
---

## Overview

The "Daylight Desk" redesign moves AI Signal Desk from a dark intelligence-terminal
look to a light editorial-premium direction (benchmarked against Linear / Vercel /
Resend, Stripe / Anthropic, Perplexity / Exa) while keeping the brand's signal /
field-brief DNA. It ships **light and dark themes of the same layout**.

The product still does one thing: filter the AI firehose into a small set of
**concepts, products, repos, and workflows** worth attention, each item **classified**,
**scored** for signal versus hype (0-100), and given a verdict and next action
(**learn / try / watch / ignore**).

## Theming

All theme-dependent values are CSS custom properties on `:root` (light, default) and
`[data-theme="dark"]` in `styles.css`, swapped wholesale. The accent
(`--accent`, default teal `#0a7ea4`) is theme-independent. Theme is chosen by
`theme.js` from `localStorage`, falling back to `prefers-color-scheme`, and is
applied before first paint.

## Typography

**Space Grotesk** for display and UI; **IBM Plex Mono** for labels, metadata,
category tags, scores, and kickers. Headlines are large, tightly tracked, and fluid
via `clamp()`. The Space Grotesk / IBM Plex Mono contrast (editorial clarity plus
operational metadata) is core to the brand.

## Layout

- Sticky blurred header (brand SD tile + nav + theme toggle + Subscribe).
- Home: hero (eyebrow, H1 "AI signal, not AI noise.", search) + "this week at a
  glance" aside, wayfinding tiles, then the classified signal-card grid with filter
  chips and a segmented sort control.
- Article (`signal.html?i=N`): category/verdict, lead, meta card (signal/hype bars +
  confidence), prose (What it is / Why it matters / Try this), source, related.
- Weekly: items grouped by verdict (learn / try / watch / ignore).
- About: method (Classify / Score / Action) + principles.
- Shared newsletter band + footer.

## Components

- **Signal card:** surface panel with category tag + verdict pill, title, summary,
  signal/hype bars, a "Try this" line, and a "Read full signal" cue. Whole card is a
  link to the article.
- **Signal/hype bars:** mono label + track + colored fill (`--signal` green /
  `--hype` coral) + numeric score. Fill width is data-driven via the `--w` custom
  property set from JS (so no inline styles are needed under the strict CSP).
- **Verdict pill / category tag:** mono, color-coded by `--s-{status}` / `--c-{category}`.
- **This week at a glance:** elevated aside summarizing the issue.
- **Newsletter band:** inverted panel CTA framed as receiving the field brief.

## Implementation rules

- No inline `style` attributes and no inline `<script>`: everything lives in
  `styles.css` / external JS, so the strict Content-Security-Policy (`script-src
  'self'`, `style-src 'self'`) holds. Dynamic styling uses the CSSOM.
- Multi-page (no build step): each route is a real HTML file sharing `styles.css`,
  `theme.js`, and the digest (`content/digest.json`).
- Card index numbers are the item's 1-based position in the full unfiltered list and
  stay stable across filter/sort.

## Do's and Don'ts

### Do
- Use "signal," "field brief," "classified," and "hype filter" language consistently.
- Classify every item by category and verdict, and give it a next action.
- Use mono labels for metadata; keep the palette restrained.
- Respect `prefers-reduced-motion` (the live dots pulse otherwise).

### Don't
- Do not use generic AI gradients, robot/brain/bolt cliches, or fake metrics.
- Do not publish tool lists without a next action.
- Do not introduce inline styles or scripts (it would force weakening the CSP).
