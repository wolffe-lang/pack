# pk09 — the aim window: pack's macOS nightly

pack's scheduled `ci` was red every night from 2026-10-26 (pack#44), always on the macOS arm64 job's pty row
`aim-window`. **The fault was the row's in every case measured.** It scheduled its key events by wall-clock sleeps and
judged the game's answer against the milliseconds it meant, while the game answers the ticks it applied the bytes on,
and a busy runner moves those. The game's aim matched its own documented rule in all 2,922 sessions checked on the Mac,
under trunk's row and under the fixed one, loaded and unloaded (`before/`, `calibration/`, `proof-mac*/`, `stress/`). The row is now paced by the game's own trace
ticks and judged on the applied ticks, as cub's cb11/cb11b rows are. No game, engine, pin, CI, case or golden byte
moved, and the maintainer's feel of the aim is unchanged in every case.

## Before / after

**The six nightly lines** (run 41194811528, `notes/pk09-evidence/nightly-41194811528.txt`; the contract quotes five), by
cause:

| nightly line | what the game applied | verdict |
|---|---|---|
| `rich up>right 400ms … Space=40 up_at=24 aim=1,0` | Up's last press 16 ticks before Space | the row: one tick past the 15-tick window the game documents |
| `rich down>left 400ms … Space=40 down_at=24 aim=-1,0` | 16 ticks | the row, the same |
| `rich left>down 400ms … Space=40 left_at=24 aim=0,-1` | 16 ticks | the row, the same |
| `plain left>up 400ms actual=405ms … Space=41 left_at=25 aim=0,1` | 16 ticks, with `actual` only 405 ms | the row: its `actual` omits the 50 ms settle after the first arrow's last byte |
| `rich up>right 200ms … Space=33 right_at=31 held=0 aim=1,1` | Right's last press 2 ticks before Space; its Hold had ended | the row: the fixture refusing its own setup; the aim is right |
| `plain right>up 200ms … Space=34 up_at=31 held=0 aim=1,1` | 3 ticks; the Hold had ended | the row, the same; the aim is right |

**Why the fixture refused its own setup.** Its `fixture Hold set is not the last key alone` line asserts that the raw
Hold at Space holds the second arrow alone. The row wrote the second arrow's last repeat at `delay − 50 ms` and slept to
`delay` before Space, so Space trailed the last repeat by a whole repeat interval plus the writer's lateness (64 and 82
ms that night) where a keyboard would have sent one more repeat. The engine's Hold lasts one measured repeat interval
plus a tick after the last press; two repeats applied on consecutive ticks measure a 1-tick rate, so the Hold was over 2
ticks after the last byte and the raw Hold at Space was empty. Under the forced stall a third form appears: the first
arrow's repeats stretched past 5 ticks read as a fresh delay, so the first arrow is still held at Space (`held=6`). The
aim was the diagonal every time.

**Measured on the Mac** (trunk's row and binary, 58 sessions a run, every write timestamped by
`notes/pk09-evidence/measure.py`, which also applies the documented rule to the ticks in the trace; `before/`):

