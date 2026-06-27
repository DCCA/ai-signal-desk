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

- [ ] Kit landing page is published with double opt-in (opt-in confirmation) on
- [ ] The real Kit URL is wired into the newsletter band (no `KIT-LANDING-URL-PENDING` placeholder; `check_site.py` is green)
- [ ] "Subscribe free" button opens the Kit landing page in a new tab
- [ ] A test signup receives the double opt-in email and, once confirmed, appears in Kit
- [ ] Signup path works from the homepage hero (in-page scroll to the band) on every page

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
