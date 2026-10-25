# pk00 — the engine (M-PK0): one wolf trots up a scrolling path

Lane pk00 of track 19 (lair, the wolf games; the planning repo's `sprints/lair/00-the-engine/pk00-the-engine.md`),
Fable, crawl 54, 2026-10-25. The repository was a licence and a README stub (`1eb0880`); this pass turns the
campaign's design document into an engine with one wolf, proven on macOS and in a Linux pty.

## 1. What this pass does

- **The pin** (`wolf-toolchain.toml`): wolf 0.2.35, lupin 0.1.56 and the std tree the compiler bundles
  (wolf-std `2386522e`), by sha256 digest read twice from the release API, equal to yew's fourth pin;
  `tools/fetch-toolchain` refuses a mismatch and refuses a std pin that drifts from the bundle.
- **The cell model** (`src/grid`): a `Cell` of four ints (code point, two colour indices, attribute bits),
  a `Grid`, a diff renderer that writes the fewest bytes a pen allows (a cursor move only when the cursor is
  elsewhere, an SGR only when the style changes, the glyph as UTF-8) in three colour dialects (the sixteen,
  the 256 cube, RGB), the headless dump formats, and a terminal model (`model.lu`) that applies the bytes back
  to a grid: the property test's oracle and the pty runner's instrument.
- **Two tiers** (`src/tier`): semantic sprites to cells. Rich: block elements and half-blocks for the wolf
  (3 by 2, R-pk00-4 B: only the wolves are doubled), braille for foliage, heavy box drawing for trunks, the
  256 cube. Plain: code points 0-255 and the sixteen colours; a test holds every sprite and variant to it.
  Detection from `TERM`, `COLORTERM` and the locale (R-pk00-3 A), `--tier` overriding.
- **The terminal** (`src/term`): raw mode and the alternate screen through `std.term`; the runtime's
  `restore_at_exit` registered on standard output BEFORE the first byte and before the mode changes, with the
  leave bytes; refusals by name (not a tty, `TERM=dumb`, under 80x24, a refused mode).
- **The decoder** (`src/input`): arrows in both forms, `ESC [ 1 ; m X` with Shift+Down the parry (R-PK-3),
  Space, `z`, `q`, a lone ESC by a 50 ms timeout, Ctrl-C as a byte, kitty and tilde forms recognised and
  ignored; table tests whole and split at every byte; `docs/KEYS.md`.
- **The clock** (`src/clock`): a fixed 30 Hz tick, the one wait in `std.signal.wait_fds` on standard input
  with the next deadline, frames dropped when late and the simulation never skipping a tick.
- **The world and the wolf** (`src/world`, `src/sim`): the path from seeded 1-D value noise (centre and half
  width, any row at any time, nothing stored), the forest's density from the same hash; one wolf with
  position, heading, speed, acceleration and turn rate, steered by taps, a stamina-bounded sprint, a stop,
  the forest edge slowing and scratching, exhaustion as a posture; the alpha's eye (the wolf five rows above
  the bottom; the screen leads). Every number a named constant, mirrored in `docs/DESIGN.md`.
- **The frame** (`src/art`): terrain and the wolf on either tier; the four-frame trot by distance; the pant;
  the sprite sheet of every sprite the tiers know (the fainted wolf, the shadow with red eyes, the deer, a
  pack in formation) committed as a golden; `docs/ART.md`, `docs/GLYPHS.md` (18 code points, held to the tier
  by a test), `docs/PALETTE.md`.
- **Headless goldens and replays** (`src/replay`, `tests/cases`, `tests/goldens`): `pack --headless --seed S
  --script in.pk --frames N --every K --tier T --size WxH --dump DIR` writes each frame as cell text and a
  styles file; six cases (a standstill, a trot, a steer into the forest, a sprint to exhaustion, a resize
  mid-run, the 200x60 field) on both tiers plus the art sheets, 776 KB; the `.pk` format (`docs/REPLAY.md`)
  with `--replay` and `--record`.
- **The pty runner** (`tools/pty`): the real binary in a pseudo-terminal held by a session-leader process
  with the game as its foreground job; five rows: `quit`, `ctrl-c` (the byte 0x03 through the line
  discipline), `trap` (`--trap-at 20`), and `agree-rich`/`agree-plain` (the captured bytes through the
  model equal the headless final frame, glyphs and styles). Each asserts the alternate screen entered and
  left, the cursor hidden and shown, termios and `stty -a` equal before and after, the leave bytes last, and
  what ended the loop.