| condition | trunk's row | tick lateness, per-session max (median / max) | 400 ms diagonals: written gap, first arrow → Space | applied gap | the game against its rule |
|---|---|---|---|---|---|
| unloaded | green | 3.0 / 3.0 ms | 461–478 ms | 14–15 ticks (12 of 16 on the window's last tick) | 58 of 58 agree |
| background clamp alone | red, 6 lines | 2.0 / 222.8 ms | 464–508 ms | 13–16 | 58 of 58 agree |
| background clamp + 12 busy processes | red, 10 lines | 86.6 / 337.8 ms | 450–505 ms | 11–16 | 58 of 58 agree |

Unloaded, trunk's 400 ms cases already land on the window's last tick: the nominal gap from the first arrow's last byte
to Space is the unmeasured 50 ms settle plus the 400 ms delay, 13.5 ticks against 15, and the pump's own overshoot
spends the rest. Under a stall a further class appears, `accepted Space rows []`: the row read the trace 120 ms after
Space (a wall-clock settle) before a stalled game had printed the tell.

The stall moves the applied gap two ways. The writer's lateness lengthens the written gap. And a byte read on a late wake
is applied on the earliest tick then due (lair's clock steps every due tick at once, the keys on the first), so a stall
can stamp the first arrow's last byte earlier than it arrived and lengthen the applied gap with no writer lateness at
all: `plain left>down`, written 480 ms apart, applied 16 ticks apart (`before/bg12`). That is the engine's documented
clock, bounded by the stall, not the aim model (R-pk09-2).

**The fix** (`tests/pty_rows.py`, `row_aim_window` and the block above it). Every byte is written once the game's
`--trace` shows the tick before its target, alone, and acknowledged by the first later trace line that applied a key; that
step is the byte's applied tick, and the sim's own record (`<arrow>_at`) must agree with it. The schedule is in ticks: the
first arrow at once, again 8 ticks later (the keyboard's delay), then every 2 ticks four times; the second from the next
tick, every 2 ticks; Space 6, 9 or 12 ticks after the second starts (the old 200, 300 and 400 ms). An oracle written from
the documented rule (the 15-tick window, the engine's Hold, opposing arrows to the later press, the leap's stamina and
pant) predicts the raw Hold and the aim from the acknowledged ticks and must equal the game's in every session. A late
byte is input, never a verdict. A session a stall pushed out of its case (the first arrow still held, past the window, or
the pack sprinted too tired to leap) is driven again in a fresh session, up to four, every re-drive printed; a case never
realised is a SCHEDULE failure; no re-drive forgives a disagreement. The oracle's 34 controls run before the first session
and alone as `python3 -I tests/pty_rows.py`.

**After: the proof under the forced stall** (the game, the row and one competing busy process in macOS's background QoS
clamp, `notes/pk09-evidence/stall.py`; runs interleaved trunk, head, trunk, head …, each its own locked run;
`proof-mac/`, tabulated by `summarise-proof.py`):

| row | runs | verdict | red lines, by class | sessions | the game against the rule |
|---|---|---|---|---|---|
| trunk's (`2784809`) | 20, then 1 more | **20 of 20 red**, and the extra run red (5 Hold lines): 21 of 21 | `fixture Hold set` 74, `expected=` 12, `accepted Space rows []` 6 | 1154 | 0 of 1154 disagree (its aim against the window on the ticks it reported) |
| the head's (`dded677`) | 20, one voided (below), then 1 more | **19 of 19 green**, and the extra run green: **20 of 20 with a verdict** | none | 1104 in the 19: 1102 realised at once, 2 re-driven (once the pack too tired to leap, once the first arrow 38 ticks back); 58 more in the extra run, none re-driven | 0 of 1104 disagree (raw Hold and aim) |

The stall reached the head's row too: 413 ticks of late delivery over the 19 runs (per session: 840 on time, 210 one
tick late, 46 two, 6 between three and seven, and two sessions 30 and 57 ticks late in all), every one input, not a
verdict. Past the proof's stall (`stress.sh`, `stress/`): with the proof's one busy process every pty row is green
(quit, ctrl-c, trap, both agree rows, held-run, card, title, directional-chords, aim-window). With 12 busy processes the
row's own process is starved for seconds (2033 ticks of late delivery in one run, 34 re-drives: 20 for a pack the
stretched Up stream sprinted to exhaustion, 14 for a first arrow pushed past the window), and 8 of the 58 cases, all
with Up, were never realised in four sessions: the row is red there, by `SCHEDULE`, never by a false aim verdict
(R-pk09-6).

**The plant** `pk09-plant-aim` (`9781521`: this branch at `8d5ba18` plus an `aim_arrows` that keeps the arrow pressed
first and drops the second), run locally on nomad (`plant-run.sh`, `plant-aim.log`): the unit tests `171 passed; 4
failed`, among them `test_pk06b_timing_table_diagonals_in_both_orders_cardinals_and_default`; the `aim-window` row red
unstalled and under the stall alike, all 48 diagonal sessions each time, every cardinal and the default green, by name:
`rich up>right delay=6: the game aims 0,1 where the rule on the applied ticks gives 1,1`.

## Prediction

Committed before the first measurement and the first change: `1935cca`, `notes/pk09-evidence/prediction.md`. Scored:

- The four `expected=` lines are the row's, one tick outside the window: **hit** (16 ticks each; the game applied its
  rule).
