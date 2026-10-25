# Fonts in this directory

All four upstream families are licensed under the SIL Open Font License 1.1.
Full licence texts are in `LICENSES/`. The OFL permits bundling and
redistributing these fonts with software; it does not permit selling them on
their own.

| file | upstream | modified? |
|---|---|---|
| `ReelSans-400..800.ttf` | [Figtree](https://github.com/erikdkennedy/figtree) © 2022 The Figtree Project Authors | **yes** |
| `ReelSerif-600.ttf`, `ReelSerif-Italic-500.ttf` | [Playfair Display](https://github.com/clauseggers/Playfair) © The Playfair Project Authors | **yes** |
| `ChakraPetch-SemiBold.ttf`, `ChakraPetch-Bold.ttf` | [Chakra Petch](https://github.com/cadsondemak/Chakra-Petch) © 2018 The Chakra Petch Project Authors | no |
| `Amiri-Regular.ttf`, `Amiri-Bold.ttf` | [Amiri](https://github.com/aliftype/amiri) © 2010-2022 The Amiri Project Authors | no |

## What was modified, and why they were renamed

These derivatives add transliteration characters absent from their source
faces: dot-below letters ḥ ṣ ṭ ḍ ẓ ṛ, dot-above ṅ, line-below ḏ, and their
capitals, plus the half-ring letters ʿ ʾ. This avoids a different fallback
font appearing mid-word in citations such as `ṢAḤĪḤ MUSLIM 875`.

`scripts/patch_font.py` adds those letters as TrueType composites built from
each font's own base glyph plus its own period or macron. The added marks
retain the family's colour, contrast and weight. D/d with line below use
a macron translated below the baseline; N/n with dot above have their dot
placed above the base letter. These four composites were corrected in all
seven bundled Reel faces; the other glyph outlines were preserved.
The half-rings are cmap aliases onto the existing typographic quotes.

The modified faces were renamed to **Reel Sans** and **Reel Serif**:

- Playfair Display is released *with Reserved Font Name "Playfair Display"*.
  OFL 1.1 clause 3 forbids a Modified Version from using that name, so
  renaming is required, not optional.
- Figtree declares no Reserved Font Name, so renaming it is not required.
  It is renamed anyway, because a patched font carrying the upstream name
  misrepresents the upstream project.

Internal family, full and PostScript names use the derivative names. Any
retained variations PostScript name prefixes (name ID 25) were also renamed
to `ReelSans` or `ReelSerif`. Original copyright notices, Reserved Font Name
declarations and OFL licence text remain intact.

No changes were made here to the supplied Chakra Petch and Amiri files;
they keep their names. Their supplied bytes have not been independently
compared with an upstream release.

To patch another face:

```bash
python3 scripts/patch_font.py IN.ttf runtime/fonts/OUT.ttf \
        --weight 600 --rename "Your Name" --style "SemiBold"
```

Check the upstream OFL for a Reserved Font Name before you ship it.
