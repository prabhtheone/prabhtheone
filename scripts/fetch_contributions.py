#!/usr/bin/env python3
"""Fetch GitHub's public contribution calendar without a personal access token."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "prabhtheone"
URL = f"https://github.com/users/{USERNAME}/contributions"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "contributions.json"


def contribution_count(cell):
    """Read the count from the cell or its tooltip across GitHub markup variants."""
    candidates = [
        cell.get("aria-label", ""),
        cell.get("title", ""),
        cell.get_text(" ", strip=True),
    ]
    candidates.extend(
        node.get("aria-label", "") or node.get("title", "")
        for node in cell.find_all(True)
    )
    for label in candidates:
        match = re.search(r"(\d[\d,]*)\s+contributions?", label, re.I)
        if match:
            return int(match.group(1).replace(",", ""))
    return 0


def main():
    response = requests.get(
        URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; profile-calendar/1.0)"},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # GitHub has changed the calendar class names over time. The date/level
    # attributes are the stable data needed by the renderer.
    cells = soup.select("[data-date][data-level]")
    if not cells:
        raise RuntimeError(
            "GitHub returned no dated contribution cells; refusing to overwrite data."
        )

    days = []
    for cell in cells:
        day = cell.get("data-date")
        if not day:
            continue
        try:
            level = max(0, min(int(cell.get("data-level", "0")), 4))
        except ValueError:
            level = 0
        count = contribution_count(cell)
        days.append({"date": day, "count": count, "level": level})

    if not days:
        raise RuntimeError("Contribution calendar contained no usable dates.")
    days.sort(key=lambda item: item["date"])
    counts = [item["count"] for item in days]
    data = {
        "username": USERNAME,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": sum(counts),
        "active_days": sum(value > 0 for value in counts),
        "best_day": max(counts, default=0),
        "days": days,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(
        f"Saved {len(days)} days, {data['total']} contributions, "
        f"and {data['active_days']} active days."
    )


if __name__ == "__main__":
    main()
