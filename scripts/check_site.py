#!/usr/bin/env python3
"""Deterministic checks for the AI Signal Desk static site ("Daylight Desk").

Validates the multi-page structure, the shared design system, the digest data
contract, and the security invariants that keep the strict CSP intact
(no inline styles, no inline scripts). Run from anywhere:

    python3 scripts/check_site.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    "index.html", "archive.html", "signal.html", "weekly.html",
    "about.html", "privacy.html", "contact.html",
]

# Internal preview pages (not in the primary nav / sitemap) held to the same
# shared-shell and security standards as the main pages.
PREVIEW_PAGES = ["brand.html", "logo-exploration.html"]
ALL_PAGES = PAGES + PREVIEW_PAGES

REQUIRED_FILES = PAGES + PREVIEW_PAGES + [
    "styles.css", "preview.css", "theme.js",
    "signals-shared.js", "app.js", "archive.js", "signal.js", "weekly.js",
    "content/digest.json",
    "favicon.svg", "assets/brand-mark.svg", "assets/og-image.png",
    "robots.txt", "sitemap.xml", "CNAME", ".nojekyll",
    "DESIGN.md", "README.md", "SECURITY.md",
    ".github/workflows/deploy-pages.yml", ".github/dependabot.yml",
    "docs/product-brief.md", "docs/brand-foundation.md",
    "scripts/check_site.py",
]

CATEGORIES = {"concept", "product", "repo", "workflow"}
STATUSES = {"learn", "try", "watch", "ignore"}
CONFIDENCES = {"low", "medium", "high"}

# Strings that must no longer appear on any page: the old posts/ design and
# the reserved, non-deliverable .example contact domain.
REMOVED_REFS = ["posts/", "aisignaldesk.example"]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def assert_required_files() -> None:
    missing = [p for p in REQUIRED_FILES if not (ROOT / p).exists()]
    assert not missing, f"Missing required files: {missing}"


def assert_shared_page_contract() -> None:
    """Every page shares the same head/header/footer + a11y landmarks."""
    for page in ALL_PAGES:
        html = read(page)
        assert 'lang="en"' in html, f"{page}: missing lang"
        assert 'class="skip-link" href="#main"' in html, f"{page}: missing skip link"
        assert re.search(r'<main[^>]*id="main"[^>]*tabindex="-1"', html), f"{page}: <main id=main tabindex=-1> required"
        assert 'name="viewport"' in html, f"{page}: missing viewport"
        assert 'name="referrer"' in html, f"{page}: missing referrer policy"
        assert 'fonts.googleapis.com/css2' in html, f"{page}: missing Google Fonts link"
        assert 'href="styles.css"' in html, f"{page}: missing styles.css"
        assert '<script src="theme.js"></script>' in html, f"{page}: theme.js must be loaded"
        assert 'class="site-header"' in html, f"{page}: missing shared header"
        assert 'class="site-footer"' in html, f"{page}: missing shared footer"
        assert 'id="newsletter"' in html, f"{page}: missing newsletter band"
        # Shared nav + footer links.
        for target in ["archive.html", "weekly.html", "about.html"]:
            assert f'href="{target}"' in html, f"{page}: nav/footer missing {target}"
        for target in ["about.html", "privacy.html", "contact.html"]:
            assert f'href="{target}"' in html, f"{page}: footer missing {target}"
        # Theme toggle present and wired.
        assert "data-theme-toggle" in html, f"{page}: missing theme toggle button"
    # Every public (sitemap-listed) page carries social/SEO cards. The share
    # image must be a raster (PNG) at the standard 1200x630 — social platforms
    # do not render SVG OG images, so a share would otherwise have no preview.
    for page in PAGES:
        html = read(page)
        assert 'rel="canonical"' in html, f"{page}: missing canonical"
        assert 'property="og:title"' in html, f"{page}: missing Open Graph tags"
        assert 'name="twitter:card"' in html, f"{page}: missing Twitter card tags"
        assert 'content="summary_large_image"' in html, f"{page}: twitter:card should be summary_large_image"
        assert "assets/og-image.png" in html, f"{page}: og/twitter image must be the raster og-image.png"
        assert "brand-mark.svg" not in html, f"{page}: must not use an SVG as the social share image"


def assert_security_invariants() -> None:
    """The hardening that lets the strict CSP stay strict."""
    for page in ALL_PAGES:
        html = read(page)
        # No inline style attributes (style-src 'self' has no 'unsafe-inline').
        assert 'style="' not in html, f"{page}: inline style attribute breaks the strict CSP"
        assert "<style" not in html, f"{page}: inline <style> block breaks the strict CSP"
        # Every <script> must be external (src=), never an inline block.
        for m in re.finditer(r"<script\b([^>]*)>", html):
            attrs = m.group(1)
            assert "src=" in attrs, f"{page}: inline <script> breaks script-src 'self'"
        # CSP present and strict.
        assert 'http-equiv="Content-Security-Policy"' in html, f"{page}: missing CSP meta"
        assert "script-src 'self'" in html, f"{page}: CSP must pin script-src 'self'"
        assert "style-src 'self'" in html, f"{page}: CSP must pin style-src 'self'"
        assert "object-src 'none'" in html, f"{page}: CSP should set object-src 'none'"
        assert "'unsafe-inline'" not in html, f"{page}: CSP must not allow 'unsafe-inline'"
        assert "'unsafe-eval'" not in html, f"{page}: CSP must not allow 'unsafe-eval'"
    # No external links opening a new tab without noopener.
    for page in ALL_PAGES + ["signal.js"]:
        text = read(page)
        for m in re.finditer(r'target="_blank"', text):
            window = text[max(0, m.start() - 200): m.end() + 200]
            assert "noopener" in window, f"{page}: target=_blank without rel=noopener"


def assert_no_removed_refs() -> None:
    for page in ALL_PAGES:
        html = read(page)
        for ref in REMOVED_REFS:
            assert ref not in html, f"{page}: still references removed asset '{ref}'"


def assert_preview_pages() -> None:
    brand = read("brand.html")
    for marker in ["Brand System", "Visual system", "Component language"]:
        assert marker in brand, f"brand.html missing marker: {marker}"
    logos = read("logo-exploration.html")
    for marker in ["Logo exploration", "Radar monogram", "Signal aperture",
                   "Terminal signal", "Classified stamp", "Signal grid",
                   "Minimal ASD square", "Keep Option F"]:
        assert marker in logos, f"logo-exploration.html missing marker: {marker}"
    # The logo board references the restored SVG assets.
    for svg in ["assets/logo-radar-monogram.svg", "assets/logo-minimal-asd.svg"]:
        assert svg in logos, f"logo-exploration.html missing {svg}"
        assert (ROOT / svg).exists(), f"missing asset {svg}"


def assert_design_system() -> None:
    css = read("styles.css")
    # Token architecture.
    assert ":root" in css, "styles.css missing :root tokens"
    assert '[data-theme="dark"]' in css, "styles.css missing dark theme tokens"
    for token in ["--accent", "--bg", "--ink", "--muted", "--line",
                  "--signal", "--hype", "--c-concept", "--s-ignore",
                  "--panel-bg", "--chip-active-bg", "--seg-track"]:
        assert token in css, f"styles.css missing token {token}"
    # Light + dark accent-driven category colors both defined.
    assert "#0a7ea4" in css, "styles.css missing light teal accent"
    assert "#58e6ff" in css, "styles.css missing dark concept color"
    # Typography.
    assert "Space Grotesk" in css, "styles.css must use Space Grotesk"
    assert "IBM Plex Mono" in css, "styles.css must use IBM Plex Mono"
    assert "font-family: Inter" not in css, "styles.css must not default to Inter"
    # Accessibility.
    assert ":focus-visible" in css, "styles.css must define a visible focus style"
    assert ".skip-link" in css, "styles.css must style a skip link"
    assert "prefers-reduced-motion" in css, "styles.css must respect reduced motion"
    # Core component classes used by the JS renderers exist.
    for cls in [".signal-card", ".bar-fill", ".chip", ".seg-btn",
                ".wk-row", ".meta-card", ".related-card", ".method-card", ".principle-card"]:
        assert cls in css, f"styles.css missing component class {cls}"
    # Dynamic bar fill must be driven by a custom property (set via CSSOM in JS).
    assert "var(--w" in css, "styles.css .bar-fill must use var(--w) for dynamic width"


def assert_home_contract() -> None:
    html = read("index.html")
    for phrase in ["AI signal,", "not AI noise", "Classified signal cards",
                   "This week at a glance"]:
        assert phrase in html, f"index.html missing hero/section phrase: {phrase}"
    # Home is now a lean "best of" front door: the grid + wayfinding remain, but
    # the filter/sort/search controls moved to the archive.
    for hook in ["data-digest-grid", "data-results-count", 'id="digest"']:
        assert hook in html, f"index.html missing hook: {hook}"
    for removed in ["data-filters", "data-sorts", "data-search"]:
        assert removed not in html, f"index.html should no longer carry {removed} (moved to archive)"
    assert 'href="archive.html"' in html, "index.html missing archive CTA/link"
    for cat in CATEGORIES:
        assert f'data-count="{cat}"' in html, f"index.html wayfinding missing count for {cat}"
        assert f'archive.html?filter={cat}' in html, f"index.html wayfinding must link into the archive for {cat}"
    # SEO/social tags.
    for tag in ['rel="canonical"', 'property="og:title"', 'property="og:image"',
                'name="twitter:card"', 'property="og:description"']:
        assert tag in html, f"index.html missing SEO tag: {tag}"
    assert "aisignaldesk.ai" in html, "index.html canonical/OG should use the live domain"
    assert "<noscript>" in html, "index.html should degrade without JS"


def assert_archive_contract() -> None:
    """The archive is the date-grouped, filterable view of the full digest."""
    html = read("archive.html")
    for hook in ["data-archive", "data-filters", "data-search"]:
        assert hook in html, f"archive.html missing hook: {hook}"
    assert '<script src="signals-shared.js"></script>' in html, "archive.html must load signals-shared.js"
    assert '<script src="archive.js"></script>' in html, "archive.html must load archive.js"
    # signals-shared.js must be loaded before archive.js (it provides buildCard).
    assert html.index("signals-shared.js") < html.index("archive.js"), \
        "archive.html must load signals-shared.js before archive.js"
    for tag in ['rel="canonical"', 'property="og:title"', 'name="twitter:card"']:
        assert tag in html, f"archive.html missing SEO tag: {tag}"
    assert "<noscript>" in html, "archive.html should degrade without JS"

    js = read("archive.js")
    # Date is the spine: group by week, link back to articles, honor deep links.
    assert "weekKey" in js, "archive.js must group by weekKey"
    assert "weekLabel" in js, "archive.js must label week sections via weekLabel"
    assert "signal.html?i=" in read("signals-shared.js"), "shared card must link to articles"
    for param in ["filter", "q"]:
        assert f"get('{param}')" in js, f"archive.js must read the ?{param} deep-link param"


def assert_other_views() -> None:
    signal = read("signal.html")
    assert "data-article" in signal, "signal.html missing data-article mount"
    assert '<script src="signal.js"></script>' in signal, "signal.html must load signal.js"

    weekly = read("weekly.html")
    assert "The weekly field brief" in weekly, "weekly.html missing H1"
    assert "data-weekly-groups" in weekly, "weekly.html missing groups mount"
    assert '<script src="weekly.js"></script>' in weekly, "weekly.html must load weekly.js"
    assert '<script src="signals-shared.js"></script>' in weekly, "weekly.html must load signals-shared.js"
    assert 'href="archive.html"' in weekly, "weekly.html must link to the full archive"
    # The weekly brief is scoped to the current week via the shared week helper.
    assert "weekKey" in read("weekly.js"), "weekly.js must scope to the current week via weekKey"

    about = read("about.html")
    for marker in ["What we hold to", "Classify", "Score", "Action",
                   "calm intelligence desk"]:
        assert marker in about, f"about.html missing marker: {marker}"


def assert_trust_pages() -> None:
    privacy = read("privacy.html")
    for marker in ["email address", "unsubscribe", "no selling"]:
        assert marker.lower() in privacy.lower(), f"privacy.html missing marker: {marker}"
    contact = read("contact.html")
    # The contact address must live on the production domain, not the reserved
    # .example TLD (which is non-deliverable).
    assert "aisignaldesk.example" not in contact, "contact.html must not use the reserved .example domain"
    for marker in ["Contact", "signals@aisignaldesk.ai", "signals"]:
        assert marker.lower() in contact.lower(), f"contact.html missing marker: {marker}"


def assert_js_render_safety() -> None:
    for js in ["signals-shared.js", "app.js", "archive.js", "signal.js", "weekly.js"]:
        src = read(js)
        # DOM construction only: no innerHTML/insertAdjacentHTML sink for
        # untrusted-looking fields (matches real assignments, not comments).
        assert not re.search(r"\.innerHTML\s*=", src), f"{js}: must not assign innerHTML (use the DOM API)"
        assert "insertAdjacentHTML" not in src, f"{js}: must not use insertAdjacentHTML"
        assert ("textContent" in src or "createTextNode" in src), f"{js}: must set text via textContent"
    # Bar widths set through the CSSOM, never inline markup. The shared card
    # builder owns the home/archive bars; signal.js renders its own.
    for js in ["signals-shared.js", "signal.js"]:
        assert "setProperty('--w'" in read(js), f"{js}: bar width must use setProperty('--w', ...)"
    # The article's external source link is scheme-sanitized.
    signal = read("signal.js")
    assert "function safeUrl" in signal, "signal.js must define safeUrl"
    assert "i" in read("signal.js"), "signal.js must read the ?i index param"
    # Weekly groups by verdict, in order, linking back to articles.
    weekly = read("weekly.js")
    for key in STATUSES:
        assert key in weekly, f"weekly.js missing status group: {key}"
    assert "signal.html?i=" in weekly, "weekly.js rows must link to articles"


def assert_digest_contract() -> None:
    data = json.loads(read("content/digest.json"))
    items = data.get("items", [])
    assert len(items) >= 18, "digest should ship at least 18 items"
    cats = {it.get("category") for it in items}
    assert CATEGORIES <= cats, f"digest missing categories: {CATEGORIES - cats}"
    for it in items:
        for key in ["title", "category", "summary", "why_it_matters",
                    "try_this", "status", "confidence", "source_label",
                    "signal_score", "hype_score", "published_date"]:
            assert it.get(key) not in (None, ""), f"digest item missing {key}: {it.get('title')}"
        # published_date is the date spine the archive groups by.
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", str(it["published_date"])), \
            f"bad published_date: {it.get('title')} -> {it.get('published_date')}"
        assert it["category"] in CATEGORIES, it
        assert it["status"] in STATUSES, it
        assert it["confidence"] in CONFIDENCES, it
        for score in ("signal_score", "hype_score"):
            v = it[score]
            assert isinstance(v, int) and 0 <= v <= 100, f"{score} out of range: {it.get('title')}"
        # source_url is optional but, when present, must be a safe scheme.
        su = it.get("source_url", "")
        assert su == "" or su.startswith(("https://", "http://", "mailto:")), f"bad source_url: {su}"


def assert_seo_files() -> None:
    sitemap = read("sitemap.xml")
    for page in ["archive.html", "weekly.html", "about.html", "privacy.html", "contact.html"]:
        assert page in sitemap, f"sitemap.xml missing {page}"
    assert "aisignaldesk.ai" in sitemap, "sitemap should use the live domain"
    assert "posts/" not in sitemap, "sitemap must not reference removed posts/"
    robots = read("robots.txt")
    assert "Sitemap:" in robots, "robots.txt should point to the sitemap"


def main() -> None:
    assert_required_files()
    assert_shared_page_contract()
    assert_security_invariants()
    assert_no_removed_refs()
    assert_preview_pages()
    assert_design_system()
    assert_home_contract()
    assert_archive_contract()
    assert_other_views()
    assert_trust_pages()
    assert_js_render_safety()
    assert_digest_contract()
    assert_seo_files()
    print("OK: AI Signal Desk (Daylight Desk) passes site + security checks")


if __name__ == "__main__":
    main()
