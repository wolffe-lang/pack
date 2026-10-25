# Design constants

Every tuning number in pack is a named constant in `src/sim/sim.lu` or `src/trail/trail.lu` (the path and the rates over the engine's noise), mirrored here
with its meaning and the date it was last set. The numbers are the maintainer's to tune by play (campaign
ruling R-PK-7); a change here is a change there in the same commit, and the goldens move with it. The rows
marked "the maintainer's word" were set from the maintainer's play of the pk00 and pk01 builds on 2026-10-25;
the rows marked "proposed" are pk01's, pk02's and pk03's first values, waiting on play.

To tune by play without rebuilding: `target/pack --debug --speed-scale N` scales every speed constant to N
percent (100 is the table), and under `--debug` the keys `-` and `=` move the pack's health by ten so the
fainting and the return can be watched. Both are refused by name without `--debug`, and a run recorded with
`--speed-scale` is noted on its closing line (the replay file does not carry the scale). `--start N` (pk03)
begins a run N rows up the path — the same forest, the curve and the dusk read from there — so the second
minute's groups (`--start 600`), full dusk (`--start 1200`) or the night (`--start 1800`) can be seen at once;
a replay carries it as its `start` header line.

Units: positions and speeds are in `world.FP` units a cell (256), so a speed of 46 is 0.180 cells a tick.
The tick is 30 a second (`clock.TICK_HZ`), so 46 is 5.39 cells a second. Headings are in 64ths of a 45-degree
turn off the path's axis. Stamina and health are in points.

## The pack's motion (`src/sim/sim.lu`)

| constant | value | meaning | set |
|---|---|---|---|
| `TROT_V` | 46 | the trot, `v`: 5.39 cells/s; "only 15 % faster" than 40 | 2026-10-25 the maintainer's word |
| `SPRINT_V` | 83 | the sprint, rounded 1.8 `v`: "only 15 % faster" than 72 | 2026-10-25 the maintainer's word |
| `RETURN_V` | 83 | the return, matching the sprint: "only 15 % faster" than 72 | 2026-10-25 the maintainer's word |
| `FOREST_V` | 23 | the forest cap, `v`/2: "only 15 % faster" than 20 | 2026-10-25 the maintainer's word |
| `ACCEL` | 5 | integer acceleration preserving ten ticks from rest to trot at 46 (4 would take twelve) | 2026-10-25 the maintainer's word |
| `BRAKE` | 10 | integer braking preserving five ticks from trot to rest (8 would take six) | 2026-10-25 the maintainer's word |
| `HEADING_MAX` | 64 | the heading's reference: 45 degrees; the small-angle split is written against it | 2026-10-25 pk00 |
| `STEER_HEADING` | 48 | the heading a held steer key turns toward, 34 degrees: enough to follow the path's steepest bend at the trot | 2026-10-25 proposed |
| `TURN_RATE` | 12 | the maximum turn rate, heading units a tick: full steer in 4 ticks, straight again in 4 (133 ms) on release; the whole of the residual motion after a release | 2026-10-25 the maintainer's word |
| `HOLD_TAP_TICKS` (the engine's `input`) | 12 | a lone press is held this long (400 ms, a keyboard's initial repeat delay): a tap is a readable swerve | 2026-10-25 proposed |
| `HOLD_RATE_MAX` (the engine's `input`) | 5 | a gap between presses at most this long is the autorepeat rate; longer is the initial delay or a new tap | 2026-10-25 proposed |
| `HOLD_MARGIN` (the engine's `input`) | 1 | the hold outlives the last repeat by the measured interval plus this | 2026-10-25 proposed |
| `WOLF_ROW_FROM_BOTTOM` | 5 | the alpha's screen row, counted from the bottom (the alpha's eye) | 2026-10-25 pk00 |

How the steering works, in one paragraph: a terminal has no key-up, so a held key arrives as its first byte
and then the keyboard's autorepeat. The simulation holds a steer key from the ticks its bytes arrive on (so a
replay reproduces the hold): a lone press holds `HOLD_TAP_TICKS`; a repeat holds the measured interval (the
larger of the last two, since a 90 ms rate lands on alternating 2- and 3-tick gaps) plus `HOLD_MARGIN`; the
first repeat after the initial delay holds `HOLD_RATE_MAX` plus the margin. While held the heading target is
`STEER_HEADING` that way (both keys held cancel); released, it is straight. The heading moves toward the target
by at most `TURN_RATE` a tick, both ways. pk00 relaxed the target one unit a tick instead, which left the wolf
drifting sideways for two seconds after a release: the pty row `held-run` measures the new behaviour (the
hold ends within two ticks of the last byte, the pack straight and its column at rest within ten).

