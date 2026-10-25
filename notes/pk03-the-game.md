# pk03 — the game (M-PK3): deer, the curve, dusk, the title, replays verified

Lane pk03 of track 19 (lair, the wolf games; the planning repo's `sprints/lair/03-the-game/pk03-the-game.md`,
adopted from pk02's draft), Fable, crawl 54, 2026-10-25. pk02 left a complete loop at `7fcdcc3`: play,
fight, die, score, a replay saved from the card. This pass makes it the game as designed: deer that feed the
pack, a difficulty curve, dusk on both tiers, a title card that keeps the best, replays loaded from the title
and verified, and the rows and goldens that pin each. No word from the maintainer's play arrived during the
lane; every new number is "proposed" in `docs/DESIGN.md` with the date (R-PK-7).

## 1. What this pass does

- **The deer** (item 1; `120c239`). `sim.Deer` with the realism bars: a position, a lateral heading turned at
  `DEER_TURN_RATE` 16, a speed moved at `DEER_ACCEL` 6 and `DEER_BRAKE` 8, a direction along the path that
  flips only at rest. Spawned from the seed's roll like the shadows (a salt apart, `world.deer_rate`), rarer,
  on the path one row above the top of the screen at a column the seed picks; at most `DEER_MAX` 3. It
  wanders at `DEER_WALK_V` 16 (0.4 v) on slow seeded noise across the path and the verge, turning back past
  the verge. A running wolf within `DEER_PERCEIVE` 10 cells puts it to flight at `FLEE_V` 60 (1.5 v: above
  the trot, below the sprint) along the path away from the nearest wolf and onto the path's centre; beyond
  16 cells it calms (`DEER_CALM` 6, a hysteresis so it does not stutter at the edge). Flight drains a stamina
  of `DEER_STAMINA` 90 a point a tick; walking returns one every `DEER_REGEN_TICKS` 3, so a deer put to flight
  again and again tires and runs at `DEER_TIRED_V` 32, below the trot, until it is back to `DEER_RECOVER` 60.
  A running wolf within `CATCH_REACH` 3 brings it down: the pack's health rises by `FEED` 25 (R-pk03-3 A)
  through the channel the bites take from, so a fainted wolf may return; the deer is gone. Deer are bodies
  for the separation rule (`sim.body` indexes wolves, shadows, deer; nothing overlaps). Drawn on both tiers:
  rich `▝▘` over `██` in a pale fawn (223), plain `YD`; the colour moved from pk00's 173 because 173 is the
  earth's own hue and the deer vanished on the path (the first thing the first frame showed). GLYPHS.md gains
  no row. `--bench-deer N` seeds the perf bench.
- **The difficulty curve** (item 2; `03399c7`). `world.spawn_rate` is now `min(1 + rows/120 + density ×
  6/256, 1 + rows/50, 12)`: one thousandth a tick at the start however dense the forest, a ramp of one more
  every 50 rows (eleven seconds), groups (above `GROUP_RATE` 5) from about row 250 (fifty seconds), the
  body of the curve reaching the ceiling of 12 at about row 850 in a stand and 1,300 in a clearing.
  `world.deer_rate` is `2 + spawn_rate/4 + (256 − density) × 3/256`: 2 to 5 at the start, 5 to 8 at the
  ceiling, more in clearings. The spawn side follows the path's bend (pk02's issue 3): a group lurks on the
  OUTSIDE of the bend between the alpha's row and the spawn row, the verge an unsteered pack drifts to; a
  straight takes the seed's coin (`sim.spawn_side`, tested on the first bending seed of forty). Probed with
  a scripted player (section 3): the shape is as the contract asked; the pair "survivable with deer and not
  without" appears at five minutes, not two (the prediction's miss).
