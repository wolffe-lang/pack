# pk02 — the native probes (what `wolf test` would not say)

`wolf test` on the checked machine reports a failed assert as `FAILED (trap(assert))` and drops the
message (section 2's finding 8, the wolf-lang issue to file), so every behaviour below was read from a
native probe program: `~/lanes/pk02/probe/t1/main.lu` with `sim` and `world` symlinked in from the
worktree, run with `wolf run`, printing one line per shadow state change and per landed attack. The
checked machine and the native tier agreed on every number (`wolf conform-run --checked` on the chase
probe gave the same line). Ticks; `dy_rows`/`dx_cells` are the shadow's offset from the alpha.

## Seed 5 (a quieter start: a pair at about six seconds), the natural run

```
t 166 shadow 0 spawns  lurking  dy 19 dx -11      (a single roll)
t 167 shadow 1 spawns  lurking  dy 18 dx -9       (a second single roll: same world row, bumped beside)
t 223 both perceive (the left flanker within 8) -> chasing, stalking down at STALK_V
t 242 shadow 1 winds up on the passing flanker (dir -1, speed 20)
t 251 LANDED 1  health 95  (alone: DAMAGE_LONE)
t 281 shadow 1, turned (dir 1), level with the alpha, winds up again
t 290 LANDED 2  health 90
t 329 LANDED 3  health 85
t 364-373 both in reach: LANDED 4, 5  health 75, 65  (DAMAGE each; one wolf down at 80)
t 407-412 LANDED 6, 7  health 55, 45  (two down)
t 446     LANDED 8     health 40      (three down)
t 472     LANDED 9     health 30
end 480: spawned 2, landed 9, health 30, 3 down, alive
```

## Seed 16 (a dense stand from row 0: the rate above GROUP_RATE), the natural run

```
t 87  shadows 0,1,2 spawn as a group, left verge, rows 19/22/25 ahead, dx -6/-5/-4
t 126 shadow 0 perceives (a leader within 8) -> chasing
t 136 shadows 3,4,5 spawn as a group, right verge, 19/22/25 ahead
t 143 shadow 0 winds up on the passing leader (dir -1, speed 20)
t 152 LANDED 1  health 95
t 160/169 shadow 1 winds up, LANDED 2  health 85
t 182 shadow 0 turned (dir 1, speed 4) level with the alpha; windup interrupted by a bump, resumed
t 189 LANDED 3  health 75  (one wolf down)
t 199 shadow 1 winds up (the parry golden presses at 203)
t 208 LANDED 4  health 70
t 236 LANDED 5  health 60  (two down)
t 247 LANDED 6  health 55
t 274 shadows 6,7 spawn (a pair, right)
t 286 LANDED 7  health 50
t 304 LANDED 8  health 40  (three down)
t 325 LANDED 9  health 35
t 364 LANDED 10 health 30
t 399 LANDED 11 health 25
t 403 LANDED 12 health 20  (four down: the alpha alone)
end 420: spawned 10, landed 12, health 20, 4 down, alive  (the death follows at about 450)
```

With health taken to zero at tick 1 (the `death-card` case) the four wolves faint at ticks 1-4, the
lurkers see only the alpha, and the first landing — the death — comes at about tick 245 (the card is in
frame 250; the pty `card` row's runs recorded their quit at ticks 242 and 244).

## The chase test's values (native and checked agree)

A shadow placed one row behind the alpha and five cells right, stalking at 20, dir -1, 200 ticks:

```
max_ds 8  max_dh 0  flipped_at 2  speed_at_flip 4  peak 52  dir 1  speed 37  state 1  health 75
```

The speed never changes by more than SHADOW_BRAKE (8) a tick, the heading never by more than
SHADOW_TURN_RATE (0 here: the target's column was within FLANK), the direction flipped at tick 2 with the
speed at 4 (at rest within one brake step), the chase reached CHASE_V (52) after the flip, and in reach it
settled to the pack's own slowed pace (37 at health 75).

## The first death probe (seed 7, health -100 at tick 1, REACH 3)

900 ticks: the first shadow spawned at tick 720 and glued itself to the alpha's flank at 3 cells, bumped to
4, steered back, bumped again — in reach one tick in each cycle, the windup never finishing, nobody bitten.
`REACH` 4 and `FLANK` 4 (section 2, finding 2); the death then came within 15 ticks of contact.