- "Every such red, measured, has a written gap above 500 ms": **missed in part.** I predicted a game-side stall could
  only stamp a byte earlier and so only shorten gaps; stamping the first arrow's byte earlier lengthens the gap. One of
  the three measured `expected=` reds (`before/bg12`, `plain left>down`) was written 480 ms apart and applied 16 ticks
  apart. Corrected above.
- The two Hold lines are the fixture's, with the aim right: **hit**, the mechanism (a 1-tick measured rate, the Hold
  over 2 ticks after the last byte) confirmed in the trace; a third form (the first arrow still held) found under the
  stall.
- No aim fault: **hit**, 0 disagreements in every session measured.
- The design question raised as R-pk09-1, not acted on: **as predicted.**
- "A competing CPU load with the game and the row at a lowered priority": **hit**, with a correction: the load I first
  sized (12 busy processes) starved the row itself for seconds, past anything a tick-paced row can keep (its first
  version failed there, `after-ff10ee7-bg12/`: eight re-drives, one case never realised in four sessions and six
  leaps the tired pack was refused, which is how the stamina precondition was found). The proof's stall is one
  competing process, sized by calibration (`calibration/`) to redden trunk's row in the classes the nightly showed.
- Trunk red at least once in 20, the head 20 of 20: **hit**: trunk 20 of 20 red (21 of 21 with the extra run), the
  head 20 of 20 green with a verdict (one run voided by my wrapper fault, replaced by the extra run).
- The plant red by name, under the stall and without it, and `test_pk06b_timing_table…` red: **hit**.
- No golden, case, replay, engine or pin byte; the unit-test count unchanged: **hit** (175).

## Forbidden

No game code (`src/`), case, golden, replay, engine, `lair.pin`, toolchain, `.github/` or `tools/` change; the input
model and the maintainer's feel of the aim are untouched in every case. No other game's code or material. No label,
merge, tag, release, issue filed or closed; no CI waited on, re-run or cancelled; no attribution trailer. The planning
repo and `~/.claude` are not written. kasumi is not touched. On the Mac every build and run is behind the mkdir lock and
its 8 GiB gate from a worktree pinned to its commit, the maintainer's MLX server is never stopped, scratch lives under
`~/lanes/pk09/`; on hasu block B is held per run with both lock names, rootless podman under a `pk09-` image tag,
`taskset` inside the container. Nothing here sends a signal: the stall's busy processes stop on a file and the row ends
its sessions with `q`.

**One fault of mine, on the Mac lock.** At 21:41 I edited the lane's lock wrapper (`~/lanes/pk09/run`) in place to add a
fairness pause while two copies of it were running. bash reads a script as it goes, so both copies resumed at a shifted
offset: the plant's (21:47:12) and the proof's head run 05 (21:49:53) each took the lock with `mkdir`, then died on a
parse error before writing `pid`, leaving an empty lock directory for about one and two minutes. I removed each, mine by
its creation time, and restored the wrapper's exact bytes from `8d5ba18`. The proof's head run 05 has no verdict and is
not counted; one extra pair was run (below). No other lane's lock or run was touched.

## Inputs verified