## The formation (`src/sim/sim.lu`; R-pk01-2 C, the maintainer's ruling)

| constant | value | meaning | set |
|---|---|---|---|
| `PACK_SIZE` | 5 | wolves in the pack; `ALPHA` = 4 is the trailing slot at the centre | 2026-10-25 campaign |
| `slot_dx`, `slot_dy` | leaders (−2, +5) (+2, +5); flankers (−5, +2) (+5, +2); alpha (0, 0) | each slot's offset from the reference point, in cells (sideways, ahead); the leaders' four-cell gap between three-cell bodies is what lets their wander meet | 2026-10-25 proposed |
| `slot_lag` | leaders 0, flankers 3, alpha 6 (`LAG_MAX`) | the ticks a slot's heading follows the steer late: the turn ripples back through the pack | 2026-10-25 proposed |
| `WANDER_X`, `WANDER_Y` | 3, 1 | the wander's amplitude around the slot in half cells either way (a cell and a half sideways, half a cell along), seeded value noise over 64 ticks | 2026-10-25 proposed |
| `PULL`, `PULL_MAX` | 16, 24 | the pull toward the slot: a wolf closes a sixteenth of its offset a tick, at most 24 FP units | 2026-10-25 proposed |
| `BODY_W`, `BODY_H` | 3, 2 | a body's footprint for the separation rule, cells (the rich sprite) | 2026-10-25 proposed |
| `BUMP` | 128 | a bump moves each wolf half a cell apart in the tick the bodies touch; never through each other | 2026-10-25 proposed |

How the formation works, in one paragraph: a reference point moves under the steer at lag zero, at the pack's
speed. Each wolf has its own heading, which turns toward the steer `slot_lag` ticks late at `TURN_RATE`, and
its own speed, which follows the pack's target (the trot, the sprint while a burst lasts, zero while stopping,
`FOREST_V` while that wolf is in the trees; the pack's own target is capped while the alpha is). It moves by
its heading's split of its speed, then the pull closes on its slot plus its wander. Then the separation rule
runs over the pairs in a fixed order, repeating while a push made a new pair touch: two bodies that overlap
are nudged `BUMP` apart each (or half the overlap if more), the left one leftward, and the share the field's
edge refuses one goes to the other. Everything is integer arithmetic on the seed, so the drift and the bumps
are the same on every machine and in every replay.

## Stamina and health (`src/sim/sim.lu`)