- **The perf gate** (`tools/perf`, `pack --bench`, `tools/perf-idle`): render + diff per frame on both tiers
  at 80x24 and 200x60; the voluntary context switches of a standing game over 10 s; the key-to-frame latency.
- **CI** (`ci/tiers.py`, its test, `ci/nightly-red.sh`, `.github/workflows/ci.yml`, `ci/Containerfile`):
  clef's planner cut to pack; `tier pr` = the planner's test and the Linux leg in the container (fmt, the 66
  unit tests on the checked machine, both builds, `pack --selftest`, the goldens, the pty rows); `tier full`
  adds the macOS leg and the perf gate; the `full-matrix` label read as clef reads it; a red nightly opens
  one issue.
- **The public docs**: README with the machines and controls tables; six documents under `docs/`.

## 2. How it was tested

| what | where | result |
|---|---|---|
| `wolf fmt --check`, 66 unit tests on the checked machine (`tools/test`), 0 SKIP | hasu B (container, `taskset -c 6-11`), nomad | green both |
| both tiers built, warnings denied | hasu B, nomad | green |
| `pack --selftest` on the release binary (the decoder table whole and split at every byte; the diff property) | hasu B, nomad | green |
| the goldens, six cases on both tiers and the art sheets, byte-identical | hasu B (Linux x86-64), nomad (macOS arm64) | green both, the same bytes |
| the pty rows `quit`, `ctrl-c`, `trap`, `agree-rich`, `agree-plain` | hasu B in the container; nomad | all five green on both |
| the perf gate | hasu B (kasumi-class), nomad | render bars met on both; idle 300 wake-ups in 10 s on Linux; latency: see 3 |
| CI, `tier pr` | the PR run | the orchestrator reads the id; see the hand-back |
| the plants (item 10) | three draft PRs, each red on its named row | `pk00-plant-golden` PR #1, `pk00-plant-restore` PR #2 run 40165937290 (the `ctrl-c` row: termios and stty differ after), `pk00-plant-decoder` PR #3 run 40165941203 (`test_shift_down_is_parry` red); the golden plant's run id is in the hand-back |

Two faults the rows caught that the unit tests did not:

1. **Keys read between ticks were dropped.** The live loop reset its key list on every wake, so a key that
   arrived on an input wake with no tick due never reached the simulation. The `quit` row hung for 30 s.
   Fixed (`ce2c4c3`): the list is reset only after a tick consumed it, so a key waits at most one tick.
