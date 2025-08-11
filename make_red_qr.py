#!/usr/bin/env python3
"""
make_red_qr.py
Generates a red QR code PNG containing the text/details you provide.

Usage examples:
  python make_red_qr.py --text "Hello! This is my info." --out myqr.png
  python make_red_qr.py --file details.txt --out red-contact.png
  python make_red_qr.py --text "https://example.com/profile?id=123" --out link_qr.png --size 10
"""

import argparse
from pathlib import Path
import qrcode
from qrcode.constants import ERROR_CORRECT_M
from PIL import Image

def generate_qr(data: str, out_path: Path, box_size: int = 10, border: int = 4,
                fill_color: str = "red", back_color: str = "white"):
    """
    Generate a colored QR code.
    - data: text to encode (URL, JSON, vCard, plain text, etc.).
    - out_path: output PNG file path.
    - box_size: size of each QR module in pixels.
    - border: width of border (in modules).
    - fill_color: color of QR "dots" (use a color name or hex, e.g. '#cc0000').
    - back_color: background color.
    """
    qr = qrcode.QRCode(
        version=None,  # automatic size
        error_correction=ERROR_CORRECT_M,  # medium error correction; increase if you plan logos/overlays
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")

    # Optional: ensure high-DPI friendly by saving as PNG (Pillow will do).
    img.save(out_path, format="PNG")
    print(f"Saved QR to: {out_path.resolve()}")

def main():
    p = argparse.ArgumentParser(description="Generate a red QR code with provided details.")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Text or URL to encode into the QR.")
    group.add_argument("--file", help="Path to a file containing the text to encode.")
    p.add_argument("--out", default="qr.png", help="Output PNG filename (default: qr.png).")
    p.add_argument("--size", type=int, default=10, help="Box size in pixels (default: 10).")
    p.add_argument("--border", type=int, default=4, help="QR border width in modules (default: 4).")
    p.add_argument("--color", default="red", help="QR color (name or hex), default 'red'.")
    p.add_argument("--bg", default="white", help="Background color, default 'white'.")

    args = p.parse_args()

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            p.error(f"File not found: {args.file}")
        data = file_path.read_text(encoding="utf-8")
    else:
        data = args.text

    out_path = Path(args.out)
    generate_qr(data, out_path, box_size=args.size, border=args.border,
                fill_color=args.color, back_color=args.bg)

if __name__ == "__main__":
    main()
