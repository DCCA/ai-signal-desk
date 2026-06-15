#!/usr/bin/env python3
"""Deterministic checks for the AI Signal Desk static MVP."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "index.html",
    "brand.html",
    "logo-exploration.html",
    "styles.css",
    "app.js",
    "content/digest.json",
    "docs/product-brief.md",
    "docs/brand-foundation.md",
    "DESIGN.md",
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
    for marker in REQUIRED_IDENTITY_MARKERS:
        assert marker in html, f"Homepage missing unique identity marker: {marker}"
    for target in REQUIRED_NAV_TARGETS:
        assert f'href="{target}"' in html, f"Navigation missing target {target}"
    for section in ["concepts", "products", "repos", "workflows", "weekly"]:
        assert f'id="{section}"' in html, f"Homepage missing #{section} section"
    assert "digest-grid" in html, "Homepage should render digest cards"
    assert "newsletter" in html.lower(), "Homepage should include a newsletter/conversion section"


def assert_content_contract() -> None:
    data = json.loads(read("content/digest.json"))
    items = data.get("items", [])
    assert len(items) >= 6, "MVP should include at least 6 seeded digest items"
    categories = {item.get("category") for item in items}
    assert REQUIRED_CONTENT_CATEGORIES <= categories, (
        f"Missing categories: {REQUIRED_CONTENT_CATEGORIES - categories}"
    )
    for item in items:
        for key in ["title", "category", "summary", "why_it_matters", "try_this", "status"]:
            assert item.get(key), f"Digest item missing {key}: {item}"
        assert item["status"] in {"learn", "try", "watch", "ignore"}, item


def assert_css_quality_bar() -> None:
    css = read("styles.css")
    for token in ["--ink", "--muted", "--card-shadow", "font-family", "@media"]:
        assert token in css, f"CSS missing expected design token/pattern: {token}"
    assert len(re.findall(r"\.(digest-card|pillar-card|signal-console)", css)) >= 3, "CSS should define distinct signal-desk card styling"


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
    assert_content_contract()
    assert_css_quality_bar()
    assert_product_brief_contract()
    assert_brand_contract()
    assert_logo_exploration_contract()
    print("OK: AI Signal Desk static MVP passes scaffold checks")


if __name__ == "__main__":
    main()
