#!/usr/bin/env python3
"""
tools/convert_pcx.py

Usage:
  python tools/convert_pcx.py --zip SonicXtreme_v37.zip --out assets/png --keep-originals

What it does:
- Scans the given ZIP for files with a .pcx extension (case-insensitive).
- Converts each PCX to a PNG using Pillow, preserving directory structure.
- Writes assets/manifest.json with the list of converted images and their sizes.

Requirements:
- Python 3.8+
- Pillow (pip install Pillow)

Notes:
- By default the script will write PNGs as 24-bit RGBA (lossless). Use --quantize to reduce size (palette based).
- The script does not modify the repo by itself; run it locally in a clone and commit the generated assets if you want them in git.

"""

import argparse
import json
import os
import sys
import zipfile
from io import BytesIO
from pathlib import Path

try:
    from PIL import Image
except Exception:
    print("Pillow is required. Install with: pip install Pillow")
    sys.exit(1)


def ensure_dir(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def convert_pcx_bytes(b: bytes, quantize: bool = False):
    with Image.open(BytesIO(b)) as im:
        im = im.convert('RGBA')  # Normalize to RGBA
        if quantize:
            # Convert to P mode (palette) to reduce size, then back to RGBA for consistent output
            p = im.convert('P', palette=Image.ADAPTIVE)
            im = p.convert('RGBA')
        out = BytesIO()
        im.save(out, format='PNG', optimize=True)
        out.seek(0)
        return out.read(), im.width, im.height


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--zip', required=True, help='Path to ZIP file to scan (e.g., SonicXtreme_v37.zip)')
    p.add_argument('--out', default='assets/png', help='Output directory for PNGs')
    p.add_argument('--keep-originals', action='store_true', help='Also write PCX bytes to assets/pcx-originals (optional)')
    p.add_argument('--quantize', action='store_true', help='Quantize images to reduce size (palette-based)')
    p.add_argument('--manifest', default='assets/manifest.json', help='Output manifest JSON path')
    args = p.parse_args()

    zip_path = Path(args.zip)
    if not zip_path.exists():
        print(f"ZIP file not found: {zip_path}")
        sys.exit(2)

    out_root = Path(args.out)
    manifest = []
    total = 0

    with zipfile.ZipFile(zip_path, 'r') as z:
        names = [n for n in z.namelist() if n.lower().endswith('.pcx')]
        print(f"Found {len(names)} .pcx files in {zip_path}")
        for name in names:
            try:
                b = z.read(name)
            except KeyError:
                print(f"Could not read {name} from zip")
                continue

            # Write original if requested
            if args.keep_originals:
                orig_path = Path('assets/pcx-originals') / name
                ensure_dir(orig_path)
                orig_path.parent.mkdir(parents=True, exist_ok=True)
                with open(orig_path, 'wb') as f:
                    f.write(b)

            # Convert
            try:
                png_bytes, w, h = convert_pcx_bytes(b, quantize=args.quantize)
            except Exception as e:
                print(f"Failed to convert {name}: {e}")
                continue

            out_path = out_root / Path(name).with_suffix('.png')
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, 'wb') as f:
                f.write(png_bytes)

            manifest.append({
                'source': name,
                'png': str(out_path).replace('\\', '/'),
                'width': w,
                'height': h,
                'bytes': len(png_bytes),
            })
            total += 1

    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump({'images': manifest}, f, indent=2)

    print(f"Converted {total} images. Manifest written to {manifest_path}")


if __name__ == '__main__':
    main()
