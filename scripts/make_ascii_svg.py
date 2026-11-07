#!/usr/bin/env python3
"""Convert source-prepped.png to a row-by-row animated ASCII SVG."""
from pathlib import Path
from html import escape
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE, OUTPUT = ROOT / "source-prepped.png", ROOT / "avi-ascii.svg"
RAMP = " .`:-=+*cs#%@"


def main():
    if not SOURCE.exists():
        raise SystemExit("Missing source-prepped.png. Run prep_photo.py with your photo first.")
    image = Image.open(SOURCE).convert("L")
    columns = 88
    rows = max(1, round(columns * image.height / image.width * 0.52))
    image = image.resize((columns, rows))
    pixels = image.load()
    glyph_rows = []
    for y in range(rows):
        chars = []
        for x in range(columns):
            shade = pixels[x, y]
            chars.append(RAMP[round((255 - shade) / 255 * (len(RAMP) - 1))])
        glyph_rows.append(escape("".join(chars)))

    char_width, line_height = 7.2, 11
    width, height = round(columns * char_width + 24), rows * line_height + 42
    elements = []
    for index, line in enumerate(glyph_rows):
        y = 31 + (index + 1) * line_height
        delay = index * 0.035
        elements.append(
            f'<clipPath id="r{index}"><rect x="12" y="{y - 10}" width="0" height="{line_height}">'
            f'<animate attributeName="width" from="0" to="{columns * char_width}" dur=".65s" '
            f'begin="{delay:.3f}s" fill="freeze"/></rect></clipPath>'
            f'<text x="12" y="{y}" clip-path="url(#r{index})">{line}</text>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">Animated ASCII portrait</title><desc id="desc">Monochrome portrait that types itself row by row.</desc>
<style>text{{font-family:ui-monospace,monospace;font-size:10px;fill:#d1d5db;white-space:pre}}</style>
<rect width="100%" height="100%" rx="12" fill="#0d1117"/>
<text x="12" y="21" style="font-family:monospace;font-size:11px;fill:#86efac">$ ./portrait.sh</text>
{''.join(elements)}
</svg>'''
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Rendered {OUTPUT}")


if __name__ == "__main__":
    main()
