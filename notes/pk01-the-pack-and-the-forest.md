# pk01 — the pack and the forest (M-PK1): five wolves run the forest

Lane pk01 of track 19 (lair, the wolf games; the planning repo's `sprints/lair/01-the-pack-and-the-forest/
pk01-the-pack-and-the-forest.md`, adopted from pk00's draft), Fable, crawl 54, 2026-10-25. pk00 left one wolf
on a scrolling path at `76dce6ef`; this pass makes it a pack in a forest, and first answers what the
maintainer felt playing pk00's build (the orchestrator's message of 2026-10-25, the four rulings): the input
drift, the speed, the pack's motion, and what the build does not yet contain.

## 1. What this pass does

- **The latency trace and the drift** (item 1, first by the maintainer's ruling). `pack --trace` prints one
  line a tick on standard error (`trace tick T in B keys K queue Q steer S heading H x X y Y stamina S
  health H down D spawn R wall_us W`) and one line after writing a frame that carries a key (`trace frame F
  tick T carries_key inner_us U wall_us W`). Two rows read it: `tools/pty`'s `held-run` (Left as a 33 ms
  autorepeat stream for a second, then nothing; the hold must end within two ticks of the last byte and the
  pack be straight with its column at rest within ten) and `tools/perf-idle`'s latency row, which now times
  a key's write to the trace line of the frame that CARRIES it, so a frame that happened to be in flight is
  never counted (pk00's four-tick outliers were that).
  The drift's cause, measured on the unchanged model: not the queue (every key that arrived was applied in
  the one tick that consumed the list) but the steering: a tap moved the heading target by 24, autorepeat
  saturated it at 64, and the target relaxed toward straight at one unit a tick — the row's evidence line on
  pk00's model reads `last key at tick 49, peak |heading| 63, straight at 112` (63 ticks, 2.1 s, of residual
  sideways motion). The fix is a **held-key model from ticks** (`sim.Hold`): a lone press holds
  `HOLD_TAP_TICKS` = 12 (400 ms, the span of a keyboard's initial repeat delay, so a tap is a readable
  swerve); a repeat holds the measured interval (the larger of the last two, since a 90 ms rate lands on
  alternating 2- and 3-tick gaps) plus `HOLD_MARGIN` = 1; the first repeat after the initial delay holds
  `HOLD_RATE_MAX` + 1 = 6 until the rate is known. The heading target is `STEER_HEADING` = 48 while held and
  0 when not, and the heading moves at `TURN_RATE` = 12 a tick both ways; no relaxation term remains, so the
  residual motion after a release is the turn-rate decay alone (the realism bar). The same row on the new
  model: `last key at tick 50, straight at 56, column at rest at 55` (200 ms). The hold lives in the
  simulation and reads ticks, so a replay reproduces it; `.pk` files carry what the terminal sent.
- **Speed** (the maintainer: "migrating, not running the 100 m"): `TROT_V` 96 → 40 (0.156 cells a tick, 4.7
  a second), `SPRINT_V` 72 (1.8 v), `FOREST_V` 20, `ACCEL` 4, `BRAKE` 8; `pack --debug --speed-scale N`
  scales every speed to N percent for tuning by play, refused by name without `--debug`; every constant is
  in `docs/DESIGN.md` with the date and "the maintainer's word" or "proposed".
- **The pack of five** (item 2; R-pk01-2 as the maintainer ruled it, (C): slots with lag, drift, bumps,
  never overlapping). `sim.Sim` holds a reference point that moves under the steer at lag zero and five
  `Wolf`s, each with its own position, heading, speed, state, forest touch and scratches. Slots relative to
  the reference, in cells: leaders (−2, +5) (+2, +5), flankers (−5, +2) (+5, +2), the alpha (0, 0) trailing.
  Each wolf's heading follows the steer `slot_lag` ticks late (0 / 3 / 6: the turn ripples back through the
  pack, `test_the_turn_ripples_back_through_the_pack`), its speed follows the pack's target (capped at
  `FOREST_V` while that wolf is in the trees; the pack's own target is capped while the alpha is), it moves
  by its heading's split of its speed, then a bounded pull (a sixteenth of the offset a tick, at most 24 FP)
  closes on its slot plus a seeded wander (value noise over 64 ticks, a cell and a half sideways, half a
  cell along). Then the separation rule: two 3-by-2 bodies that touch are nudged `BUMP` = half a cell apart
  each (or half the overlap if more), the left one leftward, the share the field's edge refuses one going to
  the other, the pass repeating while a push made a new pair touch — so no overlap survives a tick
  (`test_bodies_never_overlap`, `sim.any_overlap`). The leaders' slots had to tighten from the draft's 3 to
  2 cells and the wander grow to a cell and a half before a bump ever happened: with the draft's numbers
  there were none in 2400 ticks. The alpha's eye anchors the screen to the alpha (`sim.world_row`,
  `screen_row`, `screen_col`); the forest edge slows and scratches each wolf that touches it. Stamina is one
  value for the pack (R-pk01-1 A); sprint and stop are pack states.
- **Health as fainting and return** (item 3; R-pk01-3 A). `HEALTH_MAX` 100 with floors every 20 (80, 60,
  40, 20): at each the farthest wolf from the alpha (never the alpha) faints, stops where it is and lies
  there (`art.draw_fainted`, under the running pack) as the world scrolls it off the bottom edge; at each
  recovery threshold (the floor + `HEALTH_HYST` 10) a fainted wolf returns: from where it lies if that is
  still on the screen, else from one row below the bottom edge at its slot's column, accelerating to
  `RETURN_V` = `SPRINT_V`, aiming at its slot's column, running again once it reaches its slot's row. The
  gait slows linearly to three quarters at zero health. Health moves only by the replay's new event `t TICK
  health N` (the goldens' channel; `docs/REPLAY.md`) and, under `--debug`, the keys `-` and `=` by ten,
  recorded as that event. There is no `--debug-health N` flag (the orchestrator's ruling on the lane's
  question): the goldens are scripts, so the event is their channel, and the keys serve the hand test.
- **The forest from the noise** (item 4). `world.density(seed, row)` is the noise's third channel (the same
  seed and lattice as the bends), banded by `DENSITY_CLEARING` 72 and `DENSITY_STAND` 168 of 256:
  `forest_kind` takes the density (a clearing is grass to the verge with the odd trunk; thin woods open near
  the path and close beyond; a stand is canopy from the verge and deep forest three cells in); the path's
  half width gains (256 − density) × width/32, so a clearing is up to 2.5 cells wider each side on an
  80-column field; `world.spawn_rate(seed, row)` = 2 + row/200 + density × 6/256 thousandths of a shadow a
  tick is the input pk02 reads, computed each tick and logged as `spawn` in the trace; nothing spawns.
- **Posture as HUD** (item 5). The rich wolf is `ear head ear` over `legs body tail`: ears by stamina band
  (fresh up `▝ ▘`, tired back `▘ ▝`, spent flat `▀ ▀`), the tail by band (fresh wags `▘ ▝` with the gait,
  tired level `▀`, spent low `▄`), the pant as before (`█`/`▓` every eight ticks), the gait by each wolf's
  own distance and slowed by health. The plain wolf is `W` with a tail cell (`,`/`'` wag, `,` level, `.`
  low), `w` spent or panting, dim in the forest edge. `docs/GLYPHS.md`'s eighteen code points are unchanged
  (`test_glyphs_doc_matches_the_tier` holds); `docs/ART.md` has the posture table and the bands.