- Base pack trunk `278480955f7c088b40b9f2cdd57565ece8f4a865` (pk08's note materialised), worktree `~/lanes/pk09/pack`,
  branch `pk09`; every build and gate from a worktree pinned to its commit (`~/lanes/pk09/build-<sha>`).
- Engine `aa6c4dc0bc5071d3c07121451d913a8837cd2a6a` (`lair.pin`, unchanged), staged by `tools/fetch-lair`.
- wolf 0.2.35 `cf0c13d`, archive SHA-256 `240b84d0…a5f042a` (aarch64-apple-darwin), `4cc4045b…90dad1a` (x86-64 Linux,
  hasu); lupin 0.1.56, `9133bfdb…d58f7687`; std `2386522eb059cca5a84108562c2c0a0e72345d34`: staged and digest-checked by
  `.lair/tools/fetch-toolchain` on each host.
- Read: the lane rules of 10-31, the contract, pack#44 whole, pk08's contract, pk06's and pk06b's notes, lair's
  `tools/pty`, `src/clock`, `src/input` (the Hold), pack's `src/sim/sim.lu` (`aim_recent`, `aim_arrows`, `step`, `leap`,
  stamina), `src/pack.lu` (the loop, the trace), `docs/KEYS.md`, cub's `notes/cb11-the-combo-rethink.md` and
  `notes/cb11b-late-input.md` (the protocol this row follows), hasu's `~/lanes/hasu-env/README.md`.
- README read against the pass: the pty paragraph's "58 timed sessions … 200–400 ms later" moved and is refreshed in a
  README-only commit; the test counts (175, 38 cases, 77 directories) and everything else are current.

## Evidence index

All under `notes/pk09-evidence/`.

- `prediction.md` (`1935cca`); `nightly-41194811528.txt`, the nightly's lines verbatim.
- `measure.py`: trunk's (or any) row through the engine's runner with every write timestamped; `before/{noload,bg0,bg12}/`
  hold each run's `sessions.jsonl` (written and applied gaps, tick lateness, the rule's Hold and aim beside the game's),
  `problems.txt` and `raw.jsonl.gz` (every write and the full trace; `measure.py --reanalyse DIR` re-reads it).
- `stall.py`, the forced stall; `calibration/`, two interleaved pairs under the clamp and one busy process (trunk red 2
  of 2, the head green 2 of 2) and trunk's row green on hasu's one CPU with one busy process.
- `after-ff10ee7-bg12/`: the first paced row under the 12-process stall, red, the run that found the stamina
  precondition (`dded677`).
- `proof.sh`, `mac-lock-run.sh` (the lock wrapper's bytes), `summarise-proof.py`; `proof-mac/` (each run's pty log
  and session rows, `proof.out` the run lines) and `proof-mac.txt` (the table); `proof-mac-extra/` and
  `proof-mac-extra.txt`, the extra pair.
- `stress.sh`, `stress/`: the row under 12 busy processes, and every pty row under the proof's stall.
- `proof-hasu.sh`, `hasu-crun.sh`, `hasu-stage.sh`: the one-CPU witness on hasu block B (`taskset -c 6` inside the
  container, one busy process on the same CPU, 5 interleaved pairs), launched detached at 21:54 (its first run
  waiting from 22:25, once the head binary was built); block B was held by other lanes' gauntlets for the rest of this lane's time, so its runs are not in this note. They land in
  `/home/mfwolffe/lanes/pk09/lane/proof/` (`exit` marker, `pid`), and the PR body says what had finished at hand-back.
  The calibration run there (`calibration/hasu-trunk-one-cpu.log`) had trunk's row green: Linux's scheduler on one CPU
  with one busy process delays the row by little, so the macOS clamp is the stall that reproduces the nightly.
- `plant-run.sh`, `plant-aim.log`, `plant-aim-sessions-{unstalled,stalled}.txt`.
- `gauntlet.sh`: the final-head gauntlet (every `END` line is in the PR body).

