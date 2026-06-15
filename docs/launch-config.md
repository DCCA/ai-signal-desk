# AI Signal Desk Launch Config

## Free beta stack

AI Signal Desk is staying free while testing demand.

Recommended setup:

- Hosting: Cloudflare Pages free tier if the repo stays private, or GitHub Pages if the repo becomes public.
- Waitlist capture: email link now; Tally free when the beta needs structured intake.
- Analytics: Cloudflare Web Analytics.
- Email sending: manual beta email until the product proves enough pull for a newsletter provider.

## Waitlist URL

Current free beta capture path:

```text
mailto:signals@aisignaldesk.example?subject=Join%20AI%20Signal%20Desk%20beta
```

This keeps testing free and does not require a new external form account.

Optional upgrade after initial pull: create a free Tally form and replace the `mailto:` link in:

```text
index.html
```

Suggested Tally questions:

1. Email address
2. Role / context
3. Which AI topics do you want filtered?
4. Preferred cadence
5. What do you usually ignore or find too noisy?

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
