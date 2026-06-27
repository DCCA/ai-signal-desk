# AI Signal Desk Launch Config

## Free beta stack

AI Signal Desk is staying free while testing demand.

Recommended setup:

- Hosting: Cloudflare Pages free tier if the repo stays private, or GitHub Pages if the repo becomes public.
- Signup: link-out to a free Kit (ConvertKit) landing page (double opt-in on). The repo holds only the public Kit URL — no form, no backend, no secret, strict CSP unchanged.
- Analytics: Cloudflare Web Analytics — cookieless beacon on every page (manual snippet, GitHub Pages stays as-is). Adds one bounded, test-enforced CSP exception (`static.cloudflareinsights.com` in `script-src`, `cloudflareinsights.com` in `connect-src`); the public beacon token is the only repo change. See `docs/superpowers/specs/2026-06-27-analytics-cloudflare-design.md`.
- Email sending: Kit broadcasts from the dashboard (free plan). Automate sends from the editorial pipeline via the Kit API/MCP (paid plan) only once pull is proven.

## Signup URL

The newsletter band on every page links out to a Kit-hosted landing page:

```text
https://<handle>.kit.com/<slug>
```

Create the landing page in the Kit dashboard (Grow → Landing Pages & Forms),
reuse the band copy, turn on opt-in confirmation, publish, and wire the public
URL into the shared band. `scripts/check_site.py::assert_newsletter_contract`
enforces that the band links to a real Kit host — the
`https://KIT-LANDING-URL-PENDING` placeholder fails the build until swapped.

See `docs/superpowers/specs/2026-06-27-newsletter-kit-linkout-design.md` for the
full rationale (the link-out trilemma, why Kit, the security model).

## Deployment notes

### Cloudflare Pages

Use this when keeping the repository private during beta.

Recommended settings:

```text
Framework preset: None
Build command: <empty>
Build output directory: /
```

### GitHub Pages

Use this if the repository can be public or if Pages support is available for the repo plan.

Recommended settings:

```text
Source: Deploy from branch
Branch: main
Folder: /root
```

## Beta validation rule

Do not migrate to paid newsletter tooling until there is evidence of pull:

- 25 early subscribers/testers
- 5 qualitative replies
- 2 manually published issues
- 3 people say they would keep reading weekly
- 1 person shares or forwards it without being asked
