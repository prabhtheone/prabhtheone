#!/usr/bin/env python3
"""Render contribution JSON into an animated, self-contained SVG calendar."""
import json
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "contrib-heatmap.svg"
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def main():
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    days = payload.get("days", [])
    if not days:
        raise SystemExit("No contribution data. Run fetch_contributions.py first.")
    parsed = [(date.fromisoformat(item["date"]), item) for item in days]
    first = parsed[0][0]
    first_sunday = date.fromordinal(first.toordinal() - (first.weekday() + 1) % 7)
    cell, gap, left, top = 12, 4, 32, 43
    weeks = max(53, ((parsed[-1][0] - first_sunday).days // 7) + 1)
    width, height = left * 2 + weeks * (cell + gap), 145
    shapes, months, seen = [], [], set()

    for day, item in parsed:
        offset = (day - first_sunday).days
        x, y = left + offset // 7 * (cell + gap), top + offset % 7 * (cell + gap)
        level = max(0, min(int(item.get("level", 0)), 4))
        count = int(item.get("count", 0))
        delay = offset // 7 * 0.018 + offset % 7 * 0.025
        title = escape(f"{count} contributions on {day.isoformat()}")
        shapes.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{COLORS[level]}">'
            f'<title>{title}</title><animate attributeName="opacity" from="0.1" to="1" '
            f'dur=".4s" begin="{delay:.3f}s" fill="freeze"/></rect>'
        )
        key = (day.year, day.month)
        if key not in seen and day.day <= 7:
            seen.add(key)
            months.append(f'<text x="{x}" y="23">{day.strftime("%b")}</text>')

    total = int(payload.get("total", 0))
    active = int(payload.get("active_days", 0))
    legend = "".join(
        f'<rect x="{width - 118 + i * 16}" y="124" width="10" height="10" rx="2" fill="{c}"/>'
        for i, c in enumerate(COLORS)
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">GitHub contributions for {escape(payload.get("username", "GitHub user"))}</title>
<desc id="desc">{total} contributions across {active} active days.</desc>
<style>text{{font-family:ui-monospace,monospace;fill:#94a3b8;font-size:11px}}.prompt{{fill:#86efac;font-size:13px;font-weight:600}}.stat{{fill:#e2e8f0;font-size:12px}}</style>
<rect width="100%" height="100%" rx="12" fill="#0d1117"/>
<text x="18" y="23" class="prompt">prabhjot@github ~ $ ./contributions.sh</text>
{''.join(months)}{''.join(shapes)}
<text x="18" y="136" class="stat">{total:,} contributions · {active} active days</text>
<text x="{width - 151}" y="136">Less</text>{legend}<text x="{width - 24}" y="136">More</text>
</svg>'''
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Rendered {OUTPUT}")


if __name__ == "__main__":
    main()
