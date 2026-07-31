#!/usr/bin/env python3

from pathlib import Path
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
import sys


def repair_font(src: Path, dst: Path):
    print(f"Repairing: {src}")

    font = TTFont(src)

    # Get the existing Unicode mappings.
    best_cmap = font.getBestCmap()

    if not best_cmap:
        print(f"  WARNING: No Unicode cmap found: {src}")
        return False

    # Keep only BMP characters.
    bmp_cmap = {
        cp: glyph_name
        for cp, glyph_name in best_cmap.items()
        if cp <= 0xFFFF
    }

    pua = [
        cp for cp in bmp_cmap
        if 0xE000 <= cp <= 0xF8FF
    ]

    print(f"  Unicode mappings: {len(bmp_cmap)}")
    print(f"  PUA mappings:     {len(pua)}")

    if pua:
        print(
            f"  PUA range:        "
            f"U+{min(pua):04X}-U+{max(pua):04X}"
        )

    # Build a clean cmap table.
    cmap = newTable("cmap")
    cmap.tableVersion = 0
    cmap.tables = []

    # Windows Unicode BMP — format 4.
    windows = CmapSubtable.newSubtable(4)
    windows.platformID = 3
    windows.platEncID = 1
    windows.language = 0
    windows.cmap = dict(bmp_cmap)

    cmap.tables.append(windows)

    # Unicode BMP — format 4.
    unicode_bmp = CmapSubtable.newSubtable(4)
    unicode_bmp.platformID = 0
    unicode_bmp.platEncID = 3
    unicode_bmp.language = 0
    unicode_bmp.cmap = dict(bmp_cmap)

    cmap.tables.append(unicode_bmp)

    font["cmap"] = cmap

    dst.parent.mkdir(parents=True, exist_ok=True)
    font.save(dst)

    print(f"  Saved: {dst}")
    return True


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: repair_tac_fonts.py "
            "<source-directory> <output-directory>"
        )
        sys.exit(1)

    source_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    fonts = sorted(source_dir.rglob("*.ttf"))

    if not fonts:
        print(f"No TTF fonts found in {source_dir}")
        sys.exit(1)

    print(f"Found {len(fonts)} TTF font(s).")

    for src in fonts:
        relative = src.relative_to(source_dir)
        dst = output_dir / relative
        repair_font(src, dst)

    print("Font repair completed.")


if __name__ == "__main__":
    main()