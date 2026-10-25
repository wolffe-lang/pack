# pack

Lead a pack of wolves up an endless, meandering forest path. Shadow wolves with red eyes come out of the
trees; leap at them as a pack, parry, or sprint past and be chased. Deer feed the pack. There is no health
bar: as the pack weakens, wolves faint and are left behind, and as it recovers they sprint back to rejoin
you.

A terminal game written in wolf, the first of the lair, the wolf games collection.

**What is in this build:** the game as designed — the title card, the pack, the forest, the shadows, the
deer, dusk, the death card and replays verified. Deer graze the path and bolt up it at one and a half
times the trot when a wolf comes close; they tire, slow below the trot and are run down, and each one
brought down feeds the pack (the first thing that raises health, so a fainted wolf can return). The
difficulty curve is gentle for the first minute, brings groups in the second and reaches its ceiling in
the third or fourth, with more deer where there are more shadows and in clearings. The afternoon turns to
dusk after two minutes of path and to night after six, on both tiers, the shadows' red eyes unchanged so
they come with the dark. The title card holds the seed, the last score and the best (kept in
`~/.pack/best`), runs the same seed again on `r`, the next on any key, and plays a saved replay (`p` the
last, `/` one by name) with its score verified by a headless re-run — a mismatch is shown, never accepted.
Every number is in `docs/DESIGN.md` and is the maintainer's to tune by play; `--start N` shows any part
of the curve or the dusk at once. The PAX font row, the installer row and the equal-experience proof are
the next lane's (pk04).

## Where it runs

| machine | tier | state |
|---|---|---|
| macOS, Terminal.app or iTerm2 (arm64) | rich: block elements, braille, 256 colours, true colour where `COLORTERM` says so | the maintainer's play; the pty rows run on every push to trunk |
| Linux, any UTF-8 terminal emulator (x86-64) | rich | the pty rows run on every pull request, inside a container |
| a Linux virtual terminal (`TERM=linux`) | plain: code points 0-255 and the sixteen colours | detected from `TERM`; untested on a VT itself |
| PAX's console | plain today; rich once PAX's font draws `docs/GLYPHS.md` | the installer row and the font row are the pk04 lane's |

The terminal must be at least 80 columns by 24 rows; the field grows to fill a larger one.

## Controls