2. **The release tier read every key as the quit key** (wolf 0.2.35, LLVM with the mid-end on), while the
   native tier, the checked machine and the release tier with `WOLF_MIDEND=0` decoded every key. The same
   release binary's `--selftest` decoded the table right, so the miscompile is context-dependent; a first
   version of `input.feed` that called itself after a stray byte following ESC answered 7 for every byte even
   in a probe, and a minimal reproduction of that shape alone did not fail. `tools/build` sets `WOLF_MIDEND=0`
   for the release tier (the guide's precedent, wolf-lang#146) and names the issue; `pack --selftest` holds
   the shipped tier to the table from now on. The wolf-lang issue is listed in section 5 with its witness.
   The pty rows passed while this fault was live, because `q` and a misread key both ended the game with
   exit 0: the closing line now names what ended the loop and the rows assert it.

The prediction (`notes/pk00-evidence/prediction.md`), scored:

| | predicted | measured | |
|---|---|---|---|
| 1 render | 0.3-0.6 ms at 80x24, 2.5-4.5 ms at 200x60 | 0.06 / 0.24 ms on hasu, 0.03 / 0.21 ms on nomad (release, mid-end off) | miss, pessimistic by 10x: a frame changes far fewer cells than the whole path (the scroll moves rows one cell a tick, most cells keep their glyph) |
| 2 wait_fds | identical on both hosts; a std surface gap first | identical (keys, deadline, Ctrl-C, resize); the first gap was `fs.read_into` absent at the pin, then the release miscompile | hit on the wait; the first finding was a compiler fault, not std |
| 3 the first wrong-width rich glyph on Terminal.app | braille | owed to the maintainer's `pack --probe-glyphs` | open |
| 4 decoder table | about 24 rows | 20 rows in the selftest table, 14 sequence kinds in the decoder | hit |
| 5 the two paths at the first try | would not agree; one iteration | agreed at the first try on both hosts | miss |
| the plain tier needs no glyph above 127 | yes | yes (`test_plain_tier_needs_no_row`) | hit |
| zero wake-ups beyond the tick at idle | 300 in 10 s | 300 exactly (hasu, `/proc`) | hit |

## 3. Measurements

Release binaries, mid-end off; hasu block B is the kasumi-class host the contract names; nomad's load
averages were 3.3 to 6.4 during the runs (the maintainer's MLX server beside the lane).

| measurement | hasu B (Linux x86-64) | nomad (macOS arm64) | bar |
|---|---|---|---|
| render + diff, 80x24 rich, avg / p99 / max, 300 frames | 59 / 284 / 422 us | 29 / 59 / 67 us | < 1 ms |
| render + diff, 80x24 plain | 33 / 57 / 65 us | 29 / 52 / 54 us | < 1 ms |
| render + diff, 200x60 rich | 244 / 476 / 501 us | 207 / 405 / 424 us | < 4 ms |
| render + diff, 200x60 plain | 228 / 364 / 383 us | 198 / 320 / 337 us | < 4 ms |
| bytes a frame, 80x24 rich / plain; 200x60 rich / plain | 3,407 / 1,896; 25,675 / 14,532 | the same (the bytes are deterministic) | |
| with the mid-end on (before the switch): 80x24 rich / 200x60 rich | 53 / 202 us | | the switch costs about 10 percent |
| voluntary context switches, standing, 10 s | 300 (bar 240-360) | no counter without root: a loud SKIP | one a tick |
| tick wakes late against their deadline, avg / max | 0.66 / 1.1 ms | 1.4 / 2.0 ms | |
| key to the next frame's first byte, median | 24-36 ms | 37-63 ms | one tick (33 ms) plus a render |
| the same, p90 / max | 113-133 / 166 ms | 99-134 / 166 ms | see below |
| the goldens | 776 KB, byte-identical across the two hosts | | |
| the unit tests | 66 on the checked machine, 0 SKIP | | |

**The latency outliers.** The median is one tick, as designed (a key is applied on the next tick and drawn
then). The 90th percentile and the maximum are exact multiples of the tick (133 and 167 ms, four and five
ticks) on both hosts, while the same run's closing line says 236 ticks, 236 frames, 0 dropped and tick wakes
never more than 1.1 ms late: the game drew every tick on time. So the outliers are the measurement's: the
runner times the first byte after the key, which counts a frame that happened to be in flight (the near-zero
samples, `5 1 0 13 19 ... 1 1 1 1`) and, when the key lands just after a frame, waits a full tick plus
whatever the pty master hands it in one batch. The sound measurement is the time to the frame that CARRIES
the key (the wolf's column or heading changed), which needs a marker the frame can be read for; pk01's first
item. The bar as written is therefore not shown met and not shown missed; the row stays red in `tools/perf`
until the measurement is sound, and the perf job is `tier full`'s, so a pull request is not held by it.

**What the pty rows measured about restore** (both hosts): after `q`, after the Ctrl-C byte and after the
planted trap, termios and `stty -a` are equal to the recorded state; on macOS `pendin` differs, the kernel's
"retype pending input" flag set by any return to canonical mode, which the spec's own restore witness records
too, and the runner masks that one bit. The runtime's leave bytes are the last output on every path.

**A runtime finding worth a doc line** (not a bug): `os_term_restore_at_exit` writes its bytes through a dup
of the handle it is given; a program started as `prog < /dev/tty` has a READ-ONLY descriptor 0, and a restore
registered on it restores the mode but loses the bytes silently (measured by the probe under the first
runner). pack registers on standard output.

## 4. Rulings asked (recommended and implemented)

- **R-pk00-1 the minimum size**: (A) 80x24. Implemented: `term.MIN_COLS/MIN_ROWS`; the field scales up. The
  rich wolf needs 3 by 2 cells and the path 10 cells; 60x20 would work for the sprites, 80x24 is the room the
  forest needs to read as a place.
- **R-pk00-2 the tick**: (A) 30 Hz. Render is 0.06 ms a frame at 80x24, so 60 Hz would cost nothing in
  render; 30 Hz is chosen for the input model (a tap is a whole tick of motion) and the idle budget.
- **R-pk00-3 rich-tier detection**: (A) `--tier` with a default from `TERM`/`COLORTERM`/the locale.
  Implemented in `tier.detect`; PAX's `TERM` is `linux` (px58's measurement) and lands on plain.
- **R-pk00-4 the half-block doubling**: (B) the wolves only. The cost of (A) measured: a frame at 80x24 rich
  with every cell a half-block pair would double the glyph bytes (3 bytes a cell against 1 for ASCII marks)
  and the diff cost with it, well inside the bar; the reason to keep (B) is legibility, not cost: the
  forest's braille reads as foliage at one glyph a cell.
- **R-pk00-5 (new) the release tier with the mid-end off**: (A) `WOLF_MIDEND=0` in `tools/build` until the
  wolf-lang issue is answered, with `pack --selftest` as the gate; (B) ship the native tier. Recommend (A):
  the render numbers are within 10 percent, and the selftest holds it. Implemented.
- **R-pk00-6 (new) the latency bar's statistic**: (A) median under one tick plus a render and p90 under two
  ticks, the maximum recorded; (B) the maximum under two ticks. Recommend (A) on a shared host; implemented,
  and the row is red today on both hosts at p90 (section 3).

## 5. What is next

**pk01 — the pack and the forest (M-PK1), a draft contract.**
1. The per-sample latency trace first: a key's tick of arrival and the tick it is drawn, logged under
   `--trace`, run in the pty on both hosts; fix or name the four-tick outlier.
2. The pack of five: `sim.Pack` with slots in formation (two leading, two flanking, the alpha trailing at
   the centre, `art.sheet` rows 16-21 are the shape), each wolf its own position, heading and gait frame,
   steered as one with per-slot lag so a turn ripples through the pack; the alpha's eye anchored to the
   alpha.
3. Health as the pack's: a floor per wolf; at each floor the farthest wolf faints (drawn with
   `art.draw_fainted`, left behind as the world scrolls); at each recovery threshold it sprints back from
   the bottom edge to its slot at `SPRINT_V`.
4. The forest's density from the same noise: `world.forest_kind` taking a density channel; clearings; the
   spawn rate's input for pk02.
5. Posture as HUD: ears and tail glyphs by stamina band; the pant per wolf.
6. Goldens for each (a formation turn, a faint and return, a clearing), both tiers; the pty rows unchanged.
7. The macOS owed rows closed by the maintainer's runs (below), pasted into KEYS.md and GLYPHS.md.

**Owed to the maintainer's run on this Mac** (the lane cannot drive a GUI terminal under RULES section 4):
- in Terminal.app and in iTerm2: `cd ~/lanes/pk00/pack && target/pack --probe-glyphs`, paste the table into
  `docs/GLYPHS.md`'s measured columns with the date;
- in each: `python3 -I tools/keyprobe`, press the arrows, Shift+arrows, Space, z, q, Esc, paste into
  `docs/KEYS.md`;
- play: `cd ~/lanes/pk00/pack && target/pack` (`--seed N` for another forest, `--record run.pk` to keep
  the run, `--tier plain` to see PAX's view); `q` quits. The binary is the release tier built at the final
  head by `tools/build --release`.

**Issues to file** (the lane files nothing):
1. wolf-lang: at 0.2.35 the release tier's mid-end miscompiles pack's key path — every key decoded as the
   quit key in the live loop while the same binary's `--selftest` passes; native, checked and
   `WOLF_MIDEND=0` are right. Witness: pack at `7fd0fae^` (the commit before the switch), `tools/build
   --release` without `WOLF_MIDEND=0`, then `python3 -I tools/pty --rows quit` (red: "ended by the quit key"
   with only arrows typed) against the same with the switch (green); and the earlier recursive `feed`, whose
   release build answered 7 for every byte in a probe (`notes/pk00-evidence/` keeps the probe text). A
   minimal shape (a push of a constant then a self-call) did not reproduce.
2. wolf-lang (a spec/doc line): `[os.term.restore]` writes the bytes through a dup of the given handle; on
   a read-only descriptor the bytes are lost with no row (measured under a pty with `< /dev/tty`). Say so,
   or answer `io` at registration when the handle is not writable.
3. pack: the latency measurement counts coincidental frames; measure to the frame that carries the key (section 3); pk01's first item.
4. pack: the macOS owed rows (KEYS.md, GLYPHS.md) after the maintainer's runs.
5. pack: the pty runner's `idle` row has no macOS counter (a loud SKIP); a `sample`-based or
   `proc_pidinfo` route for nomad.

**Prune list** (nothing deleted by the lane):
- nomad: `~/lanes/pk00/probe/` (p1, p2, w1, w2, w3, const-probe: the toolchain and terminal probes),
  `~/lanes/pk00/plants/` (three worktrees; after the orchestrator closes PRs #1-#3), `~/lanes/pk00/pack/target/`
  but `target/pack` (the maintainer's binary);
- hasu: `~/lanes/pk00/probe/`, `~/lanes/pk00/image/` (the first image recipe, superseded by `ci/Containerfile`),
  `~/lanes/pk00/pack/target/`, the logs `~/lanes/pk00/*.log`, the podman image `localhost/pk00-ubuntu:24.04`
  (superseded by `localhost/pack-ci:<tag>`); `~/lanes/pk00` is 423 MB.
