# AI Signal Desk Launch Checklist

Use this before sharing the beta URL.

## Deterministic checks

- [ ] `python3 scripts/check_site.py` passes
- [ ] No broken internal links
- [ ] Browser console has no JavaScript errors

## Site pages

- [ ] Homepage loads
- [ ] About page explains the editorial standard
- [ ] Privacy page explains email capture and unsubscribe expectations
- [ ] Contact page includes the feedback/signals route
- [ ] Issue 001 exists at `weekly.html`
- [ ] At least 3 sample posts exist

## Signup

- [ ] Email waitlist link opens a prefilled message to `signals@aisignaldesk.example`
- [ ] Test message is received
- [ ] Optional Tally form is created only if structured intake is needed
- [ ] Signup path works from homepage hero/briefing section

## Mobile

- [ ] Mobile width around 375px is readable
- [ ] Cards stack correctly
- [ ] Header does not block content
- [ ] CTA is visible or reachable

## Content quality

- [ ] Each published card has `source_url`
- [ ] Each published card has `source_label`
- [ ] Each published card has `confidence`
- [ ] Sample posts include What changed, Why it matters, Try this, and Sources
- [ ] Issue 001 includes five useful updates, three things to try, one concept, and one thing to ignore

## Free beta guardrails

- [ ] No paid newsletter provider required
- [ ] No backend required
- [ ] No automated publish without human review
- [ ] Feedback is tracked manually until there is real pull
