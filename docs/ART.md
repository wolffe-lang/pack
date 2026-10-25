# The art study

What pack draws, on both tiers, and why. Every sprite here is a mock frame committed as a golden:
`tests/goldens/art/sheet-rich.txt` and `sheet-plain.txt` (with their `.sty` style files) are the sheets
`pack --art-study --dump DIR` writes, and `tools/goldens` keeps them current. Change a sprite and the
sheet's golden moves with it; the diff shows exactly which cells.

The rule for the tiers (campaign R-PK-4): one cell model, two glyph sets. The rich tier may use any code
point in `docs/GLYPHS.md`; the plain tier uses code points 0-255 and the sixteen colours, what PAX's
console font draws today. The sheet's plain half is held to that by `tier_test` and `art_test`.

## The viewpoint

Top down, the path running up the screen, the alpha low on the screen so the path leads (the alpha's eye,
campaign innovation 2) and the rest of the pack ahead of it. A wolf heads up; a shadow wolf faces down toward
the pack; a deer stands across or along the path. A wolf that faints lies where it fell and the world scrolls
it off the bottom edge; when it returns it sprints up from below the bottom edge to its slot.

## The wolf

Rich: three cells wide, two tall, half-blocks doubling the vertical resolution (R-pk00-4 B: only the
wolves are doubled; the forest and path stay one glyph a cell, and the cost of doubling everything is
measured in the note).

```
▝█▘      the head row: an ear, the head, an ear
▀█▘      the body row: the legs, the body, the tail
```

The gait is the leg cell: four frames cycle `▀ ▘ ▄ ▗`, advancing with each wolf's own distance travelled so
the stride matches its speed, and a standing wolf holds frame 0. In the forest edge the body is drawn in dim
fur. Fur is 250 on the path's 137.

**Posture is the HUD** (campaign innovation 5): there is no bar and no number. The ears and the tail carry
the pack's stamina band and the head carries exhaustion, so the player reads the pack the way one reads a dog:

| band | stamina | ears | tail | head |
|---|---|---|---|---|
| fresh | 200 and above | up, `▝ ▘` | wags with the gait, `▘ ▝` | `█` |
| tired | 100 to 199 | back, `▘ ▝` (the quadrants swapped inward) | level, `▀` | `█` |
| spent | under 100, or exhausted | flat, `▀ ▀` | low, `▄` | `█`, and while exhausted the pant: `█` and `▓` alternating every eight ticks |

The gait itself slows as health falls (the pack's speed loses up to a quarter at zero health), and a wolf
that is gone from its slot is health's other reading.

The plain wolf is `W` in bold bright white with a tail cell to its right: fresh `,` and `'` alternating with
the gait, tired `,`, spent `.`; spent or panting the head is `w`; in the forest edge the `W` is dim.

Sheet rows 3 (the four trot frames), 7 (standing, sprinting, the two pant phases, dim, tired, spent).

## The fainted wolf

Rich `▄░▄`: a low shape with a pale head, in the fainted grey 243; plain `x_`. Sheet row 11, left.

## The shadow wolf

Rich, two rows: a body row of three shadow cells `███` (236) and a near row `▪█▪`, the two `▪` in red 196
on the shadow — the eyes, facing down the path. Plain `W:` in bright black with a bright red `:`. Sheet
row 11, middle, twice (the second with the eye variant pk02 will blink).

## The deer

Rich `▀` over `█` in 173, a tall shape with its head up the path; plain `Y|` in bright yellow. Sheet row 11,
right.

## The path

Background 137 (dry earth). Marks on about one cell in nine: rich `·`, `░`, `․` and `` ` `` in 180; plain
`.`, `,`, `'` and `` ` `` in bright yellow. The marks scroll with the world, so the eye reads the speed.

## The forest

The verge, within a cell of the path's edge, is grass: `⠶` and `⠖` (plain `"` and `'`) in 64 on the floor
234. Beyond it trunks `┃` (plain `|`), canopy `⣿ ⣶ ⣮ ⠶` (plain `& % * ;`) in two greens, and deep forest
where nothing is drawn; the cover rises with distance from the path. The forest's **density**, a third
channel of the same noise that bends the path (`world.density`, `world.forest_kind`), picks the band: a
**clearing** (density under 72 of 256) is grass to the verge with the odd trunk and the path at its widest;
**thin woods** open near the path and close beyond it; a **dense stand** (168 and above) draws the woods'
foliage with more trunks and the path at its narrowest. The stand had its own texture in pk01 (canopy from
the verge, deep forest three cells in); the maintainer, playing that build on 2026-10-25, saw it as dense
horizontal bands of dots against the varied foliage the run starts with and ruled that the starting
texture is kept for the duration of the run (R-PK-7, the maintainer's word), so one foliage texture serves
both bands and density shows in the trunks, the path's width and the spawn rate. The forest is noise, not
sprites: the same seed is the same forest, and a clearing sits in the bend it came with. The sheet shows
the three bands top to bottom (rows 0-7 a clearing, 8-15 woods, 16-23 a stand); the goldens `clearing`
(seed 11) and `dense-stand` (seed 16) show each on both tiers.

## The pack in formation

Sheet rows 16-21: five wolves, two leading, two flanking, the alpha trailing at the centre, each with its
own gait frame, at the slots `sim.slot_dx`/`slot_dy` give (leaders two cells either side and five ahead,
flankers five either side and two ahead). In the game they move: each wolf follows the steer its slot's lag
late (the leaders at once, the flankers three ticks later, the alpha six: a turn ripples back through the
pack), wanders a cell or so around its slot on seeded noise, and bumps a neighbour it touches half a cell
away rather than overlapping it (the maintainer's ruling R-pk01-2 C). The golden `formation-turn` (seed 3)
has such a bump at tick 16: frame 15 shows the leaders touching, frame 20 nudged apart.

## The fainted wolf in the game

At each health floor the wolf farthest from the alpha faints: it is drawn with the fainted sprite where it
fell, under the running pack, and the world scrolls it off the bottom edge. At each recovery threshold a
fainted wolf returns: from where it lies if that is still on the screen, else from one row below the bottom
edge, sprinting (the sprint posture) up to its slot. The golden `faint-return` (seed 7) shows two faints and
two returns on both tiers.

## What the maintainer may want to change first

The wolf's ears read best at a large font; at 12 points the quadrant blocks are small. A variant with
`▞█▚` (U+259E, U+259A) for the fresh ears is one glyph change in `tier.rich`'s `SP_WOLF_EAR` and two rows
in GLYPHS.md. The three stamina bands are two numbers (`STAMINA_TIRED`, `STAMINA_SPENT`); the density bands
are two (`DENSITY_CLEARING`, `DENSITY_STAND`); the formation's slots, lags, wander and bump are the table in
`docs/DESIGN.md`, each a named constant.
