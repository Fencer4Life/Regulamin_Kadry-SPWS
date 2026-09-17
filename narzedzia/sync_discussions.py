from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

CATEGORY = "propozycje-zmian-regulaminu"


def _discussion_nodes(payload: dict | list[dict]):
    pages = payload if isinstance(payload, list) else [payload]
    for page in pages:
        yield from page.get("data", {}).get("repository", {}).get("discussions", {}).get("nodes", [])


def normalize_discussions(payload: dict | list[dict], generated_at: str) -> dict:
    open_items = []
    closed_items = []
    for node in _discussion_nodes(payload):
        if node.get("category", {}).get("slug") != CATEGORY:
            continue
        item = {
            "number": node["number"], "title": node["title"], "url": node["url"],
            "created_at": node["createdAt"], "author": (node.get("author") or {}).get("login", "konto usunięte"),
            "comments": node.get("comments", {}).get("totalCount", 0),
            "labels": [label["name"] for label in node.get("labels", {}).get("nodes", [])],
            "closed_at": node.get("closedAt"),
        }
        (closed_items if item["closed_at"] else open_items).append(item)
    open_items.sort(key=lambda item: item["created_at"], reverse=True)
    closed_items.sort(key=lambda item: item["closed_at"], reverse=True)
    return {
        "generated_at": generated_at,
        "open_items": open_items,
        "closed_items": closed_items,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.source.read_text(encoding="utf-8"))
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    args.destination.write_text(json.dumps(normalize_discussions(payload, generated_at), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