- **Dusk** (item 3; `64e9dd8`). `sim.phase` is a function of the distance: 0 to `DUSK_START` 600 rows is the
  afternoon, 256 at `DUSK_FULL` 1200 is dusk, 512 at `NIGHT_FULL` 1800 is night, climbing by at most two a
  row. `tier.palette_at(tier, phase)` builds a `Palette` struct of fourteen colours once a frame: the rich
  tier blends `PALETTE.md`'s keyframes in RGB and quantizes to the nearest index of the 256-colour cube or
  grey ramp (`tier.nearest_index`, integer arithmetic, round-trips every index), so a role moves in a few
  small steps (the path 137, 95, 241, 59; never the keyframes' jump); the plain tier's sixteen colours step at
  the midpoints, the canopy losing its bold at dusk and the path dropping to bright black at night. The red
  eyes are fixed at every phase. Every glyph lookup takes the frame's palette (`tier.glyph_at`,
  `card_text_at`, `card_frame_at`); the afternoon forms stay for the sheet and the tests. To pin a phase in
  a golden and to tune by eye, the replay header gained `start N` (the run begins N rows up the path, the
  same forest) and the command line `--start N`: `--start 1200` is full dusk at once (R-pk03-6).
- **The title card** (item 4; `2cb8505`, `c1acb8e`, `b788513`, `a4f417a`). The game opens on the title, drawn
  over the seed's forest at its start from the card's cell model, 56 by 14: the name, `any key to run; r runs
  this seed again`, the seed, the last score (and a replay's verdict), the best in bold (score, seed, date,
  the replay's name), the last saved replay, `p plays the last saved replay; / one by name`, `q leaves`, and
  a prompt or message line. The best and the last live in `~/.pack/best` (R-pk03-1 A; `src/best`: a
  four-line text file, an absolute path for the saved replay, a file that does not parse is left alone and
  said so). After a run the title shows again: `r` keeps the seed, any other key runs the seed plus one
  (R-pk03-4 A: deterministic, no clock, `--seed` stays meaningful). The live loop was split into `play` (one
  run, the loop pk02 wrote, returning an `Outcome`) and the title loop; `q` and Esc now leave what they are
  in — a run or the death card for the title, the title for the shell — and Ctrl-C leaves from anywhere
  (R-pk03-8); `--no-title` keeps the old shape (the run at once, `q` quits) for the pty rows and the perf
  rows, which pass it. The decoder gained the title's keys (`r`, `p`, `/`) and a text mode for the prompt
  (printable bytes as character keys, Enter and Backspace, Esc the cancel); only the simulation's keys are
  applied and recorded in play, so the title's keys never reach a replay.
- **Replays loaded and verified** (item 5; `9a9fa24`, `a4f417a`). The card's `s` writes `# score N` after
  the header (R-pk03-2 A; a comment to every reader, `replay.format_scored`, `replay.score_of`). The title's
  `p` (the last saved) and `/` (a name typed) and the command line's `--replay FILE` re-run the simulation
  alone through the file's ticks (`rerun_score`, no render) and compare: `score N verified`, `UNVERIFIED: the
  file says N, the run gives M`, or `score M, the file carries none` — shown on the death card's last line
  during the replay, on the title's message line after it, and in the closing line; never silently accepted.
  A replay from the title returns to the title at its end; q leaves it early.
- **Polish from the maintainer's play** (item 6): none arrived during the lane; `DAMAGE` 10 and
  `ATTACK_COOLDOWN` 30 stand as pk02 proposed them. The record file: `--record FILE` is written by the run
  that ends on it, except that a file the card saved there is kept for the session (the title row caught a
  second run overwriting the saved, scored replay).
- **Goldens and rows** (item 7; `0daebc9`, `2f9727a`). Four new cases: `deer-flee` (seed 4, one wolf down
  from tick 5: a deer grazes down the path from tick 39, bolts at 57, tires at 146, two sprints at 374 and
  398 run it down, fed at 421 and the wolf returns), `dusk-early` (start 750), `dusk` (1200), `night` (1800).
  The five seed-16 shadow cases moved to `start 600`, where the curve is at 8 (the second minute): to the
  tick the same timeline pk02 measured at row 0 with the old rate 7 (a spawn of three at 87, perception at
  126, the first landing at 152, the flip at 173), so their frame windows and keys stand and their comments
  say "from row 600". Every pack-only golden held byte for byte: a lurker above the top of the screen is not
  drawn and no deer entered their frames. The art sheets moved for the deer's shape and gained the title on
  both tiers. 39 directories, 3.6 MB, written on nomad and byte-identical on kasumi at the first try. The pty
  rows: pk02's seven unchanged but for `--no-title`, and the new `title` row — under a `HOME` of its own
  (`target/pty/home`, so the maintainer's `~/.pack/best` is never touched by a test): the title on the first
  screen, `r`, the run to its death, `s`, `q` back to the title with the last and the best and the saved name
  shown and the best file written, `r` again the SAME seed (the trace restarting at tick 1, the closing lines
  naming seed 16 twice), `q`, `p` playing the saved replay to its verified card and back, `q` out: exit 0 and
  the restore assertions. `tools/perf` benches with a dozen shadows and three deer from `--start 900`, inside
  the dusk blend.
- **Docs**: DESIGN.md (the deer table, the curve rows, dusk, the title, `--start`), PALETTE.md (the keyframes
  as built, the quantization and its steps), REPLAY.md (`start`, `# score`, the verdicts), KEYS.md (the
  title's keys, text mode, what q leaves), ART.md (the deer, dusk, the title), GLYPHS.md (eighteen code points
  still), README (what is in this build, the title, `--start`, `--no-title`, the counts).

