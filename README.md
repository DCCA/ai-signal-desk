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
- `brand.html` — brand-system preview page
- `logo-exploration.html` — comparison board for six SVG logo directions
- `styles.css` — dark editorial Signal Desk visual system
- `app.js` — loads and filters digest cards
- `content/digest.json` — seeded MVP content
- `docs/product-brief.md` — product direction and editorial rules
- `docs/brand-foundation.md` — positioning, voice, taxonomy, tagline, and copy rules
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

## Next steps

1. Convert existing AI Daily Digest entries into three long-form sample posts.
2. Add a `/weekly` archive page.
3. Connect a newsletter provider or simple waitlist form.
4. Add a Hermes workflow that turns daily digest notes into draft cards for review.
