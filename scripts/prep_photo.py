#!/usr/bin/env python3
"""Prepare a photo locally for ASCII conversion; optional dependencies only."""
import sys
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/prep_photo.py path/to/photo.jpg")
    source = Path(sys.argv[1]).expanduser()
    if not source.is_file():
        raise SystemExit(f"Photo not found: {source}")
    image = Image.open(source).convert("RGBA")
    try:
        from rembg import remove
        image = remove(image)
    except ImportError as exc:
        raise SystemExit("Install photo extras: pip install -r scripts/requirements-photo.txt") from exc
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    background.alpha_composite(image)
    gray = ImageOps.grayscale(background.convert("RGB"))
    try:
        import cv2
        import numpy as np
        gray = Image.fromarray(cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(np.array(gray)))
    except ImportError:
        gray = ImageOps.autocontrast(gray)
    output = ROOT / "source-prepped.png"
    gray.save(output)
    print(f"Prepared image: {output}")


if __name__ == "__main__":
    main()
