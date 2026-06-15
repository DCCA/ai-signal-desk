# AI Signal Desk Launch Readiness Plan

## Goal

Move AI Signal Desk from a polished static MVP to a **free, testable launch candidate** that can validate whether people want a practical AI signal brief before paying for newsletter tooling or building a backend.

## Current state

Verified on 2026-06-15:

- Repo: `DCCA/ai-signal-desk`
- Current branch: `main`
- Static MVP exists: homepage, brand page, logo exploration, seeded digest cards
- Deterministic check passes: `python3 scripts/check_site.py`
- Repo is private
- Free beta capture path uses a prefilled email link to `dcca.hermes@gmail.com`
- Launch trust pages exist: `about.html`, `privacy.html`, `contact.html`
- Issue 001 exists at `weekly.html`
- Three launch sample posts exist under `posts/`
- Published signal cards include source links and confidence labels
- Hermes editorial workflow docs exist for draft-to-human-review publishing
- No public deployment URL yet

## Launch thesis

AI Signal Desk should launch as a **curated practical AI brief**, not as a generic AI news site.

Promise:

> Practical AI signal reports: what changed, why it matters, what to try, and what to ignore.

The free testing version should prove:

1. The positioning is clear in 5 seconds.
2. A reader can subscribe or join the beta immediately.
3. The content is differentiated enough that people trust the filter.
4. A simple Hermes-assisted editorial workflow can produce useful issues consistently.

## Free testing stack

| Need | Free choice | Recommendation |
|---|---|---|
| Hosting | GitHub Pages or Cloudflare Pages free tier | Cloudflare Pages if keeping repo private; GitHub Pages if repo can be public |
| Signup capture | Tally free, Google Forms, or Formspree free | Tally free for best UX with minimal setup |
| Subscriber storage | Tally dashboard / CSV export / Google Sheets | Enough for first 25–100 testers |
| Analytics | Cloudflare Web Analytics | Free and privacy-friendly |
| Content workflow | Static JSON + Markdown/HTML posts + Hermes drafts | Avoid CMS complexity |
| Email sending | Manual beta emails / BCC / personal outreach | Avoid paid newsletter tools until pull is proven |

## Beta success criteria

Do not pay for newsletter infrastructure until at least some of these are true:

- 25 early subscribers/testers
- 5 qualitative replies about what readers want more or less of
- 2 manually published weekly issues
- At least 3 people say they would keep reading weekly
- At least 1 person forwards or shares it without being asked

## Launch blockers

These must be solved before sharing publicly:

1. Real signup/waitlist capture
2. Public URL
3. At least 3 sample posts or deep signal reports
4. One concrete Issue 001 weekly page
5. Basic `about`, `privacy`, and `contact` pages
6. SEO/OpenGraph metadata
7. Mobile check

## Not launch blockers

Defer these until after testing:

- paid newsletter provider
- full CMS
- backend
- user accounts
- search
- paid subscriptions
- automated publishing
- complex dashboard
- perfect analytics event taxonomy

## Recommended implementation phases

### Phase 1 — Free beta launch foundation

Goal: make the current site credible enough to share with testers.

Tasks:

1. Add `about.html` explaining the editorial standard.
2. Add `privacy.html` explaining email capture and unsubscribe expectations.
3. Add `contact.html` with the Hermes/contact route.
4. Replace demo signup with a configurable free waitlist link or embed.
5. Add SEO/OpenGraph/Twitter metadata.
6. Add `robots.txt` and `sitemap.xml`.
7. Update `scripts/check_site.py` so launch basics are enforced.
8. Update `README.md` with free beta setup instructions.

Acceptance criteria:

- `python3 scripts/check_site.py` passes.
- Homepage no longer contains demo-only signup copy.
- Footer/nav links to about/privacy/contact.
- Site is ready to deploy as static files.

### Phase 2 — Launch sample content

Goal: prove the editorial product, not just the brand.

Tasks:

1. Add 3 sample signal posts:
   - Agent loops
   - Context engineering
   - Lightweight eval harnesses
2. Add `weekly.html` with Issue 001.
3. Add source links and confidence labels to digest items.
4. Update `app.js` and `content/digest.json` if new fields are needed.
5. Add checks for post links and weekly issue structure.

Acceptance criteria:

- Homepage cards link to real examples.
- Issue 001 shows the intended weekly format.
- Content feels public-facing, not placeholder/internal.

### Phase 3 — Free deployment and testing

Goal: get a public URL and start learning.

Tasks:

1. Deploy with Cloudflare Pages or GitHub Pages.
2. Connect the free Tally/Google/Formspree waitlist.
3. Add Cloudflare Web Analytics if using Cloudflare.
4. Share with 10–25 trusted testers.
5. Track signups, replies, and content feedback manually.

Acceptance criteria:

- Public URL loads.
- Signup path works.
- Test submission is received.
- Mobile layout is acceptable.

### Phase 4 — Hermes editorial workflow

Goal: use Hermes to reduce manual curation work while keeping human review.

Workflow:

```text
AI Daily Digest + newsletters at dcca.hermes@gmail.com
→ Hermes filters high-signal items
→ Hermes drafts signal cards
→ human review
→ publish to content/digest.json, weekly issue, or post
```

Tasks:

1. Create `docs/editorial-workflow.md`.
2. Create `docs/signal-card-schema.md`.
3. Define draft vs published content rules.
4. Add `content/drafts/` for review-only cards.
5. Add a validation rule that published cards need source links and confidence.

Acceptance criteria:

- Hermes can draft content without publishing automatically.
- Published content is always human-reviewed.
- Newsletter/email inputs can become candidate signal cards.

## First PR recommendation

Branch:

```text
feat/free-beta-launch-foundation
```

PR title:

```text
feat: add free beta launch foundation
```

Scope:

- about/privacy/contact pages
- free waitlist configuration
- launch metadata
- robots/sitemap
- README launch instructions
- expanded deterministic checks

Keep sample posts and weekly issue in a second PR.

## Second PR recommendation

Branch:

```text
feat/launch-sample-content
```

PR title:

```text
feat: add issue 001 and launch sample posts
```

Scope:

- `weekly.html`
- 3 sample posts
- source links/confidence labels
- digest card improvements
- validation checks

## Manual validation checklist

Before sharing the beta URL:

- [ ] `python3 scripts/check_site.py` passes
- [ ] Homepage loads locally
- [ ] Signup path works
- [ ] About page explains the editorial standard
- [ ] Privacy page explains email capture
- [ ] Contact page exists
- [ ] All nav/footer links work
- [ ] Mobile width around 375px is readable
- [ ] OpenGraph preview works after deploy
- [ ] At least 3 sample posts exist
- [ ] Issue 001 exists

## Open decisions

- Use Tally, Google Forms, or Formspree for the first waitlist?
- Use Cloudflare Pages or GitHub Pages for the first deployment?
- Keep repo private during beta or make it public?
- Should the first beta audience be personal friends/builders, LinkedIn/X, or side-project peers?
