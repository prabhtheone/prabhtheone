#!/usr/bin/env python3
"""Render GitHub's daily contribution levels as an animated SVG calendar."""
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

    parsed = sorted(
        ((date.fromisoformat(item["date"]), item) for item in days),
        key=lambda pair: pair[0],
    )
    first = parsed[0][0]
    first_sunday = date.fromordinal(first.toordinal() - (first.weekday() + 1) % 7)
    cell, gap, left, top = 12, 4, 32, 43
    weeks = max(53, ((parsed[-1][0] - first_sunday).days // 7) + 1)
    width, height = left * 2 + weeks * (cell + gap), 145
    shapes, months, seen = [], [], set()

    for day, item in parsed:
        offset = (day - first_sunday).days
        x = left + offset // 7 * (cell + gap)
        y = top + offset % 7 * (cell + gap)
        level = max(0, min(int(item.get("level", 0)), 4))
        delay = offset // 7 * 0.018 + offset % 7 * 0.025
        title = escape(f"Contribution activity on {day.isoformat()} (level {level}/4)")
        shapes.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" '
            f'fill="{COLORS[level]}"><title>{title}</title>'
            f'<animate attributeName="opacity" from="0.15" to="1" dur=".35s" '
            f'begin="{delay:.3f}s" fill="freeze"/></rect>'
        )
        key = (day.year, day.month)
        if key not in seen and day.day <= 7:
            seen.add(key)
            months.append(f'<text x="{x}" y="23">{day.strftime("%b")}</text>')

    legend_x = width - 112
    legend = "".join(
        f'<rect x="{legend_x + i * 15}" y="124" width="10" height="10" '
        f'rx="2" fill="{color}"/>'
        for i, color in enumerate(COLORS)
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">GitHub contribution activity for {escape(payload.get("username", "GitHub user"))}</title>
<desc id="desc">A calendar heatmap showing the daily contribution intensity over the last year.</desc>
<style>text{{font-family:ui-monospace,monospace;fill:#94a3b8;font-size:11px}}.prompt{{fill:#86efac;font-size:13px;font-weight:600}}</style>
<rect width="100%" height="100%" rx="12" fill="#0d1117"/>
<text x="18" y="23" class="prompt">prabhjot@github ~ $ contribution-activity</text>
{''.join(months)}{''.join(shapes)}
<text x="{legend_x - 34}" y="134">Less</text>{legend}<text x="{width - 28}" y="134">More</text>
</svg>'''
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Rendered {len(parsed)} contribution days for {payload.get('username')}.")


if __name__ == "__main__":
    main()
