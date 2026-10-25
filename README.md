# pack

Lead a pack of wolves up an endless, meandering forest path. Shadow wolves with red eyes come out of the
trees; leap at them as a pack, parry, or sprint past and be chased. Deer feed the pack. There is no health
bar: as the pack weakens, wolves faint and are left behind, and as it recovers they sprint back to rejoin
you.

A terminal game written in wolf, the first of the lair, the wolf games collection.

**What is in this build:** a pack of five runs the forest. The wolves hold a formation with the alpha
trailing, steer as one with the turn rippling back through the pack, drift and bump without overlapping,
sprint, stop and tire; the forest has clearings and dense stands and the path widens and narrows with them;
posture is the only gauge (ears, tail, gait, the pant); health works as fainting and return. **No shadows
and no deer yet:** nothing attacks and nothing feeds the pack, so health only moves under `--debug`. The
shadows, the leap and the parry are the next build (pk02); the deer, dusk and the score card the one after
(pk03).

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
| Space | leap (the attack, from pk02) |
| Shift+Down, or `z` | parry (from pk02) |
| `q` or Esc | quit; the terminal is restored on every exit |

The pack moves at a migrating trot, not a run. An exhausted pack pants and cannot sprint until it has
recovered; a tired pack's ears go back and its tails drop. Posture is the only gauge: there are no bars. As
health falls, wolves faint and are left behind; as it recovers they sprint back up from the bottom of the
screen to their places.

## Build and run

The toolchain is pinned by digest in `wolf-toolchain.toml` (wolf 0.2.35, lupin 0.1.56, the std tree the
compiler bundles). Nothing is built from source but pack itself; the only dependency is wolf-std.

```
tools/fetch-toolchain     stage the pinned toolchain into .wolf-bin/
tools/build --release     target/release/pack (and a copy at target/pack)
target/pack               play; --seed N picks a forest, --tier plain forces the plain tier
target/pack --record run.pk   save the run you just played; --replay run.pk plays it back
target/pack --debug --speed-scale 150   every speed at 150 percent, to tune by play; under --debug the
                          keys - and = move the pack's health by ten, so fainting and return can be watched
```

`pack --help` lists the rest: the headless mode that writes frames for the goldens, `--bench`, `--trace`
(one line a tick on standard error), the glyph probe. Seeds worth a look: 11 starts in a clearing, 16 in a
dense stand, 3 shows the pack bump in a right turn.

## Tests

Determinism is the oracle. A run is a pure function of the seed, the inputs, the tier and the size, so
`tests/cases/*.pk` (ten cases: a standstill, a trot, a steer into the forest, a sprint to exhaustion, a
formation turn with a bump, a faint and a return, a clearing, a dense stand, a resize mid-run, the wide
field) are run headless on both tiers and diffed against `tests/goldens/` cell for cell (`tools/goldens`).
The unit tests (`tools/test`, 83 of them) cover the diff renderer with a terminal model, the key decoder
with every sequence split at every byte, the clock, the world's noise and density, the simulation's bars
(the speeds, the turn rate, the held key, the formation's lag, the wander and the bumps, health's floors
and returns) and the tiers' promises. The pty runner (`tools/pty`) drives the real binary in a
pseudo-terminal and checks that raw mode is undone and the alternate screen left on `q`, on Ctrl-C (the
interrupt the line discipline raises) and on a planted trap, that the bytes it captured, replayed through
the model, equal the headless frames, and that a held key releases within two ticks of its last byte.
`tools/perf` holds the render under a millisecond at 80x24 and under four at 200x60, counts the loop's
wake-ups at idle, and times a key to the frame that carries it (median under a tick and a render, p90 under
two ticks). `tools/check` runs all of it; CI runs it on Linux for every pull request and on macOS as well
for trunk.

## Documents

`docs/DESIGN.md` the tuning constants; `docs/ART.md` the sprites; `docs/GLYPHS.md` every code point the
rich tier uses (PAX's font specification); `docs/PALETTE.md` the colours; `docs/KEYS.md` what terminals
send; `docs/REPLAY.md` the `.pk` file.

## Licence

GNU GPL v3 with the wolf Training Data Permission (see LICENSE and LICENSE-TRAINING-DATA).
