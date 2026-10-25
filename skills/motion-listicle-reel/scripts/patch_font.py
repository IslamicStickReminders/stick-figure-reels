#!/usr/bin/env python3
"""
Add Arabic-transliteration letters to a display font that lacks them.

Most pretty display faces (Figtree, Playfair, DM Sans...) cover macrons
(a i u) but not the dot-below letters used in academic transliteration
(h s t d z). Without them the browser silently falls back to another font
mid-word, which looks broken on screen.

This builds the missing letters as TrueType COMPOSITES out of glyphs the
font already has: base letter + the font's own period or macron. Marks are
placed above or below the base as the Unicode character requires, retaining
the font's colour, contrast and optical weight.

  python3 patch_font.py IN.ttf OUT.ttf [--weight 600] [--rename "Reel Sans"]

--rename rewrites the font's internal name table. Use it whenever you patch
a face: a modified font carrying the original's name is confusing at best,
and if the upstream licence declares a Reserved Font Name (OFL 1.1 clause 3)
shipping a modified version under that name is not permitted. Playfair
Display reserves its name; Figtree, Chakra Petch and Amiri do not.

A variable font is instantiated to a static weight first, because adding
composites to a varfont without matching gvar deltas corrupts it.
"""
import sys, argparse
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
from fontTools.varLib import instancer

# target codepoint -> (base char, mark kind)
MARKED_LETTERS = {
    0x1E25: ("h", "dot"), 0x1E24: ("H", "dot"),   # h H
    0x1E63: ("s", "dot"), 0x1E62: ("S", "dot"),   # s S
    0x1E6D: ("t", "dot"), 0x1E6C: ("T", "dot"),   # t T
    0x1E0D: ("d", "dot"), 0x1E0C: ("D", "dot"),   # d D
    0x1E93: ("z", "dot"), 0x1E92: ("Z", "dot"),   # z Z
    0x1E45: ("n", "dot_above"), 0x1E44: ("N", "dot_above"),
    0x1E5B: ("r", "dot"), 0x1E5A: ("R", "dot"),   # r R
    0x1E0F: ("d", "bar"), 0x1E0E: ("D", "bar"),   # d D (line below)
}
# half-ring letters: borrow the typographic quotes, which every text font has
ALIAS = {0x02BF: "quoteleft", 0x02BE: "quoteright", 0x02BB: "quoteleft", 0x02BC: "quoteright"}


def best_cmap_table(font):
    """Every unicode cmap subtable, so aliases land in all of them."""
    return [t for t in font["cmap"].tables if t.isUnicode()]


def glyph_for_char(font, ch):
    cm = font.getBestCmap()
    return cm.get(ord(ch))


def bounds(glyf, hmtx, name):
    g = glyf[name]
    if g.numberOfContours == 0:
        adv = hmtx[name][0]
        return 0, 0, adv, 0
    g.recalcBounds(glyf)
    return g.xMin, g.yMin, g.xMax, g.yMax


WIN, MAC = (3, 1, 0x409), (1, 0, 0)


def rename(font, family, style="Regular"):
    """Rewrite the name table so a modified face stops claiming to be the
    original. Required by OFL 1.1 clause 3 for any font with a Reserved
    Font Name; good manners for every other patched font."""
    ps = (family + "-" + style).replace(" ", "")
    full = family + " " + style
    vals = {1: family, 2: style, 3: full + "; patched", 4: full, 6: ps,
            16: family, 17: style}
    nt = font["name"]
    for nid, val in vals.items():
        for pid, eid, lid in (WIN, MAC):
            if nid in (16, 17) and not nt.getName(nid, pid, eid, lid):
                continue
            nt.setName(val, nid, pid, eid, lid)
    # A static instance may retain its upstream variations PostScript prefix.
    # Update every existing language/platform record, not only WIN and MAC.
    prefix = "".join(c for c in family if c.isascii() and c.isalnum())
    if not prefix:
        raise ValueError("Font family must contain ASCII letters or digits")
    for record in list(nt.names):
        if record.nameID == 25:
            nt.setName(prefix, 25, record.platformID, record.platEncID,
                       record.langID)
    return full


