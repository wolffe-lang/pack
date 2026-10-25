# The art study

What pack draws, on both tiers, and why. Every sprite here is a mock frame committed as a golden:
`tests/goldens/art/sheet-rich.txt` and `sheet-plain.txt` (with their `.sty` style files) are the sheets
`pack --art-study --dump DIR` writes, and `tools/goldens` keeps them current. Change a sprite and the
sheet's golden moves with it; the diff shows exactly which cells.

The rule for the tiers (campaign R-PK-4): one cell model, two glyph sets. The rich tier may use any code
point in `docs/GLYPHS.md`; the plain tier uses code points 0-255 and the sixteen colours, what PAX's
console font draws today. The sheet's plain half is held to that by `tier_test` and `art_test`.

## The viewpoint

Top down, the path running up the screen, the wolf low on the screen so the path leads (the alpha's eye,
campaign innovation 2). A wolf heads up; a shadow wolf faces down toward the pack; a deer stands across or
along the path.

## The wolf

Rich: three cells wide, two tall, half-blocks doubling the vertical resolution (R-pk00-4 B: only the
wolves are doubled; the forest and path stay one glyph a cell, and the cost of doubling everything is
measured in the note).

```
▝█▘      the head row: two ears and the head
▀█▄      the body row: a leg cell, the body, a leg cell
```

The gait is the leg cells: four frames cycle `▀ ▘ ▄ ▗` on the left and the opposite phase on the right,
advancing with distance travelled so the stride matches the speed, and a standing wolf holds frame 0. The
pant (exhausted) alternates the head between `█` and `▓` every eight ticks; in the forest edge the body is
drawn in dim fur. Fur is 250 on the path's 137; the plain wolf is `W` (the ears are the W's points) in bold
bright white with a tail cell that alternates `,` and `.`, and pants as `w`.

Sheet rows 3 (the four trot frames), 7 (standing, sprinting, the two pant phases, dim).

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
where nothing is drawn; density rises with distance from the path (`world.forest_kind`). The forest is
noise, not sprites: the same seed is the same forest.

## The pack in formation (pk01's shape)

Sheet rows 16-21: five wolves, two leading, two flanking, the alpha trailing at the centre, each with its
own gait frame. pk01 makes them move.

## What the maintainer may want to change first

The wolf's ears read best at a large font; at 12 points the quadrant blocks are small. A variant with
`▞█▚` (U+259E, U+259A) for the head row is one glyph change in `tier.rich`'s `SP_WOLF_EAR` and two rows
in GLYPHS.md. The canopy is dense; `world.forest_kind`'s thresholds are three numbers.