| constant | value | meaning | set |
|---|---|---|---|
| `STAMINA_MAX` | 300 | stamina's ceiling; one value for the pack (R-pk01-1 A) | 2026-10-25 pk00 |
| `STAMINA_TIRED` | 200 | below this the pack reads tired: ears back | 2026-10-25 proposed |
| `STAMINA_SPENT` | 100 | below this the pack reads spent: ears flat, tail low, the plain `w` | 2026-10-25 proposed |
| `SPRINT_BURST_TICKS` | 24 | a burst's length, 0.8 s (a tap starts a burst) | 2026-10-25 pk00 |
| `SPRINT_DRAIN` | 6 | stamina a sprinting tick costs: a full burst is 144 | 2026-10-25 pk00 |
| `REGEN_STAND` | 3 | stamina a standing tick returns | 2026-10-25 pk00 |
| `REGEN_TROT` | 1 | stamina a trotting tick returns | 2026-10-25 pk00 |
| `SPRINT_MIN` | 60 | stamina needed to start a burst | 2026-10-25 pk00 |
| `EXHAUST_RECOVER` | 90 | stamina that ends the pant | 2026-10-25 pk00 |
| `HEALTH_MAX` | 100 | health's ceiling; the pack's | 2026-10-25 proposed |
| `HEALTH_FLOOR` | 20 | the floors are every 20 points below the ceiling: at 80, 60, 40 and 20 one more wolf faints (the farthest from the alpha, never the alpha); at 0 the alpha is alone (pk02's card) | 2026-10-25 proposed |
| `HEALTH_HYST` | 10 | a fainted wolf returns once health is this far back above its floor (90, 70, 50, 30) | 2026-10-25 proposed |
| `HEALTH_SLOW` | 25 | the percent of the speed lost at zero health, linearly: the gait slows as the pack weakens | 2026-10-25 proposed |

A fainted wolf stops where it is and lies there; the world scrolls it off the bottom edge. When it returns it
starts from where it lies if that is still on the screen, else from one row below the bottom edge at its slot's
column, accelerates to `RETURN_V`, aims at its slot's column, and is running again once it reaches its slot's
row. Health falls by the shadows' landed attacks (below), by the replay's `health` events and by the debug keys,
and rises by `FEED` when the pack brings a deer down (pk03, the deer table). At 0 the alpha is alone, and the
next landed attack ends the run.

## The deer (`src/sim/sim.lu`; pk03)

| constant | value | meaning | set |
|---|---|---|---|
| `DEER_WALK_V` | 18 | the walk, rounded 0.4 `v`: "adjust the deer flee speed to match" | 2026-10-25 the maintainer's word |
| `FLEE_V` | 69 | flight, exactly 1.5 `v`, above trot and below sprint; "keep the wear-down mechanic" | 2026-10-25 the maintainer's word |
| `DEER_TIRED_V` | 37 | tired flight, still below trot; "keep the wear-down mechanic" | 2026-10-25 the maintainer's word |
| `DEER_ACCEL`, `DEER_BRAKE` | 6, 8 | a deer bolts (the wolves accelerate at 5) and brakes as they do | 2026-10-25 proposed |
| `DEER_TURN_RATE` | 16 | a deer's maximum turn rate, heading units a tick: a lighter animal turns quicker than a wolf's 12 | 2026-10-25 proposed |
| `DEER_PERCEIVE` | 10 | a running wolf this close (cells, the larger of sideways and along) puts a deer to flight | 2026-10-25 proposed |
| `DEER_CALM` | 6 | a fleeing deer calms once the nearest wolf is this far beyond `DEER_PERCEIVE` (so it does not stutter at the edge) | 2026-10-25 proposed |
| `DEER_STAMINA` | 90 | ticks of flight before a deer tires (three seconds) | 2026-10-25 proposed |
| `DEER_REGEN_TICKS` | 3 | a walking deer regains a point every this many ticks (flight costs one a tick): a deer put to flight again and again tires, which is how a pack at the trot runs one down | 2026-10-25 proposed |
| `DEER_RECOVER` | 60 | a tired deer flees at `FLEE_V` again once its stamina is back to this | 2026-10-25 proposed |
| `CATCH_REACH` | 3 | a running wolf this close (cells) brings a deer down: from behind, since the separation rule keeps bodies three cells apart sideways | 2026-10-25 proposed |
| `FEED` | 25 | health a deer feeds the pack (R-pk03-3 A: a fixed feed, one floor and a bit): the first thing that raises health in play | 2026-10-25 proposed |
| `DEER_MAX` | 3 | deer alive at once, at most; the spawn waits | 2026-10-25 proposed |
| `DEER_GONE_MARGIN` | 20 | a deer this many rows beyond the top of the screen has got away and is gone; behind the alpha the shadows' `GONE_ROWS` holds for it | 2026-10-25 proposed |

How a deer works, in one paragraph: each tick the world's hash of the tick (salted apart from the shadows'
roll) is rolled against `world.deer_rate`, and a deer appears on the path one row above the top of the
screen, at a column the seed picks across the path's width, facing down the path at a walk. It wanders: its
lateral heading follows slow seeded noise (turned back toward the path once it is a cell past the verge), its
direction along the path the sign of a slower channel, and a direction change is a brake to rest and a flip,
never a pivot. When a running wolf comes within `DEER_PERCEIVE` it flees: along the path away from the
nearest wolf, steering onto the path's centre, at `FLEE_V` while its stamina lasts and at `DEER_TIRED_V`
once it is spent; beyond `DEER_PERCEIVE` plus `DEER_CALM` it calms and walks, regaining a point every
`DEER_REGEN_TICKS`. A running wolf within `CATCH_REACH` brings it down: the pack's health rises by `FEED`
through the same channel the bites take from, so a fainted wolf may return, and the deer is gone. Deer are
bodies for the separation rule (nothing overlaps) and are the seed's, never a replay event. Measured on the
probe bot (the note's section 3): a deer first seen at the trot is run down in about ten seconds with one
or two sprints once it tires; a fresh deer cannot be caught by a sprint alone (the sprint closes 14 FP units
a tick for 24 ticks: a cell a burst).

## The shadows (`src/sim/sim.lu`; pk02)

| constant | value | meaning | set |
|---|---|---|---|
| `CHASE_V` | 52 | a shadow's chase speed, unchanged after the pack's increase: 52 > 46 and 52 < 83, so a sprint shakes a chaser and a trot does not | 2026-10-25 proposed |
| `STALK_V` | 20 | the original stalk speed, unchanged when the pack became faster: its turn happens on the screen, not below it | 2026-10-25 proposed |
| `SHADOW_ACCEL`, `SHADOW_BRAKE` | 4, 8 | a shadow's acceleration and braking, the wolves' | 2026-10-25 proposed |
| `SHADOW_TURN_RATE` | 12 | a shadow's maximum turn rate, the wolves' `TURN_RATE` (R-pk02-1 A) | 2026-10-25 proposed |
| `PERCEIVE` | 12 | the outer Chebyshev range on a narrow path, with a 60-degree forward half-cone; any visible wolf wakes it (8 before pk07) | 2026-10-25 the maintainer's word (pk07: "line of sight could use increasing") |
| `PERCEIVE_ACROSS` | 4 | a lurker's range at its row is the larger of `PERCEIVE` and that row's half width plus this: the field grows with the terminal (12.5–31 cells of half width at 200 columns) and a forest-edge lurker must still see a pack trotting the centre; before pk07 a 200x60 centre trot met 19% of the shadows, after it 98% | 2026-10-25 proposed (pk07) |
| `PERCEIVE_NEAR` | 3 | short all-round contact radius; beyond it, the 60-degree half-cone (`4 dot² >= norm² product`) | 2026-10-25 proposed, R-pk04-1 A |
| `SPAWN_EDGE_PERCENT`, `SPAWN_VERGE_PERCENT`, `SPAWN_SHOULDER_PERCENT`, `SPAWN_SHOULDER_CELLS` | 15, 20, 35, 3 | 15% at the forest edge (+0.5 cells outside the path), 20% inner verge (0.5 inside), 35% shoulder (3 inside), the remaining 30% in the middle of the path (`SPAWN_BAND_MID`: from the centre to half way out, by the seed), waiting on the path and scrolling into view; the five outward facings are weighted toward the oncoming pack (down, diagonally down, across twice in eight each; diagonally up and up the path once each) and a middle-band lurker always faces down the path (20/30/50 and five even facings before pk07) | 2026-10-25 the maintainer's word (pk07: "spawn in the middle/offset on the path… mix it up a bit") |
| `REACH` | 4 | the attack reach, cells, measured the same way: bodies three cells wide that touch are three apart centre to centre and a bump leaves them four, so a shadow on a wolf's flank is in reach | 2026-10-25 proposed |
| `FLANK` | 4 | a chasing shadow stops steering toward its target's column this close to it and rides the flank | 2026-10-25 proposed |
| `ATTACK_WINDUP` | 12 | 400 ms: six ticks gathering in a compressed crouch, six carrying the body toward its target; steady eyes, bite on the final tick | 2026-10-25 the maintainer's word (timing proposed) |
| `ATTACK_LUNGE_TICKS` | 6 | final half of the windup; same half-cell/tick arc as the pack, body collision clipped | 2026-10-25 proposed |
| `ATTACK_COOLDOWN` | 30 | the ticks between one shadow's attacks (one landing a second) | 2026-10-25 proposed |
| `DAMAGE` | 10 | health a landed attack costs when another shadow is in reach too (a group attack lands once per shadow in it: two landed cost one wolf; R-pk02-2 A) | 2026-10-25 proposed |
| `DAMAGE_LONE` | 5 | health a lone shadow's landed attack costs | 2026-10-25 proposed |
| `GROUP_RATE` | 5 | above this spawn rate (thousandths a tick) shadows come in groups of two or three, three rows apart on one side | 2026-10-25 proposed |
| `GONE_ROWS` | 12 | a shadow this many rows behind the alpha is gone (a sprint can shake a chase; a lurker never woken scrolls away) | 2026-10-25 proposed |
| `SHADOW_MAX` | 12 | shadows alive at once, at most; the spawn waits | 2026-10-25 proposed |
| `FLOCK_CELLS`, `COHESION`, `COHESION_MAX` | 8, 32, 8 | cohesion: a chasing shadow closes a thirty-second of its offset to the centre of the other chasers within eight cells, at most 8 FP units a tick | 2026-10-25 proposed |
| `FADE_TICKS` | 15 | a vanquished shadow's body fades (full block, dark shade, light shade) over half a second, then is gone | 2026-10-25 proposed |
| `EYE_PULSE` | 4 | the eyes alternate bright and dim every four ticks while a shadow chases (dim while it lurks or recoils, steady bright through a windup) | 2026-10-25 proposed |

How a shadow works, in one paragraph: each tick the world's hash of the tick is rolled against
`world.spawn_rate` (thousandths), so a run's spawns are the seed's and never a replay event. A shadow
spawns across the forest edge, inner verge and path shoulder (20/30/50 percent),
with one of five evenly spaced facings in the outward half-circle, never into the woods.
A lurking shadow sees inside an eight-cell range and a 60-degree forward half-cone, or hears
contact within three cells all round (R-pk04-1 A, proposed). When any living wolf is visible,
it turns toward the nearest one: it steers to the wolf's
column at the chase speed's split (the lateral heading turning at `SHADOW_TURN_RATE`, bounded by
`STEER_HEADING`) and moves along the path toward the pack at `STALK_V`. Once its target is past it, it
decelerates at `SHADOW_BRAKE`, flips its direction only when its speed has reached zero (no pivot), and
accelerates at `SHADOW_ACCEL` up the path to `CHASE_V`; in reach it matches its target's pace rather than
overshooting. The separation rule is the pack's, over every pair of bodies (wolf or shadow), so nothing ever
overlaps; a shadow in reach with its cooldown spent winds up for `ATTACK_WINDUP` ticks and lands if the
target is still in reach.

