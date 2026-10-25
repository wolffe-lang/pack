# pk02 — the shadows (M-PK2): a complete loop, play, fight, die, score

Lane pk02 of track 19 (lair, the wolf games; the planning repo's `sprints/lair/02-the-shadows/
pk02-the-shadows.md`, adopted from pk01's draft), Fable, crawl 54, 2026-10-25. pk01 left a pack of five
in a forest at `027ae19` with `world.spawn_rate` computed and nothing spawning; this pass makes it a fight
and a run with an end: shadow wolves that lurk, perceive, stalk, turn and chase, flock and bite; the leap
and the parry; damage into the health pk01 built; the death card and the score; the replay saved from the
card and re-run to the same card. It first landed the maintainer's word from play of pk01's build (the
forest's foliage texture), as its own commit.

## 1. What this pass does

- **The maintainer's word first** (`4b02ee7`, R-PK-7). Playing pk01's build on the rich tier, the
  maintainer saw the foliage go from the varied braille the run starts with to "horizontal stripes of
  dots" as the pack advanced into a dense stand, and ruled: keep the starting texture for the run.
  `world.forest_kind` now draws the thin woods' foliage for every density band; a stand is told by more
  trunks alone (four points of a hundred), and density keeps its other effects (the path's width, the
  spawn rate). The clearing's grass verge was not mentioned and stays. The goldens moved for the texture
  alone: `dense-stand`, `formation-turn` (seed 3 crosses a stand), `wide` (200x60 reaches a stand's rows),
  the art sheet's stand band; `clearing` did not move. ART.md and DESIGN.md say so with the date.
- **Perception and spawn** (item 1). `sim.Shadow`: position, lateral heading, speed, a direction along the
  path (`dir` +1 up the path with the pack, -1 down toward the oncoming pack), state (`LURKING`,
  `CHASING`, `ATTACKING`, `VANQUISHED`, `GONE`), the pack member it pursues, an attack's windup and
  cooldown, a parry's recoil, its fade. Each tick `sim.spawn_roll(seed, tick, rate)` rolls the world's hash
  of the tick against `world.spawn_rate` (thousandths): one shadow, or two or three once the rate passes
  `GROUP_RATE` = 5 (a second hash picks), three rows apart on one side. A shadow appears half a cell into
  the verge one row above the top of the screen (`sim.lurker`) and lurks, speed zero, eyes dim. Spawns are
  the seed's and never a replay event (REPLAY.md), so the same seed and keys meet the same shadows on every
  machine: `test_shadows_spawn_at_the_edge_ahead_from_the_seed` steps two runs of seed 16 side by side. A
  lurker whose nearest running pack member is within `PERCEIVE` = 8 cells (the larger of the sideways and
  the along distance) turns to `CHASING`. A shadow more than `GONE_ROWS` = 12 behind the alpha is gone,
  lurker or chaser: a sprint shakes a chase, and a lurker never woken scrolls away. At most `SHADOW_MAX` =
  12 alive; the spawn waits.
- **Turn rate and chase** (item 2; R-pk02-1 A). The bars are the wolves': `SHADOW_TURN_RATE` = `TURN_RATE`
  = 12, `SHADOW_ACCEL` 4, `SHADOW_BRAKE` 8. A chasing shadow steers its lateral heading toward its target's
  column at the turn rate (bounded by `STEER_HEADING`), stopping `FLANK` = 4 cells short so it rides the
  flank where the bump leaves it rather than jostling in every tick, and cuts across at the chase speed's
  split. Along the path it wants `STALK_V` = 20 (v/2) toward an oncoming pack, so its turn happens on the
  screen; `CHASE_V` = 52 (1.3 v, the campaign's bar) after a pack that passed it; its target's own pace
  once level and in reach (no overshoot). When the wanted direction differs from its own it brakes to zero
  and the direction flips only at rest: no pivot. `test_a_passed_shadow_decelerates_turns_at_rest_and_chases_at_1_3_v`
  holds the speed's change under the brake, the heading's under the turn rate, the flip at speed 4 or
  less, and the peak after it at `CHASE_V`; `test_a_sprint_shakes_a_chaser_a_trot_does_not` the campaign's
  bar. On the screen (the `spawn-chase` golden, seed 16): the shadow slides down beside the leaders,
  bites one as it passes (eyes steady), is carried below the alpha as it brakes, and climbs back up with
  its eyes now above its body — the direction change is what the eye catches, as the bump was in pk01.
- **Flocking** (item 3). Pursuit of the nearest running or returning pack member, re-chosen every tick;
  cohesion toward the centre of the other chasers within `FLOCK_CELLS` = 8 (a thirty-second of the offset
  a tick, at most 8 FP units); and separation as pk01's rule generalised over every pair of bodies —
  `sim.body(k)` indexes the five wolves then the live shadows, `separate_pass` pushes any two that overlap
  (wolf-wolf, wolf-shadow, shadow-shadow), the fainted and the fading are not bodies. `any_overlap` covers
  the mixed pairs and `test_bodies_never_overlap_with_shadows` steps three shadows through a steering pack
  on two seeds. Two shadows that spawn on one row (two single rolls a few ticks apart land on the same
  world row) are bumped side by side and move as a pair.
- **Group attack** (item 4; R-pk02-2 A). A shadow within `REACH` = 4 cells of its target with its cooldown
  spent winds up for `ATTACK_WINDUP` = 9 ticks (300 ms; its eyes go steady bright: the cue to parry) and
  lands if the target is still in reach: `DAMAGE` = 10 when another shadow is in reach too (a group attack
  lands once per shadow in it), `DAMAGE_LONE` = 5 alone, then `ATTACK_COOLDOWN` = 30. `REACH` is 4, not
  the draft's 3, because two three-cell bodies touching are three cells apart centre to centre and a bump
  leaves them four: at 3 a shadow on a wolf's flank was in reach for one tick in every bump cycle and
  never finished a windup (the first probe's finding, section 2). `LEAP_REACH` is 4 for the same reason:
  a shadow that can bite can be leapt on.
- **Leap and parry** (item 5; R-pk02-3 A). Space: if the pack is not panting, has `LEAP_STAMINA` = 60 and
  the `LEAP_COOLDOWN` = 20 is over, stamina is paid, the pack lunges at the sprint for `LEAP_TICKS` = 6
  (`POSTURE_LEAP`), and every live shadow within `LEAP_REACH` of a running wolf is vanquished: eyes out,
  the body thinning `█ ▓ ░` over `FADE_TICKS` = 15, then gone. Otherwise nothing happens, no message
  (`test_the_spent_pack_cannot_leap`). Shift+Down or `z`: if `PARRY_COOLDOWN` = 30 is over, a window of
  `PARRY_WINDOW` = 9 ticks opens; an attack landing inside it is turned — no damage, the shadow's speed
  lost and a recoil of `PARRY_PUSH` = 3 cells away from its target over `PARRY_RECOIL` = 6 ticks (half a
  cell a tick: a knock-back the eye follows, no teleport), eyes dim. A parry is a press; the window is from
  ticks, so a replay reproduces it.
- **Damage into health** (item 6). `shadows_step` returns the health the landed attacks cost; `sim.step`
  adds it to pk01's channel (`health_delta`, the replay's and debug's) and `health_step` faints and
  returns as built; the gait slows with health, and so does a chaser riding the flank, since it matches
  its target's pace. Nothing raises health in this build (deer are pk03's), so every bite is permanent.
- **The death card and score** (item 7; R-pk02-4 A). At health 0 the alpha is alone (pk01's floors: four
  down) and the next landed attack sets `dead` and `died_tick`; the simulation then stands still (the
  world, the gaits, the eyes' pulse reads the death's tick) while the tick keeps counting for the card's
  keys. `art.card` draws over the field from the same cell model on both tiers: a 44 by 10 frame of the
  half blocks and the full block (plain `-` `|`) in dim fur on the floor, ASCII text in fur — `the pack is
  gone`, shadows vanquished, seconds survived (the death's tick over 30), distance in cells, the score
  `shadows × 100 + seconds × 2 + distance_cells` — and the offer `s saves the replay, q leaves`. The text
  is Latin-1, so GLYPHS.md gains no row (`test_card_cells_need_no_font_row`); no digit is drawn in the
  field before it (`test_no_digit_in_the_field_before_the_card_and_the_card_has_them`). In the live loop
  `s` (a new decoder key, never recorded) writes the recording with a `quit` at the press's tick appended
  to `pack-SEED-SCORE.pk` in the working directory, or to `--record`'s path, and the card says `saved
  NAME; q leaves`; `q`, Esc and Ctrl-C leave; other keys are dropped. The quit (or interrupt) that ends
  any run is now recorded, so a replay ends where the run did and shows the card for as long as it was
  up. The terminal is restored on every path out (the pty rows, section 2).
- **Goldens and rows** (item 8). Five cases on seed 16 (a dense stand from row 0, the rate above
  `GROUP_RATE`: a group of three at tick 87): `spawn-chase` (frames 80-200: the group lurking above the
  top, the first turning onto the path at 126, biting the passing leader at 152, braking and turning at
  182), `group-attack` (180-260: the three on the left flank, landings at 189, 208, 236, 247, two wolves
  down), `leap-lands` (196-220 every 4: Space at 200, the lunge, two shadows fading, gone by 216),
  `parry-turns` (198-230 every 3: a windup at 199, the parry at 203, the landing at 208 turned, the
  recoil), `death-card` (200-300: health taken to zero at tick 1, the alpha alone, the card from the
  first landing at about 245). The headless runner and the cases gained `from T`, so a case's written
  frames start where its event is and the directories stay small. Every pack-only golden moved too: the
  spawn roll puts a shadow into every trotting case's first lattice of rows except `standstill`, which
  did not move (the separation rule's generalisation changes no pack-only frame). 31 directories, 3.3 MB,
  written on nomad and compared on kasumi (section 2). The pty rows: the six of pk01's unchanged and
  green on both hosts, and the new `card` row — `--seed 16 --debug --trace --record target/pty/card.pk`,
  the debug key `-` ten times, the trace's `dead 1` awaited, `s` then `q`: the restore assertions, the
  closing line naming the death and the saved file, the file parsing and ending with the quit, re-run
  headless twice to byte-identical frames, and the screen captured before `s` equal to the headless final
  frame of the saved replay, cell for cell. `tools/perf` runs the render bench with `--bench-shadows 12`
  (a dozen chasers placed around the pack from the first frame) on both tiers and sizes.
- **Docs.** DESIGN.md: three new tables (the shadows, the leap and the parry, the card), every constant
  dated "proposed"; ART.md: the shadow (eyes by state, the fade, facing), the card, the shadows in the
  game; PALETTE.md: the dim red and the card's colours; REPLAY.md: the quit recorded, the card's save, a
  spawn never an event; KEYS.md: `s`; GLYPHS.md: the card adds no row, the eighteen stand; README: what
  is in this build (the complete loop, no deer yet), the controls, the seeds, the test counts.

## 2. How it was tested

| what | where | result |
|---|---|---|
| `wolf fmt --check`; 104 unit tests on the checked machine (`tools/test`), 0 SKIP | nomad; kasumi (container, CPUs 4-7) | green both |
| both tiers built with warnings denied; `pack --selftest` on the release binary (the decoder table, now 27 rows, whole and split at every byte; the diff property) | nomad; kasumi | green both |
| the goldens, 15 cases on both tiers and the sheets (31 directories, 3.3 MB), byte-identical | written on nomad (macOS arm64), compared on kasumi (Linux x86-64) | every case ok on kasumi: byte-identical at the first try |
| the pty rows quit, ctrl-c, trap, agree-rich, agree-plain, held-run and the new card | nomad; kasumi in the container | nomad all seven green; kasumi all seven green |
| the perf gate with a dozen shadows (`tools/perf`) | nomad (idle a loud SKIP); kasumi | green nomad; kasumi green; section 3 |
| the plants (item 9) | three draft PRs | section 6 and the hand-back |

What the probes and rows caught that the first draft of the code did not:

1. **`spawn` is a keyword** (E0008): the guide's list bites; `spawn_shadows`.
2. **A reach of three cells never lands.** Two three-cell bodies touching are three cells apart and the
   bump leaves them four, so a shadow riding a flank at reach 3 was in reach for one tick in each bump
   cycle and its windup never finished: the first death probe ran 900 ticks with a shadow glued to the
   alpha's flank and nobody bitten. `REACH` 4 and `FLANK` 4 (the shadow stops steering in four cells off
   and rides where the bump left it); `LEAP_REACH` 4 to match.
3. **A lurker could never be gone.** The gone check sat inside the chasing branch; a lurker scrolled off
   the bottom and stayed in the list forever. Moved outside; `test_a_shaken_shadow_is_gone_behind_the_alpha`.
4. **A lurker's lateral speed.** With the sideways move split from the stalk speed (20) a shadow crossed
   to the path at 0.06 cells a tick and hung in the verge for seconds; it now cuts across at the chase
   speed's split (0.15 cells a tick) while stalking slowly along the path. In the goldens most ambushes
   still come from the verge, because the left flanker's column is within `FLANK` of the left verge on
   seed 16's narrow path: that is the design, not the fault.
5. **The eyes pulsed under the card.** The pulse read the live tick, which keeps counting after the death
   for the card's keys, so the "standing still" frame changed every four ticks and the pty card row could
   not compare the card with a headless frame. The drawing reads the death's tick when the run is over.
6. **A fading shadow under a live one.** The fading are not bodies, so a live shadow can cross one; drawn
   in list order the corpse's cells cut the live sprite (`▪█░░░`). The fading are drawn first.
7. **`wolf fmt` moved the test before the patch.** A test edit written against the unformatted text
   missed silently after the formatter re-wrapped a long assert; the one failing test took a native probe
   to read (finding 8). Patches now assert their match.
8. **`wolf test` drops the assert's message.** On the checked machine a failed `assert` is reported as
   `FAILED (trap(assert))` with empty stdout and stderr even under `--nocapture` and `--json`, so the
   reason a test fails is not in the output: every failing test here was diagnosed by a native probe
   program printing the same values (`notes/pk02-evidence/probes.md`). A wolf-lang issue (section 5).

The prediction (`notes/pk02-evidence/prediction.md`, commit `12930d6`), scored:

| | predicted | measured | |
|---|---|---|---|
| 1 the chase as a threat | the speed alone does not read; the turn does; the eyes need to pulse and the body a silhouette on the earth | the goldens read exactly so: a chaser climbing the bottom of the screen is a cell every twenty ticks, the turn below the alpha is the event; the eyes pulse while chasing, go dim lurking, steady winding up (built); the shadow stays drawn on the path's background | hit on the turn and the pulse; the maintainer judges the threat by play |
| 2 shadows survivable without a parry | two on leaps alone; three a fight; four cost two wolves and the run | seed 16's group of three, unanswered, puts four wolves down by tick 403 and kills about tick 450 (`probes.md`): three unanswered is a death, not a fight; two (seed 5) take one wolf by tick 420 | miss by one: the group bites harder than predicted because two in reach land `DAMAGE` each every cooldown — 20 a second; the maintainer's first tuning message is predicted to be about `DAMAGE` or the cooldown |
| 3 render with a dozen at 200x60 | within 15 percent of pk01's 235 us on kasumi; sim under the render | nomad 166 us rich (pk01 170); kasumi 247 us rich (pk01 235: +5 percent) | hit on nomad |
| 4 new goldens | 10 directories, 31 in all; every trotting case moves; `standstill` holds | 31; every case but `standstill` moved | hit |
| 5 the card's numbers first | yes by construction; the closing line stays after | yes: a test scans every pre-card frame for a digit on both tiers; the closing line prints after the restore | hit |
| the goldens byte-identical across hosts at the first try | yes | byte-identical on kasumi (every case ok) | |
| the pty rows pass unchanged | yes | yes, six for six on both hosts, and the seventh | hit |
| the first wolf gap | the step budget again; #950 on the save message | neither: the gap met was `wolf test` hiding the assert message (finding 8); no test needed more than 300 steps; the save message carries no row | miss |

## 3. Measurements

Release binaries, mid-end off (R-pk00-5 stands). kasumi: CPUs 4-7 in the container under the shared lock;
nomad: load 2-3 with the maintainer's MLX server beside the lane, builds and rows only when the memory
gate found 8 GB (refused three times, waited each time behind `~/lanes/pk02/with-gate.sh`, which polls
`vm_stat` and runs the tool only past 8.5 GB; the tool re-checks its own floor).

| measurement | kasumi (Linux x86-64) | nomad (macOS arm64) | bar |
|---|---|---|---|
| render + diff, 80x24 rich, avg / p99 / max, 300 frames, five wolves and a dozen shadows | 38 / 71 / 90 us | 26 / 53 / 405 us | < 1 ms |
| render + diff, 80x24 plain | 37 / 61 / 71 us | 24 / 44 / 46 us | < 1 ms |
| render + diff, 200x60 rich | 247 / 689 / 755 us | 166 / 320 / 336 us | < 4 ms |
| render + diff, 200x60 plain | 227 / 378 / 394 us | 158 / 263 / 272 us | < 4 ms |
| bytes a frame, 80x24 rich / plain; 200x60 rich / plain | the same | 1,126 / 603; 17,797 / 10,081 | |
| voluntary context switches, standing, 10 s | 300 (bar 240-360) | no counter: a loud SKIP | one a tick (240-360) |
| key to the frame that carries it, median / p90 / max, 20 keys | 13.4 / 33.4 / 34 ms | 33.1 / 33.4 / 34.1 ms | median < 40, p90 < 70 |
| the card row: death in the trace, events saved, the last tick | 11 events, last tick 243; re-run twice identical; the card equal | 11 events (ten `health`, the quit), last tick 242; re-run twice identical; the card equal to the replay's | |
| the goldens | 31 directories, 3.3 MB, byte-identical on kasumi (every case ok) | | |
| the unit tests | 104 on the checked machine, 0 SKIP, both hosts | | |

The bench's bytes a frame fell from pk01's (2,739 and 18,681 at rich) to 1,126 and 17,797: the dozen
chasers hold the pack's column steadier than the bench's bare scripted steer did (the bumps), so fewer path
cells change a frame, and the shadows themselves are 72 cells. The render cost with twelve shadows is within
5 percent of pk01's five wolves on kasumi (247 against 235 us at 200x60 rich) and under 4 ms by a factor of
sixteen; the simulation's cost (136 pairs a separation pass over 17 bodies, up to five passes; the
cohesion's 144 reads) is not in the render figure and the live loop's `render avg` on the latency runs was
42 to 46 us. The latency samples are the phase, as pk01 found: kasumi's land at 13 ms or one tick, nomad's
at one tick; the tick's wake was 0.6 ms late on average on kasumi and 2.3 ms on nomad (the host's load),
inside the bar's margin. The idle row holds one wake a tick with twelve shadows' worth of simulation in the
loop's budget.

## 4. Rulings asked (recommended and implemented)

- **R-pk02-1 the shadow's turn rate**: (A) the wolves' `TURN_RATE`. Implemented as `SHADOW_TURN_RATE` =
  12, its own constant so play can move one without the other; the turn in the goldens is the brake to
  rest and the flip, which the turn rate does not govern — (B) would change how quickly a chaser lines up
  with the flank, not how a passed shadow comes about.
- **R-pk02-2 damage**: (A) a fixed `DAMAGE` per landed attack, a group attack landing once per shadow in
  it; with `DAMAGE_LONE` = 5 for a lone shadow ("less effect"). Implemented; `test_group_attack_lands_damage_per_shadow_a_lone_one_less`.
  By play, section 2's prediction 2: three unanswered shadows kill in about fifteen seconds; the numbers
  to move are `DAMAGE` and `ATTACK_COOLDOWN`.
- **R-pk02-3 the parry**: (A) a window after the press, then a cooldown, with `PARRY_WINDOW` = 9 ticks.
  Implemented, with a windup of `ATTACK_WINDUP` = 9 before any landing so the window has something to
  meet and the player something to read (the eyes go steady): without the windup a bite landed the tick
  a shadow came into reach and (A) would have been (B) in practice.
- **R-pk02-4 the death card's offer**: (A) `s` saves, `q` leaves, nothing else. Implemented; Esc and
  Ctrl-C leave too (the restore's paths), every other key is dropped on the card.
- **R-pk02-5 (new) the stalk**: a perceiving shadow ahead of the pack closes at (A) the chase speed, which
  carries it below the alpha's eye before it can turn (the first design: a 52 + 40 closing speed put the
  turn off the bottom of the screen); (B) a slower stalk, `STALK_V` = v/2, so the turn is on the screen.
  Recommended and implemented (B); the number is the maintainer's.
- **R-pk02-6 (new) the quit recorded**: pk01 recorded no quit; with the card, a replay that ended at the
  last key would end before the death. (A) record the quit (and the interrupt) at its tick, and append
  one when `s` saves from the card; (B) a `dead` event. Recommended and implemented (A): the replay stays
  keys and the seed, and the file ends where the run did.

## 5. What is next

**pk03 — the game (M-PK3), a draft contract.**
1. **Deer.** `sim.Deer` with the realism bars: wander on the path and the verge at a walk, flee inside a
   perception radius at `1.5 v` (`FLEE_V` 60) along the path away from the nearest wolf, tire (a stamina
   that drains fleeing and returns walking; a tired deer slows below the trot), and feed the pack when a
   running wolf reaches one (health up by `FEED`, the deer gone; the first thing that raises health).
   Spawned from the seed's roll as the shadows are, rarer, on the path; drawn with pk00's sprite.
2. **The difficulty curve.** `world.spawn_rate` over distance is the curve today (2 + rows/200 thousandths
   plus density): tune its shape by play — a gentle first minute, groups from the second, the rate's
   ceiling — and the deer's rate against it, so a long run is survivable with deer and not without.
3. **Dusk** on both tiers: the palette takes a phase from distance (PALETTE.md's keyframes: afternoon,
   dusk, night), the red eyes unchanged so shadows come with the dark; the plain tier dims the greens and
   drops the path to bright black at night.
4. **The title card** from the card's cell model: the name, `any key to run`, the last score and the best
   (a file beside the replays), `r` to restart the same seed (R-pk02-4 B deferred here), `q` to leave.
5. **Replays loaded with `--replay`** from the title card too (a file name typed, or the last saved); a
   `.pk` carries no score, so the title re-runs it headless to read one — or the card writes a `# score N`
   comment the title reads and the re-run verifies.
6. **Polish from the maintainer's play**: the numbers in DESIGN.md's shadows tables (prediction 2 says
   `DAMAGE` and `ATTACK_COOLDOWN` first), a parry stance for the window if wanted (one `draw_wolf`
   variant), the shadows' spawn side against the path's bend.
7. **Goldens** for each (a deer fleeing and caught, dusk at three distances, the title card), the pty rows
   unchanged plus one for the title's restart, the perf gate with the deer.

**How the maintainer plays it**: `cd ~/lanes/pk02/pack && tools/build --release && target/pack --seed 16`
(a group of three within five seconds; `--seed 5` a pair at six). Hold Left or Right to turn; Up a sprint
burst; Down a stop; **Space leaps** — every shadow within reach of a wolf goes down and fades; **Shift+Down
or `z` parries** — when a shadow's eyes go steady it is winding up, and a parry in the next 300 ms turns
the bite and knocks it back. Dim eyes in the verge are a lurker; pulsing eyes a chaser. A sprint shakes a
chaser (1.3 v is slower than 1.8 v); a trot does not. When the last wolf is bitten with the alpha alone the
card comes up: `s` saves `pack-SEED-SCORE.pk` in the current directory, `q` leaves; `target/pack --replay
pack-16-NNN.pk` plays the run back to the same card. `--debug` with `-` and `=` moves health by ten (`-`
ten times puts the alpha alone at once, for the card); `--speed-scale N` scales every speed. `--tier plain`
is PAX's view.

**Issues to file** (the lane files nothing):
1. wolf-lang: `wolf test` reports a failed `assert` as `FAILED (trap(assert))` and nothing else — the
   assert's message is not printed, under `--nocapture` nor in `--json`'s `detail`/`stderr`, so a failing
   test's reason is invisible (a native `wolf run` of the same code prints it). Witness: pack at `cfbc9b6`
   with `src/sim_test.lu`'s `assert(peak_after_flip == sim.CHASE_V, "...")` made false. Ask: carry the
   message in `detail` and on stderr.
2. wolf-lang (a guide line): `spawn` is a keyword and bites as a function name (E0008 with a fix-it); the
   guide's keyword list names `spawn` but a game's vocabulary reaches for it first. No action beyond the
   line; recorded for the next reader.
3. pack: the shadows' spawn side ignores the path's bend (a group on the outside of a bend lurks in deep
   forest for longer); pk03's polish.
4. pack: the macOS owed rows (KEYS.md, GLYPHS.md) after the maintainer's runs, carried from pk00.
5. pack: the pty runner's `idle` row has no macOS counter (a loud SKIP), carried from pk00.
6. pk00's and pk01's wolf-lang issues stand (the release mid-end miscompile, `WOLF_MIDEND=0` stays; the
   `restore_at_exit` doc line; the checked machine's unnamed step budget; the move out of a `List`
   element).

**Prune list** (nothing deleted by the lane):
- nomad: `~/lanes/pk02/probe/` (the seed searches, the death probes, `t1/` the native probe program with
  symlinks into the worktree), `~/lanes/pk02/pack/target/` but `target/pack` (the maintainer's binary),
  the plant worktrees under `~/lanes/pk02/plants/` after the orchestrator closes PRs #9-#11,
  `~/lanes/pk02/*.log`, `with-gate.sh`;
- kasumi: `~/lanes/pk02/pack/target/`, the logs and markers `~/lanes/pk02/leg*.{log,exit}`,
  `baseline-linux.*`, the scripts `~/lanes/pk02/*.sh`; the image `localhost/pack-ci:fbee7e864f7dbee6`
  (701 MB) is pk01's and pk03 can reuse it while the Containerfile is unchanged. `~/lanes/pk02` is under
  1 GB on each host.

## 6. The plants

| branch | the break | PR | expected red |
|---|---|---|---|
| `pk02-plant-perception` | `PERCEIVE` read as zero: no shadow ever turns | #9 | the five shadow goldens; the perception and spawn tests |
| `pk02-plant-leap` | `LEAP_REACH` read as zero: a leap vanquishes nothing | #10 | `leap-lands`; `test_leap_vanquishes_in_reach_costs_stamina_and_fades` |
| `pk02-plant-damage` | the landed damage multiplied by zero: no bite costs health, no run ends | #11 | `death-card`, `group-attack`, `spawn-chase`; the damage and death tests; the pty `card` row |

Each went red in its `linux` job at the unit tests — `check-linux` runs the tests before the goldens and
stops at the first red step, so the goldens behind them did not run: #9 (run 40176050227)
`test_a_lurker_perceives_within_the_radius_and_not_beyond`; #10 (run 40176053918)
`test_leap_vanquishes_in_reach_costs_stamina_and_fades`; #11 (run 40176055972)
`test_group_attack_lands_damage_per_shadow_a_lone_one_less` and
`test_death_at_zero_health_on_the_next_landed_attack_freezes_the_run`. The run ids and first states
(`in_progress`) were read once at the open; the completions once more for the rows.