Commits (base `2784809`):
- `1935cca` prediction; `682ec5a` measure.py; `1bedbfd` nightly lines; `43443ef` trunk measured; `6c85eca` stall.py.
- `ff10ee7` the tick-paced row and its oracle; `dded677` the leap's stamina precondition.
- `020492f`, `d7e2b99` KEYS; `3be5601` README (README-only).
- `8d5ba18`, `f6a8c49`, `8dd493a`, `430266b` scripts; `269f58f` plant evidence; `a7f17f7` calibration evidence.
- `18a26bc` proof evidence; `5afa29c` the extra pair; `6b7ba37` the stress runs; this note's commit after them.

## Rulings recommended (implemented)

- **R-pk09-1, where the aim window starts (the maintainer's feel).** (A) keep it: an arrow counts within 15 ticks of its
  last byte, which for a last-key-only keyboard is when the next arrow was pressed, so a diagonal held longer than about
  450 ms before Space is the later arrow's cardinal; (B) a handover rule: an arrow whose repeats stopped when another
  arrow began counts as held while that arrow repeats. B keeps any held diagonal, but also an arrow released before
  switching, and moves the feel the maintainer judges by play. **Recommend A**; nothing measured is an aim fault.
  Implemented: no game change.
- **R-pk09-2, the tick a late-read key gets.** (A) keep lair's clock: keys read on a late wake are applied on the first
  due tick, so a stall moves a key earlier by at most the stall; replays stay exact and latency lowest; say so in
  `docs/KEYS.md`; (B) a lair lane applies them on the last due tick. **Recommend A.** Implemented: the KEYS sentence.
- **R-pk09-3, a stall that pushes a session out of its case.** (A) drive the case again in a fresh session, up to four,
  every re-drive printed, never forgiving a disagreement; (B) accept any applied stream and require only agreement with
  the rule (cb11b's shape), which lets a stall thin the diagonal coverage unseen; (C) fail any missed target tick (cb11's
  first shape), red under any stall. **Recommend A.** Implemented.
- **R-pk09-4, the forced stall on the Mac.** The Mac has no CPU-affinity call. (A) the game, the row and one busy process
  in the background QoS clamp (`taskpolicy -c background`), calibrated to redden trunk's row as the nightly did; (B) 12
  busy processes, which starve the row for seconds, a stall no runner showed; (C) default QoS with busy processes on
  every core (the maintainer's machine: no). **Recommend A**, with the literal one-CPU witness on hasu block B
  (`taskset -c 6` inside the container, one busy process on the same CPU). Implemented.
- **R-pk09-5, the macOS leg before the merge.** `tier pr` runs the Linux leg only; the macOS job that went red runs at
  `tier full`. **Recommend** the orchestrator adds `full-matrix` at the final head, so the macOS leg is seen green before
  the merge rather than first on the trunk push.
- **R-pk09-6, a stall past the proof's.** Under 12 busy processes the row's own process does not run for seconds and
  some cases cannot be realised. (A) accept the `SCHEDULE` red there as the honest answer (the row cannot set up its
  case when it is not scheduled, and says so); (B) raise the re-drive ceiling, which buys little when every attempt is
  starved alike; (C) run the row at a higher scheduling class than the game, which no runner does. **Recommend A.**
  Implemented: nothing more.

## Done-when

- [x] Measure first: every failing case of the nightly and of three local conditions explained, the game against its rule
  in every session, the Hold lines' setup refusal explained.
- [x] The fix where the fault is: the row, tick-paced and judged on the applied ticks; no game change, the feel of the
  aim unchanged in every case.
- [x] The proof: 20 runs under the forced stall, trunk's row red 20 of 20, the head's green 20 of 20 with a verdict.
- [x] The plant `pk09-plant-aim` red by name, locally, unstalled and stalled; its draft PR opened.
- [x] README refreshed (README-only commit); KEYS refreshed.
- [x] The final-head gauntlet green; every `END` line in the PR body.
- [ ] `tier pr` green at the head, and (R-pk09-5) the macOS leg at `full-matrix`: the orchestrator's.
- [ ] The nightly green after the merge, then pack#44 closed: the orchestrator's.
- [ ] The hasu one-CPU witness: running, block B contended (above).
