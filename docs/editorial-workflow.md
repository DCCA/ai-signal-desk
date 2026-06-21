# AI Signal Desk Editorial Workflow

## Goal

Use Hermes to turn the AI Daily Digest and newsletters at `signals@aisignaldesk.example` into public signal cards while keeping the automation auditable and clearly labeled.

```text
AI Daily Digest + newsletters at signals@aisignaldesk.example
→ Hermes filters high-signal items
→ Hermes drafts signal cards in content/drafts/
→ automated reviewer/editor validation
→ publish to content/digest.json
→ commit + push to production
→ optional later human review for deeper posts or weekly issues
```

## Intake

Sources allowed for drafts:

- AI Daily Digest notes already saved by Hermes
- newsletters in the dedicated Hermes email inbox
- links manually sent by the user
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

## Automated publication gate

Daily signal cards may be published automatically when the Hermes feeder and automated reviewer/editor both pass:

1. The source link is public and relevant.
2. The summary does not overclaim.
3. The next action is practical.
4. The confidence level matches the evidence.
5. The item fits AI Signal Desk positioning: practical AI signal, not generic AI news.
6. No private DCCA, Telegram, Obsidian, local-path, cron, or Hermes-internal context appears in the public card.
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
