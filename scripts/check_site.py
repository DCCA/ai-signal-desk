#!/usr/bin/env python3
"""Deterministic checks for the AI Signal Desk static MVP."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "content/digest.json",
    "docs/product-brief.md",
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


def main() -> None:
    assert_required_files()
    assert_homepage_contract()
    assert_content_contract()
    assert_css_quality_bar()
    assert_product_brief_contract()
    print("OK: AI Signal Desk static MVP passes scaffold checks")


if __name__ == "__main__":
    main()
