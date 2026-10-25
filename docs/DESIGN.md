# Design constants

Every tuning number in pack is a named constant in `src/sim/sim.lu` or `src/world/world.lu`, mirrored here
with its meaning and the date it was last set. The numbers are the maintainer's to tune by play (campaign
ruling R-PK-7); a change here is a change there in the same commit, and the goldens move with it. The rows
marked "the maintainer's word" were set from the maintainer's play of the pk00 and pk01 builds on 2026-10-25;
the rows marked "proposed" are pk01's and pk02's first values, waiting on play.

To tune by play without rebuilding: `target/pack --debug --speed-scale N` scales every speed constant to N
percent (100 is the table), and under `--debug` the keys `-` and `=` move the pack's health by ten so the
fainting and the return can be watched. Both are refused by name without `--debug`, and a run recorded with
`--speed-scale` is noted on its closing line (the replay file does not carry the scale).

Units: positions and speeds are in `world.FP` units a cell (256), so a speed of 40 is 0.156 cells a tick.
The tick is 30 a second (`clock.TICK_HZ`), so 40 is 4.7 cells a second. Headings are in 64ths of a 45-degree
turn off the path's axis. Stamina and health are in points.

## The pack's motion (`src/sim/sim.lu`)

| constant | value | meaning | set |
|---|---|---|---|
| `TROT_V` | 40 | the trot, `v`: 0.156 cells a tick, 4.7 a second ("migrating, not running the 100 m"; pk00's 96 cut) | 2026-10-25 the maintainer's word |
| `SPRINT_V` | 72 | the sprint, 1.8 `v` (the campaign's bar): a bounded burst, clearly faster | 2026-10-25 the maintainer's word |
| `RETURN_V` | 72 | a fainted wolf's return speed, the sprint (R-pk01-3 A) | 2026-10-25 proposed |
| `FOREST_V` | 20 | the speed cap in the forest edge, `v`/2 | 2026-10-25 the maintainer's word |
| `ACCEL` | 4 | acceleration, FP units a tick each tick: the trot from a stop in 10 ticks | 2026-10-25 the maintainer's word |
| `BRAKE` | 8 | braking: a stop from the trot in 5 ticks; a wolf stops faster than it starts | 2026-10-25 the maintainer's word |
| `HEADING_MAX` | 64 | the heading's reference: 45 degrees; the small-angle split is written against it | 2026-10-25 pk00 |
| `STEER_HEADING` | 48 | the heading a held steer key turns toward, 34 degrees: enough to follow the path's steepest bend at the trot | 2026-10-25 proposed |
| `TURN_RATE` | 12 | the maximum turn rate, heading units a tick: full steer in 4 ticks, straight again in 4 (133 ms) on release; the whole of the residual motion after a release | 2026-10-25 the maintainer's word |
| `HOLD_TAP_TICKS` | 12 | a lone press is held this long (400 ms, a keyboard's initial repeat delay): a tap is a readable swerve | 2026-10-25 proposed |
| `HOLD_RATE_MAX` | 5 | a gap between presses at most this long is the autorepeat rate; longer is the initial delay or a new tap | 2026-10-25 proposed |
| `HOLD_MARGIN` | 1 | the hold outlives the last repeat by the measured interval plus this | 2026-10-25 proposed |
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
row. Health falls by the shadows' landed attacks (below), by the replay's `health` events and by the debug keys;
nothing raises it in play until pk03's deer feed the pack. At 0 the alpha is alone, and the next landed attack
ends the run.

## The shadows (`src/sim/sim.lu`; pk02)

| constant | value | meaning | set |
|---|---|---|---|
| `CHASE_V` | 52 | a shadow's chase speed, 1.3 `v` (the campaign's bar: faster than the trot, slower than the sprint, so a sprint shakes a chaser and a trot does not) | 2026-10-25 proposed |
| `STALK_V` | 20 | the speed a shadow stalks down the path toward the oncoming pack, `v`/2: its turn happens on the screen, not below it | 2026-10-25 proposed |
| `SHADOW_ACCEL`, `SHADOW_BRAKE` | 4, 8 | a shadow's acceleration and braking, the wolves' | 2026-10-25 proposed |
| `SHADOW_TURN_RATE` | 12 | a shadow's maximum turn rate, the wolves' `TURN_RATE` (R-pk02-1 A) | 2026-10-25 proposed |
| `PERCEIVE` | 8 | the perception radius, cells (the larger of the sideways and the along distance): a lurking shadow this close to a pack member turns toward it | 2026-10-25 proposed |
| `REACH` | 4 | the attack reach, cells, measured the same way: bodies three cells wide that touch are three apart centre to centre and a bump leaves them four, so a shadow on a wolf's flank is in reach | 2026-10-25 proposed |
| `FLANK` | 4 | a chasing shadow stops steering toward its target's column this close to it and rides the flank | 2026-10-25 proposed |
| `ATTACK_WINDUP` | 9 | the ticks an attack winds up before it lands (300 ms): the lunge the player reads and parries; the eyes go steady | 2026-10-25 proposed |
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
appears half a cell into the verge one row above the top of the screen and lurks, speed zero, facing down the
path. When a pack member comes within `PERCEIVE` it turns toward the nearest one: it steers to the wolf's
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
| `LEAP_REACH` | 4 | Space vanquishes every shadow within this many cells of a running wolf (the attack reach: a shadow that can bite can be leapt on) | 2026-10-25 proposed |
| `LEAP_STAMINA` | 60 | a leap's cost, a fifth of the ceiling: about five leaps, then the pant; the spent pack cannot leap (the pant refuses, nothing happens) | 2026-10-25 proposed |
| `LEAP_COOLDOWN` | 20 | the ticks between leaps | 2026-10-25 proposed |
| `LEAP_TICKS` | 6 | the lunge: the pack at the sprint, the leap posture, for this long | 2026-10-25 proposed |
| `PARRY_WINDOW` | 9 | Shift+Down or `z` turns any attack that lands within this many ticks of the press (300 ms; R-pk02-3 A: a press, never a held stance) | 2026-10-25 proposed |
| `PARRY_COOLDOWN` | 30 | the ticks between parries | 2026-10-25 proposed |
| `PARRY_PUSH`, `PARRY_RECOIL` | 3, 6 | a turned shadow loses its speed and recoils three cells away from its target over six ticks (half a cell a tick: a visible knock-back, no teleport), eyes dim | 2026-10-25 proposed |

## The death card (`src/art/art.lu`; pk02)

| constant | value | meaning | set |
|---|---|---|---|
| `CARD_COLS` x `CARD_ROWS` | 44 x 10 | the card's size, centred over the field on both tiers; the first numbers the player sees (shadows vanquished, seconds survived, the distance in cells, the score) with the offer `s saves the replay, q leaves` (R-pk02-4 A: nothing else on it) | 2026-10-25 proposed |
| the score | `shadows × 100 + seconds × 2 + distance_cells` | the campaign's formula; seconds are the death's tick over 30 | 2026-10-25 campaign |

## The world (`src/world/world.lu`)

| constant | value | meaning | set |
|---|---|---|---|
| `FP` | 256 | fixed-point units a cell | 2026-10-25 pk00 |
| `LATTICE` | 64 | rows between noise lattice points; the path bends, and the forest's density changes, over this scale | 2026-10-25 pk00 |
| the centre's swing | 3/8 of the width | with the lattice, the steepest bend stays under a cell a row, which `STEER_HEADING` can follow | 2026-10-25 pk00 |
| the half width | 1/16 to 1/8 of the width, plus (1 − density) × 1/32, never under 3 cells | the path is 10 to 20 cells wide on an 80-column field in a stand and up to 5 cells wider in a clearing | 2026-10-25 proposed |
| `DENSITY_CHANNEL` | 3 | the noise channel the density reads (1 is the centre, 2 the width) | 2026-10-25 proposed |
| `DENSITY_CLEARING` | 72 | density below this (of 256) is a clearing: grass to the verge, the odd trunk | 2026-10-25 proposed |
| `DENSITY_STAND` | 168 | density at or above this is a dense stand; between is thin woods. A stand draws the woods' foliage texture with more trunks (the trunk share up 4 points of 100): its own texture (canopy from the verge, deep forest three cells in) read as striped bands in play and was retired | 2026-10-25 the maintainer's word (the texture); the threshold proposed |
| `SPAWN_BASE`, `SPAWN_DISTANCE`, `SPAWN_DENSITY` | 2, 200, 6 | the spawn rate, in thousandths of a shadow a tick: 2 at the start, one more every 200 rows, up to 6 more in a dense stand; logged under `--trace` as `spawn`, rolled each tick against the world's hash of the tick (pk02) | 2026-10-25 proposed |

## The engine (`src/clock`, `src/term`, `src/input`)

| constant | value | meaning | set |
|---|---|---|---|
| `TICK_HZ` | 30 | the simulation's tick (R-pk00-2 A) | 2026-10-25 pk00 |
| `MIN_COLS` x `MIN_ROWS` | 80 x 24 | the smallest terminal (R-pk00-1 A, campaign R-PK-6); the field scales up, never down | 2026-10-25 pk00 |
| `ESC_TIMEOUT_MS` | 50 | a lone ESC is Esc after this long with nothing after it | 2026-10-25 pk00 |