## 2. How it was tested

| what | where | result |
|---|---|---|
| `wolf fmt --check`; 129 unit tests on the checked machine (`tools/test`), 0 SKIP | nomad; kasumi (container, CPUs 4-7) | green both |
| both tiers built with warnings denied; `pack --selftest` on the release binary (the decoder table, now 30 rows, whole and split at every byte; the diff property) | nomad; kasumi | green both |
| the goldens: 19 cases on both tiers, the sheets and the title (39 directories, 3.6 MB), byte-identical | written on nomad (macOS arm64), compared on kasumi (Linux x86-64) | every directory ok on kasumi at the first try |
| the pty rows quit, ctrl-c, trap, agree-rich, agree-plain, held-run, card (`--no-title`) and the new title | nomad; kasumi in the container | all eight green on both |
| the perf gate with a dozen shadows and three deer at dusk (`tools/perf`) | nomad (idle a loud SKIP); kasumi | green both; section 3 |
| the plants (item 8) | three draft PRs | section 6 and the hand-back |

What the probes and rows caught that the first draft did not:

1. **A deer the earth's colour.** pk00's deer was 173 (215,135,95) on the path's 137 (175,135,95): the first
   rendered frame showed nothing where the simulation had a deer. 223, a pale fawn; PALETTE.md says why.
