#!/usr/bin/env python3
"""Create AI Signal Desk draft cards from manually shared links.

This is the deterministic boundary between platform chats (Discord/Telegram) and
public-facing Signal Desk drafts. The LLM/Hermes still does the editorial
synthesis, but this script enforces the repo schema, source-platform metadata,
private-context scanning, duplicate checks, and stable draft filenames before a
card can enter content/drafts/.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

# Import the existing publisher validator so shared-link drafts use exactly the
# same schema/enums/privacy/source checks as the publication path.
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import publish_signal_drafts as publisher  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DRAFTS_DIR = ROOT / "content" / "drafts"
DIGEST_PATH = ROOT / "content" / "digest.json"

PLATFORMS = {"discord", "telegram", "manual"}
SHARED_LINK_REQUIRED = [
    "title",
    "category",
    "status",
    "summary",
    "why_it_matters",
    "try_this",
    "title_pt",
    "summary_pt",
    "why_it_matters_pt",
    "try_this_pt",
    "source_label",
    "source_url",
    "confidence",
]


def load_payload(path: str | None) -> dict[str, Any]:
    if path and path != "-":
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return json.loads(sys.stdin.read())


def public_slug(value: str) -> str:
    return publisher.slugify(value)[:64] or "shared-link"


def load_existing() -> tuple[set[str], set[str]]:
    if not DIGEST_PATH.exists():
        return set(), set()
    digest = json.loads(DIGEST_PATH.read_text(encoding="utf-8"))
    items = digest.get("items", [])
    urls = {str(item.get("source_url", "")).strip().lower() for item in items}
    titles = {publisher.slugify(str(item.get("title", ""))) for item in items}
    return urls, titles


def draft_duplicates(date_prefix: str, source_url: str, title: str) -> list[str]:
    matches: list[str] = []
    source_url_norm = source_url.strip().lower()
    title_slug = publisher.slugify(title)
    for path in sorted(DRAFTS_DIR.glob("*.json")):
        try:
            card = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 - report malformed drafts elsewhere
            continue
        if str(card.get("source_url", "")).strip().lower() == source_url_norm:
            matches.append(f"{path.name}: duplicate draft source_url")
        if publisher.slugify(str(card.get("title", ""))) == title_slug:
            matches.append(f"{path.name}: duplicate draft title")
    return matches


def build_card(payload: dict[str, Any], source_platform: str, source_digest_date: str) -> dict[str, Any]:
    missing = [key for key in SHARED_LINK_REQUIRED if key not in payload]
    if missing:
        raise ValueError(f"missing required input field(s): {', '.join(missing)}")

    # Keep chat-platform provenance in draft-only metadata, not review_notes,
    # because review_notes are copied into the public digest at promotion time.
    review_bits = [
        "Shared-link intake validated for public Signal Desk draft.",
        "Private-context scan and source URL validation run before draft creation.",
    ]
    if payload.get("review_notes"):
        review_bits.append(str(payload["review_notes"]).strip())

    card: dict[str, Any] = {key: payload[key] for key in SHARED_LINK_REQUIRED}
    card.update(
        {
            "human_reviewed": False,
            "published": False,
            "review_notes": " ".join(part for part in review_bits if part),
            "source_digest_date": source_digest_date,
            "sanitized": True,
        }
    )
    if "signal_score" in payload:
        card["signal_score"] = payload["signal_score"]
    if "hype_score" in payload:
        card["hype_score"] = payload["hype_score"]
    return card


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Create Signal Desk draft JSON from a shared link synthesis payload.")
    parser.add_argument("--input", "-i", help="JSON payload path; omit or pass - for stdin")
    parser.add_argument("--source-platform", required=True, choices=sorted(PLATFORMS))
    parser.add_argument("--date", default=date.today().isoformat(), help="Draft/source date, YYYY-MM-DD")
    parser.add_argument("--force", action="store_true", help="Write even when a duplicate draft exists")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print target path without writing")
    args = parser.parse_args(argv)

    payload = load_payload(args.input)
    card = build_card(payload, args.source_platform, args.date)

    errors = publisher.validate_card(card, Path("shared-link-payload.json"))

    existing_urls, existing_titles = load_existing()
    source_url = str(card["source_url"]).strip().lower()
    title_slug = publisher.slugify(str(card["title"]))
    if source_url in existing_urls:
        errors.append("already published source_url in content/digest.json")
    if title_slug in existing_titles:
        errors.append("already published title in content/digest.json")

    dupes = draft_duplicates(args.date, str(card["source_url"]), str(card["title"]))
    if dupes and not args.force:
        errors.extend(dupes)

    if errors:
        print("ERROR: shared-link draft validation failed", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    slug = public_slug(str(card["title"]))
    target = DRAFTS_DIR / f"{args.date}-shared-{args.source_platform}-{slug}.json"

    if args.dry_run:
        print(f"Would create {target.relative_to(ROOT)}")
        return 0

    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Created {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
