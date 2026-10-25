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

Rich, two rows: a body row of three shadow cells `███` (236) and a near row `▪█▪`, the two `▪` in red
on the shadow — the eyes, on the row toward the pack: below the body while the shadow faces down the path
(lurking ahead, stalking), above it once it has turned and chases from behind. Red is the one colour both
tiers share for the eyes, and the eyes carry the shadow's state: dim (124; plain red) while it lurks in the
verge or is knocked back by a parry, pulsing bright (196) and dim every `EYE_PULSE` ticks while it chases,
steady bright through an attack's windup — the lunge the player parries. Plain `W:` in bright black with the
`:` bright red or red the same way. A shadow comes out of the forest half a cell into the verge, so it is
drawn over the foliage there; it leaves the dark for the earth as it chases.

A vanquished shadow (a leap landed) fades where it stands: the eyes go out and the body thins from `█` to
`▓` to `░` over `FADE_TICKS`, then it is gone; plain `W`, `w`, `.`. The fading are drawn under the live, so
a shadow passing over one is whole. Sheet row 11: a shadow with bright eyes facing down the path, one with
dim eyes facing up it, and one fading.

## The deer

Rich, two cells wide and two tall: the antlers `▝▘` (the quadrant blocks the wolf's ears use, leaning out)
over the body `██`, in a pale fawn (223) on the path's earth, so it stands against the earth where pk00's
tan (173, the earth's own hue) did not; plain `YD` in bright yellow, bold. The head is up the path as it
grazes toward the oncoming pack or flees from it. A deer is a lighter, paler, antlered shape beside the
wolf's three-cell grey; what makes it prey is its motion against the pack's — the slow sideways wander
across the path while everything else scrolls, and the bolt up the path at 1.5 v when a wolf comes within
ten cells, pulling away from the trot until it tires and slows below it (`docs/DESIGN.md`, the deer table).
A tired deer is not yet drawn differently (a head-down variant, `▄▄` over the body, is one glyph change in
`SP_DEER` if play wants it). Sheet row 11, right; the golden `deer-flee` (seed 4) shows one grazing,
bolting, tiring and run down on both tiers.

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

## The deer in the game

The golden `deer-flee` (seed 4, one wolf down from tick 5): a deer grazes down the path at the walk from
tick 39, bolts at 57 when a leader comes within `DEER_PERCEIVE`, pulls away at `FLEE_V` until its stamina
is spent at 146 and it slows to `DEER_TIRED_V`, below the trot; the pack closes, two sprints (374, 398)
run it down, and at 421 a leader within `CATCH_REACH` brings it down: the deer is gone, health is up by
`FEED`, and the fainted wolf sprints back to its slot. Deer are bodies for the separation rule, so a wolf
and a deer bump and never overlap, and a shadow may cross one (the deer are drawn under the live shadows).

## Dusk

The colours, not the glyphs, carry the time of day (campaign innovation 4): `docs/PALETTE.md`'s keyframes,
blended by the distance travelled. At dusk the earth goes to a dull rose-grey and the canopy to a darker
green; at night the path is grey, the canopy a dark blue over black, the fur dim, and a shadow's body is a
shade off the earth so its red eyes are what the player sees first. The goldens `dusk-early`, `dusk` and
`night` (seed 11 from rows 750, 1200 and 1800) show the three on both tiers.

## The death card

At health 0 the alpha is alone and the next landed attack ends the run: the world stands still (the eyes
stop pulsing, the gaits hold) and the card is drawn over the field from the same cell model on both tiers,
`CARD_COLS` by `CARD_ROWS` centred. Its frame is the upper and lower half blocks and the full block in dim
fur on the forest floor (plain `-` and `|`); its text is ASCII in fur on the floor, the title and the score
bold. The lines: `the pack is gone`; `shadows vanquished`, `seconds survived`, `distance, cells`, `score`
with their numbers at the right; and the offer `s saves the replay, q leaves`, which becomes `saved NAME; q
leaves` once `s` has written the file. These are the first numbers the player sees (innovation 5): a test
scans every frame before the card for a digit. The golden `death-card` (seed 16, health taken to zero at
tick 1) shows it on both tiers.

## The title card

The game opens on the title (pk03), drawn over the seed's forest at its start from the same cell model as
the death card, `TITLE_COLS` by `TITLE_ROWS` centred: the name, `lead the pack up the forest path`, the
seed the next run takes, the last score (and a replay's verdict), the best (score, seed, date, the replay's
name) in bold, the last saved replay, what the keys do (`any key to run; r runs this seed again`, `p plays
the last saved replay; / one by name`, `q leaves`), and a last line that is the prompt (`replay: name_`)
when `/` opened it or a message (a verdict, a refusal by name). Its text is ASCII, so GLYPHS.md gains no
row. The art study writes it on both tiers as `title-rich` and `title-plain` with a record to show.

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

## The shadows in the game

The goldens `spawn-chase`, `group-attack`, `leap-lands` and `parry-turns` (all seed 16, which starts in a
dense stand where the spawn rate is above `GROUP_RATE`) show a group of three appearing at the forest edge
above the top of the screen, lurking with dim eyes, one turning onto the path as a leader comes within
`PERCEIVE` and stalking down it with pulsing eyes, biting the leader as it passes (eyes steady through the
windup), braking to rest and turning up the path after the pack (the direction change is what the eye
catches, as pk01's bump was), the three riding the pack's left flank and landing together, a leap taking two
of them (the pack's lunge, the fade), and a parry turning a landing attack (the shadow knocked back half a
cell a tick, eyes dim, then chasing again).

## What the maintainer may want to change first

The wolf's ears read best at a large font; at 12 points the quadrant blocks are small. A variant with
`▞█▚` (U+259E, U+259A) for the fresh ears is one glyph change in `tier.rich`'s `SP_WOLF_EAR` and two rows
in GLYPHS.md. The three stamina bands are two numbers (`STAMINA_TIRED`, `STAMINA_SPENT`); the density bands
are two (`DENSITY_CLEARING`, `DENSITY_STAND`); the formation's slots, lags, wander and bump are the table in
`docs/DESIGN.md`, each a named constant. The shadows' pulse is `EYE_PULSE` and its two reds are
`PALETTE.md`'s; the fade is `FADE_TICKS`; the card's size is `CARD_COLS` by `CARD_ROWS` and its text is
`art.card_with`'s six lines. The leap now has a low stretched block pose (sheet row 3, column 42), plain `>W`.
The leaders and left flanker travel first; the right flanker and alpha next.
The non-leaping wolves hold formation; a one-tick bright dot (plain `*`) marks each
vanquished target at landing. A parry stance remains a possible later change. The deer's shape and colour are `SP_DEER`'s three variants and `C_DEER`'s three keyframes; the dusk's
keyframes are `tier.rich_key` and `tier.plain_key`, one line a role; the phase's distances are
`DUSK_START`, `DUSK_FULL` and `NIGHT_FULL`.

## Alternating leap

Eight ticks out and back, at most two cells at half a cell per tick, toward the
nearest in-range shadow (forward when there is none). Live bodies clip the arc
before contact. The low, stretched pose is separate from sprinting on both tiers.
A second accepted press after fourteen ticks launches the other group; the alpha
is second, and its sprite never pulls the viewport away from the path.

## The shadow's two-beat attack

A low crouch (rich lower half-block body, plain `w:`) gathers backwards
for three ticks and holds for three; its eyes are steady bright. A stretched
lunge (upper half-block body, plain `>:`) crosses toward the target over
six ticks, landing with the bite. Both use the same integer arc as the pack.
Contact clips the travel before a body; the shape stays distinct even when
the gap is short. A parry stops the bite, dims the eyes and pushes the shadow
back. Sheet row 14, columns 43 and 50 shows the two beats; `shadow-lunge`
pins every tick of the first seed-16 attack from row 600.
