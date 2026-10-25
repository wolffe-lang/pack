# The palette

Colours are named by role in `src/tier/tier.lu` (`palette`), one number per role per tier. The rich tier
indexes the 256-colour cube (`38;5;n`), upgraded to the cube's own RGB (`38;2;r;g;b`) when `COLORTERM` says
`truecolor` or `24bit`; the plain tier uses the sixteen VT colours only (SGR 30-37 and 90-97, 40-47 and
100-107), which is what PAX's console and a Linux VT draw, and what their themes recolour.

## Afternoon (phase 0)

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
| red eye | 196 (255,0,0) | 9 bright red | a shadow's eyes: bright while it attacks, one phase of the pulse while it chases |
| red eye, dim | 124 (175,0,0) | 1 red | a shadow's eyes while it lurks or recoils, the pulse's other phase (pk02) |
| deer | 223 (255,215,175: a pale fawn; pk00's 173 was the earth's own hue and vanished on the path) | 11 bright yellow, bold | the deer (pk03) |
| the fainted | 243 (118,118,118) | 8 bright black | a fainted wolf |
| the card's text | fur 250 on the floor 234 | 15 bright white, bold, on 0 black | the death card (pk02); its frame in dim fur 245 (plain 7 white) |

The RGB values are the xterm cube's for each index (`grid.rgb_of`), so a true-colour terminal shows exactly
what a 256-colour one approximates. The plain column is a VT colour number; its RGB is the terminal's
theme, which pack does not control, and `grid.model`'s inverse of the RGB dialect maps the sixteen back to
their numbers rather than to a cube cell, so a captured stream reads back as the same cells.

## Dusk and night (pk03, campaign innovation 4)

The palette takes a phase from the distance travelled (`sim.phase`: 0 to `DUSK_START` 600 rows is the
afternoon, 256 at `DUSK_FULL` 1200 is dusk, 512 at `NIGHT_FULL` 1800 is night, climbing between by at most
two a row; `docs/DESIGN.md`). `tier.palette_at` builds the frame's palette once a frame from three
keyframes:

| role | afternoon | dusk | night | plain afternoon / dusk / night |
|---|---|---|---|---|
| path (background) | 137 (175,135,95) | 95 (135,95,95) | 59 (95,95,95) | 3 / 3 / 8 bright black |
| path mark | 180 (215,175,135) | 138 (175,135,135) | 102 (135,135,135) | 11 / 3 / 7 |
| grass | 64 (95,135,0) | 58 (95,95,0) | 22 (0,95,0) | 2 / 2 / 0 (black on black) |
| trunk | 94 (135,95,0) | 58 (95,95,0) | 237 (58,58,58) | 3 / 3 / 8 |
| canopy, light | 28 (0,135,0) | 22 (0,95,0) | 17 (0,0,95) | 2 bold / 2 (the bold dropped: the greens dim) / 0 |
| canopy, dark | 22 (0,95,0) | 17 (0,0,95) | 16 (0,0,0) | 0 / 0 / 0 |
| forest floor (background) | 234 (28,28,28) | 233 (18,18,18) | 232 (8,8,8) | 0 / 0 / 0 |
| fur | 250 (188,188,188) | 248 (168,168,168) | 245 (138,138,138) | 15 bold / 15 bold / 7 |
| fur, dim | 245 | 243 (118,118,118) | 240 (88,88,88) | 7 / 7 / 8 |
| shadow | 236 (48,48,48) | 235 (38,38,38) | 233 (18,18,18) | 8 / 8 / 0 |
| red eye | 196 | 196 | 196 | 9 / 9 / 9 |
| red eye, dim | 124 | 124 | 124 | 1 / 1 / 1 |
| deer | 223 (255,215,175) | 180 (215,175,135) | 138 (175,135,135) | 11 / 11 / 7 |
| the fainted | 243 (118,118,118) | 241 (98,98,98) | 238 (68,68,68) | 8 / 8 / 0 |

The rich tier blends the two keyframes around the phase in RGB and takes the nearest index of the 256-colour
cube or grey ramp (`tier.nearest_index`; never one of the sixteen theme colours), in integer arithmetic so
every machine quantizes alike. The cube is coarse, so a role moves in a few small steps rather than
continuously: the path takes 137, 95, 241, 59 on its way to night (phases 0, 135, 378, 487), the fur six
steps, the eyes none. Each step recolours every cell of its role, so the frame it lands on is a full redraw
(the diff's worst case, measured under the perf gate with `--start 900`). A true-colour terminal could be
handed the blended RGB itself for a continuous shift; today it is given the quantized index's RGB, the same
on every terminal (a follow-up, listed in the pk03 note). The plain tier's sixteen colours cannot blend: they
step at the midpoints (phase 128 and 384). The red eyes are the same at every phase, so shadows come with
the dark: at night the shadow's body is a shade off the path and the eyes are all one sees of a lurker.

The death card and the title card draw in the phase's fur on the phase's floor, so a card at night is dim
fur on near-black; the title (shown over the seed's forest at its start) is the afternoon's unless `--start`
places the run later. The goldens `dusk-early` (start 750), `dusk` (1200) and `night` (1800) pin the three on
both tiers; the keyframes are the maintainer's to tune by play (R-PK-7), with `--start N` to see any phase
at once.
