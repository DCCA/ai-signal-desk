# AI Signal Desk Editorial Workflow

## Goal

Use the automated feeder to turn the AI Daily Digest and newsletters at `signals@aisignaldesk.example` into public signal cards while keeping the automation auditable and clearly labeled.

```text
AI Daily Digest + newsletters at signals@aisignaldesk.example + user-shared links from Discord/Telegram
→ The feeder or Hermes extracts public-source signal candidates
→ The feeder filters high-signal items
→ The feeder drafts signal cards in content/drafts/
→ automated reviewer/editor validation
→ publish to content/digest.json
→ commit + push to production
→ optional later human review for deeper posts or weekly issues
```

## Intake

Sources allowed for drafts:

- AI Daily Digest notes already saved by the feeder
- newsletters in the dedicated editorial email inbox
- links manually sent by the user from Discord or Telegram
- public source pages for products, repos, papers, or docs

## Drafting rules

A draft is not published content. Drafts should include:

- title
- category: concept, product, repo, or workflow
- status: learn, try, watch, or ignore
- summary
- why_it_matters
- try_this
- source_label
- source_url
- confidence: high, medium, or low
- human_reviewed: false
- published: false

Drafts live under:

```text
content/drafts/
```

## Shared-link intake from Discord or Telegram

When the user shares a link in Discord or Telegram and asks to use it for AI Signal Desk:

1. Extract the public source and synthesize only public-facing signal candidates.
2. Drop personal learning notes, Obsidian paths, local workflow details, private project references, and unsupported claims.
3. Translate the four required public fields into pt-BR before draft creation.
4. Create the draft with the deterministic intake script:

```bash
python3 scripts/create_link_signal_draft.py \
  --source-platform discord \
  --date YYYY-MM-DD \
  --input payload.json

python3 scripts/create_link_signal_draft.py \
  --source-platform telegram \
  --date YYYY-MM-DD \
  --input payload.json
```

The payload must contain the same public fields required for a draft card:

```json
{
  "title": "Implementation is cheap; taste is the bottleneck",
  "category": "concept",
  "status": "learn",
  "summary": "...",
  "why_it_matters": "...",
  "try_this": "...",
  "title_pt": "...",
  "summary_pt": "...",
  "why_it_matters_pt": "...",
  "try_this_pt": "...",
  "source_label": "Source name",
  "source_url": "https://...",
  "confidence": "medium"
}
```

`create_link_signal_draft.py` validates the card against the same schema/private-pattern/source-link checks used by the publisher, records whether the link came from Discord or Telegram in the draft filename, and refuses duplicates already in `content/digest.json` or `content/drafts/` unless `--force` is used.

## Automated publication gate

Daily signal cards may be published automatically when the automated feeder and reviewer/editor both pass:

1. The source link is public and relevant.
2. The summary does not overclaim.
3. The next action is practical.
4. The confidence level matches the evidence.
5. The item fits AI Signal Desk positioning: practical AI signal, not generic AI news.
6. No private or internal context (personal handles, private tools, local file paths, automation, internal system names, or project codenames) appears in the public card.
7. The deterministic site checks pass before commit/push.

Automatically published cards should use:

```json
{
  "human_reviewed": false,
  "published": true,
  "automated_reviewed": true
}
```

Human review remains required before creating deeper `posts/*.html` analysis pages or promoting cards into manually curated weekly issues.

## Publish targets

Published items may be added to:

- `content/digest.json` for homepage cards
- `weekly.html` for the current issue
- `posts/*.html` for deeper signal reports

## Feedback loop

After sharing beta issues, collect:

- signups
- replies
- forwards/shares
- topics readers want more of
- topics readers found noisy

Use that feedback to adjust future signal selection before adding paid newsletter tooling.
