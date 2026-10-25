# The rich tier's glyphs

Every code point the rich tier can draw, each once. This list is the specification for PAX's console font
row (pk04): once PAX's font draws each of these at one cell, PAX runs the rich tier unchanged. The plain
tier uses nothing above U+00FF, so it needs no row.

The list is held to the code by a test: `src/glyphs_test.lu` reads this file and compares the `U+` entries
with `tier.rich_code_points()`, both ways. Add a glyph to `src/tier/tier.lu` and this table must gain it in
the same commit.

## How a width is measured

A photo is not evidence. `pack --probe-glyphs` writes each glyph on an empty line and asks the terminal
where the cursor landed (`CSI 6 n`, the cursor position report); the column it answers, less one, is the
cells the glyph took on that terminal. Run it in the terminal you want to know about and paste the table
into the matching column below with the date. The pseudo-terminal runner cannot measure this: a pty has no
font. What it does check is that the model and the live stream agree on cell positions, which is a
different fact.

| | Terminal.app | iTerm2 | Linux VT (kasumi's kernel) | PAX's console |
|---|---|---|---|---|
| measured | owed: run `pack --probe-glyphs` here and record the date | owed, the same way | owed; the VT draws from its own font and substitutes what it lacks | draws `?` for every code point at or above U+0100 today (`kernel/screen/screen.lu`'s header); pk04's row |

## The glyphs

Unicode's East Asian Width is `N` (neutral) for every entry, so a conforming terminal gives each one cell;
that is the expectation the columns above measure against.

| code point | glyph | name | block | UTF-8 | used for |
|---|---|---|---|---|---|
| U+0060 | ` | GRAVE ACCENT | Basic Latin | 60 | a path mark |
| U+00B7 | · | MIDDLE DOT | Latin-1 Supplement | C2 B7 | a path mark |
| U+2024 | ․ | ONE DOT LEADER | General Punctuation | E2 80 A4 | a path mark |
| U+2503 | ┃ | BOX DRAWINGS HEAVY VERTICAL | Box Drawing | E2 94 83 | a trunk |
| U+2580 | ▀ | UPPER HALF BLOCK | Block Elements | E2 96 80 | the wolf's leg cells, the cards' top edge |
| U+2584 | ▄ | LOWER HALF BLOCK | Block Elements | E2 96 84 | the wolf's leg cells, the fainted wolf |
| U+2588 | █ | FULL BLOCK | Block Elements | E2 96 88 | a wolf's body and head, a shadow, the deer's body |
| U+2591 | ░ | LIGHT SHADE | Block Elements | E2 96 91 | a path mark, the fainted wolf's head |
| U+2593 | ▓ | DARK SHADE | Block Elements | E2 96 93 | the panting head |
| U+2597 | ▗ | QUADRANT LOWER RIGHT | Block Elements | E2 96 97 | a leg cell |
| U+2598 | ▘ | QUADRANT UPPER LEFT | Block Elements | E2 96 98 | a leg cell, the right ear, the deer's right antler |
| U+259D | ▝ | QUADRANT UPPER RIGHT | Block Elements | E2 96 9D | the left ear, the deer's left antler |
| U+25AA | ▪ | BLACK SMALL SQUARE | Geometric Shapes | E2 96 AA | a shadow's red eye |
| U+2816 | ⠖ | BRAILLE PATTERN DOTS-235 | Braille Patterns | E2 A0 96 | grass |
| U+2836 | ⠶ | BRAILLE PATTERN DOTS-2356 | Braille Patterns | E2 A0 B6 | grass, thin canopy |
| U+28EE | ⣮ | BRAILLE PATTERN DOTS-234678 | Braille Patterns | E2 A3 AE | canopy |
| U+28F6 | ⣶ | BRAILLE PATTERN DOTS-2345678 | Braille Patterns | E2 A3 B6 | canopy |
| U+28FF | ⣿ | BRAILLE PATTERN DOTS-12345678 | Braille Patterns | E2 A3 BF | dense canopy |

Eighteen code points in five blocks: two already inside Latin-1 (PAX draws them today), one from General
Punctuation, one from Box Drawing, nine from Block Elements, one from Geometric Shapes and five from
Braille Patterns. The pack (pk01) and the shadows (pk02) reuse these cells: the shadow's fade is the full
block, the dark shade and the light shade, its eyes pulse by colour, and the death card's frame is the two
half blocks and the full block, all already here. The cards' text is ASCII (U+0020 to U+007E), inside
PAX's font today, so the death card and the title card (pk03) add no row (`tier.card_text`;
`test_card_cells_need_no_font_row` holds it). The dusk shift (pk03) changes colours, not glyphs, and the
deer's antlers and body reuse the wolf's quadrants and the full block, so the row for PAX stayed this
size through pk03: eighteen code points.