2. **A faint can take a leader.** The catch test placed a deer three rows ahead of wolf 0 and nothing was
   caught: `faint_one` takes the farthest wolf from the alpha, and at full formation a leader and a flanker
   tie, so wolf 0 had fainted. The test picks a running leader (a native probe, as pk02's, read the values:
   `wolf test` still drops the assert's message, wolf-lang #958).
3. **A deer never tired.** With a stamina of 150 and a regen of one a tick, a deer put to flight at 16 cells
   and calming at 10 regained on the walk what the flight cost: eleven cycles to tire, and most got away
   beyond the top. Stamina 90 and a point every three walking ticks: tired on the second cycle, run down in
   about ten seconds at the trot.
4. **Catching deer costs leaps.** The scripted player that sprinted after every tired deer lost health on
   every seed against the player that ignored them: a burst is 144 stamina, a leap 60, so each deer cost two
   leaps and the groups bit. The thrifty player (a sprint only with a wolf down and stamina over 250) did
   better with deer than without on three seeds of five. The stamina economy between deer and leaps is the
   tuning question the maintainer's play will answer first (section 5).
5. **The record file overwritten.** With the title, a second run under `--record FILE` wrote over the file
   the card had saved there (with its score); the title row's replay then played thirty ticks of nothing. A
   card-saved record file is kept for the session.
6. **`wolf fmt` moved a test before the patch**, again (pk02's finding 7): a patch to the blend test matched
   a single-line assert the formatter had wrapped, missed silently, and the old assertion stayed red until a
   line-range edit replaced it.
7. **`spawn` is a keyword**, again, now as a variable: `var spawn = -1` is E0207 "expected a pattern" and
   every later use E0201 "expected `proc` after `spawn`" — two diagnostics that do not say the word is
   reserved (pk02 met E0008 for the function name). A guide line (section 5).
8. **The one `q` too many.** The title row typed a second `q` after the replay had already returned to the
   title and the first `q` had left: an EIO on the pty, read as the row's own fault, not the game's.

The prediction (`notes/pk03-evidence/prediction.md`, commit `9ba131f`), scored:

| | predicted | measured | |
|---|---|---|---|
| 1 the deer read as prey at one glyph a cell | standing no, fleeing yes; the maintainer's first word is about the shape; I widen it to two cells | two cells wide and two tall, antlered, in a pale fawn; the stand's read is the maintainer's to judge; the colour, not the shape, was the first fault (finding 1) | hit on the widening; the shape's read is open |
| 2 the curve: a two-minute run survivable with deer and not without | the pair reachable within an hour; the probe needs a sprint per deer | at two minutes nobody dies, not even a player who misses one leap in three; the pair appears at five minutes (seed 3 alive with deer at health 5, dead without at tick 8884, the first curve; seeds 3, 7, 16 better with deer on the steeper); the sprint per deer was the finding (4) | miss on the time, hit on the shape and the sprint |
| 3 render with deer, a dozen shadows and the blend at 200x60 | within 10 percent of pk02's 247 us on kasumi, 166 on nomad; the stepping frames double the max | kasumi 215 us rich (pk02 247: −13 percent), nomad 146 (166); the max 468 against pk02's 755: the dusk frames carry fewer bytes (14,580 against 17,797), and the stepping frames did not show in the max | hit on the bound, miss on the mechanism |
| 4 new goldens | 10 directories, 41 in all; every shadow golden moves and is re-timed; the pack-only goldens move where a deer spawns; `standstill` holds | 8 directories and the title's four files, 39 in all (dusk is three cases, the title is in the sheets); every shadow golden moved and is re-timed by `start 600` to pk02's own ticks; every pack-only golden held | hit on the shadows, miss on the pack-only churn (none) and the count |
| 5 the title's re-run of a long replay | 50 to 300 ms on nomad for 9,000 ticks | 220 ms for 9,000 ticks on nomad (seed 7, a living pack), 3 ms for a run that died early; the title row's replay verified without a visible wait | hit |
| the goldens byte-identical across hosts at the first try | yes | yes, 39 of 39 on kasumi | hit |
| the pty rows pass unchanged, with a `--no-title` flag | yes | yes, seven of seven on both hosts with the flag; the eighth green on both | hit |
| the first wolf gap | none new; #950 if a row is interpolated | none new; the keyword `spawn` as a variable (finding 7) is a diagnostic's wording, not a gap | hit |

## 3. Measurements

Release binaries, mid-end off (R-pk00-5 stands). kasumi: CPUs 4-7 in the container under the shared lock
(`~/lanes/pk03/leg.sh`, check-linux then perf, each under its own `flock`; the lock was free both times);
nomad: load 2-3 with the maintainer's servers up, every build and row behind `tools/lib-mem.sh`'s gate
(never refused this lane: 15 GB free at the start).

| measurement | kasumi (Linux x86-64) | nomad (macOS arm64) | bar |
|---|---|---|---|
| render + diff, 80x24 rich, avg / p99 / max, 300 frames, five wolves, a dozen shadows, three deer, from row 900 | 38 / 71 / 92 us | 27 / 55 / 341 us | < 1 ms |
| render + diff, 80x24 plain | 36 / 58 / 65 us | 25 / 42 / 46 us | < 1 ms |
| render + diff, 200x60 rich | 215 / 404 / 468 us | 146 / 297 / 314 us | < 4 ms |
| render + diff, 200x60 plain | 215 / 366 / 377 us | 143 / 244 / 249 us | < 4 ms |
| bytes a frame, 80x24 rich / plain; 200x60 rich / plain | 1,236 / 615; 14,580 / 8,182 | the same | |
| voluntary context switches, standing, 10 s | 300 (bar 240-360) | no counter: a loud SKIP | one a tick |
| key to the frame that carries it, median / p90 / max, 20 keys | 32.3 / 33.5 / 33.6 ms | 31.9 / 33.4 / 34.3 ms | median < 40, p90 < 70 |
| the title row: the first run's score, closing lines, the best file | 47; 3; written | 47; 3; written | |
| a 9,000-tick headless re-run (seed 7, no render, the title's verification) | | 0.22 s | "instant" |
| the goldens | 39 directories, 3.6 MB, byte-identical on kasumi | | |
| the unit tests | 129 on the checked machine, 0 SKIP, both hosts | | |

The curve, by the scripted player (`notes/pk03-evidence/probe-survival.lu`: leaps at a shadow's windup,
missing one in three by the seed's hash; a sprint at a tired deer within fourteen rows only with a wolf down
and stamina over 250; no steering, no parry), five minutes (9,000 ticks), the final curve:

| seed | with deer | without deer |
|---|---|---|
| 11 (a clearing) | alive, health 35, 74 vanquished, 1 of 24 deer fed | alive, health 75, 68 vanquished |
| 7 | alive, health 90, 84 vanquished, 13 of 18 fed | alive, health 20, 69 vanquished |
| 3 | dead at 8470, 71 vanquished, 16 of 22 fed | dead at 7779, 54 vanquished |
| 5 | alive, health 85, 37 vanquished, 2 of 22 fed | alive, health 85, 37 vanquished |
| 16 (a stand) | dead at 6098, 51 vanquished, 15 of 20 fed | dead at 7589, 66 vanquished |

Deer help where the player's column meets theirs (seeds 7 and 3) and cost where the sprint spends the leaps
(seed 16: the bot's sprints, not the deer). Nobody dies before the fourth minute; the second minute's
groups cost health that the third minute's deer return. The first curve (ramp 70, distance 150) left every
seed alive at five minutes but seed 3 without deer; the steeper one proposed here bites a minute sooner.
These are a bot's numbers: the maintainer's hands decide (R-PK-7).

## 4. Rulings asked (recommended and implemented)

- **R-pk03-1 where the best lives**: (A) `~/.pack/best`. Implemented (`src/best`); the file records absolute
  paths so a replay saved in one directory plays from another; `HOME` unset is said on the title, not fatal.
- **R-pk03-2 the replay's score**: (A) the card writes `# score N`, the title verifies by a headless re-run.
  Implemented; the re-run steps the simulation to the tick the card saved at (the quit's tick), the state the
  score was read from, and the three verdicts are spelled out on the card, the title and the closing line.
- **R-pk03-3 the deer's feed**: (A) a fixed `FEED` 25. Implemented.
- **R-pk03-4 (new) the next seed**: after a run, (A) the seed plus one, `r` keeping it; (B) a seed from the
  clock. Recommended and implemented (A): no clock anywhere, the title shows the seed, `--seed` stays the
  first run's.
- **R-pk03-5 (new) the spawn side**: (A) the outside of the bend, where an unsteered pack drifts (the group
  is met); (B) the inside (the group is often missed, pk02's finding). Recommended and implemented (A);
  one hash call fewer on a bend, so the shadow goldens from row 0 would have moved for this alone.
- **R-pk03-6 (new) the dusk goldens' distance**: (A) a replay header line `start N`, with `--start N` on the
  command line, also the maintainer's knob to see a phase or the curve's second minute at once; (B) health
  events every few ticks to keep a pack alive for 11,000 ticks. Recommended and implemented (A): a header
  line is an input a frame is a function of, and a tuning knob besides.
- **R-pk03-7 (new) a continuous blend on true-colour terminals**: (A) hand a true-colour terminal the
  blended RGB itself (a cell colour encoding beyond the 256 indices, the model's inverse mapping, the goldens'
  styles); (B) the quantized index's RGB everywhere, the same on every terminal, a few small steps a phase.
  Recommended (B) for now: the steps are one cube level each and the maintainer has not seen them; (A) is a
  pk04 or later item if play wants it. Implemented (B).
- **R-pk03-8 (new) what q leaves**: (A) a run or the death card for the title, the title for the shell,
  `--no-title` keeping pk02's quit; (B) q quits from anywhere and the title has its own key. Recommended and
  implemented (A): one word, one meaning — leave what you are in; Ctrl-C leaves from anywhere.

## 5. What is next

**pk04 — PAX (M-PK4), a draft contract.**
1. **The console font row**, a px lane: `docs/GLYPHS.md`'s eighteen code points (two already in Latin-1, one
   from General Punctuation, one from Box Drawing, nine from Block Elements, one from Geometric Shapes, five
   from Braille Patterns) drawn at one cell each by PAX's console font (`kernel/screen/screen.lu`'s header
   draws `?` above U+00FF today); `pack --probe-glyphs` on PAX's console is the measurement, pasted into
   GLYPHS.md's PAX column with the date. The row is pack's specification and the lane's acceptance.
2. **The installer row** in px71: "Install the lair, the wolf games?" → `~/Games/pack/` (the binary, the
   docs, a `README`), the static Linux build the way boreutils' is (`tools/build --release` on x86-64 with the
   pinned toolchain; the binary runs unmodified on PAX as boreutils' do, M-PX3), `~/.pack/best` created on
   the first run.
3. **The equal-experience proof** via pax's screen-compare harness: the plain tier on PAX's console today,
   byte-identical in cells to the headless goldens (`tests/goldens/*-plain`); the rich tier once the font row
   lands, byte-identical to `*-rich` — the same seed, the same keys, the same cells on PAX as on macOS.
4. **Owed rows** carried from pk00: the macOS terminals' KEYS.md and GLYPHS.md measurements (the maintainer's
   runs of `tools/keyprobe` and `pack --probe-glyphs` in Terminal.app and iTerm2), and the pty `idle` row's
   macOS counter.
5. **Polish from play** as it arrives: the stamina economy between deer and leaps (finding 4), a tired deer's
   posture (head down), the parry stance, the dusk's steps (R-pk03-7 A if wanted), `DAMAGE` and
   `ATTACK_COOLDOWN`.

**How the maintainer plays it**: `cd ~/lanes/pk03/pack && tools/build --release && target/pack` opens the
title: any key runs seed 1, `--seed 4` has a deer on the path within two seconds (watch it bolt when a leader
comes within ten cells; keep after it, it tires and slows; Up to sprint and the pack eats, a fainted wolf
returning), `--seed 16 --start 600` is pk02's group of three within five seconds, `--start 1200` full dusk,
`--start 1800` the night. On the title `r` is the same seed again, `p` the last saved replay, `/` then a file
name and Enter any replay, `q` leaves; the death card's `s` saves `pack-SEED-SCORE.pk` with its score and `q`
returns to the title, where the last and the best show (kept in `~/.pack/best`). `target/pack --replay
pack-16-NNN.pk` plays a file back and says whether its score verified. `--tier plain` is PAX's view;
`--debug --speed-scale N` and the keys `-`/`=` as before; `--no-title` the old shape.

**Issues to file** (the lane files nothing):
1. wolf-lang (a guide line): `spawn` as a variable name is E0207 "expected a pattern" and E0201 "expected
   `proc` after `spawn`" at every use — neither says the word is reserved (E0008 does, for a function name).
   Witness: `notes/pk03-evidence/probe-deer-seeds.lu`'s first draft, `var spawn = -1`.
2. pack: a continuous dusk blend on true-colour terminals (R-pk03-7 A): a cell colour beyond the 256 indices,
   `grid.model`'s inverse for it, the goldens' styles; today the blend steps one cube level at a time.
3. pack: a tired deer's posture (head down, `▄▄` over the body; plain `yD`) if play wants to read the moment
   to sprint.
4. pack: the stamina economy between deer and leaps (finding 4), a tuning question for the maintainer's play:
   a cheaper sprint, a bigger feed, or a deer that is caught at the trot sooner.
5. pack: the macOS owed rows (KEYS.md, GLYPHS.md) and the pty `idle` row's macOS counter, carried from pk00.
6. pk00's, pk01's and pk02's wolf-lang issues stand (`WOLF_MIDEND=0` stays, #940; `wolf test` drops the
   assert's message, #958; the checked machine's step budget; the move out of a `List` element).

**Prune list** (nothing deleted by the lane):
- nomad: `~/lanes/pk03/probe/` (the probes, `t1`–`t5` with symlinks into the worktree, the debug scripts, the
  headless dumps), `~/lanes/pk03/pack/target/` but `target/pack` (the maintainer's binary), the plant
  worktrees under `~/lanes/pk03/plants/` after the orchestrator closes PRs #13–#15 (`git worktree remove`
  each by its exact path, then the branches), `~/lanes/pk03/*.log`, `~/lanes/pk03/split/`;
- kasumi: `~/lanes/pk03/pack/target/`, `~/lanes/pk03/leg.{sh,log,pid}`, `leg-*.exit`; the image
  `localhost/pack-ci:fbee7e864f7dbee6` (701 MB) stays while the Containerfile is unchanged. `~/lanes/pk03`
  is 419 MB on kasumi.

## 6. The plants

| branch | the break | PR | expected red |
|---|---|---|---|
| `pk03-plant-deer-flee` | `DEER_PERCEIVE` read as zero: no deer ever flees | #13 | `test_a_deer_flees_at_1_5_v_away_from_the_pack_under_the_bars`, `test_a_tired_deer_slows_below_the_trot_and_recovers_walking`; the `deer-flee` goldens behind them |
| `pk03-plant-dusk` | `sim.phase` answers the afternoon at every distance | #14 | `test_a_run_can_start_up_the_path`, `test_night_changes_the_colours_and_not_the_glyphs`; the `dusk-early`, `dusk`, `night` goldens behind them |
| `pk03-plant-title-restart` | the title's `r` advances the seed like any other key | #15 | the pty `title` row in the linux job (the second run's closing line names seed 17), after the unit tests and the goldens pass |

Each is a draft PR red in its own `tier pr` run; the run ids and first states (`queued`) were read once at
the open and the completions once more for the rows, each red in its `linux` job: #13 (run 40180596157)
`test_a_deer_flees_at_1_5_v_away_from_the_pack_under_the_bars` and
`test_a_tired_deer_slows_below_the_trot_and_recovers_walking` (127 passed, 2 failed; `check-linux` stops
at the first red step, so the goldens behind them did not run); #14 (run 40180599742)
`test_a_run_can_start_up_the_path` (128 passed, 1 failed) — and the night render test passed it, because
that test compared two places on the path and could not fail: it now asserts night's colours at one place
(`5ff3dea`, after the plants were cut, so the plant's run shows one red test, the head's test would show
two); #15 (run 40180603704) the unit tests and the goldens green, the pty `title` row red on three
assertions: the first run's closing line names seed 17, the best file records seed 17, the second run is
seed 17 again.
