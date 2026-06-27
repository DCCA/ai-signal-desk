#!/usr/bin/env python3
"""Promote validated draft signal cards into the public AI Signal Desk digest.

This script is intentionally deterministic so the scheduled feeder can publish
without relying on prose-only LLM self-checks.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
DIGEST_PATH = ROOT / "content" / "digest.json"
DRAFTS_DIR = ROOT / "content" / "drafts"

REQUIRED = [
    "title",
    "category",
    "status",
    "summary",
    "why_it_matters",
    "try_this",
    "source_label",
    "source_url",
    "confidence",
    "human_reviewed",
    "published",
    "review_notes",
    "source_digest_date",
    "sanitized",
]
CATEGORIES = {"concept", "product", "repo", "workflow"}
STATUSES = {"learn", "try", "watch", "ignore"}
CONFIDENCE = {"high", "medium", "low"}
# Generic, non-identifying private-context patterns kept in this public file.
# Account-specific terms (personal handles, private tool/app names, internal
# system names, project codenames) are NOT committed here — they load from a
# gitignored local file so they never enter this public repo. See
# scripts/private_patterns.example.txt for setup.
DEFAULT_PRIVATE_PATTERNS = [
    r"/home/[^\s/\"']+",       # any local home-directory path
    r"/mnt/[a-z](?:/|\b)",     # WSL drive mounts (/mnt/c, /mnt/d, ...)
    r"\bcron\b",
    r"local file path",
    r"private repo",
    r"personal side project",
    r"your workflow",
    r"my workflow",
]

SCRIPT_DIR = Path(__file__).resolve().parent


def load_private_patterns() -> list[str]:
    """Union the generic in-source patterns with account-specific ones loaded
    from a local (gitignored) file. Falls back to the committed example file and
    warns, so the editorial flow never silently runs without the local terms."""
    patterns = list(DEFAULT_PRIVATE_PATTERNS)
    local = SCRIPT_DIR / "private_patterns.local.txt"
    source = local if local.exists() else SCRIPT_DIR / "private_patterns.example.txt"
    if source != local:
        print(
            "warning: scripts/private_patterns.local.txt not found — only generic "
            "patterns are active. Copy private_patterns.example.txt to "
            "private_patterns.local.txt and add your account-specific terms "
            "before publishing.",
            file=sys.stderr,
        )
    if source.exists():
        for line in source.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.append(line)
    return patterns


PRIVATE_PATTERNS = load_private_patterns()


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:80] or "signal"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def text_blob(card: dict[str, Any]) -> str:
    return json.dumps(card, ensure_ascii=False)


def validate_url(url: str) -> tuple[bool, str]:
    parsed = urlparse(url)
    if parsed.scheme not in {"https", "mailto"}:
        return False, f"unsupported URL scheme: {parsed.scheme!r}"
    if parsed.scheme == "mailto":
        return True, "mailto URL not fetched"
    req = Request(url, headers={"User-Agent": "AI Signal Desk validation bot"}, method="GET")
    try:
        with urlopen(req, timeout=20) as response:
            code = getattr(response, "status", 200)
        if 200 <= code < 400:
            return True, f"HTTP {code}"
        return False, f"HTTP {code}"
    except HTTPError as exc:
        # Some canonical sources (notably OpenAI pages) reject bot traffic.
        # Keep them publishable, but mark the caveat in review notes upstream.
        if exc.code in {401, 403, 405, 429}:
            return True, f"HTTP {exc.code} bot-blocked; accepted with caveat"
        return False, f"HTTP {exc.code}"
    except URLError as exc:
        return False, f"URL error: {exc.reason}"
    except Exception as exc:  # noqa: BLE001 - CLI validator should report exact failure
        return False, f"URL validation error: {exc}"


def validate_card(card: dict[str, Any], path: Path) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED:
        if key not in card:
            errors.append(f"{path.name}: missing {key}")
    if errors:
        return errors
    if card["category"] not in CATEGORIES:
        errors.append(f"{path.name}: invalid category {card['category']!r}")
    if card["status"] not in STATUSES:
        errors.append(f"{path.name}: invalid status {card['status']!r}")
    if card["confidence"] not in CONFIDENCE:
        errors.append(f"{path.name}: invalid confidence {card['confidence']!r}")
    if card["human_reviewed"] is not False:
        errors.append(f"{path.name}: draft human_reviewed must be false before promotion")
    if card["published"] is not False:
        errors.append(f"{path.name}: draft published must be false before promotion")
    if card["sanitized"] is not True:
        errors.append(f"{path.name}: sanitized must be true")
    for key in ["title", "summary", "why_it_matters", "try_this", "source_label", "source_url"]:
        if not str(card.get(key, "")).strip():
            errors.append(f"{path.name}: empty {key}")
    blob = text_blob(card)
    for pattern in PRIVATE_PATTERNS:
        if re.search(pattern, blob, flags=re.IGNORECASE):
            errors.append(f"{path.name}: privacy/private-context pattern found: {pattern}")
    ok, note = validate_url(str(card.get("source_url", "")))
    if not ok:
        errors.append(f"{path.name}: source_url failed validation: {note}")
    else:
        card.setdefault("validation_notes", {})
        if isinstance(card["validation_notes"], dict):
            card["validation_notes"]["source_url_check"] = note
    return errors


def public_review_notes(card: dict[str, Any]) -> str:
    """Return review notes that are safe to expose in the public digest."""
    notes = str(card.get("review_notes", "")).strip()
    if not notes:
        notes = "Automated review passed: schema, source URL, duplicate, and private-context checks completed before publication."
    for pattern in PRIVATE_PATTERNS:
        if re.search(pattern, notes, flags=re.IGNORECASE):
            raise ValueError(f"review_notes contains private-context pattern: {pattern}")
    return notes


def promote_card(card: dict[str, Any], publish_date: str) -> dict[str, Any]:
    promoted = {
        "title": card["title"],
        "category": card["category"],
        "summary": card["summary"],
        "why_it_matters": card["why_it_matters"],
        "try_this": card["try_this"],
        "status": card["status"],
        "confidence": card["confidence"],
        "source_label": card["source_label"],
        "source_url": card["source_url"],
        "human_reviewed": False,
        "published": True,
        "automated_reviewed": True,
        "review_notes": public_review_notes(card),
        "source_digest_date": card["source_digest_date"],
        "published_date": publish_date,
        "sanitized": True,
        "signal_score": card.get("signal_score", default_signal_score(card)),
        "hype_score": card.get("hype_score", default_hype_score(card)),
    }
    return promoted


def default_signal_score(card: dict[str, Any]) -> int:
    base = {"try": 86, "learn": 82, "watch": 76, "ignore": 35}[card["status"]]
    conf = {"high": 5, "medium": 0, "low": -8}[card["confidence"]]
    cat = {"repo": 2, "workflow": 3, "concept": 0, "product": -1}[card["category"]]
    return max(1, min(100, base + conf + cat))


def default_hype_score(card: dict[str, Any]) -> int:
    base = {"try": 22, "learn": 18, "watch": 34, "ignore": 88}[card["status"]]
    conf = {"high": -4, "medium": 0, "low": 10}[card["confidence"]]
    return max(1, min(100, base + conf))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat(), help="source_digest_date to publish")
    parser.add_argument("--max-cards", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--delete-promoted-drafts",
        action="store_true",
        help="Delete draft JSON files after successful promotion to content/digest.json.",
    )
    args = parser.parse_args(argv)

    if not DIGEST_PATH.exists():
        print(f"ERROR: missing {DIGEST_PATH}", file=sys.stderr)
        return 2

    digest = load_json(DIGEST_PATH)
    items = digest.setdefault("items", [])
    existing_urls = {str(item.get("source_url", "")).strip().lower() for item in items}
    existing_titles = {slugify(str(item.get("title", ""))) for item in items}

    draft_paths = sorted(DRAFTS_DIR.glob(f"{args.date}-*.json"))
    candidates: list[tuple[Path, dict[str, Any]]] = []
    errors: list[str] = []
    skipped: list[str] = []

    for path in draft_paths:
        card = load_json(path)
        if card.get("source_digest_date") != args.date:
            skipped.append(f"{path.name}: source_digest_date mismatch")
            continue
        card_errors = validate_card(card, path)
        if card_errors:
            errors.extend(card_errors)
            continue
        title_slug = slugify(card["title"])
        source_url = str(card["source_url"]).strip().lower()
        if source_url in existing_urls or title_slug in existing_titles:
            skipped.append(f"{path.name}: duplicate published source/title")
            continue
        candidates.append((path, card))

    if errors:
        print("ERROR: validation failed", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    if not candidates:
        print("No publishable draft cards found.")
        if skipped:
            print("Skipped:")
            for item in skipped:
                print(f"- {item}")
        return 0

    promoted: list[dict[str, Any]] = []
    for path, card in candidates[: args.max_cards]:
        promoted_item = promote_card(card, args.date)
        promoted.append(promoted_item)
        existing_urls.add(str(promoted_item["source_url"]).strip().lower())
        existing_titles.add(slugify(promoted_item["title"]))

    if args.dry_run:
        print(f"Would publish {len(promoted)} card(s):")
        for item in promoted:
            print(f"- {item['title']} ({item['source_url']})")
        if skipped:
            print("Skipped:")
            for item in skipped:
                print(f"- {item}")
        return 0

    items.extend(promoted)
    digest["updated"] = args.date
    save_json(DIGEST_PATH, digest)

    if args.delete_promoted_drafts:
        for path, _card in candidates[: args.max_cards]:
            path.unlink()

    print(f"Published {len(promoted)} card(s) to content/digest.json")
    for item in promoted:
        print(f"- {item['title']} ({item['source_url']})")
    if skipped:
        print("Skipped:")
        for item in skipped:
            print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
