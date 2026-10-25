# Design constants

Every tuning number in pack is a named constant in `src/sim/sim.lu` or `src/world/world.lu`, mirrored here
with its meaning and the date it was last set. The numbers are the maintainer's to tune by play (campaign
ruling R-PK-7); a change here is a change there in the same commit, and the goldens move with it. The rows
marked "the maintainer's word" were set from the maintainer's play of the pk00 build on 2026-10-25; the rows
marked "proposed" are pk01's first values, waiting on play.

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
row. Health moves only by the replay's `health` events and the debug keys until pk02's shadows deal damage and
pk03's deer feed the pack.

## The world (`src/world/world.lu`)

| constant | value | meaning | set |
|---|---|---|---|
| `FP` | 256 | fixed-point units a cell | 2026-10-25 pk00 |
| `LATTICE` | 64 | rows between noise lattice points; the path bends, and the forest's density changes, over this scale | 2026-10-25 pk00 |
| the centre's swing | 3/8 of the width | with the lattice, the steepest bend stays under a cell a row, which `STEER_HEADING` can follow | 2026-10-25 pk00 |
| the half width | 1/16 to 1/8 of the width, plus (1 − density) × 1/32, never under 3 cells | the path is 10 to 20 cells wide on an 80-column field in a stand and up to 5 cells wider in a clearing | 2026-10-25 proposed |
| `DENSITY_CHANNEL` | 3 | the noise channel the density reads (1 is the centre, 2 the width) | 2026-10-25 proposed |
| `DENSITY_CLEARING` | 72 | density below this (of 256) is a clearing: grass to the verge, the odd trunk | 2026-10-25 proposed |
| `DENSITY_STAND` | 168 | density at or above this is a dense stand: canopy from the verge, deep forest three cells in; between is thin woods | 2026-10-25 proposed |
| `SPAWN_BASE`, `SPAWN_DISTANCE`, `SPAWN_DENSITY` | 2, 200, 6 | the spawn-rate input pk02 reads, in thousandths of a shadow a tick: 2 at the start, one more every 200 rows, up to 6 more in a dense stand; logged under `--trace` as `spawn`, nothing spawns yet | 2026-10-25 proposed |

## The engine (`src/clock`, `src/term`, `src/input`)

| constant | value | meaning | set |
|---|---|---|---|
| `TICK_HZ` | 30 | the simulation's tick (R-pk00-2 A) | 2026-10-25 pk00 |
| `MIN_COLS` x `MIN_ROWS` | 80 x 24 | the smallest terminal (R-pk00-1 A, campaign R-PK-6); the field scales up, never down | 2026-10-25 pk00 |
| `ESC_TIMEOUT_MS` | 50 | a lone ESC is Esc after this long with nothing after it | 2026-10-25 pk00 |