## The leap and the parry (`src/sim/sim.lu`; pk02)

| constant | value | meaning | set |
|---|---|---|---|
| `LEAP_REACH` | 2 | all-round contact reach from an active running leaper | 2026-10-25 proposed, R-pk06-1 A |
| `LEAP_REACH_AIM` | 6 | Chebyshev cell reach within an inclusive ±45-degree sector along the held aim, from an active running leaper | 2026-10-25 proposed, R-pk06-1 A |
| `LEAP_RANGE` | 6 | out-and-back presentation arc's apex in grid cells along the aim (diagonals advance each coordinate six); body collision can shorten it | 2026-10-25 proposed |
| `LEAP_STAMINA` | 60 | a leap's cost, a fifth of the ceiling: about five leaps, then the pant; the spent pack cannot leap (the pant refuses, nothing happens) | 2026-10-25 proposed |
| `LEAP_COOLDOWN` | 14 | accepted leaps alternate groups at up to 2.14/s while stamina lasts | 2026-10-25 the maintainer's word (rhythm proposed) |
| `LEAP_TICKS` | 8 | one compass-tell tick before an eight-tick six-cell arc (1.5 grid cells/tick), leaders+left flanker then right flanker+alpha; other group holds, one-tick landing mark | 2026-10-25 the maintainer's word (aim); duration/range proposed |
| `AIM_WINDOW_TICKS` | 15 | 500 ms inclusive recent-press window in addition to inferred held arrows, for last-key-only terminal autorepeat; later opposing arrow wins per axis | 2026-10-25 the maintainer's word (window proposed) |
| `leap_aim(aim_arrows(s))` | eight compass aims | Space alone/Up forward; Left/Right sideways; diagonals from recent/held arrows in either order; Down backward then resume forward | 2026-10-25 the maintainer's word |
| `PARRY_WINDOW` | 12 | Shift+Down or `z` turns a landing within 400 ms; covers the entire lunge, still a press and never a held stance | 2026-10-25 proposed |
| `PARRY_COOLDOWN` | 30 | the ticks between parries | 2026-10-25 proposed |
| `PARRY_PUSH`, `PARRY_RECOIL` | 3, 6 | a turned shadow loses its speed and recoils three cells away from its target over six ticks (half a cell a tick: a visible knock-back, no teleport), eyes dim | 2026-10-25 proposed |

