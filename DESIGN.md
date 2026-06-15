---
version: alpha
name: AI Signal Desk
description: "Calm intelligence desk for the AI firehose: dark editorial surfaces, radar motifs, and operational signal labels."
colors:
  primary: "#080A0F"
  secondary: "#111722"
  tertiary: "#58E6FF"
  neutral: "#F4F1E8"
  muted: "#9AA4B8"
  line: "#2A3342"
  amber: "#F6C85F"
  coral: "#FF6B6B"
  violet: "#9B87FF"
  green: "#78F0B2"
typography:
  h1:
    fontFamily: Inter
    fontSize: 6rem
    fontWeight: 800
    lineHeight: 0.86
    letterSpacing: "-0.085em"
  h2:
    fontFamily: Inter
    fontSize: 3.5rem
    fontWeight: 800
    lineHeight: 0.96
    letterSpacing: "-0.065em"
  body-md:
    fontFamily: Inter
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.65
  body-lg:
    fontFamily: Inter
    fontSize: 1.25rem
    fontWeight: 400
    lineHeight: 1.7
  mono-label:
    fontFamily: IBM Plex Mono
    fontSize: 0.75rem
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.11em"
rounded:
  sm: 8px
  md: 16px
  lg: 24px
  pill: 999px
spacing:
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 72px
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.primary}"
    rounded: "{rounded.pill}"
    padding: 13px 16px
  button-secondary:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.pill}"
    padding: 12px 16px
  signal-card:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.lg}"
    padding: 24px
  label-concept:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.tertiary}"
    rounded: "{rounded.pill}"
    padding: 5px 8px
  label-product:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.violet}"
    rounded: "{rounded.pill}"
    padding: 5px 8px
  label-repo:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.green}"
    rounded: "{rounded.pill}"
    padding: 5px 8px
  label-workflow:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.amber}"
    rounded: "{rounded.pill}"
    padding: 5px 8px
  text-muted:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.muted}"
    rounded: "{rounded.sm}"
    padding: 0px
  divider-line:
    backgroundColor: "{colors.line}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.sm}"
    padding: 0px
  label-alert:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.coral}"
    rounded: "{rounded.pill}"
    padding: 5px 8px
---

## Overview

AI Signal Desk should feel like a calm intelligence terminal for practical AI — more editorial briefing room than cyberpunk dashboard. The brand classifies the AI firehose into useful signals with clear next actions.

The visual system is dark, precise, and restrained. It uses radar/scanner motifs, classified report cards, mono metadata, and a small operational palette to make the product memorable without becoming noisy.

## Colors

- **Primary / Deep Ink (#080A0F):** Main background. It creates the intelligence-desk atmosphere.
- **Secondary / Graphite Panel (#111722):** Card and console surfaces.
- **Tertiary / Signal Cyan (#58E6FF):** Primary action color, radar glow, concept labels, active filters.
- **Neutral / Pearl (#F4F1E8):** Main text. Warm enough to avoid sterile white.
- **Muted / Steel (#9AA4B8):** Supporting body copy and metadata.
- **Amber (#F6C85F):** Watch/action emphasis and hype-filter accents.
- **Coral (#FF6B6B):** Alert/high-hype emphasis, used sparingly.
- **Violet (#9B87FF):** Product category.
- **Green (#78F0B2):** Repo/open-source category.

## Typography

Use **Inter** for editorial headlines and readable body text. Headlines are large, tightly tracked, and confident. Use **IBM Plex Mono** for operational labels, category tags, scores, and terminal fragments.

The contrast between Inter and IBM Plex Mono is core to the brand: editorial clarity plus intelligence-desk metadata.

## Layout

Prefer asymmetric editorial layouts over repeated generic card grids. Pages should feel like briefings:

- hero statement + console/radar artifact;
- content classified by type and action;
- metadata visible but not overwhelming;
- generous section spacing with dense cards only where useful.

## Elevation & Depth

Cards use dark layered surfaces with subtle borders and atmospheric shadows. Avoid bright glassmorphism. Glow is reserved for radar/signal moments and should be low-opacity.

## Shapes

Use rounded-but-not-cute geometry:

- 8px for compact controls;
- 16px for smaller panels;
- 24px for signal cards and hero consoles;
- full pill for filters, category labels, and CTAs.

## Components

- **Signal card:** dark panel with category/action header, title, summary, signal/hype scores, why-it-matters, and try-this.
- **Signal console:** terminal-like preview with command/status lines and meters.
- **Radar panel:** circular scanning motif showing concepts, products, repos, and workflows.
- **Hype filter:** explicit signal-versus-hype comparison.
- **Field brief CTA:** newsletter/subscribe action framed as receiving a briefing.

## Do's and Don'ts

### Do

- Use “signal,” “field brief,” “classified,” “watchlist,” and “hype filter” language consistently.
- Classify every item by category and action.
- Use mono labels for metadata.
- Keep the palette restrained.
- Make the product feel useful before it feels decorative.

### Don't

- Do not use generic AI gradients as the main identity.
- Do not add robot/brain/bolt clichés.
- Do not make the page look like a crypto trading dashboard.
- Do not use fake metrics unless they explain editorial judgment.
- Do not publish generic tool lists without a next action.