- **Goldens and rows** (item 6). Four new cases — `formation-turn` (seed 3: Right held ticks 10–40 as an
  autorepeat every two ticks, then Left 50–80; the leaders bump at tick 16: frame 15 touching, frame 20
  nudged apart), `faint-return` (seed 7: health −25 at 30, −20 at 60, +30 at 200, +10 at 330; two faints,
  two returns), `clearing` (seed 11, density 10) and `dense-stand` (seed 16, density 252) — beside the six
  of pk00's, every one regenerated for the pack: 10 cases on 2 tiers plus the sheets, 21 directories, 1.7 MB,
  byte-identical on nomad (where they were written) and kasumi (where `tools/goldens` compared them: every
  case `ok`). The pty rows quit, ctrl-c, trap, agree-rich, agree-plain and the new held-run green on both
  hosts; `tools/perf` green on both (section 3).
- **Docs**: `docs/DESIGN.md` rewritten with every constant dated; `docs/ART.md`, `docs/REPLAY.md` (the health
  event, the hold), `docs/KEYS.md` (the debug keys, the held key); README with the build's status line (no
  shadows, no deer yet), the held steer, the knobs, the counts.

## 2. How it was tested

| what | where | result |
|---|---|---|
| `wolf fmt --check`; 83 unit tests on the checked machine (`tools/test`), 0 SKIP | kasumi (container, CPUs 0–3), nomad | green both |
| both tiers built, warnings denied; `pack --selftest` on the release binary (the decoder table, now 25 rows, whole and split at every byte; the diff property) | kasumi, nomad | green both |
| the goldens, 10 cases on both tiers and the sheets, byte-identical | written on nomad (macOS arm64), compared on kasumi (Linux x86-64) | every case ok |
| the pty rows quit, ctrl-c, trap, agree-rich, agree-plain, held-run | kasumi in the container; nomad | all six green on both |
| the perf gate (`tools/perf`: render bars, idle wake-ups, the latency to the carrying frame) | kasumi; nomad (idle a loud SKIP) | green both; section 3 |
| the drift, before and after | nomad, `held-run` on pk00's model then pk01's | red then green; the traces in `notes/pk01-evidence/trace/` |
| the plants (item 7) | three draft PRs | section 6 and the hand-back |