## The death card (`src/art/art.lu`; pk02)

| constant | value | meaning | set |
|---|---|---|---|
| `CARD_COLS` x `CARD_ROWS` | 44 x 10 | the card's size, centred over the field on both tiers; the first numbers the player sees (shadows vanquished, seconds survived, the distance in cells, the score) with the offer `s saves the replay, q leaves` (R-pk02-4 A: nothing else on it) | 2026-10-25 proposed |
| the score | `shadows × 100 + seconds × 2 + distance_cells` | the campaign's formula; seconds are the death's tick over 30 | 2026-10-25 campaign |

## Dusk (`src/sim/sim.lu`, `src/sprites/sprites.lu`; pk03, innovation 4)

| constant | value | meaning | set |
|---|---|---|---|
| `DUSK_START` | 600 | rows of afternoon (111.3 seconds at a flat full-health trot) before the palette begins to turn | 2026-10-25 proposed |
| `DUSK_FULL` | 1200 | rows at which the palette is dusk's keyframe (222.6 seconds at a flat trot) | 2026-10-25 proposed |
| `NIGHT_FULL` | 1800 | rows at which it is night's, and holds (333.9 seconds at a flat trot) | 2026-10-25 proposed |
| `tier.PHASE_DUSK`, `tier.PHASE_NIGHT` | 256, 512 | the phase's units: `sim.phase` climbs from 0 at `DUSK_START` to 256 at `DUSK_FULL` and 512 at `NIGHT_FULL`, never by more than two a row | 2026-10-25 pk03 |

