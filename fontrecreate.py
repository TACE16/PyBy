from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

src = ".//TAC-Barathi.ttf"
dst = "TAC-Barathi"

font = TTFont(src)

# Preserve the existing Unicode mappings.
best_cmap = font.getBestCmap()

print("Existing mappings:", len(best_cmap))

# Keep only the Unicode BMP mappings.
bmp_cmap = {
    cp: glyph_name
    for cp, glyph_name in best_cmap.items()
    if cp <= 0xFFFF
}

print("BMP mappings:", len(bmp_cmap))

# Build a clean cmap table.
cmap = newTable("cmap")
cmap.tableVersion = 0
cmap.tables = []

# Windows Unicode BMP — format 4.
subtable = CmapSubtable.newSubtable(4)
subtable.platformID = 3
subtable.platEncID = 1
subtable.language = 0
subtable.cmap = dict(bmp_cmap)

cmap.tables.append(subtable)

# Unicode BMP — format 4.
subtable_unicode = CmapSubtable.newSubtable(4)
subtable_unicode.platformID = 0
subtable_unicode.platEncID = 3
subtable_unicode.language = 0
subtable_unicode.cmap = dict(bmp_cmap)

cmap.tables.append(subtable_unicode)

font["cmap"] = cmap

font.save(dst)

print("Saved:", dst)