def patch(inp, out, weight=None, verbose=True, new_name=None, style="Regular"):
    font = TTFont(inp)

    if "fvar" in font:
        axes = {a.axisTag: a for a in font["fvar"].axes}
        loc = {}
        if "wght" in axes:
            w = weight if weight is not None else axes["wght"].defaultValue
            loc["wght"] = max(axes["wght"].minValue, min(axes["wght"].maxValue, w))
        for tag, a in axes.items():
            loc.setdefault(tag, a.defaultValue)
        font = instancer.instantiateVariableFont(font, loc, inplace=False, updateFontNames=False)
        if verbose:
            print(f"  instantiated variable font at {loc}")

    if "glyf" not in font:
        raise SystemExit("patch_font: CFF/OTF input not supported - use a TTF")

    glyf, hmtx = font["glyf"], font["hmtx"]
    upem = font["head"].unitsPerEm
    cmaps = best_cmap_table(font)
    have = font.getBestCmap()

    # Borrow marks from this same font, preserving their original outlines.
    dot_src = have.get(ord(".")) or have.get(ord("·"))
    if dot_src is None:
        raise SystemExit("patch_font: font has no period to clone a dot from")
    bar_src = have.get(0x00AF) or have.get(0x0304) or have.get(ord("-"))

    added, skipped = [], []
    for cp, (base_ch, kind) in MARKED_LETTERS.items():
        if cp in have:
            skipped.append(chr(cp)); continue
        base = glyph_for_char(font, base_ch)
        if base is None:
            continue
        bx0, by0, bx1, by1 = bounds(glyf, hmtx, base)
        mark_src = bar_src if kind == "bar" else dot_src
        if mark_src is None:
            raise SystemExit("patch_font: font has no macron or hyphen to clone a line from")
        mx0, my0, mx1, my1 = bounds(glyf, hmtx, mark_src)
        name = "uni%04X" % cp

        comp_base = GlyphComponent()
        comp_base.glyphName = base
        comp_base.x, comp_base.y = 0, 0
        comp_base.flags = 0x04  # ROUND_XY_TO_GRID

        comp_mark = GlyphComponent()
        comp_mark.glyphName = mark_src
        comp_mark.x = int(round((bx0 + bx1) / 2 - (mx0 + mx1) / 2))
        if kind == "dot_above":
            comp_mark.y = int(round(by1 + upem * 0.075 - my0))
        else:
            comp_mark.y = int(round(-upem * 0.175 - my1))
        comp_mark.flags = 0x04

        g = Glyph()
        g.numberOfContours = -1
        g.components = [comp_base, comp_mark]
        glyf.glyphs[name] = g
        if name not in font.getGlyphOrder():
            font.getGlyphOrder().append(name)
        hmtx[name] = hmtx[base]
        for t in cmaps:
            t.cmap[cp] = name
        added.append(chr(cp))

    for cp, target in ALIAS.items():
        if cp in have or target not in glyf.glyphs:
            continue
        for t in cmaps:
            t.cmap[cp] = target
        added.append(chr(cp))

    if new_name:
        full = rename(font, new_name, style)
        if verbose:
            print(f"  renamed: {full}")

    font["maxp"].numGlyphs = len(font.getGlyphOrder())
    font.save(out)
    if verbose:
        print(f"  added  : {''.join(added) or 'none'}")
        if skipped:
            print(f"  already: {''.join(skipped)}")
        print(f"  wrote  : {out}")
    return added


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--weight", type=float, default=None)
    ap.add_argument("--rename", default=None, help="new internal family name")
    ap.add_argument("--style", default="Regular", help="style name, e.g. Italic")
    a = ap.parse_args()
    patch(a.inp, a.out, a.weight, new_name=a.rename, style=a.style)