The palette's keyframes are `docs/PALETTE.md`'s; the rich tier blends them in RGB by the phase and quantizes
to the nearest index of the 256-colour cube and grey ramp, so the change comes in small steps (the path takes
three on its way to night: 137, 95, 241, 59), never the keyframes' jump; the plain tier's sixteen colours
step at the midpoints. The red eyes are the same at every phase, so shadows come with the dark. `--start
750`, `1200` and `1800` show the blend, full dusk and the night at once (the goldens `dusk-early`, `dusk`,
`night`).

## The title card (`src/art/art.lu`, `src/best/best.lu`; pk03)

| constant | value | meaning | set |
|---|---|---|---|
| `TITLE_COLS` x `TITLE_ROWS` | 56 x 14 | the title card's size, centred over the seed's forest at its start: the name, `any key to run`, the seed, the last score and the best (score, seed, date, the replay's name), the last saved replay, the keys, a prompt or message line | 2026-10-25 proposed |
| the next seed | the seed + 1 after a run; `r` keeps it | R-pk03-4 A: deterministic, no clock, `--seed` stays meaningful; the title shows the seed | 2026-10-25 proposed |
| `~/.pack/best` | one file | the best and the last score with seed, date and the replay's name, and the last saved replay's path (R-pk03-1 A) | 2026-10-25 proposed |

## The world (`src/trail/trail.lu` over the engine's `world`)

| constant | value | meaning | set |
|---|---|---|---|
| `FP` | 256 | fixed-point units a cell | 2026-10-25 pk00 |
| `LATTICE` | 64 | rows between noise lattice points; the path bends, and the forest's density changes, over this scale | 2026-10-25 pk00 |
| the centre's swing | 3/8 of the width | with the lattice, the steepest bend stays under a cell a row, which `STEER_HEADING` can follow | 2026-10-25 pk00 |
| the half width | 1/16 to 1/8 of the width, plus (1 − density) × 1/32, never under 3 cells | the path is 10 to 20 cells wide on an 80-column field in a stand and up to 5 cells wider in a clearing | 2026-10-25 proposed |
| `DENSITY_CHANNEL` | 3 | the noise channel the density reads (1 is the centre, 2 the width) | 2026-10-25 proposed |
| `DENSITY_CLEARING` | 72 | density below this (of 256) is a clearing: grass to the verge, the odd trunk | 2026-10-25 proposed |
| `DENSITY_STAND` | 168 | density at or above this is a dense stand; between is thin woods. A stand draws the woods' foliage texture with more trunks (the trunk share up 4 points of 100): its own texture (canopy from the verge, deep forest three cells in) read as striped bands in play and was retired | 2026-10-25 the maintainer's word (the texture); the threshold proposed |
| `SPAWN_BASE`, `SPAWN_DISTANCE`, `SPAWN_DENSITY` | 1, 120, 6 | the difficulty curve's body (pk03): the shadows' spawn rate in thousandths a tick, 1 at the start, one more every 120 rows, up to 6 more in a dense stand | 2026-10-25 proposed |
| `SPAWN_RAMP_BASE`, `SPAWN_RAMP_ROWS` | 1, 50 | the ramp the rate is held under from the start: 1 at row 0 however dense the forest, one more every 50 rows (eleven seconds at the trot), so groups (above `sim.GROUP_RATE` 5) come no sooner than row 250, about fifty seconds, and a clearing's later | 2026-10-25 proposed |
| `SPAWN_CEILING` | 12 | the curve's ceiling: a shadow every 2.8 s on average, in groups of two or three; reached in a stand at about row 850 (three minutes) and in a clearing at about 1,300 | 2026-10-25 proposed |
| `DEER_BASE`, `DEER_PER_SHADOW`, `DEER_CLEARING` | 2, 4, 3 | the deer's rate, thousandths a tick: a base, a quarter of the shadows' rate (so a long run is survivable with deer and not without), and up to 3 more in a clearing, where deer graze: 2 to 5 at the start, 5 to 8 at the ceiling | 2026-10-25 proposed |
| the spawn side | the outside of the bend | a group lurks on the verge an unsteered pack drifts to: the side the path's centre moves away from between the alpha's row and the spawn row (over a cell of bend); a straight takes the seed's coin (pk03, from pk02's issue) | 2026-10-25 proposed |

