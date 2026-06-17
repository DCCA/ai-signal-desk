#!/usr/bin/env python3
"""Deterministic checks for the AI Signal Desk static MVP."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "index.html",
    "about.html",
    "privacy.html",
    "contact.html",
    "weekly.html",
    "brand.html",
    "logo-exploration.html",
    "styles.css",
    "app.js",
    "content/digest.json",
    "docs/product-brief.md",
    "docs/brand-foundation.md",
    "docs/launch-readiness-plan.md",
    "docs/launch-config.md",
    "docs/editorial-workflow.md",
    "docs/signal-card-schema.md",
    "docs/launch-checklist.md",
    "content/drafts/.gitkeep",
    "posts/agent-loops.html",
    "posts/context-engineering.html",
    "posts/lightweight-eval-harnesses.html",
    "DESIGN.md",
    "robots.txt",
    "sitemap.xml",
    "assets/brand-mark.svg",
    "favicon.svg",
    "assets/logo-radar-monogram.svg",
    "assets/logo-aperture.svg",
    "assets/logo-terminal-signal.svg",
    "assets/logo-classified-stamp.svg",
    "assets/logo-signal-grid.svg",
    "assets/logo-minimal-asd.svg",
    "README.md",
]

REQUIRED_NAV_TARGETS = ["#concepts", "#products", "#repos", "#workflows", "#weekly"]
REQUIRED_CONTENT_CATEGORIES = {"concept", "product", "repo", "workflow"}
REQUIRED_HERO_PHRASES = [
    "AI signal, not AI noise",
    "weekly field brief",
]
REQUIRED_META_MARKERS = [
    'property="og:title"',
    'property="og:description"',
    'property="og:type"',
    'property="og:image"',
    'name="twitter:card"',
    'rel="canonical"',
]
REQUIRED_TRUST_LINKS = ["about.html", "privacy.html", "contact.html"]
REQUIRED_WAITLIST_MARKERS = [
    "Join the free beta",
    "data-waitlist-link",
    "One practical brief per week",
]

REQUIRED_IDENTITY_MARKERS = [
    "signal-console",
    "radar-panel",
    "hype-filter",
    "field-brief",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def assert_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    assert not missing, f"Missing required files: {missing}"


def assert_homepage_contract() -> None:
    html = read("index.html")
    for phrase in REQUIRED_HERO_PHRASES:
        assert phrase in html, f"Homepage missing hero phrase: {phrase}"
    for marker in REQUIRED_META_MARKERS:
        assert marker in html, f"Homepage missing launch metadata marker: {marker}"
    for marker in REQUIRED_WAITLIST_MARKERS:
        assert marker in html, f"Homepage missing waitlist marker: {marker}"
    assert "replace-with-ai-signal-desk-waitlist" not in html, "Homepage should not ship with placeholder waitlist URL"
    assert "Newsletter signup demo" not in html, "Homepage should not contain demo-only signup form copy"
    for marker in REQUIRED_IDENTITY_MARKERS:
        assert marker in html, f"Homepage missing unique identity marker: {marker}"
    for target in REQUIRED_NAV_TARGETS:
        assert f'href="{target}"' in html, f"Navigation missing target {target}"
    for target in REQUIRED_TRUST_LINKS:
        assert f'href="{target}"' in html, f"Homepage missing trust link {target}"
    for section in ["concepts", "products", "repos", "workflows", "weekly"]:
        assert f'id="{section}"' in html, f"Homepage missing #{section} section"
    assert "digest-grid" in html, "Homepage should render digest cards"
    assert "newsletter" in html.lower(), "Homepage should include a newsletter/conversion section"


def assert_launch_trust_pages() -> None:
    page_requirements = {
        "about.html": ["Editorial standard", "What gets ignored", "human review"],
        "privacy.html": ["email address", "unsubscribe", "no selling"],
        "contact.html": ["Contact", "signals@aisignaldesk.example", "signals"],
    }
    for page_path, markers in page_requirements.items():
        page = read(page_path)
        assert 'href="styles.css"' in page, f"Trust page missing stylesheet: {page_path}"
        assert 'src="assets/brand-mark.svg"' in page, f"Trust page missing brand mark: {page_path}"
        for marker in markers:
            assert marker.lower() in page.lower(), f"{page_path} missing marker: {marker}"


def assert_launch_config_contract() -> None:
    config = read("docs/launch-config.md")
    for marker in ["Free beta", "Tally", "Cloudflare Pages", "Waitlist URL"]:
        assert marker in config, f"Launch config missing marker: {marker}"
    robots = read("robots.txt")
    assert "User-agent: *" in robots, "robots.txt missing user-agent rule"
    assert "Sitemap:" in robots, "robots.txt should point to sitemap"
    sitemap = read("sitemap.xml")
    for page in ["index.html", "about.html", "privacy.html", "contact.html"]:
        assert page in sitemap, f"sitemap.xml missing page: {page}"


def assert_content_contract() -> None:
    data = json.loads(read("content/digest.json"))
    items = data.get("items", [])
    assert len(items) >= 6, "MVP should include at least 6 seeded digest items"
    categories = {item.get("category") for item in items}
    assert REQUIRED_CONTENT_CATEGORIES <= categories, (
        f"Missing categories: {REQUIRED_CONTENT_CATEGORIES - categories}"
    )
    linked_posts = 0
    for item in items:
        for key in [
            "title",
            "category",
            "summary",
            "why_it_matters",
            "try_this",
            "status",
            "confidence",
            "source_url",
            "source_label",
        ]:
            assert item.get(key), f"Digest item missing {key}: {item}"
        assert item["status"] in {"learn", "try", "watch", "ignore"}, item
        assert item["confidence"] in {"high", "medium", "low"}, item
        assert item["source_url"].startswith(("https://", "mailto:")), item
        if item.get("post_url"):
            linked_posts += 1
            assert (ROOT / item["post_url"]).exists(), f"Digest post_url does not exist: {item['post_url']}"
    assert linked_posts >= 3, "At least 3 homepage cards should link to launch sample posts"


def assert_sample_posts_contract() -> None:
    index = read("index.html")
    for path, markers in {
        "posts/agent-loops.html": ["Agent loops", "What changed", "Why it matters", "Try this", "Sources"],
        "posts/context-engineering.html": ["Context engineering", "What changed", "Why it matters", "Try this", "Sources"],
        "posts/lightweight-eval-harnesses.html": ["Lightweight eval harnesses", "What changed", "Why it matters", "Try this", "Sources"],
    }.items():
        page = read(path)
        assert 'href="../styles.css"' in page, f"Post missing shared stylesheet: {path}"
        assert 'src="../assets/brand-mark.svg"' in page, f"Post missing brand mark: {path}"
        for marker in markers:
            assert marker in page, f"Post {path} missing marker: {marker}"
        assert path in index or path in read("content/digest.json"), f"Post not linked from launch content: {path}"


def assert_weekly_issue_contract() -> None:
    weekly = read("weekly.html")
    for marker in [
        "Issue 001",
        "Five useful updates",
        "Three things to try",
        "One concept to learn",
        "One thing to ignore",
        "Agent loops",
        "Context engineering",
        "Lightweight eval harnesses",
        "Sources reviewed",
    ]:
        assert marker in weekly, f"weekly.html missing marker: {marker}"
    assert 'href="posts/agent-loops.html"' in weekly, "weekly.html should link sample post"
    assert 'href="styles.css"' in weekly, "weekly.html should use shared stylesheet"


def assert_editorial_workflow_contract() -> None:
    workflow = read("docs/editorial-workflow.md")
    schema = read("docs/signal-card-schema.md")
    checklist = read("docs/launch-checklist.md")
    for marker in ["AI Daily Digest", "signals@aisignaldesk.example", "human review", "draft", "publish"]:
        assert marker.lower() in workflow.lower(), f"Editorial workflow missing marker: {marker}"
    for marker in ["source_url", "confidence", "status", "human_reviewed", "published"]:
        assert marker in schema, f"Signal card schema missing marker: {marker}"
    for marker in ["Mobile", "Signup", "Issue 001", "sample posts", "Tally"]:
        assert marker.lower() in checklist.lower(), f"Launch checklist missing marker: {marker}"


def assert_css_quality_bar() -> None:
    css = read("styles.css")
    for token in ["--ink", "--muted", "--card-shadow", "font-family", "@media"]:
        assert token in css, f"CSS missing expected design token/pattern: {token}"
    assert len(re.findall(r"\.(digest-card|pillar-card|signal-console)", css)) >= 3, "CSS should define distinct signal-desk card styling"


HTML_PAGES = ["index.html", "brand.html", "logo-exploration.html"]


def assert_accessibility_contract() -> None:
    css = read("styles.css")
    assert ":focus-visible" in css, "CSS must define a visible keyboard focus style"
    assert ".skip-link" in css, "CSS must style a skip-to-content link"
    assert "prefers-reduced-motion" in css, "CSS must respect reduced-motion users"
    # Navigation must stay reachable on mobile, never fully hidden.
    assert "nav { display: none; }" not in css, "Mobile nav must not be hidden entirely"

    for page in HTML_PAGES:
        html = read(page)
        assert 'lang="en"' in html, f"{page} must declare a document language"
        assert 'class="skip-link"' in html, f"{page} missing skip-to-content link"
        assert "<main" in html, f"{page} missing a <main> landmark"
        # Skip link target must resolve to a focusable main landmark.
        match = re.search(r'class="skip-link" href="#([\w-]+)"', html)
        assert match, f"{page} skip link must point to an in-page target"
        target = match.group(1)
        assert re.search(rf'<main[^>]*id="{target}"', html), (
            f"{page} skip link target #{target} must be the <main> landmark"
        )
        assert re.search(r'<main[^>]*tabindex="-1"', html), (
            f"{page} <main> must be focusable for skip-link navigation"
        )


def assert_seo_contract() -> None:
    html = read("index.html")
    for tag in [
        'rel="canonical"',
        'property="og:title"',
        'property="og:description"',
        'property="og:image"',
        'name="twitter:card"',
    ]:
        assert tag in html, f"index.html missing social/SEO tag: {tag}"


def assert_digest_filter_contract() -> None:
    html = read("index.html")
    # Every filter button must expose its pressed state to assistive tech.
    buttons = re.findall(r'<button class="filter[^"]*"[^>]*>', html)
    assert buttons, "Homepage must render digest filter buttons"
    for button in buttons:
        assert "aria-pressed" in button, f"Filter button missing aria-pressed: {button}"


def assert_render_safety() -> None:
    app = read("app.js")
    assert "function escapeHtml" in app, "app.js must define an HTML escaper"
    # Untrusted digest fields must be escaped, never interpolated raw, so that
    # automated content ingestion cannot inject markup.
    for field in ["title", "summary", "why_it_matters", "try_this", "category", "status"]:
        assert f"${{item.{field}}}" not in app, (
            f"app.js interpolates item.{field} without escaping"
        )
        assert f"escapeHtml(item.{field})" in app or f"escapeHtml(scoreFor" in app, (
            f"app.js must escape item.{field}"
        )


def assert_internal_anchors() -> None:
    for page in HTML_PAGES:
        html = read(page)
        ids = set(re.findall(r'id="([\w-]+)"', html))
        targets = set(re.findall(r'href="#([\w-]+)"', html))
        broken = sorted(target for target in targets if target not in ids)
        assert not broken, f"{page} has in-page links with no matching id: {broken}"


def assert_product_brief_contract() -> None:
    brief = read("docs/product-brief.md")
    for heading in ["## Target reader", "## Product promise", "## MVP scope", "## Editorial rules"]:
        assert heading in brief, f"Product brief missing {heading}"
    assert "not generic ai news" in brief.lower(), "Brief should protect differentiated positioning"


def assert_brand_contract() -> None:
    brand = read("docs/brand-foundation.md")
    for phrase in [
        "AI signal, not AI noise",
        "calm intelligence desk",
        "learn, try, watch, or ignore",
        "Signal score",
        "Hype score",
    ]:
        assert phrase in brand, f"Brand foundation missing phrase: {phrase}"
    design = read("DESIGN.md")
    for token in ["#080A0F", "#58E6FF", "IBM Plex Mono", "signal-card"]:
        assert token in design, f"DESIGN.md missing brand token: {token}"
    brand_page = read("brand.html")
    for marker in ["Brand System", "Visual system", "Component language"]:
        assert marker in brand_page, f"Brand page missing marker: {marker}"
    for page_path in ["index.html", "brand.html", "logo-exploration.html"]:
        page = read(page_path)
        assert 'href="favicon.svg"' in page, f"Page missing favicon link: {page_path}"
        assert 'src="assets/brand-mark.svg"' in page, f"Page missing selected brand mark: {page_path}"


def assert_logo_exploration_contract() -> None:
    logo_page = read("logo-exploration.html")
    for marker in [
        "Logo exploration / v0.1",
        "Radar monogram",
        "Signal aperture",
        "Terminal signal",
        "Classified stamp",
        "Signal grid",
        "Minimal ASD square",
        "Keep Option F",
    ]:
        assert marker in logo_page, f"Logo exploration missing marker: {marker}"
    for path in [
        "assets/logo-radar-monogram.svg",
        "assets/logo-aperture.svg",
        "assets/logo-terminal-signal.svg",
        "assets/logo-classified-stamp.svg",
        "assets/logo-signal-grid.svg",
        "assets/logo-minimal-asd.svg",
    ]:
        svg = read(path)
        assert "<svg" in svg and "</svg>" in svg, f"Invalid SVG wrapper: {path}"
        assert "#080A0F" in svg, f"Logo should use brand ink background: {path}"


def main() -> None:
    assert_required_files()
    assert_homepage_contract()
    assert_launch_trust_pages()
    assert_launch_config_contract()
    assert_content_contract()
    assert_sample_posts_contract()
    assert_weekly_issue_contract()
    assert_editorial_workflow_contract()
    assert_css_quality_bar()
    assert_accessibility_contract()
    assert_seo_contract()
    assert_digest_filter_contract()
    assert_render_safety()
    assert_internal_anchors()
    assert_product_brief_contract()
    assert_brand_contract()
    assert_logo_exploration_contract()
    print("OK: AI Signal Desk static MVP passes scaffold checks")


if __name__ == "__main__":
    main()
