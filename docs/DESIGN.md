# Design constants

Every tuning number in pack is a named constant in `src/sim/sim.lu`, mirrored here with its meaning and
the date it was last set. The numbers are the maintainer's to tune by play (campaign ruling R-PK-7); a
change here is a change there in the same commit, and the goldens move with it.

Units: positions and speeds are in `world.FP` units a cell (256), so a speed of 96 is 0.375 cells a tick.
The tick is 30 a second (`clock.TICK_HZ`), so 96 is 11.25 cells a second. Headings are in 64ths of a
45-degree turn off the path's axis. Stamina is in points.

| constant | value | meaning | set |
|---|---|---|---|
| `TROT_V` | 96 | the trot, `v`: 0.375 cells a tick, 11.25 a second | 2026-10-25 pk00 |
| `SPRINT_V` | 172 | the sprint, 1.8 `v` (the campaign's bar) | 2026-10-25 pk00 |
| `FOREST_V` | 48 | the speed cap in the forest edge, `v`/2 | 2026-10-25 pk00 |
| `ACCEL` | 8 | acceleration, FP units a tick each tick: the trot is reached from a stop in 12 ticks | 2026-10-25 pk00 |
| `BRAKE` | 16 | braking: a stop from the trot in 6 ticks; a wolf stops faster than it starts | 2026-10-25 pk00 |
| `TURN_STEP` | 24 | one steering tap moves the heading target by this | 2026-10-25 pk00 |
| `HEADING_MAX` | 64 | the heading's bound, 45 degrees | 2026-10-25 pk00 |
| `TURN_RATE` | 6 | the maximum turn rate, heading units a tick | 2026-10-25 pk00 |
| `RETURN_RATE` | 1 | the heading target relaxes toward straight this much a tick, so a tap is a swerve, not a new course | 2026-10-25 pk00 |
| `STAMINA_MAX` | 300 | stamina's ceiling | 2026-10-25 pk00 |
| `SPRINT_BURST_TICKS` | 24 | a burst's length, 0.8 s (a terminal has no key-up, so a tap starts a burst) | 2026-10-25 pk00 |
| `SPRINT_DRAIN` | 6 | stamina a sprinting tick costs: a full burst is 144 | 2026-10-25 pk00 |
| `REGEN_STAND` | 3 | stamina a standing tick returns | 2026-10-25 pk00 |
| `REGEN_TROT` | 1 | stamina a trotting tick returns | 2026-10-25 pk00 |
| `SPRINT_MIN` | 60 | stamina needed to start a burst | 2026-10-25 pk00 |
| `EXHAUST_RECOVER` | 90 | stamina that ends the pant | 2026-10-25 pk00 |
| `WOLF_ROW_FROM_BOTTOM` | 5 | the wolf's screen row, counted from the bottom (the alpha's eye) | 2026-10-25 pk00 |

The world's shape (`src/world/world.lu`):

| constant | value | meaning | set |
|---|---|---|---|
| `FP` | 256 | fixed-point units a cell | 2026-10-25 pk00 |
| `LATTICE` | 64 | rows between noise lattice points; the path bends over about two seconds of trot | 2026-10-25 pk00 |
| the centre's swing | 3/8 of the width | with the lattice, the steepest bend stays under a cell a row, which a wolf at 45 degrees can follow | 2026-10-25 pk00 |
| the half width | 1/16 to 1/8 of the width, never under 3 cells | the path is 10 to 20 cells wide on an 80-column field | 2026-10-25 pk00 |

The engine (`src/clock`, `src/term`, `src/input`):

| constant | value | meaning | set |
|---|---|---|---|
| `TICK_HZ` | 30 | the simulation's tick (R-pk00-2 A) | 2026-10-25 pk00 |
| `MIN_COLS` x `MIN_ROWS` | 80 x 24 | the smallest terminal (R-pk00-1 A, campaign R-PK-6); the field scales up, never down | 2026-10-25 pk00 |
| `ESC_TIMEOUT_MS` | 50 | a lone ESC is Esc after this long with nothing after it | 2026-10-25 pk00 |

How the motion works, in one paragraph: each tick the heading target relaxes one unit toward straight and
the heading turns at most `TURN_RATE` toward the target; the speed moves toward the posture's target (the
trot, the sprint while a burst lasts, zero while stopping, the forest cap while off the path) by `ACCEL`
upward or `BRAKE` downward; then the wolf moves `speed * heading / HEADING_MAX` sideways and
`speed * (1 - heading^2 / (2 * HEADING_MAX^2))` forward, the small-angle split. Stamina drains during a
burst and returns otherwise; at zero the wolf pants and cannot burst until `EXHAUST_RECOVER`.
