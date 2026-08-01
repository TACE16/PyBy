"""
Fixes font issues with TAC-Barathi
"""

import tempfile
import shutil
from pathlib import Path
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

root = Path(".")
fonts = sorted(root.rglob("TAC-*.ttf"))

if not fonts:
    raise SystemExit("TAC எழுத்துருக்கள் எதுவும் கிடைக்கவில்லை.")

print(f"{len(fonts)} TAC எழுத்துருக்கள் கண்டறியப்பட்டன.")

for src in fonts:
    print(f"சரிசெய்கிறது: {src}")

    font = TTFont(src)

    # ஏற்கனவே உள்ள  mapping-களைப் பெறுதல்
    best_cmap = font.getBestCmap()

    if not best_cmap:
        raise RuntimeError(f" cmap கிடைக்கவில்லை: {src}")

    # BMP  எழுத்துகள் மட்டும்.
    bmp_cmap = {cp: glyph_name for cp, glyph_name in best_cmap.items() if cp <= 0xFFFF}

    pua = [cp for cp in bmp_cmap if 0xE000 <= cp <= 0xF8FF]

    print(f"   mappings: {len(bmp_cmap)}")
    print(f"  PUA mappings:     {len(pua)}")

    if pua:
        print(f"  PUA range:        " f"U+{min(pua):04X}-U+{max(pua):04X}")

    # Firefox ஏற்றுக்கொள்ளும் சுத்தமான cmap table.
    cmap = newTable("cmap")
    cmap.tableVersion = 0
    cmap.tables = []

    # Windows  BMP — format 4
    windows = CmapSubtable.newSubtable(4)
    windows.platformID = 3
    windows.platEncID = 1
    windows.language = 0
    windows.cmap = dict(bmp_cmap)

    cmap.tables.append(windows)

    #  BMP — format 4
    unicode_bmp = CmapSubtable.newSubtable(4)
    unicode_bmp.platformID = 0
    unicode_bmp.platEncID = 3
    unicode_bmp.language = 0
    unicode_bmp.cmap = dict(bmp_cmap)

    cmap.tables.append(unicode_bmp)

    font["cmap"] = cmap

    # TAC எழுத்துருக்களின் gasp table தீநரியில்
    # malformed என்று நிராகரிக்கப்படுகிறது.
    # gasp optional என்பதால் அதை அகற்றுகிறோம்.
    if "gasp" in font:
        del font["gasp"]

    # முதலில் தற்காலிக கோப்பில் எழுதுதல்.
    with tempfile.NamedTemporaryFile(suffix=".ttf", delete=False) as tmp:
        temp_path = Path(tmp.name)

    try:
        font.save(temp_path)

        # சரிசெய்யப்பட்ட font-ஐ source font-ன்
        # அதே இடத்தில் வைக்கிறது.
        shutil.copy2(temp_path, src)
    finally:
        temp_path.unlink(missing_ok=True)

    # சரிசெய்யப்பட்ட font-ஐ மீண்டும் திறந்து
    # PUA mappings சரியாக உள்ளதா என்று சரிபார்த்தல்.
    repaired = TTFont(src)
    repaired_cmap = repaired.getBestCmap()

    repaired_pua = [cp for cp in repaired_cmap if 0xE000 <= cp <= 0xF8FF]

    if len(repaired_pua) != len(pua):
        raise RuntimeError(
            f"PUA mapping எண்ணிக்கை மாறியுள்ளது: {src} "
            f"({len(pua)} -> {len(repaired_pua)})"
        )

    if pua:
        if min(repaired_pua) != min(pua) or max(repaired_pua) != max(pua):
            raise RuntimeError(f"PUA range மாறியுள்ளது: {src}")

    # gasp table உண்மையில் அகற்றப்பட்டுள்ளதா என்று சரிபார்த்தல்.
    if "gasp" in repaired:
        raise RuntimeError(f"gasp table இன்னும் உள்ளது: {src}")

    repaired.close()

    print(f"  சரிசெய்யப்பட்டது: {src}")

print("அனைத்து TAC எழுத்துருக்களும் சரிசெய்யப்பட்டன.")
