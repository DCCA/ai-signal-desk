# Signal Card Schema

Signal cards are the atomic content unit for AI Signal Desk.

## JSON fields

```json
{
  "title": "Agent loops",
  "category": "concept",
  "summary": "One sentence plain-English explanation.",
  "why_it_matters": "Why a practical reader should care.",
  "try_this": "A concrete next action.",
  "status": "learn",
  "confidence": "high",
  "source_label": "Anthropic — Building effective agents",
  "source_url": "https://www.anthropic.com/research/building-effective-agents",
  "post_url": "posts/agent-loops.html",
  "human_reviewed": true,
  "published": true,
  "signal_score": 92,
  "hype_score": 18
}
```

## Required published fields

Published cards require:

- `title`
- `category`
- `summary`
- `why_it_matters`
- `try_this`
- `status`
- `confidence`
- `source_label`
- `source_url`

## Allowed values

### category

- `concept`
- `product`
- `repo`
- `workflow`

### status

- `learn`
- `try`
- `watch`
- `ignore`

### confidence

- `high` — strong source and clear practical implication
- `medium` — useful but early, incomplete, or partially inferred
- `low` — exploratory, reader-submitted, or needs more validation

## Draft-only fields

Draft cards in `content/drafts/` should include:

- `human_reviewed: false`
- `published: false`
- optional `review_notes`

## Publication rule

A card should not appear in `content/digest.json`, `weekly.html`, or `posts/` until it is human-reviewed and has source attribution.
