# AI Signal Desk Editorial Workflow

## Goal

Use Hermes to turn the AI Daily Digest and newsletters at `dcca.hermes@gmail.com` into draft signal cards while keeping publication human review gated.

```text
AI Daily Digest + newsletters at dcca.hermes@gmail.com
→ Hermes filters high-signal items
→ Hermes drafts signal cards in content/drafts/
→ human review
→ publish to content/digest.json, weekly.html, or posts/
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

## Human review gate

Do not publish automatically. A card can move from draft to published only after human review checks:

1. The source link is real and relevant.
2. The summary does not overclaim.
3. The next action is practical.
4. The confidence level matches the evidence.
5. The item fits AI Signal Desk positioning: practical AI signal, not generic AI news.

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
