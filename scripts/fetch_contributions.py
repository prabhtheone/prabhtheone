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


def main():
    response = requests.get(URL, headers={"User-Agent": "profile-calendar/1.0"}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("td.day[data-date]")
    if not cells:
        raise RuntimeError("No contribution cells found; refusing to overwrite existing data.")

    days = []
    for cell in cells:
        day = cell.get("data-date")
        if not day:
            continue
        label = cell.get("aria-label", "")
        match = re.search(r"(\d[\d,]*) contribution", label, re.I)
        count = int(match.group(1).replace(",", "")) if match else 0
        level = max(0, min(int(cell.get("data-level", "0")), 4))
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
    print(f"Saved {len(days)} days and {data['total']} contributions.")


if __name__ == "__main__":
    main()