| key | action |
|---|---|
| Left, Right | steer the pack; hold to keep turning, release to straighten; the forest edge slows and scratches |
| Up | a sprint burst, while stamina lasts |
| Down | stop; stamina returns fastest standing |
| Space | leap, the pack together: every shadow within reach of a wolf is vanquished; costs stamina, and the spent pack cannot leap |
| Shift+Down, or `z` | parry: an attack that lands within 300 ms of the press is turned and the shadow knocked back; a press, never a held stance |
| `s` | on the death card: save the replay as `pack-SEED-SCORE.pk` in the working directory (or at `--record`'s path), with its score |
| `q` or Esc | leave: a run or the death card for the title, the title for the shell (under `--no-title`, the program quits at once); the terminal is restored on every exit |
| on the title | any key runs the next seed; `r` runs the same seed again; `p` plays the last saved replay; `/` asks for a replay's name (type it, Enter plays, Esc cancels); `q` leaves |

The pack moves at a migrating trot, not a run. An exhausted pack pants and cannot sprint or leap until it
has recovered; a tired pack's ears go back and its tails drop. Posture is the only gauge: there are no bars,
and the first numbers you see are the card's. As health falls, wolves faint and are left behind; as it
recovers they sprint back up from the bottom of the screen to their places. A shadow's eyes tell its mind:
dim while it lurks, pulsing while it chases, steady while it winds up to bite — that is the moment to parry.
A deer (the pale antlered shape) bolts when you come within ten cells and outruns the trot; keep after it
and it tires and slows, then a sprint runs it down and the pack eats.

## Build and run

The toolchain is pinned by digest in `wolf-toolchain.toml` (wolf 0.2.35, lupin 0.1.56, the std tree the
compiler bundles). Nothing is built from source but pack itself; the only dependency is wolf-std.

```
tools/fetch-toolchain     stage the pinned toolchain into .wolf-bin/
tools/build --release     target/release/pack (and a copy at target/pack)
target/pack               the title card, then play; --seed N picks a forest, --tier plain forces the plain tier
target/pack --record run.pk   save the run you just played; --replay run.pk plays it back and verifies its score
target/pack --start 1200  begin 1200 rows up the path: the curve near its ceiling and full dusk at once
                          (600 is the second minute's groups, 1800 the night); a replay keeps it as `start`
target/pack --no-title    the run at once, no title card (what the pty rows and every build before pk03 did)
target/pack --debug --speed-scale 150   every speed at 150 percent, to tune by play; under --debug the
                          keys - and = move the pack's health by ten, so fainting and return can be watched
```

`pack --help` lists the rest: the headless mode that writes frames for the goldens, `--bench`, `--trace`
(one line a tick on standard error), the glyph probe. Seeds worth a look: 11 starts in a clearing with
deer; 4 has a deer on the path within two seconds; 3 shows the pack bump in a right turn; 16 starts in a
dense stand, and `--seed 16 --start 600` puts a group of three shadows on you within five seconds.

## Tests

Determinism is the oracle. A run is a pure function of the seed, the inputs, the tier and the size, so
`tests/cases/*.pk` (nineteen cases: a standstill, a trot, a steer into the forest, a sprint to exhaustion, a
formation turn with a bump, a faint and a return, a clearing, a dense stand, a resize mid-run, the wide
field, the shadows' five — a spawn and a chase with the turn, a group attack, a leap that lands and the
fade, a parry that turns an attack, a death and its card, all from row 600 where the curve has groups — a
deer fleeing and run down, and dusk coming, dusk and night) are run headless on both tiers and diffed
against `tests/goldens/` cell for cell (`tools/goldens`), with the art study's sheets and the title card.
Shadows and deer are the seed's, never a replay event, so the same file meets the same on every machine.
The unit tests (`tools/test`, 129 of them) cover the diff renderer with a terminal model, the key decoder
with every sequence split at every byte and the prompt's text mode, the clock, the world's noise and
density, the curve and the deer's rate, the simulation's bars (the speeds, the turn rate, the held key, the
formation's lag, the wander and the bumps, health's floors and returns, the shadows' roll, perception, the
turn at rest and the chase, the sprint that shakes, bodies never overlapping, group and lone damage, the
leap and its refusals, the parry's window and recoil, death and the score, the deer's roll, walk, flight,
tiring, catch and feed, the spawn side on a bend, the phase of the day), the palette's blend (the keyframes
met, the eyes fixed, the cube round-tripped, the plain tier's promise at night), the replay's `start` and
`# score`, the best file, and the tiers' promises (the cards' text is Latin-1, no digit in the field before
the card). The pty runner (`tools/pty`) drives the real binary in a pseudo-terminal and checks that raw
mode is undone and the alternate screen left on `q`, on Ctrl-C (the interrupt the line discipline raises)
and on a planted trap, that the bytes it captured, replayed through the model, equal the headless frames,
that a held key releases within two ticks of its last byte, that a run played to its death, saved from the
card and re-run, gives the same card byte for byte, and that the title card runs the same seed on `r`,
records the score and the saved replay in its own `HOME`, and plays the replay back verified. `tools/perf`
holds the render under a millisecond at 80x24 and under four at 200x60 with a dozen shadows and three deer
at dusk, counts the loop's wake-ups at idle, and times a key to the frame that carries it (median under a
tick and a render, p90 under two ticks). `tools/check` runs all of it; CI runs it on Linux for every pull request and
on macOS as well for trunk.

## Documents

`docs/DESIGN.md` the tuning constants; `docs/ART.md` the sprites; `docs/GLYPHS.md` every code point the
rich tier uses (PAX's font specification); `docs/PALETTE.md` the colours; `docs/KEYS.md` what terminals
send; `docs/REPLAY.md` the `.pk` file.

## Licence

GNU GPL v3 with the wolf Training Data Permission (see LICENSE and LICENSE-TRAINING-DATA).
