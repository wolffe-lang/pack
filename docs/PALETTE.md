# The palette

Colours are named by role in `src/tier/tier.lu` (`palette`), one number per role per tier. The rich tier
indexes the 256-colour cube (`38;5;n`), upgraded to the cube's own RGB (`38;2;r;g;b`) when `COLORTERM` says
`truecolor` or `24bit`; the plain tier uses the sixteen VT colours only (SGR 30-37 and 90-97, 40-47 and
100-107), which is what PAX's console and a Linux VT draw, and what their themes recolour.

## Afternoon (the one phase today)

| role | rich (256 index, cube RGB) | plain (VT colour) | where |
|---|---|---|---|
| path (background) | 137 (175,135,95: dry earth) | 3 yellow | every path cell, the wolves' background |
| path mark | 180 (215,175,135) | 11 bright yellow | pebbles and prints on the path |
| grass | 64 (95,135,0) | 2 green | the verge |
| trunk | 94 (135,95,0) | 3 yellow | trunks |
| canopy, light | 28 (0,135,0) | 2 green, bold | thin and medium canopy |
| canopy, dark | 22 (0,95,0) | 0 black (on the floor it reads as the dark) | dense canopy, the deep forest's glyphs |
| forest floor (background) | 234 (28,28,28) | 0 black | every forest cell's background |
| fur | 250 (188,188,188) | 15 bright white, bold | the wolf |
| fur, dim | 245 (138,138,138) | 7 white | the wolf in the forest edge |
| shadow | 236 (48,48,48) | 8 bright black | a shadow wolf's body |
| red eye | 196 (255,0,0) | 9 bright red | a shadow's eyes |
| deer | 173 (215,135,95) | 11 bright yellow, bold | the deer |
| the fainted | 243 (118,118,118) | 8 bright black | a fainted wolf |

The RGB values are the xterm cube's for each index (`grid.rgb_of`), so a true-colour terminal shows exactly
what a 256-colour one approximates. The plain column is a VT colour number; its RGB is the terminal's
theme, which pack does not control, and `grid.model`'s inverse of the RGB dialect maps the sixteen back to
their numbers rather than to a cube cell, so a captured stream reads back as the same cells.

## Dusk (pk03's keyframes, planned)

The dusk shift is a function from distance to a phase, and the palette takes the phase: afternoon as above;
dusk with the path at 95 (135,95,95), the canopy at 22 and 17, the floor at 233 and the fur at 248; night
with the path at 59 (95,95,95), the canopy at 17 and 16, the floor at 232 and the fur at 245, the red eyes
unchanged so that shadows come with the dark. On the plain tier dusk dims the greens to black-on-black and
night drops the path to 8 bright black. These are the first proposals for pk03 to tune by play; nothing in
pk00 reads them.