## The engine (lair's `clock`, `term`, `input`, pinned by `lair.pin`)

| constant | value | meaning | set |
|---|---|---|---|
| `TICK_HZ` | 30 | the simulation's tick (R-pk00-2 A) | 2026-10-25 pk00 |
| `MIN_COLS` x `MIN_ROWS` | 80 x 24 | the smallest terminal (R-pk00-1 A, campaign R-PK-6); the field scales up, never down | 2026-10-25 pk00 |
| `ESC_TIMEOUT_MS` | 50 | a lone ESC is Esc after this long with nothing after it | 2026-10-25 pk00 |

The speed change on 2026-10-25 leaves all deer wear-down timers and all shadow speeds unchanged.
Dusk distances stay 600/1200/1800 rows: at a flat full-health trot the times are
111.3/222.6/333.9 seconds, formerly 128/256/384. A 15% faster trot arrives
13.04% sooner in seconds (the informal "15% sooner" is not the reciprocal).

The arrows held or pressed within 500 ms before Space choose the leap's
compass aim; the latest opposite press wins on each axis (`docs/KEYS.md`).
This aim window compensates for last-key-only autorepeat without prolonging
the short steering Hold. Byte order breaks same-tick ties; later bytes
cannot change an already accepted aim.
The active group alone hits: at the accepted press, from its formation
positions, within six grid cells and ±45 degrees (integer dot >= absolute
cross), or within two cells all round. Fainted/returning wolves cannot hit.
The old four-cell all-round envelope from every living wolf is retired.
The visible group follows a one-tick `Leap NE`-style tell with a six-cell
out-and-back arc, clipped in eighth-cell substeps against every live body.
It never moves the camera, physical hitboxes, gait or other group. A refused
press changes neither aim nor group. R-pk06-1 A (sector/contact) and
R-pk06-2 A (ordinary cost) are recommendations, not settled rulings.
Backward has zero added trail cost relative to the same forward leap:
Down stops normally, but an accepted Space clears the stop. An existing
sprint is cancelled by Down as before; Space does not start a new sprint.

The shadow gathers back at half a cell/tick for three ticks and holds for three,
then crosses that gap in six lunge ticks. After landing it settles over six
ticks rather than snapping back. Parry keeps the existing three-cell/six-tick
recoil and dim eyes. The shadow uses `leap_arc`, the pack `leap_displacement`; the presentation-offset
choice (R-pk04-3, recommended) preserves the bite and vanquish hit envelopes.
