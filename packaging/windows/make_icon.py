"""Generate the Windows application icon (multi-size .ico) with Pillow.

Run: python packaging/windows/make_icon.py
Outputs desktop/assets/icon.ico (and a 256px PNG preview).
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

_OUT = Path(__file__).resolve().parents[2] / "desktop" / "assets"


def _draw(size: int) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    pad = size // 8
    # rounded blue shield/card
    draw.rounded_rectangle(
        [pad, pad, size - pad, size - pad], radius=size // 6, fill=(59, 130, 246, 255)
    )
    # a simple white "book" glyph
    bx0, by0, bx1, by1 = size * 0.30, size * 0.32, size * 0.70, size * 0.68
    draw.rectangle([bx0, by0, bx1, by1], fill=(255, 255, 255, 255))
    draw.line([(size * 0.5, by0), (size * 0.5, by1)], fill=(59, 130, 246, 255), width=max(1, size // 40))
    return image


def main() -> None:
    _OUT.mkdir(parents=True, exist_ok=True)
    sizes = [16, 24, 32, 48, 64, 128, 256]
    base = _draw(256)
    base.save(_OUT / "icon.png")
    base.save(_OUT / "icon.ico", sizes=[(s, s) for s in sizes])
    print("wrote", _OUT / "icon.ico")


if __name__ == "__main__":
    main()
