# Animated profile README

The profile README is a stack of generated SVG cards. The daily GitHub Action
refreshes contribution data and regenerates the cards in `cards/`.

## Preview locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
python scripts/fetch_contributions.py
STATIC=1 python scripts/render_profile_cards.py
open cards/hero.svg
```

Use `STATIC=1` for screenshot-ready final frames. Run without it to restore
the staggered CSS and SMIL animations.

The renderer embeds subsetted Inter and IBM Plex Mono WOFF fonts as base64 data
URIs. Font licence notices are kept in `assets/fonts/OFL-1.1.txt`.

The scheduled workflow runs daily at 06:17 UTC and commits refreshed
`data/contributions.json`, the existing heatmap, and all generated SVG cards.
