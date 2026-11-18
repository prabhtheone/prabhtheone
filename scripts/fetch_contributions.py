#!/usr/bin/env python3
"""Refresh the public GitHub contribution calendar as JSON."""
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

USERNAME = "prabhtheone"
URL = f"https://github-contributions-api.jogruber.de/v4/{USERNAME}?y=last"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "contributions.json"


def main():
    response = requests.get(
        URL,
        headers={"User-Agent": "prabhtheone-profile-cards/1.0"},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    raw_days = payload.get("contributions")
    if not isinstance(raw_days, list) or not raw_days:
        raise RuntimeError("Contribution API returned no daily contribution data.")

    days = []
    for item in raw_days:
        date = item.get("date")
        if not date:
            continue
        count = int(item.get("count", 0))
        level = max(0, min(int(item.get("level", 0)), 4))
        if count < 0:
            raise RuntimeError(f"Invalid negative contribution count for {date}.")
        days.append({"date": date, "count": count, "level": level})

    if not days:
        raise RuntimeError("Contribution API returned no usable dates.")
    days.sort(key=lambda item: item["date"])
    counts = [day["count"] for day in days]
    data = {
        "username": USERNAME,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": sum(counts),
        "active_days": sum(count > 0 for count in counts),
        "best_day": max(counts, default=0),
        "days": days,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(
        f"Saved {len(days)} days, {data['total']} contributions, "
        f"{data['active_days']} active days."
    )


if __name__ == "__main__":
    main()