What the rows and probes caught that the first draft of the code did not:

1. **A struct read out of a `List` is a move.** `let w = s.wolves[i]` followed by any use of `s` is E1001
   ("`s.wolves[i]` moved here"); the spelling is `copy s.wolves[i]`, which is real on the native tier since
   0.2.35 (the guide's s165 note). A learning for the guide, not a gap.
2. **The checked machine's step budget.** Two unit tests that stepped the pack 2400 and 3000 times answered
   `unsupported (step budget exhausted)`; the tests now step 600 and 100, and the long scenarios are
   goldens, where they belong. Listed in section 5 as a question for wolf-lang (name the budget, or a flag).
3. **One separation pass is not enough.** Pairs in order: (0,1) pushed wolf 1 right, then (1,4) pushed it
   back left into 0, and `test_bodies_never_overlap` caught the survivor; the pass now repeats while a push
   made a new pair touch (at most five passes).
4. **A soft wall is not a bump.** With half the overlap as the push, the wander closed on a neighbour a few
   units a tick and the pushes were as small: invisible. The push is now at least half a cell each.
5. **The field's edge ate a push.** A wolf clamped at the field's edge could not take its half, and the pair
   stayed overlapped; the refused share now goes to the other wolf.
6. **`weak` is a keyword** (a test variable).

The prediction (`notes/pk01-evidence/prediction.md`, commit `2628e26`), scored:

| | predicted | measured | |
|---|---|---|---|
| 1 the latency outlier | the instrument's; the sound median 25–40 ms, p90 under two ticks | nomad median 9–13 ms, kasumi 23 ms; p90 33 ms on both; the samples bimodal at the key's phase against the tick | hit (the median lower than predicted: the frame is drawn right at the tick) |
| 2 the drift | not the queue; `RETURN_RATE` 1 a tick, 40–60 ticks of residual heading | the queue empty every tick; straight 63 ticks after the last byte | hit |
| 3 the lag at 30 Hz | lags of 2 and 4 read as a ripple without interpolation; the drift-and-bump carries the life | lags 0/3/6 read as a one-cell lean of the leaders against the alpha at frames 16–20 of the turn (`formation-turn`), no interpolation; the bump is what the eye catches | hit on no interpolation; the lag is the smaller half of the read, as predicted |
| 4 render at 200x60 with five | within 10 percent of pk00's 244 us on Linux; the density under 5 percent | kasumi 235 us rich (pk00's hasu 244), nomad 170 (pk00 207): faster, since the slower trot changes fewer cells a frame | hit |
| 5 new goldens | 7 cases, 15 directories; every existing golden moves | 10 cases (the six kept and four added), 21 directories; every existing golden moved | miss on the count (I had the old cases replaced; keeping them costs nothing and keeps pk00's rows); hit on the churn |
| 6 the density on the plain tier | a clearing reads; a stand against woods by trunks and the path's width | both read on the plain goldens (`clearing-plain`: grass to the verge, the path 16 wide; `dense-stand-plain`: canopy, dark cells, the path narrow) | hit |
| byte-identical goldens at the first try | yes | yes (kasumi compared nomad's) | hit |
| the pty rows pass unchanged | yes | yes, six for six on both hosts | hit |
| the first wolf gap: the checked machine on a larger struct graph | a modelling gap | the step budget on long loops, and the move-out-of-a-list rule | partly: the checked machine, not its modelling |

## 3. Measurements

Release binaries, mid-end off (R-pk00-5 stands). kasumi: CPUs 0–3 in the container under the shared lock;
nomad: load 3–6 with the maintainer's server beside the lane, builds and rows only when the memory gate
found 8 GB (refused four times, waited each time).

| measurement | kasumi (Linux x86-64) | nomad (macOS arm64) | bar |
|---|---|---|---|
| render + diff, 80x24 rich, avg / p99 / max, 300 frames, five wolves | 38 / 69 / 88 us | 27 / 54 / 61 us | < 1 ms |
| render + diff, 80x24 plain | 37 / 65 / 75 us | 25 / 46 / 49 us | < 1 ms |
| render + diff, 200x60 rich | 235 / 422 / 477 us | 170 / 326 / 340 us | < 4 ms |
| render + diff, 200x60 plain | 231 / 377 / 414 us | 163 / 276 / 324 us | < 4 ms |
| bytes a frame, 80x24 rich / plain; 200x60 rich / plain | 2,739 / 1,505; 18,681 / 10,639 | the same | |
| voluntary context switches, standing, 10 s | 300 (bar 240–360) | no counter: a loud SKIP | one a tick |
| key to the frame that carries it, median / p90 / max, 20 keys | 23.4 / 33.4 / 33.8 ms | 12.6 / 33.4 / 34.5 ms (and 9.2 / 33.1 / 33.4 on the first run) | median < 40, p90 < 70 (R-pk00-6) |
| the same, the loop's own share (`inner_us`) | equal to the wall figure within a millisecond | equal | |
| the held run: last byte → the hold ends → straight → the column at rest | 55 → 57 → 60 → 59 (ticks) | 50 → 52 → 56 → 55; pk00's model 49 → — → 112 → 110 | stops turning within 2, straight within 10 |
| the goldens | 21 directories, 1.7 MB, byte-identical across the hosts | | |
| the unit tests | 83 on the checked machine, 0 SKIP | | |

**The latency, soundly.** The samples are bimodal: about 9 ms or exactly one tick on nomad, 23 ms or one tick
on kasumi. A key lands at a fixed phase against the tick (the runner's 300 ms cadence is nine ticks), and the
frame that carries it is drawn at the next tick: the figure is the phase, not a cost. The loop's own share
equals the wall figure, so the pty adds nothing measurable. The bar is met on both hosts and the perf row is
green; pk00's p90 of four ticks was the first-byte measurement counting frames in flight.

**The ripple's read.** At the trot the pack moves sideways 0.12 cells a tick under full steer, so six ticks of
lag between the leaders and the alpha is under a cell of lateral offset: in the `formation-turn` golden it
shows as the leaders a column to the right of where the flankers and alpha still are (frames 16–20) and then
the rest following. It is a lean, not a wave; the bump and the wander are what make the pack read as five
animals rather than a sprite. Longer lags (say 0/5/10) would read more and cost nothing; the maintainer's
call by play, the constants are `slot_lag`.

## 4. Rulings asked (recommended and implemented)

- **R-pk01-1 stamina**: (A) one pack stamina. Implemented: `Sim.stamina`, the bands `BAND_FRESH/TIRED/SPENT`
  read by every wolf's ears and tail; an exhausted pack pants together (the campaign's sentence). How (B)
  would read: `art.draw_wolf` takes the band per call and `sim.band` is one function of the pack, so a
  per-wolf stamina is a `stamina` field on `Wolf`, `band(s, i)`, and the pace set by the slowest — the
  posture would show individual tails dropping and one wolf panting while the others trot. The plumbing is
  there if the maintainer wants it; not recommended for pk01 (the pack is steered as one, so its stamina is
  one thing to read).
- **R-pk01-2 the formation under a turn**: ruled (C) by the maintainer: slots with per-slot lag as the
  targets, each wolf drifting around its slot on seeded wander, a separation rule that bumps bodies apart
  and never lets them overlap. Implemented as section 1 describes; deterministic from the seed
  (`test_two_runs_are_one` over 300 ticks with keys and health events); the formation golden shows a bump.
- **R-pk01-3 the fainted wolf's return speed**: (A) `SPRINT_V`. Implemented as `RETURN_V` = 72, its own
  constant so play can move it without moving the sprint; the return from the bottom edge to a leader's slot
  takes about 80 ticks (2.7 s) at the trot, visible in `faint-return` frames 240 and 280.
- **R-pk01-4 (new) the drift's fix**: the held-key model from ticks with the heading returning at the turn
  rate, as the orchestrator's message specified; the alternative (a steer that holds its course until
  steered back) would send the pack into the trees on every bend. Implemented; the maintainer's numbers are
  `HOLD_TAP_TICKS`, `HOLD_RATE_MAX`, `HOLD_MARGIN`, `STEER_HEADING`, `TURN_RATE`.
- **R-pk01-5 (new) `--debug-health`**: the replay event and the debug keys, no flag (the orchestrator,
  2026-10-25). Implemented.

## 5. What is next

**pk02 — the shadows (M-PK2), a draft contract.**
1. **Perception and spawn.** `sim.Shadow` with position, heading, speed, state (lurking, chasing, attacking,
   vanquished); spawned from the forest edge at the rate `world.spawn_rate` gives (the trace's `spawn`,
   thousandths a tick, rolled on the world's hash of the tick so it is the seed's), alone and, once the
   rate passes a threshold, in groups; a perception radius in cells inside which a shadow turns toward the
   nearest pack member.
2. **Turn rate and chase.** A shadow has the wolves' realism bars (`TURN_RATE`, acceleration, a maximum
   turn rate); chase at `1.3 v` (52 at today's trot); a passed shadow decelerates, turns at its turn rate
   and chases — the lag model makes the turn visible.
3. **Flocking.** Separation, cohesion and pursuit of the nearest pack member over the shadows in reach; the
   separation rule from `sim.separate` generalised to any two bodies (a pack wolf and a shadow bump too).
4. **Group attack.** Two or more shadows within reach attack together; the reach and the cooldown are
   `docs/DESIGN.md` numbers.
5. **Leap and parry.** Space leaps the pack together at a reach and a cooldown (stamina-bounded, the pant
   refuses); Shift+Down or `z` parries within a window; a leap on a shadow in reach vanquishes it (red eyes
   out, the body fades over a few ticks); a parry turns an attack.
6. **Damage into health.** An attack that lands costs health through the channel item 3 built
   (`sim.step`'s `health_delta`, now the shadows' as well as the replay's); the faint and return follow.
7. **The death card and score.** At health 0 the alpha is alone and the next attack ends the run: a card
   (the first numbers the player sees: shadows × 100 + seconds × 2 + distance cells) with the offer to save
   the replay (`--record`'s path or a prompt); `q` leaves.
8. **Goldens**: a shadow's spawn and chase, a group attack, a leap that lands, a parry, a death; the pty rows
   unchanged; the perf gate with a dozen shadows at 200x60.

**Owed to the maintainer's run on this Mac** (unchanged from pk00; the lane cannot drive a GUI terminal
under RULES section 4): `pack --probe-glyphs` and `tools/keyprobe` in Terminal.app and iTerm2, pasted into
`docs/GLYPHS.md` and `docs/KEYS.md` with the date.

**How the maintainer plays it**: `cd ~/lanes/pk01/pack && target/pack` (the release tier built at the final
head by `tools/build --release`; `q` quits). Hold Left or Right to turn, release to straighten; Up a sprint
burst, Down a stop. `--seed 3` shows the bump in a right turn, `--seed 11` starts in a clearing, `--seed 16` in
a dense stand. `target/pack --debug --speed-scale 150` for every speed at 150 percent (any N); under `--debug`
the keys `-` and `=` move health by ten: at 80 the farthest wolf faints and falls behind, at 90 it sprints
back from the bottom. `--tier plain` is PAX's view; `--record run.pk` keeps the run; `--trace 2>trace.txt`
logs a line a tick.

**Issues to file** (the lane files nothing):
1. wolf-lang: `wolf test` on the checked machine answers `unsupported (step budget exhausted)` for a test
   that steps a five-wolf simulation 2400 times; the budget is not named in the output or the docs, and
   there is no flag to raise it per test. Witness: pack at `343a107^`'s `test_bodies_never_overlap` (4 seeds
   × 600 steps) under `tools/test`. Ask: name the budget in the message, or take `--step-budget N`.
2. wolf-lang (a guide line, not a bug): `let w = xs[i]` with `xs: List[Struct]` moves the element out and
   makes `xs` unusable (E1001); the fix-it says `copy`. The guide's Modes section should say so beside the
   `take`/`read` rules; pack's sim and art spell `copy` at every such read.
3. pack: the macOS owed rows (KEYS.md, GLYPHS.md) after the maintainer's runs (carried from pk00).
4. pack: the pty runner's `idle` row has no macOS counter (a loud SKIP; carried from pk00).
5. pack: the per-wolf stamina (R-pk01-1 B) if the maintainer wants individual tails; the plumbing in
   section 4.
6. pk00's wolf-lang issues stand (the release mid-end miscompile of the key path, `WOLF_MIDEND=0` stays;
   the `restore_at_exit` doc line).

**Prune list** (nothing deleted by the lane):
- nomad: `~/lanes/pk01/probe/`, `probe2/`, `probe3/` (the move/overlap/seed probes; symlinks into the
  worktree), `~/lanes/pk01/pack/target/` but `target/pack` (the maintainer's binary), the plant worktrees
  under `~/lanes/pk01/plants/` after the orchestrator closes the plant PRs;
- kasumi: `~/lanes/pk01/pack/target/`, the logs `~/lanes/pk01/*.log` and markers, the scripts
  `~/lanes/pk01/*.sh`; the image `localhost/pack-ci:fbee7e864f7dbee6` (701 MB; pk02 can reuse it, the tag is
  the Containerfile's hash). `~/lanes/pk01` is under 1 GB on each host.
